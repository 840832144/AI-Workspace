"""Bingo Voyage 采集器 —— 离线结构化抽取。

把 mitmproxy 落盘的原始帧（out/bv_ws.jsonl + out/bv_bodies/*）转成可分析的表格：

    data/balls.jsonl    报号流水   {ts, round_id, seq, ball, window[]}
    data/rounds.json    每局汇总   {round_id, room, balls[], n_balls, first_ts, last_ts, card_count}
    data/daubs.jsonl    客户端 daub 上报 {ts, round_id, subtype, cells|state}
    data/reactions.jsonl 房间表情  {ts, round_id, player, emoji, robot_id}
    data/joins.jsonl    玩家入座    {ts, round_id, player, state}
    data/chat.jsonl     聊天        {ts, player, text}
    data/halls.json     房间/特性列表
    data/account.json   登录账号态（JWT/统计/货币/服务器表）

用法：
    python collector\\bv_extract.py            # 增量抽取（默认）
    python collector\\bv_extract.py --full     # 全量重建
"""
import argparse
import base64
import json
import os
import re
import sys
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bv_ws2                      # noqa: E402
from bv_proto import parse, try_str  # noqa: E402

CFG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "config.json"), encoding="utf-8"))
OUT = CFG["paths"]["out"]
DATA = CFG["paths"]["data"]
os.makedirs(DATA, exist_ok=True)


# ---------- 通用 protobuf 取值 ----------

def fields(b):
    """[(field, wiretype, value_or_len, chunk)]，容错"""
    try:
        return parse(b)
    except Exception:
        return []


def f_str(b, want):
    for fld, wt, val, ch in fields(b):
        if fld == want and wt == 2 and ch is not None:
            s = try_str(ch)
            if s is not None:
                return s
    return None


def f_varints(b, want):
    return [v for fld, wt, v, ch in fields(b) if fld == want and wt == 0]


# ---------- 各类抽取 ----------

def extract_ball(body):
    """cmd169 body -> (round_id, window:list[int])；window 右端为最新号码"""
    rid = f_str(body, 1)
    win = []
    for fld, wt, val, ch in fields(body):
        if fld == 2 and wt == 2 and ch is not None:
            win = list(ch)
            break
    return rid, win


def extract_round_action(body):
    """cmd167 C->S -> (round_id, subtype, detail)"""
    rid = f_str(body, 1)
    sub = None
    detail = None
    for fld, wt, val, ch in fields(body):
        if fld == 2 and wt == 2 and ch is not None:
            inner = fields(ch)
            for f2, w2, v2, c2 in inner:
                if f2 == 1 and w2 == 0:
                    sub = v2
                if f2 == 2 and w2 == 2:
                    s = try_str(c2) if c2 is not None else None
                    detail = s if s is not None else (c2.hex() if c2 else None)
                if f2 == 3 and w2 == 2 and c2 is not None:
                    d = {}
                    for f3, w3, v3, c3 in fields(c2):
                        if f3 is not None and w3 == 0:
                            d[f3] = v3
                    detail = d
    return rid, sub, detail


def extract_reaction(body):
    """cmd203 -> list of {round_path, player, emoji, ts, robot}"""
    out = []
    for fld, wt, val, ch in fields(body):
        if fld != 1 or wt != 2 or ch is None:
            continue
        rec = {}
        for f2, w2, v2, c2 in fields(ch):
            if f2 == 1 and w2 == 2 and c2 is not None:
                rec["round_path"] = try_str(c2)
            if f2 == 2 and w2 == 2 and c2 is not None:
                for f3, w3, v3, c3 in fields(c2):
                    if w3 != 2 or c3 is None:
                        continue
                    s = try_str(c3)
                    if f3 == 1:
                        rec["player"] = s
                    elif f3 == 2:
                        rec["emoji"] = s
                    elif f3 == 3:
                        rec["ts_ms"] = v3 if w3 == 0 else s
                    elif f3 == 5:
                        rec["robot"] = s
                    elif f3 == 3 and w3 == 0:
                        rec["ts_ms"] = v3
        if rec:
            out.append(rec)
    return out


