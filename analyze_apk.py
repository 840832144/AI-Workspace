"""分析 Bingo Voyage 的 APK 结构，确定引擎与注入路线。"""
import json, os, re, sys, zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
APKDIR = r"D:\BingoVoyageProbe\apk"

for name in ("base.apk", "split_config.arm64_v8a.apk"):
    p = os.path.join(APKDIR, name)
    if not os.path.exists(p):
        print("MISSING", p)
        continue
    print("=" * 76)
    print(name, "(%.1f MB)" % (os.path.getsize(p) / 1e6))
    print("=" * 76)
    z = zipfile.ZipFile(p)
    names = z.namelist()

    libs = [n for n in names if n.startswith("lib/")]
    so = sorted({n.split("/")[-1] for n in libs})
    print("  lib/ 目录: %s" % sorted({n.split("/")[1] for n in libs if len(n.split("/")) > 2}))
    print("  .so 文件 (%d):" % len(so))
    for s in so:
        info = None
        for n in libs:
            if n.endswith("/" + s):
                info = z.getinfo(n)
                break
        print("     %-42s %10s" % (s, "{:,}".format(info.file_size) if info else "?"))

    # 引擎特征
    feats = []
    for key, label in [
        ("libil2cpp.so", "Unity IL2CPP"),
        ("libunity.so", "Unity"),
        ("libmonobdwgc-2.0.so", "Unity Mono"),
        ("libmain.so", "Unity main"),
        ("libcocos", "Cocos"),
        ("libflambe", "Flambe"),
        ("liblua", "Lua (native)"),
        ("libhermes", "Hermes/RN"),
        ("libreactnative", "React Native"),
        ("libflutter", "Flutter"),
        ("libv8", "V8"),
        ("libapp.so", "Flutter AOT"),
    ]:
        if any(key in s.lower() for s in so):
            feats.append(label)
    print("  引擎特征: %s" % (", ".join(feats) if feats else "无匹配"))

    # asset 层
    assets = [n for n in names if n.startswith("assets/")]
    exts = {}
    for a in assets:
        e = os.path.splitext(a)[1].lower()
        exts[e] = exts.get(e, 0) + 1
    top = sorted(exts.items(), key=lambda kv: -kv[1])[:14]
    print("  assets/ (%d):" % len(assets))
    for e, c in top:
        print("     %-10s %d" % (e or "(no ext)", c))

    # 关键路径
    for probe in ("assets/bin/Data/", "assets/lua", "assets/scripts", "assets/config",
                  "assets/AssetBundles", "assets/aa/", "assets/StreamingAssets"):
        hit = [n for n in names if n.startswith(probe)]
        if hit:
            print("  ★ %-26s %d 个文件   例: %s" % (probe, len(hit), hit[0]))

    # 包名 / 版本
    if "AndroidManifest.xml" in names:
        raw = z.read("AndroidManifest.xml")[:200000]
        txt = raw.decode("utf-16-le", "ignore")
        pk = re.findall(r"[\w.]{8,60}", txt)
        cands = [x for x in pk if x.count(".") >= 2 and not x.startswith("android")]
        print("  manifest 里的包/类名样本: %s" % ", ".join(dict.fromkeys(cands))[:200])
    print()
