# TASK-0039｜当前票额与在线执行边界

最终候选离线验证：101项通过，29.719秒，exit0；正式账本字节不变。包含真实CLI十局来源复算、余额暂停后同版恢复、拒绝换版/STOP、整批任务预算与逐局钱包不足拒绝；均为隔离测试，不是真实十局成绩。生产context另将当前PanelQuote选择写入冻结输入并保留面板来源引用，旧存档不参与购买。

User最新明确：“预算放宽，如果后面余额不够我会补充”。治理225215a已登记；本次按历史52票+真实12票×十局自行封顶172票，版本execution-budget-relaxed-20261014。仍单局16票/300秒、18完整位置、3历史定位、累计6000秒；旧96票/5400秒及96票/6000秒政策原样保留，新额度不追认历史超限。

真实普通四卡12票已通过生产Device.context/PanelQuote与实际--check/--start，来源功能候选3a052b1；原入口因旧96票预算不足未登记、未购买。新十局仍待真实执行，准备成功不等于完整验收。历史账本52票/2567.120秒保留，以下每个历史快照按其版本和时间解释。

整批任务预算仍预留全部剩余局数；钱包改为每局按当前结构化余额核对。未来余额缺口单列，不自动充值。买前余额不足会保留原登记和全部成绩，停止输入；User补充后用bv_autoplay.py --resume <原batch目录>恢复。恢复必须相同代码/解析器/口径/资源版本、原登记与原账本一致、所有已完成局来源完整且结算到位，无STOP；不能跳过失败局或混版。结算进入大厅时只先执行已识别的非消费开面板导航，再重读当前报价。

当前入口与测试中硬编码上限同步；额外定位/试购仍不允许，位置9–18用于一个冻结候选的新十局。逐局>90%，争取加权≥95%。原第6局未达标、第8局历史超限与接管保留。普通开发自主推进，不逐步等待Review；最终统一提交真实结果与受控复算。

不合并、发布、SVN、扩权或finalize。Subagents: none。

---

## 历史：报价接入成功、User尚未放宽票额时的记录

# TASK-0039 当前报价接入与整批资源缺口（2026-10-14）

功能候选3a052b1e7df99340a95401cf6938e9b39ee16b77已通过实际入口：bv_autoplay.py --start → preflight → Device.context → ScopedPanelReader → PanelQuote → Budget.batch_plan。真实最低普通档为四卡、BET_NP_SYMBOL_3、每卡3票、面板结构化显示12票；只有这一个可用档。免费局结束值为0，折扣状态/配置为空，多倍快速状态关闭；相关方法分派、构建、进程启动时间、boot、组件归属及GDS版本均校验。不是旧存档、图像估价或手写验证标签。

--check与冻结后的--start都exit2，仅报batch_budget_insufficient。新批次未登记，购买/填格0次，新十局0/10。前者已有当前PanelQuote；后者三次刷新分别0.829/0.875/0.797秒，每次两遍真实读取，保持2秒上限。旧逐字段读取两次因超时拒绝，随后分析读数时间间隔并改为最多4组独立只读块并行，两遍整体仍顺序执行。固定类型/方法名称仅作元数据缓存；业务值、对象类型指针、方法槽/分派位/目标均重读。初始定址不是可购买报价。

当前总账52票、2567.120秒、8历史完整位置/3定位；新时间版本execution-time-relaxed-20261014封顶6000秒，是User放宽时间后Codex自限增加600秒，不是User指定新数值。还剩44票、3432.880秒及10位置，保留十局3000秒+30秒收尾后准备余量402.880秒。旧5400秒授权版本及历史账本保留。单局仍16票/300秒，总票额96，完整位置18，不增加定位。

按实时报价12票，十局需120票；授权剩44票，差76票，最低累计总票额计划为172票（52历史+120新批）。当前可用票也不足120，具体差额只保留受控记录。上述172是待User决定的资源计划，代码仍96；没有充值、购买资源或扩大技术权限。不先买无法覆盖整批的局。后续若报价变化，重新按整批预算核对；不追加第19位置。

