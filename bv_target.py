"""从 data/cards.jsonl + balls.jsonl 算出「已叫号但未 daub」的格子，给出屏幕坐标。

用法：python bv_target.py [局号关键字]
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DATA = r"D:\BingoVoyageProbe\data"

# 4 卡布局（900x1600 实测）
COLS = {"1": [113, 215, 312, 413, 515], "2": [533, 630, 731, 830, 930],
        "3": [113, 215, 312, 413, 515], "4": [533, 630, 731, 830, 930]}
ROWS = {"1": [450, 552, 656, 762, 867], "2": [450, 552, 656, 762, 867],
        "3": [930, 1032, 1140, 1245, 1353], "4": [930, 1032, 1140, 1245, 1353]}


def jl(n):
    p = os.path.join(DATA, n)
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else ""
    cards = jl("cards.jsonl")
    balls = jl("balls.jsonl")
    if not cards:
        print("没有卡面数据"); return 1
    rid = cards[-1]["round_id"]
    if key:
        for c in cards:
            if key in (c["round_id"] or ""):
                rid = c["round_id"]
                break
    rc = [c for c in cards if c["round_id"] == rid]
    rb = [b["ball"] for b in balls if b["round_id"] == rid]
    print("局: %s" % rid)
    print("卡数: %d   已叫号: %d 个" % (len(rc), len(rb)))
    print("报号序列: %s" % rb)
    print()
    called = set(rb)
    for c in rc:
        slot = str(c["slot"])
        hits = []
        for r in range(5):
            for col in range(5):
                v = c["grid"][r][col]
                if v and v in called:
                    hits.append((v, r, col, COLS[slot][col], ROWS[slot][r]))
        if hits:
            print("卡%s 已叫号且可 daub 的格（共 %d）:" % (slot, len(hits)))
            for v, r, col, x, y in hits:
                print("   号码 %2d  r%dc%d   tap(%d,%d)   <= 列序 token 索引 %d"
                      % (v, r + 1, col + 1, x, y, col * 5 + r - (1 if col >= 3 else 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
