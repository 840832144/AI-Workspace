"""调试：cmd 216(聊天) / cmd 179(房间列表) 的真实结构。"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
import bv_ws2
from bv_proto import parse, try_str, render  # noqa


def hexdump(b, n=96):
    for i in range(0, min(len(b), n), 16):
        c = b[i:i + 16]
        print("  %04x  %-47s  %s" % (
            i, " ".join("%02x" % x for x in c),
            "".join(chr(x) if 32 <= x < 127 else "." for x in c)))


for want in (216, 179):
    print("=" * 96)
    print("### cmd %d" % want)
    n = 0
    dirs = {}
    for r in bv_ws2.load():
        f = r["f"]
        if not f.get("ok") or f["cmd"] != want:
            continue
        dirs[r["dir"]] = dirs.get(r["dir"], 0) + 1
        if n >= 2:
            continue
        n += 1
        print("-" * 88)
        print("%s %s %dB topic=%s" % (r["ts"], r["dir"], len(f["body"]), f["topic"][:40]))
        hexdump(f["body"], 112)
        if f["body"]:
            print("\n".join("  " + x for x in render(f["body"])[:18]))
    print("方向:", dirs)
