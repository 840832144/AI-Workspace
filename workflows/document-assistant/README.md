# Document Assistant Workflow

## 目标

通过 Document Capability 创建或维护正式公司文档，并确保每份正式飞书文档都可从唯一的《AI Workspace｜文档导航中心》找到。Git 是规则、Task、ADR、状态和实现的真相源；导航中心只负责飞书导航。

## 正式文档输入

- 唯一标题和正文来源；
- 一句话介绍；
- 固定分类之一：`🏗 项目介绍`、`🎮 游戏研究`、`🧰 工具`、`📄 部署`、`📊 报告`、`📚 知识库`、`📝 标准 / Workflow / Capability`、`📦 Archive`；
- 状态之一：`Draft`、`Review`、`Accepted`、`Archived`；
- 权限策略；未明确指定时使用企业内可编辑。

## 创建流程

1. 使用 `search_documents` 按标题确认不存在正式文档或唯一 Hub 重复项。
2. 调用 `create_document` 创建正式文档并应用权限。
3. 使用 `get_document` 回读标题与正文；失败时保留文档并停止。
4. 调用 `register_document` 写入分类、简介与状态，由 Document Assistant 重建唯一 Hub。
5. 回读文档导航中心，确认新链接只出现一次、字段完整、无敏感信息。
6. 只有全部成功后才报告完成。

`create_document` 的当前批准实现会自动执行第 3–5 步；Workflow 仍按结果证据逐项验收。导航中心更新失败时，不删除已创建文档、不重复创建，返回失败并等待修复；修复后对原文档调用 `register_document`。

## 更新流程

更新原文档时保持同一链接；正文写入回读成功后，调用 `register_document` 刷新简介、分类、状态或最后更新时间，再回读导航中心。不得人工编辑导航中心正文。

## 临时文档

只有烟测或一次性验证文档可以显式标记为 `temporary` 并跳过 Hub。验证结束必须通过受控清理删除；正式成果不得借此规避登记。

## 失败处理

- 同名导航中心超过一个、链接重复或回读不一致：fail closed，停止创建并报告治理冲突。
- 权限被企业策略拒绝：保留已创建文档，报告权限失败；不得创建副本。
- 导航中心登记失败：正式文档流程失败，但文档本身保留；不得重复创建，等待修复后登记原文档。
- Provider 不可用：报告 `Implementation unavailable`，不伪造完成状态。
