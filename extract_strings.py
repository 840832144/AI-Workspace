"""从 global-metadata.dat 全量提取字符串并做 bingo 关键词聚类。

不依赖 IL2CPP 头解析（版本差异会踩坑），直接扫可打印字符串。
IL2CPP 会把所有类名/方法名/字段名以 null 分隔存在元数据里。
"""
import os, re, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe"
META = os.path.join(OUT, "bin", "global-metadata.dat")
raw = open(META, "rb").read()
print("metadata %.1f MB" % (len(raw) / 1e6))

# ── 提取所有可打印字符串（含 . 和 _ 的标识符优先）─────────
strs = []
for m in re.finditer(rb"[\x20-\x7e]{3,120}", raw):
    s = m.group(0).decode("ascii")
    strs.append(s)
print("可打印字符串: %d（去重前）" % len(strs))

uniq = sorted(set(strs))
print("去重后: %d" % len(uniq))

# ── 标识符（看起来像 C# 类型/成员名）──────────────────────
ident = re.compile(r"^[A-Za-z_][A-Za-z0-9_.<>`]{2,80}$")
idents = [s for s in uniq if ident.match(s)]
print("标识符形态: %d" % len(idents))

os.makedirs(os.path.join(OUT, "out"), exist_ok=True)
with open(os.path.join(OUT, "out", "meta_strings_all.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(uniq))
with open(os.path.join(OUT, "out", "meta_idents.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(idents))

# ── bingo 关键词聚类 ──────────────────────────────────────
GROUPS = {
    "bingo 本体": ["bingo"],
    "卡/票": ["card", "ticket", "book", "strip"],
    "球/叫号": ["ball", "call", "draw", "number", "sequence", "caller"],
    "标记/涂抹": ["daub", "mark", "stamp", "auto", "tap"],
    "图案/连线": ["pattern", "line", "row", "column", "diagonal", "blackout", "coverall", "fullhouse"],
    "奖金/奖池": ["prize", "payout", "win", "reward", "jackpot", "pot", "pool", "payout"],
    "房间/场次": ["room", "round", "session", "match", "lobby", "tier"],
    "下注/货币": ["bet", "stake", "coin", "cash", "credit", "currency", "buy"],
    "道具/加速": ["powerup", "power", "boost", "speed", "extra"],
    "主题/航程": ["voyage", "cruise", "ship", "port", "map", "chapter", "stage", "level", "island"],
    "收集": ["collection", "album", "sticker", "card_", "deck"],
    "玩家/钱包": ["player", "user", "wallet", "balance", "profile"],
    "网络/协议": ["api", "http", "request", "response", "server", "socket", "protobuf"],
}

print("\n=== 关键词命中统计 ===")
found = {}
for gname, keys in GROUPS.items():
    hits = []
    for s in idents:
        low = s.lower()
        for k in keys:
            if k in low:
                hits.append(s)
                break
    found[gname] = sorted(set(hits))
    print("  %-14s %5d" % (gname, len(found[gname])))

print("\n=== bingo 直接命中（全部）===")
bg = sorted({s for s in idents if "bingo" in s.lower()})
for s in bg[:60]:
    print("   " + s)

print("\n=== 核心玩法组样本（各取 12 条）===")
for g in ("卡/票", "球/叫号", "标记/涂抹", "图案/连线", "奖金/奖池", "房间/场次"):
    print("\n--- %s ---" % g)
    for s in found[g][:12]:
        print("   " + s)

with open(os.path.join(OUT, "out", "meta_keyword_hits.txt"), "w", encoding="utf-8") as fh:
    for g in GROUPS:
        fh.write("=== %s ===\n" % g)
        for s in found[g]:
            fh.write(s + "\n")
        fh.write("\n")

print("\n产出: out/meta_strings_all.txt, out/meta_idents.txt, out/meta_keyword_hits.txt")
