"""搜「卡面样式的载荷」：任意消息里出现 重复的 {1:n} 子消息、n 大部分落在 1..75、数量>=20。

之前 bv_findcards.py 漏了这种嵌套形态（值是分散在 25 个子消息里的，不是同一 message 的重复 varint）。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
import bv_ws2
from bv_proto import parse, try_str  # noqa


def scan_msgs(b, depth=0, path="", out=None):
    """递归收集所有 message 的 {子字段: [varint]}, 子消息形如 {1:n}"""
    if out is None:
        out = []
    if depth > 6:
        return out
    for fld, wt, val, ch in parse(b):
        if wt != 2 or ch is None:
            continue
        p = "%s.%d" % (path, fld)
        # 这个子消息里 field1 是否为 varint（{1:n} 形态）
        sub = list(parse(ch))
        v1 = [v2 for f2, w2, v2, c2 in sub if f2 == 1 and w2 == 0]
        if v1 and len(sub) <= 3:
            out.append((p, v1[0]))
        scan_msgs(ch, depth + 1, p, out)
    return out


def main():
    recs = bv_ws2.load()
    print("扫描 %d 帧" % len(recs))
    hits = []
    for r in recs:
        f = r["f"]
        if not f.get("ok") or not f["body"]:
            continue
        vals = scan_msgs(f["body"])
        # 同一个父路径下的连续 {1:n}
        groups = {}
        for p, v in vals:
            parent = p.rsplit(".", 1)[0]
            groups.setdefault(parent, []).append(v)
        for parent, vs in groups.items():
            if len(vs) >= 20:
                inrange = sum(1 for v in vs if 1 <= v <= 75)
                if inrange >= len(vs) * 0.8:
                    hits.append((r["ts"], r["dir"], f["cmd"], parent, len(vs), vs[:30]))
    print("\n=== 命中（>=20 个 {1:n}，>=80% 落 1..75）===")
    seen = {}
    for ts, d, cmd, parent, n, vs in hits:
        key = (cmd, parent, n)
        seen.setdefault(key, []).append(ts)
    for (cmd, parent, n), tss in sorted(seen.items(), key=lambda kv: -len(kv[1])):
        print("  cmd=%-4d path=%-16s 组大小=%-3d 出现 %d 次   例: %s" % (
            cmd, parent, n, len(tss), tss[0]))
    if not seen:
        print("  (无)")
    print("\n总计 %d 条命中记录" % len(hits))


if __name__ == "__main__":
    main()
