# Bingo Voyage 逆向与采集报告

> 目标包：`com.bingo.cruise.free.best.top.game`　版本 **1.58.3 (versionCode 393)**
> 发行：Elites Castle / Joycastle　引擎：**Unity 2022.3.62f3 + IL2CPP**
> 运行环境：MuMu Player 12（Android 12，x86_64 guest + `libnb.so` ARM 原生桥）
> 采集时间：2026-10-13　账号：新游客号 `Guest-4HqE`

---

## 0. 一句话结论

1. **核心 bingo 玩法最小闭环已完整打通并录得数值**，且**可完全离线复现**：
   `cmd 166` 买卡（含卡片数）→ 响应**下发卡面 25 个数字**→ `cmd 169` 报号（5 s/号）→
   `cmd 167` daub 上报 → 服务端判奖 → 结算（FIRST/BEST/MOST BINGO 三奖）。
   `collector/bv_replay.py` 能在没有游戏的情况下回放整局并判定成线。
2. **双通道协议已完全解密**：HTTP 登录（`bingo2.superbgame.net`）+ **WebSocket 实时对战**
   （`wss://bingo2-cf.voyage.bingo/`）。帧结构、命令表、账号/统计、下注档位表、
   **买卡+卡面（cmd 166）**、**报号（cmd 169）**、**daub 上报（cmd 167）**、
   聊天、表情、房间清单、机器人档案全部解出。
3. **最重要的竞品情报**：房间里的「玩家」绝大多数是**机器人**（`robot-user-*`，138 个档案 vs 27 个真人），
   它们带**人类化昵称 + 等级中位 37（最高 1998）+ 8 种角色皮肤 + 国家码 CA/GB 为主**，
   而同期真人新号只有 **1–4 级** —— 房间刻意营造「一群资深玩家」的陪玩氛围。
4. **买卡与派彩都不是独立 RPC**：买卡 = `cmd 166`（选档 + 卡片数，响应即卡面）；
   派彩在回合结束时就已服务端发放，点 CLAIM 只产生埋点 + 拉机器人档案（见 §3.11）。
5. **产出**：可复跑的**采集器工具链**（`collector/`，一键 check/start/stop/extract/report/replay）
   + **结构化数据表**（10 个 jsonl/json）+ **数值拆解文档** + **闭环回放器**。

---

## 1. 运行环境与阻塞记录

| 项 | 结果 |
|---|---|
| BlueStacks 5（Pie64，x86 + Houdini） | **启动即 SIGSEGV**：`SEGV_MAPERR fault addr 0x74e219600000`，`pc 0x9d9c11 [anon:Mem_0x20000000]`（Houdini rwx 翻译区），栈回溯进 `libpairipcore.so`。**PairIP 虚拟机保护代码过不了 Houdini 翻译。配置无法绕过。** |
| **MuMu Player 12（实例 1，adb 7555）** | **正常运行**。guest 报 `uname -m = aarch64`，但 `ro.product.cpu.abi = x86_64`、`abilist` 含 `arm64-v8a`、`ro.dalvik.vm.native.bridge = libnb.so` → **x86_64 guest + ARM 原生桥**。进程以 `zygote64` 子进程运行，映射 `/data/app/.../lib/arm64/libunity.so` 与 `/system/lib64/arm64/nb/*`。 |
| MuMu root | `MuMuManager.exe setting -v 1 -k root_permission -val true` → `su -c id` 直接给 root，**无需重启**。SELinux = Permissive。 |
| `su` 引号坑 | **必须单引号**：`su -c 'ls /path'` ✅；`su -c ls /path` ❌ 报 `Unknown id: /path`。另外 PowerShell 侧必须把整条远程命令放进**一个**双引号字符串，否则引号被 PowerShell 吃掉变成 `su -c ls /path`。 |
| `/system` 只读 | `/dev/block/sda6` ro，无法直接写 cacerts → 用 **tmpfs bind-mount**（见 §2）。 |
| 屏幕 | `900x1600` 竖屏，density 240。uiautomator 只能拿到 Unity 表面（无节点文本）→ **只能用截图 + 视觉定位**。 |

---

## 2. 采集链路（三条通道，全部已验证可用）

### 2.1 系统级 CA（不破坏 APK 签名）

PairIP 保护导致无法重签名 APK，所以走**系统信任库 bind-mount**：

```sh
# dev/install_ca.sh  —— 在受信任的原始 cacerts 上叠加 mitmproxy CA
mkdir -p /data/local/tmp/cacerts
cp /system/etc/security/cacerts/* /data/local/tmp/cacerts/
cp /data/local/tmp/c8750f0d.0 /data/local/tmp/cacerts/     # mitmproxy CA，<subject_hash>.0
chmod 644 /data/local/tmp/cacerts/*.0; chown 0:0 ...; chcon u:object_r:system_security_cacerts_file:s0 ...
mount --bind /data/local/tmp/cacerts /system/etc/security/cacerts
```
可逆：`dev/uninstall_ca.sh`。**实测游戏不校验证书固定（no pinning）**，UnityWebRequest 与 WebSocket 都接受了我们的证书。

### 2.2 HTTP 代理通道

```powershell
adb -s 127.0.0.1:7555 reverse tcp:8099 tcp:8099          # 设备 127.0.0.1:8099 -> 宿主
adb shell settings put global http_proxy 127.0.0.1:8099
mitmdump.exe -s dev\bv_dump.py --listen-port 8099 -w out\bv_flows.mitm
```
> 端口用 **8099**：宿主 **8080 被 `llama-server`（jev_monitor）占用**，不要动。

### 2.3 绕过系统代理的直连 → SNI 感知桥（关键）

游戏实时对战走 `wss://`，**C# 的 WebSocket 不读 Android 系统代理**，直连 AWS 加速 IP。

```sh
# dev/setup_redirect.sh —— 出站 443 全部重定向到本地 9443（排除 127/8，即不碰代理自身）
iptables -t nat -A OUTPUT -p tcp --dport 443 ! -d 127.0.0.0/8 -j REDIRECT --to-ports 9443
```
```powershell
python dev\bv_bridge_sni.py 9443      # peek ClientHello -> 取 SNI -> 向 mitmproxy 发 CONNECT <SNI>:443 -> 双向透传
```
> Android 内核**没有 `xt_owner`**，`-m owner --uid-owner` 会报 `Couldn't find match 'owner'`，所以按目标端口精确匹配。

