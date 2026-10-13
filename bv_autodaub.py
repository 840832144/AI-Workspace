"""协议驱动的自动 daub：直接读 WebSocket 的 cmd 169 报号帧，命中即点。

★ 注意：这是**有时间上限的短跑工具**，用完即退，不做常驻。
   默认 --seconds 60，最大允许 180。

原理：
    bv_ws.jsonl 里每个 cmd 169 帧的 protobuf field 2 = 最近 5 个已叫号码的滑动窗口，
    右端即最新叫出的号（见 docs/BINGO_VOYAGE_FINDINGS.md §3.6）。
    本脚本增量读该文件，取新号，与 out/round_cards.json 的卡面比对，命中且未 daub 则 adb tap。

用法：
    python bv_autodaub.py --seconds 60
    python bv_autodaub.py --seconds 60 --dry     # 只打印不点击
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
from bv_ws2 import parse_frame as _parse_frame  # noqa: E402

BASE = r"D:\BingoVoyageProbe"
WS = os.path.join(BASE, "out", "bv_ws.jsonl")
CARDS = os.path.join(BASE, "out", "round_cards.json")
STATE = os.path.join(BASE, "out", "autodaub_state.json")
BVBAT = os.path.join(BASE, "bvtool.py")
ADB = r"C:\platform-tools\adb.exe"
DEV = "127.0.0.1:16384"


def read_varint(b, i):
    v = 0
    s = 0
    while i < len(b):
        c = b[i]
        i += 1
        v |= (c & 0x7F) << s
        if not (c & 0x80):
            return v, i
        s += 7
    return None, i


def newest_ball(body):
    """cmd 169 body -> 最新叫出的号（field2 的最后一个 uint8）"""
    i = 0
    while i < len(body):
        k, i = read_varint(body, i)
        if k is None:
            return None
        fld, wt = k >> 3, k & 7
        if wt == 0:
            _, i = read_varint(body, i)
        elif wt == 2:
            ln, i = read_varint(body, i)
            if ln is None or i + ln > len(body):
                return None
            if fld == 2 and ln:
                return body[i + ln - 1]
            i += ln
        elif wt == 5:
            i += 4
        elif wt == 1:
            i += 8
        else:
            return None
    return None


def load_cards():
    return json.load(open(CARDS, encoding="utf-8"))


def find_hits(cfg, num):
    """返回 (slot,row,col,x,y) 列表"""
    out = []
    for card in cfg["cards"]:
        slot = str(card["slot"])
        for r, row in enumerate(card["grid"]):
            for c, v in enumerate(row):
                if v == num:
                    out.append((slot, r, c,
                                cfg["layout"]["cols_x"][slot][c],
                                cfg["layout"]["rows_y"][slot][r]))
    return out


def tap(x, y):
    subprocess.run([ADB, "-s", DEV, "shell", "input", "swipe",
                    str(x), str(y), str(x), str(y), "120"],
                   capture_output=True, timeout=30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=60)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    secs = max(5, min(a.seconds, 180))

    cfg = load_cards()
    st = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {"daubed": []}
    daubed = set(st.get("daubed", []))
    if not os.path.exists(WS):
        print("找不到 %s（先在 mitmproxy 里抓一轮）" % WS)
        return 1
    pos = os.path.getsize(WS)
    print("从 offset=%d 开始增量读，运行 %d 秒%s" % (pos, secs, "（dry-run）" if a.dry else ""))
    t0 = time.time()
    seen_balls = []
    n_tap = 0
    while time.time() - t0 < secs:
        size = os.path.getsize(WS)
        if size > pos:
            with open(WS, encoding="utf-8") as f:
                f.seek(pos)
                chunk = f.read()
                pos = f.tell()
            for line in chunk.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                h = r.get("hdr") or {}
                p = os.path.join(BASE, "out", "bv_bodies", r["file"])
                if not os.path.exists(p):
                    continue
                body = open(p, "rb").read()
                # 用 bv_ws2 的权威解析（addon 写的 hdr 可能来自旧版逻辑）
                fr = _parse_frame(body)
                if not fr.get("ok") or fr["cmd"] != 169:
                    continue
                num = newest_ball(body)
                if num is None or num in seen_balls:
                    continue
                seen_balls.append(num)
                hits = find_hits(cfg, num)
                if not hits:
                    print("[%s] ball=%2d  (不在卡上)" % (time.strftime("%H:%M:%S"), num))
                    continue
                for slot, r_, c_, x, y in hits:
                    key = "%s-%d-%d" % (slot, r_, c_)
                    if key in daubed:
                        continue
                    print("[%s] ball=%2d  卡%s r%dc%d (num=%d) -> tap(%d,%d)" % (
                        time.strftime("%H:%M:%S"), num, slot, r_ + 1, c_ + 1, num, x, y))
                    if not a.dry:
                        tap(x, y)
                        time.sleep(0.25)
                    daubed.add(key)
                    n_tap += 1
        time.sleep(0.4)
    st["daubed"] = sorted(daubed)
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n结束：收到 %d 个新号，执行 %d 次点击" % (len(seen_balls), n_tap))
    print("号码序列: %s" % seen_balls)
    return 0


if __name__ == "__main__":
    sys.exit(main())
