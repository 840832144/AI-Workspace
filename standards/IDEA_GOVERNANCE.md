# Idea Governance

- Status: Review / Waiting for ChatGPT Review
- Related Task: `TASK-0023`
- Canonical Product Roadmap: `docs/roadmaps/PRODUCT_ROADMAP.md`

## 目标

长期产品想法不能只停留在聊天。ChatGPT、User 或其他 AI 在游戏策划项目中产生的产品能力、长期优化、Workflow、Capability、Collector 方向或 UX 改进，必须经过防重与分类，进入 Product Roadmap 的 `Current`、`Backlog`、`Ideas`、`Done` 之一，或明确判定为不值得长期保留。

## 对象边界

- Product Roadmap：长期产品方向的唯一规划入口。
- Task：一次获得授权、可执行且可验收的工作，不由 Roadmap 自动生成。
- Documentation Hub：正式云文档导航，不保存产品优先级。
- Knowledge：研究事实、证据和分析，不保存产品排期。
- Memory：帮助召回来源与长期决定，不替代 Product Roadmap。

## ChatGPT 自动判断规则

当 ChatGPT 在任何项目聊天中主动提出新的长期产品方向时，必须在回复完成前判断：

1. 是否值得跨对话长期保留；一次性修辞、小修复和当前 Task 已包含的实现细节不进入 Roadmap。
2. 是否与 Roadmap 现有条目重复；重复时更新原条目的来源、条件或说明，不创建同义条目。
3. 分类：
   - `Current`：正在开发，或 User 已批准即将开发；
   - `Backlog`：大概率会做，但尚未批准进入当前开发；
   - `Ideas`：长期设想、待验证方向或探索性建议；
   - `Done`：已有实现、验证和正式 Review 证据。
4. 在对应 Task 收尾时通知 Codex 更新 Product Roadmap；不依赖 User 再次提醒。

ChatGPT 本身没有批准 Git writer 时，不得声称已经更新 Roadmap，应输出最小 Idea Handoff。

## 最小 Idea Handoff

```text
Idea title: <稳定、可防重的名称>
Suggested section: Current | Backlog | Ideas | Done
Value: <一句话产品价值>
Source: <项目 / Task / Review / 对话日期>
Related object: <可选项目、Capability、Workflow 或 Task>
Evidence / gate: <为什么这样分类，下一次升级需要什么>
Duplicate checked: yes | no
```

Codex 收到后必须读取最新 Product Roadmap，完成防重、分类、Git 更新、必要的飞书发布与回读，再把结果写入 canonical Task / Handoff。

## 状态迁移

```text
Ideas → Backlog → Current → Done
```

- 可以跨级，但必须有 User 决定或可复查证据。
- `Backlog → Current` 需要 User 批准、已存在 active canonical Task，或正式 Review 明确授权为即将开发。
- `Current → Done` 需要实现、测试/运行证据和正式 Review；仅完成设计、建目录或写 Roadmap 不算 Done。
- 被拒绝、暂停或 superseded 的长期想法可保留在 `Ideas` 并标明原因；不得伪装为 Done。

## 更新与发布

1. Git 源稿先更新并通过 Review-ready 校验。
2. 正式飞书 Roadmap 搜索防重后原位创建或替换。
3. 执行正文回读、企业内可编辑权限回读、`register_document` 和文档导航中心回读。
4. 项目全景说明只增加 Roadmap 链接，不复制 Roadmap 正文。
5. Hub 或回读失败时保留已创建文档、不重复创建，返回失败并等待修复。

## 安全与质量

- 不保存完整聊天、Secret、Raw Capture、账号信息、完整响应、私有 Registry 或租户文档 ID。
- 不把未经批准的 Idea 写成 Current，不把 Planned 写成 Done。
- 不因更新 Roadmap 修改业务仓库、运行环境、Workspace Sync 模式或其他 Task。
- 面向策划使用中文；专有名词和稳定技术术语可保留英文。
