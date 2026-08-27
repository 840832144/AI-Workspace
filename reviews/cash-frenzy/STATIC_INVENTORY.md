# TASK-0022 Static Inventory

## Package Identity

| Field | Confirmed value |
| --- | --- |
| Official Google Play title | Cash Frenzy™ - Casino Slots |
| Developer | SpinX Games Limited |
| Package | `slots.pcg.casino.games.free.android` |
| Installed sample | 4.78 / versionCode 478 |
| SDK | minSdk 24 / targetSdk 35 |
| Signing | APK Signature Scheme v3 |
| Primary ABI | arm64-v8a |
| Emulator ABI baseline | x86_64 with arm64 native bridge；独立实例待复核 |
| Engine | Cocos2d-x + LuaJIT |
| Android entry | `org.cocos2dx.lua.AppActivity` |

官方产品身份来源：[Google Play](https://play.google.com/store/apps/details?id=slots.pcg.casino.games.free.android)。公开商店页不证明客户端协议或本机安装版本。

## APK / Split Hashes

| File | SHA-256 |
| --- | --- |
| `base.apk` | `19D6C49E006D490A1B09FD283F71D0B3AFBC67B13082AE924C418DDD0F0C70B8` |
| `split_config.arm64_v8a.apk` | `19408A2F27130A8779828782A56F0771A4EAE7C2EFA2805BEED4187B46C175F0` |
| `split_config.hdpi.apk` | `09C1E442B76D28942D042F5EBB61AFC1C30C2A69DABC2A62946AD809A151A076` |
| `split_config.zh.apk` | `C7D42D727E7283F8EDFC1644EDE9E55871281568969A41782F55D270BEF4CA91` |

二进制仅留本机；Git 只保存文件名和 hash。

## Native Inventory

| Library | Role signal | SHA-256 |
| --- | --- | --- |
| `libcocos2dlua.so` | Cocos/LuaJIT、socket/TLS/WebSocket、protocol symbols | `3DD89EE17150C53B6B0760AF6E6C2F2AABC44133F85E1C9315C5E52AB9785E49` |
| `libEncryptorP.so` | encryption boundary candidate | `45FD9913DC05CF9BAF36AA83611FE59E4F0167A2EEEA79E23E7935FD797209DE` |
| `libsigner.so` | signing/SHA boundary candidate | `47A6F1900EBD86C2E3BA3A49020FF8FE3D79784BAB4C80C0ED4AA18FD0D2EE90` |
| `libflipped.so` | unknown small native helper | `31494063717F1E594B6A30795255164A0DAFB5ABDB1CBAFE4375988448C50B84` |
| `libapminsighta.so` / `libapminsightb.so` / `libvolc_log.so` | telemetry/crash candidates | hashes retained in local inventory |
| `libapplovin-native-crash-reporter.so` | advertising crash reporter | hash retained in local inventory |

## Resource Inventory

- 16,887 `.luac`、2,888 PNG、998 XML、528 atlas、516 JSON、491 plist、394 font、236 MP3、121 CSB。
- `assets/src` 与 `assets/src64` 各 6,730 files；`src64/Systems` 5,739 files、`Themes` 528、`TestUI` 123、`UI` 106。
- Lua header `1B 4C 4A 02` 确认是 LuaJIT bytecode，而非可直接读取的 Lua source。
- 7 个主 DEX，另有广告 SDK DEX；未执行完整反编译。
- 23 个 `.proto`/`.textproto` 均属于 Google/Firebase/SDK 范围；未确认游戏业务 descriptor。

## Tooling

- BlueStacks 5 China 5.22.170.6509。
- Bundled `HD-Aapt` 用于 manifest/badging；bundled 7-Zip 24.09 用于只读解包。
- 静态副本与解包目录位于 Host-local `CashFrenzyResearch/local-only`，不进入 Git。
