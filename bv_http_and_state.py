"""1) 列出 HTTP POST 到 bingo2 主 API 的所有 (cmd, body 结构)；
2) 拆解 cmd 167 的 150 字符棋盘状态串，找结构周期。"""
import base64
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
import bv_ws2
from bv_proto import parse, try_str  # noqa

OUT = r"D:\BingoVoyageProbe\out"


def http_catalog():
    p = os.path.join(OUT, "bv_flows.jsonl")
    recs = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    print("=== HTTP: 发往 bingo2 主 API 的 POST ===")
    sig = Counter()
    for r in recs:
        if r["method"] != "POST" or not r["req"].get("b64"):
            continue
        if "superbgame" not in r["host"] or "cdn" in r["host"]:
            continue
        b = base64.b64decode(r["req"]["b64"])
        if len(b) < 10:
            continue
        hdr = "pkt=%d seq=%d flags=0x%04x cmd=%d" % (
            int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:6], "little"),
            int.from_bytes(b[6:8], "little"), b[8])
        sig[(hdr, len(b), r["status"], r["resp"]["len"])] += 1
    for k, n in sorted(sig.items(), key=lambda kv: -kv[1]):
        print("  x%-4d %s req=%dB -> %s resp=%dB" % (n, k[0], k[1], k[2], k[3]))
    print()
    print("=== HTTP: 发往 bingo2 主 API 的 GET ===")
    got = Counter()
    for r in recs:
        if r["method"] == "GET" and "bingo2.superbgame.net" in r["host"]:
            got[(r["path"].split("?")[0], r["status"], r["resp"]["len"])] += 1
    for k, n in sorted(got.items(), key=lambda kv: -kv[1]):
        print("  x%-4d %s -> %s (%dB)" % (n, k[0], k[1], k[2]))


def state_string():
    print("\n\n=== cmd 167 的棋盘状态串拆解 ===")
    recs = bv_ws2.load()
    seen = []
    for r in recs:
        f = r["f"]
        if not f.get("ok") or f["cmd"] != 167 or r["dir"] != "C->S":
            continue
        for fld, wt, val, ch in parse(f["body"]):
            if fld == 2 and wt == 2 and isinstance(val, int) and ch:
                for f2, w2, v2, c2 in parse(ch):
                    if f2 == 2 and w2 == 2 and c2 is not None:
                        s = try_str(c2)
                        if s and "|" in s:
                            seen.append((r["ts"], s))
    print("找到 %d 条状态串" % len(seen))
    for ts, s in seen[:4]:
        print("\n%s  len=%d" % (ts, len(s)))
        toks = s.split("|")
        print("  split('|') -> %d 个 token" % len(toks))
        for i, t in enumerate(toks):
            if t:
                print("    [%2d] %r" % (i, t))
        print("  尾部 20 字符: %r" % s[-20:])


if __name__ == "__main__":
    http_catalog()
    state_string()
