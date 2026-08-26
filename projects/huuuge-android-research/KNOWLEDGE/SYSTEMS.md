# Systems Knowledge Navigation

Systems 分类包含长期存在的玩家、任务、奖励、成长、经济与社交基础系统。它不包含主要按周期运行的活动，也不把 MiniPass task flow 与通用 Missions 合并。

| ID / Module | 证据等级 | 证据摘要 | 当前完成度 | 下一步计划 |
| --- | --- | --- | --- | --- |
| [`missions` — Missions / Quests / Daily-Weekly Tasks](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/missions.md) | L1 Schema | Runtime 0；Schema 16M/3E；Schema hint ZPK 0 | 30/100 — schema skeleton | 未来 unrestricted capture 分别访问 daily、weekly、general task 面板，确认专用 endpoint 与 progress/reward 字段 |
| [`loyalty` — Loyalty / VIP](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/loyalty.md) | L3 Runtime Observed | Runtime P 5 + X 23；Schema 7M/3E；Schema hint ZPK 1 | 65/100 — partial live structure | 检查 VIP overview、tier benefits、progress/history，验证等级、门槛和权益字段 |
| [`clubs` — Clubs / Social Club Progression](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/clubs.md) | L2 Configured / Visible | Runtime P 0 + X 19；Schema 79M/28E；Schema hint ZPK 7 | 55/100 — partial live structure | 正常访问 club home、members、chat、events、league/season、donation，补 dedicated endpoint evidence |
| [`rewards` — Rewards / Mystery / Hourly / Free Gift](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/rewards.md) | L3 Runtime Observed | Runtime P 19 + X 56；Schema 111M/21E；Schema hint ZPK 4 | 90/100 — substantial live structure | 分离 hourly/daily/shop bonus、mystery reward 与 free gift，验证 reward bundle、timing 和 eligibility |
| [`progression` — Fame / Level / General Progression](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/progression.md) | L3 Runtime Observed | Runtime P 63 + X 40；Schema 54M/8E；Schema hint ZPK 4 | 75/100 — substantial live structure | 检查 profile、fame/level progress、rank benefits 和 history，建立成长实体与门槛关系 |
| [`economy` — Currency / Balance / Economy Statistics](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/economy.md) | L2 Configured / Visible | Runtime P 0 + X 250；Schema 17M/2E；Schema hint ZPK 12 | 65/100 — partial live structure | 用时间与 endpoint 关联 spin、reward、shop preview 前后可见 balance；只输出脱敏结构/差异，不提交值 |
| [`player_lobby` — Player / Game / Lobby State](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/player_lobby.md) | L3 Runtime Observed | Runtime P 245 + X 4；Schema 55M/29E；Schema hint ZPK 10 | 90/100 — substantial live structure | 复核 cold start、lobby loaded、profile、friends/leaderboard 与 game-list navigation 的结构关系 |
| [`authentication` — Authentication / Account / Consent](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/authentication.md) | L1 Schema | Runtime 0；Schema 59M/17E；Schema hint ZPK 3 | 35/100 — schema skeleton | 只利用自然 cold start 补证；不为 catalog 主动重新登录或触碰 account/consent 状态 |
| [`social` — Social Recommendations / Invites](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/social.md) | L1 Schema | Runtime 0；Schema 5M/2E；Schema hint ZPK 0 | 30/100 — schema skeleton | 在未来正常操作中访问 invite/recommendation/referral 界面，确认实体与限制字段 |
| [`contact_point` — Contact Point / Engagement Surface](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/contact_point.md) | L1 Schema | Runtime 0；Schema 4M/2E；Schema hint ZPK 0 | 30/100 — schema skeleton | 正常访问 inbox/contact/help/engagement surface，确认该 schema 的真实产品归属 |

## Review Notes

- `economy` 和 `rewards` 是 cross-cutting 视角，会与 Events、Offers、Slots 共享字段；不要把重复 evidence 当作重复事件。
- `authentication` 只做被动自然启动观察，不需要为目录完整度主动触发高风险账号流程。
- 通用 Missions 与 MiniPass missions 的 entity、reset、reward track 可能不同，后续 normalized schema 必须保持来源字段。

本页等级与引用类型统一遵循 [`Huuuge Evidence Standard`](../../../standards/HUUUGE_EVIDENCE_STANDARD.md)。
