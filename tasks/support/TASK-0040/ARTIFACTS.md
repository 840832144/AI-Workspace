# TASK-0040 受控产物导航

本页只公开脱敏导航；完整配置、数值和分析实现保留在User本机。

- 任务根目录：`%LOCALAPPDATA%/AI-Workspace/101-card-pack-usd-20261013/`。
- 正式工作簿：`outputs/TASK-0040/101_卡包美元价值.xlsx`。
- 口径说明：`outputs/TASK-0040/101_卡包美元价值_说明.md`。
- 本轮核心复核包：`outputs/TASK-0040/TASK-0040_核心计算复核包.zip`。仅补评审5505803167剩余R1，不含原主表/截图/全量配置/游戏源码。解压后运行`python scripts/review_core.py`或随包`运行复核.ps1`；README、预期结果与工作簿行号定位均在包内。
- 复核包真实验证：`core-review-package/verification-unpacked/TASK-0040_核心计算复核包/actual/validation.json`，最终ZIP独立解压后运行；53项通过，7个旧整包例、5组增量对照和5条固定路径。依赖声明在包内requirements.txt，没有安装新服务。
- 复算入口：根目录 `一键计算.ps1`；核对入口 `一键检查.ps1`。执行需要本机既有Codex随附运行时，不安装服务，不更新源配置。
- 分析与独立检查：`scripts/calculate.py`、`scripts/check_results.py`、`scripts/check_workbook.py`；工作簿作者脚本为 `scripts/build_workbook.mjs`。
- 来源：`input_manifest.json`、`code_manifest.json`；参数与结果在 `outputs/TASK-0040/model_parameters.json`、`results.json`、`coverage.json`、`weight_sensitivity.json`。
- 验证：`outputs/TASK-0040/validation.json`、`workbook_validation.json`、`workbook_build_checks.json`；失败尝试与修正保留在同目录 `执行记录.md`。

主表展示明确基准的单次领取窗口条件估值，内含全部目标包及变体，不提供未经确认的统一面值或真实售价。合成玩家状态、统计误差、结构上不可能事件、未来收益边界分别标注。没有真实购买或线上开包证据。

公共仓库不包含业务脚本、源表、源码摘录、价格明细、原始日志或私有地址。[Round 2](../../../reviews/TASK-0040-CHATGPT-REVIEW-2.md)已实际读取并运行User提供的本ZIP，独立复核核心金币链，结论Accepted、R1 Closed；接受范围及未验证事项以该评审为准。本轮只更新治理导航，不修改或重建上述受控产物；PR仍OPEN、未合并或finalize，未Complete。Subagents: none。
