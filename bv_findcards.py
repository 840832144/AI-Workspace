"""在全量 WS 帧里搜「卡面数据」：找重复 varint 字段、值域 1..75、数量 25 的倍数。"""
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
import bv_ws2
from bv_proto import parse, try_str  # noqa


def walk(b, depth=0, path=""):
    """递归产出 (path, [(field, varint)...])"""
    groups = {}
    i_list = []
    try:
        items = parse(b)
    except Exception:
        return
    for fld, wt, val, ch in items:
        if fld is None:
            continue
        p = "%s.%d" % (path, fld)
        if wt == 0:
            i_list.append((fld, val))
        elif wt == 2 and isinstance(val, int) and val > 1 and ch is not None:
            if depth < 6:
                yield from walk(ch, depth + 1, p)
    if i_list:
        yield (path, i_list)


def main():
    recs = bv_ws2.load()
    print("扫描 %d 帧..." % len(recs))
    hits = Counter()
    examples = {}
    for r in recs:
        f = r["f"]
        if not f.get("ok") or not f["body"]:
            continue
        for path, lst in walk(f["body"]):
            # 同一字段连续出现 >=25 次且都在 1..75
            by = {}
            for fld, v in lst:
                by.setdefault(fld, []).append(v)
            for fld, vals in by.items():
                if len(vals) >= 25 and all(1 <= v <= 75 for v in vals):
                    key = (f["cmd"], path + ".%d" % fld)
                    hits[key] += 1
                    examples.setdefault(key, (r["ts"], r["dir"], vals[:30]))
    print("\n=== 命中（cmd, 字段路径）候选 ===")
    for (cmd, pth), n in hits.most_common(30):
        ts, d, vals = examples[(cmd, pth)]
        print("cmd=%-5d %-18s x%-4d  例 %s %s  前30值=%s" % (
            cmd, pth, n, ts, d, vals))
    print("\n总候选 %d 组" % len(hits))


if __name__ == "__main__":
    main()
