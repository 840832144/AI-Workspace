# -*- coding: utf-8 -*-
"""用「应填」检验 token→格 的候选映射。

应填 = 已叫号 ∩ 卡面格，是独立于状态串算出来的。
正确的映射必须让「非空 token 的格」几乎全部落在应填里（重叠率接近 100%）。
逐个试候选映射，重叠率最高的就是对的。
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


# ---- 候选映射：token 下标 k(0..23) -> 25 格里的 index ----
def mk_col_skip(k):      # 列主序，跳过 FREE(12)
    return k if k < 12 else k + 1


def mk_row_skip(k):      # 行主序，跳过 FREE(12)
    i = k if k < 12 else k + 1
    return (i % 5) * 5 + (i // 5)


def mk_col_noskip(k):    # 列主序，不跳（token 直接对应 24 个前格）
    return k


def mk_row_noskip(k):
    return (k % 5) * 5 + (k // 5)


MAPS = [("列主序跳FREE", mk_col_skip), ("行主序跳FREE", mk_row_skip),
        ("列主序不跳", mk_col_noskip), ("行主序不跳", mk_row_noskip)]

sess = sys.argv[1] if len(sys.argv) > 1 else None
if not sess:
    print("用法: python bv_tokenmap.py <session目录>")
    sys.exit(1)
C = json.load(open(os.path.join(sess, "cards_in_round.json"), encoding="utf-8"))
cards, rid = C["cards"], C["round"]
balls = set(Reader(WSJ).round_balls(rid))

need = set()
for c in cards:
    for k in range(25):
        if k == 12:
            continue
        if c["vals"][k] in balls:
            need.add((c["slot"], k))
print("局号 %s   卡 %d 张   叫号 %d 个   应填 %d 格\n" % (rid[-22:], len(cards), len(balls), len(need)))

toks = None
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
    if not (fs and fs[0][0] == 1 and fs[0][1] == 2):
        continue
    if fs[0][2].decode("utf-8", "replace") != rid:
        continue
    i = bd.find(b"|")
    while i > 0 and bd[i - 1] in b"|:@#Z0123456789,.":
        i -= 1
    j = bd.find(b"@Z", i)
    if j >= 0:
        toks = bd[i:j + 2].decode("ascii", "replace").split("|")

if not toks:
    print("该局没有状态帧")
    sys.exit(0)

nc = (len(toks) - 1) // 24
print("状态帧 token %d，卡数 %d\n" % (len(toks), nc))
print("%-14s %6s %6s %8s %8s" % ("映射", "非空", "命中", "重叠率", "覆盖率"))
for name, fn in MAPS:
    filled = set()
    for ci in range(nc):
        for k, t in enumerate(toks[ci * 24:(ci + 1) * 24]):
            if t == "":
                continue
            filled.add((ci + 1, fn(k)))
    hit = len(filled & need)
    print("%-14s %6d %6d %7.1f%% %7.1f%%" % (
        name, len(filled), hit,
        100.0 * hit / max(len(filled), 1), 100.0 * hit / max(len(need), 1)))
