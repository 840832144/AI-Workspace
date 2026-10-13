"""协议原生自动打局器：卡面读 cmd 166，报号读 cmd 169，命中即点。

★ 有时间上限（--seconds，最大 300），非常驻。

与 bv_autodaub.py 的区别：卡面不再依赖截图录入的 round_cards.json，
而是直接在 WS 帧里取 cmd 166 的响应 -> 与 data/cards.jsonl 同源。

用法：
    python bv_play.py --seconds 120
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"D:\BingoVoyageProbe"
sys.path.insert(0, ROOT)
from bv_ws2 import parse_frame  # noqa: E402
from bv_proto import parse, try_str  # noqa: E402
from collector.bv_extract import extract_cards as _xcards, harvest_strings  # noqa: E402

WS = os.path.join(ROOT, "out", "bv_ws.jsonl")
BODIES = os.path.join(ROOT, "out", "bv_bodies")
ADB = r"C:\platform-tools\adb.exe"
DEV = "127.0.0.1:16384"
BANDS = [("B", 1, 15), ("I", 16, 30), ("N", 31, 45), ("G", 46, 60), ("O", 61, 75)]

# 4 卡布局（900x1600 实测）
COLS = {"1": [113, 215, 312, 413, 515], "2": [533, 630, 731, 830, 930],
        "3": [113, 215, 312, 413, 515], "4": [533, 630, 731, 830, 930]}
ROWS = {"1": [450, 552, 656, 762, 867], "2": [450, 552, 656, 762, 867],
        "3": [930, 1032, 1140, 1245, 1353], "4": [930, 1032, 1140, 1245, 1353]}


def read_varint(b, i):
    v = s = 0
    while i < len(b):
        c = b[i]; i += 1
        v |= (c & 0x7F) << s
        if not (c & 0x80):
            return v, i
        s += 7
    return None, i


def newest_ball(body):
    """cmd169: field2 = 最近 5 个号码滑动窗口，右端最新"""
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



def _rid_of(body):
    for sv in harvest_strings(body, 20, 6):
        if sv.startswith("BINGO_HALL") and sv.count(".") >= 3 \
                and sv.rsplit(".", 1)[-1].isdigit():
            return sv
    return None


def _cards_of(body):
    return _xcards(body, _rid_of(body))


def grid_of(card):
    """卡面来自 cards.jsonl（已是 5x5，FREE=0）"""
    return card["grid"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=120)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    secs = max(5, min(a.seconds, 300))

    if not os.path.exists(WS):
        print("找不到 %s" % WS); return 1
    pos = os.path.getsize(WS)
    pos_card = 0
    cards = {}          # round_id -> [card...]
    daubed = set()      # (round_id, slot, r, c)
    seq = 0
    n_tap = 0
    t0 = time.time()

    # 先把已有的 cmd166 卡面读进来（当前局可能已经开过）
    with open(WS, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            h = r.get("hdr") or {}
            p = os.path.join(BODIES, r.get("file", ""))
            if not os.path.exists(p):
                continue
            fr = parse_frame(open(p, "rb").read())
            if fr.get("ok") and fr["cmd"] in (163, 166, 167) and r["dir"] == "S->C":
                found = _cards_of(fr["body"])
                if found:
                    cards[_rid_of(fr["body"]) or ("t%s" % r["ts"])] = found
    pos_card = pos
    print("预载 %d 局卡面，运行 %d 秒%s" % (
        len(cards), secs, "（dry-run）" if a.dry else ""))

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
                p = os.path.join(BODIES, r.get("file", ""))
                if not os.path.exists(p):
                    continue
                fr = parse_frame(open(p, "rb").read())
                if not fr.get("ok"):
                    continue
                if fr["cmd"] in (163, 166, 167) and r["dir"] == "S->C":
                    found = _cards_of(fr["body"])
                    if found:
                        ridn = _rid_of(fr["body"]) or ("t%s" % r["ts"])
                        cards[ridn] = found
                        print("[%s] 拿到卡面 %d 张  round=%s" % (
                            time.strftime("%H:%M:%S"), len(found), str(ridn)[-6:]))
                    continue
                if fr["cmd"] != 169 or r["dir"] != "S->C":
                    continue
                body = fr["body"]
                rid = None
                for fld, wt, val, ch in parse(body):
                    if fld == 1 and wt == 2 and ch is not None:
                        rid = try_str(ch)
                        break
                ball = newest_ball(body)
                if ball is None or rid not in cards:
                    continue
                for c in cards[rid]:
                    for rr in range(5):
                        for cc in range(5):
                            if c["grid"][rr][cc] != ball:
                                continue
                            key = (rid, c["slot"], rr, cc)
                            if key in daubed:
                                continue
                            slot = str(c["slot"])
                            if slot not in COLS:
                                continue
                            x, y = COLS[slot][cc], ROWS[slot][rr]
                            seq += 1
                            print("[%s] #%d ball=%2d 卡%s r%dc%d -> tap(%d,%d)" % (
                                time.strftime("%H:%M:%S"), seq, ball, slot, rr + 1, cc + 1, x, y))
                            if not a.dry:
                                subprocess.run([ADB, "-s", DEV, "shell", "input", "swipe",
                                                str(x), str(y), str(x), str(y), "120"],
                                               capture_output=True, timeout=30)
                                time.sleep(0.22)
                            daubed.add(key)
                            n_tap += 1
        time.sleep(0.35)
    print("\n结束：点击 %d 次，覆盖 %d 局卡面" % (n_tap, len(cards)))
    return 0


def extract_cards(body):
    """与 collector/bv_extract.py 一致：cmd166 响应 -> 卡面"""
    from collector.bv_extract import build_grid, fields
    rid = None
    cards = []
    for fld, wt, val, ch in fields(body):
        if fld == 1 and wt == 2 and ch is not None:
            rid = try_str(ch)
        elif fld == 2 and wt == 2 and ch is not None:
            for f2, w2, v2, c2 in fields(ch):
                if w2 != 2 or c2 is None:
                    continue
                seed, vals = None, []
                for f3, w3, v3, c3 in fields(c2):
                    if f3 == 1 and w3 == 0:
                        seed = v3
                    elif f3 == 2 and w3 == 2 and c3 is not None:
                        for f4, w4, v4, c4 in fields(c3):
                            if f4 == 1 and w4 == 0:
                                vals.append(v4)
                if vals:
                    cards.append({"round_id": rid, "slot": len(cards) + 1,
                                  "seed": seed, "vals": vals, "grid": build_grid(vals)})
    return cards


if __name__ == "__main__":
    sys.exit(main())
