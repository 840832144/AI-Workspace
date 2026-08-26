# Slots Knowledge Navigation

Slots 分类聚焦核心 Slot lobby、spin、bet、win、feature 与 jackpot。当前外部 catalog 只有一个 primary Slots dossier；Non-Spin Bonus 等独立小玩法放在 [`OTHERS.md`](OTHERS.md)。

| ID / Module | 证据等级 | 数据来源 | 当前完成度 | 下一步计划 |
| --- | --- | --- | --- | --- |
| [`slots` — Slots / Lobby / Spin / Jackpot](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/slots.md) | E3 Primary live | Live P 288 + X 1；Schema 90M/32E；ZPK 17 | 90/100 — substantial live structure | 先复用现有 29 Spin pairs；Review 后选择代表性机器、bet change 和自然 feature/free-spin/jackpot 状态补证，或定义首个 normalized gameplay Extractor |

## Current Knowledge

- 这是当前最适合作为 gameplay extractor 候选的模块，但“结构完整”不等于已经能够计算稳定 RTP/EV。
- Broad Session 已有真实 `Spin` request/response；sanitized example 不含账号标识、逐 spin balance 或完整 reel-stop values。
- 若关键状态不在 AppServer/AppClient RPC 中，后续应把 GameServer、Lua/native state 或 static config 作为独立 evidence channel，不强行塞入同一模型。

## Review Gate

ChatGPT 需要确认：Slots 是否应成为第一个 normalized gameplay Extractor；若是，先定义 entity、fact grain、输入字段、版本 lineage 和验收证据，不在本任务实现。
