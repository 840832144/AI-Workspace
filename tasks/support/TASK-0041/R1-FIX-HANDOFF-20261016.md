# TASK-0041 Round 1代码修订交接

- Kind: implementation-handoff；关联唯一[TASK-0041](../../TASK-0041-BINGO-CORE-DEMO.md)。
- Date: 2026-10-16；原PR #21，Task合法状态In Progress，Review结论Needs changes，未Accepted。
- 唯一评审：[CHATGPT-REVIEW-1.md](CHATGPT-REVIEW-1.md)，来源052bdaa66be6f85b46782e8a2985cb35ef41b7f0，原文通过cherry-pick纳入，历史不覆盖。
- 业务：D:\BingoCoreDemo，codex/task-0041-core-demo，82c2dd98a8a73749745fe4b068a0e980785755ab，仅本地Git，无批准远端。
- 最新User指令：“修复完就行了 先跳过验证”。这条指令覆盖本轮立即执行R3的顺序，不删除原验收条件。
- Subagents: none。

## 已修改与待验证

|项|代码修改|当前证明/状态|
|---|---|---|
|R1|BingoClient的GET与POST统一调用ApplyState；拒绝更小revision、同revision跨roundId或更早elapsedMs。通过服务X-Bingo-Instance与首次session绑定，身份改变/缺失则停收状态和动作，提示重启；不自动重发动作|仅代码审阅，未编译、未执行可控乱序替身或原生实跑；不标Closed|
|R2|Build.ps1首条dotnet run取消--no-restore，恢复隐式依赖恢复，保留非零退出检查|未在干净目录运行正式构建，未复制缓存，不标Closed|
|R3|保留原评审的1/2/4/6卡选择/取消/操作/结束/返回再开、道具固定案例、当前HTTP、离线与独立解压包要求|按User指令暂缓，未执行，不缩减成旧47项/49条或十局填充率|

未修改Bingo.Core玩法、规则配置、九道具或结束补填。客户端与服务增加配套会话身份，新源码不能与旧服务混搭。构建入口仍包含规则与Unity验证，因此本轮不执行Build，也不把旧二进制重新打包冒充修复包。源码归档为D:\BingoCoreDemo\artifacts\TASK-0041-R1-code-only-82c2dd9.zip；不是可玩包或新实测证据。

原0.2.1/08529d8试玩包和所有旧失败/测试证据保留，尚不含此次修改。后续验证从新候选开始，固定准确源码/配置/二进制版本后再补短场景；本轮没有操作运行中的Demo或原客户端。

## DSH与后续兼容方案

DSH材料状态纠正为已收到、部分关键结论待补证。本轮直接读取DSH-Delivery-Review-20261015.zip的复核正文及Round 1，不假称重跑原设备或独立复核全部原始附件。业务docs/DSH-EVIDENCE.md、RULES.md、QUESTIONS.md对应Q1–Q6保留来源/采用值/差异；九道具、补填及User四条修正规则均不被缺证推断覆盖。

原客户端兼容仅整理[下一步方案](ORIGINAL-CLIENT-NEXT-PLAN-20261016.md)，更新已有Roadmap Idea，不新建执行Task；不并入当前验收，不恢复TASK-0039，不新增技术权限。

## 治理与边界

main898358f已fetch且为本分支祖先。Workspace Sync本轮入口实际执行：ON_DEMAND、provider不可用、stale6、conflict0；不将云状态称已同步。Task/Status/Handoff与Registry按现有工具更新；产品运行验证按User要求跳过，Registry属于治理一致性检查，单独报告。

首次Registry扫描拒绝把Needs changes写作canonical Status；该值保留为评审结论，Task改用工具支持的In Progress，再重建校验。不修改校验器或弱化规则。

等待后续验证/Review安排，不自动合并、发布、提交SVN或finalize。Roadmap仅更新Git条目，本轮未发布云文档。
