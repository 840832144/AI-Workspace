# -*- coding: utf-8 -*-
"""递归 dump 一帧 cmd 167，并把每个 bytes 字段同时按 hex / ascii / 整数数组看。"""
import json
import os
import sys

sys.path.insert(0, r"D:\BingoVoyageProbe")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from bv_autoplay import parse_frame, parse  # noqa

WSJ = r"D:\BingoVoyageProbe\out\bv_ws.jsonl"
BODIES = r"D:\BingoVoyageProbe\out\bv_bodies"


def show(b, ind, tag):
    pad = "  " * ind
    if isinstance(b, str):
        b = b.encode("utf-8", "replace")
    print("%s%s bytes[%d] hex=%s" % (pad, tag, len(b), b[:48].hex()))
    try:
        t = b.decode("utf-8")
        if all(32 <= ord(c) < 127 or c in "|@.,:-_" for c in t):
            print("%s    ascii: %s" % (pad, t[:160]))
    except Exception:
        pass
    print("%s    ints : %s" % (pad, list(b[:32])))


def rec(b, ind=1, depth=0):
    if depth > 4:
        return
    pad = "  " * ind
    try:
        fields = list(parse(b))
    except Exception as e:
        print("%s[子消息解析失败 %s]" % (pad, e))
        return
    for fld, wt, val, ch in fields:
        if wt == 2 and ch is not None:
            print("%sf%d <submsg %d>" % (pad, fld, len(ch)))
            rec(ch, ind + 1, depth + 1)
        elif wt == 2:
            show(val or b"", ind, "f%d" % fld)
        else:
            print("%sf%d = %s (wt=%d)" % (pad, fld, val, wt))


rows = []
for ln in open(WSJ, encoding="utf-8"):
    ln = ln.strip()
    if not ln:
        continue
    r = json.loads(ln)
    if r.get("hdr", {}).get("cmd") == 167 and r.get("dir") == "C->S":
        rows.append(r)

shown = 0
for r in reversed(rows):
    p = os.path.join(BODIES, r.get("file", ""))
    if not os.path.exists(p):
        continue
    try:
        fr = parse_frame(open(p, "rb").read())
    except Exception:
        continue
    if not fr.get("ok") or len(fr["body"]) < 10:
        continue
    body = fr["body"]
    # 找 subtype
    sub = None
    try:
        for fld, wt, val, ch in parse(body):
            if wt == 2 and ch is not None:
                inner = list(parse(ch))
                if inner and inner[0][1] == 0:
                    sub = inner[0][2]
    except Exception:
        pass
    if sub not in (1, 3, 4):
        continue
    print("===== %s subtype=%s len=%d =====" % (r["ts"], sub, len(body)))
    rec(body)
    print()
    shown += 1
    if shown >= 4:
        break

# 顺带找 subtype9
print("\n===== 全量搜 subtype9 =====")
n9 = 0
for r in rows:
    p = os.path.join(BODIES, r.get("file", ""))
    if not os.path.exists(p):
        continue
    try:
        fr = parse_frame(open(p, "rb").read())
        if not fr.get("ok"):
            continue
        for fld, wt, val, ch in parse(fr["body"]):
            if wt == 2 and ch is not None:
                inner = list(parse(ch))
                if inner and inner[0][1] == 0 and inner[0][2] == 9:
                    n9 += 1
                    print("  subtype9 @ %s len=%d" % (r["ts"], len(fr["body"])))
                    if n9 <= 2:
                        rec(fr["body"])
    except Exception:
        continue
print("subtype9 共 %d 帧" % n9)
