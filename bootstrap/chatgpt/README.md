# ChatGPT Project Bootstrap

本目录把 Game Planner AI Workspace 的稳定规则、系统背景和当前状态整理成 ChatGPT Project 可复用的来源文件，解决“同一项目中新建对话却不知道既有体系”的问题。

## 安装到 ChatGPT Project

1. 打开 ChatGPT Project 的设置，把 `PROJECT_INSTRUCTIONS.md` 内容复制到“项目指令”。
2. 在项目主页的“来源 / Sources”中上传稳定 Bootstrap：
   - `00_CORE_RULES.md`
   - `01_SYSTEM_CONTEXT.md`
   - `02_CURRENT_STATE.md`（仅作为离线回退）
   - `03_NEW_CHAT_BOOTSTRAP.md`
   - `../../standards/PLANNER_WRITING_STYLE.md`（中文行文与技术术语唯一规范）
   - `../../docs/roadmaps/PRODUCT_ROADMAP.md`（长期产品方向）
3. 把与本项目有关的重要历史对话移动到同一个 Project。
4. 新建一个测试对话，发送：

```text
请先读取项目来源中的 00、01、02、03，并用 8 行以内说明：
项目定位、Huuuge 优先级、ChatGPT/Codex 分工、当前任务、Idea Governance、术语规则、真相源和安全边界。
```

回答正确后再开始正式工作。

新会话的稳定读取顺序为：Core Rules / System Context / Writing Style → 最新 Git `main` 的 `memory/context/WORKSPACE.md` → 相关 Task / Review / Status / Handoff / 业务证据。Git unavailable 时才使用 Project Source Pack，并标记可能过期。

## 更新规则

- `00_CORE_RULES.md`：稳定治理规则，只有长期规则改变时更新。
- `01_SYSTEM_CONTEXT.md`：系统架构和仓库关系，能力边界变化时更新。
- `02_CURRENT_STATE.md`：离线回退；动态状态优先由 Workspace Sync 从 Git 生成，不再把人工重新上传当作唯一 freshness 机制。
- `memory/context/WORKSPACE.md`：跨会话 public-safe 长期记忆的唯一稳定读入口；刷新清单必须显示路径、SHA-256 与读取时 Git HEAD。
- `03_NEW_CHAT_BOOTSTRAP.md`：新对话启动协议，通常保持稳定。
- `standards/PLANNER_WRITING_STYLE.md`：面向策划的中文行文与技术术语唯一规范；默认表达和必须保留精确术语的例外同时生效。
- `docs/roadmaps/PRODUCT_ROADMAP.md`：唯一长期产品规划；主动产生的新产品 Idea 在 Task 收尾时分类并交接，不自动创建 Task。
- Git 中的 AI-Workspace、对应业务仓库、Task、Status 和 Handoff 始终是最新真相源；Project Sources 是便于检索的快照，不代替 Git。
- 新对话先同步 Git 并读取 Workspace Memory，再读取 `LIVE_CONTEXT_MANIFEST.json` 和相关事实来源；无法同步时才回退 Project Sources 并明确显示 stale/unavailable。

## 边界

这些文件不得包含 Secret、账号标识、原始采集数据、完整运行日志、私有 Registry 或其他敏感信息。ChatGPT Project 不承担 Codex 本机 MCP、环境变量、CLI 或服务连接状态管理。
