"""Round-one regressions against imported code and the actual command entry."""
import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from concurrent.futures import Future

import bv_autoplay as ap
import bv_live as live
from test_price_binding import synthetic_quote
from bv_batch import check_batch,verify_batch,IDENTITY
from bv_evidence import aggregate,measure,decode
from test_reliability import controller,stabilize,grid,freeze,wire
from bv_client_state import terminal_cells,ClientTrace


class Deferred:
    def submit(self,fn):
        self.fn=fn;self.future=Future();return self.future


class Dispatch(unittest.TestCase):
    def queued(self):
        c=controller();c.a.dry=False;c.input_pool=Deferred()
        with patch.object(ap.time,'monotonic',return_value=10):c.on_ball('',c.rid,1)
        stabilize(c,grid(),start=10.8)
        with patch.object(ap.time,'monotonic',return_value=12):c.tick([])
        return c

    def test_deferred_real_closure_revoked_and_recovery_new_coordinates(self):
        c=self.queued()
        with patch.object(ap,'spawn_tap') as send,patch.object(ap.time,'monotonic',return_value=12):
            c.revoke('layout_changed')
            result=c.input_pool.fn();self.assertEqual(result,'cancelled');send.assert_not_called()
            c.input_future.set_result(result);c.tick([])
        self.assertEqual(c.n_tap,0);self.assertFalse(c.awaiting);self.assertFalse(c.giveup)
        stabilize(c,grid(12),start=13)
        c.foreground_at=14
        process=SimpleNamespace(communicate=lambda **kw:None,returncode=0)
        with patch.object(ap,'spawn_tap',return_value=process) as send,patch.object(ap.time,'monotonic',return_value=14):
            c.tick([]);self.assertEqual(c.input_pool.fn(),'executed')
            self.assertEqual(send.call_args.args,(92,500));self.assertEqual(c.n_tap,1)

    def test_deferred_closure_round_stop_foreground_expiry(self):
        for reason in ('round','stop','foreground','expired','version'):
            c=self.queued()
            with tempfile.TemporaryDirectory() as folder:
                c.sess=folder
                if reason=='round':c.rid='other'
                elif reason=='stop':Path(folder,'STOP').touch()
                elif reason=='foreground':c.foreground_ok=False
                elif reason=='version':c.grid[c.input_target['slot']]['version']+=1
                with patch.object(ap,'spawn_tap') as send,patch.object(ap.time,'monotonic',return_value=20 if reason=='expired' else 12):
                    self.assertEqual(c.input_pool.fn(),'cancelled',reason);send.assert_not_called()

    def test_layout_revocation_does_not_wait_for_slow_adb_completion(self):
        c=self.queued()
        import threading
        entered=threading.Event();release=threading.Event()
        p=SimpleNamespace(returncode=0,communicate=lambda **kw:(entered.set(),release.wait(2)))
        with patch.object(ap,'spawn_tap',return_value=p),patch.object(ap.time,'monotonic',return_value=12):
            t=threading.Thread(target=c.input_pool.fn);t.start();self.assertTrue(entered.wait(1))
            c.revoke('new_layout');self.assertIsNone(c.grid)
            release.set();t.join(2);self.assertFalse(t.is_alive())


def batch_fixture():
    reg=dict(batch_id='synthetic-batch',instance='synthetic-device',code_version='fixed-code',
             parser_version='fixed-parser',metric_version='fixed-metric',purpose='acceptance',
             planned_rounds=10,registered_ns=1,source_start=0)
    starts=[];results=[]
    for i in range(10):
        identity={k:reg[k] for k in IDENTITY}
        start=dict(**identity,ordinal=i+1,session_id=f's{i}',frozen_ref=f's{i}/round.json',
                   started_ns=10+i*10,source_start=i*100)
        r=dict(**identity,session_id=f's{i}',round_id=f'r{i}',frozen_ref=start['frozen_ref'],
               cardset_ref=f'raw:{i}',sources_rebuilt=True,ended_ns=19+i*10,
               source_start=i*100,source_end=(i+1)*100,status='verified_lower_bound',
               N=19,E=20,Unknown=1,confirmed_unfilled=0)
        starts.append(start);results.append(r)
    return reg,starts,results