def extract_seats(body):
    """cmd227 S->C -> {round_id, room_path, players:[{id,state}]}"""
    for fld, wt, val, ch in fields(body):
        if fld != 1 or wt != 2 or ch is None:
            continue
        r = {"players": []}
        for f2, w2, v2, c2 in fields(ch):
            if f2 == 1 and w2 == 2 and c2 is not None:
                r["round_id"] = try_str(c2)
            elif f2 == 2 and w2 == 2 and c2 is not None:
                r["room_path"] = try_str(c2)
            elif f2 == 3 and w2 == 0:
                r["flag3"] = v2
            elif f2 == 5 and w2 == 2 and c2 is not None:
                p = {}
                for f3, w3, v3, c3 in fields(c2):
                    if f3 == 1 and w3 == 2 and c3 is not None:
                        p["id"] = try_str(c3)
                    elif f3 == 2 and w3 == 0:
                        p["state"] = v3
                if p:
                    r["players"].append(p)
        return r
    return None


def harvest_strings(b, minlen=4, maxdepth=4, depth=0, out=None):
    """递归收集所有可打印字符串（用于聊天的双层嵌套）"""
    if out is None:
        out = []
    if depth > maxdepth:
        return out
    for fld, wt, val, ch in fields(b):
        if wt != 2 or ch is None:
            continue
        s = try_str(ch)
        if s is not None and len(s) >= minlen:
            out.append(s)
        else:
            harvest_strings(ch, minlen, maxdepth, depth + 1, out)
    return out


BANDS = [("B", 1, 15), ("I", 16, 30), ("N", 31, 45), ("G", 46, 60), ("O", 61, 75)]


def all_varints(b, depth=0, out=None):
    """按文档顺序收集全部 varint（递归）"""
    if out is None:
        out = []
    if depth > 8:
        return out
    for fld, wt, val, ch in fields(b):
        if fld is None:
            continue
        if wt == 0 and isinstance(val, int):
            out.append(val)
        elif wt == 2 and ch is not None:
            all_varints(ch, depth + 1, out)
    return out


def _band_ok(vals):
    """25 个值是否满足卡面签名：
    ① 每列落在自己的区间（N 列中点 = FREE 占位不校验）
    ② 每列的 5 个号码互不相同（真 bingo 卡必然列内唯一）
    """
    for c in range(5):
        col = vals[c * 5:(c + 1) * 5]
        if len(set(col)) != 5:
            return False
        for i, v in enumerate(col):
            if c == 2 and i == 2:
                continue
            lo, hi = BANDS[c][1], BANDS[c][2]
            if not (lo <= v <= hi):
                return False
    return True


def find_cards_generic(body):
    """★ 通用卡面识别：列区间 + 列内唯一 的双重签名，跨命令通用。

    注意：**不要做「卡间号码互斥」过滤** —— 同一玩家的多张卡本来就会重复号码
    （实测同一局 4 张卡共享 11/8/30/40/33/59/52/72），互斥假设是错的，会把真卡砍掉。
    签名本身（每列落在 1-15/16-30/31-45/46-60/61-75 且列内 5 个互不相同）已足够强。
    """
    vs = all_varints(body)
    n = len(vs)
    cards = []
    i = 0
    while i + 25 <= n:
        win = vs[i:i + 25]
        if _band_ok(win):
            cards.append({"slot": len(cards) + 1, "vals": win,
                          "seed": vs[i + 25] if i + 25 < n else None,
                          "grid": build_grid(win), "offset": i})
            i += 25
        else:
            i += 1
    return cards


def extract_cards(body, rid=None):
    """从任意帧体提卡面：先试规范结构（cmd166），再退回列区间签名搜索（cmd163/167 等）。"""
    cards = []
    for fld, wt, val, ch in fields(body):
        if fld == 1 and wt == 2 and ch is not None and rid is None:
            s = try_str(ch)
            if s and ".0." in s:
                rid = s
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
                if len(vals) == 25 and _band_ok(vals):
                    cards.append({"slot": len(cards) + 1, "seed": seed,
                                  "vals": vals, "grid": build_grid(vals)})
    if not cards:
        cards = find_cards_generic(body)
    for c in cards:
        c["round_id"] = rid
    return cards


def build_grid(vals):
    """25 个列序数字 -> 5x5 网格（N 列中间置 0 表示 FREE）"""
    grid = [[0] * 5 for _ in range(5)]
    i = 0
    for c, (name, lo, hi) in enumerate(BANDS):
        for r in range(5):
            if i < len(vals):
                grid[r][c] = vals[i]
            i += 1
    grid[2][2] = 0            # FREE
    return grid


def cell_order():
    """返回 [(slot_local_index, row, col)] —— 与状态串 token 顺序一致（列序，跳过 FREE）"""
    out = []
    for c in range(5):
        for r in range(5):
            if r == 2 and c == 2:
                continue
            out.append((len(out), r, c))
    return out


