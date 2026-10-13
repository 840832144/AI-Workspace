"""从 IL2CPP global-metadata.dat 提取全部类型/方法/字段名 —— 不需要游戏运行。

这是被崩溃阻塞时最有价值的切入点：IL2CPP 的元数据里含完整的数据模型，
bingo 玩法的核心数值结构（卡、球、叫号、图案、奖金）都会在里面。

    python dump_il2cpp.py
"""
import os, struct, sys, zipfile
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe"
META = os.path.join(OUT, "bin", "global-metadata.dat")
os.makedirs(os.path.dirname(META), exist_ok=True)

# ── 从 base.apk 里取出 metadata ────────────────────────────
if not os.path.exists(META):
    z = zipfile.ZipFile(os.path.join(OUT, "apk", "base.apk"))
    for n in z.namelist():
        if n.endswith("global-metadata.dat"):
            data = z.read(n)
            open(META, "wb").write(data)
            print("提取: %s -> %s (%.1f MB)" % (n, META, len(data) / 1e6))
            break

raw = open(META, "rb").read()
print("metadata: %.1f MB" % (len(raw) / 1e6))

# ── IL2CPP metadata 头（版本 24+ 通用布局）────────────────
magic, version = struct.unpack_from("<II", raw, 0)
print("magic=0x%08X  version=%d" % (magic, version))

# 头部字段（IL2CPP v24-v29 结构一致）
FIELDS = [
    "sanity", "version",
    "stringLiteralOffset", "stringLiteralCount",
    "stringLiteralDataOffset", "stringLiteralDataCount",
    "stringOffset", "stringCount",
    "eventsOffset", "eventsCount",
    "propertiesOffset", "propertiesCount",
    "methodsOffset", "methodsCount",
    "parameterDefaultValuesOffset", "parameterDefaultValuesCount",
    "fieldDefaultValuesOffset", "fieldDefaultValuesCount",
    "fieldAndParameterDefaultValueDataOffset", "fieldAndParameterDefaultValueDataCount",
    "fieldMarshaledSizesOffset", "fieldMarshaledSizesCount",
    "parametersOffset", "parametersCount",
    "fieldsOffset", "fieldsCount",
    "genericParametersOffset", "genericParametersCount",
    "genericParameterConstraintsOffset", "genericParameterConstraintsCount",
    "genericContainersOffset", "genericContainersCount",
    "nestedTypesOffset", "nestedTypesCount",
    "interfacesOffset", "interfacesCount",
    "vtableMethodsOffset", "vtableMethodsCount",
    "interfaceOffsetsOffset", "interfaceOffsetsCount",
    "typeDefinitionsOffset", "typeDefinitionsCount",
    "imagesOffset", "imagesCount",
    "assembliesOffset", "assembliesCount",
    "metadataUsageListsOffset", "metadataUsageListsCount",
    "metadataUsagePairsOffset", "metadataUsagePairsCount",
    "fieldRefsOffset", "fieldRefsCount",
    "referencedAssembliesOffset", "referencedAssembliesCount",
    "attributesInfoOffset", "attributesInfoCount",
    "attributeTypesOffset", "attributeTypesCount",
    "unresolvedVirtualCallParameterTypesOffset", "unresolvedVirtualCallParameterTypesCount",
    "unresolvedVirtualCallParameterRangesOffset", "unresolvedVirtualCallParameterRangesCount",
    "windowsRuntimeTypeNamesOffset", "windowsRuntimeTypeNamesSize",
    "windowsRuntimeStringsOffset", "windowsRuntimeStringsSize",
    "exportedTypeDefinitionsOffset", "exportedTypeDefinitionsCount",
]
hdr = {}
for i, name in enumerate(FIELDS):
    if 8 + i * 4 + 4 > len(raw):
        break
    hdr[name] = struct.unpack_from("<I", raw, 8 + i * 4)[0]

def hdrget(k):
    return hdr.get(k)

print("\n=== 关键段 ===")
for k in ("stringOffset", "stringCount", "typeDefinitionsOffset", "typeDefinitionsCount",
          "methodsOffset", "methodsCount", "fieldsOffset", "fieldsCount",
          "imagesOffset", "imagesCount", "assembliesOffset", "assembliesCount"):
    print("  %-26s %s" % (k, hdr.get(k)))

# ── 字符串表（null 分隔）──────────────────────────────────
soff, scnt = hdr.get("stringOffset"), hdr.get("stringCount")
strings = []
if soff and scnt and soff + scnt <= len(raw):
    blob = raw[soff:soff + scnt]
    for s in blob.split(b"\x00"):
        if 3 <= len(s) <= 200:
            try:
                strings.append(s.decode("utf-8"))
            except Exception:
                pass
print("\n字符串总数: %d" % len(strings))

# ── 类型定义表 ────────────────────────────────────────────
tdoff, tdcnt = hdr.get("typeDefinitionsOffset"), hdr.get("typeDefinitionsCount")
types = []
if tdoff and tdcnt:
    for i in range(tdcnt):
        o = tdoff + i * 88          # Il2CppTypeDefinition 88 bytes (v24+)
        if o + 88 > len(raw):
            break
        nameIdx = struct.unpack_from("<i", raw, o + 0)[0]
        nsIdx = struct.unpack_from("<i", raw, o + 4)[0]
        if 0 <= nameIdx < len(strings):
            types.append((strings[nsIdx] if 0 <= nsIdx < len(strings) else "",
                          strings[nameIdx]))
print("类型数: %d" % len(types))

# ── bingo 关键词命中 ──────────────────────────────────────
KEY = ["bingo", "card", "ball", "call", "daub", "mark", "pattern", "line",
       "prize", "jackpot", "pot", "room", "round", "ticket", "draw", "number",
       "win", "stake", "bet", "coin", "cash", "powerup", "boost", "theme",
       "collection", "album", "sticker", "voyage", "cruise", "ship"]
hits = defaultdict(list)
for ns, nm in types:
    low = nm.lower()
    for k in KEY:
        if k in low:
            hits[k].append(ns + "." + nm if ns else nm)

os.makedirs(os.path.join(OUT, "out"), exist_ok=True)
with open(os.path.join(OUT, "out", "il2cpp_types.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join("%s.%s" % (ns, nm) if ns else nm for ns, nm in sorted(types)))
with open(os.path.join(OUT, "out", "il2cpp_strings.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(strings))

print("\n=== 类型名关键词命中 ===")
for k in sorted(hits, key=lambda x: -len(hits[x])):
    print("  %-12s %4d   例: %s" % (k, len(hits[k]), ", ".join(hits[k][:4])[:110]))

print("\n产出:")
print("  " + os.path.join(OUT, "out", "il2cpp_types.txt"))
print("  " + os.path.join(OUT, "out", "il2cpp_strings.txt"))
