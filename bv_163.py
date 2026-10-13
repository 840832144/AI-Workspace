"""解 cmd 163（回合卡面/状态下发）的完整结构。"""
import sys
import json
import os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
import bv_ws2
from bv_proto import parse, try_str, render  # noqa
from collector.bv_extract import build_grid, BANDS  # noqa


def main():
    for r in bv_ws2.load():
        f = r["f"]
        if not f.get("ok") or f["cmd"] != 163:
            continue
        print("=" * 96)
        print("%s %s %dB topic=%s" % (r["ts"], r["dir"], len(f["body"]),
                                      str(f["topic"])[:44]))
        if len(f["body"]) < 50:
            continue
        lines = render(f["body"])
        print("\n".join(lines[:70]))
        print("...(共 %d 行)" % len(lines))

        # 试着按卡面提取
        cards = []
        for fld, wt, val, ch in parse(f["body"]):
            if fld != 1 or wt != 2 or ch is None:
                continue
            for f2, w2, v2, c2 in parse(ch):
                if w2 != 2 or c2 is None:
                    continue
                seed, vals = None, []
                for f3, w3, v3, c3 in parse(c2):
                    if f3 == 1 and w3 == 0:
                        seed = v3
                    elif f3 == 2 and w3 == 2 and c3 is not None:
                        for f4, w4, v4, c4 in parse(c3):
                            if f4 == 1 and w4 == 0:
                                vals.append(v4)
                if len(vals) >= 20:
                    cards.append((seed, vals))
        if cards:
            print("\n### 按卡面解读: %d 张" % len(cards))
            for n, (seed, vals) in enumerate(cards, 1):
                print("--- 卡 %d seed=%s (%d 个值)" % (n, seed, len(vals)))
                print("    %s" % vals)
                if len(vals) == 25:
                    g = build_grid(vals)
                    print("      B    I    N    G    O")
                    for row in g:
                        print("     " + " ".join(
                            "FREE" if v == 0 else "%4d" % v for v in row))
        break


if __name__ == "__main__":
    main()
