"""扫描 Unity 数据包，找出配置表（含真实数值的 JSON/ScriptableObject/文本资源）。"""
import os, re, sys, zipfile
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe"
APK = os.path.join(OUT, "apk", "split_UnityDataAssetPack.apk")

z = zipfile.ZipFile(APK)
infos = z.infolist()
print("Unity 数据包: %d 个条目" % len(infos))

ext = Counter()
big = []
for i in infos:
    e = os.path.splitext(i.filename)[1].lower()
    ext[e] += 1
    if i.file_size > 200_000:
        big.append(i)

print("\n=== 扩展名分布 ===")
for e, c in ext.most_common(20):
    print("  %-14s %d" % (e or "(no ext)", c))

print("\n=== 最大的 25 个条目 ===")
for i in sorted(big, key=lambda x: -x.file_size)[:25]:
    print("  %12s  %s" % ("{:,}".format(i.file_size), i.filename))

# ── 找配置/文本资源 ───────────────────────────────────────
CFG = re.compile(r"(config|Config|table|Table|data|Data|json|Json|setting|Setting|param|Param|"
                 r"balance|Balance|level|Level|reward|Reward|bingo|Bingo|card|Card)", re.I)
cands = [i for i in infos if CFG.search(i.filename) and i.file_size > 1000]
print("\n=== 疑似配置资源（%d，取前 30）===" % len(cands))
for i in sorted(cands, key=lambda x: -x.file_size)[:30]:
    print("  %12s  %s" % ("{:,}".format(i.file_size), i.filename))

# ── StreamingAssets / Resources 路径 ──────────────────────
for probe in ("assets/aa/", "assets/StreamingAssets/", "assets/Resources/"):
    hit = [i for i in infos if i.filename.startswith(probe)]
    if hit:
        print("\n★ %s : %d 个" % (probe, len(hit)))
        for i in sorted(hit, key=lambda x: -x.file_size)[:12]:
            print("     %12s  %s" % ("{:,}".format(i.file_size), i.filename))

os.makedirs(os.path.join(OUT, "out"), exist_ok=True)
with open(os.path.join(OUT, "out", "unity_pack_list.txt"), "w", encoding="utf-8") as fh:
    for i in infos:
        fh.write("%12d  %s\n" % (i.file_size, i.filename))
print("\n完整清单: out/unity_pack_list.txt")
