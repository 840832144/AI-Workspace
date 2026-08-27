# TASK-0023 ChatGPT Review — Round 1

- Decision: **Needs changes**
- Reviewed branch: `codex/idea-governance-product-roadmap`
- Reviewed commit: `47cdec11d67557cc10d72ecc5891eca2ae9bedc3`
- Review date: 2026-08-27
- Subagents observed: none

## Passed

TASK-0023 的主体交付可以保留：唯一 Product Roadmap、`Current / Backlog / Ideas / Done` 四分区、Idea Governance standard/workflow、飞书导航入口、项目全景入口、临时 Idea 回读与删除、Task/Context/Memory 回归和 `ON_DEMAND` 边界均满足当前目标。

## Required Fix — 准确、克制、面向受众的技术术语

User 要求 ChatGPT、Codex、Trae / DeepSeek、Generic Agent、Subagents 与后续接入的其他 AI 统一遵守一条术语规则：默认使用准确、克制、与真实工作相符的表达；只有技术精度、复现、安全、合规或 Review 确实需要时，才使用更强或更底层的术语。

这不是为了规避平台安全检查，也不得把高风险行为改名后隐藏。所有表达必须如实反映实际动作、权限和风险。

### 默认表达

面向策划、普通项目协作、飞书说明和非技术摘要时，优先使用：

- 游戏客户端研究
- 静态审计 / 动态分析
- 被动数据采集
- 协议或数据结构分析
- 运行时插桩（首次可写“运行时插桩 / Hook”）
- 客户端状态观察
- 证据恢复与字段映射
- 数值体验分析
- 研究环境授权与隔离

不要在并不准确时使用“破解、黑客、攻击、爆破、入侵、偷取、绕过”等夸张或误导性词语。

### 必须使用精确术语的情况

以下场景必须保留真实技术名称，不得为了显得温和而模糊：

- 复现步骤、技术附录、代码、日志、风险说明和安全 Review；
- 实际执行 Root、Frida、Hook、逆向分析、协议解密、签名校验绕过、完整性检查修改或漏洞利用时；
- 涉及授权范围、系统修改、合规边界、失败原因或潜在风险时；
- 精确术语会直接影响工程判断或验收时。

例如，实际使用 Frida Hook 时不能只写“数据观察”；实际修改签名校验时不能只写“环境适配”。

### 禁止

- 不得通过改名、同义替换或模糊表达规避安全策略、权限检查、Review 或 User 授权；
- 不得弱化真实风险，也不得把普通被动研究夸张成攻击行为；
- 不得在策划主流程堆叠不必要的底层术语；必要技术细节应放在维护文档或技术附录。

## Required Propagation

请在同一 TASK-0023 分支完成以下最小传播，不新建 Task：

1. 在 `standards/PLANNER_WRITING_STYLE.md` 增加“技术术语与风险表述”章节，或建立一个单独的 canonical terminology standard 并由该文件引用。
2. 更新 `bootstrap/chatgpt/00_CORE_RULES.md`，明确该规则适用于所有 AI。
3. 更新根 `AGENTS.md`、`bootstrap/AGENTS.md`、`bootstrap/chatgpt/PROJECT_INSTRUCTIONS.md` 和 ChatGPT Bootstrap，使 ChatGPT、Codex 与其他 Agent 启动时读取该规则。
4. 为 `bootstrap/generic-agent/` 增加稳定入口或引用，确保 Generic Agent / Trae / DeepSeek 也读取同一标准。
5. 将标准纳入 Workspace Context / Source refresh；更新 Task、CHANGELOG、Handoff 和 Registry，并重新运行现有 Task、Context、Memory 与 Doctor 验证。

## Acceptance for Round 2

- 所有主要 Agent 入口均引用同一条 canonical 术语规则；
- 默认表达与必须精确表达的例外均写清楚；
- 明确声明不得用术语调整规避安全系统或隐藏真实行为；
- 不修改 TASK-0022、Cash Frenzy、Huuuge、Document Assistant 或 Workspace Sync 模式；
- Product Roadmap 和 Idea Governance 主体不退化；
- 完成后继续等待 ChatGPT Review，不自动合并 main。
