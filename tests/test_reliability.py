"""Synthetic fault regressions. These tests NEVER start ADB or spend resources."""
import copy
import importlib.util
import json
import tempfile
import unittest
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import bv_autoplay as ap
from bv_evidence import RawTail, aggregate, decode, expected_cells, measure, state_diagnostics
from bv_ws2 import parse_frame


def cards():
    return [{"slot": i, "vals": [col*15+r+1 for col in range(5) for r in range(5)]}
            for i in range(1, 5)]


def grid(dx=0):
    return [{"cols": [80+col*78+x+dx for col in range(5)],
             "rows": [500+r*78+y for r in range(5)]}
            for y in (0, 470) for x in (0, 420)]


def controller():
    # Construct the actual controller methods without starting capture/UI workers.
    c = ap.AutoPlay.__new__(ap.AutoPlay)
    c.a = SimpleNamespace(settle=1.8, retries=2, ack_wait=1.5, dry=True)
    c.rid = "round1"
    c.cards = cards()
    c.reader = SimpleNamespace(best_cards=lambda rid: cards())
    c.order = list(ap.DEFAULT_ORDER)
    c.closed_rounds = set()
    c.closed = c.halted = c.repeat_safe = False
    c.pending = []; c.awaiting = []; c.called = []; c.first_seen = {}
    c.done = set(); c.tapped = set(); c.giveup = set(); c.observed_cells = set()
    c.layout_candidate = c.grid = None
    c.layout_samples = c.layout_version = 0
    c.layout_at = 0
    c.input_future = c.input_target = None
    c.input_pool = SimpleNamespace(submit=lambda fn: Future())
    c.n_retry = c.n_tap = c.n_giveup = 0
    c.logs = []
    c.log = lambda **kw: c.logs.append(kw)
    c.freeze_round = lambda reason: None
    return c


def stabilize(c, det, start=8.8):
    for t in (start,start+.5,start+1):
        with patch.object(ap.time,"monotonic",return_value=t):c.setup_grid(4,det)


