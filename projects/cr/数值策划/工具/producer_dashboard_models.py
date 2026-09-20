"""TASK-0036 制作人模型。只接受固定导出数据；结果是受控分析，不写配置。

随机模型固定seed，并保留逐样本计数/完成时间。未完成样本不当成完成成本；
卡册的日Spin和UID权重分层是显式敏感性情景，不是实际玩家分布。
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime
from functools import lru_cache
import math
import random
from typing import Any

SEED = 9227013


def weighted(rng: random.Random, rows: list, weights: list, inclusive_first: bool = False) -> Any:
    weights = [max(0, int(w or 0)) for w in weights]
    if inclusive_first and weights:
        weights[0] += 1  # r7013 CardCollectSvc.GetRandomWeight
    total = sum(weights)
    if not rows or not total:
        return None
    n = rng.randrange(total)
    for r, w in zip(rows, weights):
        if n < w:
            return r
        n -= w
    raise AssertionError('weight mass')


def max_unlocked(rows: list[dict], level: int, highroller: int = 0) -> dict:
    eligible = [r for r in rows if r['highroller'] == highroller and r['level'] <= level]
    return max(eligible, key=lambda r: (r['betlevel'], r['level']))


def lucky_simulation(raw: dict, samples: int = 1000) -> tuple[list[dict], dict]:
    """按User闭合规则：特殊格免费进入下一内圈，普通格消失，再返回。

    使用当前权重；临时内圈仍可递归特殊格，特殊格不计forceTurn。
    圈清空普通格后转圈；所有普通格清空为本轮终点。
    与r7013代码中自动内圈仍扣费的差异另列，不覆盖已批准分析口径。
    """
    rng = random.Random(SEED)
    rows = raw['StrikeLucky']
    result, checks = [], Counter()
    for sample in range(samples):
        for rd in raw['StrikeLuckyRound']:
            grids = [r for r in rows if r['round'] == rd['round']]
            by_ring = {c: [g for g in grids if g['inout'] == c] for c in (1,2,3)}
            selected, paid, special, paid_special = set(), Counter(), Counter(), Counter()
            counts = Counter()

            def draw(circle: int, is_paid: bool) -> dict:
                ordinary_inner = [g for g in by_ring.get(circle+1, []) if g['itemId'] != 215006 and g['gridId'] not in selected]
                candidates = [g for g in by_ring[circle] if (g['itemId'] == 215006 and ordinary_inner) or (g['itemId'] != 215006 and g['gridId'] not in selected)]
                assert candidates
                if is_paid:
                    paid[circle] += 1
                due = [g for g in candidates if is_paid and g['itemId'] != 215006 and (g['forceTurn'] or 0)>0 and paid[circle]>=g['forceTurn']]
                hit = min(due,key=lambda g:(g['forceTurn'],g['gridId'])) if due else weighted(rng,candidates,[g['hitWeight'] for g in candidates])
                if hit['itemId']==215006:
                    special[circle]+=1
                    if is_paid:paid_special[circle]+=1
                    before=set(selected)
                    draw(circle+1,False)
                    assert len(selected)>len(before)
                    checks['inner_removal']+=1
                else:
                    assert hit['gridId'] not in selected
                    selected.add(hit['gridId']); counts[hit['gridId']]+=1
                    if due:checks['ordinary_guarantee']+=1
                return hit

            for circle in (1,2,3):
                while any(g['itemId']!=215006 and g['gridId'] not in selected for g in by_ring[circle]):
                    draw(circle,True)
                    assert sum(paid.values()) < 500
            assert len(selected)==sum(g['itemId']!=215006 for g in grids)
            result.append({'sample':sample,'round':rd['round'],'paid':[paid[c] for c in (1,2,3)],'special':[special[c] for c in (1,2,3)],'paid_special':[paid_special[c] for c in (1,2,3)],'counts':dict(counts)})
    return result,dict(checks)


def snack_simulation(raw: dict, samples: int = 400) -> tuple[list[dict], dict]:
    """自然渠道，不购买幸运值；User覆盖：初始/重置均满20盒、初始道具0。
    保留当前首收集保底、首轮强制重置和权重归一化；JP完成清零可重复。
    输出各Pass阶段/首个Grand完成的样本及20/50/100/200次开盒截面。
    """
    rng=random.Random(SEED+1)
    jackpots=sorted([r for r in raw['QuestJackpotCfg'] if r['Type']==4],key=lambda r:r['Id'])
    thresholds=[];total=0
    for r in sorted([r for r in raw['SnackPassReward'] if r['category']==0],key=lambda r:r['levelId']):
        total+=r['LevelExp'];thresholds.append((r['levelId'],total))
    result=[];checks=Counter()
    for sample in range(samples):
        boxes=20;luck=0;held=[0]*4;won=Counter();coins=Counter();ticket_rows=Counter()
        ticket=0;dropped=False;reset=False;recorded=set()
        for used in range(1,20001):
            luck += next((r['addLuck'] for r in raw['SnackAddLuck'] if r['usedItemCountMin']<=used<=r['usedItemCountMax']),0)
            cfg=max((r for r in raw['SnackDropItemCfg'] if r['boxNum']==boxes and r['luck']<=luck),key=lambda r:r['luck'])
            weights=[cfg['resetItemProb'],cfg['passItemProb'] if ticket<total else 0,cfg['chipItemProb']]
            weights += [cfg[f'jackpot{i+1}Prob_3_{min(held[i],j["NeedCount"]-1)}'] for i,j in enumerate(jackpots)]
            event=weighted(rng,list(range(7)),weights)
            if not reset and (boxes<=1 or (event==6 and held[3]+1>=jackpots[3]['NeedCount'])):event=0
            guarantee=next(r['val'] for r in raw['CommCfg'] if r['id']==192)
            if used==guarantee and not dropped:event=3+rng.randrange(4)
            if event==0:
                boxes=20;reset=True;checks['reset_20']+=1
            else:
                boxes-=1
                if event==1:ticket+=cfg['passNum'];ticket_rows[cfg['_excel_row']]+=1
                elif event==2:coins[cfg['_excel_row']]+=1
                else:
                    j=event-3;held[j]+=1;dropped=True
                    if held[j]>=jackpots[j]['NeedCount']:
                        won[j]+=1;held[j]=0;luck=max(0,luck-(jackpots[j]['ReduceLuck'] or 0));checks['jackpot_reset']+=1
            assert 1<=boxes<=20
            milestones=[f'Pass {lv}' for lv,t in thresholds if ticket>=t]
            if won[3]:milestones.append('首次Grand')
            if used in (20,50,100,160,200):milestones.append(f'{used}次开盒')
            for label in milestones:
                if label in recorded:continue
                recorded.add(label)
                result.append({'sample':sample,'stage':label,'draws':used,'tickets':ticket,'jackpots':[won[i] for i in range(4)],'coin_rows':dict(coins),'pass_rows':dict(ticket_rows)})
            if ticket>=total and won[3] and used>=200:break
        else:raise ValueError('薯片模拟截断，不能报完成期望')
    return result,dict(checks)


def card_simulation(raw: dict, profiles: list[dict], samples: int = 100) -> tuple[list[dict], dict]:
    """r7013包→组→章→卡，21次拒绝重抽、UID 0..9均衡敏感性。
    只含自然Spin掉包；从空册开始，不叠加赠送、交易或星星兑换。
    季末右删失；不把已完成子样本均值报作无条件期望。
    """
    rng=random.Random(SEED+2)
    season=max(raw['CardAlbumCfg'],key=lambda r:r['startTime'])
    days=math.ceil((datetime.fromisoformat(season['endTime'])-datetime.fromisoformat(season['startTime'])).total_seconds()/86400)
    chapters=[r for r in raw['CardChapter'] if r['seasonId']==season['id'] and not r['isPrestige']]
    cards=[r for r in raw['CardList'] if r['seasonId']==season['id'] and r['cardChapter'] in {x['id'] for x in chapters}]
    by_ch=defaultdict(list)
    for r in cards:by_ch[r['cardChapter']].append(r)
    cp={r['id']:r for r in chapters}
    packs=defaultdict(list)
    for r in raw['CardPack']:
        if r['season']==season['id']:packs[r['pack']].append(r)
    groups=defaultdict(list)
    for r in raw['CardGroup']:
        if not r['isPrestige'] and r['chapterId'] in cp:groups[r['group']].append(r)

    @lru_cache(None)
    def candidates(group: int, day: int, progress: int) -> list[dict]:
        return [r for r in groups[group] if r['seasonDayMin']<=day<=r['seasonDayMax'] and r['progMin']<=progress<=r['progMax']]

    @lru_cache(None)
    def pool(ch: int, kind: int, star: int) -> list[dict]:
        return [r for r in by_ch[ch] if (not kind or r['type']==kind) and (not star or r['starLevel']==star)]

    result=[];checks=Counter()
    for prof in profiles:
        drops=[r for r in raw['SlotsCasinoDropCards'] if r['betIndex']==prof['bet_index'] and r['level']<=prof['level'] and r['needVipMinCard']<=prof['vip']<=r['needVipMaxCard']]
        drop=drops[-1];prob=drop['dropPro']/10000
        ids=[drop[f'cardId{i}'] for i in (1,2,3)];weights=[drop[f'cardWeight{i}'] or 0 for i in (1,2,3)]
        for sample in range(samples):
            held=Counter();completed={};spins=0;opened=0;uid=sample%10
            while spins < days*prof['daily_spin'] and len(completed)<len(chapters):
                spins+=max(1,math.ceil(math.log1p(-rng.random())/math.log1p(-prob)))
                if spins>days*prof['daily_spin']:break
                day=int((spins-1)//prof['daily_spin']);progress=len(held)
                pack=weighted(rng,ids,weights)
                if not packs[pack]:raise ValueError('当前赛季掉包缺少组成')
                rule=weighted(rng,packs[pack],[r['weight'] for r in packs[pack]],True)
                out=Counter()
                for slot in range(1,6):
                    kind,star,group,num=[rule.get(f'{f}{slot}') for f in ('type','star','group','num')]
                    if kind is None or kind<0 or not star or not group or not num:continue
                    for _ in range(int(num)):
                        for attempt in range(21):
                            gr=candidates(int(group),day,progress)
                            g=weighted(rng,gr,[r['weight'] for r in gr],True)
                            if g is None:continue
                            rr=pool(g['chapterId'],kind,star);cfg=cp[g['chapterId']]
                            if (cfg['cardTotalNum'] or 0)>0 and (cfg['needNum'] or 0)>0:
                                have=sum(held[r['cardId']] for r in by_ch[cfg['id']]);unique=sum(r['cardId'] in held for r in by_ch[cfg['id']])
                                if have>=cfg['cardTotalNum'] and cfg['cardNum']-unique<=cfg['needNum']:
                                    new=[r for r in rr if r['cardId'] not in held]
                                    if new:rr=new
                            card=weighted(rng,rr,[r[f'weight_10_{uid}'] for r in rr],True)
                            if card and card['cardId'] not in out:
                                out[card['cardId']]+=1;break
                            checks['duplicate_or_empty_retry']+=1
                for slot in range(1,4):
                    cid=rule.get(f'cardId{slot}')
                    if cid and any(r['cardId']==cid for r in cards):out[cid]+=1
                held.update(out);opened+=1
                for ch in chapters:
                    if ch['id'] not in completed and all(r['cardId'] in held for r in by_ch[ch['id']]):completed[ch['id']]=spins
            for ch in chapters:
                result.append({'profile':prof['name'],'sample':sample,'uid_class':uid,'chapter':ch['id'],'spins':completed.get(ch['id']),'horizon':days*prof['daily_spin'],'opened':opened,'unique':len(held),'complete':int(ch['id'] in completed)})
            result.append({'profile':prof['name'],'sample':sample,'uid_class':uid,'chapter':'整册','spins':max(completed.values()) if len(completed)==len(chapters) else None,'horizon':days*prof['daily_spin'],'opened':opened,'unique':len(held),'complete':int(len(completed)==len(chapters))})
    return result,dict(checks)
