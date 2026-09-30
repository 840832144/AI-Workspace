# Huuuge 自助工作台 V1 — 登记前交接

- Date: 2026-09-30。
- Actor: ChatGPT；Owner: User；下一执行者：原Codex。
- Kind: approved-spec-handoff；不分配或冒用新Task编号。
- User decision: Approved，现阶段全部产品内容完成才验收。
- 唯一完整规格：[HUUUGE-SELF-SERVICE-V1-20260930.md](../docs/plans/HUUUGE-SELF-SERVICE-V1-20260930.md)。

## 已明确的决策

一台现有云手机，固定Huuuge游戏账号、不切换；工作台使用者是独立身份，轮流排他操作。简单账号密码+记住登录作为默认方案，已有成熟受控免密可替代，不做匿名公网入口或让策划登录主云账号。

一个网页包含游戏画面与实时面板，开始自动采集，结束停止并一键下载供本地AI读取的脱敏含值数据包。主状态严格为“开始采集灰、采集中绿、采集错误红、采集结束红”；结束用停止图标和已保存文案，不与错误混为一类。管理服务常驻、采集按研究会话启停，错误/断线/刷新/重复请求和下载失败都有恢复路径；正常使用无需Codex后台值守。

账号进度共享是明确产品选择，数据仍按操作者/研究会话隔离；不把不同使用者的批次解释成独立游戏账号。下一阶段才接同手机的其他游戏和采集器；未来每人一台还没有资源采购授权。

## 实时来源与分工

本轮读取治理main b0a36c8、原PR #4/head4a634f0、原Task/Handoff；业务PR #2/head52477c8。原TASK-0031 Round1已在Review中Accepted，但Task/Handoff仍显示Review，原两个PR尚OPEN未合并。先把评审原文按原收尾要求登记，不倒写旧312/312/0快照、不撤销Accepted或新增旧任务验收条件。

本页对应新产品化范围，正式登记应与TASK-0031形成前后继依赖，不向旧试点PR直接追加新平台代码。新实现仍在huuuge-android-research；AI-Workspace只存治理和规格。使用独立分支保留别的Agent变更；尚未获合并授权时可明确基线/依赖，不自动合入或强推。

当前容器git ls-remote因github.com DNS失败，未能运行Workspace Sync、Registry validator或remote-CAS。GitHub连接器读写可用，但不将API读取冒充本地最新main验证。此提交只增加规格和交接，不修改Task/Registry或声明分配成功。

## 原Codex的下一动作

先做登记准备：安全同步最新两仓、任务目录、在途分支和Handoff，读完整规格，按既有validator/独立worktree/remote-CAS流程确认后继关系并登记唯一 `Project key: HUUUGE` 的正式Task；若已存在完全相同活动目标则续接，不重复创建。登记完成回填本页关联入口，然后按正式Task实施，不再让User重述范围。

实现前最早验证两项外部依赖：现有这台手机的Web SDK/便捷账号登录能否支持策划简单进入，以及旧控制会话能否被撤销以保证轮流使用。不要默认已开“免授权”或为此重建手机。厂商SDK只按许可在受控部署使用，不上传整包到public Git。

无新增权限/付费/公共入口时可做范围内代码与定向测试；真正需要开通SDK能力、云身份、HTTPS发布/共享nginx或网络修改时，给Owner一个具体变更与回滚确认，不把配置琐事转给策划。正常运行的密钥轮换、启停与打包必须自动化；旧试点的短时公网ADB限制不能直接当常驻安全结论。

所有A—F验收均在本阶段完成，含未参与开发策划的真实使用、至少两个身份轮流采集、四态/故障显示、导出复下、现有本地AI离线读包及退出管理会话后的新一轮。合成检查与真人证据分列，不重用旧312条当本次产品化验收。

## Idea Handoff / 路线图防重

Codex登记时读取唯一 `docs/roadmaps/PRODUCT_ROADMAP.md`：将本阶段自助工作台作为已批准Current；复用已有 `One Research Environment → Multiple Games → Independent Evidence` 条目记下一阶段Backlog，具体游戏仍待下一阶段明确；每策划独立实例记未来Ideas。本交接不是第二路线图，不因已有未来条目自动执行别的游戏。

完成实现后更新新正式Task/Status/Handoff/业务部署验收和变更记录，提交实际入口、可用演示、包内读数说明、真实验证和剩余限制，交ChatGPT Review。默认不自动合并，不启动下一阶段，不重新索要已配好的主机或密钥。
