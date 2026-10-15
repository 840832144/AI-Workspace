# TASK-0039 实验持续记录

## 2026-10-15 后续：原实例启动崩溃，新十局尚未登记

User报告已返回大厅，并要求沿用原TASK-0039冻结f95ba94、预登记位置14–23。实时只读检查发现游戏进程已退出、前台为Google Play；控制锁可取得，无自动玩或观察器进程，原采集器仍在。f95ba94工作树干净、原109项回归有效，没有改候选或因新回合重跑计量。

通过包管理器给出的原Launcher组件正常启动一次，未force-stop、清数据或修改安全设置；游戏约2秒后原生崩溃，未进入大厅。系统另有此前同类崩溃记录。当前版本仍1.58.3/393，最后更新时间2026-10-13；堆栈含libpairipcore.so+0x4ae38与翻译执行区，SIGSEGV/SEGV_ACCERR。仅凭这些证据不能判定保护拒绝或ARM翻译故障，未修改保护组件或恢复已停止的emulated路线。

本次新增0登记/0购买/0填格，原累计13位置/112毛票/3933.070主动秒，剩16位置/272票/6866.930秒。设备只读和一次正常启动均记入原账本，历史不清零。位置14–23仍是待执行计划，不能冒称已正式预登记或游戏成绩。原运行入口f95ba94保留；恢复大厅、来源、实时价格/钱包和整批预算后直接继续，不逐局等Review。

已形成受控DSH-STARTUP-CRASH-20261015.md并请求User转述DSH：只问可证实原因、最小原权限内恢复或0票取证、停止判据；若涉及重启实例及临时挂载/采集连接影响，须明确范围，不推定授权。未重启模拟器或采集器、换实例、重装/重打包、扩权或自动充值。

受控目录：%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\execution16\hook\dsh-review；experiment6-return-check.json、experiment6-restored.json、experiment6-exit.txt、experiment6-native-crash.txt、experiment6-environment.json及控制进程清单。原件不上Git。Task In Progress，当前阻塞是游戏启动失败；真实十局仍未交付，不把0购买称为失败十局。原PR #16/#17、历史Review和pending-main保留，不合并、发布、SVN或finalize。Subagents: none。


## 2026-10-15 当前f95ba94：修复已推送，等待超时局人工收尾

75f5aa4新增位置13实际报价/扣减12票，正常UI开关已点击，但5秒内存档Auto仍true；候选在首次填格前错误退出，0次自动填格，冻结缺少完整闭局/终态，不给填充率。闭局后同一文件自然变为Auto=false。失败来源与版本完整保留，不追认成功；退款界面不冲减累计毛消费或位置。

已修复并推送[f95ba94](https://github.com/840832144/AI-Workspace/commit/f95ba94)：可选自动道具配置最多一次正常UI尝试和1秒读回，未确认单列记录，不阻断独立合法的格子输入，不触发重试开关。未直接写存档/内存、调用业务方法或发协议；设置状态不进入计分，PowerUp仍Unknown，既有价格、来源、STOP和300秒校验保留。109项完整回归通过（30.254秒、exit0、正式账本不变），含存档迟到不阻断与不重复点击。新候选尚未购买。

本轮5次入口尝试、4次新增购买共48票；累计13位置/112毛票/3904.975主动秒，剩16位置/272票/6895.025秒，仍能预留位置14–23的新十局。原3定位保留。当前停控，上一局超过300秒后停在ROUND REFUND领取提示，已请求User手动领取回大厅；不得代点超时收尾，不因等待清零账本。收到返回后沿用原任务连续推进，不额外请求整任务或额度批准。

受控入口：%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\execution16\hook\dsh-review\CURRENT-EXPERIMENT-6.md；recompute_experiments.py已真实复跑，EXPERIMENTS-RECOMPUTED.json分列原候选结果与当前解析研究复算。05c5d6e零购买；3d8d9a3研究37/45/U6/未填2；f9d6a39原终态缺失且User最后两格介入；c6a8e74原31/37/U6/未填0；75f5aa4闭局不完整。所有原批均1/10或未登记，不能拼版、挑局或称正式通过。Task In Progress，未交付完整十局。

最新main898358f安全同步、原pending-main保留；本次继续原PR #16/#17并验证Registry。尚未请求最终Review，不合并、发布、SVN、扩权或finalize。Subagents: none。


## 2026-10-15 当前候选75f5aa4：完整运行继续

实验额度接纳0e1a3c5保持有效，原PR #16/#17、历史Review和所有失败批次保留。本轮三次完整购买均12票，候选3d8d9a3、f9d6a39、c6a8e74各1局，不能拼成同版成绩。f9d6a39最后两个格User介入，原冻结终态不足；c6a8e74修复后终态及独立闭局通过、自然回大厅，31次自动输入均有自然受理，E37/N31/Unknown6/确认未填0，下界83.78%，六格均PowerUp且不计自动贡献。下一局遇奖励飞行动画，买前拒绝、无第二次购买。

新候选[75f5aa4](https://github.com/840832144/AI-Workspace/commit/75f5aa4)保留Bingo覆盖恢复、末球补排、闭局等待真实终态、评分前安全结算；新增最多30秒等待大厅/面板动画，最多打开面板一次。首次填格前读取当前账号Auto偏好，需要时通过原游戏开关关闭自动道具并回读Auto=false，之后重新标定。不写存档、内存、返回值或协议，不调用游戏方法，不扩大技术权限；历史PowerUp继续Unknown，分母/计量不变。

109项离线与实际函数/CLI集成回归通过（31.262秒，exit0，正式账本不变），不是十局实测。最新启动前账本100票/3826.054秒/12位置，含一段取消的本地全历史只读扫描墙钟保守计时；剩17位置/284票/6973.946秒。正按冻结75f5aa4预登记新十局位置13–22。实际结果统一更新，当前未达成十局目标。

受控入口：%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\execution16\hook\dsh-review\CURRENT-EXPERIMENT-5.md，实际入口production-experiment-start-2..5、tests-powerup-panel-final.txt、原账本runtime/budget.jsonl。源日志/账号/余额/卡面/内存仅受控本机。最新main898358f安全fetch且为祖先；沿用原pending-main，不新建任务、不finalize。Subagents: none。

