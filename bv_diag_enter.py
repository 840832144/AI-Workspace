# -*- coding: utf-8 -*-
"""时间线：cmd 202(进房买卡, C->S) / 163(回合快照, S->C, 带卡面?) / 169(报号) 的先后关系。"""
import json
import os
import sys

sys.path.insert(0, r"D:\BingoVoyageProbe")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from bv_autoplay import parse_frame, extract_cards, rid_of  # noqa

WSJ = r"D:\BingoVoyageProbe\out\bv_ws.jsonl"
BODIES = r"D:\BingoVoyageProbe\out\bv_bodies"

lines = open(WSJ, encoding="utf-8").read().splitlines()[-6000:]
rows = []
for ln in lines:
    if not ln.strip():
        continue
    r = json.loads(ln)
    cmd = r.get("hdr", {}).get("cmd")
    if cmd not in (163, 202):
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
    rid, nc = rid_of(fr["body"]), 0
    if cmd == 163:
        try:
            nc = len(extract_cards(fr["body"]) or [])
        except Exception:
            nc = -1
    rows.append((r["ts"], r["dir"], cmd, (rid or "")[-16:], nc))

print("最近 6000 帧内 cmd 202 / 163 时间线（后 40 条）：")
print("%-20s %-5s %-5s %-18s %s" % ("时间", "方向", "cmd", "局号", "卡面数"))
for t, d, c, rid, nc in rows[-40:]:
    print("%-20s %-5s %-5d %-18s %s" % (t, d, c, rid, ("%d 张" % nc) if c == 163 else "-"))
n163 = [x for x in rows if x[2] == 163]
n202 = [x for x in rows if x[2] == 202]
print()
print("163 共 %d 帧，其中带卡面 %d 帧" % (len(n163), len([x for x in n163 if x[4] > 0])))
print("202 共 %d 帧（方向：%s）" % (len(n202), {x[1] for x in n202}))
