# Huuuge 云端调试任务交接（v2：补齐 Google Play）

- Date / Updated: 2026-09-29
- Actor: ChatGPT
- Owner: User 本人，全程负责本试点资源、登录与验收；不等待其他技术对接人。
- Executor: 原 Codex 会话，唯一实现与运行执行者。
- 正式任务：[TASK-0031](https://github.com/840832144/AI-Workspace/blob/codex/huuuge-cloud-single-instance/tasks/TASK-0031-HUUUGE-CLOUD-SINGLE-INSTANCE.md)
- 完整修订任务：[CLOUD_DEBUG_PLAN_20260929.md](../tasks/support/TASK-0031/CLOUD_DEBUG_PLAN_20260929.md)
- 调试文档 PR：[AI-Workspace PR #11](https://github.com/840832144/AI-Workspace/pull/11)
- 性质：已有任务的执行修订；不新建 Task/PR，不接受准备代码 Review，不代表真实云端验收。

## 本次 User 修订

User 明确指出上一版漏掉谷歌商店安装，要求重新出任务。本版取代原“检查环境后直接跑游戏”的顺序。**Google Play商店及配套GMS的检测、安装/启用、正常更新和排障由Codex负责，不能变成User自行完成的额外部署流程。** 只有Google/游戏身份登录、验证码、必要授权和普通游戏操作由User本人完成。

## 当前事实与来源

User已提供云手机网页Android桌面，并报告工具安装；桌面截图不能证明Google Play未安装、GMS已齐全或Huuuge已可玩，须现场区分缺图标、已装停用和确实缺组件。CLI版本、认证、终端归属、独立Linux执行端和真实采集状态均单独核验，不再笼统等待“技术提供所有资源”。

本次重读：AI-Workspace main `b0a36c8`；正式Task/专用Handoff分支 `872e2dc`；业务PR #2 / CURRENT_STATUS `402e0d4`；原调试PR #11 `f37f3a6`。原两条准备PR仍OPEN/未合并，canonical Task仍为准备Review。上述旧记录不覆盖User已展示云手机桌面的新事实，也没有本轮Google/游戏/采集实测通过证据。

阿里云官方FAQ说明默认支持GMS但依赖Google服务连通，Android12镜像发布说明提及GMS一键配置和兼容优化。仅支持优先查找厂商方案，不能据此宣称本机已经安装，也不能编造具体按钮、setprop命令或第三方APK安装顺序。官方来源在完整任务中。

## 执行顺序

1. 核对真实云手机、Android/镜像/ABI、Google组件状态及手机自身网络，不凭桌面图标下结论。
2. 优先复用内置Google组件或厂商适用的GMS安装/启用入口，完成实际安装/恢复及必要正常更新；记录修改前后状态与来源。无官方适用步骤时明确该缺口，不让User网上找包，不随机拼装GMS。
3. 到Google原生登录界面后暂停敏感输出，提示User本人登录；不采集登录过程，不索要密码/验证码，不截图账号页面。确认商店首页/搜索/详情和认证实际状态。
4. 在Google Play定位正确Huuuge，完成正常安装/更新或确认已安装来源与版本；已装复用不写成新下载通过。商店地区、下载和设备问题单独排查，不静默改为APK侧载。
5. User完成Huuuge登录及无探针游戏基线；之后才接入云端Linux、原采集器，取得真实新增业务解码，再正常停止/保存/回读。

不把Play图标、商店能启动、游戏安装、游戏可玩和采集通过合成一个Ready。香港实例不等于Google账号地区；不自动更改地区/支付配置、清账号数据、重建镜像、去除/隐藏Root或做认证绕过。必要破坏性/权限/付费变更先由User确认。

## 原 Codex 唯一下一步

读取完整v2任务，安全同步原分支并将本次User修订纳入现有Task/Status/Handoff，按既有Registry流程调整Changes Requested/实际执行状态，不分配新ID。不覆盖其他Agent工作或自动合并有冲突的准备PR。

先返回本实例Google组件及网络实况，并推进可独立完成的官方安装/启用；无需等待独立Linux执行端就可先完成手机商店准备。安装完成后明确提示User登录Google，不直接叫User打开一个尚未安装的商店。

交付必须包含业务仓库 `deploy/cloud/README.md` / `ACCEPTANCE.md` 中可复现的Google组件准备方法、本人登录节点、商店获取Huuuge结果以及后续真实云采集结果。Google路径失败时不能仅有Frida部署说明便交完整成功。

## 不变的运行边界

Workbench CLI面向Linux ECS，不凭云手机页面终端推断CLI支持云手机ID。管理通道与Linux到Android数据通道分开验证；不在User电脑运行生产采集/解码/必需转发。首次连接的安全组副作用、OSS中转和短exec超时按原方案保留。原生ARM64、Root、私网、descriptor前提以实测为准，不删校验凑通过，不影响晨会。

本次ChatGPT仅修订自己PR #11中的两份文档并通知原任务执行者，未修改Codex业务分支、canonical Task或Registry，未连接云环境、安装商店、运行采集或Workspace Sync/validator。原准备Review、商店可用和最终云端三项验收分别记录。Subagents: none。
