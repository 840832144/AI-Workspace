"""从类型名里还原 protobuf API 面与 bingo 数据结构。"""
import os, re, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe"
ids = open(os.path.join(OUT, "out", "meta_idents.txt"), encoding="utf-8").read().splitlines()
print("标识符池: %d" % len(ids))

REQ = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*?(?:Request|Req|Resp|Response|Reply|Ack|Notify|Message|Cmd|Query)$")

req = sorted({s for s in ids if REQ.match(s) and len(s) < 70})
print("\n=== 请求/响应类（API 面）共 %d ===" % len(req))
for s in req[:120]:
    print("   " + s)

# ── bingo 核心数据结构 ────────────────────────────────────
print("\n=== bingo 核心数据类（Card/Ball/Daub/Pattern/Prize/Room/Round）===")
CORE = re.compile(r"^(?:[A-Za-z0-9_]*?)(BingoCard|BingoBall|CalledBall|Daub|BingoPattern|"
                  r"BingoRound|BingoRoom|BingoHall|BingoPrize|BingoReward|BingoWin|"
                  r"BingoGrid|BingoCell|BingoNumber|CardGrid|CardCell)[A-Za-z0-9_]*$")
core = sorted({s for s in ids if CORE.match(s)})
for s in core:
    print("   " + s)

# ── 数值/配置字段（找可挖的数值维度）──────────────────────
print("\n=== 数值维度字段名（赔率/价格/数量/概率/阈值）===")
NUM = re.compile(r"^[a-z][A-Za-z0-9_]{1,50}$")
DIM = re.compile(r"(price|cost|amount|count|rate|ratio|prob|weight|threshold|limit|max|min|"
                 r"reward|prize|jackpot|multiplier|bonus|payout|value|num|total|level|tier|"
                 r"bet|coin|cash|gem|energy|ticket|card)")
dims = sorted({s for s in ids if NUM.match(s) and DIM.search(s)})
print("   共 %d 个，展示前 100：" % len(dims))
for s in dims[:100]:
    print("   " + s)

# ── 落盘 ──────────────────────────────────────────────────
os.makedirs(os.path.join(OUT, "out"), exist_ok=True)
open(os.path.join(OUT, "out", "api_reqresp.txt"), "w", encoding="utf-8").write("\n".join(req))
open(os.path.join(OUT, "out", "bingo_core_types.txt"), "w", encoding="utf-8").write("\n".join(core))
open(os.path.join(OUT, "out", "numeric_dims.txt"), "w", encoding="utf-8").write("\n".join(dims))
print("\n产出: api_reqresp.txt / bingo_core_types.txt / numeric_dims.txt")
