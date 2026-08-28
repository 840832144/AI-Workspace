# 数值工具

所有工具使用 Python 3，当前脚本仅依赖标准库。

## 数据同步

每位策划在当前终端配置自己的源目录；这些值不会写入仓库：

```powershell
$env:CR_DESIGNER_WORKBOOKS_DIR = "本机的 CR 策划源表目录"

# 预览
python .\数值策划\工具\sync_data_sources.py

# 确认后执行
python .\数值策划\工具\sync_data_sources.py --apply
```

同步只复制新增或内容变化的策划源表，不覆盖来源，不自动删除目标中多出的文件。程序配置不执行本地同步，分析时直接只读目标 `dev` 或 `trunk`。来源配置只声明环境变量名，见 `config/data_sources.json`。

## 构建知识目录

```powershell
python .\数值策划\工具\build_catalog.py
```

脚本使用 XLSX 的 Open XML 结构读取 Sheet 名、有效行列和表头预览，不依赖 Excel 客户端。

## 仓库验收

```powershell
python .\数值策划\工具\validate_repository.py
```

校验必需目录、Skill 结构、Python 语法、临时文件和知识库生成物。

## 新用户 Spin 串联模拟

```powershell
python .\数值策划\工具\simulate_new_user_spin.py `
  --config-root "目标dev或trunk的ExcelConfigExport\Excel" `
  --start-level 0 `
  --vip 0 `
  --start-coins 33600 `
  --target-level 15
```

创角账户初始金币为0；默认 `33,600` 是领取第1建筑满额产出后的老虎机启动资金。

脚本只读解析等级、Bet、解锁、新手 RTP、升级奖励、VIP 和前 20 Spin 建设币配置，
输出逐等级消耗、期望返还、进度和余额。结果是期望模型，不包含中奖方差和破产概率。

## SVN 安全提交

默认命令只读取状态并演练，不会添加或提交文件：

```powershell
python .\数值策划\工具\svn_submit.py
```

演练通过且已确认提交说明后，执行全流程自动提交：

```powershell
python .\数值策划\工具\svn_submit.py --execute -m "更新活动数值方案与推导脚本"
```

工具会依次更新工作副本、运行仓库验收、拦截冲突和风险文件、添加新文件、提交并复核工作副本。
删除文件默认中止，必须显式提供 `--allow-delete`。工具只使用系统已有的 SVN 凭据缓存，不保存账号或密码。