def freeze(n=20, filled=19):
    cs = cards()
    balls = cs[0]["vals"][:n//4]
    targets = sorted(expected_cells(cs, balls))
    return {"evidence_kind": "synthetic", "instance": "synthetic", "session_id": "test",
            "round_id": "round1", "cards": cs, "balls": balls, "start": 1, "end": 10,
            "denominator_complete": True, "closed": True, "terminal_complete": True,
            "verified_cells": [{"instance": "synthetic", "session_id": "test", "round_id": "round1",
                                "card_id": slot, "cell_index": cell, "at": 5, "filled": True}
                               for slot, cell in targets[:filled]]}


def wire(window=(1, 2, 3), seq=1):
    rid = b"BINGO_HALL.synthetic.1"
    body = bytes([10, len(rid)]) + rid + bytes([18, len(window)]) + bytes(window)
    data = (5).to_bytes(4, "little") + seq.to_bytes(2, "little") + b"\0\0" + bytes([169, 0]) + body
    rec = {"file": "synthetic.bin", "len": len(data), "dir": "S->C", "ts": "2026-10-13 00:00:00",
           "hdr": {"cmd": 169, "seq": seq, "flags": 0}}
    return data, rec


class CountingTests(unittest.TestCase):
    def test_normal_four_cards_free_duplicates(self):
        cs=cards()
        expected=expected_cells(cs, cs[0]["vals"]*2)
        self.assertEqual(len(expected),96)
        self.assertTrue(all(cell!=12 for _,cell in expected))
        f=freeze();f["verified_cells"]*=2
        self.assertEqual(measure(f)["N"],19)

    def test_thresholds_zero_and_weighting(self):
        self.assertFalse(measure(freeze(filled=18))["hard_pass"])
        self.assertTrue(measure(freeze(filled=19))["hard_pass"])
        f=freeze();f["balls"]=[];f["verified_cells"]=[]
        self.assertEqual(measure(f)["status"],"N/A")
        # Aggregate arithmetic fixtures; synthetic sources cannot be live acceptance.
        rs=[measure(freeze()) for _ in range(10)]
        self.assertFalse(aggregate(rs)["qualified"])
        for r in rs:r["evidence_kind"]="observed-live"
        self.assertTrue(aggregate(rs)["optimization_pass"])
        rs[-1].update(N=1,E=100,hard_pass=False)
        total=aggregate(rs)
        self.assertEqual(total["weighted_rate"],172/280)
        self.assertFalse(total["hard_pass"])
        self.assertFalse(aggregate(rs[:-1])["qualified"])

    def test_lower_bound_unknown_and_live_not_certified(self):
        f=freeze();f["terminal_complete"]=False
        r=measure(f)
        self.assertEqual(r["status"],"verified_lower_bound")
        self.assertEqual(r["Unknown"],1)
        f["evidence_kind"]="observed-live"
        r=measure(f)
        self.assertIsNone(r["rate"])
        self.assertIn("production_semantics_unverified",r["errors"])

    def test_missing_terminal_denominator_and_cross_round(self):
        for key in ("closed","denominator_complete"):
            f=freeze();f[key]=False
            self.assertEqual(measure(f)["status"],"Invalid")
        f=freeze();f["verified_cells"][0]["round_id"]="another"
        self.assertEqual(measure(f)["status"],"Invalid")
        f=freeze();f["verified_cells"][0]["cell_index"]=12
        self.assertEqual(measure(f)["status"],"Invalid")

    def test_wrapper_special_truncation_is_not_fill(self):
        tokens=[""]*97;tokens[0]="1::";tokens[24]="@1.2.3#";tokens[48]="@#:2:";tokens[-1]="@"
        d=state_diagnostics("|".join(tokens))
        self.assertEqual(d["legacy_nonempty"],[1,1,1,0])
        self.assertEqual(d["payload_nonempty"],[1,0,1,0])
        self.assertEqual(d["semantic_status"],"Unknown")
        self.assertFalse(state_diagnostics("|".join(tokens[:-2]))["shape_valid"])

    def test_contradiction_unfilled_and_independence(self):
        f=freeze();bad=copy.deepcopy(f["verified_cells"][0]);bad["filled"]=False
        f["verified_cells"].append(bad)
        self.assertIn("contradictory_state",measure(f)["errors"])
        c=controller();c.done={(1,1,1)}
        f=freeze(filled=0)
        self.assertEqual(measure(f)["N"],0)


class ControllerTests(unittest.TestCase):
    def test_calibration_failure_animation_geometry_recovery(self):
        c=controller()
        self.assertFalse(c.setup_grid(4,[]));self.assertIsNone(c.grid)
        with patch.object(ap.time,"monotonic",return_value=10):
            self.assertFalse(c.setup_grid(4,grid()))
            self.assertFalse(c.setup_grid(4,grid())) # no duplicate instant sample
        with patch.object(ap.time,"monotonic",return_value=10.5):
            self.assertFalse(c.setup_grid(4,grid(8)))
        stabilize(c,grid(),start=11)
        self.assertIsNotNone(c.grid)
        bad=grid();bad[0]["cols"]=[0,0,0,0,0]
        self.assertFalse(c.setup_grid(4,bad));self.assertIsNone(c.grid)

    def test_bad_orientation_and_failed_shot_cannot_reuse_image(self):
        from PIL import Image
        c=controller()
        with tempfile.TemporaryDirectory() as folder:
            c.sess=folder
            path=Path(folder)/'_grid.png'
            Image.new('RGB',(1600,900)).save(path)
            with patch.object(ap,'shot',return_value=str(path)):
                self.assertIsNone(c.detect_grid())
            with patch.object(ap,'shot',return_value=None):
                self.assertIsNone(c.detect_grid())

    def test_stop_only_marks_requested_session(self):
        with tempfile.TemporaryDirectory() as folder:
            session=Path(folder)/'autoplay_synthetic';session.mkdir()
            with patch.object(ap,'SESS',folder), patch.object(ap.sys,'argv',['bv_autoplay.py','--stop',str(session)]), patch('builtins.print'):
                self.assertEqual(ap.main(),0)
            self.assertTrue((session/'STOP').exists())

    def test_backfill_settle_and_current_coordinates(self):
        c=controller()
        with patch.object(ap.time,"monotonic",return_value=10):
            c.on_ball("unused","round1",1);c.backfill()
            stabilize(c,grid())
            self.assertEqual(len(c.pending),4)
            self.assertTrue(all(q["due"]==11.8 for q in c.pending))
            c.tick([]);self.assertIsNone(c.input_future)
        with patch.object(ap.time,"monotonic",return_value=12):
            stabilize(c,grid(8),start=10.8)
            c.tick([])
            action=next(e for e in c.logs if e["kind"]=="attempt")
            self.assertEqual(action["x"],88)
            self.assertEqual(action["layout_version"],c.layout_version)

    def test_wrong_missing_fifo_and_uplink_never_success(self):
        c=controller();c.awaiting=[{"round_id":"round1","slot":1,"r":0,"c":0,"t":10,"tries":0}]
        with patch.object(ap.time,"monotonic",return_value=10):
            for e in ({"round_id":"round1","card_id":2,"cell_index":1},
                      {"round_id":"old","card_id":1,"cell_index":0},
                      {"round_id":"round1","cell_index":0},
                      {"round_id":"round1","card_id":1,"cell_index":0}):
                c.tick([e])
        self.assertEqual(c.done,set())
        self.assertEqual(len(c.awaiting),1)

    def test_unknown_not_retried_not_executed_bounded(self):
        c=controller()
        q={"round_id":"round1","slot":1,"r":0,"c":0,"t":0,"tries":0,"input_outcome":"unknown"}
        c.awaiting=[q.copy()]
        with patch.object(ap.time,"monotonic",return_value=10):c.tick([])
        self.assertFalse(c.pending)
        c=controller();q["input_outcome"]="not_executed";c.awaiting=[q.copy()]
        with patch.object(ap.time,"monotonic",return_value=10):c.tick([])
        self.assertEqual(c.pending[0]["tries"],1)
        q["tries"]=2;c.pending=[];c.awaiting=[q]
        with patch.object(ap.time,"monotonic",return_value=20):c.tick([])
        self.assertFalse(c.pending)

    def test_slow_input_sparse_observations_new_balls_and_cutover(self):
        c=controller()
        with patch.object(ap.time,"monotonic",return_value=10):
            c.on_ball("unused","round1",1)
            stabilize(c,grid())
        with patch.object(ap.time,"monotonic",return_value=12):
            c.tick([]);first=c.input_future
            c.on_ball("unused","round1",2);c.backfill();c.tick([])
            self.assertEqual(sum(q["ball"]==1 for q in c.pending),3)
            self.assertIs(c.input_future,first)
            first.set_result("executed")
            c.tick([])
            self.assertIsNotNone(c.input_future) # observations do not monopolize input slot
            self.assertEqual(len(c.awaiting),1)
            c.on_ball("unused","old",3)
            self.assertTrue(c.halted);self.assertIsNone(c.grid)

    def test_close_expiry_no_cross_round(self):
        c=controller()
        with patch.object(ap.time,"monotonic",return_value=10):c.on_ball("unused","round1",1)
        c.close_round("round1",verified=True)
        self.assertTrue(c.closed);self.assertFalse(c.pending)
        c.on_ball("unused","round1",2)
        self.assertNotIn(2,c.called)

    def test_resource_unknown_popup_navigation_is_blocked(self):
        c=controller()
        self.assertFalse(c.go_next_round());self.assertTrue(c.halted)
        self.assertFalse(ap.preflight()["live_ready"])
        with patch.object(ap.subprocess,"run",return_value=SimpleNamespace(returncode=1)) as run:
            self.assertEqual(ap.tap(10,10),"unknown")
            self.assertEqual(run.call_count,1)
            self.assertIn("tap",run.call_args.args[0])


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.index=self.root/'index.jsonl';self.index.write_bytes(b'')
        self.data,self.rec=wire()

    def tearDown(self):
        self.temp.cleanup()

    def test_half_line_delayed_body_all_window_numbers_and_duplicates(self):
        t=RawTail(self.index,self.root)
        line=json.dumps(self.rec).encode()+b'\n'
        self.index.write_bytes(line[:20]);self.assertEqual(t.poll(now=0),[]);self.assertEqual(t.pos,0)
        with self.index.open('ab') as f:f.write(line[20:])
        self.assertEqual(t.poll(now=0),[])
        (self.root/self.rec['file']).write_bytes(self.data)
        es=t.poll(now=1);self.assertEqual(es[0]['window'],[1,2,3])
        self.assertEqual(t.poll(now=1),[])
        with self.index.open('ab') as f:f.write(line)
        self.assertEqual(t.poll(now=1),[]);self.assertTrue(t.errors)

    def test_missing_body_timeout_rotation_and_parse_error(self):
        self.index.write_text(json.dumps(self.rec)+'\n','utf-8');t=RawTail(self.index,self.root)
        t.poll(now=0);t.poll(now=3);self.assertEqual(t.errors['missing_body'],1)
        self.index.write_bytes(b'')
        with self.assertRaisesRegex(ValueError,'index_rotation'):t.poll(now=4)
        self.index.write_bytes(b'{bad}\n');t=RawTail(self.index,self.root)
        t.poll(now=0);self.assertEqual(t.errors['invalid_index_record'],1)

    def test_frame_mismatch_truncated_header(self):
        wrong=dict(self.rec,len=123)
        with self.assertRaises(ValueError):decode(self.data,wrong,{})
        self.assertFalse(parse_frame(self.data[:9]+b'\xff'*4)['ok'])

    def test_reader_full_window_dedup_and_conflicting_cards(self):
        (self.root/self.rec['file']).write_bytes(self.data)
        self.index.write_text(json.dumps(self.rec)+'\n','utf-8')
        reader=ap.Reader(str(self.index),bodies=self.root,start=0)
        balls,_=reader.poll();self.assertEqual([b[2] for b in balls],[1,2,3])
        self.assertEqual(reader.poll()[0],[])
        reader.cards['r']={('a',):cards(),('b',):cards()}
        self.assertIsNone(reader.best_cards('r'))

    def test_live_reader_does_not_act_on_backlog_offline_query_still_works(self):
        (self.root/self.rec['file']).write_bytes(self.data)
        self.index.write_text(json.dumps(self.rec)+'\n','utf-8')
        live=ap.Reader(str(self.index),bodies=self.root)
        self.assertEqual(live.poll()[0],[])
        self.assertEqual(live.round_balls('BINGO_HALL.synthetic.1'),[1,2,3])
        self.assertEqual(live.poll()[0],[])

    def test_addon_restart_unique_and_exclusive_writes(self):
        for relative,method in [('dev/bv_dump.py','_save_blob'),('collector/bv_dump.py','_save')]:
            names=[]
            for i in range(2):
                spec=importlib.util.spec_from_file_location('synthetic_addon',Path(ap.ROOT)/relative)
                mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
                mod.BODIES=str(self.root)
                name=getattr(mod,method)(b'synthetic','test');names.append(name)
                mod._seq[0]=0
                with self.assertRaises(FileExistsError):getattr(mod,method)(b'overwrite','test')
                self.assertEqual((self.root/name).read_bytes(),b'synthetic')
            self.assertNotEqual(*names)


if __name__=='__main__':
    unittest.main()
