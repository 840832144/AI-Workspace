# -*- coding: utf-8 -*-
"""TASK-0039 controller and governed runtime entry. Uplinks are observations."""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from bv_evidence import RawTail, expected_cells

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "collector"))

from bv_ws2 import parse_frame                        # noqa: E402
from bv_proto import parse                            # noqa: E402
from bv_extract import extract_cards, harvest_strings  # noqa: E402

ADB = r"C:\platform-tools\adb.exe"
DEV = "127.0.0.1:16384"
WS = os.path.join(ROOT, "out", "bv_ws.jsonl")
BODIES = os.path.join(ROOT, "out", "bv_bodies")
SESS = os.path.join(ROOT, "sessions")

# 协议卡面下标 -> 视觉位置。实测：1→左上 2→左下 3→右上 4→右下
DEFAULT_ORDER = ["tl", "bl", "tr", "br"]


def spawn_tap(x, y):
    """The dispatch boundary. Waiting for ADB happens outside the state lock."""
    return subprocess.Popen([ADB, "-s", DEV, "shell", "input", "tap", str(int(x)), str(int(y))],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def finish_tap(process):
    try:
        process.communicate(timeout=5)
        return "executed" if process.returncode == 0 else "unknown"
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        return "unknown"  # may already have reached Android


def tap(x, y, hold=None):
    """点击。

    ★ 必须用 input tap：在 MuMu Nx(Android 15, adb root) 上，
    `input swipe x y x y 110`（同起止点当长按用）会被静默丢弃、一个事件都不注入，
    而 `input tap` 稳定生效。这是自动玩「点了没反应」的真正原因。
    """
    x, y = int(x), int(y)
    r = subprocess.run([ADB, "-s", DEV, "shell", "input", "tap", str(x), str(y)],
                       capture_output=True, timeout=30)
    # Nonzero/timeout is Unknown: the device might have received the command.
    return "executed" if r.returncode == 0 else "unknown"



def shot(path, tries=3):
    """截一张图。Android 15 上 screencap 偶发吐空数据（写出 0 字节 → 后面
    PIL 报 UnidentifiedImageError），所以校验 PNG 魔数并重试。"""
    for i in range(tries):
        r = subprocess.run([ADB, "-s", DEV, "exec-out", "screencap", "-p"],
                           capture_output=True, timeout=5)
        b = r.stdout or b""
        if b[:8] == b"\x89PNG\r\n\x1a\n" and len(b) > 4096:
            with open(path, "wb") as f:
                f.write(b)
            return path
        time.sleep(0.6)
    print("    [截图] 失败 %d 次，跳过画面标定" % tries)
    return None



def idx2rc(k):
    """列序 0 基索引 -> (row, col)"""
    return k % 5, k // 5

def rid_of(body):
    for s in harvest_strings(body, 20, 6):
        if s.startswith("BINGO_HALL") and s.count(".") >= 3 and s.rsplit(".", 1)[-1].isdigit():
            return s
    return None


# ---------------------------------------------------------------------------
class Reader:
    """Bounded incremental capture. Uplink events remain client observations."""
    def __init__(self, path, backscan=8000, bodies=None, start=None):
        self.path = path
        self.tail = RawTail(path, bodies, start=os.path.getsize(path) if start is None else start)
        self.cards = {}
        self.balls = {}
        self.events = []
        self.new_balls = []
        self.acks = []
        self.errors = self.tail.errors

    def poll(self):
        self.new_balls, self.acks = [], []
        for event in self.tail.poll():
            self.events.append(event)
            rid = event.get("round_id")
            if event["type"] == "balls":
                known = self.balls.setdefault(rid, [])
                for ball in event["window"]:
                    if ball not in known:
                        known.append(ball)
                        self.new_balls.append((event["received_at"], rid, ball))
            elif event["type"] == "cell_observation":
                self.acks.append(event)
            elif event["cmd"] in (163, 166, 167) and event["direction"] == "S->C":
                # Preserve candidates, never choose the most frequent of conflicting cards.
                raw = open(event["source_ref"]["body"], "rb").read()
                body = parse_frame(raw)["body"]
                rid = rid_of(body)
                got = extract_cards(body)
                if rid and got:
                    try:
                        expected_cells(got, [])
                    except ValueError:
                        self.errors["invalid_cardset"] += 1
                        continue
                    fp = tuple(tuple(c["vals"]) for c in got)
                    self.cards.setdefault(rid, {})[fp] = got
        return self.new_balls, self.acks

    def round_balls(self, rid):
        if rid not in self.balls:
            # Compatibility for existing offline callers; freeze a read boundary.
            replay = RawTail(self.path, self.tail.bodies, end=os.path.getsize(self.path))
            while replay.pos < replay.end:
                before = replay.pos
                for e in replay.poll(now=0):
                    if e["type"] == "balls":
                        target = self.balls.setdefault(e["round_id"], [])
                        target.extend(n for n in e["window"] if n not in target)
                if replay.pos == before:
                    break
            replay.poll(now=3)
            self.errors.update(replay.errors)
        return list(self.balls.get(rid, []))

    def best_cards(self, rid):
        candidates = self.cards.get(rid, {})
        if len(candidates) != 1:
            return None
        return next(iter(candidates.values()))


# ---------------------------------------------------------------------------
class AutoPlay:
    def __init__(self, a):
        self.a = a
        supplied = getattr(a,"session_path",None)
        self.sess = supplied or os.path.join(SESS, "autoplay_%d"%time.time_ns())
        os.makedirs(self.sess, exist_ok=bool(supplied))
        self.act = open(os.path.join(self.sess, "actions.jsonl"), "w", encoding="utf-8")
        self.reader = Reader(getattr(a,"capture_index",WS), bodies=getattr(a,"bodies",None))
        self.rid = None
        self.cards = None
        self.grid = None
        self.order = ([x.strip() for x in a.map.split(",")] if a.map else list(DEFAULT_ORDER))
        self.called = []
        self.done = set()
        self.special_observed = set()  # Suppress re-input; never counts as confirmed fill.
        self.tapped = set()          # ★ 已经点过的格（每格只点一次）
        self.pending = []
        self.awaiting = []
        self.n_tap = self.n_ack = self.n_retry = self.n_auto = self.n_nocard = self.n_miss = 0
        self._last_cards = None
        self.n_mismatch = 0
        self.n_giveup = 0
        self.giveup = set()
        self.t_last_rescan = time.monotonic()
        self.first_seen = {}
        self.closed_rounds = set()
        self.layout_candidate = None
        self.layout_samples = 0
        self.layout_sample_at = None
        self.layout_version = 0
        self.layout_at = 0
        self.input_pool = ThreadPoolExecutor(max_workers=1)
        self.input_future = None
        self.input_target = None
        self.observed_cells = set()
        self.repeat_safe = False  # No live idempotence evidence yet.
        self.halted = False
        self.round_started = time.monotonic()
        self.closed = False
        self.state_lock = threading.RLock()
        self.foreground_ok = False
        self.foreground_at = 0
        self.generation = 0

    def revoke(self, reason, halt=False):
        with self.state_lock:
            self.generation += 1
            self.grid = self.layout_candidate = None
            self.layout_samples = 0
            self.layout_sample_at = None
            self.layout_tracks = {}
            self.halted = self.halted or halt
            self.log(kind="input_revoked", reason=reason, generation=self.generation)

    def stop_requested(self):
        batch_stop=getattr(self.a,'batch_stop_path',None)
        return (time.monotonic()>=getattr(self.a,'round_deadline',float('inf'))
                or Path(self.sess, "STOP").exists() or bool(batch_stop and Path(batch_stop).exists()))

    def execute_target(self, q):
        with self.state_lock:
            now = time.monotonic()
            if (self.closed or self.halted or self.stop_requested() or q["round_id"] != self.rid
                    or q["generation"] != self.generation or not self.grid
                    or not self.grid[q['slot']].get('input_ready',True)
                    or q["layout_version"] != self.grid[q["slot"]].get("version",self.layout_version)
                    or now-self.grid[q["slot"]].get("sampled_at",self.layout_at) > 2.5
                    or q["c"]*5+q["r"] not in self.grid[q["slot"]].get("reachable_cells",range(25))
                    or not self.foreground_ok or now-self.foreground_at > 2.5
                    or q["due"] > now or q["ball"] not in self.first_seen
                    or (q['slot'],q['r'],q['c']) in self.done | getattr(self,'special_observed',set())
                    or (q['slot'],q['r'],q['c']) in getattr(self,'uncertain_observed',set())
                    or self.n_tap >= getattr(self.a,"max_dispatches",float("inf"))):
                self.log(kind="cancelled_before_dispatch", slot=q["slot"], cell_index=q["c"]*5+q["r"])
                return "cancelled"
            # Coordinates are derived here, never captured by a deferred closure.
            g = self.grid[q["slot"]]
            x, y = g["cols"][q["c"]], g["rows"][q["r"]]
            if self.a.dry:
                return "dry"
            sent_ns=time.time_ns()
            process = spawn_tap(x, y)
            if not hasattr(self,'dispatch_times'):self.dispatch_times={}
            self.dispatch_times[(q['slot'],q['r'],q['c'])]=sent_ns
            self.n_tap += 1
            self.tapped.add((q["slot"], q["r"], q["c"]))
            self.log(kind="input_dispatched", slot=q["slot"], cell_index=q["c"]*5+q["r"],
                     x=x, y=y, layout_version=q["layout_version"], dispatched_ns=sent_ns)
        return finish_tap(process)

    def log(self, **kw):
        kw["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        kw["monotonic_ns"] = time.monotonic_ns()
        kw["round_id"] = self.rid
        self.act.write(json.dumps(kw, ensure_ascii=False) + "\n")
        self.act.flush()

    # 三次稳定标定；失败暂停，禁止内置坐标回退。
    def detect_grid(self):
        """返回 [卡0, 卡1, ...]（视觉顺序 tl,tr,bl,br），或 None"""
        try:
            from PIL import Image
            import bv_cardgrid
            path = os.path.join(self.sess, "_grid.png")
            if not shot(path):
                return None
            img = Image.open(path).convert("RGB")
            if img.size != (900, 1600):
                return None
            return bv_cardgrid.detect(img)
        except Exception as e:
            print("    [卡位] 实测失败 %r" % (e,))
            return None

    def setup_grid(self, nslots, det=None):
        """Require three fresh stable samples; failure revokes the layout."""
        det = self.detect_grid() if det is None else det
        with self.state_lock:
            return self._setup_grid(nslots, det)

    def _setup_grid(self, nslots, det):
        try:
            now = time.monotonic()
            if nslots != 4 or len(det or []) != 4:
                raise ValueError("card_count")
            grid = {}
            for k, c in enumerate(det):
                pos = self.pos_of_detected(det, k)
                slot = self.order.index(pos) + 1
                for axis, bound in (("cols", 900), ("rows", 1600)):
                    values = c[axis]
                    gaps = [b-a for a, b in zip(values, values[1:])]
                    if len(values) != 5 or not all(0 < v < bound for v in values) or not all(
                            35 <= g <= 125 for g in gaps) or max(gaps)-min(gaps) > 12:
                        raise ValueError("geometry")
                if slot in grid:
                    raise ValueError("duplicate_position")
                grid[slot] = {a: list(c[a]) for a in ("cols", "rows")}
                grid[slot]['input_ready']=c.get('input_ready',True)
                grid[slot]['reachable_cells']=list(c.get('reachable_cells',range(25)))
                grid[slot]['pause_reason']=c.get('pause_reason','not_ready')
            # Four distinct nonoverlapping card rectangles, not four detections of one.
            for i in range(1, 5):
                for j in range(i+1, 5):
                    x, y = grid[i], grid[j]
                    if not (x["cols"][-1] < y["cols"][0] or y["cols"][-1] < x["cols"][0] or
                            x["rows"][-1] < y["rows"][0] or y["rows"][-1] < x["rows"][0]):
                        raise ValueError("overlap")
            tracks=getattr(self,'layout_tracks',{});previous=self.grid or {};result={}
            for slot,current in grid.items():
                old=previous.get(slot,{});track=tracks.get(slot,{})
                candidate=track.get('candidate')
                stable=candidate is not None and max(abs(current[a][k]-candidate[a][k])
                    for a in ('cols','rows') for k in range(5))<=4
                ready=current['input_ready']
                if not ready:
                    tracks.pop(slot,None);count=0
                elif stable and now-track.get('at',0)<.4:
                    count=track['count']
                else:
                    count=track.get('count',0)+1 if stable else 1
                    tracks[slot]=dict(candidate=current,count=count,at=now)
                current['input_ready']=ready and count>=3
                current['sampled_at']=now
                changed=(old.get('input_ready')!=current['input_ready'] or not old or
                         any(old.get(a)!=current[a] for a in ('cols','rows')) or
                         old.get('reachable_cells')!=current.get('reachable_cells'))
                current['version']=old.get('version',0)+int(changed)
                if changed:
                    self.layout_version+=1
                    self.log(kind='card_layout',slot=slot,ready=current['input_ready'],
                             version=current['version'],reason=current.get('pause_reason') if not ready else
                             ('reacquired' if current['input_ready'] else 'geometry_stabilizing'))
                result[slot]=current
            self.layout_tracks=tracks;self.layout_candidate=grid;self.grid=result
            self.layout_at=now
            return any(c['input_ready'] for c in result.values())
        except (ValueError, KeyError, TypeError):
            self.generation += 1
            self.grid = None
            self.layout_candidate = None
            self.layout_samples = 0
            self.layout_sample_at = None
            self.layout_tracks = {}
            return False

    @staticmethod
    def pos_of_detected(cards, k):
        """判出第 k 张实测卡在画面上的方位名 tl/tr/bl/br"""
        xs = [(c["cols"][0] + c["cols"][-1]) / 2.0 for c in cards]
        ys = [(c["rows"][0] + c["rows"][-1]) / 2.0 for c in cards]
        mx = (min(xs) + max(xs)) / 2.0
        my = (min(ys) + max(ys)) / 2.0
        return ("t" if ys[k] <= my else "b") + ("l" if xs[k] <= mx else "r")

    def freeze_round(self, reason):
        if self.rid and self.cards:
            name = "round_%d.json" % time.time_ns()
            with open(os.path.join(self.sess, name), "x", encoding="utf-8") as f:
                json.dump({"round": self.rid, "cards": self.cards, "balls": list(self.called),
                           "closed": self.closed, "reason": reason,
                           "source_end_offset": self.reader.tail.pos,
                           "capture_errors": dict(self.reader.errors)}, f, ensure_ascii=False)

    def close_round(self, rid, verified=False):
        if rid == self.rid and verified:
            with self.state_lock:
                self.closed = True
                self.closed_rounds.add(rid)
                self.pending.clear()
                self.revoke("round_closed")
            self.freeze_round("verified_close")

    def on_ball(self, ts, rid, ball):
        now = time.monotonic()
        if rid in self.closed_rounds:
            self.log(kind="late_round_ignored")
            return
        if self.rid and rid != self.rid:
            # A ball with another ID cannot authorize a round switch or buy cards.
            self.revoke("round_identity_mismatch", halt=True)
            self.log(kind="round_identity_mismatch")
            return
        if self.rid is None:
            self.rid = rid
            self.round_started = now
        if ball not in self.called:
            self.called.append(ball)
        self.first_seen.setdefault(ball, now)  # conservative local observation, never invented back-time
        if self.cards is None:
            self.cards = self.reader.best_cards(rid)
        if self.cards:
            self.queue_targets(ball, self.first_seen[ball] + self.a.settle)

    def queue_targets(self, ball, due, verbose=True):
        if ball not in self.first_seen or self.closed or self.halted:
            return 0
        n = 0
        for c in self.cards or []:
            for k, number in enumerate(c["vals"]):
                r, col = idx2rc(k)
                key = (c["slot"], r, col)
                if getattr(self.a,'diagnostic_slot',None) not in (None,c['slot']):continue
                if number != ball or k == 12 or key in self.done | getattr(self,'special_observed',set()):
                    continue
                active = self.pending + self.awaiting + ([self.input_target] if self.input_target else [])
                if any((q["slot"], q["r"], q["c"]) == key for q in active):
                    continue
                if key in self.giveup:
                    continue
                self.pending.append({"round_id": self.rid, "ball": ball, "slot": c["slot"],
                                     "r": r, "c": col, "due": max(due, self.first_seen[ball] + self.a.settle),
                                     "tries": 0, "status": "pending"})
                n += 1
        return n

    def backfill(self):
        return sum(self.queue_targets(b, self.first_seen[b] + self.a.settle)
                   for b in self.called if b in self.first_seen)

    def rescan(self):
        return self.backfill()

    def completes_bingo(self,q):
        # Standard 5x5 lines, based only on source-confirmed cell observations.
        known=self.done | getattr(self,'special_observed',set()) | getattr(self,'uncertain_observed',set())
        marked={(r,c) for slot,r,c in known if slot==q['slot']} | {(2,2)}
        target=(q['r'],q['c'])
        lines=[{(i,c) for c in range(5)} for i in range(5)]
        lines += [{(r,i) for r in range(5)} for i in range(5)]
        lines += [{(i,i) for i in range(5)},{(i,4-i) for i in range(5)}]
        return any(target in line and line-marked=={target} for line in lines)

    def tick(self, observations):
        now = time.monotonic()
        for event in observations:
            slot, cell = event.get("card_id"), event.get("cell_index")
            if event.get("round_id") != self.rid or type(slot) is not int or type(cell) is not int or not (
                    1 <= slot <= 4 and 0 <= cell < 25 and cell != 12):
                self.log(kind="unmatched_observation")
                continue
            r, col = idx2rc(cell)
            key = (slot, r, col)
            self.observed_cells.add(key)
            matched = next((q for q in self.awaiting if q["round_id"] == self.rid and
                            (q["slot"], q["r"], q["c"]) == key), None)
            # A C->S event is not proof of accepted fill; no FIFO fallback.
            self.log(kind="client_observation", matched=matched is not None,
                     slot=slot, cell_index=cell, source_ref=event.get("source_ref"))

        if self.input_future is not None and self.input_future.done():
            q = self.input_target
            try:
                outcome = self.input_future.result()
            except Exception as exc:
                outcome = "unknown"
                self.log(kind="input_error", error=type(exc).__name__)
            q["input_outcome"] = outcome
            q["t"] = now
            q["status"] = "attempted_unconfirmed"
            if outcome == "cancelled":
                # Unsent targets retain their retry budget and can recover after calibration.
                if q["round_id"] == self.rid and not self.closed and not self.halted and (q['slot'],q['r'],q['c']) not in getattr(self,'special_observed',set()):
                    q["status"] = "pending"
                    self.pending.append(q)
            elif (q['slot'],q['r'],q['c']) not in self.done | getattr(self,'special_observed',set()):
                self.awaiting.append(q)
            self.input_future = self.input_target = None
            self.log(kind="input_finished", outcome=outcome, slot=q["slot"], cell_index=q["c"]*5+q["r"])

        for q in list(self.awaiting):
            if now - q["t"] < self.a.ack_wait:
                continue
            self.awaiting.remove(q)
            safe = self.repeat_safe or q.get("input_outcome") == "not_executed"
            if safe and q["tries"] < self.a.retries and not self.closed and not self.halted:
                q["tries"] += 1
                q["due"] = now + self.a.ack_wait
                q["status"] = "retryable"
                self.pending.append(q)
                self.n_retry += 1
            else:
                q["status"] = "unknown_or_expired"
                self.giveup.add((q["slot"], q["r"], q["c"]))
                self.n_giveup += 1
                self.log(kind=q["status"], slot=q["slot"], cell_index=q["c"]*5+q["r"])
        if self.input_future is not None or self.closed or self.halted or self.stop_requested() or not self.grid or now-self.layout_at > 2.5 or self.n_tap >= getattr(self.a,"max_dispatches",float("inf")):
            return
        ready = [q for q in self.pending if q["due"] <= now and q["round_id"] == self.rid
                 and self.grid[q['slot']].get('input_ready',True)
                 and now-self.grid[q['slot']].get('sampled_at',self.layout_at)<=2.5
                 and q['c']*5+q['r'] in self.grid[q['slot']].get('reachable_cells',range(25))]
        # New targets before bounded retries; sparse observations never hold input slots.
        # Age eventually dominates new work; a bounded retry cannot starve forever.
        ready.sort(key=lambda q: (not self.completes_bingo(q),
                                  self.first_seen[q['ball']]+q['tries']*2, q['slot']))
        if not ready:
            return
        q = ready[0]
        self.pending.remove(q)
        q["layout_version"] = self.grid[q["slot"]].get("version",self.layout_version)
        q["generation"] = self.generation
        self.log(kind="queued", slot=q["slot"], cell_index=q["c"]*5+q["r"],
                 layout_version=q["layout_version"])
        self.input_target = q
        self.input_future = self.input_pool.submit(lambda: self.execute_target(q))

    def accept_client_mark(self, event):
        """Called only by the source-bound runtime after diagnostic qualification.

        A correctly identified mark can arrive after timeout or before ADB completion.
        Its timestamp must follow an actual dispatch for that exact target.
        """
        slot,cell=event.get('card_id'),event.get('cell_index')
        if event.get('round_id')!=self.rid:return False
        if type(slot)is not int or type(cell)is not int or not (1<=slot<=4 and 0<=cell<25) or cell==12:return False
        key=(slot,*idx2rc(cell))
        card=next((c for c in self.cards or [] if c['slot']==slot),None)
        if not card or card['vals'][cell]!=event.get('ball'):return False
        if event.get('daub_type')=='PowerUp':
            with self.state_lock:
                if not hasattr(self,'special_observed'):self.special_observed=set()
                self.special_observed.add(key);self.done.discard(key)
                self.pending=[q for q in self.pending if (q['slot'],q['r'],q['c'])!=key]
                self.awaiting=[q for q in self.awaiting if (q['slot'],q['r'],q['c'])!=key]
                self.log(kind='special_unknown',slot=slot,cell_index=cell,source_ref=event['source_ref'])
            return True  # Observation handled, not confirmation; verifier keeps Unknown.
        if event.get('daub_type')!='Manual' or key in getattr(self,'special_observed',set()):return False
        sent=getattr(self,'dispatch_times',{}).get(key)
        if (not card or card['vals'][cell]!=event.get('ball') or event['ball'] not in self.first_seen
                or sent is None):return False
        from bv_clock import matched
        if not matched(event,sent):return False
        self.done.add(key);self.giveup.discard(key)
        getattr(self,'uncertain_observed',set()).discard(key)
        self.pending=[q for q in self.pending if (q['slot'],q['r'],q['c'])!=key]
        self.awaiting=[q for q in self.awaiting if (q['slot'],q['r'],q['c'])!=key]
        self.log(kind='client_accepted',slot=slot,cell_index=cell,source_ref=event['source_ref'])
        return True

    def observe_unmatched(self,event):
        """One uncertain confirmation must not halt unrelated safe first attempts."""
        slot,cell=event.get('card_id'),event.get('cell_index')
        if event.get('round_id')!=self.rid or type(slot)is not int or type(cell)is not int:return
        card=next((c for c in self.cards or [] if c['slot']==slot),None)
        if not card or not 0<=cell<25 or card['vals'][cell]!=event.get('ball'):
            self.revoke('unmatched_mark_identity',halt=True);return
        key=(slot,*idx2rc(cell))
        with self.state_lock:
            if not hasattr(self,'uncertain_observed'):self.uncertain_observed=set()
            self.uncertain_observed.add(key)
            self.giveup.add(key)
            self.pending=[q for q in self.pending if (q['slot'],q['r'],q['c'])!=key]
            self.awaiting=[q for q in self.awaiting if (q['slot'],q['r'],q['c'])!=key]
            self.log(kind='unmatched_mark_unknown',slot=slot,cell_index=cell,source_ref=event.get('source_ref'))

    def summary(self):
        targets={(c['slot'],*idx2rc(k)) for c in self.cards or [] for k,n in enumerate(c['vals']) if k!=12 and n in self.called}
        special=getattr(self,'special_observed',set())
        unknown=(self.giveup|special|self.tapped)-self.done
        return dict(targets=len(targets),dispatched=self.n_tap,confirmed=len(self.done),
                    unattempted=len(targets-self.tapped-special),unknown=len(targets&unknown),
                    pending=len(self.pending),awaiting=len(self.awaiting),retries=self.n_retry,
                    target_states=[dict(slot=k[0],cell_index=k[2]*5+k[1],
                      input_ready=bool(self.grid and self.grid[k[0]].get('input_ready')),
                      blocked_reason=(self.grid[k[0]].get('pause_reason') if self.grid and not self.grid[k[0]].get('input_ready') else
                          'cell_not_reachable' if self.grid and k[2]*5+k[1] not in self.grid[k[0]].get('reachable_cells',range(25)) else None),
                      status='confirmed' if k in self.done else 'special_unknown' if k in special else
                      'attempted_unknown' if k in self.tapped else 'unattempted') for k in sorted(targets)])


def preflight():
    from bv_live import preflight as live_preflight,Budget
    b=Budget();sid='readonly_check_'+str(time.time_ns());start=time.monotonic()
    b.append('runtime_start',session_id=sid)
    try:return live_preflight()[0]
    finally:b.append('runtime_end',session_id=sid,seconds=time.monotonic()-start)


def main():
    ap = argparse.ArgumentParser(description="TASK-0039 受控定位、来源核验与自动玩入口")
    ap.add_argument("--check", action="store_true", help="只读检查；Blocked 返回 2")
    ap.add_argument("--start", action="store_true", help="正式验收启动；先核对当前数据和资源")
    ap.add_argument("--diagnose", action="store_true", help="受控定位；结果不能作为正式验收")
    ap.add_argument("--open-panel", action="store_true", help="定位时允许从已识别大厅打开选卡面板；不点击购买")
    ap.add_argument("--diagnostic-round", action="store_true", help="定位时按结构化报价买四卡并作一次合法点击；任务累计最多三局")
    ap.add_argument("--seconds", type=float, default=20, help="定位运行秒数，最多300")
    ap.add_argument("--batch-results", metavar="BATCH", help="从预登记和冻结原始来源重建十局结果")
    ap.add_argument("--stop", metavar="SESSION", help="仅向指定本工具会话写 STOP，不停止采集器")
    ap.add_argument("--results", metavar="FROZEN", help="独立核验冻结证据")
    a = ap.parse_args()
    if a.stop:
        target = Path(a.stop).resolve()
        root = Path(SESS).resolve()
        from bv_live import CONTROL
        owned = (root in target.parents and target.name.startswith("autoplay_")) or (target.parent==CONTROL.resolve() and target.name.startswith(("diagnostic_","batch_"))) or (CONTROL.resolve() in target.parents and target.name.startswith("acceptance_") and target.parent.name.startswith("batch_"))
        if not owned or not target.is_dir():
            ap.error("只能停止本工作副本 sessions 中的指定 autoplay 会话")
        (target / "STOP").touch(exist_ok=True)
        print(json.dumps({"status": "stop_requested", "stopped_confirmed": False}))
        return 0
    if a.results:
        from bv_live import verify_round
        result = verify_round(a.results)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["acceptance_pass"] else 2
    if a.batch_results:
        from bv_batch import verify_batch
        result=verify_batch(Path(a.batch_results))
        print(json.dumps(result,ensure_ascii=False))
        return 0 if result["acceptance_pass"] else 2
    if a.diagnose:
        from bv_live import diagnose,LIMITS
        if not 0<a.seconds<=LIMITS['round_seconds']:ap.error("定位时长超过单局限制")
        result=diagnose(a.seconds,a.open_panel,play_round=a.diagnostic_round)
        print(json.dumps(result,ensure_ascii=False))
        return 2 # diagnostic collection is never production acceptance
    if a.start:
        from bv_live import start_batch
        result=start_batch();print(json.dumps(result,ensure_ascii=False))
        return 0 if result["acceptance_pass"] else 2
    result=preflight();print(json.dumps(result, ensure_ascii=False))
    return 0 if result['live_ready'] else 2


if __name__ == "__main__":
    sys.exit(main())
