"""Bingo Voyage 闭环回放器：有了卡面（cmd 166）+ 报号（cmd 169），
离线把「买卡 -> 叫号 -> 中奖判定」完整推演出来，并与客户端上报（cmd 167）对账。

输出：
    data/replay.jsonl   每局：卡面 / 报号序列 / 自动命中格 / 达成的 BINGO 线
    data/replay_summary.md

用法：
    python collector\\bv_replay.py
"""
import json
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import collector.bv_extract as EX  # noqa: E402

DATA = EX.DATA
BANDS = EX.BANDS
CELL_ORDER = EX.cell_order()   # [(local_idx, row, col)] 列序，跳过 FREE


def jl(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def lines_of(grid_daubed):
    """返回所有连线（横5 / 竖5 / 两条对角）"""
    out = []
    for r in range(5):
        if all(grid_daubed[r][c] for c in range(5)):
            out.append(("row", r + 1, [(r, c) for c in range(5)]))
    for c in range(5):
        if all(grid_daubed[r][c] for r in range(5)):
            out.append(("col", c + 1, [(r, c) for r in range(5)]))
    if all(grid_daubed[i][i] for i in range(5)):
        out.append(("diag", "\\", [(i, i) for i in range(5)]))
    if all(grid_daubed[i][4 - i] for i in range(5)):
        out.append(("diag", "/", [(i, 4 - i) for i in range(5)]))
    return out


def main():
    cards = jl("cards.jsonl")
    balls = jl("balls.jsonl")
    daubs = jl("daubs.jsonl")

    by_round_cards = OrderedDict()
    for c in cards:
        by_round_cards.setdefault(c["round_id"], []).append(c)
    by_round_balls = OrderedDict()
    for b in balls:
        by_round_balls.setdefault(b["round_id"], []).append(b["ball"])
    reports = OrderedDict()
    for d in daubs:
        if d.get("round_id"):
            reports.setdefault(d["round_id"], []).append(d)

    out = open(os.path.join(DATA, "replay.jsonl"), "w", encoding="utf-8")
    L = ["# Bingo Voyage 闭环回放", "",
         "> 卡面来自 `cmd 166`，报号来自 `cmd 169`，daub 上报来自 `cmd 167`。", ""]
    n_full = 0

    for rid, cs in by_round_cards.items():
        bseq = by_round_balls.get(rid, [])
        rec = {"round_id": rid, "n_cards": len(cs), "balls": bseq, "cards": []}
        L.append("\n## `%s`\n" % rid)
        L.append("报号序列（%d 个）：`%s`\n" % (len(bseq), bseq))

        for c in cs:
            grid = c["grid"]
            # 号码 -> 格坐标
            num2cell = {}
            for r in range(5):
                for col in range(5):
                    v = grid[r][col]
                    if v:
                        num2cell[v] = (r, col)
            daubed = [[False] * 5 for _ in range(5)]
            daubed[2][2] = True          # FREE 自带
            hits = []
            bingos = []
            for n, ball in enumerate(bseq, 1):
                cell = num2cell.get(ball)
                if cell is None:
                    continue
                r, col = cell
                if daubed[r][col]:
                    continue
                daubed[r][col] = True
                hits.append((n, ball, r + 1, col + 1))
                ls = lines_of(daubed)
                if ls:
                    bingos.append({"after_ball_no": n, "ball": ball,
                                   "lines": ["%s%s" % (k, i) for k, i, _ in ls]})
                    break                # 一卡一局只判一次
            rec["cards"].append({
                "slot": c["slot"], "seed": c["seed"],
                "hits": [{"ball_no": a, "ball": b, "row": r, "col": cl}
                         for a, b, r, cl in hits],
                "bingos": bingos,
                "grid": grid,
            })
            tag = "**BINGO**" if bingos else "未成线"
            L.append("- 卡 %d：命中 %d 格%s" % (
                c["slot"], len(hits),
                ("　→ **BINGO @ 第 %d 号(%d)** 线=%s" % (
                    bingos[0]["after_ball_no"], bingos[0]["ball"],
                    ",".join(bingos[0]["lines"]))) if bingos else ""))
            if hits:
                L.append("  - 命中明细：" + ", ".join(
                    "#%d球%d→r%dc%d" % h for h in hits))

        nb = sum(1 for c in rec["cards"] if c["bingos"])
        rec["n_bingo_cards"] = nb
        if nb:
            n_full += 1
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")

        rep = reports.get(rid, [])
        if rep:
            L.append("\n**客户端 cmd 167 上报（%d 条）**\n" % len(rep))
            for d in rep:
                L.append("- `%s` subtype=%s detail=`%s`" % (
                    d["ts"][11:], d["subtype"], str(d["detail"])[:80]))
        else:
            L.append("\n_(本局无 cmd 167 上报被抓到)_")

    out.close()
    L.append("\n---\n\n共回放 %d 局，其中 %d 局至少有一张卡成线。\n" % (
        len(by_round_cards), n_full))
    p = os.path.join(DATA, "replay_summary.md")
    open(p, "w", encoding="utf-8").write("\n".join(L))
    print("已回放 %d 局（%d 局出 bingo）-> %s" % (
        len(by_round_cards), n_full, p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
