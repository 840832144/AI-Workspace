"""Historical resource ordering via exact packet receipt, never clock extrapolation."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import bv_live as live


class WalletChain(unittest.TestCase):
    def test_exact_receipt_and_complete_change_chain_or_refuse(self):
        receipt=b'I:1:10:26/10/14 18:39:58.274 +08:00 [WebSocket] RECEIVE Response|[2]|301||Payload:3 bytes\n'
        one=b'I:1:11:26/10/14 18:41:21.365 +08:00 NotifyResources TICKET current=105 next=112 delta=7\n'
        two=b'I:1:12:26/10/14 18:41:27.906 +08:00 NotifyResources TICKET current=112 next=113 delta=1\n'
        wallet=dict(sequence=2,currencies={'TICKET':105},source_ref={'synthetic':True})
        with tempfile.TemporaryDirectory() as folder,patch.object(live,'body_for',return_value=b'abc'),patch.object(live,'ticket_balance',side_effect=ValueError('resource_clock_not_covered')):
            p=Path(folder)/'client-before.log';q=dict(client_before_ref=str(p))
            connect=b'[WebSocket] Socket Begin Connect\n'
            p.write_bytes(connect+receipt+one+two)
            self.assertEqual(live.current_ticket_balance(wallet,q,SimpleNamespace()),113)
            # A resumed socket need not resend 301; the continuous ledger still
            # binds to the latest wallet-bearing connection, never an old one.
            p.write_bytes(connect+receipt+one+connect+two)
            self.assertEqual(live.current_ticket_balance(wallet,q,SimpleNamespace()),113)
            for raw in [receipt+two,receipt+receipt+one+two,receipt+one+two[:-1],
                        receipt.replace(b'[2]',b'[3]')+one+two,
                        receipt+one+two+b'RECEIVE Response|[4]|301||Payload:2 bytes\n',
                        receipt+one+two+b'NotifyResources TICKET malformed\n']:
                p.write_bytes(connect+raw)
                with self.assertRaises(ValueError):live.current_ticket_balance(wallet,q,SimpleNamespace())
