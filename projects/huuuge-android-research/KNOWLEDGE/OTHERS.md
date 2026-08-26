# Others Knowledge Navigation

Others 分类承接礼包/购买、小玩法、牌桌游戏、runtime/platform supporting modules 和尚未归类的协议。它不是低优先级垃圾桶；每个模块仍保留独立证据等级与下一步。

| ID / Module | 证据等级 | 证据摘要 | 当前完成度 | 下一步计划 |
| --- | --- | --- | --- | --- |
| [`offers` — Offers / Shop / Bundles](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/offers.md) | L3 Runtime Observed | Runtime P 34 + X 11；Schema 62M/15E；Schema hint ZPK 20 | 90/100 — substantial live structure | 分离 shop、offer family、bundle detail、personal offer、Offer Trail、Tile Shop 的 eligibility/price/reward |
| [`purchases` — Purchase / Checkout / Price Localization](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/purchases.md) | L3 Runtime Observed | Runtime P 4 + X 4；Schema 32M/9E；Schema hint ZPK 12 | 80/100 — substantial live structure | 只观察 purchase detail 到 platform checkout preview，并在授权前取消；不执行购买 |
| [`vouchers` — Vouchers](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/vouchers.md) | L1 Schema | Runtime 0；Schema 7M/1E；Schema hint ZPK 0 | 30/100 — schema skeleton | 访问 voucher event/shop、balance、item detail、tutorial，确认用途和生命周期 |
| [`non_spin_bonus` — Non-Spin Bonus Games](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/non_spin_bonus.md) | L1 Schema | Runtime 0；Schema 13M/7E；Schema hint ZPK 3 | 35/100 — schema skeleton | 在正常游戏中自然遇到可见 bonus，观察 trigger/start/end；不人为修改触发条件 |
| [`baccarat` — Baccarat](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/baccarat.md) | L1 Schema | Runtime 0；Schema 15M/6E；Schema hint ZPK 0 | 30/100 — schema skeleton | 正常进入 room，观察 join/config/betting/result 结构，不做异常请求 |
| [`blackjack` — Blackjack](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/blackjack.md) | L1 Schema | Runtime 0；Schema 15M/6E；Schema hint ZPK 0 | 30/100 — schema skeleton | 正常进入 room，观察 betting/action/result state |
| [`roulette` — Roulette](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/roulette.md) | L1 Schema | Runtime 0；Schema 14M/6E；Schema hint ZPK 0 | 30/100 — schema skeleton | 正常进入 room，观察 ready/betting/result state |
| [`texas_poker` — Texas Poker](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/texas_poker.md) | L1 Schema | Runtime 0；Schema 19M/10E；Schema hint ZPK 0 | 30/100 — schema skeleton | 正常访问 table/tournament，观察 lobby、buy-in、hand、result 结构 |
| [`video_poker` — Video Poker](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/video_poker.md) | L1 Schema | Runtime 0；Schema 14M/7E；Schema hint ZPK 0 | 30/100 — schema skeleton | 正常观察 first draw、hold selection、second draw、result |
| [`game_runtime` — Game Runtime / Host / Room State](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/game_runtime.md) | L1 Schema | Runtime 0；Schema 66M/21E；Schema hint ZPK 7 | 35/100 — schema skeleton | 用 normal play 时间线关联 lobby entry、game join、room loaded、leave、reconnect |
| [`platform_diagnostics` — HTF / Proxy / Test Infrastructure](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/platform_diagnostics.md) | L1 Schema | Runtime 0；Schema 74M/11E；Schema hint ZPK 0 | 30/100 — schema skeleton | 保持 schema-only；只有自然出现 diagnostic traffic 时才补证，不主动触发测试接口 |
| [`other_protocol` — Other / Unclassified Protocol Families](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/other_protocol.md) | L1 Schema | Runtime 0；Schema 92M/13E；Schema hint ZPK 0 | 30/100 — schema skeleton | 每次新 capture 后审阅 unknown endpoints；只在形成 coherent family 后拆新 dossier |

## Review Notes

- Offers/Purchases 是当前 evidence-rich 的商业化结构入口，但不授权购买、绕过或服务端修改。
- 牌桌和小玩法的 schema 不代表相同 runtime transport；未来 live evidence 应分别保留 game/module source。
- `other_protocol` 只用于暂存未形成模块所有权的 schema family，不能作为最终业务分类。

本页等级与引用类型统一遵循 [`Huuuge Evidence Standard`](../../../standards/HUUUGE_EVIDENCE_STANDARD.md)。
