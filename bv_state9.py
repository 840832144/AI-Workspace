# -*- coding: utf-8 -*-
"""解 cmd 167 subtype9 状态串：97 token = 4 卡 × 24 格（跳过 FREE）。

用法：python bv_state9.py [起始时间 HH:MM:SS] [结束 HH:MM:SS]
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WSJ = r"D:\BingoVoyageProbe\out\bv_ws.jsonl"
BODIES = r"D:\BingoVoyageProbe\out\bv_bodies"


def rv(bb, i):
    r = s = 0
    while True:
        x = bb[i]
        i += 1
        r |= (x & 0x7F) << s
        s += 7
        if not x & 0x80:
            return r, i


def body_of(b):
    ln, i = rv(b, 9)
    i += ln
    return b[i:]


t_lo = sys.argv[1] if len(sys.argv) > 1 else "00:00:00"
t_hi = sys.argv[2] if len(sys.argv) > 2 else "99:99:99"

hits = []
for ln in open(WSJ, encoding="utf-8"):
    ln = ln.strip()
    if not ln:
        continue
    r = json.loads(ln)
    if r.get("hdr", {}).get("cmd") != 167:
        continue
    hh = r.get("ts", "")[-8:]
    if not (t_lo <= hh <= t_hi):
        continue
    p = os.path.join(BODIES, r.get("file", ""))
    if not os.path.exists(p):
        continue
    bd = body_of(open(p, "rb").read())
    # subtype9 的形状：f2{ f1:9, f2:<状态串> }  —— 串里一定带 '|' 和 '@'
    if b"|" not in bd or b"@" not in bd:
        continue
    i = bd.find(b"|")
    while i >= 0 and bd[i - 1] in b"|:@#Z0123456789":
        i -= 1
    j = bd.find(b"@Z", i)
    tok = bd[i:j + 2] if j >= 0 else bd[i:]
    hits.append((r["ts"], r["dir"], tok))

print("时间窗 %s ~ %s，subtype9 帧 %d 条\n" % (t_lo, t_hi, len(hits)))
for ts, d, tok in hits[-6:]:
    s = tok.decode("ascii", "replace")
    parts = s.split("|")
    print("=== %s %s  %d token ===" % (ts, d, len(parts)))
    # 每 24 个 token 一张卡；非空 token 就是「有状态」的格
    for c in range(4):
        seg = parts[c * 24:(c + 1) * 24]
        if not seg or all(seg[i] == "" for i in range(len(seg))):
            continue
        marks = [(k, seg[k]) for k in range(len(seg)) if seg[k] != ""]
        print("   卡%d: 非空 %d 个 -> %s" % (c + 1, len(marks), marks))
    print()
