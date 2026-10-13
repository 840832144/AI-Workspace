# -*- coding: utf-8 -*-
"""填充率：完全用协议数据算，不碰截图。

  应填 = 本局已叫号 ∩ 卡面上的格（FREE 除外）
  已填 = 本局 cmd167 subtype9 最后一个状态帧里的非空 token 数
  填充率 = 已填 / 应填

用法：python bv_fill.py <session目录>
"""
import json
import os
import sys

sys.path.insert(0, r"D:\BingoVoyageProbe")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from bv_autoplay import Reader, parse_frame, rid_of, parse, BODIES  # noqa

WSJ = r"D:\BingoVoyageProbe\out\bv_ws.jsonl"


def rv(bb, i):
    r = s = 0
    while True:
        x = bb[i]
        i += 1
        r |= (x & 0x7F) << s
        s += 7
        if not x & 0x80:
            return r, i


def body_of(b):
    ln, i = rv(b, 9)
    i += ln
    return b[i:]


def fields(b):
    out, i, n = [], 0, len(b)
    while i < n:
        try:
            key, i = rv(b, i)
        except Exception:
            break
        fld, wt = key >> 3, key & 7
        if wt == 0:
            v, i = rv(b, i)
            out.append((fld, 0, v))
        elif wt == 2:
            try:
                ln, i = rv(b, i)
            except Exception:
                break
            if i + ln > n:
                break
            out.append((fld, 2, b[i:i + ln]))
            i += ln
        elif wt == 5:
            i += 4
        elif wt == 1:
            i += 8
        else:
            break
    return out


def state_tokens():
    """返回 {rid: (ts, token列表)}，取每个局最后一个状态帧"""
    got = {}
    for ln in open(WSJ, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        if r.get("hdr", {}).get("cmd") != 167 or r.get("dir") != "C->S":
            continue
        p = os.path.join(BODIES, r.get("file", ""))
        if not os.path.exists(p):
            continue
        bd = body_of(open(p, "rb").read())
        if b"|" not in bd or b"@" not in bd:
            continue
        fs = fields(bd)
        rid = fs[0][2].decode("utf-8", "replace") if fs and fs[0][0] == 1 else None
        i = bd.find(b"|")
        while i > 0 and bd[i - 1] in b"|:@#Z0123456789,.":
            i -= 1
        j = bd.find(b"@Z", i)
        tok = bd[i:j + 2] if j >= 0 else bd[i:]
        got[rid] = (r["ts"], tok.decode("ascii", "replace").split("|"))
    return got


def tok2cell(k):
    return k if k < 12 else k + 1


def main():
    sess = sys.argv[1] if len(sys.argv) > 1 else None
    if not sess:
        print("用法: python bv_fill.py <session目录>")
        return 1
    C = json.load(open(os.path.join(sess, "cards_in_round.json"), encoding="utf-8"))
    cards = C.get("cards") or []
    rid = C.get("round")
    if not cards or not rid:
        print("会话里没有卡面/局号")
        return 1
    r = Reader(WSJ)
    balls = sorted(set(r.round_balls(rid)))
    print("局号: %s" % rid)
    print("卡数: %d   已叫号: %d 个 -> %s" % (len(cards), len(balls), balls))

    need = set()
    for c in cards:
        v = c["vals"]
        for k in range(25):
            if k == 12:
                continue
            if v[k] in balls:
                need.add((c["slot"], k))
    print("应填 = %d 格" % len(need))

    st = state_tokens().get(rid)
    if not st:
        print("该局没有 subtype9 状态帧，无法算已填")
        return 1
    ts, toks = st
    ncard = (len(toks) - 1) // 24
    filled = set()
    kinds = {}
    for ci in range(ncard):
        seg = toks[ci * 24:(ci + 1) * 24]
        for k, t in enumerate(seg):
            if t == "":
                continue
            v = t.split("@")[0].split("#")[0][-4:]
            kinds[v] = kinds.get(v, 0) + 1
            idx = tok2cell(k)
            filled.add((ci + 1, idx))
    print("状态帧 %s  卡数 %d  token %d" % (ts, ncard, len(toks)))
    print("已填 = %d 格   类型分布 %s" % (len(filled), kinds))

    inter = len(need & filled)
    extra = len(filled - need)
    miss = len(need - filled)
    print()
    print("对齐：应填∩已填 = %d，漏点 = %d，已填但不在应填里 = %d" % (inter, miss, extra))
    print("★ 填充率 = %d / %d = %.1f%%" % (inter, len(need), 100.0 * inter / max(len(need), 1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
