"""探测 bingo2.superbgame.net 的帧结构：打印请求/响应前 N 字节，并按候选头长解析。"""
import base64
import json
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
from bv_proto import render  # noqa

JSONL = r"D:\BingoVoyageProbe\out\bv_flows.jsonl"
recs = [json.loads(l) for l in open(JSONL, encoding="utf-8") if l.strip()]


def hexdump(b, n=96):
    out = []
    for i in range(0, min(len(b), n), 16):
        chunk = b[i:i + 16]
        hx = " ".join("%02x" % c for c in chunk)
        asc = "".join(chr(c) if 32 <= c < 127 else "." for c in chunk)
        out.append("%04x  %-47s  %s" % (i, hx, asc))
    return "\n".join(out)


for r in recs:
    if "bingo2.superbgame.net" not in r["host"] or r["method"] != "POST":
        continue
    rq = base64.b64decode(r["req"]["b64"]) if r["req"].get("b64") else b""
    rs = base64.b64decode(r["resp"]["b64"]) if r["resp"].get("b64") else b""
    print("=" * 90)
    print("%s  req=%dB resp=%dB" % (r["ts"], len(rq), len(rs)))
    print("\n--- REQ 前 64B ---")
    print(hexdump(rq, 64))
    print("\n--- RESP 前 32B ---")
    print(hexdump(rs, 32))
    # 候选头长
    for hlen in (8, 10, 12, 16):
        if len(rs) <= hlen:
            continue
        u32a, u32b = struct.unpack_from("<II", rs, 0)
        c16 = struct.unpack_from("<H", rs, 8)[0] if len(rs) >= 10 else None
        print("\n>>> 假设头长=%d  head=%s  u32a=%d u32b=%d cmd16=%s  payload=%dB" % (
            hlen, rs[:hlen].hex(), u32a, u32b, c16, len(rs) - hlen))
        if hlen == 10:
            body = rs[hlen:]
            lines = render(body)
            print("\n".join(lines[:60]))
            print("...(共 %d 行)" % len(lines))
            break
