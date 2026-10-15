# Bingo核心玩法本地Demo 状态

- Task: [TASK-0041](../../tasks/TASK-0041-BINGO-CORE-DEMO.md)
- Status: In Progress；Review result: Round 1 Needs changes，唯一评审052bdaa已纳入。User最新要求先修复、跳过验证；未Accepted。Gate 0登记d65039f保留。
- 规格：完整EXECUTION_SPEC.md f42e249/330f754，最新四项规则修正生效。
- 治理：独立linked worktree `D:\AI-Workspace-bingo-core-demo`，沿用PR #21。
- 业务工程：已建 `D:\BingoCoreDemo`；无批准远端，先本地Git。
- 当前候选：业务08529d8／原生包0.2.1；47项核心、Unity同核心一致性、Windows构建、真实Launch/Check与客户端连接通过。当前User试玩49条实际输入复算一致。此前c31f0c8的39项HTTP属于历史证据，不混版。
- User接手普通人工试玩；Codex负责规则、协议、复算与启停等专业测试，人工结果单独记录。
- 当前环境：.NET SDK10.0.402、Unity6000.6.5f1、Hub3.22.3、官方CLI1.0.0-beta.13；真实构建许可可用。团队模板尚未提供。
- TASK-0039：User暂停，原账本保留，不恢复原实例/采集/自动玩。
- Subagents: none。

## 2026-10-16 Round 1当前状态

业务82c2dd98a8a73749745fe4b068a0e980785755ab：R1统一GET/POST状态应用，绑定服务instance，过滤旧revision/同revision倒退时间，服务更换时停用当前会话且不重发；R2首次dotnet run恢复隐式restore。玩法核心和配置未改。按User“先跳过验证”，本轮未编译、未跑规则/HTTP/原生/断外网测试，未生成新可玩包，R3暂缓。旧0.2.1包不包含本次修改。当前入口为[修订交接](../../tasks/support/TASK-0041/R1-FIX-HANDOFF-20261016.md)，下文旧候选证据保留作历史，不替代本轮验证。

DSH状态纠正为“已收到材料及复核，部分关键结论待补证”；RULES/QUESTIONS已对应登记。未接受“七道具/无补填”等缺证推断。原客户端兼容只完成下一步方案，不执行原游戏操作。Workspace Sync本轮入口成功运行，provider不可用、6项stale/0conflict；当前任务依据最新Git与User指令，不引用stale云状态。

- 当前入口：[Review交接](../../tasks/support/bingo-core-demo-20261015/CHATGPT-REVIEW-HANDOFF-20261016.md)；历史过程保留[阶段实测](../../tasks/support/bingo-core-demo-20261015/IMPLEMENTATION-PROGRESS-20261015.md)。User原话“看起来没啥太大问题”作为初步体验反馈，完整验收缺口仍列明。

- 版本边界：已交浏览器试玩包c31f0c8不变；最新426b145独立端口HTTP复测被自动审批拦截，保留待验证，不混用成绩。

- 最新环境实测：Hub3.22.3.65535保留；旧6.3下载已以curl56停止且未安装，User另在Hub安装的6000.6.5f1已通过CLI结构检查和真实构建。官方Unity CLI1.0.0-beta.13已安装，构建脚本按项目版本查询已安装Editor，未重复下载/安装。首次CLI许可查询失败，但随后Editor实际取得许可并退出0，不再将许可证作为当前阻塞。
- 原生试玩入口：D:\BingoCoreDemo\artifacts\packages\BingoCoreDemo-0.2.1-unity-preview.zip（08529d8）；受控Review包TASK-0041-Review-0.2.1-20261016.zip位于同工程artifacts。没有安装Pipeline/MCP/全局Agent插件，没有创建Unity Cloud项目。
- 启动故障复核：旧0.1.0占18741，按User要求经自有Stop入口切换0.2.0后，窗口存在/服务Lobby曾被误判为客户端已就绪；随后零session/catalog请求、Unity连向系统代理29290及User截图证实仍连不上。ce87d64的“客户端持续请求”结论撤回，失败证据native-startup-handoff.json保留。
- 当前试玩：1卡/默认Bet1，21次填格请求中19接受/2因not_called拒绝，R1/N3各使用1次，手动结束获得1 Bingo；49条记录复算通过。未记录返回再开，其他卡数/全部九道具未做当前原生逐项验收；系统代理未改。证据artifacts/review-20261016/user-play-summary.json。
- 保留缺口：新版完整HTTP及其他Unity卡数端到端、断外网、干净试玩机/团队模板、dsh规则二次核验。历史审批拒绝的测试未绕过。下一步ChatGPT Review；不合并、发布、SVN或finalize。
