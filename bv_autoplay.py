# -*- coding: utf-8 -*-
"""Bingo Voyage 自动玩 —— 事件驱动版。

设计原则（按要求重写）
----------------------
1) **决策全部走事件/参数，不做逐次图像采样。**
   出球来自 `cmd 169`，卡面来自 `cmd 163/166/167`，
   点击位置 = 内置卡位表 + 卡面里的格号，纯数据算出来，不看图。
2) **只点已经出过的球。** 维护本局「已叫号集合」，只有号码在集合里的格子才进队列。
3) **不能比出球还早点。** 收到出球后先等 `--settle` 秒 —— 客户端还在播报球动画，
   这时游戏内部还没认定这球已叫，点了不会生效。
4) **用 `cmd 167 subtype1` 当点击回执。** 客户端成功 daub 会立刻上行该帧；
   规定时间内没收到就重试（最多 `--retries` 次）。全程不看像素。
5) **图像只用在两处**：可选的卡位核对（`--recalibrate`，默认关）；
   以及后续做「自动续局/回大厅」时判断当前界面。

用法
----
    python bv_autoplay.py --seconds 200 --auto-next      # 正式
    python bv_autoplay.py --seconds 60 --dry             # 只决策不点击
    python bv_autoplay.py --probe-map --seconds 90       # 受控实验：反推卡位映射
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time

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

# ---------------------------------------------------------------------------
# 内置卡位表：进对局后卡面位置固定（实测），所以直接查表，不需要看图。
# LAYOUTS[n] = [ [卡0, 卡1, ...] ]，列表顺序 = 视觉位置 POS_OF_LAYOUT
# ---------------------------------------------------------------------------
POS_OF_LAYOUT = ["tl", "tr", "bl", "br"]
LAYOUTS = {
    1: [[{"cols": [222, 336, 450, 564, 678], "rows": [647, 761, 875, 989, 1103]}]],
    2: [[{"cols": [222, 336, 450, 564, 678], "rows": [311, 425, 539, 653, 767]},
         {"cols": [222, 336, 450, 564, 678], "rows": [982, 1096, 1210, 1324, 1438]}]],
    4: [[{"cols": [79, 158, 238, 318, 398], "rows": [498, 578, 657, 737, 817]},
         {"cols": [502, 581, 662, 742, 821], "rows": [498, 578, 657, 737, 817]},
         {"cols": [79, 158, 238, 318, 398], "rows": [959, 1039, 1118, 1198, 1278]},
         {"cols": [502, 581, 662, 742, 821], "rows": [959, 1039, 1118, 1198, 1278]}]],
}

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
    if r.returncode != 0:                       # 兜底：极少数机型 tap 不好使
        subprocess.run([ADB, "-s", DEV, "shell", "input", "swipe",
                        str(x), str(y), str(x), str(y), "80"],
                       capture_output=True, timeout=30)


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

def ts2s(t):
    return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timestamp()


def rid_of(body):
    for s in harvest_strings(body, 20, 6):
        if s.startswith("BINGO_HALL") and s.count(".") >= 3 and s.rsplit(".", 1)[-1].isdigit():
            return s
    return None


# ---------------------------------------------------------------------------
class Reader:
    """增量读 WS：出球 / 卡面 / daub 回执"""

    def __init__(self, path, backscan=8000):
        self.path = path
        self.pos = os.path.getsize(path)
        self.cards = {}
        self.new_balls = []
        self.acks = []
        self.events = []
        lines = open(path, encoding="utf-8").read().splitlines()
        for line in lines[-backscan:]:
            line = line.strip()
            if line:
                try:
                    self._handle(json.loads(line), collect=False)
                except Exception:
                    pass

    def _handle(self, rec, collect=True):
        p = os.path.join(BODIES, rec.get("file", ""))
        if not os.path.exists(p):
            return
        try:
            fr = parse_frame(open(p, "rb").read())
        except Exception:
            return
        if not fr.get("ok"):
            return
        cmd, d, body, ts = fr["cmd"], rec["dir"], fr["body"], rec["ts"]
        if collect:
            self.events.append({"ts": ts, "dir": d, "cmd": cmd, "len": len(body)})

        if d == "S->C" and cmd in (163, 166, 167):
            got = extract_cards(body)
            rid = rid_of(body)
            if got and rid:
                fp = tuple(tuple(c["vals"]) for c in got)
                self.cards.setdefault(rid, {})
                self.cards[rid][fp] = self.cards[rid].get(fp, 0) + 1

        elif d == "S->C" and cmd == 169:
            rid = rid_of(body)
            win = []
            for fld, wt, val, ch in parse(body):
                if fld == 2 and wt == 2 and ch is not None:
                    win = list(ch)
                    break
            if rid and win and collect:
                self.new_balls.append((ts, rid, win[-1]))

        elif d == "C->S" and cmd == 167:
            # daub 回执：{1:...} 是 subtype；subtype 1 时 payload 里带 {1:格, 2:卡}
            sub, f1, f2 = None, None, None
            for fld, wt, val, ch in parse(body):
                if fld != 2 or wt != 2 or ch is None:
                    continue
                inner = parse(ch)
                for f2_, w2, v2, c2 in inner:
                    if f2_ == 1 and w2 == 0 and sub is None:
                        sub = v2
                        break
                if sub == 1:
                    for f2_, w2, v2, c2 in inner:
                        if w2 == 2 and c2 is not None:
                            for f3, w3, v3, c3 in parse(c2):
                                if f3 == 1 and w3 == 0:
                                    f1 = v3
                                elif f3 == 2 and w3 == 0:
                                    f2 = v3
                        elif w2 == 0 and f2_ == 3:
                            f1 = v2
            if collect and sub == 1:
                self.acks.append((ts, f1, f2))

    def round_balls(self, rid):
        """把整局已经叫过的号从抓包里回捞出来。

        cmd 169 每帧带「最近 5 个号」的滑动窗口，把整局所有 169 帧的窗口
        求并集就能还原完整叫号序列 —— 中途挂载的会话靠这个才救得回开局那段，
        否则那些格子永远没人点（就是一直闪的白数字）。
        """
        out, seen = [], set()
        try:
            for line in open(self.path, encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("dir") != "S->C" or rec.get("hdr", {}).get("cmd") != 169:
                    continue
                p = os.path.join(BODIES, rec.get("file", ""))
                if not os.path.exists(p):
                    continue
                try:
                    fr = parse_frame(open(p, "rb").read())
                except Exception:
                    continue
                if not fr.get("ok") or rid_of(fr["body"]) != rid:
                    continue
                for fld, wt, val, ch in parse(fr["body"]):
                    if fld == 2 and wt == 2 and ch is not None:
                        for b in ch:
                            if b not in seen:
                                seen.add(b)
                                out.append(b)
                        break
        except Exception:
            pass
        return out

    def poll(self):
        self.new_balls = []
        self.acks = []
        size = os.path.getsize(self.path)
        if size > self.pos:
            with open(self.path, encoding="utf-8") as f:
                f.seek(self.pos)
                chunk = f.read()
                self.pos = f.tell()
            for line in chunk.splitlines():
                line = line.strip()
                if line:
                    try:
                        self._handle(json.loads(line), collect=True)
                    except Exception:
                        pass
        return self.new_balls, self.acks

    def best_cards(self, rid):
        d = self.cards.get(rid)
        if not d:
            return None
        fp = max(d.items(), key=lambda kv: kv[1])[0]
        return [{"slot": i + 1, "vals": list(v)} for i, v in enumerate(fp)]


# ---------------------------------------------------------------------------
class AutoPlay:
    def __init__(self, a):
        self.a = a
        self.sess = os.path.join(SESS, "autoplay_" + time.strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.sess, exist_ok=True)
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
        self.t_last_rescan = time.time()

    def log(self, **kw):
        kw["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.act.write(json.dumps(kw, ensure_ascii=False) + "\n")
        self.act.flush()

    # ---- 卡位：每局开局用截图实测一次；失败退回内置表 ----
    def detect_grid(self):
        """返回 [卡0, 卡1, ...]（视觉顺序 tl,tr,bl,br），或 None"""
        try:
            from PIL import Image
            import bv_cardgrid
            path = os.path.join(self.sess, "_grid.png")
            shot(path)
            return bv_cardgrid.detect(Image.open(path).convert("RGB"))
        except Exception as e:
            print("    [卡位] 实测失败 %r" % (e,))
            return None

    def setup_grid(self, nslots):
        vis2slot = {}
        for i, slot in enumerate(range(1, nslots + 1)):
            vis2slot[self.order[i] if i < len(self.order) else POS_OF_LAYOUT[i]] = slot

        # 1) 先实测
        det = self.detect_grid()
        if det and len(det) == nslots:
            self.grid = {}
            for k, c in enumerate(det):
                pos = self.pos_of_detected(det, k)
                if pos in vis2slot:
                    self.grid[vis2slot[pos]] = {"cols": c["cols"], "rows": c["rows"]}
            if len(self.grid) == nslots:
                print("  [卡位] 实测 %d 张卡（列间距 %.0f）" % (nslots, det[0]["spacing"]))
                for slot in sorted(self.grid):
                    g = self.grid[slot]
                    print("        卡%d -> %s cols=[%s] rows=[%s]" % (
                        slot, self.order[slot - 1],
                        ",".join("%.0f" % x for x in g["cols"]),
                        ",".join("%.0f" % y for y in g["rows"])))
                return True
            print("  [卡位] 实测张数对但映射不全，退回内置表")

        # 2) 兜底：内置表
        layout = LAYOUTS.get(nslots)
        if not layout:
            print("  [!] 没有 %d 张卡的内置卡位表" % nslots)
            return False
        self.grid = {}
        for k, cell in enumerate(layout[0]):
            p = POS_OF_LAYOUT[k]
            if p in vis2slot:
                self.grid[vis2slot[p]] = {"cols": list(cell["cols"]), "rows": list(cell["rows"])}
        print("  [卡位] 用内置表 %d 张卡" % nslots)
        return len(self.grid) == nslots

    @staticmethod
    def pos_of_detected(cards, k):
        """判出第 k 张实测卡在画面上的方位名 tl/tr/bl/br"""
        xs = [(c["cols"][0] + c["cols"][-1]) / 2.0 for c in cards]
        ys = [(c["rows"][0] + c["rows"][-1]) / 2.0 for c in cards]
        mx = (min(xs) + max(xs)) / 2.0
        my = (min(ys) + max(ys)) / 2.0
        return ("t" if ys[k] <= my else "b") + ("l" if xs[k] <= mx else "r")

    def _check_with_screen(self):
        try:
            from PIL import Image
            import bv_cardgrid
            p = shot(os.path.join(self.sess, "grid_check.png"))
            cards = bv_cardgrid.detect(Image.open(p).convert("RGB"))
            print("    [核对] 截图检出 %d 张卡（内置表 %d 张）%s"
                  % (len(cards), len(self.grid),
                     "" if len(cards) == len(self.grid) else "  ← 不一致，需重新标定"))
        except Exception as e:
            print("    [核对] 跳过 (%r)" % (e,))

    # ---- 出球 ----
    def on_ball(self, ts, rid, ball):
        if rid != self.rid:
            print("  [新局] %s" % rid[-22:])
            self.rid = rid
            # ★ 从抓包回捞整局叫号，救回「会话挂上之前」叫掉的号
            hist = self.reader.round_balls(rid)
            self.called = hist if hist else []
            self.done.clear()
            self.tapped.clear()
            self.pending.clear()
            self.awaiting.clear()
            if self.cards:
                self.cards_used = self.cards      # ★ 换局也不丢上一局的卡面留档
                self.grid_used = self.grid
            self.cards = None
            self.grid = None
            self.n_nocard = 0
            self.n_grid_wait = 0
        self.called.append(ball)                      # ★ 只认已叫过的号
        if self.cards is None:
            got = self.reader.best_cards(rid)
            if not got:
                self.n_nocard += 1
                # 本局卡面只在「进局那一刻」由服务端下发（cmd 163/166）。
                # 中途挂上来的会话拿不到，只能等下一局开局；这里不刷屏。
                if self.n_nocard == 1:
                    print("  [待卡面] 本局无卡面下发（中途挂载），等下一局开局…")
                elif self.a.wait_round and self.n_nocard % 40 == 0:
                    print("  [待卡面] 仍在等下一局开局（已等 %d 个号）" % self.n_nocard)
                if not self.a.wait_round:
                    print("    球 %d (第 %d 次无卡面)" % (ball, self.n_nocard))
                    if self.a.auto_next and self.n_nocard >= 3:
                        self.go_next_round()
                return
            self.n_nocard = 0
            self.n_grid_wait = 0
            self.cards = got
            self.cards_used = got
        # 卡面有了但还没标定出卡位（例如结算/大厅界面挡着）→ 每个球都重试标定
        if self.cards is not None and not self.grid:
            if not self.setup_grid(len(self.cards)):
                self.n_grid_wait += 1
                if self.n_grid_wait == 1 or self.n_grid_wait % 20 == 0:
                    print("  [卡位] 当前画面不是对局界面，等它出现后再测（第 %d 次）"
                          % self.n_grid_wait)
                return
            self.n_grid_wait = 0
            print("  [卡面] %d 张就绪（含开局前补排）" % len(self.cards))
            self.backfill()          # ★ 补排「拿到卡面之前」已经叫过的球
            return

        due = ts2s(ts) + self.a.settle                # ★ 等客户端播完球再点
        n = self.queue_targets(ball, due, verbose=False)
        if n == 0:
            self.n_miss += 1
            print("    球 %2d  (不在卡上)" % ball)
        else:
            print("    球 %2d  排入 %d 个目标（%.1fs 后点）" % (ball, n, self.a.settle))

    def queue_targets(self, ball, due, verbose=True):
        """把某个已叫号在卡面上对应的、还没 daub 的格子排进队列。返回新增个数。"""
        n = 0
        for c in (self.cards or []):
            slot = c["slot"]
            g = self.grid.get(slot)
            if not g:
                continue
            vals = c["vals"]
            for k in range(min(25, len(vals))):
                if vals[k] != ball:
                    continue
                col_, r_ = k // 5, k % 5
                if r_ == 2 and col_ == 2:
                    continue
                if (slot, r_, col_) in self.done:
                    continue
                if (slot, r_, col_) in self.tapped:      # ★ 每格只点一次，不再因无回执反复补排
                    continue
                if any(q["slot"] == slot and q["r"] == r_ and q["c"] == col_
                       for q in self.pending + self.awaiting):
                    continue
                self.pending.append({"ball": ball, "slot": slot, "r": r_, "c": col_,
                                     "x": g["cols"][col_], "y": g["rows"][r_], "due": due})
                n += 1
                if verbose:
                    print("      (补排) 球 %d -> 卡%d r%dc%d" % (ball, slot, r_ + 1, col_ + 1))
        return n

    def backfill(self):
        """拿到卡面后，把之前已经叫过的球全部补排 —— 这些球原来全被漏掉了（就是闪个不停的格子）"""
        now = time.time()
        n = 0
        for b in self.called:
            n += self.queue_targets(b, now, verbose=False)
        if n:
            print("  [补排] 把已叫号的 %d 个历史球补成了 %d 个待点格" % (len(self.called), n))
        return n

    def rescan(self):
        """周期补扫：已叫号集合里凡是还没 daub、又不在队列里的格，全部补排"""
        now = time.time()
        n = 0
        for b in self.called:
            n += self.queue_targets(b, now, verbose=False)
        if n:
            print("  [补扫] 补排 %d 个漏掉的格" % n)
        return n

    # ---- 点击 + 回执 ----
    def tick(self, acks):
        now = time.time()
        for (ts, f1, f2) in acks:
            slot = (f2 + 1) if isinstance(f2, int) else None
            rc = idx2rc(f1) if isinstance(f1, int) else None
            matched = None
            if slot is not None and rc is not None:
                for a in self.awaiting:
                    if a["slot"] == slot and (a["r"], a["c"]) == rc:
                        matched = a
                        break
            exact = matched is not None
            if matched is None and self.awaiting:
                matched = self.awaiting[0]
                slot, rc = matched["slot"], (matched["r"], matched["c"])
            if matched is not None:
                self.awaiting.remove(matched)
                self.n_ack += 1
                self.done.add((slot, rc[0], rc[1]))
                print("      ✓ 回执 卡%d r%dc%d (f1=%s f2=%s)%s" % (
                    slot, rc[0] + 1, rc[1] + 1, f1, f2, "" if exact else "  [按序兜配]"))
                self.log(kind="ack", ball=matched["ball"], slot=slot, r=rc[0], c=rc[1],
                         field1=f1, field2=f2, tries=matched["tries"] + 1, exact=exact)
                if not exact:
                    self.n_mismatch += 1
            else:
                self.log(kind="ack_orphan", field1=f1, field2=f2)
        for a in list(self.awaiting):
            if now - a["t"] > self.a.ack_wait:
                self.awaiting.remove(a)
                if a["tries"] < self.a.retries:
                    a["tries"] += 1
                    self.n_retry += 1
                    print("      ⟳ 无回执，重试第 %d 次：球%d 卡%d r%dc%d" % (
                        a["tries"], a["ball"], a["slot"], a["r"] + 1, a["c"] + 1))
                    self.log(kind="retry", ball=a["ball"], slot=a["slot"],
                             r=a["r"], c=a["c"], tries=a["tries"])
                    if not self.a.dry:
                        tap(a["x"], a["y"])
                        self.n_tap += 1
                    a["t"] = now
                    self.awaiting.append(a)
                else:
                    rec = a.get("recycles", 0)
                    if rec < 0:                       # ★ 已停用回收重排（改为每格只点一次）
                        a["tries"] = 0
                        a["recycles"] = rec + 1
                        a["due"] = now + 0.4
                        a["t"] = now
                        self.pending.append(a)
                        print("      ↺ 回收重排：球%d 卡%d r%dc%d（第 %d 轮）" % (
                            a["ball"], a["slot"], a["r"] + 1, a["c"] + 1, rec + 1))
                        self.log(kind="recycle", ball=a["ball"], slot=a["slot"],
                                 r=a["r"], c=a["c"], rounds=rec + 1)
                    else:
                        self.n_giveup += 1
                        self.giveup.add((a["slot"], a["r"], a["c"]))
                        print("      ✗ 放弃：球%d 卡%d r%dc%d" % (
                            a["ball"], a["slot"], a["r"] + 1, a["c"] + 1))
                        self.log(kind="give_up", ball=a["ball"], slot=a["slot"],
                                 r=a["r"], c=a["c"], tries=a["tries"])
        if len(self.awaiting) >= self.a.inflight:
            return
        for p in [q for q in self.pending if q["due"] <= now]:
            if len(self.awaiting) >= self.a.inflight:
                break
            self.pending.remove(p)
            print("    球 %2d  -> 卡%d r%dc%d  tap(%d,%d)" % (
                p["ball"], p["slot"], p["r"] + 1, p["c"] + 1, p["x"], p["y"]))
            self.log(kind="tap", ball=p["ball"], slot=p["slot"], r=p["r"], c=p["c"],
                     x=p["x"], y=p["y"])
            self.tapped.add((p["slot"], p["r"], p["c"]))   # ★ 记「已点过」
            if not self.a.dry:
                tap(p["x"], p["y"])
                self.n_tap += 1
            p["t"] = time.time()
            p["tries"] = 0
            self.awaiting.append(p)

    # ---- 界面识别（只在续局/回大厅这类导航时用图像）----
    def probe_screen(self):
        """返回 (state, ncards)：state in {round, congrats, lobby, betpanel, unknown}"""
        path = os.path.join(self.sess, "_probe.png")
        shot(path)
        try:
            from PIL import Image
            import bv_cardgrid
            img = Image.open(path).convert("RGB")
            cards = bv_cardgrid.detect(img)
            if cards:
                self._last_cards = cards
                return "round", len(cards)
            px = img.load()

            def patch(x, y, r=18):
                rs = gs = bs = n = 0
                for dy in range(-r, r + 1, 4):
                    for dx in range(-r, r + 1, 4):
                        c = px[min(max(x + dx, 0), img.width - 1),
                               min(max(y + dy, 0), img.height - 1)]
                        rs += c[0]; gs += c[1]; bs += c[2]; n += 1
                return rs / n, gs / n, bs / n

            # 结算屏：顶部大字 CONGRATS（橙红）
            r1, g1, b1 = patch(450, 108)
            if r1 > 170 and r1 - g1 > 45 and r1 - b1 > 60:
                return "congrats", 0
            # 玩法面板：中部大片绿色（BINGO WIN 大圆）
            r2, g2, b2 = patch(450, 620)
            if g2 > 140 and g2 - r2 > 35 and g2 - b2 > 35:
                return "betpanel", 0
            # 大厅：左下 PLAY 是绿色大按钮
            r3, g3, b3 = patch(225, 1308)
            if g3 > 120 and g3 - r3 > 25 and g3 - b3 > 25:
                return "lobby", 0
            return "unknown", 0
        except Exception as e:
            print("    [界面识别] 失败 %r" % (e,))
            return "unknown", 0

    def in_round(self):
        st, n = self.probe_screen()
        return st == "round", st, n

    def go_next_round(self):
        """进对局：按候选点依次推进，每步后以「能否检出卡片」验证。

        非对局状态不止一种（结算屏 / 大厅 / 玩法面板 / 章节剧情过场），
        用颜色分类很容易误判（实测把甲板木色当成 CONGRATS 橙红）。
        这里只保留一个可靠判据 —— 屏幕上能不能检出卡片，其余靠候选点覆盖。
        """
        CANDS = [
            (450, 1520, "continue"),    # 剧情过场 "Tap to continue"
            (450, 1035, "claim"),       # 结算屏 CLAIM
            (450, 1308, "orlando"),     # 大厅：章节领奖 / 房间面板
            (225, 1308, "play"),        # 大厅 PLAY
            (450, 1185, "bet_play"),    # 玩法面板 PLAY
        ]
        print("  [续局] 第 %d 次" % (self.n_auto + 1))
        self.log(kind="auto_next", step=0)
        ok = False
        for attempt in range(1, 4):
            st, n = self.in_round()
            if st:
                ok = True
                break
            print("    [尝试 %d] 不在对局，依次试候选点" % attempt)
            for (x, y, nm) in CANDS:
                if self.a.dry:
                    print("      跳过 %s（dry）" % nm)
                    continue
                tap(x, y)
                time.sleep(2.2)
                self.log(kind="nav_tap", name=nm, x=x, y=y)
                st2, n2 = self.in_round()
                if st2:
                    print("      点 %s 后进局（%d 张卡）" % (nm, n2))
                    ok = True
                    break
                print("      点 %-9s (%d,%d) -> 仍未进局" % (nm, x, y))
            if ok:
                break
            time.sleep(1.5)
        if ok:
            print("    [续局] 已进入对局")
        else:
            print("    [续局] 3 轮都没进局")
        self.n_auto += 1
        self.n_nocard = 0
        self.cards = None
        self.grid = None
        self.pending.clear()
        self.awaiting.clear()
        self.done.clear()
        self.log(kind="auto_next", step=9, done=ok)
        return ok

    def in_round(self):
        """唯一可靠判据：屏幕上能不能检出 bingo 卡"""
        path = os.path.join(self.sess, "_probe.png")
        shot(path)
        try:
            from PIL import Image
            import bv_cardgrid
            cards = bv_cardgrid.detect(Image.open(path).convert("RGB"))
            self._last_cards = cards
            return len(cards) > 0, len(cards)
        except Exception as e:
            print("    [判据] 截图检测失败 %r" % (e,))
            return False, 0

    def probe_screen(self):
        st, n = self.in_round()
        return ("round" if st else "unknown"), n


    def run(self):
        t0 = time.time()
        print("会话目录 %s" % self.sess)
        print("参数 settle=%.1fs ack_wait=%.1fs retries=%d inflight=%d map=%s%s"
              % (self.a.settle, self.a.ack_wait, self.a.retries, self.a.inflight,
                 self.order, "  [DRY]" if self.a.dry else ""))
        while time.time() - t0 < self.a.seconds:
            balls, acks = self.reader.poll()
            for (ts, rid, ball) in balls:
                self.on_ball(ts, rid, ball)
            self.tick(acks)
            if self.cards and time.time() - self.t_last_rescan > self.a.rescan:
                self.t_last_rescan = time.time()
                self.rescan()
            time.sleep(0.3)
        # 本局用到的卡面参数落盘 —— 度量与复盘都以此为唯一依据，不再依赖全局卡表
        json.dump({"round": self.rid, "map": self.order,
                   "cards": getattr(self, "cards_used", None) or self.cards or [],
                   "grid": getattr(self, "grid_used", None) or self.grid or {}},
                  open(os.path.join(self.sess, "cards_in_round.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        summ = {"start": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t0)),
                "seconds": self.a.seconds, "dry": self.a.dry,
                "settle": self.a.settle, "ack_wait": self.a.ack_wait,
                "taps": self.n_tap, "acks": self.n_ack, "retries": self.n_retry,
                "give_up": 0, "auto_next": self.n_auto, "map": self.order,
                "round": self.rid, "called_balls": len(self.called),
                "daubed_cells": len(self.done), "retry_giveup": self.n_giveup,
                "ack_mismatch": self.n_mismatch, "balls_not_on_card": self.n_miss,
                "frames_seen": len(self.reader.events)}
        json.dump(summ, open(os.path.join(self.sess, "session.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        with open(os.path.join(self.sess, "events.jsonl"), "w", encoding="utf-8") as f:
            for e in self.reader.events:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        print("\n结束：点击 %d / 回执 %d / 重试 %d / 续局 %d / 已 daub %d 格 / 球不在卡上 %d"
              % (self.n_tap, self.n_ack, self.n_retry, self.n_auto,
                 len(self.done), self.n_miss))
        print("会话摘要 -> %s" % os.path.join(self.sess, "session.json"))
        self.act.close()
        return 0

    # ---- 受控实验：反推卡位映射 ----
    def probe_map(self):
        print("=== 受控实验：反推「协议卡下标 -> 视觉位置」映射 ===")
        print("逻辑：一个已叫号的球只出现在部分协议卡上；")
        print("      依次点 4 个物理位置的对应格，只有协议卡里真有这个号的位置才会收到回执。")
        t0 = time.time()
        while time.time() - t0 < self.a.seconds:
            balls, _ = self.reader.poll()
            for (ts, rid, ball) in balls:
                self.on_ball(ts, rid, ball)
            if self.cards and self.pending:
                break
            time.sleep(0.3)
        if not self.cards:
            print("没拿到卡面，退出")
            return 1
        p = self.pending[0]
        ball = p["ball"]
        on_slots = sorted({c["slot"] for c in self.cards
                           if ball in c["vals"]})
        print("\n球 %d 出现在协议卡 %s 上" % (ball, on_slots))
        nslots = len(self.cards)
        layout = LAYOUTS.get(nslots, [[]])[0]
        results = {}
        for k, cell in enumerate(layout):
            r_ = p["r"]
            c_ = p["c"]
            x, y = cell["cols"][c_], cell["rows"][r_]
            pos = POS_OF_LAYOUT[k]
            print("  物理位置 %-2s tap(%d,%d) …" % (pos, x, y))
            if not self.a.dry:
                tap(x, y)
            time.sleep(4.2)
            _, acks = self.reader.poll()
            got = acks[-1] if acks else None
            results[pos] = got
            print("      回执 = %s  -> %s" % (got, "有（该位置=球所在的协议卡之一）" if got else "无"))
            self.log(kind="probe", pos=pos, x=x, y=y, ack=got, ball=ball)
        hit = [p_ for p_, g in results.items() if g]
        print("\n结论：有回执的物理位置 %s，协议卡 %s" % (hit, on_slots))
        if len(hit) == len(on_slots):
            print("        => 把 %s 依次对应到协议卡 %s" % (hit, on_slots))
        else:
            print("        个数不一致，需要换一个球再跑一次")
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=200)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--auto-next", action="store_true")
    ap.add_argument("--settle", type=float, default=1.8,
                    help="出球后等多久再点（太早点不中，客户端还在播球）")
    ap.add_argument("--ack-wait", type=float, default=1.5, help="点完等回执的秒数")
    ap.add_argument("--retries", type=int, default=0,
                    help="没回执时补点次数。实测单击命中率就够，回执稀疏不能当判据，默认不重试")
    ap.add_argument("--inflight", type=int, default=3, help="同时最多几个点击在等回执")
    ap.add_argument("--map", default="", help="协议下标到视觉位置，如 tl,bl,tr,br")
    ap.add_argument("--rescan", type=float, default=1.2, help="周期补扫间隔秒")
    ap.add_argument("--recalibrate", action="store_true", help="用截图核对卡位（默认不用）")
    ap.add_argument("--probe-map", action="store_true")
    ap.add_argument("--wait-round", action="store_true",
                    help="没卡面时不刷屏、不误点，静默等下一局开局再自动接管")
    a = ap.parse_args()
    a.seconds = max(5, min(a.seconds, 900))
    os.makedirs(SESS, exist_ok=True)
    ap_ = AutoPlay(a)
    if a.probe_map:
        return ap_.probe_map()
    return ap_.run()


if __name__ == "__main__":
    sys.exit(main())
