"""Bingo Voyage WebSocket 协议解码器。

帧结构（已用多帧交叉验证）：
    offset 0-3   u32 LE   pkt   2=客户端请求  3=服务端响应  5=服务端推送
    offset 4-5   u16 LE   seq   消息序号（同一连接内递增）
    offset 6-7   u16 LE   flags 路由/标志位
    offset 8     u8       cmd   命令号
    offset 9     varint   len   主题字符串长度
    offset 10..  bytes    topic 路由主题（如 "hall-BINGO_HALL_NOVICE-0-<uid>"）
    其后                  bytes  protobuf 消息体

用法：
    python bv_ws2.py list                # 按 cmd 汇总
    python bv_ws2.py dump [cmd]          # 展开指定 cmd（或全部）
    python bv_ws2.py topics              # 只看 topic 字符串
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
from bv_proto import render  # noqa

OUT = r"D:\BingoVoyageProbe\out"
WS = os.path.join(OUT, "bv_ws.jsonl")
BODIES = os.path.join(OUT, "bv_bodies")

PKT = {2: "REQ", 3: "RESP", 5: "PUSH"}


def read_varint(b, i):
    v = 0
    s = 0
    while i < len(b):
        c = b[i]
        i += 1
        v |= (c & 0x7F) << s
        if not (c & 0x80):
            return v, i
        s += 7
        if s > 63:
            break
    return None, i


def parse_frame(b):
    if len(b) < 10:
        return {"raw": b, "ok": False}
    pkt = int.from_bytes(b[0:4], "little")
    seq = int.from_bytes(b[4:6], "little")
    flags = int.from_bytes(b[6:8], "little")
    cmd = b[8]
    ln, i = read_varint(b, 9)
    topic = b""
    if ln:
        topic = b[i:i + ln]
        i += ln
    body = b[i:]
    return {"ok": True, "pkt": pkt, "seq": seq, "flags": flags, "cmd": cmd,
            "topic": topic.decode("utf-8", "replace"), "body": body,
            "raw": b}


def load():
    if not os.path.exists(WS):
        print("(无 %s)" % WS)
        return []
    out = []
    for line in open(WS, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        p = os.path.join(BODIES, r["file"])
        r["raw"] = open(p, "rb").read() if os.path.exists(p) else b""
        r["f"] = parse_frame(r["raw"])
        out.append(r)
    return out


def cmd_list(recs):
    agg = {}
    for r in recs:
        f = r["f"]
        if not f.get("ok"):
            continue
        k = (f["pkt"], f["cmd"], f["topic"])
        a = agg.setdefault(k, {"n": 0, "dirs": set(), "sizes": []})
        a["n"] += 1
        a["dirs"].add(r["dir"])
        a["sizes"].append(len(f["body"]))
    print("%-6s %-5s %-46s %5s %-14s %s" % ("PKT", "CMD", "TOPIC", "N", "DIR", "body 大小"))
    print("-" * 120)
    for (pkt, cmd, topic), a in sorted(agg.items(), key=lambda kv: (kv[0][1], kv[0][2])):
        print("%-6s %-5d %-46s %5d %-14s %s" % (
            PKT.get(pkt, pkt), cmd, topic[:46], a["n"],
            ",".join(sorted(a["dirs"])),
            "%d..%d" % (min(a["sizes"]), max(a["sizes"]))))
    print("\n共 %d 帧" % len(recs))


def cmd_topics(recs):
    seen = {}
    for r in recs:
        f = r["f"]
        if not f.get("ok"):
            continue
        seen.setdefault(f["topic"], 0)
        seen[f["topic"]] += 1
    for t, n in sorted(seen.items(), key=lambda kv: -kv[1]):
        print("%5d  %s" % (n, t))


def cmd_dump(recs, want=None, maxline=60):
    for r in recs:
        f = r["f"]
        if not f.get("ok"):
            continue
        if want is not None and f["cmd"] != want:
            continue
        print("=" * 92)
        print("%s %s  pkt=%s seq=%d flags=0x%04x cmd=%d topic=%r body=%dB" % (
            r["ts"], r["dir"], PKT.get(f["pkt"], f["pkt"]), f["seq"], f["flags"],
            f["cmd"], f["topic"], len(f["body"])))
        if f["body"]:
            lines = render(f["body"])
            print("\n".join(lines[:maxline]))
            if len(lines) > maxline:
                print("  ...(共 %d 行)" % len(lines))


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else "list"
    recs = load()
    if c == "list":
        cmd_list(recs)
    elif c == "topics":
        cmd_topics(recs)
    elif c == "dump":
        cmd_dump(recs, int(sys.argv[2]) if len(sys.argv) > 2 else None,
                 int(sys.argv[3]) if len(sys.argv) > 3 else 60)
    elif c == "cmds":
        for x in sorted({r["f"]["cmd"] for r in recs if r["f"].get("ok")}):
            print(x)
