# Roadmap

路线图只描述 Game Planner AI Workspace 的能力建设顺序。当前阶段不实现业务功能；具体游戏项目里程碑应放在各自 `projects/<project>/STATUS.md`。

## Phase 1 — Workspace Foundation

状态：In progress

- 建立 Game Planner AI Workspace 的领域边界和治理规则。
- 定义 Workspace Kernel 与 Capability Model。
- 建立 Game Planner Skill Tree 和统一游戏项目模板。
- 以 `huuuge-android-research` 验证首个游戏项目控制面；当前等待 ChatGPT Review。
- 建立声明式 `workspace.yaml.example` 规范。
- 建立 Global AGENTS 的 Capability Discovery、Capability Catalog 和首个 Document Capability；Tool 的检查与选择降为实现层；等待 ChatGPT Review。
- 后续完善 Capability/Skill 标识、审阅和版本规则，但不在本阶段实现运行时。

## Phase 2 — Document Assistant

状态：Planning / Waiting for ChatGPT Review

- 保持 `Document Assistant` 名称，将其定位为 Document Capability 的公司文档实现 provider。
- 以 [`Document Assistant Capability Roadmap`](docs/roadmaps/DocumentAssistantCapabilityRoadmap.md) 定义能力域、阶段、治理关卡和非目标。
- 面向游戏策划文档定义创建、读取、维护、审阅与交付流程。
- 以 [`Document Capability`](capabilities/document/README.md) 定义 provider-neutral contract，将 Feishu tools 作为当前 Implementation Binding，而不是在 Workspace 复制实现。
- 只定义共享结果契约与 Game Design 使用边界；运行时安装、endpoint、凭据和连接状态由当前 Host 与外部实现仓库负责。
- 定义读写权限、凭据、共享策略、失败处理和证据要求。
- 保持 Document Assistant 的实现与测试在独立项目仓库。

## Phase 3 — Workspace Sync

状态：Planned

- 设计 Git → SVN 的策划产物白名单同步。
- 设计 Git → Feishu 的策划文档发布与更新同步。
- 明确每类内容的真相源、冲突处理、审阅关卡、审计记录和凭据边界。
- 先形成 RFC/ADR 与安全模型，再评估自动化实现。

## Phase 4 — Planner Toolkit

状态：Future

- 建立 Game Analysis、Slot Analysis、Battle Pass、Economy Design、Lottery、Task System 的可复用方法。
- 建立 Excel、SQL、Python 的策划分析工具链规范。
- 建立 Report Writing 与 Feishu Document 的报告交付流程。
- 逐项定义输入、验证、权限和回归标准后，再决定实现或接入方式。
