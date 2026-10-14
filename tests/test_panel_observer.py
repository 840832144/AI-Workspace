"""Synthetic transport/lifecycle checks. No device, no acceptance claim."""
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from bv_panel_observer import ScopedPanelReader,merge_ranges,saved_reader


class PanelTransport(unittest.TestCase):
    def test_plan_merges_only_requested_bytes(self):
        self.assertEqual(merge_ranges([(10,4),(12,4),(16,1),(30,2)]),[(10,7),(30,2)])
        read=saved_reader({(10,4):b'abcd'})
        self.assertEqual(read(11,2),b'bc')
        with self.assertRaisesRegex(ValueError,'address_plan_changed'):read(13,2)

    def test_fresh_read_never_reuses_a_prior_value_or_accepts_partial_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=ScopedPanelReader(SimpleNamespace(stopped=lambda:False),tmp)
            r.pid=123;r.maps=[(100,200,'rw')]
            with patch.object(r,'adb',side_effect=[b'ab',b'cd',b'x']):
                self.assertEqual(r.read_ranges([(100,2)])[(100,2)],b'ab')
                self.assertEqual(r.read_ranges([(100,2)])[(100,2)],b'cd')
                with self.assertRaisesRegex(ValueError,'partial_read'):r.read_ranges([(100,2)])
            with patch.object(r,'adb') as send:
                with self.assertRaisesRegex(ValueError,'unmapped_or_unbounded'):r.read_ranges([(199,2)])
                send.assert_not_called()

    def test_stop_before_read_prevents_adb(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=ScopedPanelReader(SimpleNamespace(stopped=lambda:True),tmp)
            with patch('bv_panel_observer.subprocess.run') as run:
                with self.assertRaisesRegex(ValueError,'stopped'):r.adb(['cat','/proc/123/stat'])
                run.assert_not_called()

    def test_restart_rejected_even_if_pid_is_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=ScopedPanelReader(SimpleNamespace(stopped=lambda:False),tmp)
            r.pid=123;r.process=(123,90);r.boot='test-boot'
            stat=('123 (game process) '+' '.join(['0']*19+['91'])).encode()
            with patch.object(r,'adb',return_value=stat):
                with self.assertRaisesRegex(ValueError,'process_epoch_changed'):r.check_epoch()
