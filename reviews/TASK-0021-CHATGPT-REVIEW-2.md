# TASK-0021 ChatGPT Review — Final Closeout

- Decision: **Needs changes（仅收尾项）**
- Reviewed branch: `codex/task-0021-documentation-hub`
- Reviewed AI-Workspace commit: `e951ebdb4cc74596a8732f3d7da8c11626e2ac08`
- Reviewed Document Assistant commit: `6cf1b13d5d00bdc7778233c5d3dfc059f7a8ea18`
- Review date: 2026-08-27
- Subagents observed: none

## Passed

Documentation Hub 的主体实现可以保留：唯一 Hub、八分类、14 份正式文档初始化、链接去重、正式文档自动登记、Hub 回读、失败时保留原文档并阻止重复创建、Document Assistant 32/32 测试、Workspace Task / Context / Memory 回归、`ON_DEMAND` 与 WATCH 未启用均符合当前要求。

## Required Fix 1 — 面向策划的中文标题

将现有飞书文档：

```text
AI Workspace｜Documentation Hub
```

原位重命名为：

```text
AI Workspace｜文档导航中心
```

要求：

1. 保持同一 document ID / URL，不创建副本；
2. 更新 Host-local Registry、Hub 自身条目、Workspace 文档规则和所有正式引用中的展示标题；
3. `register_document` 的稳定 alias / 防重键保持不变，不因中文标题变化重复创建 Hub；
4. 标题回读、唯一性、八分类、14 份正式文档和企业内可编辑权限继续通过。

## Required Fix 2 — 在项目全景说明中建立首要导航

原位更新飞书文档：

```text
Game Planner AI Workspace｜项目全景说明
```

在“一页式项目说明”结束后、进入后续详细章节前，新增一个醒目的原生区块：

```text
下一步：查看全部项目文档

AI Workspace｜文档导航中心
包含项目说明、进度、部署手册、游戏研究、报告、工具、知识与规范等正式文档入口。
```

其中“AI Workspace｜文档导航中心”必须是可点击链接，指向当前唯一 Hub：

```text
https://gfok27asqq.feishu.cn/docx/TXe8dulG3osX2kxJMK3cPiHWnHf
```

要求：

1. 原位更新项目全景说明，不创建副本；
2. 入口位置必须紧跟“一页式项目说明”，方便 User 先把项目全景说明发给策划，再由策划进入总目录；
3. 使用策划可理解的中文，不展示 document ID、Registry、MCP 或实现细节；
4. 更新后回读标题、区块位置、链接目标和企业内权限。

## Documentation Governance Confirmation

现有规则继续成立：所有正式云文档创建或正式更新后，必须完成文档回读、登记到唯一“AI Workspace｜文档导航中心”、Hub 回读；Hub 是面向人的导航入口，Git 和对应业务仓库仍是真相源。

## Acceptance for Final Closeout

完成上述两项后：

1. 搜索确认只有一个“AI Workspace｜文档导航中心”；
2. Hub 保持同一 URL、14 份正式文档、无重复链接、企业内可编辑；
3. 项目全景说明在一页式说明后可直接进入 Hub；
4. Document Assistant 和 Workspace 相关测试无退化；
5. 更新 TASK-0021、CHANGELOG、Handoff、Documentation Governance 文档和必要的 Source / Context 状态；
6. 重建并验证 `TASK_REGISTRY.yaml`，不得手工维护；
7. 合并 AI-Workspace 与 Document Assistant 对应分支，重启 MCP 会话后确认 `register_document` 出现在正式工具清单；
8. `ON_DEMAND` 保持，WATCH 不启用；
9. TASK-0021 更新为 `Accepted`，ADR-0007 同步为 Accepted，并记录最终 merge commit。

完成后返回：两个飞书安全链接、标题/正文/权限 readback、最终测试摘要、AI-Workspace 与 Document Assistant merge commit。