"""泛化暴力搜索：每卡 token 数 / 偏移 / 格序 三维搜索 cmd167 状态串映射。"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DATA = r"D:\BingoVoyageProbe\data"


def jl(n):
    p = os.path.join(DATA, n)
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []


def build_orders():
    out = []
    for skipfree in (True, False):
        col = []
        for c in range(5):
            for r in range(5):
                if skipfree and r == 2 and c == 2:
                    continue
                col.append((r, c))
        out.append(("列序%s" % ("跳FREE" if skipfree else "含FREE"), col))
        row = []
        for r in range(5):
            for c in range(5):
                if skipfree and r == 2 and c == 2:
                    continue
                row.append((r, c))
        out.append(("行序%s" % ("跳FREE" if skipfree else "含FREE"), row))
    return out


def main():
    rid_key = sys.argv[1] if len(sys.argv) > 1 else ".34"
    cards = [c for c in jl("cards.jsonl") if rid_key in (c["round_id"] or "")]
    allballs = [b for b in jl("balls.jsonl") if rid_key in (b["round_id"] or "")]
    daubs = [d for d in jl("daubs.jsonl")
             if rid_key in (d["round_id"] or "") and d["subtype"] == 9 and isinstance(d["detail"], str)]
    if not (cards and daubs):
        print("缺数据"); return 1
    d = daubs[-1]
    tss = d["ts"]
    balls = [b["ball"] for b in allballs if b["ts"] <= tss]
    called = set(balls)
    toks = d["detail"].split("|")
    cells = [(i, t) for i, t in enumerate(toks) if t and "@" not in t]

    print("状态串 %s  该时刻前已叫号 %d 个" % (tss, len(balls)))
    print("非空 token: %s\n" % cells)

    lut = {}
    for c in cards:
        for r in range(5):
            for col in range(5):
                v = c["grid"][r][col]
                if v:
                    lut[(c["slot"], r, col)] = v

    best = []
    for name, order in build_orders():
        for G in (23, 24, 25):
            for off in (0, 1, 2):
                ok = bad = 0
                detail = []
                for i, t in cells:
                    j = i - off
                    if j < 0:
                        continue
                    cardno = j // G + 1
                    if cardno > len(cards):
                        continue
                    local = j % G
                    if local >= len(order):
                        continue
                    r, col = order[local]
                    num = lut.get((cardno, r, col))
                    hit = (num in called) if num else False
                    ok += 1 if hit else 0
                    bad += 0 if hit else 1
                    detail.append((i, t, cardno, r + 1, col + 1, num, hit))
                best.append((ok, bad, "%s G=%d off=%d" % (name, G, off), detail))

    best.sort(key=lambda x: (-x[0], x[1]))
    print("=== 排名 ===")
    for ok, bad, tag, _ in best[:10]:
        print("  %2d 命中 / %2d 不符   %s" % (ok, bad, tag))
    ok, bad, tag, detail = best[0]
    print("\n=== 最佳: %s ===\n" % tag)
    for i, t, cardno, r, col, num, hit in detail:
        print("  token[%2d] %-6s -> 卡%d r%dc%d 号码=%-4s %s" % (
            i, repr(t), cardno, r, col, num, "✓" if hit else "✗"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
