# Memory Candidate Store

本目录只保存 **Public-safe** Memory Candidate、Review、Archive 和索引。任何 Project Private、Cross-project Private、Local-only、Secret、Raw Capture、账号数据、完整响应或敏感日志都不得进入这里。

```text
memory/
├── inbox/    # 新 Candidate；append-only，等待 Curator
├── review/   # 冲突、高影响、证据不足或 ASSISTED mode 的人工队列
├── archive/  # duplicate、rejected、superseded、promoted 后的历史 Candidate
└── index/    # mode default、promotion index 与 refresh 元数据
```

使用入口见 [`tools/memory/README.md`](../tools/memory/README.md)，治理规则见 [`MEMORY_GOVERNANCE.md`](../standards/MEMORY_GOVERNANCE.md)。不要手工把私有 Outbox 复制进本目录。
