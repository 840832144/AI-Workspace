"""严格验证 cmd167 状态串的 token <-> 格子映射。

方法：拿同一局（round 34）的
  - 卡面（cmd 166 -> data/cards.jsonl）
  - 报号（cmd 169 -> data/balls.jsonl）
  - 状态串（cmd 167 subtype9 -> data/daubs.jsonl）
把状态串的非空 token 索引映射成 (卡, 行, 列)，看那些格子的号码是否都在已叫号集合里。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DATA = r"D:\BingoVoyageProbe\data"


def jl(n):
    p = os.path.join(DATA, n)
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []


def col_major_index(r, c):
    """列序 B5 I5 N5 G5 O5，跳过 FREE(2,2) -> 0..23"""
    idx = 0
    for cc in range(5):
        for rr in range(5):
            if rr == 2 and cc == 2:
                continue
            if rr == r and cc == c:
                return idx
            idx += 1
    return None


def main():
    rid_key = sys.argv[1] if len(sys.argv) > 1 else ".34"
    cards = [c for c in jl("cards.jsonl") if rid_key in (c["round_id"] or "")]
    balls = [b["ball"] for b in jl("balls.jsonl") if rid_key in (b["round_id"] or "")]
    daubs = [d for d in jl("daubs.jsonl")
             if rid_key in (d["round_id"] or "") and d["subtype"] == 9
             and isinstance(d["detail"], str)]

    if not (cards and daubs):
        print("缺数据: cards=%d daubs=%d" % (len(cards), len(daubs)))
        return 1

    called = set(balls)
    print("局: %s" % cards[0]["round_id"])
    print("卡数: %d   已叫号: %d 个 -> %s" % (len(cards), len(balls), balls))
    print("状态串条数: %d" % len(daubs))

    for d in daubs[-1:]:
        s = d["detail"]
        toks = s.split("|")
        print("\n状态串 (%s, 长 %d, token %d):" % (d["ts"], len(s), len(toks)))
        # @ 位置
        at = [i for i, t in enumerate(toks) if "@" in t]
        print("  '@' 边界出现在 token 索引: %s   (差 = %s)" % (
            at, [at[i + 1] - at[i] for i in range(len(at) - 1)] if len(at) > 1 else []))
        nonempty = [(i, t) for i, t in enumerate(toks) if t]
        print("  非空 token: %s" % nonempty)

        # 卡面：建立 (卡slot, row, col) -> number
        lut = {}
        for c in cards:
            for r in range(5):
                for col in range(5):
                    v = c["grid"][r][col]
                    if v:
                        lut[(c["slot"], r, col)] = v

        print("\n  假设 1：token 索引 = 卡内列序索引(0..23)，每 24 个换一张卡")
        ok = bad = 0
        for i, t in nonempty:
            if "@" in t:
                continue
            cardno = i // 24 + 1
            local = i % 24
            # local -> (row,col)
            pos = None
            k = 0
            for cc in range(5):
                for rr in range(5):
                    if rr == 2 and cc == 2:
                        continue
                    if k == local:
                        pos = (rr, cc)
                    k += 1
            if pos is None:
                continue
            num = lut.get((cardno, pos[0], pos[1]))
            hit = num in called if num else False
            ok += 1 if hit else 0
            bad += 0 if hit else 1
            print("    token[%2d] %-6s -> 卡%d r%dc%d 号码=%s  已叫号=%s" % (
                i, repr(t), cardno, pos[0] + 1, pos[1] + 1, num, "✓" if hit else "✗"))
        print("  假设1 结果: 命中已叫号 %d 个, 不符 %d 个" % (ok, bad))
    return 0


if __name__ == "__main__":
    sys.exit(main())
