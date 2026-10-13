# -*- coding: utf-8 -*-
"""填图率度量 —— 自动玩的核心 KPI。

定义
----
  应填格数（理论最大填图） = 会话时间窗内「已叫号」中，出现在我卡面上的格
                             （FREE 不算；只算会话期间，避免把开局前的球算进来）
  已填格数                 = 客户端回执确认已 daub 的格
  填图率                   = 已填 / 应填
  另有「顺手率」           = 已填 / 本会话点击过的格（衡量点击有没有白点）

正常玩家在有 Daub Alert 提示下应 ≥95%，自动玩不得低于这个数。

用法：python bv_rate.py [session目录]
"""
import datetime
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"D:\BingoVoyageProbe"
DATA_NAME = "autoplay_"
DATA = os.path.join(ROOT, "data")

# 列序 B5 I5 N5 G5 O5 的 0 基索引 -> (row, col)
def idx2rc(k):
    return k % 5, k // 5


def ts2s(t):
    return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timestamp()


def jl(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def prepare():
    cards_by_round, balls_by_round = {}, {}
    for c in jl("cards.jsonl"):
        cards_by_round.setdefault(c["round_id"], []).append(c)
    for b in jl("balls.jsonl"):
        balls_by_round.setdefault(b["round_id"], []).append(b)
    return cards_by_round, balls_by_round


def cells(vals, ball):
    out = []
    for k in range(min(25, len(vals))):
        if vals[k] != ball:
            continue
        r, c = idx2rc(k)
        if r == 2 and c == 2:
            continue
        out.append((r, c))
    return out


def one(sdir, cards_by_round, balls_by_round):
    sp = os.path.join(sdir, "session.json")
    ap = os.path.join(sdir, "actions.jsonl")
    cp = os.path.join(sdir, "cards_in_round.json")
    if not (os.path.exists(sp) and os.path.exists(ap)):
        return None
    S = json.load(open(sp, encoding="utf-8"))
    try:
        t0 = ts2s(S["start"])
    except Exception:
        return None
    t1 = t0 + float(S.get("seconds", 0))
    rid = S.get("round")

    # 卡面优先级：会话自带的 cards_in_round.json > 全局 cards.jsonl（同局精确匹配）
    cs = []
    if os.path.exists(cp):
        try:
            cs = json.load(open(cp, encoding="utf-8")).get("cards") or []
        except Exception:
            cs = []
    if not cs and rid:
        cs = cards_by_round.get(rid) or []
    if not cs:
        return None

    acked, tapped = set(), set()
    for line in open(ap, encoding="utf-8"):
        try:
            a = json.loads(line)
        except Exception:
            continue
        key = (a.get("slot"), a.get("r"), a.get("c"))
        if a.get("kind") == "ack":
            acked.add(key)
        elif a.get("kind") == "tap":
            tapped.add(key)

    # 只统计本会话时间窗内的号；优先用会话记录的局号精确匹配
    pool = balls_by_round.get(rid) if rid else None
    if pool is None:
        pool = []
        for r2, bs in sorted(balls_by_round.items()):
            if len([b for b in bs if t0 <= ts2s(b["ts"]) <= t1]) > \
               len([b for b in pool if t0 <= ts2s(b["ts"]) <= t1]):
                pool = bs
    win = [b["ball"] for b in pool if t0 <= ts2s(b["ts"]) <= t1]

    need = set()
    for b in win:
        for c in cs:
            for (r, cc) in cells(c.get("vals") or [], b):
                need.add((c.get("slot"), r, cc))
    if not need:
        return None
    return {"round": rid, "need": len(need), "got": len(acked & need),
            "balls": len(win), "tapped": len(tapped),
            "acked_total": len(acked), "taps": S.get("taps"),
            "retry": S.get("retries"), "giveup": S.get("retry_giveup") or S.get("give_up"),
            "mismatch": S.get("ack_mismatch")}


def main():
    cards_by_round, balls_by_round = prepare()
    dirs = [sys.argv[1]] if len(sys.argv) > 1 else \
        sorted(glob.glob(os.path.join(ROOT, "sessions", DATA_NAME + "*")))
    print("卡面覆盖 %d 局 / 报号覆盖 %d 局 / 会话 %d 个"
          % (len(cards_by_round), len(balls_by_round), len(dirs)))
    print()
    print("%-26s %6s %6s %7s %7s %6s" % ("会话", "应填", "已填", "填图率", "点中率", "达标"))
    tn = tg = 0
    for d in dirs:
        r = one(d, cards_by_round, balls_by_round)
        if not r:
            continue
        rate = 100.0 * r["got"] / r["need"] if r["need"] else 0
        succ = 100.0 * r["got"] / r["tapped"] if r["tapped"] else 0
        print("%-26s %6d %6d %6.1f%% %6.1f%% %6s" % (
            os.path.basename(d)[-24:], r["need"], r["got"], rate, succ,
            "✓" if rate >= 95 else "✗"))
        tn += r["need"]
        tg += r["got"]
    print()
    if tn:
        print("合计：应填 %d，已填 %d，填图率 %.1f%%" % (tn, tg, 100.0 * tg / tn))
        print("目标：≥95%（有 Daub Alert 的玩家水平）")
    else:
        print("（无可统计会话）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
