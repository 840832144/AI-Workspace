# Bingo Voyage 采集器

> 目标：`com.bingo.cruise.free.best.top.game`（Bingo Voyage，Elites Castle / Joycastle，Unity 2022.3 + IL2CPP）
> 环境：MuMu Player 12（Android 12，x86_64 guest + `libnb.so` ARM 原生桥）
> 产出：**结构化数据表** + **数值拆解报告** + **可复跑的一键链路**

---

## 快速开始（4 条命令）

```powershell
cd D:\BingoVoyageProbe

python collector\bv_collect.py check     # 1. 环境自检，须 READY
python collector\bv_collect.py start     # 2. 建立抓包链路（装 CA / 代理 / 重定向 / 两个后台进程）
python collector\bv_collect.py play      # 3. 启动游戏，手动玩几局
python collector\bv_extract.py           # 4. 抽取 -> data/*.jsonl
python collector\bv_report.py            # 5. 生成 -> data/BINGO_VOYAGE_NUMBERS.md

python collector\bv_collect.py stop      # 收尾：完全还原设备
```

不想手玩也可以用协议驱动自动 daub（**有时间上限，非常驻**）：

```powershell
python collector\bv_collect.py round --seconds 120
```

---

## 为什么需要 root + 证书重定向（关键前提）

游戏有 **两条独立网络通道**，只挂 HTTP 代理只能看到其中一条：

| 通道 | 端点 | 是否走系统代理 |
|---|---|---|
| 登录 / 账号态（HTTP POST） | `bingo2.superbgame.net` | ✅ 走 |
| **实时对战（WebSocket）** | `wss://bingo2-cf.voyage.bingo/` | ❌ **不走**（C# WebSocket 忽略 Android 全局代理），直连 AWS 加速 IP |

所以除了 CA + 代理，还必须：

1. **系统信任库装 mitmproxy CA**：APK 有 PairIP 保护无法重签名，只能走 `tmpfs bind-mount` 覆盖
   `/system/etc/security/cacerts`（`/system` 是只读的 `/dev/block/sda6`）。
2. **iptables 重定向出站 443 → 本地桥端口**，把绕过代理的直连也拉进来
   （Android 内核**没有 `xt_owner`**，`-m owner` 会报 `Couldn't find match 'owner'`，只能按目的端口匹配）。
3. **SNI 感知的透明桥**：桥 peek 首个 ClientHello，取出 SNI，再向 mitmproxy 发 `CONNECT <SNI>:443`。
   一个端口就能接管所有域名，不需要为每个域名单独配桥。

```
设备 :443 ──iptables REDIRECT──> 127.0.0.1:9443 ──adb reverse──> 宿主 :9443
                                                                  │ bv_bridge_sni.py
                                                                  │ 取 SNI
                                                                  ↓
                                                    CONNECT <SNI>:443 → mitmproxy :8099 → 落盘
```

> ⚠️ **宿主 8080 别用**：本机 8080 被 `llama-server`（jev_monitor）占用。本项目统一用 **8099**（代理）+ **9443**（桥）。

---

## mitmproxy 12.2.3 的三个坑（都已踩过并写进 addon）

| 坑 | 正确写法 |
|---|---|
| WebSocket 流不是独立类型 | 它是 **`HTTPFlow`**，消息在 **`flow.websocket.messages`**（不是 `flow.messages`） |
| 消息方向字段 | **`m.from_client`**（**不是** `from_server`，后者不存在） |
| 启动钩子名 | **`websocket_started`**（**不是** `websocket_start`） |

另外：`mitmdump.exe` 在 `%APPDATA%\Python\Python312\Scripts\`，不在 PATH；
`python -m mitmproxy.tools.dump` 会**静默退出**，必须用全路径 exe。

---

## 协议

### 帧结构（HTTP 与 WebSocket 通用）

```
offset 0-3   u32 LE   pkt    2=客户端请求  3=服务端响应  5=服务端推送  4=变体
offset 4-5   u16 LE   seq    消息序号
offset 6-7   u16 LE   flags  路由/标志（常见 0x8601 / 0x0800 / 0x0000）
offset 8     u8       cmd    命令号
offset 9     varint   len    主题字符串长度（HTTP 常为 0）
offset 10..  bytes    topic  路由主题，如 "hall-BINGO_HALL_NOVICE-0-<roomId>"
其后                  bytes  protobuf 消息体
```

验证样例（C→S 14 B）：
```
02 00 00 00 | 63 00 | 00 00 | cb | 00 | 08 62 10 62
  pkt=2       seq=99  flags    cmd=203 len=0  protobuf{1:98, 2:98}
