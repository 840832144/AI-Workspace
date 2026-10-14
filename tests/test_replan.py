"""Full entry and prospective clocks; all inputs are isolated synthetic fixtures."""
import datetime as dt
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import bv_autoplay as ap
import bv_live as live
from bv_clock import interval,matched,validate
from test_reliability import controller,grid,stabilize,cards
from test_source_binding import field


class Clocks(unittest.TestCase):
    def sample(self,offset):
        return dict(host_before_ns=10_000_000_000,host_after_ns=10_020_000_000,
                    mono_before_ns=100_000_000_000,mono_after_ns=100_020_000_000,
                    device_ns=10_010_000_000-offset,boot_id='test')

    def test_signed_offsets_delay_and_no_historical_recalibration(self):
        for offset in (-5_000_000_000,4_500_000_000):
            s=self.sample(offset);validate(s)
            event=s['device_ns']+1_000_000_000;lo,hi=interval(event,[s])
            self.assertEqual((lo+hi)//2,11_010_000_000)
            self.assertTrue(matched(dict(at_ns=event,host_interval_ns=[lo,hi]),10_900_000_000))
            self.assertFalse(matched(dict(at_ns=event,host_interval_ns=[lo,hi]),11_050_000_000))
            with self.assertRaisesRegex(ValueError,'not_current'):interval(s['device_ns']-1,[s])
            with self.assertRaisesRegex(ValueError,'not_current'):interval(s['device_ns']+46_000_000_000,[s])

    def test_wall_jump_restart_and_slow_sample_refused(self):
        s=self.sample(0)
        for change in ({'host_after_ns':s['host_after_ns']+1_000_000_000},
                       {'boot_id':'restarted'}, {'device_ns':s['device_ns']+2_000_000_000}):
            with self.assertRaises(ValueError):validate(dict(s,**change),s)

    def test_native_rotation_is_not_silently_rebound(self):
        d=live.Device();d.clock_samples=[dict(mono_after_ns=time.monotonic_ns())];d.log_identity=('synthetic',1)
        with patch.object(live.subprocess,'run',return_value=SimpleNamespace(stdout=b'2:100')),patch.object(d,'read_file') as read:
            with self.assertRaisesRegex(ValueError,'rotated'):d.read_client('synthetic',20)
            read.assert_not_called()


class ContinuousTargets(unittest.TestCase):
    def test_old_target_not_starved_and_unknown_does_not_halt_other_cards(self):
        c=controller()
        with patch.object(ap.time,'monotonic',return_value=10):c.on_ball('',c.rid,1)
        with patch.object(ap.time,'monotonic',return_value=11):c.on_ball('',c.rid,2)
        stabilize(c,grid(),start=11);c.foreground_at=13
        c.observe_unmatched(dict(round_id=c.rid,card_id=1,cell_index=0,ball=1,source_ref={}))
        with patch.object(ap.time,'monotonic',return_value=13):c.tick([])
        self.assertFalse(c.halted);self.assertEqual(c.input_target['ball'],1)
        self.assertEqual(c.input_target['slot'],2);self.assertFalse(c.done)

    def test_actual_cli_full_loop_across_cards_and_early_middle_last_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source';source.mkdir();bodies=source/'bv_bodies';bodies.mkdir()
            index=source/'bv_ws.jsonl';index.touch();batch=root/'batch_test';batch.mkdir();(batch/'starts.jsonl').touch()
            rid='BINGO_HALL.synthetic.full';seq=0
            def raw(mid,body,direction='S->C'):
                nonlocal seq
                seq+=1;name=f'frame{seq}.bin';data=b'\x05\0\0\0'+seq.to_bytes(2,'little')+mid.to_bytes(3,'big')+b'\0'+body
                (bodies/name).write_bytes(data)
                rec=dict(file=name,len=len(data),dir=direction,ts=dt.datetime.now(dt.timezone.utc).isoformat(),hdr=dict(cmd=mid&255,seq=seq,flags=int.from_bytes(data[6:8],'little')))
                with index.open('a') as f:f.write(json.dumps(rec)+'\n')
            class Device:
                purchased=False;closed=False;logs=b'';last=-1
                def line(self,text):
                    stamp=dt.datetime.now(dt.timezone.utc).strftime('%y/%m/%d %H:%M:%S.%f')[:-3]
                    self.logs+=f'I:1:2:{stamp} +00:00 {text}\n'.encode()
                def sample(self,path):return dict(foreground=True,scene='round' if self.purchased else 'betpanel',grid=grid(),sampled_at=time.monotonic(),button=[1,1])
                def context(self,account,folder):
                    (folder/'selection.json').write_text(json.dumps(dict(CardCount=4,BetCount=1,LastBetTicket=4)))
                    (folder/'base_bet_config.json').write_text(json.dumps([dict(id='BET_NP_SYMBOL_1',cost=1)]))
                    return dict(source_ref='synthetic',tickets=4,cards=4,balance=80,log_path='synthetic',log_start=0,sampled_at=time.monotonic())
                def buy(self,*args):
                    self.purchased=True;self.started=time.monotonic()
                    selected=field(1,b'BET_NP_SYMBOL_1')+field(2,4)
                    raw(100042,field(2,selected),'C->S')
                    cs=b''.join(field(2,field(1,c['slot'])+b''.join(field(2,field(1,n)) for n in c['vals']))for c in cards())
                    raw(100003,field(1,field(4,field(1,cs+field(10,rid.encode())+field(11,selected)))))
                    raw(100009,field(1,rid.encode())+field(2,bytes([1,2,3])))
                    self.line('NotifyResources TICKET current=80 next=76 delta=-4')
                    self.line(f'CardLayout StartGameLogic:layoutFrame round={rid} rule=STANDARD cards=4 layout=x')
                    return 'executed'
                def read_file(self,path,offset):
                    elapsed=time.monotonic()-self.started
                    for i,due in enumerate([.1,1.5,3.1]):
                        if elapsed>=due and i>self.last:
                            self.last=i;self.line(f'[BallCaller] index {i}, num {i+1}')
                    if elapsed>5.8 and not self.closed:
                        self.closed=True;self.line('BingoPlayView GameOver');raw(100014,field(1,rid.encode()))
                    return self.logs[offset:]
            device=Device();actual=live.diagnose
            meta=dict(batch_id=batch.name,folder=str(batch),ordinal=1,code_version='synthetic',parser_version='synthetic',metric_version='synthetic',instance='synthetic')
            def entry():return actual(6.3,True,source=source,root=root,device=device,play_round=True,batch=meta,session=batch/'acceptance_test')
            wallet=dict(type='wallet_snapshot',account='synthetic',received_at=dt.datetime.now(dt.timezone.utc).isoformat(),currencies={'TICKET':80})
            check=dict(run_ready=True,purchase_ready=True,diagnostic_navigation_ready=True,blockers=[],quote={'balance':80})
            process=SimpleNamespace(communicate=lambda **kw:None,returncode=0)
            with patch.object(live,'preflight',return_value=(check,[wallet])),patch.object(live,'clean_code',return_value=True),patch.object(live,'code_version',return_value='synthetic'),patch.object(live,'start_batch',side_effect=entry),patch.object(ap,'spawn_tap',return_value=process),patch.object(ap.sys,'argv',['bv_autoplay.py','--start']),patch('builtins.print'):
                self.assertEqual(ap.main(),2)
            p=batch/'acceptance_test';actions=[json.loads(l) for l in (p/'actions.jsonl').read_text().splitlines()]
            dispatched=[e for e in actions if e['kind']=='input_dispatched']
            self.assertEqual(len(dispatched),12)
            self.assertEqual({e['slot'] for e in dispatched},{1,2,3,4});self.assertEqual({e['cell_index'] for e in dispatched},{0,1,2})
            closed=next(e['monotonic_ns'] for e in actions if e['kind']=='input_revoked' and e['reason']=='round_closed')
            self.assertTrue(all(e['monotonic_ns']<closed for e in dispatched))
            reg=json.loads((p/'registration.json').read_text());self.assertEqual(reg['mode'],'full_autoplay');self.assertEqual(reg['target_dispatch_limit'],288)
