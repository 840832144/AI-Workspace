新电脑发布包：`release\HuuugeCollector_Installer.zip`。解压后双击其中的 `HUUUGE_BOOTSTRAP.cmd`。

策划部署手册：`HUUUGE_COLLECTOR_DEPLOYMENT_MANUAL.md`。

# Huuuge 数据采集器（策划 SVN 包）

日常入口：双击 `HUUUGE_COLLECTOR.cmd`。

首次部署或更新：双击 `HUUUGE_BOOTSTRAP.cmd`。该入口从公司 SVN 更新，不要求策划使用 Git。

策划只使用 GUI 六个主操作，不需要选择正在玩的模块或手工打 marker。采集、READY 验证、停止和整理不依赖 AI；需要解读结果时，让 Codex 或 Trae + DeepSeek 先阅读 `AGENT_DATA_USAGE_GUIDE.md`。

安全边界：仅允许 `Pie64_1 / HuuugeResearch` 采集；普通 `Pie64 / BlueStacks 5` 禁止 Root 或 instrumentation。Raw、账号数据、APK、Frida 二进制和密钥不得提交 SVN。

开发源同步：GitHub 私有仓库 `840832144/huuuge-android-research`。每次工具修改应先通过 Git 规范验证，再运行 `scripts\sync_svn_package.ps1` 同步此 SVN 包并分别提交。
