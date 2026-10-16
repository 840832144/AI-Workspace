# Bingo原客户端本地一局闭环 — dsh / Codex共同接管

- Kind: handoff。
- Date: 2026-10-16。
- Project key: BINGO-CLIENT-COMPAT。
- User已批准改为单一可玩交付目标；不再只交Schema、样件或可行性报告。
- 完整正文：`tasks/support/bingo-client-local-round-20261016/EXECUTION_SPEC.md`。

## 唯一目标

原客户端＋本地兼容服，完成一个普通单卡局：大厅→选票→开局→持续叫号/手动填格→至少一种基础局内道具→合法Bingo→正常结束→回大厅；返回后可再次进入新局。正式消息、Schema和必要初始化按实际依赖恢复，不锁死旧消息清单。

## 分工与连续执行

Codex首步按最新main、完整Registry和remote-CAS流程登记独立任务，负责服务实现、整合、Git与交付；dsh负责协议/客户端研究、接入诊断和获准环境中的联调支持。dsh可继续既有静态工作，不把TASK-0041验收通过当依赖。

双方一次核实共同受控交换目录，Codex维护唯一INTEGRATION.md，dsh专属目录交付研究合同；一批可用即整合，不等待全部消息齐全，不让User转译字段。各自独立工作树，同实例单控制者。

前轮v2的M1–M3作为内部修复一并完成；Schema恢复、最小服务、接入准备和实际联调连续推进，不逐步等待Review。普通错误自行修复并保留记录，最后交可玩结果与必要证据统一Review。

具体新增DNS/hosts/CA/Hook/独立实例等权限在开工时尽早集中列一次，未获授权不实施；这不阻止已有静态分析和本地服务开发。不能把目标授权当作无限系统权限，也不能把每个Unknown都升级给User。

TASK-0039继续暂停；TASK-0041保留代码修订、验证暂缓，原PR #21不合并、不Accepted。新任务自己的必要测试不受旧Demo暂缓验证指令替代。

本次Git支持稿不是已分配的canonical编号；编号由Codex登记，不猜号。不开新账号、不线上消费、不自动发布、合并、SVN或finalize。