class Provenance(unittest.TestCase):
    def test_synthetic_production_entry_rejects_and_formula_separate(self):
        f=freeze();r=measure(f)
        self.assertTrue(r['arithmetic_pass']);self.assertFalse(r['acceptance_pass'])
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'fixture.json';p.write_text(json.dumps(f))
            for label in ('synthetic','observed-live'):
                f['evidence_kind']=label;p.write_text(json.dumps(f))
                with patch.object(ap.sys,'argv',['bv_autoplay.py','--results',str(p)]),patch('builtins.print'):
                    self.assertEqual(ap.main(),2)
        r['evidence_kind']='observed-live'
        self.assertFalse(aggregate([r]*10)['qualified'])

    def test_ten_distinct_fixtures_arithmetic_pass_not_live_acceptance(self):
        reg,starts,rs=batch_fixture();r=check_batch(reg,starts,rs)
        self.assertTrue(r['qualified']);self.assertTrue(r['arithmetic_pass'])
        self.assertEqual(r['weighted_rate'],.95);self.assertTrue(r['optimization_arithmetic_pass'])
        self.assertFalse(r['acceptance_pass'])
        rs[-1].update(N=1,E=100,Unknown=99)
        r=check_batch(reg,starts,rs);self.assertEqual(r['weighted_rate'],172/280)
        self.assertFalse(r['arithmetic_pass'])

    def test_duplicate_missing_cross_instance_mixed_version_and_takeover(self):
        for key,value in (('round_id','r0'),('code_version','changed'),('instance','other'),
                          ('sources_rebuilt',False),('manual_takeover',True),('N',99),
                          ('cardset_ref',None),('ended_ns',1),('source_start',0)):
            reg,starts,rs=batch_fixture();rs[-1][key]=value
            self.assertFalse(check_batch(reg,starts,rs)['qualified'],key)
        reg,starts,rs=batch_fixture()
        self.assertFalse(check_batch(reg,starts,rs[:-1])['qualified'])
        self.assertFalse(check_batch(reg,starts[:-1],rs[:-1])['qualified'])
        self.assertFalse(check_batch({},starts,rs)['qualified'])
        with tempfile.TemporaryDirectory() as folder:
            self.assertFalse(verify_batch(Path(folder))['qualified'])

    def test_full_message_id_prevents_low_byte_collision(self):
        data,rec=wire();data=data[:6]+bytes([0,1])+data[8:]
        rec['hdr']['flags']=256
        self.assertEqual(decode(data,rec,{})['type'],'frame') # full 425 is not call-ball 100009


