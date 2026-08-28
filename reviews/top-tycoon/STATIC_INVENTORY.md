# Top Tycoon Static Inventory

## 实装身份

| 项目 | Confirmed |
|---|---|
| BlueStacks internal instance | `Pie64_5` |
| Display name | `topTycoon` |
| Android / API | Android 9 / API 28 |
| ADB serial | `127.0.0.1:5605` |
| Package | `com.monopoly.dream.idle.king` |
| Version | `1.0.12` / versionCode `12` |
| Foreground activity | `com.google.firebase.MessagingUnityPlayerActivity` |
| ABI | primary `arm64-v8a`; BlueStacks guest also exposes x86_64/x86/armeabi-v7a |
| Native bridge | `libnb.so` |
| Engine | Unity `2021.3.57f2`, IL2CPP |

## APK / split hashes

| Artifact | SHA-256 |
|---|---|
| `base.apk` | `165EB27F273CFEE3602439ADF43F81C44C5BB02864BEFA2EC740F19302B09DEA` |
| `split_config.arm64_v8a.apk` | `139F1CC69D5ACBBD4121149FD20FBB4A324E3D8360F526F625D8A1828E12EAB2` |
| `split_UnityDataAssetPack.apk` | `964AE901FB45E06FCB30213C60305F3FB8AF2387F397690D7A029624DFDC5C67` |

APK、SO、完整 strings 与资源文件仅保存在本机受控目录，未进入 Git。

## 运行框架与关键组件

| Component | Evidence | SHA-256 / version |
|---|---|---|
| IL2CPP metadata | `global-metadata.dat` | `323550ADA36D5FADFBC34B80F7877415C81733C14CCBFB20277D8BA3C4305CC7` |
| IL2CPP runtime | `libil2cpp.so` | `96FAD1B8581C7270A6B7AA4C76CBBA09283DC7588121AD165E9821F5060FD98B` |
| Unity runtime | `libunity.so` | `9146BB7E0966EE0E3122BF52521A866C3A2D3A3FEABD2C7B4903C303730A6186` |
| xLua | `libxlua.so`, Lua 5.3.5 markers | `F802463C2375FC8BFA28119C6C800AC26703ADEDCF080EDAEDFF3E007F60FB99` |
| Frida runtime | host/server/Gadget `17.17.0` | version现场一致 |
| Hotfix assembly | extracted `Game.Hotfix.dll` TextAsset | `760DD61E7F8BDBBBAE26BC5E929A1950CBE9807B263313935796681A7D48AB66` |

`Game.Hotfix.dll` 通过本机固定 UnityPy `1.25.3` 从 YooAsset Logic bundle 只读提取；metadata inventory 使用 dnfile `0.18.0`。两者仅用于本地静态审计。

## 结构信号

- Managed：`Assembly-CSharp`、`Game`、`Global`、`IdleGameNew.Runtime`、`BaseSlotsGame.Runtime`、`Building.Runtime`、`Catan.Runtime`、`ILRuntime`、`ILRuntimeExt`、`ProtobufRuntime`、`Newtonsoft.Json`、`LitJson`、`YooAsset`。
- Native：`libil2cpp.so`、`libunity.so`、`libxlua.so`；xLua 包含 `luaopen_pb`、lua-protobuf、RapidJSON 与 LuaSocket 符号。
- Hotfix：`Game.Hotfix.dll` 包含 Google.Protobuf generated types、Spin/Slots logic、storage、activity、economy 与 UI 类型。
- YooAsset modules：Slots、BetBox、Attack、BankRobbery、BuildPass、Building、Catan、DailyTask、Shop、Steal、Team、TycoonMilestone、ThirdPayment 等。
- Storage / serialization：Google.Protobuf、JSON（Newtonsoft/LitJson/RapidJSON）与热更用户状态；未确认 MessagePack 或 FlatBuffers。
- Network：UnityWebRequest/TLS、LuaSocket 与 protobuf request/response generated types均存在；本轮 direct live 边界为 managed Google.Protobuf encode。

## 核心静态类

- `Game.Hotfix.Logic.SpinGameLogic`：`Spin`、`SetSpinRet`、`CallSpinRet`、`SpinCanSave`；字段含 `m_CurSpinRet`。
- `Game.Hotfix.Logic.SlotGameLogic`：`ConsumeEnergy`、`AddCoin`、`CheckDataSync`、`GetCurAsset`。
- `Game.Hotfix.Gameplay.SlotsMachineController`：`FillResult`、`SetResult`、`SetRandomDeck`、`StartRotate`、`SetAuto`。
- `Game.Hotfix.Gameplay.SlotsGameplay`：`ConsumeEnergy`、`CheckCoinEvent`、`CheckEnergyEvent`、`DoSettlementEvent`。
- `Game.Hotfix.Logic.SlotResultType`：Coin、Energy、Attack、Steal、Shield、JackPot、Bonus 等枚举线索。
- `Protos.House.CGUploadCoin`：Coin、Energy、Estate。
- `Protos.Xxxgame.CGSaveUserdata`：Key、Value、Version。

以上类名/成员为 Confirmed static；“客户端形成结果后上传状态”是结合 live boundary 的 Derived architecture judgment，不宣称服务端 RNG 或概率机制。
