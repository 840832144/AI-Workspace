"""按 cmd 汇总 WS 帧里出现的所有字符串与数值（去重、计数），快速读出字段语义。"""
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
import bv_ws2  # noqa

PRINTABLE = re.compile(rb"[\x20-\x7e]{4,}")


def scan(recs, want_cmd=None):
    per_cmd = {}
    for r in recs:
        f = r["f"]
        if not f.get("ok"):
            continue
        if want_cmd is not None and f["cmd"] != want_cmd:
            continue
        d = per_cmd.setdefault(f["cmd"], {
            "n": 0, "pkts": Counter(), "topics": Counter(),
            "strs": Counter(), "blobs": [], "sizes": []})
        d["n"] += 1
        d["pkts"][f["pkt"] & 0xFF] += 1
        d["topics"][f["topic"]] += 1
        d["sizes"].append(len(f["body"]))
        for m in PRINTABLE.findall(f["body"]):
            d["strs"][m.decode("ascii")] += 1
        if len(d["blobs"]) < 6:
            d["blobs"].append(f["body"])
    return per_cmd


def show(per_cmd):
    for cmd in sorted(per_cmd):
        d = per_cmd[cmd]
        print("=" * 96)
        print("cmd=%d  n=%d  pkt=%s  body=%d..%d" % (
            cmd, d["n"], dict(d["pkts"]), min(d["sizes"]), max(d["sizes"])))
        t = [x for x in d["topics"] if x]
        if t:
            for x, c in d["topics"].most_common(4):
                if x:
                    print("  topic(%d): %s" % (c, x))
        if d["strs"]:
            print("  --- 字符串 ---")
            for s, c in d["strs"].most_common(30):
                print("    x%-4d %s" % (c, s[:110]))
        print("  --- 样本 hex（第一个 body 前 160B）---")
        if d["blobs"]:
            b = d["blobs"][0][:160]
            for i in range(0, len(b), 16):
                c = b[i:i + 16]
                print("    %04x  %-47s  %s" % (
                    i, " ".join("%02x" % x for x in c),
                    "".join(chr(x) if 32 <= x < 127 else "." for x in c)))


if __name__ == "__main__":
    recs = bv_ws2.load()
    want = int(sys.argv[1]) if len(sys.argv) > 1 else None
    show(scan(recs, want))
