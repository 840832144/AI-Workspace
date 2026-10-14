"""Synthetic regression of position 8: persisted Bet1 can buy live Bet3.

No real device inputs. Historical cost proof is deliberately allowed to succeed;
it still must not authorize purchase from an unbound current panel.
"""
import contextlib
import json
from pathlib import Path
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import bv_autoplay as ap
import bv_live as live


def synthetic_quote(**extra):
    """Isolated observer for legacy arithmetic/entry fixtures, never a live tag."""
    tickets=extra.get('tickets',4);symbol='BET_NP_SYMBOL_'+str(tickets//4)
    def read():
        return dict(instance='synthetic',epoch='test-boot',panel_id='test-panel',revision=1,
          config_version='test-config',mode='ordinary',cards=4,bet_symbol=symbol,tickets=tickets,price_effects=[],
          available_bets=[symbol],active=True,observed_mono=time.monotonic(),source_ref='synthetic')
    q=live.PanelQuote(read,[dict(id=symbol,cost=tickets//4)],'synthetic','test-config')
    q.update(extra);return q


class PriceBinding(unittest.TestCase):
    def test_caller_label_cannot_authorize_reserve_or_final_input(self):
        q=dict(source_ref='synthetic',tickets=4,cards=4,balance=80,
               sampled_at=time.monotonic(),price_scope='current_panel',verified=True)
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError,'current_panel_quote_unavailable'):
                live.Budget(folder).reserve('acceptance',q,'fake')
            d=live.Device()
            with patch.object(d,'foreground',return_value=True),patch.object(ap,'spawn_tap') as send:
                self.assertEqual(d.buy(dict(scene='betpanel',sampled_at=time.monotonic(),button=[1,1]),q),'not_executed')
                send.assert_not_called()

    def test_bound_quote_positive_then_panel_revision_invalidates(self):
        q=synthetic_quote(balance=80);d=live.Device();qread=q._read_snapshot
        with tempfile.TemporaryDirectory() as folder,contextlib.ExitStack() as stack:
            root=Path(folder);(root/'bv_ws.jsonl').touch();(root/'bv_bodies').mkdir()
            d=self.fixture(stack,root)
            stack.enter_context(patch.object(d,'context',return_value=q))
            pre,_=live.preflight(root,d)
            self.assertTrue(pre['purchase_ready']);self.assertTrue(pre['run_ready'])
            self.assertIs(pre['quote'],q)
            b=live.Budget(folder);b.reserve('acceptance',pre['quote'],'test')
            p=SimpleNamespace(communicate=lambda **kw:None,returncode=0)
            sample=dict(scene='betpanel',sampled_at=time.monotonic(),button=[1,1])
            with patch.object(d,'foreground',return_value=True),patch.object(ap,'spawn_tap',return_value=p) as send:
                self.assertEqual(d.buy(sample,q),'executed');send.assert_called_once()
            for change in [dict(revision=2),dict(panel_id='different'),dict(epoch='restart'),
                           dict(cards=1),dict(bet_symbol='BET_NP_SYMBOL_3',tickets=12),
                           dict(price_effects=['discount']),dict(mode='event'),dict(config_version='changed'),dict(active=False)]:
                q._read_snapshot=lambda:dict(qread(),**change)
                with self.assertRaises(ValueError):b.reserve('acceptance',q,'stale')
                with patch.object(d,'foreground',return_value=True),patch.object(ap,'spawn_tap') as send:
                    self.assertEqual(d.buy(sample,q),'not_executed');send.assert_not_called()
            self.assertEqual(len([r for r in b.records() if r['kind']=='purchase_reserved']),1)

    def test_panel_changes_during_foreground_read_prevent_final_input(self):
        q=synthetic_quote(balance=80);read=q._read_snapshot;d=live.Device()
        def foreground():
            q._read_snapshot=lambda:dict(read(),revision=2)
            return True
        with patch.object(d,'foreground',side_effect=foreground),patch.object(ap,'spawn_tap') as send:
            self.assertEqual(d.buy(dict(scene='betpanel',sampled_at=time.monotonic(),button=[1,1]),q),'not_executed')
            send.assert_not_called()

    def test_snapshot_lifetime_and_quote_mutation(self):
        q=synthetic_quote(balance=80)
        q['tickets']=8
        with self.assertRaisesRegex(ValueError,'changed_or_expired'):q.recheck()
        q=synthetic_quote(balance=80)
        with patch.object(live.time,'monotonic',return_value=q['sampled_at']+3):
            with self.assertRaisesRegex(ValueError,'changed_or_expired'):q.recheck()

    def fixture(self, stack, root):
        d=live.Device()
        d.clock_samples=[dict(mono_after_ns=time.monotonic_ns())]
        config=[dict(id='BET_NP_SYMBOL_'+str(n),cost=n) for n in (1,2,3)]
        files={'gds_version.txt':b'a'*32,
               'buy_card_data.json':json.dumps(dict(CardCount=4,BetCount=1,
                   LastBetTicket=4,BetIndex=0,Dirty=True)).encode(),
               'discount_buff_local_data.json':b'{"IsActivated":false}',
               'BaseBetConfig.json':json.dumps(config).encode(),
               '2026_10_14.txt':b''}
        stack.enter_context(patch.object(d,'clock_sample'))
        stack.enter_context(patch.object(d,'foreground',return_value=True))
        stack.enter_context(patch.object(d,'read_file',side_effect=lambda p:files[p.rsplit('/',1)[-1]]))
        stack.enter_context(patch.object(live.subprocess,'run',return_value=SimpleNamespace(stdout=b'2026_10_14.txt\n',returncode=0)))
        stack.enter_context(patch.object(live,'cost_proof',return_value='historical_Bet1_cost_4'))
        stack.enter_context(patch.object(live,'clean_code',return_value=True))
        stack.enter_context(patch('bv_verify.semantic_gate',return_value={'qualified':True}))
        wallet=dict(type='wallet_snapshot',account='synthetic',received_at='2026-10-14T00:00:00Z',currencies={'TICKET':80})
        stack.enter_context(patch.object(live,'scan_range',return_value=([wallet],{})))
        stack.enter_context(patch.object(live,'CONTROL',root))
        return d

    def test_persisted_quote_never_reserves_or_reaches_final_tap(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.ExitStack() as stack:
            root=Path(tmp);d=self.fixture(stack,root)
            q=d.context('synthetic',root);q['balance']=80
            self.assertEqual(q['tickets'],4)
            self.assertEqual(q['price_scope'],'persisted_selection_only')
            with self.assertRaisesRegex(ValueError,'current_panel_quote_unavailable'):
                live.Budget(root).reserve('acceptance',q,'would_buy_12')
            self.assertFalse(live.Budget(root).records())
            with patch.object(ap,'spawn_tap') as send:
                self.assertEqual(d.buy(dict(scene='betpanel',sampled_at=time.monotonic(),button=[1,1]),q),'not_executed')
                send.assert_not_called()

    def test_real_preflight_and_cli_full_entry_refuse_stale_selection(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.ExitStack() as stack:
            root=Path(tmp);(root/'bv_ws.jsonl').touch();(root/'bv_bodies').mkdir()
            d=self.fixture(stack,root)
            checked,_=live.preflight(root,d)
            self.assertFalse(checked['run_ready']);self.assertFalse(checked['purchase_ready'])
            self.assertTrue(checked['metric_ready'])
            self.assertIn('current_panel_quote_unavailable',checked['blockers'])
            budget_class=live.Budget;actual_start=live.start_batch
            stack.enter_context(patch.object(live,'Budget',side_effect=lambda root=root:budget_class(root)))
            stack.enter_context(patch.object(live,'SOURCE',root))
            stack.enter_context(patch.object(live,'code_version',return_value='synthetic'))
            # Real CLI -> batch -> diagnose -> preflight -> production context.
            def entry():
                r=actual_start(device=d)
                self.assertFalse(r['acceptance_pass'])
                self.assertEqual(r['started_rounds'],0)
                self.assertTrue(any('current_panel_quote_unavailable' in s for s in r['run_errors']))
                self.assertTrue(any('current_panel_quote_unavailable' in s for s in r['errors']))
                return r
            with patch.object(live,'start_batch',side_effect=entry),patch.object(ap.sys,'argv',['bv_autoplay.py','--start']),patch('builtins.print'),patch.object(ap,'spawn_tap') as send:
                self.assertEqual(ap.main(),2);send.assert_not_called()
            self.assertFalse(any(r['kind']=='purchase_reserved' for r in live.Budget(root).records()))
