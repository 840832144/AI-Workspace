# TASK-0031 — Huuuge 单实例云端游戏与采集闭环

- Status: In Progress
- Project key: HUUUGE
- Owner: User
- Executor: Codex
- Priority: P1 / bounded pilot
- Date: 2026-09-15
- Updated: 2026-09-29
- User decision: Approved；按 PR #11 v2-GooglePlay 续接，由 Codex 准备谷歌环境，User 本人负责权限、身份登录和手动游戏操作
- Allocation relationship: new
- Related tasks: TASK-0027
- Subagents: none

## Goal

按 [采集器 Issue #1 v3](https://github.com/840832144/huuuge-android-research/issues/1) 跑通一台云端 Huuuge 环境：策划仅用厂商网页，游戏与采集/解码均在云端，真实新增数据可保存且正常结束。2026-09-15 的“资源未就绪，先准备”是历史状态；2026-09-29 按 [PR #11 v2 方案](https://github.com/840832144/AI-Workspace/blob/5ff7190137f1512f52cddacc0f5d17ce5cc4254e/tasks/support/TASK-0031/CLOUD_DEBUG_PLAN_20260929.md)及[对应交接](https://github.com/840832144/AI-Workspace/blob/5ff7190137f1512f52cddacc0f5d17ce5cc4254e/handoff/HUUUGE-CLOUD-DEBUG-20260929.md)续接，不新建 Task/PR，不接受准备代码作为真实验收。

## 2026-09-29 续接实况

- 已将最新 main `b0a36c8` 安全合入原治理分支，保留双方 Changelog，Registry 从 canonical 重建；19 canonical、0 collision、validate=valid。Workspace Sync 实测 ON_DEMAND / provider unavailable / stale 6 / conflicts 0。
- User 更正 Workbench CLI 需要 Codex 安装。现已从阿里云官方发布包安装 Windows amd64 `v1.0.1`（commit `86c0aff`），官方 SHA-256 校验通过；版本、根帮助、exec/配置/列表帮助已读取。只安装管理工具，未部署本机采集、解码或持续转发。
- 当前管理 Host 未发现 Workbench 默认配置文件；没有读取凭据、连接 ECS 或修改安全组。安装成功不代表认证或目标核验成功，实际云手机与 Linux 执行端仍须分别核验。
- 上轮浏览器 provider 失败且 Computer Use 无法核验 URL，已停止操作。User 后续提供普通控制台入口；本轮通过受支持的内置浏览器访问 `https://wya.wuying.aliyun.com/instanceLayouts`，实际 URL 回读为官方 `account.aliyun.com/login/login.htm`，标题为“阿里云登录”。User 随后确认已登录；实际 URL 回读为无影官方实例页，核对唯一已购实例：可用、香港、4c8g32G、Android 12、镜像 26.09.1。未读取密码/验证码或导出 Cookie。点击连接时工具超时并重置，后续浏览器枚举返回 fetch 失败，无法核验连接后的 URL，已按 User 要求停止；连接结果 unknown，手机组件/网络、Google 登录和 GMS 安装仍未执行。
- 已定向阅读业务 `402e0d4` 的 controller → decoder → stop/结果回读调用链；保持现有采集器及 gate，本轮没有代码重写或运行探针。历史合成 CI 仅为准备证据。
- 顺序：Codex 核查并官方安装/启用 Google Play/GMS → User 亲自登录 → 商店首页/搜索/详情与认证状态分别验证 → Google Play 获取或确认 Huuuge → User 无探针游戏基线 → 受控云端采集 → Stop/退出/结果回读。手机准备不依赖先找到 Linux 执行端。
- 当前状态 In Progress：登录与实例页核验完成，连接后的浏览器状态无法读取，执行停在连接结果待核验。Workbench 凭据或 Linux 执行端未就绪不作为手机组件准备的前置阻塞；未重复安装 CLI，不新增付费资源或公网调试端口。

## 初始登记与能力契约（2026-09-15；续接状态见上节）

- 同步 AI-Workspace `5b5414c`、业务仓库 `759669b`；两处 main 工作树原本干净，使用独立 linked worktree 和 `codex/huuuge-cloud-single-instance` 分支。
- 完整 Registry scan/validate：14 canonical、0 collision、status=valid；远端预留 TASK-0027/0028/0030，allocator remote-CAS 实际返回 TASK-0031，reservation 保持 pending-main。
- 无同目标云端 Task/Candidate；TASK-0027 是笔记本可靠性任务，本任务不续写、不恢复其本地部署范围；晨会 TASK-0028 与其他研究任务所有权不变。
- 项目能力来源：Huuuge `docs/collector/CURRENT_CAPABILITIES.md` 的被动 RpcMessage 采集、descriptor 解码、READY、Stop/Flush 和 Session 保存。公共 Capability Catalog 已核对，不新增共享平台能力或工具目录。
- 输入：User 本人确认权限的一台无影云手机及独立核验的云端 Linux 执行端、当前版本/ABI、匹配探针/descriptor、独立结果目录。
- 操作：业务仓库 WRITE（必要适配与测试）；云端运行仅在资源授权就绪后执行。User 负责权限确认；不购买资源、不开放公网调试端口，不自动接受 Workbench 首次连接可能产生的安全组变更。
- 输出：必要云端启停/检查适配、脱敏模板、短中文部署说明、三项验收记录与受控结果交接。
- Workspace Sync：ON_DEMAND、provider unavailable、stale 6、conflicts 0；使用 Git 最新证据，未开启 WATCH。PowerShell 入口受执行策略阻止后，直接运行其原有 Python CLI，未更改执行策略。

## 实施与边界

复用现有 Collector、agent.js、解码器和停止控制文件；仅补 Linux 运行和本轮 Session 验收所必需的适配。云手机 Android/ABI、Root/Frida 权限和 Huuuge 版本由现场验证，不照搬蓝叠/Houdini。现成网页客户端由 User 登录并操作；Agent 不代玩、不自动点击、不修改请求、奖励、余额或服务端。

不做多人、克隆、统一工作台、报告平台、本地安装包、历史数据搬迁或其他游戏；不修改晨会服务和共享主机全局环境。原始数据、标识和日志仅留受控云端；Git 只收代码、模板、计数和状态。

## 验收

| 项目 | 必须证据 | 当前结果 |
| --- | --- | --- |
| Google Play/GMS 前置 | 组件前后状态、官方方法、User 登录、商店可用与认证状态 | 手机检查未执行；阿里云登录与目标实例页已核验，连接结果 unknown |
| 网页游戏 | Google Play 获取/确认 Huuuge 后，User 无探针正常交互 | 未执行 |
| 真实采集解码 | 本轮新增、关联普通手动操作的成功业务解码样本 | 未执行；计数 unknown |
| 正常结束保存 | Stop/flush、进程退出、结果仍可读、捕获/成功/失败数可核对 | 未执行；没有云端 Session |

静态和合成检查单列，仅支持准备工作 Review。云端闭环未通过时不标 Complete/Accepted。

## 交付与下一步

保留原准备 PR，按 v2 顺序继续原 Task；当前不是 Complete/Accepted，也不代表谷歌环境准备完成。

- 实施 [PR #2](https://github.com/840832144/huuuge-android-research/pull/2)，代码 commit `9bb241b`；中文[部署说明](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-cloud-single-instance/deploy/cloud/README.md)和[验收记录](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-cloud-single-instance/deploy/cloud/ACCEPTANCE.md)已提交。
- Linux [CI 34957001266](https://github.com/840832144/huuuge-android-research/actions/runs/34957001266) 14/14 合成检查通过：实际 decoder 子进程、损坏 wrapper 保留、断连失败、单运行锁、SIGTERM、supervisor 启停与最终文件回读；没有真实云手机数据。
- 业务 Status/COLLAB_LOG/TASKS/CHANGELOG/Handoff 均已更新。仅在云端部署所需的 Linux controller、配置模板和现有 decoder 异常处理有代码变更，未运行本机采集或修改晨会。
- 下一步仅在受支持浏览器恢复后读取现有标签实际 URL 与连接结果，避免盲目重复点击连接；可靠核验后由 Codex 检查 Google 组件和手机网络、推进适用官方安装/启用。到 Google 原生登录页再通知 User 本人登录；不以 Workbench/Linux 状态阻塞手机准备。URL 无法可靠核验时保持停止并报告具体工具错误。
- reservation 保持 pending-main，待 Review 后 canonical 进入共享 main，再由本独立 worktree 使用本机 reservation 元数据 finalize；不提前释放或伪称已合入 main。