class EntryAndBudget(unittest.TestCase):
    def test_terminal_has_25_cells_and_free_is_not_a_target(self):
        blocks=[]
        for card in range(4):
            cells=['']*25;cells[12]='1::'
            if card in (0,3):cells[15]='1::'
            cells[10]=':8:'
            blocks.append('|'.join(cells))
        state=blocks[0]+'@15.1.2#'+blocks[1]+'@#'+blocks[2]+'@#'+blocks[3]+'@'
        self.assertEqual(len(state.split('|')),97)
        decoded=terminal_cells(state)
        self.assertEqual(len(decoded),100)
        self.assertEqual({k for k,v in decoded.items()if v['marked'] and k[1]!=12},{(1,15),(4,15)})
        self.assertFalse(decoded[(1,10)]['marked'])
        self.assertEqual(terminal_cells(state+'11.2.1,6.8.1,21.4.1'),decoded)
        dotted=state.replace('1::','1:13.3:',1)
        result=terminal_cells(dotted)
        changed=[k for k in result if result[k]!=decoded[k]]
        self.assertEqual(len(changed),1)
        self.assertEqual(result[changed[0]],dict(marked=True,special=True))
        for token in ['2::','1:13..3:','1:unknown:']:
            with self.assertRaisesRegex(ValueError,'state_cell_semantics_unknown'):
                terminal_cells(state.replace('1::',token,1))
        with self.assertRaisesRegex(ValueError,'state_card_boundaries'):
            terminal_cells(state+'unrecognized')

    def test_client_trace_partial_lines_call_and_accepted_mark_are_distinct(self):
        trace=ClientTrace('synthetic','r')
        prefix=b'I:1:2:26/10/13 19:00:00.001 +08:00 '
        chunk=prefix+b'[BallCaller] cur 1 target 1 index 0, num 1 diff 0\n'
        self.assertEqual(trace.feed(chunk[:20]),[])
        event=trace.feed(chunk[20:])[0];self.assertEqual(event['type'],'client_called')
        mark=trace.feed(prefix+b'BingoLog: Daub Type Manual, Index: 0, 1, (0,0), Mod None\n')[0]
        self.assertEqual((mark['card_id'],mark['cell_index']),(1,0))
        self.assertEqual(mark['source_ref']['offset'],len(chunk))
        power=trace.feed(prefix+b'BingoLog: Daub Type PowerUp BoostID B_DAUB_TWO, Index: 2, 51, (2,3), Mod DOUBLE_XP, 1\n')[0]
        self.assertEqual((power['daub_type'],power['card_id'],power['cell_index']),('PowerUp',3,17))

    def test_actual_entry_buy_bind_wait_calibrate_dispatch_and_freeze(self):
        from test_reliability import cards
        def varint(n):
            out=bytearray()
            while n>127:out.append((n&127)|128);n>>=7
            out.append(n);return bytes(out)
        def fld(k,v):
            return varint(k*8)+varint(v) if isinstance(v,int) else varint(k*8+2)+varint(len(v))+v
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'source';source.mkdir();bodies=source/'bv_bodies';bodies.mkdir()
            index=source/'bv_ws.jsonl';index.write_bytes(b'');rid=b'BINGO_HALL.synthetic.1'
            def append(mid,body,num):
                data=b'\x05\x00\x00\x00'+num.to_bytes(2,'little')+mid.to_bytes(3,'big')+b'\x00'+body
                name=f'fixture{num}.bin';(bodies/name).write_bytes(data)
                rec=dict(file=name,len=len(data),dir='S->C',ts='2026-10-13 19:00:00',
                         hdr=dict(cmd=mid&255,seq=num,flags=int.from_bytes(data[6:8],'little')))
                with index.open('a')as f:f.write(json.dumps(rec)+'\n')
            class FakeDevice:
                purchased=False
                def foreground(self):return True
                def sample(self,path):
                    return dict(foreground=True,scene='round' if self.purchased else 'betpanel',
                                grid=grid() if self.purchased else [],sampled_at=time.monotonic(),button=[447,1180])
                def context(self,account,folder):
                    return synthetic_quote(source_ref='synthetic',tickets=4,cards=4,balance=81,log_path='synthetic',
                                log_start=0,sampled_at=time.monotonic())
                def buy(self,sample,quote):
                    self.purchased=True
                    cs=b''.join(fld(2,fld(1,slot['slot'])+b''.join(fld(2,fld(1,n))for n in slot['vals']))for slot in cards())
                    own=cs+fld(10,rid)+fld(11,fld(1,b'BET_NP_SYMBOL_1')+fld(2,4))
                    append(100003,fld(1,fld(4,fld(1,own))),1)
                    append(100009,fld(1,rid)+fld(2,bytes([1,2,3,4,5])),2)
                    return 'executed'
                def read_file(self,path,offset):
                    log=(b'I:1:2:26/10/13 19:00:00.000 +08:00 CardLayout StartGameLogic:layoutFrame round=BINGO_HALL.synthetic.1 rule=STANDARD cards=4 layout=x\n'
                         b'I:1:2:26/10/13 19:00:00.001 +08:00 [BallCaller] cur 1 target 1 index 0, num 1 diff 0\n'
                         b'I:1:2:26/10/13 19:00:00.002 +08:00 NotifyResources TICKET current=81 next=77 delta=-4\n')
                    return log[offset:]
            original=live.diagnose
            def route(seconds,open_panel,**kw):return original(seconds,open_panel,source=source,root=root/'run',device=FakeDevice(),**kw)
            check=dict(diagnostic_navigation_ready=True,purchase_ready=True,blockers=[],quote={'balance':81})
            process=SimpleNamespace(communicate=lambda **kw:None,returncode=0)
            wallet=dict(type='wallet_snapshot',account='synthetic',received_at='2026-10-13T19:00:00+08:00',currencies={'TICKET':81})
            with patch.object(live,'clean_code',return_value=True),patch.object(live,'preflight',return_value=(check,[wallet])),patch.object(live,'diagnose',side_effect=route),patch.object(ap,'spawn_tap',return_value=process)as send,patch.object(ap.sys,'argv',['bv_autoplay.py','--diagnose','--diagnostic-round','--seconds','2.6']),patch('builtins.print'):
                self.assertEqual(ap.main(),2)
            session=next((root/'run').glob('diagnostic_*'));r=json.loads((session/'result.json').read_text())
            self.assertTrue(r['round_bound']);self.assertEqual(r['input_dispatched'],1)
            self.assertEqual(r['gross_tickets'],4);self.assertEqual(r['capture_errors'],{})
            self.assertEqual(send.call_count,1)
            actions=[json.loads(l)for l in (session/'actions.jsonl').read_text().splitlines()]
            self.assertEqual([x['cell_index']for x in actions if x['kind']=='input_dispatched'],[0])
            self.assertFalse(r.get('acceptance_pass'))

    def test_actual_main_diagnostic_loop_collects_and_stops_without_buy(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'source';source.mkdir();(source/'bv_bodies').mkdir()
            (source/'bv_ws.jsonl').write_bytes(b'')
            class FakeDevice:
                def foreground(self):return True
                def sample(self,path):return dict(foreground=True,scene='unknown',grid=None,sampled_at=time.monotonic())
            original=live.diagnose
            def route(seconds,open_panel,**kw):
                return original(seconds,open_panel,source=source,root=root/'run',device=FakeDevice(),**kw)
            with patch.object(live,'preflight',return_value=({'diagnostic_navigation_ready':True,'purchase_ready':False,'blockers':['quote_missing']},[])),patch.object(live,'diagnose',side_effect=route),patch.object(ap.sys,'argv',['bv_autoplay.py','--diagnose','--seconds','.2']),patch('builtins.print'):
                self.assertEqual(ap.main(),2)
            sessions=list((root/'run').glob('diagnostic_*'));self.assertEqual(len(sessions),1)
            r=json.loads((sessions[0]/'result.json').read_text())
            self.assertEqual(r['rounds_started'],0);self.assertTrue(r['stopped_confirmed'])
            self.assertTrue((sessions[0]/'events.json').exists())

    def test_shared_budget_requires_sources_counts_failed_attempts_and_no_netting(self):
        with tempfile.TemporaryDirectory() as folder:
            b=live.Budget(folder)
            with self.assertRaises(ValueError):b.reserve('diagnostic',None,'s')
            quote=synthetic_quote(source_ref='synthetic',tickets=8,cards=4,balance=96)
            b.reserve('diagnostic',quote,'d1');b.reserve('diagnostic',quote,'d2')
            b.reserve('diagnostic',quote,'d3')
            with self.assertRaisesRegex(ValueError,'round_count_limit'):b.reserve('diagnostic',quote,'d4')
            for i in range(18):b.reserve('acceptance',quote,str(i))
            b.append('reward',tickets=100)
            with self.assertRaises(ValueError):b.reserve('acceptance',quote,'extra')
            self.assertEqual(sum(r.get('reserved_tickets',0) for r in b.records()),168)


if __name__=='__main__':unittest.main()
