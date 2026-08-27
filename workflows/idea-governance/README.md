# Idea Governance Workflow

本 Workflow 把项目聊天中值得长期保留的产品想法稳定地写入唯一 Product Roadmap，同时保持 Task、Documentation Hub、Knowledge 和 Memory 的职责分离。

## 流程

```text
聊天中产生长期产品想法
→ ChatGPT 判断是否值得长期保留
→ 防重并分类为 Current / Backlog / Ideas / Done
→ 在对应 Task 收尾生成 Idea Handoff
→ Codex 读取最新 Git 与 Product Roadmap
→ 更新 Git 源稿
→ 发布并回读飞书 Roadmap
→ 回读文档导航中心与项目全景入口
→ Task / CHANGELOG / Handoff 记录
```

## 责任

- ChatGPT：识别、去除一次性想法、提出分类和进入下一阶段的 Gate。
- Codex：确认最新 Git、防重、实施 Git 与正式文档更新、验证并提交。
- User：决定进入 Current、创建 Future Task、改变优先级或放弃高影响方向。

## 失败处理

- 找不到唯一 Product Roadmap：停止写入，先解决唯一性，不创建第二份。
- 分类依据不足：放入 `Ideas` 并写清待确认 Gate，不擅自进入 Current。
- 没有 Git writer：输出最小 Idea Handoff，不声称已登记。
- 飞书更新或导航中心登记失败：保留现有文档，不重复创建；Git 保持真相源并在 Handoff 标记待修复。
- 与 active Task 冲突：Roadmap 只记录方向，不修改 Task；升级给 User / Review 决定。

## 验收

- 四个固定分区各出现一次；
- 新 Idea 能按规则进入正确分区且不重复；
- Roadmap 正式飞书文档唯一、可回读、企业内可编辑并已登记；
- 文档导航中心和项目全景说明都能进入 Roadmap；
- Registry、Memory、Context 与 Workspace Sync 模式不退化。
