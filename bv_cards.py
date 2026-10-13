"""从 cmd 166 响应重建卡面（每卡 24 个数字，按列 B I N G O 顺序，FREE 省略）。"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
import bv_ws2
from bv_proto import parse, try_str  # noqa

BANDS = [("B", 1, 15), ("I", 16, 30), ("N", 31, 45), ("G", 46, 60), ("O", 61, 75)]


def nums_of(msg):
    """取某个 msg 里形如 2:{1:N} 的重复子消息，按出现顺序返回 N 列表"""
    out = []
    for fld, wt, val, ch in parse(msg):
        if fld == 2 and wt == 2 and ch is not None:
            for f2, w2, v2, c2 in parse(ch):
                if f2 == 1 and w2 == 0:
                    out.append(v2)
    return out


def build_card(vals):
    """24 个数字 -> 5x5 网格（FREE 插在 N 列中间）"""
    grid = [[None] * 5 for _ in range(5)]
    i = 0
    for c, (name, lo, hi) in enumerate(BANDS):
        take = 4 if name == "N" else 5
        col = vals[i:i + take]
        i += take
        if name == "N":
            col = col[:2] + [0] + col[2:]
        for r in range(5):
            grid[r][c] = col[r] if r < len(col) else None
    return grid


def main():
    for r in bv_ws2.load():
        f = r["f"]
        if not f.get("ok") or f["cmd"] != 166 or r["dir"] != "S->C":
            continue
        print("=" * 96)
        print("%s  %dB  topic=%s" % (r["ts"], len(f["body"]), f["topic"][:44]))
        rid = None
        cards = []
        for fld, wt, val, ch in parse(f["body"]):
            if fld == 1 and wt == 2 and ch is not None:
                rid = try_str(ch)
            if fld == 2 and wt == 2 and ch is not None:
                # 里面是 2:{...} 重复，每条是一张卡（含 1:seed + 2:{1:n}×24）
                for f2, w2, v2, c2 in parse(ch):
                    if w2 != 2 or c2 is None:
                        continue
                    seed = None
                    vals = []
                    for f3, w3, v3, c3 in parse(c2):
                        if f3 == 1 and w3 == 0:
                            seed = v3
                        elif f3 == 2 and w3 == 2 and c3 is not None:
                            for f4, w4, v4, c4 in parse(c3):
                                if f4 == 1 and w4 == 0:
                                    vals.append(v4)
                    if vals:
                        cards.append({"seed": seed, "vals": vals})
        print("roundId = %s" % rid)
        print("卡数 = %d" % len(cards))
        for n, c in enumerate(cards, 1):
            print("\n--- 卡 %d  seed=%s  下发 %d 个数字 ---" % (n, c["seed"], len(c["vals"])))
            print("    列序展开: %s" % c["vals"])
            if len(c["vals"]) == 24:
                g = build_card(c["vals"])
                print("    重建卡面:")
                print("      B    I    N    G    O")
                for row in g:
                    print("     " + " ".join(
                        ("FREE" if v == 0 else "%4s" % v) for v in row))
                # 列区间校验
                ok = True
                for col in range(5):
                    lo, hi = BANDS[col][1], BANDS[col][2]
                    for row in range(5):
                        v = g[row][col]
                        if v and not (lo <= v <= hi):
                            ok = False
                print("    列区间校验: %s" % ("✓ 全部合法" if ok else "✗ 有越界"))
        break


if __name__ == "__main__":
    main()
