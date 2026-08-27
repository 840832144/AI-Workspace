# Generic Agent 入口

本入口适用于 Trae / DeepSeek 和未使用专属 Bootstrap 的其他 AI。它只定义稳定读取顺序，不建立另一套规则。

## 启动顺序

1. 读取当前 Host 生效的 Global 与项目级 `AGENTS.md`。
2. 读取 `standards/PLANNER_WRITING_STYLE.md`，将其中“技术术语与风险表述”作为唯一规范。
3. 按 `WORKSPACE_SYNC_ADAPTER.md` 获取最新 Git 与 Context Pack；状态为 stale、conflict 或 unavailable 时明确报告。
4. 按 `MEMORY_ADAPTER.md` 处理长期信息，不把完整聊天、Secret 或敏感证据写入公共源。

## 术语规则

默认使用策划可理解、准确且克制的研究表达。涉及复现、代码、日志、工程判断、授权、合规、安全或风险时，必须保留 Root、Frida、Hook、逆向分析、协议解密、签名校验绕过、完整性校验修改、exploit 等真实技术术语。

不得通过改名或模糊化规避安全策略、权限检查、User 授权或 Review；不得弱化真实风险，也不得把被动研究夸大为攻击。详细映射、例外和自检只以 `standards/PLANNER_WRITING_STYLE.md` 为准。