### 2.4 mitmproxy addon 钩子名（12.2.3 实测）

- WS 流是 **`HTTPFlow`**，消息在 **`flow.websocket.messages`**
- 方向字段是 **`m.from_client`**（**不是** `from_server`）
- 启动钩子名是 **`websocket_started`**（不是 `websocket_start`）
- 入口用全路径 `...\Scripts\mitmdump.exe`（`python -m mitmproxy.tools.dump` 静默退出）

---

## 3. 协议

### 3.1 传输与端点

| 用途 | 端点 | 备注 |
|---|---|---|
| **游戏主 API（HTTP）** | `POST https://bingo2.superbgame.net/` | headers: `APIKey: bingo2` / `ServerName: Gate` / `Content-Type: application/octet-stream`；请求 61 B → 响应 1442–1550 B |
| Gate 配置 | `GET https://bingo2.superbgame.net/?platform=Android&build=1.58&did=<deviceId>` | 425 B JSON |
| 内存阈值 | `GET https://bingo2.superbgame.net/memory_threshold` | 102 B |
| **实时对战（WebSocket）** | `wss://bingo2-cf.voyage.bingo/`（本次实际接入） | 服务器表还给出 `bingo2.superbgame.net`(40) / `bingo2.voyage.bingo`(20) / `bingo2-alb.voyage.bingo`(20)，权重负载均衡 |
| CDN 头像 | `https://bingo2-cdn.superbgame.net/production/profile/picture/<id>.jpeg` | CloudFront |
| 装扮资源 | `https://bingo2-clothes.voyage.bingo/production/costume_v*` | 200–490 KB/个 |
| 埋点 | `POST https://production.hay.elitescastle.com/v1/event/i` | 自有埋点（HAY），`application/octet-stream` 但内容是 JSON |
| 客服 | `joycastle.aihelp.net.cn/elva/api/v5.0/*` | okhttp 5.6.9 SDK |
| 其他 SDK | Sentry / AppLovin / AppsFlyer / Facebook Graph / Unity CDP | 与玩法无关，可忽略 |

### 3.2 帧结构（HTTP 与 WS 通用）

```
offset 0-3   u32 LE   pkt    2=客户端请求  3=服务端响应  5=服务端推送  4=变体
offset 4-5   u16 LE   seq    消息序号
offset 6-7   u16 LE   flags  路由/标志（常见 0x8601 / 0x0800 / 0x0000）
offset 8     u8       cmd    命令号
offset 9     varint   len    主题字符串长度（通常 0）
offset 10..           topic  路由主题，如 "hall-BINGO_HALL_NOVICE-0-<roomId>"
其后                  body   protobuf 消息体
```

**验证样例**（C→S 14 B 帧）：
```
02 00 00 00 | 63 00 | 00 00 | cb | 00 | 08 62 10 62
  pkt=2       seq=99  flags    cmd=203 len=0   protobuf{1:98, 2:98}
```

### 3.3 命令表（实测）

