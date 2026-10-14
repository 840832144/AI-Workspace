"""Round 2: batch STOP at send, timezone ordering, unchanged cumulative limits."""
import datetime as dt
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import bv_autoplay as ap
import bv_live as live
from test_price_binding import synthetic_quote
from bv_verify import timestamp
import test_review_r1 as r1


class StopTests(unittest.TestCase):
    def test_batch_stop_after_queue_reaches_actual_deferred_closure(self):
        c=r1.Dispatch().queued()
        with tempfile.TemporaryDirectory() as folder:
            stop=Path(folder)/'STOP';c.a.batch_stop_path=str(stop)
            stop.touch()
            with patch.object(ap.time,'monotonic',return_value=12),patch.object(ap,'spawn_tap') as send:
                self.assertEqual(c.input_pool.fn(),'cancelled');send.assert_not_called()
        self.assertEqual(c.n_tap,0)

    def test_stop_during_foreground_read_cancels_all_navigation_sends(self):
        with tempfile.TemporaryDirectory() as folder:
            stop=Path(folder)/'STOP';device=live.Device();device.stop_paths=(stop,)
            for method,scene in [('open_panel','lobby'),('buy','betpanel'),('claim','congrats')]:
                stop.unlink(missing_ok=True)
                sample=dict(scene=scene,sampled_at=time.monotonic(),button=[1,1])
                def foreground():stop.touch();return True
                with patch.object(device,'foreground',side_effect=foreground),patch.object(ap,'spawn_tap') as send:
                    args=(sample,synthetic_quote()) if method=='buy' else (sample,)
                    self.assertEqual(getattr(device,method)(*args),'not_executed');send.assert_not_called()

    def test_stop_during_quote_read_main_loop_never_reserves_or_buys(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'source';source.mkdir();(source/'bv_bodies').mkdir();(source/'bv_ws.jsonl').touch()
            batch=root/'batch_synthetic';batch.mkdir();(batch/'starts.jsonl').touch()
            session=batch/'acceptance_synthetic'
            class Device:
                def sample(self,path):return dict(scene='betpanel',foreground=True,sampled_at=time.monotonic(),grid=[],button=[1,1])
                def context(self,account,session):
                    (batch/'STOP').touch()
                    return dict(tickets=4,cards=4,source_ref='synthetic',log_path='synthetic',log_start=0)
                def read_file(self,*args):return b''
                def buy(self,*args):raise AssertionError('STOP must cancel before buy')
            metadata=dict(batch_id=batch.name,code_version='test',parser_version='test',metric_version='test',instance='test',ordinal=1,folder=str(batch),planned_rounds=10)
            wallet=dict(type='wallet_snapshot',account='synthetic',received_at='2026-10-14T00:00:00Z',currencies={'TICKET':80})
            check=dict(purchase_ready=True,diagnostic_navigation_ready=True,blockers=[],quote={'balance':80})
            with patch.object(live,'clean_code',return_value=True),patch('bv_verify.semantic_gate',return_value={'qualified':True}),patch.object(live,'preflight',return_value=(check,[wallet])):
                result=live.diagnose(.5,True,source=source,root=root,device=Device(),play_round=True,batch=metadata,session=session)
            self.assertTrue(result['stop_requested']);self.assertEqual(result['rounds_started'],0)
            self.assertFalse(any(r['kind']=='purchase_reserved' for r in live.Budget(root).records()))


class TimeAndLimits(unittest.TestCase):
    def test_preflight_preserves_timezone_and_resource_recency(self):
        moment=int(dt.datetime(2026,10,14,tzinfo=dt.timezone.utc).timestamp()*1e9)
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder);(source/'bv_ws.jsonl').touch()
            for stamp,legacy in [('2026-10-14T00:00:00Z',None),('2026-10-14T08:00:00+08:00',None),('2026-10-14 08:00:00','+08:00')]:
                for offset,expected in [(-60,80),(60,70)]:
                    class Device:
                        def foreground(self):return True
                        def context(self,*args):return dict(last_ticket_change=dict(at_ns=moment+offset*10**9,after=70))
                    wallet=dict(type='wallet_snapshot',account='synthetic',received_at=stamp,legacy_timezone=legacy,currencies={'TICKET':80})
                    with patch.object(live,'CONTROL',source),patch.object(live,'scan_range',return_value=([wallet],{})),patch('bv_verify.semantic_gate',return_value={'qualified':False}):
                        result,_=live.preflight(source,Device())
                    self.assertEqual(result['quote']['balance'],expected)
            with self.assertRaisesRegex(ValueError,'timezone_unknown'):timestamp({'received_at':'2026-10-14 08:00:00'})

    def test_existing_ledger_allows_third_but_not_fourth_without_reset(self):
        with tempfile.TemporaryDirectory() as folder:
            b=live.Budget(folder);q=synthetic_quote(source_ref='synthetic',tickets=4,cards=4,balance=100)
            b.reserve('diagnostic',q,'old1');b.reserve('diagnostic',q,'old2')
            b.append('runtime_start',session_id='old');b.append('runtime_end',session_id='old',seconds=309.061)
            before=b.path.read_bytes();b.reserve('diagnostic',q,'new3')
            self.assertTrue(b.path.read_bytes().startswith(before));self.assertAlmostEqual(b.elapsed(),309.061)
            with self.assertRaisesRegex(ValueError,'round_count_limit'):b.reserve('diagnostic',q,'forbidden4')
            self.assertEqual(sum(r.get('reserved_tickets',0) for r in b.records()),12)
            self.assertEqual((live.LIMITS['gross_tickets'],live.LIMITS['total_seconds']),(96,6000))


class SpecialObservations(unittest.TestCase):
    def test_powerup_cancels_queued_input_without_confirming_or_hiding_target(self):
        c=r1.Dispatch().queued()
        event=dict(round_id=c.rid,card_id=1,cell_index=0,ball=1,at_ns=1,daub_type='PowerUp',source_ref={})
        self.assertTrue(c.accept_client_mark(event));self.assertFalse(c.done)
        with patch.object(ap.time,'monotonic',return_value=12),patch.object(ap,'spawn_tap') as send:
            result=c.input_pool.fn();self.assertEqual(result,'cancelled');send.assert_not_called()
            c.input_future.set_result(result);c.tick([])
        self.assertNotIn((1,0,0),{(q['slot'],q['r'],q['c']) for q in c.pending+c.awaiting})
        self.assertEqual(len(__import__('bv_evidence').expected_cells(c.cards,[1])),4)
        c.backfill();self.assertNotIn((1,0,0),{(q['slot'],q['r'],q['c']) for q in c.pending})
        event['ball']=75;self.assertFalse(c.accept_client_mark(event))
        event.update(ball=1,daub_type='Manual');self.assertFalse(c.accept_client_mark(event))
