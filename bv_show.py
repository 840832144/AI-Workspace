"""解析 bv_flows.jsonl 里某个 host/path 的 protobuf 请求与响应。"""
import base64
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
from bv_proto import render, try_str  # noqa

JSONL = r"D:\BingoVoyageProbe\out\bv_flows.jsonl"


def load():
    return [json.loads(l) for l in open(JSONL, encoding="utf-8") if l.strip()]


def show(rec, maxlen=6000):
    print("=" * 90)
    print("%s  %s %s -> %s" % (rec["ts"], rec["method"], rec["url"][:120], rec["status"]))
    print("REQ headers: %s" % {k: v for k, v in rec["req_headers"].items()})
    rq = base64.b64decode(rec["req"]["b64"]) if rec["req"].get("b64") else b""
    rs = base64.b64decode(rec["resp"]["b64"]) if rec["resp"].get("b64") else b""
    if rq:
        print("\n--- REQ (%d B) hex: %s" % (len(rq), rq.hex()))
        print("\n".join(render(rq))[:maxlen])
    if rs:
        print("\n--- RESP (%d B) ---" % len(rs))
        print("\n".join(render(rs))[:maxlen])


if __name__ == "__main__":
    want = sys.argv[1] if len(sys.argv) > 1 else "bingo2.superbgame.net"
    only_post = "--post" in sys.argv
    mods = [a for a in sys.argv[1:] if not a.startswith("--")]
    want = mods[0] if mods else "bingo2.superbgame.net"
    n = 0
    for r in load():
        if want not in r["host"]:
            continue
        if only_post and r["method"] != "POST":
            continue
        if r["req"]["len"] == 0 and r["resp"]["len"] == 0:
            continue
        n += 1
        show(r)
    print("\n>>> 匹配 %d 条" % n)
