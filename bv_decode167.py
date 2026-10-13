# -*- coding: utf-8 -*-
"""用「我点了哪一格」与「客户端回了什么 cmd167」做对照，解出 daub 上报的编码。

思路：sessions/*/actions.jsonl 记录了每次点击的 (球号, 卡下标, 行, 列, 坐标, 时间)；
bv_ws.jsonl 记录了客户端发出的 cmd167。把两者按时间对齐，就能看出
cmd167 的 {1: N, 2: M} 到底对应什么。
"""
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np

ROOT = r"D:\BingoVoyageProbe"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "collector"))
from bv_ws2 import parse_frame          # noqa: E402
from bv_proto import parse, try_str     # noqa: E402

BODIES = os.path.join(ROOT, "out", "bv_bodies")


def ts2s(t):
    import datetime
    return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timestamp()


# 1) 取所有 cmd167 C->S subtype1
reports = []
for line in open(os.path.join(ROOT, "out", "bv_ws.jsonl"), encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    if r["dir"] != "C->S":
        continue
    p = os.path.join(BODIES, r.get("file", ""))
    if not os.path.exists(p):
        continue
    fr = parse_frame(open(p, "rb").read())
    if not fr.get("ok") or fr["cmd"] != 167:
        continue
    body = fr["body"]
    sub, detail = None, None
    for fld, wt, val, ch in parse(body):
        if fld == 2 and wt == 2 and ch is not None:
            for f2, w2, v2, c2 in parse(ch):
                if f2 == 1 and w2 == 0:
                    sub = v2
                elif f2 == 3 and w2 == 2 and c2 is not None:
                    d = {}
                    for f3, w3, v3, c3 in parse(c2):
                        if f3 is not None and w3 == 0:
                            d[f3] = v3
                    detail = d
    if sub == 1:
        reports.append((r["ts"], detail))
print("cmd167 subtype1 上报共 %d 条" % len(reports))
print("字段取值分布:")
c1 = Counter(d.get(1) for _, d in reports)
c2 = Counter(d.get(2) for _, d in reports)
print("  field1:", dict(sorted(c1.items(), key=lambda kv: (kv[0] is None, kv[0]))))
print("  field2:", dict(sorted(c2.items(), key=lambda kv: (kv[0] is None, kv[0]))))
print()

# 2) 取我的点击动作
acts = []
for d in sorted(os.listdir(os.path.join(ROOT, "sessions"))):
    p = os.path.join(ROOT, "sessions", d, "actions.jsonl")
    if not os.path.exists(p):
        continue
    for line in open(p, encoding="utf-8"):
        try:
            a = json.loads(line)
        except Exception:
            continue
        if a.get("kind") == "daub" and not a.get("dry"):
            acts.append(a)
print("自动玩点击记录 %d 条" % len(acts))
if not acts:
    print("（没有可对照的点击记录）")
    sys.exit(0)

# 3) 对齐：点击后 3 秒内的 cmd167
print()
print("=== 点击 -> cmd167 对照（点击后 3 秒内）===")
hit = 0
pairs = []
for a in acts:
    t0 = ts2s(a["ts"])
    for ts, det in reports:
        dt = ts2s(ts) - t0
        if 0 <= dt <= 3:
            pairs.append((a, ts, dt, det))
            hit += 1
            break
print("命中 %d / %d 次点击后收到了 cmd167" % (hit, len(acts)))
print()
print("  %-19s %-6s %-10s %-16s %s" % ("点击时间", "球", "点击(卡,r,c)", "坐标", "紧随的 cmd167"))
for a, ts, dt, det in pairs[:25]:
    print("  %-19s %-6s 卡%s r%dc%d   (%s,%s)  dt=%.1fs  %s"
          % (a["ts"], a.get("ball"), a.get("card"), a.get("r", 0) + 1, a.get("c", 0) + 1,
             a.get("x"), a.get("y"), dt, det))