本轮从2363.776秒基线增加203.344秒。一次非消费导航，购买/填格/attach/agent均0；没有修改采集器、Root、证书、网络或游戏业务状态。原emulated绑定保持停止。所有失败、超时与初始字段观察保留，不挑成功记录。

验证：99项离线及真实函数/CLI集成回归通过（25.513秒，exit0，正式账本字节不变）；实际入口捕获另由纯解码器复算，通过10项变造拒绝与1项动画门/输出字段区分。首次全套发现旧测试固定2400秒不再表示新额度下余量不足，已改为当前限制推导的边界；原失败输出保留，没有删除安全断言。新的慢报价读取不能沿用过期按钮标定；资源预留之后重新标定，最终发送前再查标定时效与STOP/截止。

DSH答复经独立复核后采用：+0x169是_discountAnimPlayed，+0x168是_isShowingBuffCost输出；0x2001e615的正确元数据索引是(raw&0x1ffffffe)>>1=62218，解析到UIManager。MethodInfo不是带klass对象头，+0x20才是方法所属类型。br/blr不能独立证明业务含义，翻译执行的ARM64代码在host maps无x也不等于无效函数。Round/Discount管理器实际通过GameComponentRoot组件字典定位，不能简化为一次指针读取。早期probe把Panel+0x108标作is_playing，现已按字段表纠正为_preventClick；原读数保留。折扣常数0.9已离线确认，但折扣/免费激活状态不在本reader已支持路径内，遇到即拒绝。DSH原答复与精确离线来源留受控目录。

完整四卡持续输入、覆盖后真实受理、局末收尾及自动续局仍需在新批次证明；现有修复和第4–7局研究归因保留。运行准备与指标认证分离；当前没有新整局成绩，不把未开始写成0%失败或成功。历史第6位置31/35上界88.57%的真实未达标、第8位置当时12>8超限和User接管继续保留，不以新上限追认，不混版拼成绩。

受控入口：%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\execution16\hook\dsh-review\REVIEW-CURRENT.md；recompute_current.py、ENTRY-BINDING.json、production-start-1/result.json、panel-price-replay.json、tests-current.txt可复查。原始字节、账号、钱包、卡面、完整日志及二进制不上公共Git。

继续TASK-0039及原PR #16/#17，In Progress/等待资源决定与Review；未Accepted。Subagents: none。不合并、发布、提交SVN、扩权或finalize。

---

## 历史快照：当前实时报价接入之前

## 2026-10-14 当前：原实例已读到面板字段，最终计价仍待合证

原有四卡、覆盖恢复、末球收尾、结算、STOP和预算修复保留。emulated观察绑定因重复加载失败及库卸载限制已在41dacf7停止，CLI/worker/直接调用在设备与账本操作前拒绝；没有重新尝试。原限定被动观察授权有效，不重复索权。

已通过本地ARM64 ELF、v31 metadata、重定位及反汇编确定字段偏移与UIManager→BuyCardPanel对象路径；用原ADB权限定址读取，没有attach、装载agent、全堆扫描、调用方法或改安全设置。保留前三次失败/面板未开启结果；一次非消费导航打开选卡面板，随后2.375秒、52次ADB命令、846字节读取获得当前四卡、Bet索引0/最高可用索引0、基础每卡3票。未调整乘积12仍不是最终报价。TicketCost实际为GameObject，两个buff标志false不足以证明没有免费/折扣。

新增bv_panel_fields.py纯字段解码器，返回候选数据而非PanelQuote；实际读取序列复放及四种变造拒绝、购买校验拒绝合计6项通过。此前92项离线/真实函数与CLI集成回归通过（32.854秒、exit0、账本不变），与6项受控复放分列；不把它们当作真实整局。离线枚举解码确认raw1=Bingo13，完整普通模式、最终价格与动态分派仍需绑定。

