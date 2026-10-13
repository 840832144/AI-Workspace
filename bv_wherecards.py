# -*- coding: utf-8 -*-
"""查「进局后卡面从哪来」：把最近 N 分钟的帧按 cmd 分组，
并对每个 S->C 帧试一次卡面提取，看有没有哪条其实带着卡面但没被识别。"""
import json
import os
import sys
from collections import Counter, OrderedDict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"D:\BingoVoyageProbe"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "collector"))
from bv_ws2 import parse_frame                                  # noqa: E402
from bv_extract import extract_cards, harvest_strings, all_varints, _band_ok  # noqa: E402
from bv_proto import parse, try_str                             # noqa: E402

BODIES = os.path.join(ROOT, "out", "bv_bodies")
WS = os.path.join(ROOT, "out", "bv_ws.jsonl")
SINCE = sys.argv[1] if len(sys.argv) > 1 else "2026-10-13 11:15:00"

recs = []
for line in open(WS, encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    if r["ts"] >= SINCE:
        recs.append(r)
print("自 %s 起共 %d 帧" % (SINCE, len(recs)))

by = OrderedDict()
for r in recs:
    p = os.path.join(BODIES, r.get("file", ""))
    if not os.path.exists(p):
        continue
    fr = parse_frame(open(p, "rb").read())
    if not fr.get("ok"):
        continue
    k = (fr["cmd"], r["dir"])
    by.setdefault(k, {"n": 0, "max": 0, "ts": [], "cards": 0})
    by[k]["n"] += 1
    by[k]["max"] = max(by[k]["max"], len(fr["body"]))
    if len(by[k]["ts"]) < 3:
        by[k]["ts"].append(r["ts"][11:])
    if r["dir"] == "S->C" and fr["cmd"] not in (169,):
        try:
            if extract_cards(fr["body"]):
                by[k]["cards"] += 1
        except Exception:
            pass

print()
print("%-6s %-5s %6s %8s %-26s %s" % ("cmd", "dir", "帧数", "最大B", "首现", "带卡面帧数"))
for (cmd, d), v in sorted(by.items(), key=lambda kv: (kv[0][0], kv[0][1])):
    print("%-6d %-5s %6d %8d %-26s %s" % (cmd, d, v["n"], v["max"],
                                          ",".join(v["ts"]), v["cards"] or ""))

# 特别看：有没有任何 S->C 帧里出现了「25 个数字且列区间成立」的片段（哪怕提取器没归组）
print()
print("=== 深度扫描：所有 S->C 帧里是否存在满足列区间签名的 25 连串 ===")
hit = 0
for r in recs:
    if r["dir"] != "S->C":
        continue
    p = os.path.join(BODIES, r.get("file", ""))
    if not os.path.exists(p):
        continue
    fr = parse_frame(open(p, "rb").read())
    if not fr.get("ok") or len(fr["body"]) < 60:
        continue
    vs = all_varints(fr["body"])
    for i in range(max(0, len(vs) - 24)):
        if _band_ok(vs[i:i + 25]):
            print("  %s cmd=%d %dB offset=%d  %s" % (
                r["ts"], fr["cmd"], len(fr["body"]), i, vs[i:i + 25]))
            hit += 1
            break
print("  命中 %d 帧" % hit)
