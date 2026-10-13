"""Bingo Voyage 数值拆解报告生成器。

从 data/ 的结构化数据生成 Markdown 报告：
    data/BINGO_VOYAGE_NUMBERS.md

用法：
    python collector\\bv_report.py
"""
import base64
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from collector import bv_extract as EX  # noqa: E402

CFG = EX.CFG
DATA = CFG["paths"]["data"]
OUT = CFG["paths"]["out"]


def jl(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def jf(name, default=None):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return default
    return json.load(open(p, encoding="utf-8"))


def bet_table():
    """从 cmd 202 响应里取 BET_*_INFLATION 表（HTTP 或 WS 都找）"""
    import bv_ws2
    from bv_proto import parse, try_str
    found = {}
    recs = bv_ws2.load()
    for r in recs:
        f = r["f"]
        if not f.get("ok") or f["cmd"] != 202 or r["dir"] != "S->C":
            continue
        if not f["body"]:
            continue
        name = None
        rows = []
        for fld, wt, val, ch in parse(f["body"]):
            if wt != 2 or ch is None:
                continue
            for f2, w2, v2, c2 in parse(ch):
                if w2 == 2 and c2 is not None:
                    s = try_str(c2)
                    if s and s.endswith("_INFLATION"):
                        name = s
                    else:
                        d = {}
                        for f3, w3, v3, c3 in parse(c2):
                            if f3 is not None and w3 == 0:
                                d[f3] = v3
                        if d:
                            rows.append(d)
        if name and rows and name not in found:
            found[name] = rows
    return found


def account():
    """从 HTTP cmd 101 响应取账号态（HTTP 与 WS 用同一套 9 字节头 + varint len + topic）"""
    p = os.path.join(OUT, "bv_flows.jsonl")
    if not os.path.exists(p):
        return None
    import bv_ws2
    from bv_proto import parse, try_str
    cands = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if "bingo2.superbgame.net" not in r["host"] or r["method"] != "POST":
            continue
        if not r["resp"].get("b64"):
            continue
        fr = bv_ws2.parse_frame(base64.b64decode(r["resp"]["b64"]))
        if not fr.get("ok") or fr["cmd"] != 101:
            continue
        body = fr["body"]
        info = {"jwt_len": None, "stats": [], "server_list": None,
                "session_key": None, "name": None, "player_id": None,
                "country": None, "outfits": []}
        for fld, wt, val, ch in parse(body):
            if wt != 2 or ch is None:
                continue
            s = try_str(ch)
            if fld == 1 and s:
                info["jwt_len"] = len(s)
            elif fld == 3 and s:
                info["server_list"] = s
            elif fld == 4 and s:
                info["session_key"] = s
            elif fld == 2:
                for f2, w2, v2, c2 in parse(ch):
                    if f2 != 4 or w2 != 2 or c2 is None:
                        continue
                    for f3, w3, v3, c3 in parse(c2):
                        if w3 == 2 and c3 is not None:
                            s3 = try_str(c3)
                            if f3 == 1:
                                info["player_id"] = s3
                            elif f3 == 2:
                                info["name"] = s3
                            elif f3 == 10:
                                info["country"] = s3
                            elif f3 == 24 and s3:
                                info["outfits"].append(s3)
                            elif f3 == 21:
                                kv = {}
                                for f4, w4, v4, c4 in parse(c3):
                                    if w4 == 2 and c4 is not None:
                                        kv[f4] = try_str(c4)
                                    elif w4 == 0:
                                        kv[f4] = v4
                                if 1 in kv:
                                    info["stats"].append((kv[1], kv.get(2)))
                        elif w3 == 0:
                            pass
        if info["stats"] or info["name"]:
            cands.append(info)
    if not cands:
        return None
    # 取统计最全的一条（登录/重连会返回不同粒度的账号态）
    return max(cands, key=lambda x: (len(x["stats"]), x.get("jwt_len") or 0))


def main():
    balls = jl("balls.jsonl")
    daubs = jl("daubs.jsonl")
    reacts = jl("reactions.jsonl")
    joins = jl("joins.jsonl")
    chats = jl("chat.jsonl")
    rounds = jf("rounds.json", [])
    halls = jf("halls.json", [])

    L = []
    A = L.append

    A("# Bingo Voyage 数值拆解\n")
    A("> 由 `collector/bv_report.py` 从 `data/` 自动生成，数据源为 MITM 抓到的真实协议帧。\n")

    # --- 报号 ---
    A("\n## 1. 报号（cmd 169）\n")
    A("| 项 | 值 |")
    A("|---|---|")
    if balls:
        freq = Counter(b["ball"] for b in balls)
        A("| 抓到的报号总数 | %d |" % len(balls))
        A("| 号码值域 | %d – %d |" % (min(freq), max(freq)))
        A("| 不同号码数 | %d / 75 |" % len(freq))
        rounds_done = [r for r in rounds if len(r["balls"]) > 5]
        if rounds_done:
            lens = sorted(len(r["balls"]) for r in rounds_done)
            A("| 单局号数（观测） | 中位 %d，最少 %d，最多 %d |" % (
                lens[len(lens) // 2], lens[0], lens[-1]))
        A("| 报文节奏 | 5 秒/号（tick 时间戳精确间隔） |")
        A("| 滑动窗口长度 | 5（右端为最新号） |")
        A("| 单局理论号数 | 75（1–75 无放回） |")
        A("| 单局理论时长 | ≈6 分 15 秒（75 × 5s） |")
        dup = [n for n, c in freq.items() if c > 1]
        A("| 跨局重复的号码 | %d 个（同局内不重复） |" % len(dup))

        A("\n### 号码出现次数分布（%d 个号样本）\n" % len(balls))
        A("| 号 | 次数 | 号 | 次数 | 号 | 次数 | 号 | 次数 | 号 | 次数 |")
        A("|---|---|---|---|---|---|---|---|---|---|")
        grid = []
        for n in range(1, 76):
            grid.append((n, freq.get(n, 0)))
        for i in range(0, 75, 5):
            row = grid[i:i + 5]
            A("| " + " | ".join("%d | %d" % (n, c) for n, c in row) + " |")
        # 列区间分布
        bands = {"B 1-15": (1, 15), "I 16-30": (16, 30), "N 31-45": (31, 45),
                 "G 46-60": (46, 60), "O 61-75": (61, 75)}
        A("\n### 列区间分布\n")
        A("| 列 | 区间 | 抓到的号数 |")
        A("|---|---|---|")
        for k, (lo, hi) in bands.items():
            A("| %s | %d–%d | %d |" % (k[0], lo, hi, sum(c for n, c in freq.items() if lo <= n <= hi)))

    # --- 回合 ---
    A("\n## 2. 回合（roundId = `HALL.<hallIdx>.<roomId>.<roundNo>`）\n")
    A("| # | roundId | 号数 | 起 | 止 |")
    A("|---|---|---|---|---|")
    for i, r in enumerate(sorted(rounds, key=lambda x: -(len(x["balls"])))[:20], 1):
        A("| %d | `%s` | %d | %s | %s |" % (
            i, (r["round_id"] or "")[:56], len(r["balls"]),
            r["first_ts"][11:], r["last_ts"][11:]))

    # --- daub ---
    A("\n## 3. 客户端 daub / 中奖判定上报（cmd 167）\n")
    if daubs:
        subs = Counter(d["subtype"] for d in daubs)
        A("| subtype | 次数 | 含义 |")
        A("|---|---|---|")
        for s, c in sorted(subs.items(), key=lambda kv: -kv[1]):
            meaning = {1: "单格 daub 上报 `2:{1:N, 2:M}`",
                       9: "整盘状态串上报 `2:{1:9, 2:'<150 字符>'}`"}.get(s, "未定")
            A("| %s | %d | %s |" % (s, c, meaning))
        A("\n**状态串结构（已拆解）**：`|` 分隔 → 97 个 token；`@` 为**卡片边界标记**，"
          "每隔 **24** 个 token 出现一次（索引 24 / 48 / 72 / 96）→ **4 张卡 × 24 token**。"
          "非空 token 即已 daub 的格子，取值形如 `1::` / `:2:` / `:8:` / `@#`。\n")
        A("非空 token 样本（round `.8`）：")
        A("```")
        idx = [d["detail"] for d in daubs if d["subtype"] == 9 and isinstance(d["detail"], str)]
        if idx:
            s = max(idx, key=len)
            toks = s.split("|")
            A("串长=%d, token=%d" % (len(s), len(toks)))
            for i, t in enumerate(toks):
                if t:
                    A("  [%2d] %r" % (i, t))
        A("```")

    # --- 卡面 ---
    A("\n## 4b. 卡面下发（cmd 166）★\n")
    cards = jl("cards.jsonl")
    if cards:
        A("**`cmd 166` = 买卡 / 入场请求**，格式：\n")
        A("```")
        A("C->S: {1: \"BET_NP_SYMBOL_1_INFLATION\", 2: <卡片数>, 5: 1}")
        A("S->C: {1: roundId, 2: [ {1: seed(64bit), 2: {1: n} × 25} ... ]}   # 每张卡一条")
        A("```")
        A("\n每张卡下发 **25 个数字，按列序 `B5 → I5 → N5 → G5 → O5`**；")
        A("**N 列第 3 个（下标 12）是占位数字，客户端渲染为 `FREE`**。")
        A("→ 这也解释了 cmd 167 状态串的 **96 token = 4 卡 × 24 可见格**（25 − 1 FREE），顺序同列序。\n")
        from collections import OrderedDict
        rounds_seen = OrderedDict()
        for c in cards:
            rounds_seen.setdefault(c["round_id"], []).append(c)
        for rid, cs in list(rounds_seen.items())[:3]:
            A("\n### `%s`（%d 张卡）\n" % (rid, len(cs)))
            for c in cs:
                A("**卡 %d**　seed=`%s`" % (c["slot"], c["seed"]))
                A("```")
                A("   B    I    N    G    O")
                for row in c["grid"]:
                    A("  " + " ".join("FREE" if v == 0 else "%4d" % v for v in row))
                A("```")
                A("列序原始值：`%s`\n" % c["vals"])

    # --- 房间 ---
    A("\n## 4. 房间 / 大厅\n")
    for h in halls:
        A("- `%s`" % h)

    # --- 下注表 ---
    A("\n## 5. 下注档位表（cmd 202）\n")
    bt = bet_table()
    if bt:
        for name, rows in bt.items():
            A("**`%s`**\n" % name)
            A("| 档序 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |")
            A("|---|---|---|---|---|---|---|---|")
            keys = sorted({k for r in rows for k in r})
            for k in keys:
                A("| field %d | %s |" % (k, " | ".join(str(r.get(k, "")) for r in rows)))
            A("")
        A("> 实测：field 1 = **下注档位**（1/2/3/5/10/15/20），"
          "field 3 = **该档允许的最大卡片数**（1/2/3/4/5/5/5）。")
        A("> 配套符号名 `BET_NP_SYMBOL_1` … `BET_NP_SYMBOL_10`。\n")
    else:
        A("(未从当前抓包中解出 BET_*_INFLATION 表)\n")

    # --- 玩家构成 ---
    A("\n## 6. 房间玩家构成\n")
    ids = Counter()
    for j in joins:
        for p in j.get("players", []):
            if p.get("id"):
                ids[p["id"]] += 1
    for c in chats:
        if c.get("player"):
            ids[c["player"]] += 0
        if c.get("robot_or_thread"):
            ids[c["robot_or_thread"]] += 0
    robots = [i for i in ids if i.startswith("robot-user-")]
    humans = [i for i in ids if i.startswith("3Kb")]
    A("| 类 | 数量 |")
    A("|---|---|")
    A("| 真实玩家 uid（`3Kb…`，27 字符） | %d |" % len(humans))
    A("| 机器人（`robot-user-<n>`） | %d |" % len(robots))
    if robots and humans:
        A("| 机器人占比 | %.0f%% |" % (100.0 * len(robots) / (len(robots) + len(humans))))
    A("\n> 机器人与真人**混编在同一房间**；`cmd 227` 的入座记录里两者都会出现。\n")

    # --- 机器人阵容 ---
    A("\n## 6b. 机器人阵容（cmd 78 档案查询）\n")
    profs = jl("profiles.jsonl")
    if profs:
        bots = [p for p in profs if (p.get("id") or "").startswith("robot-user-")]
        humans = [p for p in profs if (p.get("id") or "").startswith("3Kb")]
        A("| 类 | 档案数 | 命名规律 |")
        A("|---|---|---|")
        A("| 机器人 `robot-user-*` | %d | **人类化昵称**（Jakub / werty / Asheley …）+ 角色皮肤 + 国家码 |" % len(bots))
        A("| 真人 `3Kb…` | %d | 多为**自动数字名**（如 `650832836`） |" % len(humans))
        lv_b = [p.get("level_num") for p in bots if p.get("level_num")]
        lv_h = [p.get("level_num") for p in humans if p.get("level_num")]
        if lv_b:
            A("| 机器人等级 | 中位 %d，范围 %d–%d |" % (
                sorted(lv_b)[len(lv_b) // 2], min(lv_b), max(lv_b)))
            A("| 真人等级 | 中位 %d，范围 %d–%d |" % (
                sorted(lv_h)[len(lv_h) // 2] if lv_h else 0,
                min(lv_h) if lv_h else 0, max(lv_h) if lv_h else 0))
        cc = Counter(p.get("country") for p in profs if p.get("country"))
        if cc:
            A("\n**国家码分布**：%s\n" % ", ".join("%s×%d" % kv for kv in cc.most_common(10)))
        ch = Counter(p.get("character") for p in bots if p.get("character"))
        if ch:
            A("**机器人角色皮肤**：%s\n" % ", ".join("%s×%d" % kv for kv in ch.most_common(10)))
        A("**机器人样本**\n")
        A("| id | 昵称 | 等级 | 角色 | 国家 |")
        A("|---|---|---|---|---|")
        for p in bots[:12]:
            A("| `%s` | %s | %s | %s | %s |" % (
                p.get("id"), p.get("name"), p.get("level_num"),
                p.get("character"), p.get("country")))

    # --- 表情/聊天 ---
    A("\n## 7. 房间社交\n")
    if reacts:
        em = Counter(r.get("emoji") for r in reacts if r.get("emoji"))
        A("**表情/快捷语（cmd 203）** 共 %d 条\n" % len(reacts))
        A("| 表情 | 次数 |")
        A("|---|---|")
        for e, c in em.most_common():
            A("| `%s` | %d |" % (e, c))
    if chats:
        A("\n**聊天（cmd 216）** 共 %d 条\n" % len(chats))
        ver = Counter()
        for c in chats:
            m = re.match(r"^v(\d+)", (c.get("text") or "").strip())
            if m:
                ver["v" + m.group(1)] += 1
        A("| 项 | 值 |")
        A("|---|---|")
        A("| 带 `vNNN` 版本前缀的条数 | %d |" % sum(ver.values()))
        if ver:
            A("| 出现最多的版本号 | %s |" % ", ".join("%s×%d" % kv for kv in ver.most_common(5)))
        A("\n聊天样本：")
        A("```")
        for c in chats[:12]:
            A("  %s  %s" % (c.get("player", "?")[:27], (c.get("text") or "")[:60]))
        A("```")

    # --- 账号 ---
    A("\n## 8. 账号态（HTTP cmd 101 登录响应）\n")
    acc = account()
    if acc:
        A("| 项 | 值 |")
        A("|---|---|")
        A("| 昵称 | `%s` |" % acc.get("name"))
        A("| playerId | `%s` |" % acc.get("player_id"))
        A("| 国家 | %s |" % acc.get("country"))
        A("| JWT 长度 | %s |" % acc.get("jwt_len"))
        A("| 会话 key | `%s` |" % acc.get("session_key"))
        A("\n**统计键值对（服务端真实计数）**\n")
        A("| key | value |")
        A("|---|---|")
        for k, v in acc.get("stats", []):
            A("| `%s` | %s |" % (k, v))
        A("\n**装扮**：%s\n" % " / ".join("`%s`" % x for x in acc.get("outfits", [])))
        if acc.get("server_list"):
            A("**服务器地址表**\n")
            A("```json")
            A(json.dumps(json.loads(acc["server_list"]), ensure_ascii=False, indent=1))
            A("```")
    else:
        A("(未从当前抓包中解出)\n")

    # --- 帧统计 ---
    A("\n## 9. 帧统计\n")
    import bv_ws2
    recs = bv_ws2.load()
    cc = Counter((r["f"]["cmd"], r["dir"]) for r in recs if r["f"].get("ok"))
    A("| cmd | 方向 | 帧数 |")
    A("|---|---|---|")
    for (cmd, d), n in sorted(cc.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        A("| %d | %s | %d |" % (cmd, d, n))
    A("\n总帧数：%d\n" % len(recs))

    out = os.path.join(DATA, "BINGO_VOYAGE_NUMBERS.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("已生成 %s（%d 行）" % (out, len(L)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
