# ADR-0007 — Workspace Live Context Hub

- Status: Accepted
- Date: 2026-08-27
- Decision owner: User / ChatGPT
- Implementer: Codex
- Related Task: `TASK-0021`
- Accepted by: ChatGPT Review Round 1 on 2026-08-27
- Numbering note: ADR-0006 is reserved by the active TASK-0020 allocation-governance work; this independent branch uses ADR-0007 to avoid collision.

## Context

ChatGPT Project Sources 是上传时快照，多个 Host 与策划并行工作时会快速过期。飞书适合在线协作，但不能无规则地与 Git 双向覆盖；Secret、Raw Capture 和私有 Registry也不能进入公共协作层。

TASK-0021 要求优先验证 Wiki。官方 Wiki API 存在，但当前应用对空间列表的 live probe 被拒绝，缺少 Wiki scope，因此无法证明空间/节点定位、revision、权限和 Docx 闭环。现有 Drive/Docx 能力已通过真实 healthcheck、文档读写和权限回读。

## Decision

采用以下模型：

1. Git 保存规则、Task、Capability、Workflow、ADR 与状态的 canonical truth。
2. 飞书 Drive 中建立唯一 Context Hub 文件夹和固定 Index；Git-authoritative 文档公司内可读，协作草稿公司内可编辑。
3. Workspace Sync 使用稳定 context ID、source fingerprint、provider revision 和 Host-local baseline，不按标题判断同步状态。
4. 飞书协作草稿只进入 Memory Candidate/Review；飞书对 Git-authoritative 文档的修改形成 conflict，不覆盖 Git。
5. ChatGPT、Codex 和 Generic Agent 在交互开始时运行 `ON_DEMAND` sync；WATCH 未获批准，保持关闭。
6. provider document/folder ID、私有 URL 与 Registry 只留 Host-local state，不进入公共 Git。

## Alternatives

- Feishu Wiki：目标形态更接近知识库，但当前 scope Gate 未通过，暂不采用。
- 其他协作平台：会引入第二套账号、权限和运维，当前没有批准 binding。
- 只用 Project Sources：仍需人工替换，无法满足 freshness。
- 无规则双向同步：会静默覆盖 canonical，拒绝。

## Consequences

优点是立即复用已验证 Provider，不新增权限、服务或 Secret，退出成本低。代价是 ChatGPT 直连飞书不可用时仍依赖自动 Git mirror/local pack；Drive 不是 Wiki，不能伪称知识库。Company-readable 权限能力需要 Document Assistant 的最小增量并单独测试。

未来切换 Wiki 必须先获得 User 授权并满足完整 Gate；切换只替换 provider binding，不改变 CAP-CONTEXT contract 或稳定 context ID。

`WATCH` 不属于本 ADR 的已启用范围；任何生产 watcher、webhook、Scheduled Task 或长期进程仍需 User 另行明确批准。

## Final UX Closeout

TASK-0021 最终收尾采用唯一《AI Workspace｜文档导航中心》作为所有正式飞书文档的统一入口。展示标题可以原位调整，但稳定 alias、Registry Hub 标记和文档链接保持不变；正式文档只有在正文回读、自动登记和导航中心回读全部通过后才算成功。导航中心失败时保留已创建文档并返回失败，不删除、不重复创建。面向策划的项目全景说明在靠前位置提供导航入口和可视化工作流，发布后必须同时回读章节顺序、链接与原生图形块。
