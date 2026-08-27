# Capability Catalog

Capability Catalog 是 AI 协作体系的能力导航入口。Agent 先在这里识别“需要完成什么结果”，再选择 Workflow、Skill、Implementation Binding 和 Tool；不得从当前可见的工具名称反推用户目标。

## Catalog 规则

每项 Capability 必须包含：

- 稳定 ID 与名称；
- 面向使用方的 Outcome；
- 适用范围与消费者；
- 输入、输出和操作等级；
- 前置条件、安全边界与成功证据；
- provider-neutral contract；
- 当前实现绑定及其证据来源；
- 状态、Owner 和 Review gate。

Capability 是否存在与当前 Host 是否有可用实现是两个状态：

- `Registered / Implementation available`：契约已登记，当前 Host 有经过批准的实现。
- `Registered / Implementation unavailable`：契约存在，但当前 Host 没有可用 provider 或 Tool。
- `Proposed`：只有提案，尚不能作为稳定契约使用。
- `Unknown`：Catalog 和项目规则中都没有对应能力，需要澄清或建立新提案。

不得因为某个 MCP、Connector、Skill、Plugin 或脚本暂时不可见，就把已登记 Capability 判断为不存在；也不得因为某个 Tool 可见，就虚构其能够交付尚未登记的 Capability。

## Discovery 顺序

1. 从 User 目标提取期望 Outcome、对象、操作等级和成功证据。
2. 先检查当前项目的 Capability 引用和限制，再查本 Catalog。
3. 选择一个或多个 Capability，并确认输入、输出、安全边界和状态。
4. 选择适用 Workflow 与 Skill。
5. 最后检查当前 Host 的 Implementation Binding 和实际 Tool schema。
6. 执行后按 Capability 的成功证据验收，而不是只确认 Tool 调用返回成功。

## 当前 Catalog

| ID | Capability | Outcome | Scope | Contract | Contract status | Implementation status |
| --- | --- | --- | --- | --- | --- | --- |
| `CAP-DOC` | Document Capability | 发现、读取、创建、维护、发布和授权公司文档 | Shared platform，供 Game Design 等项目消费 | [`document/README.md`](document/README.md) | Registered | Document Assistant baseline available on approved Hosts；以实际会话为准 |
| `CAP-MEM` | Memory Capability | 捕获、验证、路由、整理和刷新跨对话长期记忆 | Shared governance，供 Game Design 项目消费 | [`memory/README.md`](memory/README.md) | Registered / Waiting for ChatGPT Review | AI-Workspace reference implementation available；Host adapter 以实际会话为准 |

## 边界

- 本目录登记 Capability contract，不登记 endpoint、credential、安装状态或连接状态。
- AI-Workspace 可以保存 Game Design Capability，以及 Game Design 会消费的共享平台 Capability；不得引入其他业务域的项目正文或 Memory。
- provider 与 Tool 的源码、测试和运行配置继续以各自实现仓库和受控 Host 为真相源。
- 新 Capability 需要先通过 ChatGPT 架构审阅；涉及长期边界时必须有 RFC/ADR。
