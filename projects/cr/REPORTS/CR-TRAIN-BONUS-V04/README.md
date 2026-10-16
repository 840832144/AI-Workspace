# CR 牛仔与小偷对决 V0.6｜当前交付入口

2026-10-16；沿用 [TASK-0042](../../../../tasks/TASK-0042-CR-TRAIN-BONUS-V04.md)，Review。原三个链接已原位更新，未发布 V0.5。

- [主文 V0.6](https://gfok27asqq.feishu.cn/docx/WZyPdAKY4orhcuxZv03cLGaanjb)
- [附件 A：POP 机制与包装映射 V0.6](https://gfok27asqq.feishu.cn/docx/ISExdbUNooZWAlx3h2ncv2d2nhg)
- [附件 B：接入、比例恢复与 PB 通信草案 V0.6](https://gfok27asqq.feishu.cn/docx/KToidg2HUoFDNnxRDG3cF0KsnQc)
- [机器人可编辑表 SaloonRobotCfg V0.6](https://gfok27asqq.feishu.cn/sheets/Tt96s8ZW5hrWe2tMQtacsf4RnTh)
- [SaloonBonus.proto](https://gfok27asqq.feishu.cn/file/GCpObt54Co2UAZxs9xZc49IjnGo)
- [SaloonBonusCs.proto](https://gfok27asqq.feishu.cn/file/Fhsnbo4KQoHFapxYDmpcjklznKb)
- [协议、字段字典与非生产示例附件包](https://gfok27asqq.feishu.cn/file/RQgKbfF0EoI1roxQo4ZceXBnnOd)

## 回读结果

主文／A／B revision 28/19/8，全文来源段落无缺项，主文十五节与十张原生表格，原棋盘图、相互链接、R01～R04高亮已回读。保留原第八节评论及精确引用位置，保留同事上传的历史研究附件；旧包不作为当前规则，不在本轮重复上传。

机器人云表八个 Sheet 的内容及公式经导出逐格核对一致；空白保持空白，三行仍停用，13条已答回复归档。“NotSupport:table”是导入对 Excel 表对象的限制，不据此宣称该对象功能已保留；公式逻辑保留，未独立验证云端重算。两个 proto 与压缩包均实际下载核对内容一致，扩展名不变。Board.png云端回读为原图。

七个资源逐份权限 GET：组织内链接可编辑、组织外访问和邀请关闭、可阅读者可下载。仅当前授权账号完成回读／下载；无普通员工身份实测。本轮云端交付无阻塞。

## 待确认与范围

只保留 R01～R04供策划修改；不重开13个已答问题。完整方案来自本次交付包，不开展新调研。未开发、产正式库、RTP仿真或修改生产配置。原作者在07中的编译与结构验证记录按来源保留，不冒称本轮工程联调。

搜索和单元格 API 授权尚有缺口：根目录定向查重、已有 Drive 导出已完成本轮必要核对，不申请新授权。唯一 Hub 仍未登记，本轮未更改目录位置；原文内互链已验证。受控材料为 cr-train-bonus-v06-20261016，不提交完整正文、工作簿、协议或响应到 public Git。Subagents: none。

## 历史交付 — V0.4（以下链接已原位升级）

### V0.4 当时交付记录

2026-10-15；[TASK-0042](../../../../tasks/TASK-0042-CR-TRAIN-BONUS-V04.md)；状态 Review。交付原生可共同编辑的方案，不代表游戏实现、数值验收或正式发布上线。

- [主文：CR 火车机台新增 Bonus 开发方案 V0.4｜机器人 4v4](https://gfok27asqq.feishu.cn/docx/WZyPdAKY4orhcuxZv03cLGaanjb)
- [附件 A：POP 对战玩法实现参考](https://gfok27asqq.feishu.cn/docx/ISExdbUNooZWAlx3h2ncv2d2nhg)
- [附件 B：CR 接入与入场／重连设计草案](https://gfok27asqq.feishu.cn/docx/KToidg2HUoFDNnxRDG3cF0KsnQc)

### 实际验证

三份文档使用既有飞书 CLI、显式 user 身份单次创建。云端标题、完整正文、原生表格和全部六个相互链接回读通过；正文与受控定稿直接比较一致，无重复哈希。最终内容版本主文 4、A 5、B 4。

主文与附件分别设置、回读组织内链接可编辑（tenant_editable），组织外分享与外部邀请均关闭。无普通员工测试身份，未宣称员工账号访问或编辑实测。旧文档及其他文件权限未改动。

User 明确独立创建，不放项目目录；搜索／知识空间授权仍待审批，可跳过。User 另明确本轮跳过唯一导航登记；三份文档互相导航已验证，未手工编辑或自动登记 Hub。以上为本轮例外，不覆盖既有正式文档治理规则。

### 内容和来源边界

正文区分 POP 已有证据、CR 已确认要求、本版建议与待确认事项。原火车及 B01 收集保持原口径；正常新局禁跳，中途与重连恢复当前一致状态，已结束返回唯一结算。技术附件独立可读；PB 与模拟只写思路。

原始研究、完整正文/XML、发布脚本和 API 回应留本机受控包 `cr-train-bonus-v04-20261015`，不上传 public Git。云端只发布设计必要整理内容和脱敏样例，未上传整包 Lua、采集脚本或抓包。V0.3 原文件及旧稿引用的生产协议文件未找到，已披露，不把历史兼容性判断当本轮实证。

发布阻塞：无。后续先评审，不运行游戏开发、概率／RTP 仿真或正式产库，不改 SVN。Subagents: none。
