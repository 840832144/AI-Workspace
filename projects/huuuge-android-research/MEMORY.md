# Huuuge Android Research — Project Memory

## Confirmed

### Project and collector

- External implementation/evidence source is [`huuuge-android-research`](https://github.com/840832144/huuuge-android-research), current baseline commit [`bfed5f3`](https://github.com/840832144/huuuge-android-research/commit/bfed5f30e098522ffb98ef5eb7d63e824d68b1c4).
  - Evidence: User decision in TASK-0008 and TASK-0018 synchronized Git state on 2026-08-27.
- The proven chain is isolated research environment → x86_64 Frida server → Houdini namespace → ARM64 Gadget → three high-level `Casino.RpcMessage` hooks → descriptor-backed decode.
  - Evidence: external [`CURRENT_STATUS.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/CURRENT_STATUS.md).
- Existing proven Sessions include 84/84, 741/741 and 91/91 descriptor-decoded RPCs.
  - Evidence: external Current Status and TASK-0006 capability baseline.
- Current module catalog covers 37 dossiers, 1028 descriptor message types and 356 service methods; 15 modules have live evidence and 22 are schema-only/live-pending.
  - Evidence: external [`MODULE_INDEX.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/MODULE_INDEX.md).

### Battle Pass

- Battle Pass has recovered schema and service/method structure but no dedicated current live sample.
  - Evidence: external [`battle_pass.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/battle_pass.md) and [`BattlePass_schema.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/recovered/BattlePass_schema.md).
- An eligible account is required before collecting Battle Pass main/reward/mission traffic; Battle Pass must not block other system research.
  - Evidence: external [`TASKS.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/TASKS.md).

### Slots

- Slots is live-confirmed and one of the most structurally complete primary modules.
  - Evidence: external [`slots.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/slots.md).
- The broad Session includes a sanitized example derived from 29 `Spin` request/response pairs, 58/58 decoded, without account IDs, per-spin balances or full reel-stop arrays.
  - Evidence: external [`summary.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/analysis/20260825_182300/summary.md) and Current Status.

### Lottery

- Lottery now has L3 Runtime Observed evidence from finalized alias `LOT-20260827-A`: 346/346 primary `LotteryToss` pairs, plus 588/588 Spin and 45/45 FreeSpin pairs used for source reconciliation.
  - Evidence: external [`Lottery report`](https://github.com/840832144/huuuge-android-research/blob/bfed5f30e098522ffb98ef5eb7d63e824d68b1c4/reports/lottery/20260827_lottery-ticket-puzzle/LOTTERY_NUMERICAL_BREAKDOWN.md) and [`lottery dossier`](https://github.com/840832144/huuuge-android-research/blob/bfed5f30e098522ffb98ef5eb7d63e824d68b1c4/artifacts/module_catalog/lottery.md).
- In the observed Session, every 7 consumed ticket units returned one Bronze ticket; 933 units produced 133 returns from initial progress 1 and ended at progress 3.
  - Evidence: external report and `PROGRESSION_MODEL.csv`; scope is one account/build/Session.
- Spin/FreeSpin responses contain no direct Lottery ticket grant. Six post-level balance transitions total +16 Bronze; the transitions are Confirmed L3, while level-up causation is Estimate L3 supported by repeated timing and User Manual evidence.
  - Evidence: external `SLOT_ITEM_DROP_STATS.csv`、`PROGRESSION_MODEL.csv` and Evidence Matrix.
- The connector-verified Feishu report is company-editable: [`Huuuge Lottery 活动数值拆解（2026-08-27）`](https://gfok27asqq.feishu.cn/docx/IK5adiJyWoHVJzxlovEcjxiWnO3).

### Task / Missions

- Generic Missions is schema-only/live-pending; MiniPass contains a separate live-confirmed mission/task flow.
  - Evidence: external [`missions.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/missions.md) and [`mini_pass.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/mini_pass.md).

## Decisions

- AI-Workspace owns Context、Memory、Workflow、Status；外部 repository owns code、tests、runtime evidence and engineering history.
  - Source: User TASK-0008 and Workspace Project Standard.
- Structure first, values later; broad evidence precedes a one-off deep numerical model.
  - Source: external `MODULE_STRUCTURE_CATALOG.md` and TASK-0006 Roadmap.
- Console filters are display-only; capture retains all observable RPCs.
  - Source: external collector manifest contract and validated Sessions.
- Planner GUI does not require module selection or manual action markers; only automatic lifecycle markers are current capability.
  - Source: external TASK-0006 capability baseline.
- TASK-0008 initializes control-plane documents only and waits for ChatGPT Review.
  - Source: User instruction on 2026-08-26.
- TASK-0009 uses a four-category knowledge taxonomy: Slots、Systems、Events、Others. This taxonomy is a planner navigation layer and does not change external module ownership.
  - Source: User instruction and `KNOWLEDGE/README.md`; waiting for ChatGPT Review.
- TASK-0010 replaces the temporary E0–E3 navigation labels with the Huuuge L0–L4 Evidence Standard. Existing module evidence migrates without promotion: L3 × 11、L2 × 4、L1 × 22、L0/L4 × 0.
  - Source: User instruction、`standards/HUUUGE_EVIDENCE_STANDARD.md` and Knowledge Index；waiting for ChatGPT Review.
- TASK-0011 makes Codex or Trae + DeepSeek the default First Run operator. New planners handle only login、approval and normal game interaction; AI handles checks、startup、finalization、Markdown and Document Assistant publishing.
  - Source: User instruction and `FIRST_RUN_GUIDE.md`; independent planner validation pending.
- TASK-0011 novice access uses public AI-Workspace as the only required Git repository. Private implementation repositories remain maintainer truth sources and must not be novice prerequisites; collection comes from the official SVN package and Feishu publication uses an administrator-provisioned shared Document Assistant.
  - Source: User access decision on 2026-08-26 and `FIRST_RUN_GUIDE.md` RC4；independent 30-minute validation pending.
- Planner-facing documents default to Chinese, and newly generated cloud documents default to company-editable access unless User explicitly requests another permission mode.
  - Source: User decisions on 2026-08-26 and repository documentation rules.
- Lottery source attribution must distinguish direct Toss rewards、threshold rebates、purchases and upgrade-linked outcomes. A balance transition may be Confirmed while its causal grant remains Estimate.
  - Source: TASK-0018 evidence review and User correction on 2026-08-27.

## Hypotheses

- Slots may be the best first normalized gameplay Extractor because it has the strongest current live evidence.
  - Validation needed: ChatGPT/User priority decision and field-level extractor acceptance criteria.
- Missions or Offers may be suitable as the first meta/economy Extractor.
  - Validation needed: compare live coverage, planner value and schema completeness.
- Higher Bet may increase upgrade-linked Lottery ticket acquisition only indirectly by accelerating progression; no direct Spin ticket field was observed.
  - Validation needed: fixed-level-range、fixed-duration Bet comparison plus matching UI/runtime upgrade evidence.

## Reusable Knowledge

- Use the module dossier before inspecting Raw data; it states schema/live status, known fields and missing evidence.
- Never treat a schema field name or heuristic semantic role as confirmed business meaning without live/context validation.
- Preserve Session version, descriptor hash and source commit when deriving any report.
- Update external research evidence first, then reflect only stable confirmed facts in this Memory and current state in Status.
- Use the Knowledge Index as the human entrypoint, then follow the commit-pinned external dossier for detailed evidence.
- Every current claim must separate Evidence Level from Completion and cite Schema、Config、Runtime、UI or Manual using the Huuuge Evidence Standard.

不得记录 credential、玩家明细、完整日志、Raw/decoded values 或业务数据副本。
