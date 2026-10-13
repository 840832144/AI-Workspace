"""Bingo Voyage 自动 daub 坐标计算 + 批量点击。

用法：
    # 1) 传入当前已报的号码（空格或逗号分隔），输出需要 daub 的格子坐标
    python bv_daub.py plan 65 66 4 30 75

    # 2) 直接按计算结果点击（会跳过已 daub 的）
    python bv_daub.py tap 65 66 4 30 75

    # 3) 查看某张卡的当前卡面与 daub 状态
    python bv_daub.py show

状态文件 out/round_state.json 记录本局已 daub 的格子。
卡面数据 out/round_cards.json 每局开始时更新。
"""
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"D:\BingoVoyageProbe\out"
CARDS = os.path.join(BASE, "round_cards.json")
STATE = os.path.join(BASE, "round_state.json")
BVBAT = r"D:\BingoVoyageProbe\bvtool.py"


def load_cards():
    with open(CARDS, encoding="utf-8") as f:
        return json.load(f)


def load_state():
    if os.path.exists(STATE):
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    return {"daubed": {}}


def save_state(st):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)


def plan(nums):
    cfg = load_cards()
    st = load_state()
    daubed = set(st.get("daubed", {}).keys())
    cols_x = cfg["layout"]["cols_x"]
    rows_y = cfg["layout"]["rows_y"]
    hits = []
    for card in cfg["cards"]:
        slot = str(card["slot"])
        for r, row in enumerate(card["grid"]):
            for c, v in enumerate(row):
                if v in (0, None):
                    continue
                if v in nums:
                    key = "%s-%d-%d" % (slot, r, c)
                    hits.append({
                        "num": v, "card": slot, "row": r + 1, "col": c + 1,
                        "key": key, "done": key in daubed,
                        "x": cols_x[slot][c], "y": rows_y[slot][r],
                    })
    return hits


def show():
    cfg = load_cards()
    st = load_state()
    daubed = set(st.get("daubed", {}).keys())
    for card in cfg["cards"]:
        slot = str(card["slot"])
        print("=== 卡 %s ===" % slot)
        for r, row in enumerate(card["grid"]):
            cells = []
            for c, v in enumerate(row):
                s = "FREE" if v == 0 else str(v)
                mark = "*" if "%s-%d-%d" % (slot, r, c) in daubed else " "
                cells.append("%s%-4s" % (mark, s))
            print("  " + " ".join(cells))
        print()


def mark_done(hits):
    st = load_state()
    d = st.setdefault("daubed", {})
    for h in hits:
        d[h["key"]] = h["num"]
    save_state(st)


def cmd_plan(nums):
    hits = plan(nums)
    todo = [h for h in hits if not h["done"]]
    print("命中 %d 格，其中未 daub %d 格" % (len(hits), len(todo)))
    for h in hits:
        print("  %s卡%s r%dc%d = %d  (%d,%d) %s" % (
            "" if not h["done"] else "[已daub] ", h["card"], h["row"], h["col"],
            h["num"], h["x"], h["y"], ""))
    if todo:
        print("\n待点击:")
        for h in todo:
            print("  python bvtool.py tap %d %d   # %d" % (h["x"], h["y"], h["num"]))
    return todo


def cmd_tap(nums):
    todo = plan(nums)
    if not todo:
        print("无需点击")
        return
    for h in todo:
        subprocess.run([sys.executable, BVBAT, "tap", str(h["x"]), str(h["y"])],
                       check=False)
        print("  tapped %d at (%d,%d)" % (h["num"], h["x"], h["y"]))
        time.sleep(0.35)
    mark_done(todo)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "show":
        show()
    elif cmd == "plan":
        cmd_plan(set(int(x) for x in sys.argv[2:]))
    elif cmd == "tap":
        cmd_tap(set(int(x) for x in sys.argv[2:]))
    elif cmd == "reset":
        save_state({"daubed": {}})
        print("state reset")