当前累计52票/2363.776秒/历史8完整位置及3定位；剩44票/3036.224秒/10位置，保留十局3000秒和30秒收尾后准备6.224秒。本轮仅一次非消费导航，无购买、填格或attach；新十局0/10。若最终普通四卡12票，十局需120票、较剩44票缺76票；条件测算不追加额度。单局16票/300秒、累计96票/5400秒/18位置均不变。第6位置真实失败、第8位置旧超限及接管保留。

生产Device.context尚无合格最终报价reader；价格影响完整性、动态分派、资源时钟及覆盖后真实受理未证明，购买继续阻断。DSH具体问题已聚焦上述语义，User已答复转述。受控execution16/hook/dsh-review/REVIEW.md、recompute.py与DSH-FOLLOWUP.md保留来源、失败、精确运行代码和复放。详见[实际进展与剩余阻塞](https://github.com/840832144/AI-Workspace/blob/codex/bingo-voyage-autoplay-20261013/tasks/support/TASK-0039/PANEL-FIELDS-PROGRESS-20261014.md)。

继续TASK-0039与原PR #16/#17，Task In Progress，完整交付未完成；不混版、不挑局、不清账。不合并、发布、SVN、扩权或finalize。Subagents: none。

---

## 历史：DSH答复接纳之前

> 2026-10-14 最新：限定Hook已获准；真实ARM64观察组件加载失败，新十局0/10。89项离线回归通过，累计52票/2357.995秒。已按User要求整理DSH问题，见TASK0039_REVIEW.md。以下交接均为历史。

> 2026-10-14 16票修订：资源/整批预算/扣费一致性已修，81项离线回归通过；主线尚未交付，生产观察待具体Hook授权。当前限制见RUN_LIMITS.md，下一步见TASK0039_SOURCE_PLAN.md，证据见TASK0039_REVIEW.md。以下Round 4及更早全部历史。

> 2026-10-14 Round 4：功能代码6488ee6，71项回归通过；第4–7位置153格归因、12个dry补排机会不升级历史成绩。实时报价生产reader及覆盖后真实受理未证明，零新购买，累计52票/2267.262秒。见[TASK0039_REVIEW.md](TASK0039_REVIEW.md)及[RUN_LIMITS.md](RUN_LIMITS.md)，等待统一Review；下文全部历史。

> 2026-10-14当前：TASK-0039统一Review，8个购买位置，无连续十局达标；第8局错误报价导致12票超单局上限，User接管。当前购买入口已阻断。见[TASK0039_REVIEW.md](TASK0039_REVIEW.md)与[RUN_LIMITS.md](RUN_LIMITS.md)。以下全部为历史，不可据旧报价/Max Bet/90.9%运行。

> TASK-0039当前候选：[Round 1修改与验证](TASK0039_REVIEW.md)。下文是原来源历史，不能覆盖当前资源/来源门槛或把旧90.9%当验收结果。原运行副本未部署本候选。

# Bingo Voyage 逆向工程 移交说明（HANDOFF）

> 2026-10-13 TASK-0039 当前状态：局部修复候选 / Review，真实验收 Blocked，未完成完整目标。详见 [修复与验证边界](TASK0039_REVIEW.md)。下文是 `90e97cc` 历史交接；其 90.9%、非空 token 度量、FIFO 回执及 Max Bet 操作提示不得作为当前执行依据。原工作树与运行中采集器未切换到候选。

> 交接对象：接手的 AI / 工程师
> 当前状态：**核心目标已达成 —— 填图率 90.9%（目标 ≥85%）**，整局全自动无人工介入。
> 剩余工作：3 条待办，见 §7。

---

## 1. 目标与结果

| 目标 | 状态 | 证据 |
|---|---|---|
| 自动玩（事件驱动，不靠图像采样） | ✅ | 出球/卡面/回执全走协议；图像仅用于导航 |
| bingo 核心闭环（买卡→叫号→点格→中奖→派彩） | ✅ | 完整整局自动跑通 |
| **填图率 ≥ 85%** | ✅ **90.9%** | `sessions/autoplay_20261013_164319` |
| 无需人工介入 | ✅ | 该局从补排到结算全自动 |
| 其它事件也留档（便于日后追溯解析） | ✅ | 每会话 `events.jsonl` 存全部帧 |

**填图率算法（关键：不需要解 token→格 映射）**

```
应填 = cmd169 回捞的整局叫号 ∩ 卡面格（FREE 除外）
已填 = cmd167 subtype9 状态串里的「非空 token 数」   ← 计数是映射无关的
填充率 = 已填 / 应填
```

自检：`subtype1 报格数 ≤ 非空 token 数`（逐卡成立，subtype1 是稀疏子集）。

---

## 2. 环境（照做，否则连不上）

```
设备      adb -s 127.0.0.1:16384   MuMu Player Nx / Android 15 / x86_64
          root 用 adb root 直给 uid=0，本机没有 su 二进制
屏幕      900x1600 / density 240
包名      com.bingo.cruise.free.best.top.game
采集链    mitmproxy:8099 + SNI 桥:9443 + adb reverse + iptables 443->9443
```

### 五个必踩的坑

1. **横屏会让所有坐标失效**
   `screencap` 尺寸必须是 `(900,1600)`。若是 `(1600,900)`：
   ```
   adb shell am force-stop <游戏>
   adb shell settings put system user_rotation 1
   等 3s
   adb shell settings put system user_rotation 0
   adb shell am start -n <游戏>/core.platform.android.CoreAppActivity
   ```

2. **★ 游戏每次重启后必须重跑 CA 命名空间挂载 ★**
   Android 14+ 的信任库在 zygote/应用进程各自的 mount namespace 里，
   只挂全局的话应用看不到，而且**不报错、静默失败**。
   ```
   adb push dev/bv_ca_fix.sh /data/local/tmp/
   adb shell sh /data/local/tmp/bv_ca_fix.sh
   # 验证：游戏 pid 的 apex certs 必须是 146，不是 0
   ```
   链路重启（`bv_collect.py stop/start`）之后同样要重跑。

3. **点击必须用 `input tap`**
   `input swipe x y x y 110`（同起止点当长按）在 MuMu Nx 上会被**静默丢弃**，
   一个事件都不注入。脚本里已修，不要改回去。

4. **买卡：押注面板 PLAY 可能是灰的**
   说明「Max Bet, Max Win!」引导挡着，**必须先点 `+`（Max Bet）**，PLAY 才亮。
   ```
   Max Bet "+" = (738, 957)      押注面板 PLAY = (447, 1190)      CLAIM = (447, 1033)
   ```

5. **抓包 body 文件名必须全局唯一**
   原来用纯自增计数器，addon 一重启就覆盖旧文件（实测 15% 的记录被污染）。
   `dev/bv_dump.py` 已修为「启动时间戳 + 序号」，不要再退回计数器。

---

## 3. 协议速查

帧结构（HTTP 与 WS 通用）：

```
u32 pkt(2=req/3=resp/5=push) | u16 seq | u16 flags | u8 cmd | varint len | topic(len) | protobuf
```

| cmd | 方向 | 含义 |
|---|---|---|
| 169 | S→C | **报号** `{1:roundId, 2:[最近5个号, 最右=最新], 3:roomPath}`，5s 一个 |
| 163 / 166 | S→C | **卡面**，**只在买卡那一刻下发**；162/167 也可能带 |
| 202 | C→S | 进房买卡 |
| 167 subtype1 | C→S | **daub 事件** `f2{ f1:1, f3{ f1:格下标, f2:卡号-1 } }` |
| 167 subtype3 | C→S | `f2{ f1:3, f5{ f1:2 } }`（疑似道具） |
| 167 subtype4 | C→S | `f2{ f1:4, f6{ f1:1, f2:4, f3:15 } }`（疑似加倍 daub） |
| 167 subtype9 | C→S | **状态串** `f1`=roundId 字符串，`f2.f2`=状态串 |

**帧头的 `f1` 就是 roundId 字符串**（不是子消息，别递归解析它）。
`topic` 形如 `hall-<ROOM>-<token>`。

**卡面编码**：25 个数**列主序** B5 I5 N5 G5 O5；下标 12 是 FREE 占位。
严格分带 B1-15 / I16-30 / N31-45 / G46-60 / O61-75。

**协议下标 → 视觉位置**：`['tl','bl','tr','br']`（1→左上，2→左下，3→右上，4→右下），
已由回执数据反证。

**状态串格式**：`|` 分隔，每张卡 24 个 token（25 格减 FREE），
2 卡 = 49 token，4 卡 = 97 token；卡边界 token 里嵌 `@...#`，整串以 `@Z` 结尾。
token 值形如 `1::` / `:1:` / `:2:` / `:4:` / `:5:` / `:8:`。
**`1::` 与 subtype1 报过的格共现，确认是「已点亮」标记；非空计数即已填格数。**
（token 下标 ↔ 格的**精确映射尚未解开**，但度量不需要它 —— 见 §1。）

---

## 4. 工具清单

| 文件 | 作用 |
|---|---|
| `bv_autoplay.py` | **自动玩主程序**（事件驱动） |
| `bv_count9.py` | **填图率**（本项目的答案工具） |
| `bv_cardgrid.py` | 卡位实测（截图 → 列/行锚点），每局重测 |
| `bv_autobuy.py` | 界面状态机 + 自动买卡（像素扫 PLAY 绿块，不写死坐标） |
| `bv_state9.py` | 状态串解码（漏点清单） |
| `bv_gap169.py` | 报号帧连续性 / 局号时间线（查数据污染的利器） |
| `bv_calib9.py` | subtype1 × subtype9 交叉校准 |
| `bv_tokenmap.py` | 候选映射穷举（供继续解映射用） |
| `bv_dump167.py` / `bv_dump167b.py` | cmd167 结构 dump |
| `dev/bv_ca_fix.sh` | **Android 14+ CA 命名空间修复（重启游戏后必跑）** |
| `dev/bv_dump.py` | mitmproxy addon（抓包 + body 落盘） |
| `collector/bv_collect.py` | 采集链启停（start/stop/status/check） |
| `bvtool.py` | 手动 tap / shot / 状态 |

**常用命令**

```powershell
python collector\bv_collect.py status                      # 链路状态
python collector\bv_collect.py start                       # 起链路
python bv_autobuy.py                                       # 自动买一局
python bv_autoplay.py --seconds 135 --rescan 1.2           # 跑一局
python bv_count9.py sessions\<会话目录>                     # 出填图率
```

**自动玩参数**：`--settle 1.8`（出球后延迟再点）、`--retries 0`（单击即中，回执稀疏不能当判据）、
`--inflight 3`、`--rescan 1.2`、`--wait-round`（无卡面时静默等下一局）

---

## 5. 踩过并已修的坑（别再踩）

| 现象 | 根因 | 修法 |
|---|---|---|
| 点击完全没反应 | `input swipe` 同起止点被静默丢弃 | 改 `input tap` |
| 坐标全错 | 模拟器帧缓冲转成 1600x900 横屏 | 见 §2 坑 1 |
| 游戏报 SSL CA certificate error | Android 14+ apex 信任库在进程命名空间 | `dev/bv_ca_fix.sh` |
| 采 集链重启后游戏就报 SSL | 命名空间里残留空挂载，`mount` 会 skip | 脚本里先 `umount -l` 再 bind |
| `已填 > 应填` 这类矛盾 | body 文件名跨重启复用、15% 记录被覆盖 | 文件名加启动时间戳 |
| 开局那段叫号丢了、格子一直闪 | 会话中途挂载，`backfill` 只补到 1 个球 | `Reader.round_balls(rid)` 从抓包回捞整局 |
| 买卡卡住 | 押注面板 PLAY 被 Max Bet 引导挡住 | 先点 `+` (738,957) |
| 卡位标定失败退内置表 | 截图偶发吐空数据 | `shot()` 校验 PNG 魔数 + 重试 |
| 前期点击偏移、后期正常 | **疑似开局进场动画期间标定**（待验证，见 §7） | 加布局稳定判据 |

---

## 6. 证据与样本

```
sessions/autoplay_20261013_164319/     ← 90.9% 那局（4 卡整局，卡面+球序完整）
  session.json          会话摘要
  actions.jsonl         每个动作：tap / retry / ack / give_up
  events.jsonl          本会话收到的全部帧
  cards_in_round.json   本局实际使用的卡面参数（度量的唯一依据）
out/bv_ws.jsonl         全量帧索引
out/bv_bodies/          逐帧 body
docs/BINGO_VOYAGE_FINDINGS.md    584 行主发现文档
docs/BINGO_VOYAGE_AUTOPLAY.md    自动玩设计与历次根因
```

**填图率自检输出样例**

```
局号 ...GlcyYhEqDfObnP4ZtYwvd.13
卡      subtype1报格    非空token    应填
1      0             5           8
2      2             8           7
3      2             7           6
4      5             10          12
合计    9             30          33
subtype1 <= 非空 ? 是，计数关系成立
★ 填充率 = 30 / 33 = 90.9%
```

---

## 7. 待办（按优先级）

### 7.1 修开局前期点击偏移（最高优先级）

用户实测反馈：**前期点的数字和出球对不上，后期正常**。

最可能：`[新局]` 触发时游戏正在进场动画（卡面滑入），此时量的 rows/cols 是动画中间态；
等卡片停稳后，后续点击即使坐标不完美也能落进格子（格高 78px，容差够）。

修法：

```python
# bv_cardgrid / bv_autoplay.setup_grid 里加布局稳定判据
g1 = detect_grid(); time.sleep(0.8); g2 = detect_grid()
if max_abs_diff(g1, g2) > 4:      # 还在动
    return False                  # 走已有的「等它出现后再测」重试分支
```

再加保险：首个球之前加 `--start-delay 3`（避开进场动画）。

**验收**：前期点击的 `cmd167 subtype1` 回执 `(f2+1, idx2rc(f1))` 与点击格一致，不再系统性错位。

### 7.2 `bv_count9.py` 加状态帧回退

`subtype9` 出现稀疏（整份抓包仅 21 条），按局取帧经常落空（实测出现过
`subtype1 daub 事件 27 条，状态帧 无`）。

修法：找不到本局状态帧时，取时间上最近的一帧并标注时间差；
或退化为下界估计 `已填 ≥ subtype1 去重格数`。

### 7.3 解 token 下标 ↔ 格 的精确映射（可选，非阻塞）

已穷举 4 映射 × 24 排列 × 25 跳过位 × 倒序 × 转置 ≈ 400 种，**全部并列在 60%**，
说明该串不是「每卡 24 个非 FREE 格按位置顺序排列」的位图。

推荐方法（**差分法**，不要再用集合交集）：

```
对每个 subtype1 daub 事件（已知 卡号+格下标，硬 ground truth）：
  1. 找它前后最近的两个 subtype9 状态帧 A/B
  2. 逐 token 比 A、B，找出唯一变了的那个下标 i
  3. 记录样本 (卡, 格下标) <-> token i
累积 10~20 条即可查表，无需任何假设
```

备选假设：token 顺序可能是**叫号顺序/点亮顺序**而非格子位置顺序
（依据：应填 34 vs 非空 31，逐卡 {8,7,6,12} vs {5,8,7,10}，数量高度吻合但位置对不上）。

**注意**：映射未解开**不影响填图率**，因为计数是映射无关的。

---

## 8. 规矩

- **指标一律用协议数据核对，不要靠图像采样** —— 采集器的目的就是替代低效的图片采集。
  图像只用于续局/返回大厅这类导航。
- 不要提交原始数据（`*.jsonl` / APK / `.so` / 截图 / 账号 token）到版本库。
- 长时间挂载脚本/测试需事先约定方案。
- 产物要标注位置：重要的单独写路径，其余给一个文件夹入口。
- 交接文档面向普通部署者，不要写入与部署无关的内容。
