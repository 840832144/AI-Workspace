# Events Knowledge Navigation

Events 分类包含 pass、draw、collection、competition、周期活动和 LiveOps。是否永久开放不决定分类；核心判断是它是否以 event window、reward track、leaderboard、milestone 或周期状态组织。

| ID / Module | 证据等级 | 证据摘要 | 当前完成度 | 下一步计划 |
| --- | --- | --- | --- | --- |
| [`lottery` — Lottery / Draw / Ticket](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/lottery.md) | L2 Configured / Visible | Runtime P 0 + X 5；Schema 29M/5E；Schema hint ZPK 1 | 65/100 — partial live structure | 未来访问 lottery/draw/ticket 界面，补 dedicated endpoint、ticket、schedule、tier/odds evidence |
| [`battle_pass` — Battle Pass](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/battle_pass.md) | L1 Schema | Runtime 0；Schema 27M/9E；Schema hint ZPK 1 | 35/100 — schema skeleton | 等待 eligible account；访问 main、reward track、daily/weekly missions，不阻塞其他研究 |
| [`mini_pass` — MiniPass](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/mini_pass.md) | L3 Runtime Observed | Runtime P 10；Schema 24M/10E；Schema hint ZPK 0 | 85/100 — substantial live structure | 分开 main、missions、milestone/reward track，验证 task 与 pass progression 关系 |
| [`vault` — Vault](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/vault.md) | L3 Runtime Observed | Runtime P 5；Schema 18M/4E；Schema hint ZPK 3 | 65/100 — partial live structure | 访问 main/detail/help，验证 accumulation、threshold、reward 与 timing |
| [`collection` — Collection / Collection Event / Club Set](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/collection.md) | L2 Configured / Visible | Runtime P 0 + X 44；Schema 39M/7E；Schema hint ZPK 3 | 65/100 — partial live structure | 访问 album/theme、collection event、Club Set，补 dedicated lifecycle/progress endpoints |
| [`conquest` — Conquest](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/conquest.md) | L1 Schema | Runtime 0；Schema 29M/6E；Schema hint ZPK 1 | 35/100 — schema skeleton | 访问 map、arena、slot/challenge、summary/leaderboard，确认 stage 与 reward hierarchy |
| [`charms` — Charms / Trading](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/charms.md) | L3 Runtime Observed | Runtime P 2 + X 15；Schema 43M/12E；Schema hint ZPK 2 | 65/100 — partial live structure | 访问 collection、milestones、pack/box、trading，区分 collectible 与交易状态 |
| [`sweepstakes` — Sweepstakes / Scheduled Draws](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/sweepstakes.md) | L1 Schema | Runtime 0；Schema 14M/6E；Schema hint ZPK 0 | 30/100 — schema skeleton | 访问 current/completed draw、ticket balance、history，确认 schedule/result 流程 |
| [`adventure` — Adventure](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/adventure.md) | L1 Schema | Runtime 0；Schema 21M/5E；Schema hint ZPK 0 | 30/100 — schema skeleton | 访问 map/phase、difficulty、missions、milestones，确认 progression graph |
| [`tournaments` — Content Tournaments](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/tournaments.md) | L1 Schema | Runtime 0；Schema 6M/2E；Schema hint ZPK 0 | 30/100 — schema skeleton | 访问 tournament、rules/rewards、content item、leaderboard，确认 scoring/rank/reward fields |
| [`race` — Race](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/race.md) | L1 Schema | Runtime 0；Schema 14M/3E；Schema hint ZPK 0 | 30/100 — schema skeleton | 访问 overview、reward tiers、leaderboard/detail，确认 race stage 与 ranking |
| [`elites` — Elites / Play Together](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/elites.md) | L1 Schema | Runtime 0；Schema 25M/8E；Schema hint ZPK 0 | 30/100 — schema skeleton | 访问 event、missions/milestones、leaderboard、Play Together，确认协作与竞争结构 |
| [`personal_awards` — Personal Awards](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/personal_awards.md) | L1 Schema | Runtime 0；Schema 18M/2E；Schema hint ZPK 0 | 30/100 — schema skeleton | 定位 achievement/award progress surface，确认 objective、progress、reward 结构 |
| [`liveops_events` — Other LiveOps / DCI / Tower / Balloons](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/liveops_events.md) | L3 Runtime Observed | Runtime P 66；Schema 88M/18E；Schema hint ZPK 5 | 90/100 — substantial live structure | 分离 Tower、Balloons 与 unmatched event families，避免继续堆在一个聚合 dossier |

## Review Notes

- Lottery 与 Sweepstakes 都涉及 draw/ticket，但当前 schema ownership 与 evidence 不同，不能合并。
- Battle Pass 与 MiniPass 应共享比较维度，不共享未经验证的 message/entity 含义。
- `liveops_events` 完成度高但内部仍是聚合类；未来应以 coherent endpoint families 拆分，而不是按 UI 名称猜测。

本页等级与引用类型统一遵循 [`Huuuge Evidence Standard`](../../../standards/HUUUGE_EVIDENCE_STANDARD.md)。
