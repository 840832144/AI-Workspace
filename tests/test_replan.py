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
from test_price_binding import synthetic_quote
from bv_clock import interval,matched,validate
from test_reliability import controller,grid,stabilize,cards
from test_source_binding import field


class Clocks(unittest.TestCase):
    def test_only_prospective_overlapping_brackets_are_intersected(self):
        a=self.sample(0);b=dict(a)
        b.update(host_before_ns=a['host_before_ns']+5_000_000,
                 host_after_ns=a['host_after_ns']+5_000_000)
        lo,hi=interval(a['device_ns']+1_000_000_000,[a,b])
        self.assertGreater(lo,interval(a['device_ns']+1_000_000_000,[a])[0])
        self.assertEqual(hi,interval(a['device_ns']+1_000_000_000,[a])[1])
        bad=dict(b,host_before_ns=b['host_before_ns']+100_000_000,
                 host_after_ns=b['host_after_ns']+100_000_000)
        with self.assertRaisesRegex(ValueError,'disagree'):
            interval(a['device_ns']+1_000_000_000,[a,bad])
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
    def test_reward_modal_blocks_lobby_until_bounded_dismissal(self):
        from PIL import Image,ImageDraw
        from bv_autobuy import GREEN
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'synthetic.png';im=Image.new('RGB',(900,1600));draw=ImageDraw.Draw(im)
            draw.rectangle((100,1280,350,1390),fill=GREEN)
            draw.rectangle((200,420,700,540),fill=(250,200,50))
            draw.rectangle((380,650,530,780),fill=(250,200,50))
            draw.rectangle((290,1000,600,1030),fill='white');im.save(p)
            d=live.Device()
            with patch.object(d,'foreground',return_value=True),patch.object(ap,'shot',return_value=True):
                sample=d.sample(p)
            self.assertEqual(sample['scene'],'reward')
            stop=Path(folder)/'STOP';stop.touch();d.stop_paths=(stop,)
            with patch.object(d,'foreground',return_value=True),patch.object(ap,'spawn_tap') as send:
                self.assertEqual(d.dismiss_reward(sample),'not_executed');send.assert_not_called()
            im=Image.new('RGB',(900,1600));draw=ImageDraw.Draw(im)
            draw.rectangle((330,80,580,350),fill=(250,200,50))
            draw.rectangle((300,365,600,435),fill=(250,30,20))
            draw.rectangle((280,790,640,830),fill='white');im.save(p)
            with patch.object(d,'foreground',return_value=True),patch.object(ap,'shot',return_value=True):
                level=d.sample(p)
            self.assertEqual(level['scene'],'reward');self.assertEqual(level['button'],[450,820])

    def test_late_filled_bands_cannot_shrink_measured_card(self):
        import copy
        device=live.Device();det=grid()
        for c in det:
            c.update(header_top=c['rows'][0]-60,header_bottom=c['rows'][0]-40,
                     observed_rows=list(c['rows']),row_spacing=80,spacing=80,row_mode='bands',
                     cell_geometry=dict(cols=list(c['cols']),rows=list(c['rows']),reachable_cells=list(range(25))))
        for _ in range(3):baseline=device.calibrated_grid(det)
        self.assertEqual(len(baseline),4)
        damaged=copy.deepcopy(det)
        for c in damaged:c.update(rows=[c['rows'][0]+i*45 for i in range(5)],row_mode='extent')
        repaired=device.calibrated_grid(damaged)
        self.assertEqual([c['rows']for c in repaired],[c['rows']for c in baseline])
        damaged[0]['header_top']+=20
        damaged[0]['cell_geometry']=None
        partial=device.calibrated_grid(damaged)
        self.assertFalse(partial[0]['input_ready'])
        self.assertTrue(all(c['input_ready'] for c in partial[1:]))
        c=controller()
        with patch.object(ap.time,'monotonic',return_value=10):c.on_ball('',c.rid,1)
        stabilize(c,partial,start=11);c.foreground_at=13
        with patch.object(ap.time,'monotonic',return_value=13):c.tick([])
        self.assertNotEqual(c.input_target['slot'],1)
        self.assertEqual(device.calibrated_grid([]),[])

    def test_structured_bingo_completing_target_gets_priority(self):
        c=controller()
        with patch.object(ap.time,'monotonic',return_value=10):c.on_ball('',c.rid,1)
        c.special_observed={(2,0,col)for col in range(1,5)}
        stabilize(c,grid(),start=11);c.foreground_at=13
        with patch.object(ap.time,'monotonic',return_value=13):c.tick([])
        self.assertEqual(c.input_target['slot'],2)
        self.assertFalse(c.done)  # PowerUp evidence never becomes ordinary success.
    def test_panel_navigation_ignores_green_ad_below_modal(self):
        from PIL import Image,ImageDraw
        from bv_autobuy import BLUE,GREEN
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'synthetic.png';im=Image.new('RGB',(900,1600));draw=ImageDraw.Draw(im)
            draw.rectangle((30,300,870,1250),fill=BLUE)
            draw.rectangle((300,1140,600,1220),fill=GREEN)
            draw.rectangle((480,1400,860,1580),fill=GREEN);im.save(path)
            device=live.Device()
            with patch.object(device,'foreground',return_value=True),patch.object(ap,'shot',return_value=True):
                sample=device.sample(path)
            self.assertEqual(sample['scene'],'betpanel')
            self.assertLess(abs(sample['button'][0]-450),5)
            self.assertLess(abs(sample['button'][1]-1180),5)

    def test_animated_row_band_does_not_block_other_targets(self):
        from bv_cardgrid import regular_rows
        base=[965,1043,1120,1198,1275.5]
        c=controller();c.on_ball('',c.rid,1)
        for index,shift in enumerate((14.5,14,0,14.5)):
            observed=list(base);observed[2]+=shift
            fitted=regular_rows(observed)
            self.assertIsNotNone(fitted)
            self.assertLess(max(abs(a-b) for a,b in zip(fitted,base)),1)
            geometry=grid();geometry[2]['rows']=fitted
            with patch.object(ap.time,'monotonic',return_value=10+index*.5):
                c.setup_grid(4,geometry)
        self.assertIsNotNone(c.grid)
        self.assertIsNone(regular_rows([965,1060,1134,1180,1275]))

    def test_remaining_positions_keep_both_old_reservations(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger=live.Budget(folder);q=synthetic_quote(source_ref='synthetic',tickets=4,cards=4,balance=80)
            for i in range(2):ledger.reserve('acceptance',q,'old'+str(i),'oldbatch')
            self.assertEqual(ledger.remaining_positions(),16)
            for i in range(16):ledger.reserve('acceptance',q,'new'+str(i),'newbatch')
            self.assertEqual(ledger.remaining_positions(),0)
            with self.assertRaisesRegex(ValueError,'round_count_limit'):
                ledger.reserve('acceptance',q,'forbidden','extra')
        with tempfile.TemporaryDirectory() as folder:
            ledger=live.Budget(folder)
            with patch.object(ledger,'elapsed',return_value=live.LIMITS['total_seconds']-live.LIMITS['round_seconds']+1):
                with self.assertRaisesRegex(ValueError,'remaining_time'):
                    ledger.reserve('acceptance',q,'too_late','batch')
            self.assertFalse(ledger.records())

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
                    return synthetic_quote(source_ref='synthetic',tickets=4,cards=4,balance=80,log_path='synthetic',log_start=0,sampled_at=time.monotonic())
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
            meta=dict(batch_id=batch.name,folder=str(batch),ordinal=1,code_version='synthetic',parser_version='synthetic',metric_version='synthetic',instance='synthetic',planned_rounds=10)
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
