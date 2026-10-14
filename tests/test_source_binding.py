"""Synthetic files through the real replay/CLI chain; never ADB or production data."""
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import bv_autoplay as ap
import bv_live as live
from test_price_binding import synthetic_quote
from bv_verify import freeze,semantic_gate,replay,verify_round
from bv_batch import verify_batch
from bv_evidence import VERSION
from test_reliability import cards,controller


def varint(n):
    out=bytearray()
    while n>127:out.append((n&127)|128);n>>=7
    out.append(n);return bytes(out)


def field(k,v):
    return varint(k*8)+varint(v) if isinstance(v,int) else varint(k*8+2)+varint(len(v))+v


class Sources(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.source=self.root/'source';self.source.mkdir()
        (self.source/'bv_bodies').mkdir();self.index=self.source/'bv_ws.jsonl';self.index.touch()
        self.control=self.root/'control';self.control.mkdir()
        self.enterContext(patch.object(live,'SOURCE',self.source))
        self.enterContext(patch.object(live,'CONTROL',self.control))
        self.enterContext(patch.object(live,'INSTANCE','synthetic-device'))
        # Budget's existing default parameter is rebound explicitly in this isolated test.
        budget=live.Budget
        self.enterContext(patch.object(live,'Budget',side_effect=lambda root=None:budget(root or self.control)))
        self.base=dt.datetime(2026,10,13,10,tzinfo=dt.timezone(dt.timedelta(hours=8)))
        self.counter=0;self.round_counter=0

    def raw(self,mid,body,at,direction='S->C'):
        self.counter+=1;n=self.counter
        data=b'\x05\0\0\0'+n.to_bytes(2,'little')+mid.to_bytes(3,'big')+b'\0'+body
        name=f'synthetic_{n}.bin';(self.source/'bv_bodies'/name).write_bytes(data)
        rec=dict(file=name,len=len(data),dir=direction,ts=at.isoformat(),
                 hdr=dict(cmd=mid&255,seq=n,flags=int.from_bytes(data[6:8],'little')))
        with self.index.open('a') as f:f.write(json.dumps(rec)+'\n')

    def make_round(self,purpose,reg=None,ordinal=0,session=None):
        self.round_counter+=1;n=self.round_counter
        folder=Path(session) if session else (self.control/reg['batch_id'] if reg else self.control)/(purpose+f'_synthetic{n}')
        folder.mkdir();rid=f'BINGO_HALL.synthetic.{n}';b=rid.encode()
        t=self.base+dt.timedelta(seconds=n*30);ns=lambda seconds:int((t+dt.timedelta(seconds=seconds)).timestamp()*1e9)
        selection=dict(CardCount=4,BetCount=1,LastBetTicket=4)
        (folder/'selection.json').write_text(json.dumps(selection))
        (folder/'base_bet_config.json').write_text(json.dumps([dict(id='BET_NP_SYMBOL_1',cost=1)]))
        start=self.index.stat().st_size
        selected=field(1,b'BET_NP_SYMBOL_1')+field(2,4)
        self.raw(100042,field(2,selected),t+dt.timedelta(seconds=1),'C->S')
        cs=b''.join(field(2,field(1,c['slot'])+b''.join(field(2,field(1,v)) for v in c['vals']))for c in cards())
        self.raw(100003,field(1,field(4,field(1,cs+field(10,b)+field(11,selected)))),t+dt.timedelta(seconds=2))
        self.raw(100009,field(1,b)+field(2,bytes(range(1,6))),t+dt.timedelta(seconds=3))
        marked=[(1+(n-1)%2,0)] if purpose=='diagnostic' else [(slot,cell) for slot in range(1,5) for cell in range(5)][:-1]
        lines=[(3,f'CardLayout StartGameLogic:layoutFrame round={rid} rule=STANDARD cards=4 layout=x'),
               (1.5,'NotifyResources TICKET current=81 next=77 delta=-4')]
        for i in range(5):lines.append((4+i,f'[BallCaller] cur 1 target 1 index {i}, num {i+1} diff 0'))
        actions=[]
        for slot,cell in marked:
            when=4+cell+.2+slot*.01
            lines.append((when,f'BingoLog: Daub Type Manual, Index: {slot-1}, {cell+1}, ({cell},0), Mod None'))
            actions.append(dict(kind='input_dispatched',slot=slot,cell_index=cell,round_id=rid,dispatched_ns=ns(when-.1)))
            self.raw(100007,field(1,b)+field(2,field(1,1)+field(3,field(1,cell)+field(2,slot-1))),t+dt.timedelta(seconds=when+.01),'C->S')
        lines.append((20.1,'BingoPlayView GameOver'))
        text=''
        for secs,value in sorted(lines):
            stamp=(t+dt.timedelta(seconds=secs)).strftime('%y/%m/%d %H:%M:%S.%f')[:-3]
            text+=f'I:1:2:{stamp} +08:00 {value}\n'
        (folder/'client-during.log').write_text(text)
        (folder/'actions.jsonl').write_text(''.join(json.dumps(a)+'\n' for a in actions))
        (folder/'clock.json').write_text(json.dumps(dict(samples=[dict(host_before_ns=ns(0)-1_000_000,
            host_after_ns=ns(0)+1_000_000,mono_before_ns=ns(0)-1_000_000,mono_after_ns=ns(0)+1_000_000,
            device_ns=ns(0),boot_id='synthetic-boot')],log_identity=['synthetic',1])))
        blocks=[]
        for slot in range(1,5):blocks.append('|'.join('1::' if k==12 or (slot,k) in marked else '' for k in range(25)))
        state=blocks[0]+''.join('@#'+x for x in blocks[1:])+'@'
        self.raw(100014,field(1,b),t+dt.timedelta(seconds=20))
        self.raw(100007,field(1,b)+field(2,field(1,9)+field(2,state.encode())),t+dt.timedelta(seconds=21),'C->S')
        identity=dict(instance='synthetic-device',code_version='fixed-test-code',parser_version=VERSION,metric_version=live.METRIC)
        if reg:identity.update({k:reg[k]for k in ('batch_id','instance','code_version','parser_version','metric_version')})
        policy={k:reg[k] for k in ('resource_authorization','limits') if reg and k in reg}
        identity.update(policy)
        frozen=freeze(folder,start,self.index.stat().st_size,purpose=purpose,mode='full_autoplay' if purpose=='acceptance' else 'single_target_diagnostic',session_id=folder.name,registered_ns=ns(0),ended_ns=ns(22),**identity)
        budget=live.Budget()
        with patch.object(live.time,'time_ns',return_value=ns(.5)):
            budget.append('purchase_reserved',purpose=purpose,session_id=folder.name,
                          reserved_tickets=4,batch_id=reg['batch_id']if reg else None,**policy)
        if reg:
            row=dict(identity,session_id=folder.name,ordinal=ordinal,started_ns=ns(0),source_start=start,
                     frozen_ref=str(frozen.relative_to(folder.parent)))
            with (folder.parent/'starts.jsonl').open('a')as f:f.write(json.dumps(row)+'\n')
            budget.append('batch_round_start',**row)
            (folder/'settlement.json').write_text(json.dumps(dict(navigation_ready=True)))
        return frozen

    def qualified_batch(self,policy=None):
        self.make_round('diagnostic');self.make_round('diagnostic')
        self.assertTrue(semantic_gate()['qualified'])
        batch=self.control/'batch_synthetic';batch.mkdir()
        reg=dict(batch_id=batch.name,instance='synthetic-device',code_version='fixed-test-code',parser_version=VERSION,
                 metric_version=live.METRIC,purpose='acceptance',planned_rounds=10,
                 registered_ns=int((self.base+dt.timedelta(seconds=89)).timestamp()*1e9),source_start=self.index.stat().st_size)
        reg.update(policy or {})
        (batch/'registration.json').write_text(json.dumps(reg));(batch/'starts.jsonl').touch()
        live.Budget().append('batch_registered',**reg)
        for i in range(10):self.make_round('acceptance',reg,i+1)
        return batch

    def test_new_resource_policy_bound_to_frozen_source_and_ledger(self):
        batch=self.qualified_batch(dict(resource_authorization=live.RESOURCE_AUTHORIZATION,limits=dict(live.LIMITS)))
        self.assertTrue(verify_batch(batch)['acceptance_pass'])
        p=next(batch.glob('acceptance_*/frozen.json'));f=json.loads(p.read_text())
        f.pop('resource_authorization');f.pop('limits');p.write_text(json.dumps(f))
        self.assertIn('mixed_resource_authorization',verify_batch(batch)['errors'])

    def test_real_verifier_and_cli_ten_raw_distinct_rounds_not_summary_flags(self):
        batch=self.qualified_batch();r=verify_batch(batch)
        self.assertTrue(r['acceptance_pass'],r['errors']);self.assertEqual((r['N'],r['E']),(190,200))
        self.assertEqual(r['weighted_rate'],.95)
        with patch.object(ap.sys,'argv',['bv_autoplay.py','--batch-results',str(batch)]),patch('builtins.print'):
            self.assertEqual(ap.main(),0) # isolated, file-backed synthetic source binding only
        lines=(batch/'starts.jsonl').read_text().splitlines();(batch/'starts.jsonl').write_text('\n'.join(lines[1:]))
        self.assertFalse(verify_batch(batch)['acceptance_pass'])

    def test_mutated_raw_body_and_label_cannot_promote_a_fixture(self):
        f=self.make_round('diagnostic');self.assertTrue(replay(f)['controlled_differential'])
        data=json.loads(f.read_text());data.update(purpose='acceptance',evidence_kind='observed-live')
        f.write_text(json.dumps(data));self.assertFalse(verify_round(f)['evidence_valid'])
        body=next((self.source/'bv_bodies').glob('*.bin'));body.write_bytes(body.read_bytes()+b'x')
        with self.assertRaises(ValueError):replay(f)

    def test_missing_semantic_quantity_does_not_bypass_runtime_preparation(self):
        self.make_round('diagnostic')
        self.assertFalse(semantic_gate()['qualified'])
        with patch.object(live,'Device'),patch.object(live,'clean_code',return_value=True),patch.object(live,'preflight',return_value=({'run_ready':False,'blockers':['missing_source']},[])),patch.object(ap.sys,'argv',['bv_autoplay.py','--start']),patch('builtins.print'):
            self.assertEqual(ap.main(),2)
        self.assertFalse(any(e['kind']=='purchase_reserved' and e['purpose']=='acceptance' for e in live.Budget().records()))

    def test_special_before_call_stays_unknown_and_dispatch_time_mismatch_fails(self):
        from bv_verify import content_digest
        p=self.make_round('diagnostic');f=json.loads(p.read_text());log=p.parent/f['client_ref']
        # A real file-backed synthetic PowerUp before the first call, same cell.
        lines=log.read_text().splitlines();manual=next(l for l in lines if 'Daub Type Manual' in l)
        effect=manual.replace('Daub Type Manual','Daub Type PowerUp').replace('10:00:34.210','10:00:33.500')
        log.write_text('\n'.join(sorted(lines+[effect]))+'\n')
        events,_=live.scan_range(self.index,self.source/'bv_bodies',f['source']['start'],f['source']['end'])
        files=[p.parent/f[k] for k in ('client_ref','actions_ref','selection_ref','config_ref','clock_ref')]
        f['source_digest']=content_digest(f['source'],events,files);p.write_text(json.dumps(f))
        r=replay(p);self.assertEqual(r['errors'],[]);self.assertEqual((r['N'],r['E'],r['Unknown']),(0,20,1))
        self.assertFalse(r['controlled_differential'])
        # Never widen the timestamp window to force a diagnostic to qualify.
        a=p.parent/f['actions_ref'];rows=[json.loads(l) for l in a.read_text().splitlines()]
        rows[0]['dispatched_ns']+=20_000_000_000;a.write_text(''.join(json.dumps(x)+'\n' for x in rows))
        f['source_digest']=content_digest(f['source'],events,files);p.write_text(json.dumps(f))
        self.assertIn('manual_dispatch_time_binding_mismatch',replay(p)['errors'])

    def test_restart_cost_proof_reuses_exact_replayed_symbol_cost_not_balance(self):
        p=self.make_round('diagnostic')
        self.assertEqual(live.cost_proof(b'', 'BET_NP_SYMBOL_1',4),str(p))
        with self.assertRaisesRegex(ValueError,'cost_semantics_not_crosschecked'):
            live.cost_proof(b'', 'BET_NP_SYMBOL_1',8)

    def test_start_entry_registers_all_rounds_verifies_sources_and_settles(self):
        self.base=dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
        self.make_round('diagnostic');self.make_round('diagnostic')
        class Navigation:
            pending=False
            claims=0
            def sample(self,path):return dict(scene='congrats' if self.pending else 'lobby')
            def claim(self,sample):self.pending=False;self.claims+=1;return 'executed'
        nav=Navigation()
        def round_source(*args,**kw):
            batch=kw['batch'];self.make_round('acceptance',batch,batch['ordinal'],kw['session'])
            nav.pending=True
            return dict(rounds_started=1)
        check=dict(run_ready=True,purchase_ready=True,blockers=[],quote=synthetic_quote(balance=100))
        with patch.object(live,'preflight',return_value=(check,[])),patch.object(live,'Device',return_value=nav),patch.object(live,'clean_code',return_value=True),patch.object(live,'code_version',return_value='fixed-test-code'),patch.object(live,'diagnose',side_effect=round_source),patch.object(live.time,'sleep'),patch.object(ap.sys,'argv',['bv_autoplay.py','--start']),patch('builtins.print'):
            self.assertEqual(ap.main(),0)
        result=json.loads(next(self.control.glob('batch_*/result.json')).read_text())
        self.assertTrue(result['acceptance_pass']);self.assertEqual(result['started_rounds'],10)
        self.assertEqual(nav.claims,10)
        registration=json.loads(next(self.control.glob('batch_*/registration.json')).read_text())
        self.assertEqual(registration['positions'],list(range(1,11)))
        self.assertEqual(registration['limits'],live.LIMITS)

    def test_two_full_rounds_certify_same_frozen_batch_without_single_click_gate(self):
        batch=self.control/'batch_full';batch.mkdir();(batch/'starts.jsonl').touch()
        reg=dict(batch_id=batch.name,instance='synthetic-device',code_version='fixed-test-code',parser_version=VERSION,
                 metric_version=live.METRIC,purpose='acceptance',planned_rounds=10,
                 registered_ns=int((self.base+dt.timedelta(seconds=29)).timestamp()*1e9),source_start=0)
        (batch/'registration.json').write_text(json.dumps(reg));live.Budget().append('batch_registered',**reg)
        one=self.make_round('acceptance',reg,1)
        first=verify_round(one);self.assertFalse(first['evidence_valid']);self.assertEqual(first['source_errors'],[])
        self.make_round('acceptance',reg,2)
        self.assertTrue(semantic_gate(batch_id=batch.name)['qualified'])
        self.assertTrue(verify_round(one)['evidence_valid'])

    def test_actual_entry_pauses_before_wallet_purchase_and_resumes_same_frozen_ten(self):
        self.base=dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
        class Navigation:
            prepared=0
            def sample(self,path):return dict(scene='lobby')
            def prepare_panel(self,path):self.prepared+=1
        nav=Navigation()
        def round_source(*args,**kw):
            batch=kw['batch'];self.make_round('acceptance',batch,batch['ordinal'],kw['session'])
            return dict(rounds_started=1)
        ready=dict(run_ready=True,blockers=[],quote=synthetic_quote(balance=100))
        pause=dict(run_ready=False,blockers=['batch_budget_insufficient'],
                   budget_plan=dict(deficits=dict(wallet=4,tickets=0,seconds=0,positions=0)))
        with patch.object(live,'clean_code',return_value=True),patch.object(live,'code_version',return_value='fixed-test-code'),patch.object(live,'diagnose',side_effect=round_source),patch('builtins.print'):
            with patch.object(live,'preflight',side_effect=[(ready,[]),(ready,[]),(pause,[])]):
                paused=live.start_batch(device=nav)
            self.assertEqual(paused['status'],'Paused for wallet');self.assertEqual(paused['started_rounds'],2)
            batch=Path(paused['batch_path']);original=(batch/'starts.jsonl').read_bytes()
            reg=(batch/'registration.json').read_bytes()
            with patch.object(live,'code_version',return_value='different'):
                with self.assertRaisesRegex(ValueError,'resume_candidate_changed'):
                    live.resume_registration(batch,live.Budget())
            (batch/'STOP').touch()
            with self.assertRaisesRegex(ValueError,'resume_requires_unstarted_wallet_pause'):
                live.resume_registration(batch,live.Budget())
            (batch/'STOP').unlink()
            with patch.object(live,'preflight',return_value=(ready,[])):
                result=live.start_batch(device=nav,resume=batch)
            self.assertTrue(result['acceptance_pass'],result)
            self.assertEqual(result['started_rounds'],10)
            self.assertEqual((batch/'registration.json').read_bytes(),reg)
            self.assertTrue((batch/'starts.jsonl').read_bytes().startswith(original))
            self.assertEqual(len(list(self.control.glob('batch_*'))),1)
            self.assertEqual(len([r for r in live.Budget().records() if r['kind']=='batch_registered']),1)
            self.assertEqual(nav.prepared,11)

    def test_replay_uses_prospective_positive_and_negative_clock_brackets(self):
        from bv_verify import content_digest
        import re
        for offset in [-5,4.5]:
            p=self.make_round('diagnostic');f=json.loads(p.read_text());log=p.parent/f['client_ref']
            def shift(m):return (dt.datetime.strptime(m[0],'%y/%m/%d %H:%M:%S.%f')+dt.timedelta(seconds=offset)).strftime('%y/%m/%d %H:%M:%S.%f')[:-3]
            log.write_text(re.sub(r'\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d+',shift,log.read_text()))
            clock=p.parent/f['clock_ref'];c=json.loads(clock.read_text());c['samples'][0]['device_ns']+=int(offset*1e9);clock.write_text(json.dumps(c))
            events,_=live.scan_range(self.index,self.source/'bv_bodies',f['source']['start'],f['source']['end'])
            f['source_digest']=content_digest(f['source'],events,[p.parent/f[k] for k in ('client_ref','actions_ref','selection_ref','config_ref','clock_ref')]);p.write_text(json.dumps(f))
            r=replay(p);self.assertEqual(r['errors'],[]);self.assertTrue(r['controlled_differential']);self.assertEqual(r['N'],1)


class RuntimeLimits(unittest.TestCase):
    def test_client_confirm_requires_actual_same_target_and_late_confirm_stops_retry(self):
        c=controller();c.first_seen[1]=1;c.dispatch_times={(1,0,0):100};c.giveup.add((1,0,0))
        e=dict(round_id='round1',card_id=1,cell_index=0,ball=1,at_ns=101,daub_type='Manual',source_ref={})
        self.assertTrue(c.accept_client_mark(e));self.assertIn((1,0,0),c.done);self.assertFalse(c.giveup)
        e['card_id']=2;self.assertFalse(c.accept_client_mark(e))

    def test_interrupted_runtime_and_actual_overspend_cannot_reset_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            b=live.Budget(folder);b.append('runtime_start',session_id='crashed')
            with patch.object(live.time,'time_ns',return_value=b.records()[0]['at_ns']+(live.LIMITS['total_seconds']+1)*10**9):
                with self.assertRaisesRegex(ValueError,'task_resource_limit'):
                    b.reserve('diagnostic',synthetic_quote(source_ref='synthetic',tickets=4,cards=4,balance=100),'next')
