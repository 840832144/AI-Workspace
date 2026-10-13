"""暴力搜索 cmd167 状态串的 token <-> 格子 映射（含时间过滤）。"""
import json
import os
import sys
from itertools import product

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DATA = r"D:\BingoVoyageProbe\data"


def jl(n):
    p = os.path.join(DATA, n)
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []


def orders():
    """候选 : (名字, [(row,col)] * 24 顺序)"""
    out = []
    # 1 列序 B5 I5 N5 G5 O5 跳过 FREE
    o = []
    for c in range(5):
        for r in range(5):
            if r == 2 and c == 2:
                continue
            o.append((r, c))
    out.append(("列序-B5I5N5G5O5-跳FREE", o))
    # 2 列序 不跳 FREE（25，取前24）
    o = [(r, c) for c in range(5) for r in range(5)]
    out.append(("列序-含FREE", o[:24]))
    # 3 行序 跳 FREE
    o = []
    for r in range(5):
        for c in range(5):
            if r == 2 and c == 2:
                continue
            o.append((r, c))
    out.append(("行序-跳FREE", o))
    # 4 行序 含 FREE
    o = [(r, c) for r in range(5) for c in range(5)]
    out.append(("行序-含FREE", o[:24]))
    # 5 列序但 G/O 列放在 N 之前 之类变体
    o = []
    for c in [0, 1, 3, 4, 2]:
        for r in range(5):
            if r == 2 and c == 2:
                continue
            o.append((r, c))
    out.append(("列序-BINGO重排(2最后)跳FREE", o))
    return out


def main():
    rid_key = sys.argv[1] if len(sys.argv) > 1 else ".34"
    cards = [c for c in jl("cards.jsonl") if rid_key in (c["round_id"] or "")]
    allballs = [b for b in jl("balls.jsonl") if rid_key in (b["round_id"] or "")]
    daubs = [d for d in jl("daubs.jsonl")
             if rid_key in (d["round_id"] or "") and d["subtype"] == 9 and isinstance(d["detail"], str)]
    if not (cards and daubs):
        print("缺数据")
        return 1

    d = daubs[-1]
    tss = d["ts"]
    balls = [b["ball"] for b in allballs if b["ts"] <= tss]
    called = set(balls)
    toks = d["detail"].split("|")
    nonempty = [(i, t) for i, t in enumerate(toks) if t and "@" not in t]

    print("状态串时间 %s   该时刻前已叫号 %d 个: %s" % (tss, len(balls), balls))
    print("非空 token(排除@): %s\n" % nonempty)

    lut = {}
    for c in cards:
        for r in range(5):
            for col in range(5):
                v = c["grid"][r][col]
                if v:
                    lut[(c["slot"], r, col)] = v

    results = []
    for name, order in orders():
        for off in (0, 1):
            ok = bad = 0
            detail = []
            for i, t in nonempty:
                j = i - off
                if j < 0:
                    continue
                cardno = j // 24 + 1
                local = j % 24
                if local >= len(order):
                    continue
                r, col = order[local]
                num = lut.get((cardno, r, col))
                hit = (num in called) if num else False
                ok += 1 if hit else 0
                bad += 0 if hit else 1
                detail.append((i, t, cardno, r + 1, col + 1, num, hit))
            results.append((ok, bad, name, off, detail))

    results.sort(key=lambda x: (-x[0], x[1]))
    print("=== 排名（命中已叫号数 / 不符数）===")
    for ok, bad, name, off, detail in results[:6]:
        print("  %2d 命中 / %2d 不符   %s  偏移=%d" % (ok, bad, name, off))
    ok, bad, name, off, detail = results[0]
    print("\n=== 最佳组合明细: %s 偏移=%d ===\n" % (name, off))
    for i, t, cardno, r, col, num, hit in detail:
        print("  token[%2d] %-6s -> 卡%d r%dc%d 号码=%s %s" % (
            i, repr(t), cardno, r, col, num, "✓" if hit else "✗"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
