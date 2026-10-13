"""通用 protobuf wire-format 解析 + bv_flows.jsonl 汇总。

用法：
    python bv_proto.py flows            # 按 host+path 汇总已抓到的流量
    python bv_proto.py dump <file.bin>  # 解析单个 protobuf 二进制
    python bv_proto.py match            # 把每个 POST body 解析后与 IL2CPP 类名做映射提示
"""
import base64
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe\out"
JSONL = os.path.join(OUT, "bv_flows.jsonl")


def read_varint(b, i):
    v = 0
    s = 0
    while True:
        if i >= len(b):
            raise ValueError("varint EOF")
        c = b[i]
        i += 1
        v |= (c & 0x7F) << s
        if not (c & 0x80):
            return v, i
        s += 7
        if s > 63:
            raise ValueError("varint too long")


def parse(buf, depth=0, maxdepth=8):
    """返回 [(field, wiretype, value_repr, raw)]"""
    out = []
    i = 0
    n = len(buf)
    while i < n:
        try:
            key, i = read_varint(buf, i)
        except ValueError as e:
            out.append((None, None, "PARSE_ERR %s @%d" % (e, i), buf[i:]))
            break
        field, wt = key >> 3, key & 7
        if wt == 0:
            try:
                v, i = read_varint(buf, i)
            except ValueError as e:
                out.append((field, 0, "VARINT_EOF", None))
                break
            out.append((field, 0, v, None))
        elif wt == 1:
            if i + 8 > n:
                out.append((field, 1, "TRUNC", None))
                break
            out.append((field, 1, "<8B fixed64 %s>" % buf[i:i + 8].hex(), buf[i:i + 8]))
            i += 8
        elif wt == 2:
            try:
                ln, i = read_varint(buf, i)
            except ValueError:
                out.append((field, 2, "LEN_VARINT_EOF", None))
                break
            if i + ln > n:
                out.append((field, 2, "LEN_OVERFLOW len=%d remain=%d" % (ln, n - i), None))
                break
            chunk = buf[i:i + ln]
            i += ln
            out.append((field, 2, ln, chunk))  # chunk 供递归
        elif wt == 5:
            if i + 4 > n:
                out.append((field, 5, "TRUNC", None))
                break
            out.append((field, 5, "<4B fixed32 %s>" % buf[i:i + 4].hex(), buf[i:i + 4]))
            i += 4
        else:
            out.append((field, wt, "UNKNOWN_WT", None))
            break
    return out


def try_str(chunk):
    try:
        s = chunk.decode("utf-8")
        if s and all(c.isprintable() or c in "\r\n\t" for c in s):
            return s
    except Exception:
        pass
    return None


def render(buf, depth=0, maxdepth=7, prefix=""):
    lines = []
    for field, wt, val, chunk in parse(buf):
        pad = "  " * depth
        if field is None:
            lines.append("%s%s" % (pad, val))
            continue
        tag = "%s#%d(wt%d)" % (pad, field, wt)
        if wt == 0:
            lines.append("%s = varint %d" % (tag, val))
        elif wt == 1:
            lines.append("%s = %s" % (tag, val))
        elif wt == 5:
            lines.append("%s = %s" % (tag, val))
        elif wt == 2:
            s = try_str(chunk)
            # 判断是否像一个嵌套 message
            nested_ok = False
            if depth < maxdepth and isinstance(val, int) and val > 1:
                try:
                    sub = parse(chunk)
                    if sub and all(f is not None for f, _, _, _ in sub) and len(sub) >= 1:
                        # 排除明显是字符串的情况
                        if s is None or len(sub) > 1:
                            nested_ok = True
                except Exception:
                    nested_ok = False
            if nested_ok:
                lines.append("%s = msg len=%d {" % (tag, val))
                lines.extend(render(chunk, depth + 1, maxdepth))
                lines.append("%s}" % pad)
            elif s is not None:
                lines.append('%s = str(%d) "%s"' % (tag, val, s.replace("\n", "\\n")[:300]))
            elif chunk is None:
                lines.append("%s = %s" % (tag, val))
            else:
                lines.append("%s = bytes(%d) %s" % (tag, val, chunk[:48].hex()))
    return lines


def load_flows():
    if not os.path.exists(JSONL):
        return []
    recs = []
    with open(JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    recs.append(json.loads(line))
                except Exception:
                    pass
    return recs


def cmd_flows():
    recs = load_flows()
    agg = {}
    for r in recs:
        k = (r["host"], r["method"], r["path"].split("?")[0])
        a = agg.setdefault(k, {"n": 0, "codes": {}, "rq": 0, "rs": 0})
        a["n"] += 1
        a["codes"][r["status"]] = a["codes"].get(r["status"], 0) + 1
        a["rq"] = max(a["rq"], r["req"]["len"])
        a["rs"] = max(a["rs"], r["resp"]["len"])
    print("%-42s %-5s %-38s %5s %-12s %8s %8s" % ("HOST", "M", "PATH", "N", "CODES", "maxRQ", "maxRS"))
    print("-" * 130)
    for (h, m, p), a in sorted(agg.items(), key=lambda kv: -kv[1]["n"]):
        print("%-42s %-5s %-38s %5d %-12s %8d %8d" % (
            h[:42], m, p[:38], a["n"],
            ",".join("%s:%d" % kv for kv in sorted(a["codes"].items())), a["rq"], a["rs"]))
    print("\n总计 %d 条 flow" % len(recs))


def cmd_dump(path):
    if path.startswith("b64:"):
        data = base64.b64decode(path[4:])
    else:
        data = open(path, "rb").read()
    print("len=%d" % len(data))
    print("\n".join(render(data)))


def cmd_app():
    """只看游戏本体 API（bingo2.superbgame.net 等）"""
    recs = load_flows()
    games = [r for r in recs if "superbgame" in r["host"] or "elitescastle" in r["host"]
             or "voyage.bingo" in r["host"] or "logan" in r["host"]]
    for r in games:
        print("=" * 100)
        print("%s %s %s -> %s  (req %dB / resp %dB)" % (
            r["ts"], r["method"], r["url"][:150], r["status"], r["req"]["len"], r["resp"]["len"]))
        if r["req"]["len"] and r["req"].get("b64"):
            raw = base64.b64decode(r["req"]["b64"])
            print("--- REQ protobuf ---")
            print("\n".join(render(raw)))
        if r["resp"]["len"] and r["resp"].get("b64"):
            raw = base64.b64decode(r["resp"]["b64"])
            ct = r["resp"]["content_type"]
            if "json" in ct or "text" in ct:
                print("--- RESP text ---")
                print(r["resp"]["text"])
            else:
                print("--- RESP protobuf ---")
                print("\n".join(render(raw)))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "flows"
    if cmd == "flows":
        cmd_flows()
    elif cmd == "dump":
        cmd_dump(sys.argv[2])
    elif cmd == "app":
        cmd_app()
