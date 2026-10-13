# -*- coding: utf-8 -*-
"""查 cmd 169 报号帧的完整性：把某局所有 169 帧按时间列出，看「最新号」是否连续。

169 的 field2 是「最近 5 个号」的滑动窗口，最右为最新。
如果两帧之间最新号跳了 >1，说明中间有帧没抓到（丢帧）。
用法：python bv_gap169.py [局号关键词]
"""
import json
import os
import sys

sys.path.insert(0, r"D:\BingoVoyageProbe")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from bv_autoplay import parse_frame, rid_of, parse  # noqa

WSJ = r"D:\BingoVoyageProbe\out\bv_ws.jsonl"
BODIES = r"D:\BingoVoyageProbe\out\bv_bodies"
KEY = sys.argv[1] if len(sys.argv) > 1 else "5V93HJcSwVsOXa.97"

rows = []
for ln in open(WSJ, encoding="utf-8"):
    ln = ln.strip()
    if not ln:
        continue
    r = json.loads(ln)
    if r.get("dir") != "S->C" or r.get("hdr", {}).get("cmd") != 169:
        continue
    p = os.path.join(BODIES, r.get("file", ""))
    if not os.path.exists(p):
        continue
    try:
        fr = parse_frame(open(p, "rb").read())
    except Exception:
        continue
    if not fr.get("ok"):
        continue
    rid = rid_of(fr["body"]) or ""
    if KEY not in rid:
        continue
    win = []
    for fld, wt, val, ch in parse(fr["body"]):
        if fld == 2 and wt == 2 and ch is not None:
            win = list(ch)
            break
    rows.append((r["ts"], win))

print("局号含 %r 的 169 帧: %d 条" % (KEY, len(rows)))
if not rows:
    sys.exit(0)

uniq, order = set(), []
for ts, win in rows:
    for b in win:
        if b not in uniq:
            uniq.add(b)
            order.append(b)
print("窗口并集 = %d 个号" % len(order))
print("并集序列: %s" % order)

print("\n按时间的滑动窗口（最新号在最后）：")
prev = None
gaps = 0
for i, (ts, win) in enumerate(rows):
    newest = win[-1] if win else None
    mark = ""
    if prev is None:
        mark = "  <- 首帧"
    else:
        # 上一个窗口 vs 本窗口：找新增了几个
        added = [b for b in win if b not in prev]
        if len(added) > 1:
            mark = "  <- 一次新增 %d 个，中间可能丢帧" % len(added)
            gaps += 1
    if i < 12 or i > len(rows) - 6 or mark:
        print("  %s  win=%s  最新=%s%s" % (ts, win, newest, mark))
    prev = win
print("\n疑似丢帧处: %d 处" % gaps)
