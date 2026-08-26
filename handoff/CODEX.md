# Codex Handoff

这是 Codex 的固定交接入口。实现细节以对应外部项目仓库为准。

- Updated: 2026-08-26
- Task: TASK-0010
- Current state: Huuuge Evidence Standard established and Knowledge migrated; waiting for ChatGPT Review

## Objective

统一整个 Huuuge Research 的 Evidence Level 与引用规范，使 Knowledge、后续报告和外部证据迁移使用同一套 L0–L4 判定语言。

## Completed

- 安全同步 AI-Workspace；外部 evidence baseline 保持 `huuuge-android-research@0590c2c37a0aa83b824920fa884f9f67007d3dcb`。
- 新增 `standards/HUUUGE_EVIDENCE_STANDARD.md`：
  - L0 Unverified。
  - L1 Schema。
  - L2 Configured / Visible。
  - L3 Runtime Observed。
  - L4 Triangulated。
- 定义 Schema、Config、Runtime、UI、Manual 五类引用的合格来源、必填 locator/context 和单独使用上限。
- 定义 `HGR-YYYYMMDD-TYPE-NNN` Citation ID、完整记录、紧凑引用、claim scope/limits 与升级、降级、冲突、过期规则。
- 将 Knowledge Index 和四类导航的 37 modules 无损迁移为 L3 × 11、L2 × 4、L1 × 22、L0/L4 × 0。
- 更新项目 README、Memory、Workflow、Status、Standards Index、CHANGELOG 和 ChatGPT Handoff。

## Confirmed Context

- TASK-0009 的 E0–E3 是临时导航模型；TASK-0010 以 L0–L4 正式取代它，但历史 CHANGELOG 不重写。
- 旧 E1 → L1、E2 → L2、E3 → L3；迁移没有改变外部 baseline，也没有提升证据强度。
- L4 必须同时满足 primary Runtime、匹配 UI、Manual action timeline、至少一个 Schema/Config 引用，以及两个独立观察周期。
- Completion 与 Evidence Level 分开；90/100 的结构目录完成度不代表 L4，也不代表数值或业务规则完成。
- ZPK 文件名与关键词只作为 Schema locator hint，不能单独提升等级。
- 本次没有修改外部研究仓库、Collector、SVN release、Feishu 文档或本机环境。

## Validation

- 37 个 module links 保持唯一覆盖；分类数量仍为 Slots 1、Systems 10、Events 14、Others 12。
- 迁移分布为 L3 × 11、L2 × 4、L1 × 22；L0/L4 均为 0。
- 所有 Knowledge module rows 已移除旧 E-level，并使用 Runtime/Schema 证据摘要。
- Repository-relative links、`git diff --check`、credential-like literal scan 和指定领域词扫描均已通过。

## Risks

- 当前外部 artifact 尚未使用 canonical Citation ID；本次只定义合同，不能虚构回填。
- L2 可能来自 Config、cross-cutting Runtime 或 UI，不代表捕获了 primary action；报告必须保留具体 channel。
- L3 是样本范围内 Runtime observation，不能外推为跨版本稳定规则或完整概率/经济结论。
- L4 门槛较高；若 UI/Manual lineage 记录不足，模块必须保持 L3 或以下。
- Private GitHub links 需要已授权的 collaborator session。

## Constraints

- Review 前不修改等级门槛、不运行新采集、不开发 Citation Registry/Evidence Registry，也不批量回填外部 artifact。
- 不复制 Raw/decoded values、账号/会话标识、截图、APK、binary、credential 或完整外部 dossier。
- 外部仓库仍是实现与原始证据真相源；Workspace 只保存标准、导航和脱敏引用。

## Exact Next Action

ChatGPT 审阅 `standards/HUUUGE_EVIDENCE_STANDARD.md` 与 `projects/huuuge-android-research/KNOWLEDGE/`，返回 Accepted 或针对 L0–L4 门槛、五类引用、L4 三角验证和模块迁移的具体修订。Codex 等待 Review，不开始实现。
