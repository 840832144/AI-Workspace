"""解析 bv_ws.jsonl 里的 WebSocket 帧：还原帧头 + 渲染 protobuf。"""
import base64
import json
import os
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
from bv_proto import render  # noqa

OUT = r"D:\BingoVoyageProbe\out"
WS = os.path.join(OUT, "bv_ws.jsonl")
BODIES = os.path.join(OUT, "bv_bodies")


def hexdump(b, n=80):
    out = []
    for i in range(0, min(len(b), n), 16):
        c = b[i:i + 16]
        out.append("%04x  %-47s  %s" % (
            i, " ".join("%02x" % x for x in c),
            "".join(chr(x) if 32 <= x < 127 else "." for x in c)))
    return "\n".join(out)


def load():
    if not os.path.exists(WS):
        return []
    return [json.loads(l) for l in open(WS, encoding="utf-8") if l.strip()]


def body(rec):
    p = os.path.join(BODIES, rec["file"])
    return open(p, "rb").read() if os.path.exists(p) else b""


def cmd_hex(n=12):
    for r in load()[:n]:
        b = body(r)
        print("-" * 80)
        print("%s %s %dB  %s" % (r["ts"], r["dir"], len(b), r["hdr"]))
        print(hexdump(b, 64))
        # 尝试多种帧头切分
        for hl in (8, 10, 12):
            if len(b) <= hl:
                continue
            u = struct.unpack_from("<%dI" % (hl // 4), b, 0)
            print("   head=%dB u32=%s -> payload %dB" % (hl, u, len(b) - hl))


def cmd_show(limit=40, maxline=80):
    recs = load()
    print("共 %d 帧" % len(recs))
    for r in recs[:limit]:
        b = body(r)
        h = r["hdr"]
        print("=" * 88)
        print("%s  %s  %dB   pkt=%s seq=%s cmd=%s" % (
            r["ts"], r["dir"], len(b), h.get("pkt"), h.get("ver"), h.get("cmd")))
        print(hexdump(b, 48))
        if len(b) > 10:
            lines = render(b[10:])
            print("\n".join(lines[:maxline]))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "hex"
    if cmd == "hex":
        cmd_hex(int(sys.argv[2]) if len(sys.argv) > 2 else 12)
    elif cmd == "show":
        cmd_show(int(sys.argv[2]) if len(sys.argv) > 2 else 40)
