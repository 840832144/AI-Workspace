# -*- coding: utf-8 -*-
"""用协议数据校准 cmd167 subtype9 状态串，不依赖任何截图。

两个独立数据源对齐：
  A) C->S subtype1  = 明确的 daub 事件 {f3.f1: 格下标, f3.f2: 卡号-1}
  B) C->S subtype9  = 97/49 token 状态串

subtype9 的 token 布局：每张卡 24 个 token（25 格跳过 FREE），
token k 对应格下标 = k (k<12) 或 k+1 (k>=12)。

输出：每个 token 值类型出现在哪些格上，以及这些格是否恰好等于 subtype1 报过的格。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
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
    """极简 protobuf 字段遍历：返回 [(fld, wt, val)]"""
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


def tok2cell(k):
    return k if k < 12 else k + 1


daubs, states = [], []
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
    rid = None
    if fs and fs[0][0] == 1 and fs[0][1] == 2:
        rid = fs[0][2].decode("utf-8", "replace")
    sub = None
    for f, w, v in fs[1:]:
        if f == 2 and w == 2:
            inner = fields(v)
            if inner and inner[0][1] == 0:
                sub = inner[0][2]
                if sub == 1:
                    for f2, w2, v2 in inner:
                        if f2 == 3 and w2 == 2:
                            i3 = fields(v2)
                            d = {x[0]: x[2] for x in i3 if x[1] == 0}
                            if 1 in d:
                                daubs.append((rid, d.get(2), d.get(1)))
    if b"|" in bd and b"@" in bd:
        i = bd.find(b"|")
        while i > 0 and bd[i - 1] in b"|:@#Z0123456789,.":
            i -= 1
        j = bd.find(b"@Z", i)
        tok = bd[i:j + 2] if j >= 0 else bd[i:]
        states.append((r["ts"], rid, tok))

print("subtype1 daub 事件 %d 条，subtype9 状态帧 %d 条\n" % (len(daubs), len(states)))

by_round = {}
for rid, card, cell in daubs:
    if card is None or cell is None:
        continue
    by_round.setdefault(rid, set()).add((card, cell))

for ts, rid, tok in states[-3:]:
    s = tok.decode("ascii", "replace")
    parts = s.split("|")
    ncard = (len(parts) - 1) // 24
    print("=== %s rid=%s  卡数=%d token=%d ===" % (ts, (rid or "")[-20:], ncard, len(parts)))
    ds = by_round.get(rid, set())
    print("  本局 subtype1 报过的格: %s" % sorted(ds)[:12])
    # 统计 token 值类型 -> 对应的格
    kinds = {}
    for c in range(max(ncard, 1)):
        seg = parts[c * 24:(c + 1) * 24]
        for k, t in enumerate(seg):
            if t == "":
                continue
            t2 = t.split("@")[0].split("#")[0][-4:]
            if not t2:
                continue
            kinds.setdefault(t2, []).append((c, tok2cell(k)))
    for kind, cells in sorted(kinds.items(), key=lambda x: -len(x[1])):
        hit = sum(1 for cc in cells if cc in ds)
        print("   token %-5s 出现 %2d 次，其中 %2d 次与 subtype1 报的格重合"
              % (kind, len(cells), hit))
    print()

# 反查：把 token 位置直接画成 24 位图（0=空 1=1:: 2=其它）
for ts, rid, tok in states[-1:]:
    parts = tok.decode("ascii", "replace").split("|")
    print("=== 最后帧逐卡位图（0=空, 1=1::, X=其它）===")
    for c in range((len(parts) - 1) // 24):
        seg = parts[c * 24:(c + 1) * 24]
        row = "".join("0" if t == "" else ("1" if t == "1::" else "X") for t in seg)
        print("  卡%d %s" % (c + 1, row))