def extract_profiles(body):
    """cmd78 S->C: 1:{1:id, 2:name, 3:{}, 4:{1:1, 2:name, 4:num, 7:"CHARACTER_N", 10:"CC"}}
    -> [{id,name,character,country,level_num}]"""
    out = []
    for fld, wt, val, ch in fields(body):
        if fld != 1 or wt != 2 or ch is None:
            continue
        rec = {}
        for f2, w2, v2, c2 in fields(ch):
            if w2 != 2 or c2 is None:
                continue
            s2 = try_str(c2)
            if f2 == 1:
                rec["id"] = s2
            elif f2 == 2:
                rec["name"] = s2
            elif f2 == 4:
                for f3, w3, v3, c3 in fields(c2):
                    if w3 == 0 and f3 == 4:
                        rec["level_num"] = v3
                    elif w3 == 2 and c3 is not None:
                        s3 = try_str(c3)
                        if f3 == 2 and s3:
                            rec.setdefault("name", s3)
                        elif f3 == 7 and s3:
                            rec["character"] = s3
                        elif f3 == 10 and s3:
                            rec["country"] = s3
        if rec.get("id"):
            out.append(rec)
    return out


def extract_chat(body):
    """cmd216: 1:{1:{1:playerId, 2:text, 3:ts, 5:robotId}} -> [{player,text,ts_ms}]"""
    msgs = []
    for fld, wt, val, ch in fields(body):
        if wt != 2 or ch is None:
            continue
        for f2, w2, v2, c2 in fields(ch):
            if w2 != 2 or c2 is None:
                continue
            rec = {}
            for f3, w3, v3, c3 in fields(c2):
                if w3 == 2 and c3 is not None:
                    s3 = try_str(c3)
                    if f3 == 1:
                        rec["player"] = s3
                    elif f3 == 2:
                        rec["text"] = s3
                    elif f3 == 5:
                        rec["robot_or_thread"] = s3
                elif w3 == 0 and f3 == 3:
                    rec["ts_ms"] = v3
            if rec.get("text") or rec.get("player"):
                msgs.append(rec)
    return msgs


