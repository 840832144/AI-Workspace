# Huuuge Android Research — Project Status

- Updated: 2026-09-04
- Phase: TASK-0027 P0 Laptop Demo Reliability Hardening；Phase C static preflight complete / dynamic blocked
- Owner: User
- Current milestone: TASK-0027 formal package/static preflight verified；dynamic lifecycle blocked before start
- External baseline: [`4a5dddf`](https://github.com/840832144/huuuge-android-research/commit/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b)

## Confirmed Current Facts

- AI-Workspace Project Template has been instantiated as `projects/huuuge-android-research/` with Context、Memory、Workflow、Status、Reports and Assets.
- External implementation and evidence remain in `huuuge-android-research`; no source, capture or runtime asset was migrated.
- Battle Pass entry is schema-only/live-pending.
- Slots entry is live-confirmed and supported by the broad 741/741 decoded Session plus a sanitized 29-Spin-pair example.
- Lottery now has L3 primary Runtime evidence: 346/346 `LotteryToss` request/response pairs from finalized alias `LOT-20260827-A`; the external report separates direct Lottery rewards, threshold rebates, real-money purchases and upgrade-linked ticket outcomes.
- Review Round 1 purchase re-extraction confirms four successful real-money purchases totaling 54.43 SGD, 763 Lottery tickets and 235 loyalty points. All four bundles contain another reward, so apparent per-ticket cost is not a standalone ticket price.
- The revised public terms identify 588 ordinary chip-bet Spins and 45 FreeSpins separately from real-money purchases.
- Generic Missions is schema-only/live-pending; MiniPass has a separate live-confirmed task/missions flow.
- TASK-0006 collector architecture baseline remains Waiting for ChatGPT Review in the external repository.
- TASK-0009 Knowledge Index covers all 37 external dossiers under Slots 1、Systems 10、Events 14、Others 12.
- Huuuge Evidence Standard defines L0 Unverified、L1 Schema、L2 Configured / Visible、L3 Runtime Observed and L4 Triangulated.
- Citation types are standardized as Schema、Config、Runtime、UI and Manual with required provenance、locator、context、claim scope and limits.
- All 37 Knowledge modules use the standard. After TASK-0018, Lottery moves from L2 to L3: L3 × 12、L2 × 3、L1 × 22、L0/L4 × 0.
- TASK-0015 is `Complete` and TASK-0018 is `Review`; TASK-0014 remains `Accepted`.
- The original connector-verified report [`Huuuge Lottery 活动数值拆解（2026-08-27）`](https://gfok27asqq.feishu.cn/docx/IK5adiJyWoHVJzxlovEcjxiWnO3) was replaced in place without creating a duplicate; final readback found 367 blocks, one title, complete planner section order and company-editable permission.
- TASK-0011 First Run Guide is available in Git and uses Codex or Trae + DeepSeek as the default operator instead of requiring planners to execute low-level commands.
- The Feishu edition [`Huuuge 新人上手指南（First Run Guide）`](https://gfok27asqq.feishu.cn/docx/Ffibd2Cx2oXFgfxdKnJcE6uUnZf) was created through AI Document Assistant, read back successfully, and verified as company-editable (`tenant_editable`).
- A blind-test record exists at `REPORTS/TASK-0011-FIRST-RUN-VALIDATION.md`; it contains no fabricated tester、timing or success data.
- User pre-validation feedback found that RC1 explained the AI/technical process but did not provide a sufficiently direct novice action sequence. RC2 now opens with a 12-step “新人照着做” path、zero-to-start prompt、pass conditions、recovery phrases and five common replies; this is not counted as independent planner validation.
- User pre-validation feedback corrected the initial workspace from a disposable First Run folder to persistent `C:\AI-Workspace`. RC3 also defines empty-directory Clone、existing-repository update and non-empty conflict behavior.
- User confirmed that only AI-Workspace is public while the implementation repositories remain private. RC4 therefore makes public AI-Workspace the only required Git repository, moves private implementation repositories to maintainer-only context, and requires a three-minute fail-fast check for company SVN and the administrator-provisioned Document Assistant.
- User approved P0 Reliability Hardening on 2026-09-04 for the minimum “笔记本汇报实机演示” scope；remote-CAS allocator established canonical `TASK-0027` without manually selecting an ID.
- TASK-0027 Phase B verified BlueStacks 5 `5.22.262.1001` / Services `3.0.9` under the current Hypervisor/VMP, program path `C:\Program Files\BlueStacks_nxt\`, data path `D:\BS\BlueStacks_nxt\Engine\`, and normal start/exit/restart reproduction.
- The sole local fresh Pie 64-bit internal ID is `Pie64`, displayed as `HuuugeResearch`; it uses 4 CPU / 4096 MB, ADB `127.0.0.1:5585`, remote ADB OFF and Root OFF. Default 5555 conflicted with Windows excluded ports and was changed only after User approval.
- User completed Huuuge installation/login. Read-only ADB evidence confirms package `com.huuuge.casino.slots`, versionName `12.08.27100`, versionCode `1786533240` and primary ABI `arm64-v8a`; Codex did not install, log in, click the game, run Collector or execute Spin.
- BlueStacks bundled `HD-Adb.exe` can wait indefinitely while scanning excluded default emulator ports; both run-owned attempts were cleaned by exact PID, with no 5037 or client residue. The endpoint itself passed a read-only direct ADB transport probe. This CLI behavior is explicit Phase C Reliability Hardening input, not hidden success.
- Current laptop Workspace is `D:\AI-Workspace`; the old `C:\AI-Workspace` guide path and historical `Pie64_1` identity were not reused. MuMu remained running and Nox remained unchanged; neither occupied 5585/5037 or was modified.
- TASK-0027 Phase C obtained the official SVN 1.0.1 package at `C:\HuuugeCollector@r6701`; installer/tree last changed at r6624, clean source revision is `77e0339fa73da2ab02fcbb6cff125604a9a8abd5`, ZIP SHA-256 is `ACAC144B3CB58E861345D33F6CEEB95ACA0E1CE3CF8B49211C6E7AFB260A958A`, and manifest/static parse checks passed.
- The formal controller hard-codes `Pie64_1 / 127.0.0.1:5565` and requires real `uid=0(root)`. This conflicts with the approved laptop identity `Pie64 / 127.0.0.1:5585 / Root OFF`; dynamic Start/READY/Session/Stop/Finalize was therefore not run and Demo Ready is `No`.

## In Progress

- ChatGPT Review Round 2 of TASK-0018 planner structure, purchase table and limits, ordinary-bet terminology, Extractor tests and original Feishu replacement.
- Independent First Run by one planner who did not participate in development remains a separate validation track.
- TASK-0027 is active. Phase C package/static preflight is complete; dynamic lifecycle is stopped before start pending a new scope decision.

## Risks

- Workspace state can drift from the external repo if stable commit links and Status are not refreshed after meaningful research changes.
  - Mitigation: external repo updates first; Workspace only promotes reviewed durable facts.
- Existing evidence is uneven: Slots and Lottery now have primary live evidence, while Battle Pass and generic Missions remain incomplete.
  - Mitigation: label status per module and never compare them as equally complete.
- Lottery upgrade-linked ticket causation lacks an explicit grant payload or matching UI artifact.
  - Mitigation: preserve `Confirmed L3` for the six balance transitions and `Estimate L3` for level-up causation; do not promote to L4.
- Skill categories exist only as model entries; they are not executable research Skills.
  - Mitigation: every execution still requires an explicit Workflow and external-tool evidence.
- The four-category taxonomy is optimized for planner navigation and may not match protocol ownership one-to-one.
  - Mitigation: category pages link the external primary dossier and explicitly preserve cross-cutting evidence.
- Existing external artifacts do not yet have canonical `HGR-YYYYMMDD-TYPE-NNN` Citation IDs.
  - Mitigation: Knowledge keeps commit-pinned dossier summaries; do not invent or backfill IDs before the standard is accepted and an external migration task is authorized.
- L4 requires Runtime、UI、Manual and Schema/Config triangulation; the current catalog was not built to prove this bundle.
  - Mitigation: keep every current module at L3 or below until all L4 conditions are directly evidenced.
- The guide has not yet been exercised on an uninvolved planner/new computer; documentation clarity and real elapsed time are unknown.
  - Mitigation: run the required blind test without oral help, record every stop and revise documentation/workflow only.
- Trae + DeepSeek may not expose the company Document Assistant MCP on every workstation.
  - Mitigation: Trae may generate the sanitized Markdown; an approved Codex/MCP host performs publication without sharing credentials.
- Private GitHub links require an authenticated collaborator session and are unavailable to the novice test participant.
  - Mitigation: the 30-minute First Run uses only public AI-Workspace, the official SVN package and an administrator-provisioned Document Assistant; private links remain maintainer evidence references, not novice steps.
- The approved BlueStacks endpoint works on 5585, but bundled `HD-Adb.exe` server startup scans excluded default emulator ports and can hang before opening 5037.
  - Mitigation: Phase C must pin a deterministic ADB implementation or direct endpoint strategy with timeout、exact cleanup and explicit serial; Collector remains stopped until that preflight is approved and passes.

## Blockers

- TASK-0018 has no implementation blocker; Review Round 1 fixes are complete and it is waiting for ChatGPT Review Round 2.
- TASK-0011 still has a separate validation gate: no uninvolved planner has yet been designated or observed for the required blind test.
- TASK-0027 Phase C dynamic lifecycle is blocked by the formal package's Root/Pie64_1/5565 contract mismatch and missing fixed ADB/Frida dependencies. Continuing requires Collector engineering changes or changing the approved Root/instance boundary.

## Exact Next Action

User decides whether to authorize a separately scoped Collector engineering adaptation for `Pie64 / 5585 / Root OFF`. Until then keep BlueStacks、Root、Frida、Collector and Spin stopped.
