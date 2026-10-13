"""专门拆 cmd 167（round action，含 daub 状态串）与 cmd 179（房间/特性列表）。"""
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
import bv_ws2
from bv_proto import parse, try_str, render  # noqa


def hexdump(b, n=96):
    for i in range(0, min(len(b), n), 16):
        c = b[i:i + 16]
        print("    %04x  %-47s  %s" % (
            i, " ".join("%02x" % x for x in c),
            "".join(chr(x) if 32 <= x < 127 else "." for x in c)))


def main():
    want = int(sys.argv[1]) if len(sys.argv) > 1 else 167
    recs = bv_ws2.load()
    seen = Counter()
    for r in recs:
        f = r["f"]
        if not f.get("ok") or f["cmd"] != want:
            continue
        seen[r["dir"]] += 1
        print("=" * 96)
        print("%s %s cmd=%d topic=%s  %dB" % (
            r["ts"], r["dir"], f["cmd"], f["topic"][:44], len(f["body"])))
        if f["body"]:
            hexdump(f["body"], 112)
            print("    --- 解 ---")
            print("\n".join("    " + x for x in render(f["body"])[:24]))
    print("\n方向统计:", dict(seen))


if __name__ == "__main__":
    main()
