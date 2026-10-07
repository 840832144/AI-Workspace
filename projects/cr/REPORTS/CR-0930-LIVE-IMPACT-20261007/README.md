# CR 9.30线上效果复盘 — 脱敏交付导航

[TASK-0038](../../../../tasks/TASK-0038-CR-9-30.md) / Changes Requested / 2026-10-07。此目录不保存经营结果。最终主交付已改为公司内部飞书原生文档，仅允许去敏汇总、必要分母和精选图；完整Excel继续留本机，经营结果不进public Git。首轮“不上传飞书”属于增补授权前的历史边界。

## 当前飞书交付

- 标题：CR 9.30更新效果复盘｜制作人版｜数据截至2026-10-06；[完整规格及首轮Review限制](FEISHU_DELIVERY.md)。
- 本机展示源稿`FEISHU_REPORT.md`和CLI XML草稿已完成；6章、16张原生窄表、4张精选聚合图。固定首轮快照，没有重查D7或线上全量。
- 原始/两套共同权重各写覆盖，成长保留阶段与完成者限定；旧比例区间重叠推理已删除。原Excel为首轮历史底稿，旧文字应结合当前展示修订阅读；未改原数值或重建工作簿。
- 云文档链接：尚无。实际CLI用户登录态缺失，搜索/读取均返回`token_missing`，在写入前停止；未自动改bot、创建副本或扩大权限。登记侧未发现同题，用户云空间查重仍待登录恢复。
- 恢复后依次完成目标目录/查重、创建或更新、正文/图表/内部权限回读、唯一文档导航中心登记和回读。仅在整条流程完成后回Review；当前不冒称正式交付成功。

## 本机受控交付

受控包别名：`cr-0930-live-review-20261007/outputs/TASK-0038/`。实际绝对路径在交付消息中提供，不固化到脚本或工作簿。

|文件|用途|
|---|---|
|CR_0930_线上效果复盘_2026-10-06.xlsx|八页制作人版，结论、同龄比较、分母及缺口|
|CR_0930_复盘结论_2026-10-06.md|会议短报告，区分好/坏/异常及未确认原因|
|SCOPE_AND_METRICS.md|生产项目、时区、成熟期、真实事件映射与发布边界|
|QUERY_EVIDENCE_INDEX.md / queries/|实际查询、UTC取数时刻、运行证据及替代关系|
|aggregate-results.controlled.json|完成的聚合与补充分层；完整响应另存受控工作目录|
|report-model.controlled.json|Excel受控输入；不含真实UID/订单，但仍为经营资料|
|VALIDATION.md / workbook-validation.json|数据、公式、文件和视觉核验及未验证项|
|FEISHU_REPORT.md / CLI XML草稿|去敏原生正文的受控展示源，不进入public Git|
|FEISHU_VALIDATION.local.json / 精选图|本轮定向验证与4张独立聚合图；非整页截图、非附件替代|

八页依次为：复盘总览、新增活跃、新增留存、付费留存、成长体验、经济与活动、异常与建议、口径与覆盖。简单派生保留公式；线上分位数/留存等依照查询证据，不声称Excel能重跑线上查询。D7未成熟为空，不绘成0。

## 公开方法与工具

- [方法和分母](METHODS.md)
- [脱敏验证](VALIDATION.md)
- [Python入口](tools/build_review_workbook.py)、[表格渲染适配器](tools/build_review_workbook.mjs)、[保存后验证器](tools/verify_review_workbook.py)

Python 3负责执行入口和只读验证；渲染适配器调用现有`@oai/artifact-tool` Node库，不安装或升级依赖。`openpyxl`仅用于保存后只读核对，不用于创作工作簿。运行环境从当前Host已批准的workspace dependencies取得，脚本不查找或复制凭据。

```text
python tools/build_review_workbook.py --node <approved-node> --runtime-node-modules <approved-node-modules> <controlled-model.json> <controlled-output-directory>
python tools/verify_review_workbook.py <controlled-output-directory>
```

适配器只解析传入的既有Node依赖目录，无需在Git工作区安装依赖。工具不连接数数、SVN或外部服务；输入必须为本任务已完成的受控模型，输出写到仓库外。查询或分析的复跑另需遵守当前数据权限与任务范围，不能把展示生成器当作线上分析本身。

云端交付等待CLI用户登录恢复；当前Changes Requested，完成文档与导航回读后交ChatGPT轻量Review。真实配置发布、冻结、数数资产变更、PR合并与reservation finalize均未执行。Subagents: none。
