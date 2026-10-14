"""Observer safety tests; these do not establish panel-price or game semantics."""
import json
import hashlib
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
from unittest.mock import patch

from bv_observer import prepare_helper,inspect,summarize_observations,worker,EMULATED_BINDING_STOP


class ObserverSafety(unittest.TestCase):
    def test_stopped_inspect_has_no_helper_ledger_or_device_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'absent'
            with patch('bv_observer.prepare_helper') as prepare,patch('bv_live.Budget') as budget, \
                    patch('subprocess.run') as run,patch('subprocess.Popen') as spawn:
                with self.assertRaisesRegex(RuntimeError,EMULATED_BINDING_STOP):inspect('absent',out)
                self.assertFalse(out.exists())
                for mock in (prepare,budget,run,spawn):mock.assert_not_called()

    def test_worker_cannot_bypass_stopped_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'absent'
            with patch.dict(sys.modules,{'frida':None}):
                with self.assertRaisesRegex(RuntimeError,EMULATED_BINDING_STOP):
                    worker('unused',0,out,1,bridge_diagnostic=True)
            self.assertFalse(out.exists())

    def test_actual_helper_and_worker_cli_stop_without_output_directory(self):
        entry=Path(__file__).resolve().parents[1]/'bv_observer.py'
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'absent'
            for args in (['--helper','absent'],['--worker','unused','--pid','0','--bridge-diagnostic']):
                with self.subTest(args=args):
                    result=subprocess.run([sys.executable,str(entry),'--output',str(out),*args],
                                          capture_output=True,text=True,timeout=5)
                    self.assertEqual(result.returncode,2,result.stderr)
                    report=json.loads(result.stdout)
                    self.assertEqual(report['error'],EMULATED_BINDING_STOP)
                    self.assertFalse(report['run_ready']);self.assertFalse(report['quote_source_available'])
                    self.assertEqual(report['purchase_inputs'],0);self.assertFalse(out.exists())

    def helper(self,root):
        data=bytearray(64);data[:6]=b'\x7fELF\x02\x01';data[18:20]=b'\x3e\x00'
        data+=b'16.7.19\0/sys/fs/selinux/policy\0tail'
        p=root/'original';p.write_bytes(data)
        digest=patch('bv_observer.HELPER_SHA256',hashlib.sha256(data).hexdigest())
        digest.start();self.addCleanup(digest.stop)
        return p

    def test_only_helper_policy_constant_changes_original_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=self.helper(root);original=src.read_bytes();dest=root/'prepared'
            report=prepare_helper(src,dest);actual=dest.read_bytes();at=report['changed_offset'];n=report['changed_size']
            self.assertEqual(src.read_bytes(),original)
            self.assertEqual(actual[:at],original[:at]);self.assertEqual(actual[at+n:],original[at+n:])
            self.assertEqual(len(actual),len(original));self.assertIn(b'/dev/null/',actual)
            self.assertNotIn(b'/sys/fs/selinux/policy',actual)

    def test_reject_ambiguous_helper_constant(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=self.helper(root)
            src.write_bytes(src.read_bytes()+b'/sys/fs/selinux/policy\0')
            with self.assertRaisesRegex(ValueError,'unsupported_helper'):prepare_helper(src,root/'prepared')

    def test_reject_unverified_helper_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=self.helper(root);src.write_bytes(src.read_bytes()+b'changed')
            with self.assertRaisesRegex(ValueError,'unsupported_helper'):prepare_helper(src,root/'prepared')

    def test_no_device_access_when_ten_round_margin_insufficient(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=self.helper(root)
            # Isolate the historical lifecycle below the now-stopped binding.
            with patch('bv_observer.require_emulated_binding'),patch('bv_live.Budget') as budget,patch('subprocess.run') as run:
                from bv_live import LIMITS,BATCH_ROUNDS,BATCH_CLEANUP_SECONDS
                budget.return_value.elapsed.return_value=LIMITS['total_seconds']-BATCH_ROUNDS*LIMITS['round_seconds']-BATCH_CLEANUP_SECONDS-16
                with self.assertRaisesRegex(ValueError,'insufficient_preparation_margin'):inspect(src,root/'output',12)
                run.assert_not_called();budget.return_value.append.assert_not_called()

    def test_failed_setup_cleans_up_and_charges_real_time(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=self.helper(root)
            def adb(args,**kw):
                if 'test -c /dev/null' in args[-1]:raise subprocess.TimeoutExpired(args,2)
                return subprocess.CompletedProcess(args,0,stdout='Permissive\nabc  /sys/fs/selinux/policy\n18360\nHELPER_STOPPED\n',stderr='')
            with patch('bv_observer.require_emulated_binding'),patch('bv_live.Budget') as budget,patch('subprocess.run',side_effect=adb) as run, \
                    patch('bv_observer.time.monotonic',side_effect=[1000,1000.25]):
                budget.return_value.elapsed.return_value=2300;budget.return_value.gross.return_value=52
                result=inspect(src,root/'output',12)
                self.assertEqual(result['purchase_inputs'],0);self.assertTrue(result['helper_stopped'])
                self.assertFalse(result['policy_unchanged']);self.assertFalse(result['game_alive'])
                self.assertEqual(result['seconds'],.25)
                self.assertEqual([c.args[0] for c in budget.return_value.append.call_args_list],['runtime_start','runtime_end'])
                self.assertEqual(run.call_count,2)
                self.assertIn('TimeoutExpired',json.loads((root/'output'/'result.json').read_text())['error'])

    def test_worker_success_exit_does_not_hide_emulated_attach_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'observations.jsonl').write_text(json.dumps(dict(type='worker_error',error='ProtocolError:process is not using emulation'))+'\n')
            r=summarize_observations(root)
            self.assertFalse(r['run_ready']);self.assertFalse(r['observer_ready'])
            self.assertFalse(r['quote_source_available']);self.assertEqual(len(r['observer_errors']),1)

    def test_unconfirmed_cleanup_keeps_resource_clock_open(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=self.helper(root)
            with patch('bv_observer.require_emulated_binding'),patch('bv_live.Budget') as budget,patch('subprocess.run',side_effect=subprocess.TimeoutExpired('adb',2)):
                budget.return_value.elapsed.return_value=2300;budget.return_value.gross.return_value=52
                result=inspect(src,root/'output',12)
                self.assertIn('runtime_session_open',result)
                self.assertEqual([c.args[0] for c in budget.return_value.append.call_args_list],['runtime_start'])

    def test_natural_callback_still_requires_semantic_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'observations.jsonl').write_text('\n'.join(json.dumps(dict(payload=dict(kind=k))) for k in ['observer_ready','natural_callback']))
            r=summarize_observations(root)
            self.assertEqual(r['natural_callbacks'],1);self.assertTrue(r['observer_ready'])
            self.assertEqual(r['status'],'Observed candidates only');self.assertFalse(r['run_ready'])


if __name__=='__main__':unittest.main()
