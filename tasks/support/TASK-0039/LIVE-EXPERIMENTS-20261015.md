# TASK-0039 实验持续记录

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

