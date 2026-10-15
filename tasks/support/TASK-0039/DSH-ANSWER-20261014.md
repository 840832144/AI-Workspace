> 来源：User转交的DSH分析答复。仅将固定ADB连接标识替换为占位符，原始文件保留于受控目录；其余内容原样保留。文内推论、建议与停止条件不是新增授权或已采纳事实，请先读[独立复核](DSH-ANSWER-REVIEW-20261014.md)。

# TASK-0039｜DSH 答复：emulated realm 加载失败（2026-10-14）

对应 `DSH-QUESTIONS-20261014.md`。本文件只回答问题与给出可核验事实，**不申请新任务、额度或权限**；
不含账号、卡面、余额或业务日志。源码结论来自 frida-core **16.7.19** 官方 tag，逐行给出文件:行号，
可自行复核。

---

## 零、先给结论

1. `ProtocolError: process is not using emulation` **不是**「进程没有 ARM 翻译」的意思。
   它是源码里一个**兜底错误文案**：只要 `NativeBridgeLoadLibrary*()` **返回 NULL** 就抛它。
   你们的证据（`libil2cpp.so` 为 AArch64 且已映射、`/system/lib64/libhoudini.so` 已映射）
   已经**证伪**了文案的字面含义。

2. 真正发生的事是：**Frida 找到了 NativeBridge API，也解析出了加载函数，但用它去加载
   自己释放出来的 `frida-agent-arm64.so` 时被 bridge 拒绝/失败。**

3. **已离线排除两个可自控变量**（0 秒设备时间）：
   - 你们改过的辅助二进制与官方**只差 19 个字节**、全部是同一个路径字符串、**无任何代码改动** → 不是它；
   - 官方 server **内嵌了** `frida-agent-arm64.so` → 不是「构建缺资源」。
   剩下的是**上游 Frida 与运行环境**。

4. 在**原实例、本权限、Frida 16.7.19** 下，**没有**任何已验证的被动观察接入方式。
   同症状、同版本、同厂商的上游 issue 至今 **open**，且第三方复现出唯一可行方向是**换环境**。

5. 因此这是一道**授权范围问题**，不是代码问题。你们仓库内的改动改不掉它。

---

## 一、问题一：最可能的原因

### 1.1 已核实的事实（源码级，可直接引用）

| # | 事实 | 位置 |
| --- | --- | --- |
| F1 | 该错误在 `load_library_ext()` / `load_library()` 返回空时抛出，**是通用文案** | `frida-core/16.7.19/lib/agent/agent.vala:1371-1372` |
| F2 | `NativeBridgeApi.open()` 先枚举模块，**要求**匹配 `/lib(64)?/libnativebridge.so`，**且**要求 `libart.so` 或 `libdvm.so`；两者缺一都会抛**另外的**错误 | `agent.vala:1511-1526` |
| F3 | 接着要求解析出 `NativeBridgeLoadLibrary`（modern）或 `_ZN7android23NativeBridgeLoadLibraryEPKci`（legacy）**加** `...GetTrampoline`；缺一抛 **"NativeBridge API is not available on this system"** | `agent.vala:1534-1552` |
| F4 | **modern 分支不带 namespace 参数**：`load_library(path, RTLD_LAZY)`；上游自带 FIXME 承认「拿不到 `classloader-namespace` 指针」 | `agent.vala:1361-1370` |
| F5 | **legacy 分支的 namespace 是写死的字面量 `3`**：`load_library_ext(path, RTLD_LAZY, (void*)3)` | `agent.vala:1366-1367` |
| F6 | x86_64 host 上 emulated agent 名为 `frida-agent-arm64.so`；资源缺失会抛**另外的**错误 **"Unable to handle emulated processes due to build configuration"** | `linux-host-session.vala:384-399` |
| F7 | **emulated agent 无法卸载**：modern 与 legacy **两个**分支都把 `unload` 置为 `null`，`:1467-1468` 的卸载调用是死代码 | `agent.vala:1538-1539`、`1546-1547`、`1467-1468` |

