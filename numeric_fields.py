"""抽 bingo 数值字段 + 试打服务端 API。"""
import json, os, re, sys, urllib.error, urllib.request
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe"
ids = open(os.path.join(OUT, "out", "meta_idents.txt"), encoding="utf-8").read().splitlines()

# ── 数值字段：小驼峰 + 数值语义 ───────────────────────────
NUM = re.compile(r"^[a-z][A-Za-z0-9]{2,45}$")
DIM = re.compile(r"(price|Cost|cost|Amount|Count|Num|Rate|Ratio|Prob|Weight|Threshold|"
                 r"Limit|Max|Min|Reward|Prize|Jackpot|Multiplier|Bonus|Payout|Value|"
                 r"Level|Tier|Bet|Coin|Cash|Gem|Energy|Ticket|Card|Ball|Line|Score|"
                 r"Duration|Interval|Delay|Speed|Times|Total|Balance|Free|Extra)")
dims = sorted({s for s in ids if NUM.match(s) and DIM.search(s)})
print("=== bingo 数值维度字段（%d，前 90）===" % len(dims))
for s in dims[:90]:
    print("   " + s)
open(os.path.join(OUT, "out", "numeric_dims.txt"), "w", encoding="utf-8").write("\n".join(dims))

# ── 纯变量型字段（找玩法参数）────────────────────────────
print("\n=== 玩法参数候选（ball*/card*/round*/win*/daub* 开头）===")
PRE = re.compile(r"^(ball|card|round|win|daub|call|bingo|pattern|prize|jackpot|hall|bet|"
                 r"room|match|ticket|energy|coin|cash|gem)[A-Za-z0-9]{1,40}$")
cand = sorted({s for s in ids if PRE.match(s)})
for s in cand[:110]:
    print("   " + s)
print("   共 %d 个" % len(cand))
open(os.path.join(OUT, "out", "gameplay_params.txt"), "w", encoding="utf-8").write("\n".join(cand))

# ── 试打服务端 ────────────────────────────────────────────
UA = ("Mozilla/5.0 (Linux; Android 9; SM-G998B) AppleWebKit/537.36 "
      "Chrome/120.0.0.0 Mobile Safari/537.36")


def call(url, method="POST", data=b"", ct="application/x-protobuf", timeout=12):
    hdrs = {"User-Agent": UA, "Content-Type": ct, "Accept": "*/*",
            "User-Agent-x": "bingo-voyage/1.58.3"}
    req = urllib.request.Request(url, headers=hdrs, method=method, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()[:200]
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read()[:200]
        except Exception:
            return e.code, b""
    except Exception as e:
        return 0, str(e)[:110].encode()


print("\n=== 试打 entry.bingo.elitescastle.com（protobuf POST）===")
E = "https://entry.bingo.elitescastle.com"
PATHS = ["/pb/hall", "/hall", "/api/hall", "/v1/hall", "/pb/v1/hall", "/bingo/hall",
         "/pb", "/rpc", "/api", "/game/hall", "/hall/GetState", "/v1/pb/hall"]
for p in PATHS:
    c, b = call(E + p)
    print("  %-22s http=%-4s %s" % (p, c, b[:120].decode("latin-1", "replace")))