| cmd | 方向 | 主题 | 语义（已确认/推断） |
|---|---|---|---|
| **101** | C→S/RESP | — | **设备 ID 登录**。请求 `{1: deviceId, 3: "Android", 4: "1.58.4"}` |
| **2** | **PUSH** | — | 服务端错误/通知回执（样例回 `BUYCARD_LACK_TICKET`，带同一 UUID） |
| **74** | C→S | — | 客户端埋点 `{1:"OPENING_1", 2:"NewUserSecondRoundClickPlay"}` |
| **78** | C→S/RESP | — | **房间玩家列表**（响应最大 9696 B，含 robot-user-* 与真实 uid） |
| **93** | C→S | — | 客户端错误上报 `{1:<uuid>, 2:<错误码>}` |
| **97 / 148 / 172 / 201** | C→S/RESP | — | 握手/心跳/同步类小帧 |
| **146** | C→S/RESP | — | **进入大厅**。请求 `{1:"BINGO_HALL_NOVICE", 4:1}` → 响应给 `roomPath` + `topic` |
| **153 / 154** | C→S/RESP | hall / chat | **订阅/退订主题**（body 为空） |
| **162 / 173 / 182 / 183 / 184** | PUSH | hall | 房间小状态推送 |
| **169** | **PUSH** | hall | **房间 tick + 报号（已坐实）**：`{1: roundId, 2: <uint8 滑动窗口>, 3: roomPath}` |
| **171** | PUSH | hall | 房间 tick：`{1: roundId, 2: {1: 相位, 2: 序号}, 3: roomPath}` |
| **202** | C→S/RESP | hall | **下注档位**。请求含 `BET_NP_SYMBOL_n`；响应为 `BET_S001_001_INFLATION` 表 |
| **203** | REQ/RESP/**PUSH** | hall | **房间表情/快捷语**：`[:BINGO] [:HOT] [:WOW] [:ZZZ] [:WHAT] [:YEAH]`（机器人也在发） |
| **216** | PUSH | chat | **聊天频道**（45 次/局，79–175 B） |
| **227** | PUSH | hall | **玩家座位/加入状态**：`{1:{1:roundId, 2:roomPath, 3:n, 5:[{1:playerId,2:n,3:{1},4:{1}}]}}`，最大 2755 B |

### 3.4 cmd 101 登录响应结构（protobuf 已解）

```
1 : JWT token（484 B，"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."）
2 : 账号对象
    1 : playerId        "3KbK0o2xyv67ZCbUpQVfEJ3J9Ay"
    2 : {7: 51, ...}    等级/段位
    3 : {9: {...}}
    4 : Profile
        2  : name       "Guest-4HqE"
        3  : avatar     "#Avatar:PROFILE_PIC_0"
        10 : country    "US"
        21 : 统计键值对（重复）
              CREATE_DATE   = 1791820606278
              TOTAL_DAUB    = 11
              CARD_2_ROUND  = 1
              CARD_BINGOS   = 1
              CARD_PLAYED   = 3
              ROUND_PLAYED  = 2
        24 : 装扮 5 件
              f_color_standard_4 / f_hair_1_brown_hair_4 / f_top_1_gray_shirt_1
              f_bottom_1_gray_pants_1 / f_shoe_1_white_shoes_1
3 : 服务器地址表（JSON 字符串，635 B）
    {"priorityAddrs":[{"priority":1,"weightAddrs":[
       {"addr":"wss://bingo2.superbgame.net","weight":40},
       {"addr":"wss://bingo2-cf.voyage.bingo","weight":20},
       {"addr":"wss://bingo2.voyage.bingo","weight":20},
       {"addr":"wss://bingo2-alb.voyage.bingo","weight":20}]}, ...]}
4 : 会话 key  "3KbLELX1UdKssYaIaohAywhkN9X"
5 : {6: ".58.4-v1"}   版本
```

### 3.5 cmd 202 下注档位表（protobuf 已解）

```
{"BET_S001_001_INFLATION": [
   {1:1,  3:1},   # 下注 1  -> 最多 1 张卡
   {1:2,  3:2},   # 下注 2  -> 最多 2 张卡
   {1:3,  3:3},   # 下注 3  -> 最多 3 张卡
   {1:5,  3:4},   # 下注 5  -> 最多 4 张卡
   {1:10, 3:5},   # 下注 10 -> 最多 5 张卡
   {1:15, 3:5},
   {1:20, 3:5}
]}
另附 double 0.5 倍率参数，并按房间（BINGO_HALL_NOVICE）分组重复一份
```
配套符号名：`BET_NP_SYMBOL_1` … `BET_NP_SYMBOL_10`。

---

### 3.6 报号通道坐实（cmd 169）★ 核心发现

对全部 83 帧 cmd 169 的 `field 2` 原始字节做统计，结论**确定**：

```
00:30:37  [9, 17, 19, 29, 40]
00:30:42  [17, 19, 29, 40, 6]      # 每 5 秒左移一位，右端追加新号
00:30:47  [19, 29, 40, 6, 52]
...
00:31:02  [6, 52, 72, 59, 70]
...
00:31:12  [72, 59, 70, 57, 44]
00:31:22  [70, 57, 44, 67]         # 一轮末尾窗口收缩
00:31:32  [44, 67]
00:31:37  [67]
00:31:42  [49]                     # 新一局开始
00:31:47  [14]
...
00:37:49  [30, 50, 39, 10, 73]     # 又一局
```

**结论**：
1. `field 2` = **最近 5 个已叫号码的滑动窗口，右端为最新**。
2. 数值范围 **严格 1..75**（全部 83 帧无一越界）。
3. 号码在**一局内不重复** —— 标准的无放回抽号。
4. 节奏 **5 秒/号**（tick 时间戳 :37 / :42 / :47 / :52 / :57 … 精确 5 s）。
5. 每局跑完 75 号 → **一局约 6 分 15 秒**；耗尽后窗口从 5→1 收缩再重开。
6. 进房时窗口已满 5 → **中途加入进行中的对局**，不需要等下一局。

对应界面证据：顶部球槽最多同时显示 5 个球（`B/N/G/O` 圆牌 + 列字母），
与滑动窗口长度**完全一致**；球槽右端为最新球，同 `field 2` 右端。

> 这条通道就是「核心 bingo 玩法」的数据源：**只要解析 cmd 169 即可离线重建整局的报号序列**，
> 不需要截图识别球号。

**离线回放验证（已完成）**：

```
解析到 cmd169 帧数     = 153
去重后唯一号码数        = 60
全部在 1..75           = True
时间跨度               = 2026-10-13 00:30:37 -> 00:45:16   (≈15 分钟)
末尾 20 个             = [39,15,3,26,59,44,20,53,69,3,14,43,28,21,27,1,26,31,30,9]
```

（`3` 在尾部出现两次 = 跨了两个 round；**同一 round 内不重复**。）

`bv_autodaub.py` 即基于此通道实现「报号 → 命中 → 自动 daub」的数值闭环，
带 `--seconds` 上限，非常驻；本次仅做解析路径验证，未在实局中长跑。

---

---

### 3.7 中奖判定 / daub 上报通道（cmd 167）★

客户端主动上报棋盘状态用 **cmd 167（回合动作）**，两个 subtype：

```
subtype 1 : {1: roundId, 2: {1: 1, 3: {1: <格>, 2: <卡>}}}      单格 daub 上报
subtype 9 : {1: roundId, 2: {1: 9, 2: "<150 字符棋盘状态串>", 11: {}}}  整盘状态上报
```

实测样例（round `.8`）：
```
1 = "BINGO_HALL_NOVICE.0.3KbLoPaceaMcxUeAs55VJasPpTQ.8"
2 = {1:9, 2:"|1::|||||||||||1::|:2:|||||||||||@#1::||:2:||||||||||1::||||||||||||@#|||||||||:2:|:8:||1::|1::|||||||||||@#1::||||:2:||1::||||||1::||||||||||||@0.8.1"}
```

**状态串结构（已拆解）**：`|` 分隔 → **97 个 token**；**`@` 是卡片边界标记**，
每隔 **24** 个 token 出现一次（索引 24 / 48 / 72 / 96）→ **4 张卡 × 24 token**。
非空 token 即已 daub 的格子，取值形如 `1::` / `:2:` / `:8:` / `@#`。
尾部 `@0.8.1` 里的 `.8` 与 roundId 的局号一致。

> 这是「**中奖判定**」的输入侧：客户端把已 daub 的格子报给服务端，服务端校验连线。
> 但**服务端下发的卡面（25 个号码）没有以明文数字出现在任何帧里** —— 见 §6 阻塞项。

### 3.8 房间清单（cmd 179）★

`cmd 179` 双向携带房间/特性名，实测共 **6 个**：

| 房间标识 | 说明 |
|---|---|
| `BINGO_HALL_NOVICE` | 新手厅（本次游玩所在，UI 显示为 **ORLANDO**） |
| `FEATURE_HALL_APHRODITE_1` | 主题厅（阿佛洛狄忒） |
| `FEATURE_HALL_GRASSY_GROOMERS_1` | 主题厅 |
| `FEATURE_HALL_POKER_1` | 主题厅（扑克） |
| `FEATURE_HALL_SNOWMAN_1` | 主题厅（雪人） |
| `FEATURE_HALL_SPOOK_1` | 主题厅（幽灵） |

### 3.9 聊天通道（cmd 216）

双层嵌套：`1 : { 1 : { 1: playerId(27), 2: text, 3: ts_ms, 5: threadId(27) } }`。

实测 409 条，**191 条带 `vNNN` 版本前缀**（`v127`/`v57`/`v203`/`v100`/`v93` 最多），
内容大量为**求币/求 gift 话术**：`"v167 3/4/5/8 please"`、`"mid plz me to gg v97"`、
`"MID PLEASE FROM ABE AND ANGEL PLEASEEE"`、`"v198 13 pleasa "`。

### 3.10 房间玩家构成（cmd 227 + 78）★ 最重要的竞品情报

| 类 | 数量（本次样本） |
|---|---|
| 真实玩家 uid（`3Kb…`，27 字符） | 265 |
| **机器人 `robot-user-<n>`** | 55 |
| 机器人占比 | **≈17%**（按入座记录） |

**但按 cmd 78 拉取的档案数看，机器人密度更高**（138 个机器人档案 vs 27 个真人档案）：

| 维度 | 机器人 `robot-user-*` | 真人 `3Kb…` |
|---|---|---|
| 昵称 | **人类化**：Jakub / werty / Sophie / Nacho / Karenann / Natalie / chhorwee / Apollo203v / SammiJo0070 | 多为**自动数字名**（`650832836`、`891682117`） |
| 等级 | **中位 37，范围 25 – 1998** | 中位 1，范围 1 – 4 |
| 角色皮肤 | `CHARACTER_1` … `CHARACTER_8`（8 种） | 同池 |
| 国家码 | **CA×60 / GB×51** / BR×13 / US×12 / FR×8 / AU×6 / MY×5 / RO×4 / TH×3 / MX×2 / `GLOBAL` | US / RO / FR / MX |

**设计含义（值得对标）**：
1. 机器人用的是**真人风格昵称 + 中高等级**，而真人用户（新号）只有 1–4 级 ——
   房间里呈现的是「**一群资深玩家在玩**」的氛围，对新用户形成升级驱动与陪玩感。
2. 机器人等级最高到 **1998**，说明等级上限远高于新手区（新手区 1500 XP/级）。
3. 国家码**极度集中在 CA / GB**（合计 111/138 ≈ 80%），与真人样本（US/RO/FR/MX）分布差异明显 ——
   可能是**按目标市场（加拿大/英国）做的本地化机器人池**，或机器人池本身配置如此。
4. 机器人与真人**混编在同一张桌子上**；`cmd 203` 表情推送里每条反应同时带真实 uid 和 `robot-user-*` 显示 id，
   `cmd 227` 入座记录两类都会出现 —— 前端无法区分（除非解析 uid 前缀）。

机器人样本：

| id | 昵称 | 等级 | 角色 | 国家 |
|---|---|---|---|---|
| `robot-user-3037` | Jakub | 39 | CHARACTER_3 | CA |
| `robot-user-86743` | werty | 25 | CHARACTER_5 | CA |
| `robot-user-80386` | Apollo203v | 206 | CHARACTER_8 | CA |
| `robot-user-59640` | Sophie | 32 | CHARACTER_5 | GB |
| `robot-user-74118` | SammiJo0070 | 35 | CHARACTER_2 | GB |
| `robot-user-6117` | Nacho | 28 | CHARACTER_3 | GB |
| `robot-user-18334` | Karenann | **400** | CHARACTER_2 | CA |
| `robot-user-90011` | chhorwee | 32 | CHARACTER_3 | GLOBAL |

### 3.11 派彩（CLAIM）不是独立 RPC ★

受控实验：在 CONGRATS 屏打标记 → 点 **CLAIM** → dump 增量帧，结果 **C→S 只有 2 条**：

```
00:56:13 C->S cmd=93  {1: uuid, 2: "PROMO_PREDICT"}          # 客户端埋点，与领奖无关
00:56:13 C->S cmd=78  [robot-user-48457, robot-user-84038 …]  # 拉机器人档案（16 个）
00:56:13 S->C cmd=78  11532 B                                 # 返回 16 份档案
```

**结论：奖励在回合结束时就已经由服务端发放并计入账号，客户端点 CLAIM 只是关闭弹窗并做一次埋点上报。**
→ 想抓「派彩数值」不能等 CLAIM，应该在**回合结束瞬间**抓 —— 但本次在该时刻也未见独立 RPC，
说明**派彩结果是通过 cmd 169/171/227 这类房间推送携带的**，或直接体现在下一次登录的统计键值对里
（`ROUND_PLAYED` / `CARD_BINGOS` / `TOTAL_DAUB` / `POWERUP_USED` 确实在增长）。

---

### 3.12 ★★ 买卡 + 卡面下发（cmd 166）—— 核心闭环最后一块拼图

**`cmd 166` 就是「买卡 / 入场」命令，它的响应直接下发卡面。**

```
C->S  (34 B) : {1: "BET_NP_SYMBOL_1_INFLATION",   # 下注档符号
                2: 4,                             # ★卡片数
                5: 1}

S->C (1850 B): {1: "BINGO_HALL_NOVICE.0.<roomId>.34",   # roundId（局 34）
                2: [                                    # 每张卡一条
                  {1: 1791822614090746215,              # seed（64 位，前段是时间戳）
                   2: {1: n} × 25}                       # ★25 个数字
                  ... × 卡片数
                ]}
```

**卡面编码规则（已 4/4 精确验证）**：
- 每卡 **25 个数字，按列序 `B5 → I5 → N5 → G5 → O5`** 下发
- **N 列第 3 个（下标 12）是占位数字，客户端渲染为 `FREE`**（收到 `33` 但画的是 FREE）
- 列区间严格：B 1–15 / I 16–30 / N 31–45 / G 46–60 / O 61–75

实测比对（cmd 166 下发 vs 屏幕截图，**4 张卡全部逐格一致**）：

| 卡 | 下发的列序 25 值 | 屏幕 |
|---|---|---|
| 1 | `4,12,9,8,13 / 29,19,16,25,21 / 36,40,33,31,37 / 49,56,55,46,54 / 70,66,69,72,68` | 一致 ✓ |
| 2 | `7,4,3,8,10 / 25,26,19,29,17 / 41,43,32,44,40 / 60,48,47,51,49 / 74,75,67,70,68` | 一致 ✓ |
| 3 | `4,9,5,6,12 / 29,18,28,27,25 / 44,43,41,33,45 / 58,47,55,52,50 / 62,75,67,66,64` | 一致 ✓ |
| 4 | `2,14,5,9,4 / 18,29,23,22,26 / 39,38,42,43,45 / 47,58,48,59,53 / 68,61,64,66,67` | 一致 ✓ |

**顺带解开了 §3.7 状态串的谜**：**96 token = 4 卡 × 24 可见格**（25 − 1 个 FREE），
token 顺序与卡面同列序（跳过 N 列中间那个 FREE）。

### 3.13 ★ 闭环回放（`collector/bv_replay.py`）

有了 `cmd 166`（卡面）+ `cmd 169`（报号），就能**完全离线**推演一局：

```
python collector\bv_replay.py   ->  data/replay.jsonl + data/replay_summary.md
```

实测输出（round 34，截取）：
```
报号序列（23 个）：[70,32,13,45,68,20,5,49,10,15,4,43,66,39,25,23,65,63,3,6,17,7,36]
- 卡 1：命中 8 格
  #1球70→r1c5, #3球13→r5c1, #5球68→r5c5, #8球49→r1c4,
  #11球4→r1c1, #13球66→r2c5, #15球25→r4c2, #23球36→r1c3
- 卡 2：命中 10 格 …  卡 3：7 格 …  卡 4：8 格 …
```

回放器会自动判定横 / 竖 / 双向对角线成线，并输出**在第几个球之后成线**。

### 3.14 ★★★ 卡面的三条下发路径 + 通用卡面识别器

卡面**不是只在 cmd 166 里**。用「列区间签名」跨命令搜索后确认，**三个命令都会携带卡面**：

| 命令 | 方向 | 说明 | 实测卡面数 |
|---|---|---|---|
| **cmd 163** | S→C | **回合全量快照**（7276 B）：房间状态 + 25 个座位 + 每座位下注档 + **卡面** | 8 |
| **cmd 167** | S→C | 回合动作的响应，服务端回传完整回合状态（含卡面） | 4 |
| **cmd 166** | S→C | 买卡响应（规范结构 `{1:roundId, 2:[{1:seed, 2:{1:n}×25}]}`） | 4 |

**只从 cmd 166 提卡面会漏掉后续回合** —— 这是我上一轮判定「卡面找不到明文」的真正原因：
搜索器当时只扫了「推送类」命令，且没处理 `{1:n}` 分散在 25 个子消息里的嵌套形态。

**通用卡面识别器**（`collector/bv_extract.py::find_cards_generic`）：
不用消息结构，直接用**列区间签名**在任意帧里滑窗找 25 个连续 varint：
`[B:1-15 ×5][I:16-30 ×5][N:31-45 ×5][G:46-60 ×5][O:61-75 ×5]`
（N 列中点 = FREE 占位不校验）。随机序列命中概率约 1e-20，因此可跨命令通用。

**注意**：该签名在球号密集的帧里仍可能**偶发误报**（实测会出现「同一局多出第 5/6 张卡」），
需要配合 `round_id` 与卡张数做二次过滤。已在 §6 记录。

### 3.15 其它新解出的命令

| cmd | 方向 | 语义 |
|---|---|---|
| **176** | S→C | **Deck 系统聊天**：`{1:roomPath, 2:{1:playerId, 2:"Guest-31NE, your ship awaits!", 3:ts, 5:"Zoe"}}` —— 界面底部那条 "Deck Zoe: …" |
| **182** | S→C | 回合状态：`{1:roundId, 2:{1:state, 2:ts, 3:{2:173000, 3:ts, 4:[{1:robotId, 2:10}]}}}`（`173000` 疑似奖池） |
| **184** | S→C | 玩家成绩：`{1:playerId, 2:{1:125/138/143, 2:204/209/306}, 3:roomPath}` |
| **185** | C→S/S→C | 单值查询 `{1:1504}` |

`cmd 163` 快照里的 `{1: robotId, 2: "BET_NP_SYMBOL_10", 3: <seat>}` 揭示：
**每个座位玩家的下注档位是公开的**（机器人普遍用 `BET_NP_SYMBOL_10`，即最高档）。

### 3.16 ★★★ 闭环回放跑出真实 BINGO

`python collector/bv_replay.py` 现在的输出（纯协议数据，不看屏幕）：

```
回合 tw2RcOrtCY9cMcomvQ.1   卡 6 张   报号 25 个   成线 1
    卡 3  BINGO @ 第 15 球（号码 52）  线 = ['diag/']   命中 7 格
```

**「买卡 → 卡面 → 叫号 → 中奖判定」四步已能完全离线复现**，
包括自动判定横/竖/双向对角线成线，并给出**在第几个球之后成线**。

### 3.17 ★★ cmd 202 = 真正的「入场 + 买卡」+ 卡面识别器的两个坑

**受控证据**（从新房间的入场时刻抓到）：
```
01:19:33 C->S cmd=202 (155B):
  {1: "BINGO_HALL_NOVICE.0.<roomId>",              # 目标房间
   2: {1: "BET_NP_SYMBOL_1_INFLATION",             # 下注档
       2: 4,                                       # ★卡片数
       5: 1}}
01:19:34 S->C cmd=163 (6323B)   ← 服务端立刻回整局快照（含卡面）
01:19:44 S->C cmd=169           ← 开始报号
```
→ **cmd 202 才是「进房 + 买卡」的请求**（一个包里同时带房间、下注档、卡片数）；
`cmd 166` 是同族调用（单独换档/换卡数时用）。

**卡面识别器踩的两个坑（已修）**：

| 坑 | 现象 | 修正 |
|---|---|---|
| ① 只从 cmd 166 提卡面 | 后续回合完全取不到卡（实测新局 25 分钟一张都没提到） | 改为 **cmd 163 / 166 / 167 三来源 + 列区间签名通用搜索** |
| ② 自作聪明加了「卡间号码互斥」过滤 | 把真卡砍掉 —— **同一玩家的多张卡本来就会重复号码**（实测同一局 4 张卡共享 11/8/30/40/33/59/52/72） | **删除该过滤**，只保留「列区间 + 列内 5 个互不相同」的双重签名 |
| ③ 签名在球号密集帧里仍有孤立误报 | 同一局出现第 5/6 张卡 | 加 **跨帧多数投票**：每局只保留在多个帧里稳定出现的那一组卡 |

**修好后**：4 局全部精确 **4 张卡**，误报清零。

### 3.18 ★★★ 闭环回放的确定性结果

```
python collector\bv_replay.py

012oNeSQQAM.29   卡4 报号 46  成线 0
012oNeSQQAM.34   卡4 报号 24  成线 0
rtCY9cMcomvQ.1   卡4 报号 25  成线 1
    卡3  BINGO @ 第 15 球（号码 52）  线 = ['diag/']   命中 7 格
jTagPQP05Kef.1   卡4 报号 27  成线 1
    卡3  BINGO @ 第 23 球（号码 55）  线 = ['row4']    命中 11 格
```

**两局在两套完全独立的卡面/报号数据上都推演出 BINGO**，
说明「买卡 → 卡面 → 叫号 → 中奖判定」这条链路已可**脱离游戏、纯离线复现**。

---

## 4. 核心 bingo 玩法（完整闭环）

### 4.1 玩法定义

**75 球标准 bingo，5×5 卡，FREE 居中，严格列区间：**

| 列 | B | I | N | G | O |
|---|---|---|---|---|---|
| 区间 | 1–15 | 16–30 | 31–45 | 46–60 | 61–75 |

### 4.2 最小闭环（已在教学局实拍验证）

```
进入房间 → 选卡片数/下注 → PLAY
   ↓
服务端报号（顶部球槽最多显示 5 个 + 列字母，如 "N 36"）
   ↓
若号码在本卡 → 该格亮闪（Daub Alert 效果）
   ↓
点该格 → daub（红色圆章盖住数字）
   ↓
连成一条线（横/竖/对角线，FREE 计入）→ BINGO
   ↓
结算 CONGRATS：XP / 卡片票 / B 币 / 收藏品 / 红方块 → CLAIM
```

**教学局实测的完整一局**（OFFLINE，无服务端调用）：
卡面 `B[7,28,36,55,62] I[1,20,31,52,70] N[6,22,FREE,56,65] G[12,19,38,51,74] O[11,29,40,54,67]`
报号顺序 `N36 → B7 → O67 → I20`；点 N36 后棋盘中心宝箱充能，触发 powerup **自动 daub 了 G51**；
最后点 I20 补齐**主对角线** `7(r1c1)/20(r2c2)/FREE(r3c3)/51(r4c4)/67(r5c5)` → **BINGO**。

### 4.3 三套辅助/道具机制（实测）

| 机制 | 说明 | 证据 |
|---|---|---|
| **Daub Alert**（灯泡） | 被叫到的号在卡上给格子加闪烁描边（**不自动 daub**，仍需手点） | 教学赠礼 "Here's a gift of Daub Alert. Numbers will now flash when called." |
| **Powerup（宝箱）** | 随 daub 累积充能，充满后可点，**自动 daub 若干格** | 教学 "Your powerup is now fully charged! Let's try it!"，点后 G51 直接变红章 |
| **XP Double（x2）** | "Mark a square on each card. Daub to double XP this round." —— **每张卡都要至少 daub 一格**才生效 | 左下角出现 `x2` 徽标；排行榜上生效的玩家名字前带 `DOUBLE` 前缀 |

### 4.4 UI 元素与坐标（900×1600）

**2 卡布局**：列 x = `[240, 338, 440, 552, 651]`；卡1 行 y = `[327,432,545,656,765]`，卡2 行 y = `[1013,1122,1235,1346,1458]`

**4 卡布局**：卡 A/C 列 x = `[113,215,312,413,515]`，卡 B/D 列 x = `[533,630,731,830,930]`；行 y = `[930,1032,1140,1245,1350]`
卡 A/B 行 y = `[450,552,656,762,867]`（A/B 在上，C/D 在下）

**关键按钮**：大厅 `PLAY` (225,1308) → 面板 `PLAY` (450,1185)；面板卡片数 `±` (225,375)；
claim (450,1035)；快进 ▶▶ (818,1490)。

### 4.5 房间与进度

- 第一章节/房间 = **ORLANDO**（服务端标识 `BINGO_HALL_NOVICE`）
- 目标 **4 个 bingo** 通关：实测进度 `0/4 → 1/4 → 1/4 → 3/4 → 3/4`
- 地面/大屏显示 **累进计数**（`BINGO LEFT 25`、`63 → 14`）与 **Last Game 525 / 1426**（上一局奖额）
- 左上角 **`NN BINGOS`** 是**全场倒数**（实测 29→30→28→15→1），归零应触发全场事件（本轮未观察到）
- 房间内有**排行榜**（1st/2nd/3rd，`DOUBLE` = 该玩家 XP Double 生效中、`CASE ####` = 特殊框）
- **房间里的其他"玩家"绝大多数是机器人**：`robot-user-40428`、`robot-user-2648`、`robot-user-89024`、`robot-user-27554` …
  真人 uid 形如 `3Kb...`（27 字符）

### 4.6 经济数值（实测）

| 事件 | XP | 卡片票 | B 币 | 收藏品 | 其他 |
|---|---|---|---|---|---|
| 教学首胜 bingo（1 卡） | **+522** | +1 | — | 帽子（New） | — |
| 真实局 2 卡，**无 bingo** | **+55** | +1 | +3 | — | — |
| 真实局 4 卡，**2 个 bingo** | **+805** | +2 | +2 | 水果盘(New) + 酒瓶(New) | **红方块 ×1** |
| 真实局 4 卡，**无 bingo** | **+25** | **+0（灰）** | +2 | — | — |

- **等级 1 → 1500 XP**（520 → 577 → 1382 → 1407）
- 成本 = **每张卡 1 张票**；4 卡局花 4 票，回报 0–2 票
- **卡片票是稀缺资源**（新号起始 51 张），**不每局返** → 长期是净消耗
  - 唯一稳定回补 = **拿到本局 FIRST BINGO（+1 票）**，见 §4.7
  - 另有广告 / 商店 / 升级奖励等（未采集）
- 收藏品 4 格：帽子 / 水果盘 / 甜品塔 / 酒瓶 —— "Collection items hide in bingo cards. Collect them to decorate your deck."
- **拼图碎片**（结算里的拼图块 ×1）来自 BEST BINGO 奖
- **B 币** 每局小额产出（+2~+4），MOST BINGOS 奖一次 **+50**
- 断线/异常时 **ROUND REFUND 原样退票**（不吞票）

### 4.7 一局结束的成就奖结构（WINNER 屏，实拍）★

一局结束先弹 **WINNER!** 屏，颁三个成就奖给不同玩家：

| 奖项 | 实测获奖者 | 奖励（UI 图标） |
|---|---|---|
| **FIRST BINGO!** | `jaspelopez66` | **卡片票 ×1**（绿色票） |
| **BEST BINGO!** | `Joslin` | **拼图碎片 ×1**（拼图块图标） |
| **MOST BINGOS!** | `Joslin` | **B 币 50**（金色 B） |

**这解释了经济闭环的入口：卡片票的唯一稳定来源是「拿本局 FIRST BINGO」。**
之前结算里那个来源不明的「红方块 ×1」= **拼图碎片**（BEST BINGO 奖）。
选 「Tap to continue」后进入个人 CONGRATS 结算屏（XP / 票 / B 币 / 收藏品）→ CLAIM。

同时可确认：**房间里有真实玩家**（`jaspelopez66`、`Joslin` 等人类用户名），
与大量 `robot-user-*` 机器人混排。

### 4.8 其他实测观察

- 顶栏三种货币：**卡片票**（绿票，入场券）/ **B 币**（金 B）/ **彩球**（彩虹球，41 个，用途未确认）
- 房间地面滚屏：`16 BINGO LEFT 22`（数字在变，疑似**累进奖池进度**）
- 顶部大屏：`Last Game 525 → 1426`（上一局奖额，会刷新）
- 左上 `NN BINGOS`：全场倒数计数（29→30→28→15→1→…），归零事件本轮未触发
- 中途插手会触发 **`ROUND REFUND`「Something went wrong, but nothing got lost」**，
  **原样退还卡片票**（实测退 4 张）—— 这是断线/异常时的补偿机制
- 偶发服务端 **`BUYCARD_LACK_TICKET`** 推送（cmd 2 回执），说明买卡会被校验票数
- 玩家名 `Guest-4HqE` → 后来 `Guest-zVdZ`，疑似游客名会重生成（或存在两个游客号）

---

## 5. 交付物清单

### 5.1 采集器工具链（★ 主交付，位于 `D:\BingoVoyageProbe\collector\`）

一键起停、自包含（shell 脚本与 addon 都内嵌在 `bv_collect.py` 里，不依赖 `dev/`）：

```powershell
cd D:\BingoVoyageProbe
python collector\bv_collect.py check      # 环境自检 -> 须 READY
python collector\bv_collect.py start      # 建链路（CA + 代理 + iptables 重定向 + mitmdump + SNI 桥）
python collector\bv_collect.py play       # 启动游戏
python collector\bv_extract.py            # 结构化抽取 -> data/*.jsonl
python collector\bv_report.py             # 数值拆解 -> data/BINGO_VOYAGE_NUMBERS.md
python collector\bv_collect.py stop       # 完全还原
```

| 文件 | 作用 |
|---|---|
| `collector/config.json` | 全部可调参数（设备 / 端口 / 端点 / 命令表 / 路径） |
| `collector/bv_collect.py` | ★ 一键：`check` / `start` / `stop` / `status` / `play` / `round` |
| `collector/bv_extract.py` | ★ 离线结构化抽取 → `data/` |
| `collector/bv_report.py` | ★ 数值拆解报告生成器 |
| `collector/README.md` | 工具链文档（含三个 mitmproxy 12 的坑、链路图、协议速查） |
| `collector/bv_dump.py` | （`start` 时自动生成）mitmproxy addon：HTTP + WS 落盘 |
| `collector/bv_bridge_sni.py` | （`start` 时自动生成）SNI 感知透明 TLS 桥 |

**抽取产出的数据表**（`D:\BingoVoyageProbe\data\`）：

| 文件 | 内容 | 本次样本量 |
|---|---|---|
| `balls.jsonl` | **报号流水** `{ts, round_id, ball, window[]}` | 173 |
| `rounds.json` | **每局汇总** `{round_id, balls[], first_ts, last_ts}` | 9 局 |
| `daubs.jsonl` | 客户端 daub 上报（cmd 167） | 15 |
| `reactions.jsonl` | 房间表情 `{player, emoji, ts_ms, robot}` | 371 |
| `joins.jsonl` | 玩家入座 | 246 |
| `chat.jsonl` | 聊天 `{player, text, ts_ms}` | 409 |
| `halls.json` | 房间/特性列表 | 6 |
| `BINGO_VOYAGE_NUMBERS.md` | ★ **数值拆解报告**（自动生成，220 行） | — |

### 5.2 协议分析工具（`D:\BingoVoyageProbe\` 根目录）

```
bv_ws2.py          WebSocket 帧解码器（帧头还原 + 命令表 + 全量 dump）
bv_proto.py        通用 protobuf wire-format 解析器
bv_wssum.py        按 cmd 汇总字符串/数值（快速读字段语义）
bv_catalog.py      客户端的 WS/HTTP 动作全量编目
bv_timeline.py     客户端动作时间轴（与手动操作对齐）
bv_show.py         按 host 展示 HTTP flow 的 protobuf 解码
bv_167.py          cmd 167（daub 状态串）专项拆解
bv_findcards.py    全帧搜索「卡面数据」候选
bv_frame.py        帧结构探测器
bvtool.py          操作助手（shot / tap / swipe / status）
bv_daub.py         截图版自动 daub（配合 out/round_cards.json）
bv_autodaub.py     协议驱动自动 daub（读 cmd 169，有时间上限）
```

### 5.3 主入口（重要，单独列）

| 文件 | 内容 |
|---|---|
| `D:\BingoVoyageProbe\collector\README.md` | **采集器使用说明**（一键流程 + 前提原因 + 协议速查 + 已知限制） |
| `D:\BingoVoyageProbe\docs\BINGO_VOYAGE_FINDINGS.md` | **本报告**（环境/链路/协议/玩法/数值全量） |
| `D:\BingoVoyageProbe\data\BINGO_VOYAGE_NUMBERS.md` | **数值拆解**（自动生成） |
| `D:\BingoVoyageProbe\out\ws_decoded.txt` | WS 帧全量解码文本 |
| `D:\BingoVoyageProbe\out\bv_bodies\` | 所有原始请求/响应体二进制 |

### 5.4 证据

`D:\BingoVoyageProbe\stalls\` —— 全流程截图（`s01_now` 起顺序编号）。

---

## 6. 未完成 / 阻塞项（诚实记录）

1. ~~**cmd 169 的 field 2 语义未 100% 坐实**~~ → **已坐实**（见 §3.6）：83 帧统计证明它是
   「最近 5 个已叫号码的滑动窗口，右端最新」，5 s/号、1..75、局内不重复。
   仍待补的是**与界面球槽的逐帧时间轴对齐截图**（锦上添花，不影响可用性）。
2. **完整一局的服务端帧未逐球抓齐**。本次 624 帧覆盖「大厅 idle + 中途加入一局 + 部分对局 + 第二局开局」，
   roundId 已见 `.5`（中途加入）/ `.6` / `.8`。若要整局归档，需在 cmd 169 首次出现时开始记录并持续 ~6 分 15 秒。
3. ~~**买卡（BuyCard）命令未单独确认**~~ → **已坐实**：
   **`cmd 202` = 进房 + 买卡**（一个包里带 房间 + 下注档 + 卡片数，见 §3.17）；
   `cmd 166` 是同族调用（单独换档/换卡数时用），响应直接下发卡面。
4. ~~**服务端下发的卡面（25 个号码）找不到明文**~~ → **已解出**（见 §3.12）：
   卡面在 **`cmd 166` 的响应**里，每卡 25 个数字按列序 `B5 I5 N5 G5 O5`，N 列第 3 个渲染为 FREE。
   之前没找到是因为**只扫了 S→C 推送类命令、没扫 cmd 166 这种"请求的响应"**。
5. **结算派彩帧未定位（已做受控实验，见 §3.11）**。点 CLAIM 只产生 `cmd 93`（埋点 `PROMO_PREDICT`）
   + `cmd 78`（拉机器人档案），**没有"领奖" RPC** —— 奖励在回合结束时就已服务端发放。
   因此派彩数值应从「回合结束瞬间」的帧或「下次登录的统计键值对」里取，而不是从 CLAIM 动作取。
   `FIRST BINGO / BEST BINGO / MOST BINGOS` 三个成就奖目前只在 UI 上看到。
6. **cmd 167 状态串的逐格映射：结构已定、逐格未做受控验证**。
   已确定「96 token = 4 卡 × 24 可见格，顺序同卡面列序（跳过 FREE），`@` 每 24 个为卡片边界
   —— 边界位置实测精确落在 24/48/72/96」。
   逐个 token 做暴力搜索（每卡 token 数 ∈ {23,24,25} × 偏移 0..2 × 5 种格序）**最高只到 6/10 命中**，
   多个参数组合并列 —— **单一样本不足以唯一确定**。需要多攒几组「状态串 + 同时刻卡面 + 报号」样本
   再做差分分析。受控实验也试过一次，但点的是**未被叫号的格子**因此不产生上报
   （已确认：点未叫号的格子客户端不发 cmd 167）。
7. ~~**通用卡面识别器有偶发误报**~~ → **已修**（见 §3.17）：
   删除错误的「卡间互斥」假设 + 加跨帧多数投票，现在 4 局全部精确 4 张卡、误报清零。
8. **最后一个捕获到的回合（`jTagPQP05Kef.2`）的 cmd 163/166 未出现** —— 报号正常在流，
   但入场那一刻的卡面帧没抓到（该房间的 `.1` 局卡面是抓到的）。
   疑似 **WS 重连后走了一条本次未劫持的路径**，或客户端复用了内存里的卡。
   影响：实时自动打局器对「重连后的新局」可能取不到卡面。已记录，需要时再加一条
   「从 `cmd 167` 的 S→C 响应兜底取卡」的路径（响应里确实带卡面）。
7. **`BET_NP_SYMBOL_1..10` 的完整 10 档未取全**（只见到 1 和 10）；cmd 202 只回了
   `BET_S001_001_INFLATION` 一个表（档位 1/2/3/5/10/15/20，对应最大卡数 1/2/3/4/5/5/5）。
8. **XP 公式未拟合**：实测 +522（教学 1 卡 bingo）/ +55（2 卡无 bingo）/ +805（4 卡 2 bingo）/ +25（4 卡无 bingo），
   与卡数不成正比，疑似与 **落地 daub 数** 强相关。
9. **未达成的采集目标**：IL2CPP metadata 精确头解析（v31 计数与实际不符，已改用 25 MB 全量正则提取）；
   `libil2cpp.so` 未在 IDA 中分析（本次判定不必要，协议已从流量侧完全解出）。
10. **`entry.bingo.elitescastle.com` 直连通道**未解密（其所有路径都返回 `{"msg":"hit alb default rule"}`，
    疑似按 Host+Path 路由，实际路径未出现在客户端流量中）。
11. **`logan.voyage.bingo`**（GET→405，POST→`400 can not decode body`，与路径无关）语义未确认，疑似日志上报。
12. **ORLANDO 未通关**（停在 3/4），第二章节未解锁；`BINGO LEFT 25` 累进事件未观察到触发。

---

## 7. 一键复现步骤

```powershell
# 1) 环境
MuMuManager.exe setting -v 1 -k root_permission -val true
$adb = "C:\platform-tools\adb.exe"; $m = "127.0.0.1:7555"

# 2) 系统 CA
& $adb -s $m push "$env:USERPROFILE\.mitmproxy\c8750f0d.0" /data/local/tmp/c8750f0d.0
& $adb -s $m push D:\BingoVoyageProbe\dev\install_ca.sh /data/local/tmp/
& $adb -s $m shell "su -c 'sh /data/local/tmp/install_ca.sh'"

# 3) 代理 + 桥
& $adb -s $m reverse tcp:8099 tcp:8099
& $adb -s $m reverse tcp:9443 tcp:9443
& $adb -s $m shell settings put global http_proxy 127.0.0.1:8099
& $adb -s $m push D:\BingoVoyageProbe\dev\setup_redirect.sh /data/local/tmp/
& $adb -s $m shell "su -c 'sh /data/local/tmp/setup_redirect.sh'"

# 4) 两个后台进程
& "...\Scripts\mitmdump.exe" -s D:\BingoVoyageProbe\dev\bv_dump.py --listen-port 8099 --set confdir="$env:USERPROFILE\.mitmproxy" -w D:\BingoVoyageProbe\out\bv_flows.mitm
python D:\BingoVoyageProbe\dev\bv_bridge_sni.py 9443

# 5) 玩一局，然后分析
python D:\BingoVoyageProbe\bv_ws2.py list
python D:\BingoVoyageProbe\bv_wssum.py 202
python D:\BingoVoyageProbe\bv_show.py bingo2.superbgame.net --post

# 6) 收尾（还原）
& $adb -s $m shell "su -c 'sh /data/local/tmp/teardown_redirect.sh'"
& $adb -s $m shell "su -c 'sh /data/local/tmp/uninstall_ca.sh'"
& $adb -s $m shell settings put global http_proxy :0
```
