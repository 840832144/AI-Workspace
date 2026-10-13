# -*- coding: utf-8 -*-
"""Bingo Voyage TASK-0039: bounded controller corrections and diagnostic checks.

Live buy/settlement bindings and accepted-fill semantics remain unverified.
The CLI fails closed; --check reports the missing gates, --results audits frozen
evidence. No C->S observation is promoted to a success acknowledgement.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time
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
                           capture_output=True, timeout=60)
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
        self.sess = os.path.join(SESS, "autoplay_" + time.strftime("%Y%m%d_%H%M%S"))
        self.sess += "_%d" % time.time_ns()
        os.makedirs(self.sess, exist_ok=False)
        self.act = open(os.path.join(self.sess, "actions.jsonl"), "w", encoding="utf-8")
        self.reader = Reader(WS)
        self.rid = None
        self.cards = None
        self.grid = None
        self.order = ([x.strip() for x in a.map.split(",")] if a.map else list(DEFAULT_ORDER))
        self.called = []
        self.done = set()
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
            # Four distinct nonoverlapping card rectangles, not four detections of one.
            for i in range(1, 5):
                for j in range(i+1, 5):
                    x, y = grid[i], grid[j]
                    if not (x["cols"][-1] < y["cols"][0] or y["cols"][-1] < x["cols"][0] or
                            x["rows"][-1] < y["rows"][0] or y["rows"][-1] < x["rows"][0]):
                        raise ValueError("overlap")
            stable = self.layout_candidate is not None and max(
                abs(grid[i][a][k]-self.layout_candidate[i][a][k])
                for i in grid for a in ("cols", "rows") for k in range(5)) <= 4
            previous_at = getattr(self, "layout_sample_at", None)
            if stable and previous_at is not None and now-previous_at < .4:
                return False
            self.layout_sample_at = now
            self.layout_samples = self.layout_samples + 1 if stable else 1
            if not stable:
                self.grid = None
                self.layout_candidate = grid
            if self.layout_samples < 3:
                return False
            if self.grid != grid:
                self.layout_version += 1
            self.grid = grid
            self.layout_at = time.monotonic()
            return True
        except (ValueError, KeyError, TypeError):
            self.grid = None
            self.layout_candidate = None
            self.layout_samples = 0
            self.layout_sample_at = None
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
            self.closed = True
            self.closed_rounds.add(rid)
            self.pending.clear()
            self.grid = None
            self.freeze_round("verified_close")

    def on_ball(self, ts, rid, ball):
        now = time.monotonic()
        if rid in self.closed_rounds:
            self.log(kind="late_round_ignored")
            return
        if self.rid and rid != self.rid:
            # A ball with another ID cannot authorize a round switch or buy cards.
            self.halted = True
            self.grid = None
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
                if number != ball or k == 12 or key in self.done:
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
        if self.input_future is not None or self.closed or self.halted or not self.grid or now-self.layout_at > 2.5:
            return
        ready = [q for q in self.pending if q["due"] <= now and q["round_id"] == self.rid]
        # New targets before bounded retries; sparse observations never hold input slots.
        ready.sort(key=lambda q: (q["tries"], -self.first_seen[q["ball"]], q["slot"]))
        if not ready:
            return
        q = ready[0]
        self.pending.remove(q)
        g = self.grid[q["slot"]]
        x, y = g["cols"][q["c"]], g["rows"][q["r"]]
        q["layout_version"] = self.layout_version
        self.tapped.add((q["slot"], q["r"], q["c"]))
        self.log(kind="attempt", slot=q["slot"], cell_index=q["c"]*5+q["r"],
                 layout_version=self.layout_version, x=x, y=y)
        self.input_target = q
        def execute():
            if self.closed or self.halted or q["round_id"] != self.rid:
                return "not_executed"
            return "dry" if self.a.dry else tap(x, y)
        self.input_future = self.input_pool.submit(execute)
        self.n_tap += int(not self.a.dry)

    def go_next_round(self):
        self.halted = True
        self.grid = None
        self.log(kind="blocked_navigation", reason="resource_and_round_close_binding_unverified")
        return False

    def run(self):
        """Read-only diagnostic run; runtime limit is NOT a round-close event."""
        t0 = time.monotonic()
        try:
            while time.monotonic()-t0 < self.a.seconds and not self.halted:
                if os.path.exists(os.path.join(self.sess, "STOP")):
                    break
                balls, observations = self.reader.poll()
                for ts, rid, ball in balls:
                    self.on_ball(ts, rid, ball)
                self.tick(observations)
                time.sleep(.05)
        finally:
            self.halted = True
            self.input_pool.shutdown(wait=True, cancel_futures=True)
            self.freeze_round("stopped_or_timed_out_not_complete")
            with open(os.path.join(self.sess, "events.jsonl"), "x", encoding="utf-8") as f:
                for e in self.reader.events:
                    f.write(json.dumps(e, ensure_ascii=False)+"\n")
            with open(os.path.join(self.sess, "session.json"), "x", encoding="utf-8") as f:
                json.dump({"complete": False, "reason": "no_verified_close_binding",
                           "capture_errors": dict(self.reader.errors)}, f)
            self.act.close()
        return 2

    # ---- 受控实验：反推卡位映射 ----
    def probe_map(self):
        raise RuntimeError("scoped_experiment_authorization_required")


def preflight():
    return {"status": "Blocked", "live_ready": False,
            "blockers": ["accepted_fill_semantics_unverified",
                         "round_close_binding_unverified", "structured_bet_binding_unverified"],
            "resource_decision": "User delegated conservative limits; no spend until bet and consumption are verifiable",
            "offline_entry": "python -m unittest discover -s tests -v"}


def main():
    ap = argparse.ArgumentParser(description="TASK-0039 安全检查与离线修复；真实自动玩尚被证据 Gate 阻塞")
    ap.add_argument("--check", action="store_true", help="只读检查；Blocked 返回 2")
    ap.add_argument("--start", action="store_true", help="请求启动；先检查证据 Gate，当前版本返回 Blocked")
    ap.add_argument("--stop", metavar="SESSION", help="仅向指定本工具会话写 STOP，不停止采集器")
    ap.add_argument("--results", metavar="FROZEN", help="独立核验冻结证据")
    a = ap.parse_args()
    if a.stop:
        from pathlib import Path
        target = Path(a.stop).resolve()
        root = Path(SESS).resolve()
        if root not in target.parents or not target.name.startswith("autoplay_") or not target.is_dir():
            ap.error("只能停止本工作副本 sessions 中的指定 autoplay 会话")
        (target / "STOP").touch(exist_ok=True)
        print(json.dumps({"status": "stop_requested", "stopped_confirmed": False}))
        return 0
    if a.results:
        from bv_evidence import measure
        with open(a.results, encoding="utf-8") as f:
            result = measure(json.load(f))
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["hard_pass"] else 2
    print(json.dumps(preflight(), ensure_ascii=False))
    return 2


if __name__ == "__main__":
    sys.exit(main())