**F2/F3/F6 是强判据**：你们的报错是 F1 那条，而不是 F2/F3/F6 那三条。
所以可以确定：
- `libnativebridge.so` **在**进程里，`libart.so` **在**进程里；
- `NativeBridgeLoadLibrary`（或 legacy 同名符号）与 `GetTrampoline` **都解析成功**；
- `frida-server` 里**确实内嵌**了 `frida-agent-arm64.so` 资源；
- 失败点被夹在**唯一一处**：`nb_api.load_library*(...)` 返回了 NULL。

### 1.2 候选原因与置信度

**H1｜modern bridge 下没有 namespace 控制（置信度：高）**
`libnativebridge.so` 暴露 modern C API 时，Frida 走 F4 分支：**不带 namespace** 直接按路径加载。
Android 11+ 的 bridge 实现（Google `libndk_translation`，以及模仿它的厂商 bridge）
`NativeBridgeLoadLibrary()` 会在**调用方自己的 linker namespace / 应用 native 库搜索路径**里解析，
而不是任意绝对路径。frida-server 释放出来的 agent 文件（通常在 `/data/local/tmp/...`）
**不在该搜索路径内** → 返回 NULL → F1 文案。
上游 FIXME 本身就是这个坑的自认。

**H2｜Android ≥ 11 就是分水岭（置信度：中高）**
两条**独立**的上游记录，Frida 同为 16.7.x，症状与你们**完全一致**：

