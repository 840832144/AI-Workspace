# TASK-0039 实验持续记录

## 2026-10-15 当前候选75f5aa4：完整运行继续

实验额度接纳0e1a3c5保持有效，原PR #16/#17、历史Review和所有失败批次保留。本轮三次完整购买均12票，候选3d8d9a3、f9d6a39、c6a8e74各1局，不能拼成同版成绩。f9d6a39最后两个格User介入，原冻结终态不足；c6a8e74修复后终态及独立闭局通过、自然回大厅，31次自动输入均有自然受理，E37/N31/Unknown6/确认未填0，下界83.78%，六格均PowerUp且不计自动贡献。下一局遇奖励飞行动画，买前拒绝、无第二次购买。

新候选[75f5aa4](https://github.com/840832144/AI-Workspace/commit/75f5aa4)保留Bingo覆盖恢复、末球补排、闭局等待真实终态、评分前安全结算；新增最多30秒等待大厅/面板动画，最多打开面板一次。首次填格前读取当前账号Auto偏好，需要时通过原游戏开关关闭自动道具并回读Auto=false，之后重新标定。不写存档、内存、返回值或协议，不调用游戏方法，不扩大技术权限；历史PowerUp继续Unknown，分母/计量不变。

109项离线与实际函数/CLI集成回归通过（31.262秒，exit0，正式账本不变），不是十局实测。最新启动前账本100票/3826.054秒/12位置，含一段取消的本地全历史只读扫描墙钟保守计时；剩17位置/284票/6973.946秒。正按冻结75f5aa4预登记新十局位置13–22。实际结果统一更新，当前未达成十局目标。

受控入口：%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\execution16\hook\dsh-review\CURRENT-EXPERIMENT-5.md，实际入口production-experiment-start-2..5、tests-powerup-panel-final.txt、原账本runtime/budget.jsonl。源日志/账号/余额/卡面/内存仅受控本机。最新main898358f安全fetch且为祖先；沿用原pending-main，不新建任务、不finalize。Subagents: none。

