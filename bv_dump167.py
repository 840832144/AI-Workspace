# -*- coding: utf-8 -*-
"""dump cmd 167 的原始结构，重点找 subtype9 状态串（疑似 daub 位图）。

用法：python bv_dump167.py [秒数窗口，默认最近 N 帧]
"""
import json
import os
import sys

sys.path.insert(0, r"D:\BingoVoyageProbe")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from bv_autoplay import parse_frame, parse  # noqa

WSJ = r"D:\BingoVoyageProbe\out\bv_ws.jsonl"
BODIES = r"D:\BingoVoyageProbe\out\bv_bodies"
TAIL = int(sys.argv[1]) if len(sys.argv) > 1 else 20000

rows = []
for ln in open(WSJ, encoding="utf-8"):
    ln = ln.strip()
    if not ln:
        continue
    r = json.loads(ln)
    if r.get("hdr", {}).get("cmd") != 167:
        continue
    rows.append(r)
rows = rows[-25:]

print("最后 %d 帧 cmd 167 的结构：\n" % len(rows))
for r in rows:
    p = os.path.join(BODIES, r.get("file", ""))
    if not os.path.exists(p):
        continue
    try:
        fr = parse_frame(open(p, "rb").read())
    except Exception as e:
        print("  [解析失败] %s" % e)
        continue
    if not fr.get("ok"):
        continue
    print("=== %s %s len=%d ===" % (r["ts"], r["dir"], len(fr["body"])))
    try:
        for fld, wt, val, ch in parse(fr["body"]):
            if wt == 2 and ch is not None:
                inner = list(parse(ch))
                sub = None
                if inner and inner[0][1] == 0:
                    sub = inner[0][2]
                print("  f%d submsg len=%d subtype=%s fields=%s"
                      % (fld, len(ch), sub,
                         [(i[0], i[1], i[2] if i[1] == 0 else "<sub>") for i in inner[:6]]))
                for i in inner:
                    if i[1] == 2 and i[3] is not None:
                        for j in parse(i[3]):
                            if j[1] == 2 and j[3] is not None:
                                s = j[3]
                                try:
                                    txt = s.decode("utf-8", "replace")
                                except Exception:
                                    txt = repr(s)
                                if "|" in txt or "@" in txt or len(txt) > 40:
                                    print("    >>> f%d.%d 字符串 %d 字节:" % (fld, j[0], len(s)))
                                    print("        %s" % txt[:400])
            elif wt == 0:
                print("  f%d varint %d" % (fld, val))
            elif wt == 2 and ch is None:
                print("  f%d bytes len=%d" % (fld, len(val) if val else 0))
    except Exception as e:
        print("  [字段遍历失败] %s" % e)
    print()
