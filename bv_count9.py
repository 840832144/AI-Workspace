# -*- coding: utf-8 -*-
"""验证「非空 token 数 == 已填格数」这个映射无关的计数关系。

不需要解 token->格 的映射，只需要数数：
  左边 = 该卡上 subtype1 明确报过的去重格数（硬 ground truth，可能不全）
  右边 = 该卡段非空 token 数
若 左边 <= 右边 且逐卡一致地接近，则「非空 token 数」可以当已填格数用，
填充率 = 非空token总数 / 应填，与映射无关。

用法：python bv_count9.py <session目录>
"""
import json
import os
import sys

sys.path.insert(0, r"D:\BingoVoyageProbe")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from bv_autoplay import Reader  # noqa

WSJ = r"D:\BingoVoyageProbe\out\bv_ws.jsonl"
BODIES = r"D:\BingoVoyageProbe\out\bv_bodies"


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
            k, i = rv(b, i)
        except Exception:
            break
        f, w = k >> 3, k & 7
        if w == 0:
            v, i = rv(b, i)
            out.append((f, 0, v))
        elif w == 2:
            try:
                ln, i = rv(b, i)
            except Exception:
                break
            if i + ln > n:
                break
            out.append((f, 2, b[i:i + ln]))
            i += ln
        elif w == 5:
            i += 4
        elif w == 1:
            i += 8
        else:
            break
    return out


sess = sys.argv[1] if len(sys.argv) > 1 else None
if not sess:
    print("用法: python bv_count9.py <session目录>")
    sys.exit(1)
C = json.load(open(os.path.join(sess, "cards_in_round.json"), encoding="utf-8"))
cards, rid = C["cards"], C["round"]
balls = set(Reader(WSJ).round_balls(rid))

daubs, state = [], None
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
    fs = fields(bd)
    if not (fs and fs[0][0] == 1 and fs[0][1] == 2):
        continue
    if fs[0][2].decode("utf-8", "replace") != rid:
        continue
    for f, w, v in fs[1:]:
        if f == 2 and w == 2:
            inner = fields(v)
            if inner and inner[0][1] == 0 and inner[0][2] == 1:
                for f2, w2, v2 in inner:
                    if f2 == 3 and w2 == 2:
                        d = {x[0]: x[2] for x in fields(v2) if x[1] == 0}
                        if 2 in d and 1 in d:
                            daubs.append((r["ts"], d[2] + 1, d[1]))
    if b"|" in bd and b"@" in bd:
        i = bd.find(b"|")
        while i > 0 and bd[i - 1] in b"|:@#Z0123456789,.":
            i -= 1
        j = bd.find(b"@Z", i)
        if j >= 0:
            state = (r["ts"], bd[i:j + 2].decode("ascii", "replace").split("|"))

print("局号 %s" % rid[-24:])
print("subtype1 daub 事件 %d 条，状态帧 %s" % (len(daubs), state[0] if state else "无"))
if not state:
    sys.exit(0)
toks = state[1]
nc = (len(toks) - 1) // 24

conf = {}
for ts, card, cell in daubs:
    conf.setdefault(card, set()).add(cell)

print("\n%-6s %-10s %-10s %-8s" % ("卡", "subtype1报格", "非空token", "应填"))
tot_c = tot_n = tot_need = 0
for c in range(1, nc + 1):
    seg = toks[(c - 1) * 24:c * 24]
    nz = sum(1 for t in seg if t != "")
    card = next((x for x in cards if x["slot"] == c), None)
    need = 0
    if card:
        need = sum(1 for k in range(25) if k != 12 and card["vals"][k] in balls)
    print("%-6d %-10d %-10d %-8d" % (c, len(conf.get(c, set())), nz, need))
    tot_c += len(conf.get(c, set()))
    tot_n += nz
    tot_need += need

print("\n合计   subtype1报格 %d   非空token %d   应填 %d" % (tot_c, tot_n, tot_need))
print("subtype1 <= 非空 ? %s" % ("是，计数关系成立" if tot_c <= tot_n else "否，不符"))
if tot_need:
    print("★ 用非空token数算的填充率 = %d / %d = %.1f%%" % (tot_n, tot_need, 100.0 * tot_n / tot_need))
    print("★ 用subtype1报格算的填充率 = %d / %d = %.1f%%  （会偏低，回执稀疏）"
          % (tot_c, tot_need, 100.0 * tot_c / tot_need))