# ---------- 主流程 ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()

    recs = bv_ws2.load()
    if not recs:
        print("没有 WS 帧。先跑采集：collector\\bv_collect.py start")
        return 1
    print("读入 %d 帧" % len(recs))

    balls = open(os.path.join(DATA, "balls.jsonl"), "w", encoding="utf-8")
    daubs = open(os.path.join(DATA, "daubs.jsonl"), "w", encoding="utf-8")
    reacts = open(os.path.join(DATA, "reactions.jsonl"), "w", encoding="utf-8")
    joins = open(os.path.join(DATA, "joins.jsonl"), "w", encoding="utf-8")
    chats = open(os.path.join(DATA, "chat.jsonl"), "w", encoding="utf-8")
    profs = open(os.path.join(DATA, "profiles.jsonl"), "w", encoding="utf-8")

    rounds = OrderedDict()
    halls = set()
    n_ball = n_daub = n_react = n_join = n_chat = n_prof = n_card = 0
    seen_cards = set()
    _votes = {}
    _cardbuf = {}
    last_ball = {}
    seen_ball_seq = {}

    for r in recs:
        f = r["f"]
        if not f.get("ok"):
            continue
        cmd, body, ts = f["cmd"], f["body"], r["ts"]

        if cmd == 169 and r["dir"] == "S->C":
            rid, win = extract_ball(body)
            if not win:
                continue
            key = rid or ""
            prev = last_ball.get(key)
            last_ball[key] = win[-1]
            # 窗口右端 = 最新号；只有右端变化才算新号（窗口收缩时不产生新号）
            if prev is None or win[-1] != prev:
                rec = {"ts": ts, "round_id": rid, "ball": win[-1], "window": win}
                balls.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_ball += 1
                rd = rounds.setdefault(rid, {"round_id": rid, "balls": [],
                                             "first_ts": ts, "last_ts": ts})
                rd["balls"].append(win[-1])
                rd["last_ts"] = ts

        elif cmd == 167 and r["dir"] == "C->S":
            rid, sub, detail = extract_round_action(body)
            daubs.write(json.dumps(
                {"ts": ts, "round_id": rid, "subtype": sub, "detail": detail},
                ensure_ascii=False) + "\n")
            n_daub += 1

        elif cmd == 203 and r["dir"] == "S->C":
            for x in extract_reaction(body):
                x["ts"] = ts
                reacts.write(json.dumps(x, ensure_ascii=False) + "\n")
                n_react += 1

        elif cmd == 227 and r["dir"] == "S->C":
            s = extract_seats(body)
            if s:
                s["ts"] = ts
                joins.write(json.dumps(s, ensure_ascii=False) + "\n")
                n_join += 1

        elif cmd == 216 and r["dir"] == "S->C":
            for m in extract_chat(body):
                m["ts"] = ts
                chats.write(json.dumps(m, ensure_ascii=False) + "\n")
                n_chat += 1

        elif cmd in (163, 166, 167) and r["dir"] == "S->C":
            got = extract_cards(body)
            if got:
                # 跨帧多数投票：真卡会在多个帧里稳定出现，误报不会
                _rid0 = None
                for sv in harvest_strings(body, 20, 6):
                    if sv.startswith("BINGO_HALL") and sv.count(".") >= 3 \
                            and sv.rsplit(".", 1)[-1].isdigit():
                        _rid0 = sv
                        break
                _fp = tuple((c["slot"], tuple(c["vals"])) for c in got)
                _votes.setdefault(_rid0, {})
                _votes[_rid0][_fp] = _votes[_rid0].get(_fp, 0) + 1
                _cardbuf.setdefault(_rid0, got)
                # roundId 可能嵌在任意深度，全局找 "BINGO_HALL...-0-... . <n>" 形态
                rid_c = None
                for sv in harvest_strings(body, 20, 6):
                    if sv.startswith("BINGO_HALL") and sv.count(".") >= 3 \
                            and sv.rsplit(".", 1)[-1].isdigit():
                        rid_c = sv
                        break
                for cd in got:
                    rk = cd.get("round_id") or rid_c
                    key = (rk, tuple(cd["vals"]))
                    if key in seen_cards:
                        continue
                    seen_cards.add(key)
                    cd["round_id"] = rk
                    cd["ts"] = ts
                    cd["source_cmd"] = cmd

        elif cmd == 78 and r["dir"] == "S->C":
            for p in extract_profiles(body):
                p["ts"] = ts
                profs.write(json.dumps(p, ensure_ascii=False) + "\n")
                n_prof += 1

        elif cmd == 179:
            # S->C: 2:{1:"FEATURE_HALL_*"}   C->S: 1:"..."
            for s in harvest_strings(body, 8):
                if s.startswith(("FEATURE_HALL", "BINGO_HALL")):
                    halls.add(s)

    for fh in (balls, daubs, reacts, joins, chats, profs):
        fh.close()

    # --- 卡面跨帧多数投票：每局只保留出现次数最多的那一组 ---
    n_card = 0
    with open(os.path.join(DATA, "cards.jsonl"), "w", encoding="utf-8") as cf:
        for rid0, votes in _votes.items():
            best_fp, best_n = max(votes.items(), key=lambda kv: kv[1])
            winner = _cardbuf.get(rid0)
            if winner is None:
                continue
            # 只保留与赢家指纹一致的那一组
            for c in winner:
                key = tuple(c["vals"])
                if key not in [k[1] for k in best_fp]:
                    continue
                c2 = dict(c)
                c2["round_id"] = rid0
                c2["votes"] = best_n
                c2["n_frames"] = sum(votes.values())
                cf.write(json.dumps(c2, ensure_ascii=False) + "\n")
                n_card += 1
    os.replace(os.path.join(DATA, "cards.jsonl.tmp"), os.path.join(DATA, "cards.jsonl")) \
        if False else None

    with open(os.path.join(DATA, "rounds.json"), "w", encoding="utf-8") as f:
        json.dump(list(rounds.values()), f, ensure_ascii=False, indent=1)
    with open(os.path.join(DATA, "halls.json"), "w", encoding="utf-8") as f:
        json.dump(sorted(halls), f, ensure_ascii=False, indent=1)

    print("""
=== 抽取完成 -> %s ===
报号流水 balls.jsonl     %d 条
客户端 daub daubs.jsonl  %d 条
房间表情 reactions.jsonl %d 条
玩家入座 joins.jsonl     %d 条
聊天 chat.jsonl          %d 条
机器人档案 profiles.jsonl %d 条
卡面明细 cards.jsonl      %d 张
回合汇总 rounds.json     %d 局
房间/特性 halls.json     %d 个
""" % (DATA, n_ball, n_daub, n_react, n_join, n_chat, n_prof, n_card,
       len(rounds), len(halls)))

    if rounds:
        for rid, rd in list(rounds.items())[:5]:
            print("  %-58s %3d 个号  %s -> %s" % (
                (rid or "(无)")[:58], len(rd["balls"]), rd["first_ts"][11:], rd["last_ts"][11:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
