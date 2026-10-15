# TASK-0039 原实例启动阻塞

## 2026-10-15 后续：原实例启动崩溃，新十局尚未登记

User报告已返回大厅，并要求沿用原TASK-0039冻结f95ba94、预登记位置14–23。实时只读检查发现游戏进程已退出、前台为Google Play；控制锁可取得，无自动玩或观察器进程，原采集器仍在。f95ba94工作树干净、原109项回归有效，没有改候选或因新回合重跑计量。

通过包管理器给出的原Launcher组件正常启动一次，未force-stop、清数据或修改安全设置；游戏约2秒后原生崩溃，未进入大厅。系统另有此前同类崩溃记录。当前版本仍1.58.3/393，最后更新时间2026-10-13；堆栈含libpairipcore.so+0x4ae38与翻译执行区，SIGSEGV/SEGV_ACCERR。仅凭这些证据不能判定保护拒绝或ARM翻译故障，未修改保护组件或恢复已停止的emulated路线。

本次新增0登记/0购买/0填格，原累计13位置/112毛票/3933.070主动秒，剩16位置/272票/6866.930秒。设备只读和一次正常启动均记入原账本，历史不清零。位置14–23仍是待执行计划，不能冒称已正式预登记或游戏成绩。原运行入口f95ba94保留；恢复大厅、来源、实时价格/钱包和整批预算后直接继续，不逐局等Review。

已形成受控DSH-STARTUP-CRASH-20261015.md并请求User转述DSH：只问可证实原因、最小原权限内恢复或0票取证、停止判据；若涉及重启实例及临时挂载/采集连接影响，须明确范围，不推定授权。未重启模拟器或采集器、换实例、重装/重打包、扩权或自动充值。

受控目录：%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\execution16\hook\dsh-review；experiment6-return-check.json、experiment6-restored.json、experiment6-exit.txt、experiment6-native-crash.txt、experiment6-environment.json及控制进程清单。原件不上Git。Task In Progress，当前阻塞是游戏启动失败；真实十局仍未交付，不把0购买称为失败十局。原PR #16/#17、历史Review和pending-main保留，不合并、发布、SVN或finalize。Subagents: none。

