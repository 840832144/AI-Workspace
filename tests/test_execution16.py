"""Prospective 16T authorization through the actual entry; all sources synthetic."""
import contextlib
import json
from pathlib import Path
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import bv_live as live
from bv_batch import check_batch
import test_price_binding as price
synthetic_quote=price.synthetic_quote


def historical_budget(folder):
    b=live.Budget(folder)
    for i in range(3):b.append('purchase_reserved',purpose='diagnostic',session_id=f'd{i}',reserved_tickets=4)
    for i in range(8):b.append('purchase_reserved',purpose='acceptance',session_id=f'p{i}',reserved_tickets=4)
    b.append('resource_observed',session_id='p7',tickets=12)
    b.append('runtime_start',session_id='historical')
    b.append('runtime_end',session_id='historical',seconds=2267.262)
    return b


class Execution16(unittest.TestCase):
    def test_single_minimum_quote_12_and_16_reaches_final_buy(self):
        for cost in (12,16):
            with tempfile.TemporaryDirectory() as folder,contextlib.ExitStack() as stack:
                root=Path(folder);(root/'bv_ws.jsonl').touch();(root/'bv_bodies').mkdir()
                stack.enter_context(patch.object(live,'CONTROL',root))
                d=price.PriceBinding().fixture(stack,root)
                q=synthetic_quote(tickets=cost,balance=80)
                stack.enter_context(patch.object(d,'context',return_value=q))
                pre,_=live.preflight(root,d,remaining_rounds=1)
                self.assertTrue(pre['run_ready'],pre['blockers'])
                b=live.Budget(root);b.reserve('acceptance',q,'future')
                process=SimpleNamespace(communicate=lambda **kw:None,returncode=0)
                with patch('bv_autoplay.spawn_tap',return_value=process) as send:
                    self.assertEqual(d.buy(dict(scene='betpanel',sampled_at=time.monotonic(),button=[1,1]),q),'executed')
                    send.assert_called_once()
                self.assertEqual(b.records()[0]['resource_authorization'],live.RESOURCE_AUTHORIZATION)

    def test_limit_and_current_minimum_are_independent(self):
        for cost in (17,20):
            with self.assertRaises(ValueError):synthetic_quote(tickets=cost)
        q=synthetic_quote(tickets=16);read=q._read_snapshot
        q._config.append(dict(id='BET_NP_SYMBOL_1',cost=1))
        q._read_snapshot=lambda:dict(read(),available_bets=['BET_NP_SYMBOL_1','BET_NP_SYMBOL_4'])
        with self.assertRaisesRegex(ValueError,'configuration_or_price_invalid'):q.recheck()

    def test_original_ledger_and_entire_batch_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            b=historical_budget(folder);before=b.path.read_bytes()
            self.assertEqual((b.gross(),b.remaining_positions()),(52,10))
            for cost,deficit in ((4,0),(8,36),(12,76),(16,116)):
                p=b.batch_plan(synthetic_quote(tickets=cost,balance=200))
                self.assertEqual(p['deficits']['tickets'],deficit)
                self.assertEqual(p['fits'],cost==4)
                self.assertEqual(p['required_seconds'],3030)
                self.assertAlmostEqual(p['available_seconds'],live.LIMITS['total_seconds']-2267.262)
            self.assertEqual(b.path.read_bytes(),before)
            with self.assertRaisesRegex(ValueError,'batch_budget_insufficient'):
                b.reserve('acceptance',synthetic_quote(tickets=12,balance=200),'new',remaining_rounds=10)
            self.assertEqual(b.path.read_bytes(),before)

    def test_total_time_gross_and_position_boundaries(self):
        with tempfile.TemporaryDirectory() as folder:
            b=historical_budget(folder);q=synthetic_quote(balance=200)
            for i in range(10):b.reserve('acceptance',q,f'new{i}')
            self.assertEqual((b.gross(),b.remaining_positions()),(92,0))
            with self.assertRaisesRegex(ValueError,'round_count_limit'):b.reserve('acceptance',q,'position19')
        with tempfile.TemporaryDirectory() as folder:
            b=live.Budget(folder);b.append('purchase_reserved',purpose='acceptance',session_id='history',reserved_tickets=92)
            b.reserve('acceptance',q,'exact96')
            with self.assertRaisesRegex(ValueError,'task_resource_limit'):b.reserve('acceptance',q,'over96')
        with tempfile.TemporaryDirectory() as folder:
            b=live.Budget(folder)
            with patch.object(b,'elapsed',return_value=live.LIMITS['total_seconds']):
                with self.assertRaisesRegex(ValueError,'task_resource_limit'):b.reserve('acceptance',q,'time')
            with patch.object(b,'elapsed',return_value=live.LIMITS['total_seconds']-300+1):
                with self.assertRaisesRegex(ValueError,'remaining_time'):b.reserve('acceptance',q,'time')
            with patch.object(b,'elapsed',return_value=live.LIMITS['total_seconds']-3030+1):
                self.assertEqual(b.batch_plan(q)['deficits']['seconds'],1)
            self.assertFalse(b.records())

    def test_time_extension_keeps_old_policy_and_all_other_caps(self):
        old=live.RESOURCE_POLICIES['execution-16t-20261014']
        self.assertEqual(old['total_seconds'],5400)
        self.assertEqual(live.LIMITS,dict(old,total_seconds=6000))
        self.assertEqual(live.frozen_ticket_limit(dict(
            resource_authorization='execution-16t-20261014',limits=dict(old))),16)
        with self.assertRaisesRegex(ValueError,'authorization_mismatch'):
            live.frozen_ticket_limit(dict(resource_authorization='execution-16t-20261014',limits=dict(live.LIMITS)))

    def test_start_entry_insufficient_total_has_no_registration_or_purchase(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);b=historical_budget(root);old=b.path.read_bytes()
            cls=live.Budget;q=synthetic_quote(tickets=12,balance=200)
            check=dict(run_ready=True,blockers=[],quote=q)
            with patch.object(live,'CONTROL',root),patch.object(live,'Budget',side_effect=lambda root=None:cls(root or folder)),patch.object(live,'clean_code',return_value=True),patch.object(live,'preflight',return_value=(check,[])),patch.object(live,'diagnose') as play:
                r=live.start_batch(device=object())
                play.assert_not_called()
            self.assertFalse(r['acceptance_pass']);self.assertEqual(r['started_rounds'],0)
            self.assertIn('batch_budget_insufficient',r['errors'])
            self.assertFalse(list(root.glob('batch_*/registration.json')))
            self.assertEqual(len([x for x in b.records() if x['kind']=='purchase_reserved']),11)
            self.assertTrue(b.path.read_bytes().startswith(old))

    def test_new_ten_positions_are_9_through_18(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);b=historical_budget(root);cls=live.Budget
            (root/'bv_ws.jsonl').touch()
            check=dict(run_ready=True,blockers=[],quote=synthetic_quote(balance=200))
            def stop(*args,**kw):return dict(rounds_started=0,errors=['synthetic_stop_before_purchase'])
            with patch.object(live,'CONTROL',root),patch.object(live,'SOURCE',root),patch.object(live,'Budget',side_effect=lambda root=None:cls(root or folder)),patch.object(live,'clean_code',return_value=True),patch.object(live,'preflight',return_value=(check,[])),patch.object(live,'diagnose',side_effect=stop),patch('builtins.print'):
                live.start_batch(device=SimpleNamespace())
            r=json.loads(next(root.glob('batch_*/registration.json')).read_text())
            self.assertEqual(r['positions'],list(range(9,19)))
            self.assertEqual(r['planned_rounds'],10)

    def test_spend_mismatch_both_directions_and_historical_cap(self):
        for quote,actual in ((4,12),(12,8),(16,17),(16,0)):
            with self.assertRaises(ValueError):live.validate_spend(quote,actual)
        live.validate_spend(16,16)
        self.assertEqual(live.frozen_ticket_limit({}),8)
        metadata=dict(resource_authorization=live.RESOURCE_AUTHORIZATION,limits=dict(live.LIMITS))
        self.assertEqual(live.frozen_ticket_limit(metadata),16)
        metadata['limits']['gross_tickets']=132
        with self.assertRaisesRegex(ValueError,'authorization_mismatch'):live.frozen_ticket_limit(metadata)

    def test_actual_full_loop_stops_on_under_and_over_debit(self):
        for quote_cost,actual in ((4,12),(12,8)):
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder);source=root/'source';source.mkdir();(source/'bv_bodies').mkdir();(source/'bv_ws.jsonl').touch()
                batch=root/'batch_synthetic';batch.mkdir();(batch/'starts.jsonl').touch()
                class Device:
                    purchased=False
                    def sample(self,path):return dict(foreground=True,scene='unknown' if self.purchased else 'betpanel',sampled_at=time.monotonic(),grid=[],button=[1,1])
                    def context(self,*args):return synthetic_quote(tickets=quote_cost,balance=200,log_start=0,log_path='synthetic')
                    def buy(self,*args):self.purchased=True;return 'executed'
                    def read_file(self,path,offset):
                        log=f'I:1:2:26/10/14 12:00:00.000 +08:00 NotifyResources TICKET current=200 next={200-actual} delta=-{actual}\n'.encode()
                        return log[offset:]
                wallet=dict(type='wallet_snapshot',account='synthetic',received_at='2026-10-14T12:00:00+08:00',currencies={'TICKET':200})
                check=dict(run_ready=True,purchase_ready=True,diagnostic_navigation_ready=True,blockers=[])
                meta=dict(batch_id=batch.name,folder=str(batch),ordinal=10,planned_rounds=10,code_version='test',parser_version='test',metric_version='test',instance='test')
                with patch.object(live,'preflight',return_value=(check,[wallet])),patch.object(live,'clean_code',return_value=True),patch.object(live,'code_version',return_value='test'),patch('bv_autoplay.spawn_tap') as tap:
                    result=live.diagnose(1,True,source=source,root=root,device=Device(),play_round=True,batch=meta,session=batch/'acceptance_test')
                    tap.assert_not_called()
                self.assertIn('actual_spend_mismatch',result['errors'])
                self.assertEqual(result['gross_tickets'],actual)
                self.assertTrue(result['stopped_confirmed'])
                self.assertEqual(sum(e['kind']=='purchase_reserved' for e in live.Budget(root).records()),1)

    def test_batch_cannot_mix_or_relabel_resource_policy(self):
        # Structural checker must reject policy mismatches even before source verification.
        reg=dict(purpose='acceptance',planned_rounds=10,resource_authorization=live.RESOURCE_AUTHORIZATION,limits=dict(live.LIMITS))
        result=check_batch(reg,[{}],[{}])
        self.assertIn('mixed_resource_authorization',result['errors'])
        reg['limits']['tickets_per_round']=20
        self.assertIn('batch_resource_authorization_invalid',check_batch(reg,[],[])['errors'])
