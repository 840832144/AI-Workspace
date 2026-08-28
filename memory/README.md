# Memory Candidate Store

本目录只保存 **Public-safe** Memory Candidate、Review、Archive、索引和唯一稳定读视图 `context/WORKSPACE.md`。任何 Project Private、Cross-project Private、Local-only、Secret、Raw Capture、账号数据、完整响应或敏感日志都不得进入这里。

`context/WORKSPACE.md` 只由现有 Curator 在 `ASSISTED` 模式下根据明确批准写入，不允许 Agent 绕过 Candidate/Validator 直接维护。相同 key 去重，冲突进入 Review，supersede 保留旧来源与时间。新会话以最新 Git `main` 版本为准；Project Source Pack 只是可能过期的快照。

```text
memory/
├── inbox/    # 新 Candidate；append-only，等待 Curator
├── review/   # 冲突、高影响、证据不足或 ASSISTED mode 的人工队列
├── archive/  # duplicate、rejected、superseded、promoted 后的历史 Candidate
└── index/    # mode default、promotion index 与 refresh 元数据
```

使用入口见 [`tools/memory/README.md`](../tools/memory/README.md)，治理规则见 [`MEMORY_GOVERNANCE.md`](../standards/MEMORY_GOVERNANCE.md)。不要手工把私有 Outbox 复制进本目录。
