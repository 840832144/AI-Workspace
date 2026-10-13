"""抽取 bingo 玩法相关的 API 与数据结构，按玩法环节归类。"""
import os, re, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe"
ids = open(os.path.join(OUT, "out", "meta_idents.txt"), encoding="utf-8").read().splitlines()

RR = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*?)(Req|Resp|Request|Response)$")
GROUPS = {
    "① 登录/鉴权": r"(Auth|Login|Session|Account|Device|Guest|Token)",
    "② 大厅/房间": r"(Hall|Room|Lobby|Enter|Leave|Seat|Match)",
    "③ 买卡/开局": r"(BuyCard|CardBuy|PurchaseCard|StartGame|GameStart|Book|Ticket|Deal)",
    "④ 叫号": r"(CallBall|Ball|Draw|BingoBall|NextBall|CallNum)",
    "⑤ 涂抹/标记": r"(Daub|Mark|Stamp|AutoDaub)",
    "⑥ Bingo/中奖": r"(Bingo|Win|Line|Pattern|Claim|Settle|Reward|Payout|Prize)",
    "⑦ 道具/加速": r"(PowerUp|Powerup|Buff|Boost|Prop|Item|Consume)",
    "⑧ 钱包/货币": r"(Coin|Cash|Gem|Energy|Wallet|Balance|Currency|Charge|Pay|Order|Shop|Store)",
    "⑨ 活动/任务": r"(Task|Mission|Event|Activity|Season|Pass|Rank|Leaderboard|Club|Team|Race)",
    "⑩ 收集/相册": r"(Album|Collection|Card_|Sticker|Deck)",
}

buckets = defaultdict(list)
for s in ids:
    m = RR.match(s)
    if not m:
        continue
    base = m.group(1)
    for gname, pat in GROUPS.items():
        if re.search(pat, base, re.I):
            buckets[gname].append(base)
            break

total = 0
for g in GROUPS:
    b = sorted(set(buckets[g]))
    total += len(b)
    print("\n=== %s （%d）===" % (g, len(b)))
    for x in b[:45]:
        print("   " + x)
    if len(b) > 45:
        print("   ... 另 %d 个" % (len(b) - 45))

print("\n=== 合计 %d 个 API 基名 ===" % total)

with open(os.path.join(OUT, "out", "api_by_group.txt"), "w", encoding="utf-8") as fh:
    for g in GROUPS:
        fh.write("=== %s ===\n" % g)
        for x in sorted(set(buckets[g])):
            fh.write(x + "\n")
        fh.write("\n")
print("产出: out/api_by_group.txt")
