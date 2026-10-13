# -*- coding: utf-8 -*-
"""诊断：最近若干帧里 cmd 163/166/167 的局号与卡面提取情况，与 cmd 169 的局号对比。"""
import json
import os
import sys

sys.path.insert(0, r"D:\BingoVoyageProbe")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from bv_autoplay import parse_frame, extract_cards, rid_of  # noqa

WSJ = r"D:\BingoVoyageProbe\out\bv_ws.jsonl"
BODIES = r"D:\BingoVoyageProbe\out\bv_bodies"

lines = open(WSJ, encoding="utf-8").read().splitlines()[-8000:]
print("扫描帧数 %d" % len(lines))
seen = {}
for ln in lines:
    if not ln.strip():
        continue
    r = json.loads(ln)
    cmd = r.get("hdr", {}).get("cmd")
    if cmd not in (163, 166, 167, 169):
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
    body = fr["body"]
    rid = rid_of(body)
    ncards = 0
    if cmd in (163, 166, 167):
        try:
            ncards = len(extract_cards(body) or [])
        except Exception:
            ncards = -1
    key = (r["dir"], cmd)
    d = seen.setdefault(key, {"n": 0, "rid": None, "rids": set(), "cards": []})
    d["n"] += 1
    if rid:
        d["rids"].add(rid[-24:])
    if ncards:
        d["cards"].append(ncards)

for (dr, cmd), d in sorted(seen.items(), key=lambda x: (x[0][1], x[0][0])):
    print("%-5s cmd %-4d 帧%-5d 局号%-3d %s  提取到卡面的帧=%d %s"
          % (dr, cmd, d["n"], len(d["rids"]),
             sorted(d["rids"])[-3:], len(d["cards"]), d["cards"][-6:]))