- [frida#3421](https://github.com/frida/frida/issues/3421)：Android 11 Genymotion 上 `process is not using emulation`；
  维护者式回复——「**Frida 似乎无法在 Android 11 或更高版本上检测到进程正在被模拟**」；
  提问者改用 **Android 9** 后 `--realm=emulated` 立即可用。
- [frida#3497](https://github.com/frida/frida/issues/3497)（**至今 open**）：**MuMuPlayer 12 + frida 16.7.19 +
  x86_64 frida-server**，ARM64 APK、`libil2cpp.so` 已映射但 `enumerateModules()` 看不到，
  `--realm=emulated` 报**同一句** `process is not using emulation`。提出者最后给出的 TL;DR 是
  **架构性不匹配**：x86_64 agent 的 `Interceptor` 无法 patch ARM64 代码；换成
  **BlueStacks 5 Pie64（Android 9，GUI 里勾选 ARM 32/64 ABI）+ `--realm=emulated`** 才成功。

> 你们自己写了「Android 具体版本尚未在本轮采集，**不能假定**」——这正是当前最该花的那 1 秒。
> H2 可被一条 `getprop` 直接判定。

**H3｜被你们改过的辅助二进制（置信度：中，必须先排除）**
「把唯一的 `/sys/fs/selinux/policy` 常量改到不可能存在的子路径、让上游 `g_file_test` 失败并提前返回」
——如果被跳过的这段**不只是策略检查**，而是同时参与了 agent 资源的释放或 bridge 预置，
就会直接落到 F1。**这项可以在 0 秒设备时间、纯离线排除**（见 §三.2）。

**H4｜legacy 分支写死的 namespace `3`（置信度：低–中）**
若 MuMu 的 bridge 只导出 legacy mangled 符号，Frida 走 F5：`(void*)3` 是按某一代 Android 的
namespace 表顺序假设的常量。厂商 bridge 的表顺序不同 → 在最坏情况下加载到错误/空 namespace → NULL。

**H5｜「进程没有用模拟」（置信度：低，已排除）**
被你们自己的 maps 证据证伪（AArch64 `libil2cpp.so` + `libhoudini.so` 同时映射）。

### 1.3 关于那次 `access violation accessing 0x310`

`0x310 = 784`，不是地址，是**结构体字段偏移**。这个异常的形状是 `NULL + 0x310` 解引用——
即 getter 内部取到的基址是 null（native realm 看不到该模块，`findBaseAddress`/`findExportByName`
返回 null）后继续按偏移读字段。
**它不是 bridge 的错误字符串，也不能推断 ABI 或 namespace。** 你们从提交里移除这个主动 getter 是对的。

### 1.4 所需的最少只读证据（合计 ≈ 1–2 秒设备时间，0 票、0 点击、不 attach）

```bash
S=<原授权ADB连接标识>
adb -s $S shell getprop ro.build.version.sdk
adb -s $S shell getprop ro.build.version.release
adb -s $S shell getprop ro.dalvik.vm.native.bridge
adb -s $S shell getprop ro.product.cpu.abilist
adb -s $S shell "cat /proc/$PID/maps | grep -E 'libnativebridge|libart\.so|libhoudini|libnb\.so|libndk_translation'"
adb -s $S shell "ls -ld /data/local/tmp && ls -l /data/local/tmp | grep -i frida"
```

判读表：

| 观测 | 结论 |
| --- | --- |
| `ro.build.version.sdk >= 30` | **H2 成立**，这就是已知未修的兼容性问题，不再在本实例上重试 |
| maps 里 **有** `libnativebridge.so` 和 `libart.so` | 与 F2/F3 自洽 → 失败点确定为 §1.1 那一处 load，而非模块发现 |
| maps 里**只有** `libhoudini.so`/`libnb.so`，没有 `libnativebridge.so` | 与 F2 冲突 → 说明报错不是这条路径，需重新定位（很低概率） |
| `/data/local/tmp` 下 frida 相关文件为 `root` 且非 `o+rx` | **H1 成立**：应用进程根本无法解析该路径 |

---

## 二、问题二：现有权限下有没有已验证的被动接入方式

### 2.1 直接回答：没有

- **emulated realm 本身不可撤销**（F7）。Frida 16.7.19 在两个 flavor 下都**不实现 unload**，
  `nb_api.unload_library()` 调用点是死代码。也就是说：**「加载观察组件后干净卸载」这件事，
  在本版本 + 任何 bridge 上都做不到**；唯一回退手段是杀掉应用进程。
  这一条本身可能就改变你们的治理结论——请把 F7 记进 PR #17。
- **namespace 无法从外部纠正**：modern 分支没有该参数（F4），legacy 分支写死 `(void*)3`（F5）。
  16.7.19 没有提供任何 API 让你传入正确的 namespace。

### 2.2 唯一「在授权内技术上成立」的替代：native realm 内存轮询

第三方实测记录（[frida#3497 评论, GabHST](https://github.com/frida/frida/issues/3497)）：
ARM64 模块在 native realm 下 `enumerateModules()` 看不到、`Interceptor.attach()` 会失败，
**但在已映射地址上手工读内存是可以的**（能读到字节）。

由此存在一条**不 hook、不调业务方法、不加权限、不重打包**的纯**读**路径：

- 从 native realm 用 `Memory.read*` 按偏移轮询 IL2CPP 对象字段；
- 字段偏移从你们已有的 `global-metadata.dat`(v31) **离线**解析得到；
- 实例地址通过 `libil2cpp.so` 的静态字段数组定位（BSS 可读）。

**能给你们表二的哪些行**：`BuyCardPanel._cardIndex/CardAmounts/TicketCost`、
`BetAddView._betCost`、`BuyCardContext.CardCount/BetCost` 等**采样值**。

**给不了**：表二最后一行「自然成功受理」（`DaubCell`/`SetDaubed` 一类**事件**）——
轮询拿不到事件语义；「哪个自然回调是计算完成点」也将**无法回答**。
所以它**不能替代你们表二的验收要求**，只能作为字段取值来源。

**成本判断**：这是一套新的 IL2CPP 内存读取子系统（离线数小时量级），且仍需**新的设备验证额度**。
你们已明确「不建议重做采集平台」——所以我**把它标出来供决策，不作为建议方案**。

### 2.3 一条 0 设备成本的旁路（可以先查）

复核 APK 的 DEX：购买/报价链路里是否有任何一段走 **Java 侧**（`app_process64` 是 x86_64，
native realm **可 hook**，例如 Google Play Billing 相关类）。
若命中，就是一条现成可用的 native-realm 观察面。纯离线，不花额度。
（对「局内票券价」命中概率低，但值得先看一眼。）

---

## 三、问题三：哪些必须超出现有授权

以下均为**已验证可行但不在本次授权内**的选项，逐条标注。**不要默认执行。**

1. **换模拟器实例（唯一有第三方独立复现的方向）**
   BlueStacks 5 **Pie64（Android 9）**，GUI 内勾选 ARM 32-bit / ARM 64-bit ABI，
   x86_64 frida-server，`-n <包名> --realm=emulated`。
   已由 [frida#3497](https://github.com/frida/frida/issues/3497) 多人在不同机器上复现成功。
   → 违反「原实例」，**超出授权**。
2. **重打包 APK 注入 `frida-gadget-arm64`**（apktool 反编译 + `lib/arm64-v8a/` 放 gadget +
   smali 里提前 `System.loadLibrary` + 重签 + 重装）。
   已由 [frida#3497 评论](https://github.com/frida/frida/issues/3497) /
   [frida#2247 评论](https://github.com/frida/frida/issues/2247) 确认可行。
   → 改 APK，**超出授权**。
3. **在 x86_64 实例上跑 `frida-server-arm64`**：能在 Houdini 下启动，但
   **枚举模块/进程会崩**。不可用，且是往设备上放新产物。**不建议**。
4. **升级到 Frida 17**：**不构成修复**——上游主线仍是 F4/F5 两条分支，未改；
   且会打断现有工具链。**不建议**，也不要据此改依赖。
5. 任何「先强行点购买试试」：**不提供，也不适用**——上述失败与购买链路无关。

**结论**：原实例（MuMu 12 / Android 12）× Frida 16.7.19 下，emulated realm 属
**已知且仍开放的上游不兼容**。**在现有授权内没有可交付的接入方式。**

---

## 四、请按你们的口径收口

### 4.1 原因 / 置信度

- 直接原因：bridge 的 `load_library*()` 返回 NULL（F1 兜底文案），**高**。
- 上游成因：Android ≥ 11 的 modern bridge 无 namespace 控制（H1）+ 版本分水岭（H2），**中高**。
- 你们自己的二进制改写是否参与：**未排除，必须先排除**（H3，纯离线）。

### 4.2 最小代码改动

**你们仓库内没有需要改的代码。** 本问题在 frida-core 与运行环境，不在 PR #16。
建议在 PR #17 里只落两条**记录性**修订：
- 把 F1（错误文案是兜底、**不等于**无翻译）与 F7（**emulated agent 不可卸载**）写进治理说明；
- 把「emulated realm 在 Android ≥ 11 未修」作为**已定位的环境阻塞**登记，附本文件与上游链接。

### 4.3 不消费票券的验证

#### 已完成（DSH 本轮实测，0 秒设备时间、0 票、0 点击）

脚本：`_dsh_bindiff.py`（`execution16\hook\`，Python 标准库，只读 5 个本地文件）。

**第 1 项 —— 排除 H3（辅助二进制改写）。结论：差异只有一个常量，H3 不成立。**

| 文件 | 字节数 | sha256（前 32） |
| --- | --- | --- |
| `frida-server-16.7.19-android-x86_64`（官方） | 114,292,664 | `d27e9eba721e623e6b39186f98cf9f03` |
| `observer-helper-prepared` | 114,292,664 | `6f22d35925abb7869c0f1996ac5bc2be` |
| `attempt-1..4\observer-helper`（4 份） | 114,292,664 | **均与 prepared 完全一致** `6f22d359…` |

与官方比对：**总共 19 个字节不同**，全部落在**同一段连续 22 字节**里，位于文件偏移
`0xaff81..0xaff96`：

```
官方 : /sys/fs/selinux/policy
改写 : /dev/null/xxxxxxxxxxxxxxx      ← 等长原地替换，/ 分隔符保持不动
```

- **没有任何代码字节被改动**，长度不变，无新增/移动段 → **不可能**影响 agent 资源的释放路径，
  也**不可能**影响 NativeBridge 的解析与调用。H3 **排除**。
- 四次尝试用的是**同一份二进制**（sha256 全同），所以「四次探索未冻结各版本」这一点，
  在**辅助二进制**这一维度上其实是有确定值的——可写进 PR #16。

**第 2 项 —— 排除 F6「build configuration」分支。结论：ARM64 agent 资源在。**

官方 `frida-server` 内 `frida-agent-arm64.so` 命中 **1** 次（`frida-agent-arm.so` 也命中 1 次，
`frida-agent` 共命中 13 次）。说明构建**内嵌了** ARM64 agent → 与你们的报错文案自洽，
排除了 `linux-host-session.vala:398-399` 那条分支。

**第 3 项 —— 顺带**：官方 server 里 `libnativebridge.so` 命中 2 次
（与 `agent.vala:1516` 的正则匹配逻辑一致），可作为 H1/H2 的旁证。

#### 仍建议做

4. **设备（≈1–2 秒、0 票、0 点击、不 attach）**：§1.4 那 6 条 `getprop` / `maps` / `ls`。
   这是当前 12.005 秒余量里**唯一值得花**的设备时间。
5. **离线（0 秒、0 票）**：离线解析 `global-metadata.dat` v31，落表二字段偏移
   ——无论后续走哪条路都要用，不占额度。

**不要再对本实例重试 `realm=emulated`**：已 3/3 失败，失败原因已在源码层定位到唯一一行，
且第 1、2 项离线核对已经把「自家二进制」和「构建缺资源」两个可自控变量排除干净——
剩下的是上游与环境。

### 4.4 成功与停止判据

- **成功（本步）**：能写出「SDK 版本 + `libnativebridge.so`/`libart.so` 是否在 maps +
  辅助二进制差异是否只有一个常量」三个确定值。
- **停止**：若 `sdk >= 30` 且 maps 含 `libnativebridge.so`，则判定 H1+H2 成立，
  **停止在本实例上的一切 emulated 尝试**，把「是否更换实例 / 是否重打包」作为**范围问题**上报 User。
- 明确**不**把 `Unknown` 当成功；本步不产生任何面板字段，也不改变新十局 0/10 的事实。

### 4.5 是否需要超出现有授权

- 执行 §4.3 的 1–4 项：**不需要**（纯离线 + 1–2 秒只读）。
- **拿到任何真实面板字段：需要。** 依据见 §三：唯一有第三方复现的路径是换实例或重打包，
  两者都在授权外；授权内的内存轮询路线无法给出表二最后一行要求的事件级证据。

### 4.6 时间估计与依据

- 最少只读取证：**≈2 秒设备时间**，0 票，可落在 12.005 秒余量内。
- 离线比对 + 元数据解析：**0 设备时间**。
- 任何「真正接入观察组件」：**无法在 12.005 秒内完成**。依据是 §三——它要么需要换环境/重打包
  （授权外，且需要全新验收额度），要么需要新建内存轮询子系统（离线数小时 + 新的设备验证额度）。
- **不自动增加额度**，以上仅为估计。

---

## 代码与证据入口

- 本文件：`%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\execution16\hook\DSH-ANSWER-20261014.md`
- 问题稿：`...\execution16\hook\DSH-QUESTIONS-20261014.md`
- 受控证据入口：`...\execution16\hook\REVIEW_HOOK.md`
- 上游源码（可直接复核行号）：`frida-core` tag **16.7.19**
  - `lib/agent/agent.vala:1361-1372`、`:1498-1575`
  - `src/linux/linux-host-session.vala:384-399`
- 上游 issue：[#3497（open，同版本同症状）](https://github.com/frida/frida/issues/3497)、
  [#3421](https://github.com/frida/frida/issues/3421)、[#2247](https://github.com/frida/frida/issues/2247)

Subagents: none.