```

### 命令表

完整表见 `config.json` 的 `commands` 段。核心几条：

| cmd | 方向 | 语义 |
|---|---|---|
| **101** | C→S/RESP | 设备 ID 登录（HTTP `POST /`，带 `APIKey: bingo2` / `ServerName: Gate`） |
| **146** | C→S/RESP | 进入大厅 `{1:"BINGO_HALL_NOVICE", 4:1}` → 返回 roomPath + topic |
| **153/154** | C→S | 订阅/退订 topic |
| **158** | C→S | 大厅参数 `{2:10}` |
| **167** | C→S | **回合动作**：subtype `1` = 单格 daub 上报；subtype `9` = 整盘状态串 |
| **169** | S→C | ★**报号**：`{1:roundId, 2:[最近 5 个号码 uint8 滑动窗口], 3:roomPath}` |
| **171** | S→C | 回合事件 `{1:roundId, 2:{1:26, 2:序号}}` |
| **179** | 双向 | 房间/特性列表（`FEATURE_HALL_*`） |
| **202** | C→S/RESP | 下注档选择 + `BET_*_INFLATION` 表 |
| **203** | S→C | 表情/快捷语 `[:BINGO][:HOT][:WOW][:ZZZ][:WHAT][:YEAH][:OOPS][:LUCKY]` |
| **216** | S→C | 聊天（双层嵌套 `1:{1:{1:playerId, 2:text, 3:ts, 5:thread}}`） |
| **227** | S→C | 玩家入座 `{1:{1:roundId, 2:roomPath, 5:[{1:playerId, 2:state}]}}` |

### ★ 报号通道（cmd 169）—— 核心玩法数据源

`field 2` = **最近 5 个已叫号码的滑动窗口，右端为最新**。已用 150+ 帧统计坐实：
数值严格 1..75、同局内不重复、**5 秒/号**、窗口右移一位追加一个号。
→ **不靠截图即可离线重建整局报号序列。**

### ★ daub / 中奖判定上报（cmd 167）

```
subtype 1 : {1: roundId, 2: {1: 1, 3: {1: <格>, 2: <卡>}}}     单格 daub
subtype 9 : {1: roundId, 2: {1: 9, 2: "<150 字符棋盘状态串>"}}  整盘状态
```

状态串结构：`|` 分隔 → 97 个 token；**`@` 是卡片边界标记，每 24 个 token 出现一次**
（索引 24 / 48 / 72 / 96）→ **4 张卡 × 24 token**；非空 token 即已 daub 的格子
（取值形如 `1::` / `:2:` / `:8:` / `@#`）。

---

## 目录

```
collector/
  config.json        全部可调参数（设备/端口/端点/命令表/路径）
  bv_collect.py      ★ 一键起停：check / start / stop / status / play / round
  bv_extract.py      ★ 离线结构化抽取 -> data/
  bv_report.py       ★ 数值拆解报告生成 -> data/BINGO_VOYAGE_NUMBERS.md
  bv_dump.py         （start 时自动生成）mitmproxy addon：HTTP + WS 落盘
  bv_bridge_sni.py   （start 时自动生成）SNI 感知透明 TLS 桥

../out/
  bv_ws.jsonl        WS 帧索引（方向/长度/帧头/body 文件名）
  bv_flows.jsonl     HTTP flow 索引（含 protobuf 原始字节 base64）
  bv_bodies/         所有原始请求/响应体二进制
  bv_flows.mitm      mitmproxy 原始流文件

../data/
  balls.jsonl        报号流水     {ts, round_id, ball, window[]}
  rounds.json        每局汇总     {round_id, balls[], first_ts, last_ts}
  daubs.jsonl        客户端 daub 上报
  reactions.jsonl    房间表情
  joins.jsonl        玩家入座
  chat.jsonl         聊天
  halls.json         房间/特性列表
  BINGO_VOYAGE_NUMBERS.md  ★ 数值拆解报告（autogen）

../bv_*.py           协议分析工具（bv_ws2 帧解码 / bv_proto protobuf / bv_wssum 字段汇总 …）
../docs/             逆向结论文档
../stalls/           全流程截图
```

---

## 已知限制

1. **卡面（25 个号码）不是明文下发的**——全量扫描 2000+ 帧未找到 25 个 1–75 的 varint 序列，
   疑似客户端按种子本地生成，或编码在 cmd 167 的状态串里。目前卡面靠截图录入
   （`out/round_cards.json`）。
2. **结算派彩帧未定位**——`FIRST BINGO / BEST BINGO / MOST BINGOS` 三个成就奖只在 UI 上看到，
   还没有对应到具体协议帧（`ROUND_PLAYED` / `CARD_BINGOS` 等统计确实在增长）。
3. **买卡（BuyCard）命令未单独确认**——只知道成本 = 每张卡 1 张票，
   且服务端会用 `BUYCARD_LACK_TICKET`（cmd 2 推送）拒绝票数不足。
4. `entry.bingo.elitescastle.com` 直连通道未解密（全路径返回 `hit alb default rule`）。

以上均记录在 `docs/BINGO_VOYAGE_FINDINGS.md` §6。
