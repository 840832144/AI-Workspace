"""把客户端发出的 WS 帧（C->S）与 HTTP POST 全部编目：cmd / topic / body 结构与唯一模式。

用途：定位「买卡 / daub 上报 / bingo 宣告 / 结算领取」这几个动作对应的命令。
"""
import base64
import json
import os
import sys
from collections import Counter, OrderedDict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
import bv_ws2
from bv_proto import parse, try_str, render  # noqa

OUT = r"D:\BingoVoyageProbe\out"


def body_sig(b, maxd=3):
    """把 protobuf body 压成可比较的结构签名 + 可读摘要"""
    parts = []
    for fld, wt, val, chunk in parse(b):
        if fld is None:
            parts.append("ERR")
            continue
        if wt == 0:
            parts.append("%d:i=%s" % (fld, val))
        elif wt == 2:
            s = try_str(chunk) if chunk is not None else None
            if s is not None:
                parts.append("%d:s" % fld)
            else:
                sub = None
                if isinstance(val, int) and val > 1 and chunk:
                    try:
                        sub = parse(chunk)
                    except Exception:
                        sub = None
                if sub and maxd > 0:
                    inner = []
                    for f2, w2, v2, c2 in sub:
                        if f2 is None:
                            inner.append("?")
                        elif w2 == 0:
                            inner.append("%d:i=%s" % (f2, v2))
                        else:
                            s2 = try_str(c2) if c2 is not None else None
                            inner.append("%d:%s" % (f2, "s" if s2 is not None else "b"))
                    parts.append("%d:{m %s}" % (fld, ",".join(inner[:8])))
                else:
                    parts.append("%d:b=%s" % (fld, (chunk.hex() if chunk else "?")))
        elif wt == 5:
            parts.append("%d:f32" % fld)
        elif wt == 1:
            parts.append("%d:f64" % fld)
    return " | ".join(parts)


def cmd_cs():
    recs = bv_ws2.load()
    groups = OrderedDict()
    for r in recs:
        f = r["f"]
        if not f.get("ok") or r["dir"] != "C->S":
            continue
        key = f["cmd"]
        g = groups.setdefault(key, {"n": 0, "topics": Counter(), "sigs": Counter(),
                                    "samples": []})
        g["n"] += 1
        g["topics"][f["topic"]] += 1
        g["sigs"][body_sig(f["body"])] += 1
        if len(g["samples"]) < 3:
            g["samples"].append((r["ts"], f["topic"], f["body"]))
    print("### 客户端 -> 服务端（WebSocket）共 %d 条" % sum(g["n"] for g in groups.values()))
    for cmd in sorted(groups):
        g = groups[cmd]
        print("\n" + "=" * 96)
        print("cmd=%-5d  n=%-4d  topic=%s" % (
            cmd, g["n"], ",".join(t[:40] for t, _ in g["topics"].most_common(2)) or "(无)"))
        for sig, c in g["sigs"].most_common(6):
            print("   x%-4d %s" % (c, sig[:200]))
        ts, tp, b = g["samples"][0]
        print("   样例 %s  %dB  hex=%s" % (ts, len(b), b[:72].hex()))
        if b:
            print("\n".join("     " + x for x in render(b)[:14]))


def http_catalog():
    p = os.path.join(OUT, "bv_flows.jsonl")
    if not os.path.exists(p):
        return
    recs = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    inter = [r for r in recs if r["method"] == "POST" and r["req"]["len"] > 0
             and "superbgame" in r["host"] and "cdn" not in r["host"]]
    print("\n\n### 客户端 -> 服务端（HTTP POST，bingo2 主 API）共 %d 条" % len(inter))
    sigs = Counter()
    for r in recs:
        if r["method"] != "POST" or not r["req"].get("b64"):
            continue
        if not ("superbgame" in r["host"] and "cdn" not in r["host"]):
            continue
        b = base64.b64decode(r["req"]["b64"])
        if len(b) < 10:
            continue
        cmd = b[8]
        sigs[(cmd, body_sig(b[10:]))] += 1
    for (cmd, sig), c in sorted(sigs.items()):
        print("  cmd=%-5d x%-4d %s" % (cmd, c, sig[:180]))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "ws"):
        cmd_cs()
    if what in ("all", "http"):
        http_catalog()
