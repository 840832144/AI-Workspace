"""从元数据与原生库里挖出游戏的服务端 API 地址与协议线索。"""
import os, re, sys, zipfile
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe"

# ── 1. 元数据里找 URL / 域名 ──────────────────────────────
meta = open(os.path.join(OUT, "bin", "global-metadata.dat"), "rb").read()
print("=== 元数据里的域名 / URL ===")
urls = set()
for m in re.finditer(rb"https?://[\x21-\x7e]{4,150}", meta):
    urls.add(m.group(0).decode("ascii"))
for u in sorted(urls)[:40]:
    print("   " + u)

print("\n=== 元数据里的裸域名 ===")
doms = Counter()
for m in re.finditer(rb"\b([a-z0-9][a-z0-9\-]{2,40}\.(?:com|net|io|cn|org|co|app|dev|xyz|cloud|gg))\b", meta):
    d = m.group(1).decode("ascii")
    if d.startswith(("android.", "google.", "schemas.", "www.")):
        continue
    doms[d] += 1
for d, c in doms.most_common(40):
    print("   %-48s ×%d" % (d, c))

# ── 2. 原生库字符串 ───────────────────────────────────────
so = os.path.join(OUT, "bin", "libil2cpp.so")
if not os.path.exists(so):
    z = zipfile.ZipFile(os.path.join(OUT, "apk", "split_config.arm64_v8a.apk"))
    for n in z.namelist():
        if n.endswith("libil2cpp.so"):
            print("\n提取 libil2cpp.so ...")
            open(so, "wb").write(z.read(n))
            break

if os.path.exists(so):
    data = open(so, "rb").read()
    print("\nlibil2cpp.so %.1f MB" % (len(data) / 1e6))
    print("\n=== .so 里的 URL ===")
    u2 = set()
    for m in re.finditer(rb"https?://[\x21-\x7e]{4,150}", data):
        u2.add(m.group(0).decode("ascii"))
    for u in sorted(u2)[:50]:
        print("   " + u)

    print("\n=== .so 里的 API 路径片段 ===")
    pats = set()
    for m in re.finditer(rb"/(?:api|v\d|graphql|rest|service|services|user|game|bingo|player|"
                         rb"login|auth|config|reward|room|card|ball)[A-Za-z0-9/_\-]{2,70}", data):
        pats.add(m.group(0).decode("ascii"))
    for p in sorted(pats)[:60]:
        print("   " + p)

# ── 3. 资产清单里的线索 ───────────────────────────────────
mf = os.path.join(OUT, "apk", "split_UnityDataAssetPack.apk")
if os.path.exists(mf):
    z = zipfile.ZipFile(mf)
    names = z.namelist()
    hit = [n for n in names if "BundleManifest" in n]
    if hit:
        raw = z.read(hit[0])
        print("\n=== BundleManifest.json (%d bytes) 头部 ===" % len(raw))
        print(raw[:600].decode("utf-8", "replace"))
