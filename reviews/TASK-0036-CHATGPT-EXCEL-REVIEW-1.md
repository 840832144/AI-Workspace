# TASK-0036 — 首版Excel产物Review与后续User决定

- Status: Needs changes
- Project key: CR
- Owner: ChatGPT
- Date: 2026-09-18
- Updated: 2026-09-18
- Canonical Task: [TASK-0036](../tasks/TASK-0036-CR-0922-PRODUCER-EXPERIENCE.md)
- Source: [PR #10 Excel产物Review](https://github.com/840832144/AI-Workspace/pull/10#issuecomment-5724542994)

本记录摘录评审结论及处理边界；完整原文保留在上述PR讨论。评审对象是User上传的Excel附件，不是最新Git commit，也不是重新审查已Accepted的数值模型。

评审确认首版14张前台页、隐藏SRC/CALC和公式追溯结构；其所审附件实际有394,378个公式、无公式错误或外部文件依赖。该计数只属于受评附件，不能用于后续本地候选或当前重做版。

必须修正：工作簿元数据泄露绝对本机路径，需要清理作者/本机信息；等级和价格长表缺少阅读概览与筛选，容易成为数据堆叠；大量复制公式影响飞书展示性能。评审没有重做已Accepted数值模型的独立验收。

[User最终决定](https://github.com/840832144/AI-Workspace/pull/10#issuecomment-5724897864)进一步明确：保留5000+行完整明细，采用“模块概览+明细”；真实源必须是固定r7013的trunk原始导出；本机master用相对外链，另生成无外链展示版。该决定覆盖首版自包含与仅压缩前台的方案，不得为简化展示删除明细。

当前修订方案与验收见[工作簿说明](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/WORKBOOK.md)。修订候选等待下一轮ChatGPT Review，本历史Needs changes记录不改写为Accepted。原数值报告Round 1 Accepted及“未独立连接SVN”的证据限制保持；不调参、不提交SVN、不冻结/发布、不合并或finalize。Subagents: none。
