# TASK-0040 受控产物导航

本页只公开脱敏导航；完整配置、数值和分析实现保留在User本机。

- 任务根目录：`%LOCALAPPDATA%/AI-Workspace/101-card-pack-usd-20261013/`。
- 正式工作簿：`outputs/TASK-0040/101_卡包美元价值.xlsx`。
- 口径说明：`outputs/TASK-0040/101_卡包美元价值_说明.md`。
- 复算入口：根目录 `一键计算.ps1`；核对入口 `一键检查.ps1`。执行需要本机既有Codex随附运行时，不安装服务，不更新源配置。
- 分析与独立检查：`scripts/calculate.py`、`scripts/check_results.py`、`scripts/check_workbook.py`；工作簿作者脚本为 `scripts/build_workbook.mjs`。
- 来源：`input_manifest.json`、`code_manifest.json`；参数与结果在 `outputs/TASK-0040/model_parameters.json`、`results.json`、`coverage.json`、`weight_sensitivity.json`。
- 验证：`outputs/TASK-0040/validation.json`、`workbook_validation.json`、`workbook_build_checks.json`；失败尝试与修正保留在同目录 `执行记录.md`。

主表展示明确基准的单次领取窗口条件估值，内含全部目标包及变体，不提供未经确认的统一面值或真实售价。合成玩家状态、统计误差、结构上不可能事件、未来收益边界分别标注。没有真实购买或线上开包证据。

公共仓库不包含业务脚本、源表、源码摘录、价格明细、原始日志或私有地址。ChatGPT需要查看完整数值时应由User通过受控本机产物提供，不能从本公开摘要推定已经独立审过数值。Subagents: none。
