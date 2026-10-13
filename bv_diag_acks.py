# -*- coding: utf-8 -*-
"""统计 C->S cmd 167 的各 subtype 数量与时序，核对「一次 daub 一条回执」是否成立。
用法：python bv_diag_acks.py [起始时间 HH:MM:SS] [结束时间 HH:MM:SS]
"""
import json
import os
import sys

sys.path.insert(0, r"D:\BingoVoyageProbe")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from bv_autoplay import parse_frame  # noqa

WSJ = r"D:\BingoVoyageProbe\out\bv_ws.jsonl"
BODIES = r"D:\BingoVoyageProbe\out\bv_bodies"

t_lo = sys.argv[1] if len(sys.argv) > 1 else "00:00:00"
t_hi = sys.argv[2] if len(sys.argv) > 2 else "99:99:99"

rows = []
for ln in open(WSJ, encoding="utf-8"):
    ln = ln.strip()
    if not ln:
        continue
    r = json.loads(ln)
    ts = r.get("ts", "")
    hh = ts[-8:]
    if not (t_lo <= hh <= t_hi):
        continue
    if r.get("hdr", {}).get("cmd") != 167:
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
    sub = None
    toks = 0
    for fld, wt, val, ch in parse_all(fr["body"]) if False else []:
        pass
    try:
        from bv_autoplay import parse
        for fld, wt, val, ch in parse(fr["body"]):
            if fld != 2 or wt != 2 or ch is None:
                continue
            inner = list(parse(ch))
            if inner and inner[0][1] == 0:
                sub = inner[0][2]
            # 数一数这个子消息里有多少个标量 token
            n = 0
            for f1, w1, v1, c1 in inner:
                if w1 == 2 and c1 is not None:
                    n += sum(1 for _ in parse(c1))
                elif w1 == 0:
                    n += 1
            if n > toks:
                toks = n
            break
    except Exception:
        pass
    rows.append((ts, r["dir"], sub, toks, fr["cmd"]))

print("时间窗 %s ~ %s，cmd 167 帧数 %d" % (t_lo, t_hi, len(rows)))
from collections import Counter
c = Counter((d, s) for _, d, s, _, _ in rows)
for (d, s), n in sorted(c.items(), key=lambda x: -x[1]):
    print("  %-5s subtype %-5s  %d 帧" % (d, s, n))
print()
print("C->S subtype 1（daub 回执）时间线：")
ones = [ts for ts, d, s, _, _ in rows if d == "C->S" and s == 1]
print("  共 %d 条" % len(ones))
for t in ones[:40]:
    print("   ", t)
tok9 = [t for t, d, s, n, _ in rows if d == "C->S" and s == 9]
print()
print("C->S subtype 9（状态串）共 %d 条，token 抽样：%s"
      % (len(tok9), sorted({n for _, d, s, n, _ in rows if d == "C->S" and s == 9})))
