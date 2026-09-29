---
name: cr-svn-submit
description: 安全提交 Cash Royal 数值策划 SVN 工作副本。用于用户要求检查、添加、提交、自动提交或核验 CR_design 变更时，调用 Python 3 工具完成更新、仓库校验、风险拦截、svn add、svn commit 和提交后复核；对删除、冲突及其他项目文件采用显式授权或拦截。
---

路径基准：本文相对路径均指 CR 项目目录 `projects/cr/`。先继承 Workspace 根 `AGENTS.md`，再读取本项目 `AGENTS.md`；Git 日常资料写入与公司 SVN 正式配置提交按各自授权处理。

# CR SVN 安全提交

## 必读

执行前读取 `references/safety-policy.md`。不得在命令、配置或提交说明中保存账号和密码。

## 中文提交日志

- 中文提交说明必须通过 `svn_submit.py -m` 传入，由工具写入 UTF-8 临时日志文件并使用 `svn commit --encoding UTF-8 --file` 提交。
- 禁止在 PowerShell、批处理或其他终端中直接执行包含中文的 `svn commit -m`，避免系统代码页导致仓库日志乱码。
- 禁止让 Windows PowerShell 5 执行含中文常量的 UTF-8 无 BOM 脚本来生成日志；脚本源码会先被错误解码。优先使用仓库内 Python 3 工具。
- 提交后读取最新 revision 的日志，核对作者和完整中文说明；出现乱码时不得宣称提交完成。

## 工作流

1. 先核对公司 SVN 的目标项目、URL、dev/trunk、revision、授权文件及现有策略。指定该工作副本根目录与对应策略运行只读演练；不能将 Git 资料目录自动当作 SVN 工作副本：

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python .\数值策划\工具\svn_submit.py --root "明确的公司SVN工作副本" --config "该工作副本已批准策略的绝对路径"
```

2. 阅读状态统计和路径清单。发现冲突、缺失、临时文件、其他项目文件或校验失败时停止，先处理原因。
   - 若临时文件是用户 Excel 会话产生的无关 `~$*.xlsx` 锁文件，不得擅自删除；在核验仓库身份、HEAD、目标清单与远端增量后，可使用仅包含授权文件的独立稀疏工作副本，且 dry-run 结果必须恰好等于授权清单。
3. 用户已明确要求提交且演练通过时执行：

```powershell
python .\数值策划\工具\svn_submit.py --root "明确的公司SVN工作副本" --config "该工作副本已批准策略的绝对路径" --execute -m "清晰、可追溯的提交说明"
```

4. 工具自动执行 `svn update`、仓库校验、风险检查、新文件添加、提交和干净状态复核。
5. 报告提交版本、变更数量和剩余状态；不得仅根据命令退出码宣称成功。
6. 使用 `svn log -r <revision>` 复核提交作者和中文日志可读性。

## 高风险参数

- 只有确认计划删除的文件时使用 `--allow-delete`。
- 不存在 `--allow-protected-change` 参数；不可为了通过校验自行放宽策略。
- 只有明确知道工作副本已同步或网络不可用时使用 `--skip-update`。
- 不得自动添加放宽安全策略的参数。

## 完成标准

- 使用 Python 3 和项目内策略文件，未引用个人电脑工作副本路径。
- 提交前仓库校验为 0 个错误。
- 提交后没有未版本化文件、冲突或待提交变更。
- 输出可核验的 SVN 版本号。
