"""正确解析 IL2CPP 元数据的「字符串字面量」段 —— 拿到运行时用到的真实字符串。

Il2CppStringLiteral = { uint32 length; int32 dataIndex }  (8 字节)
字面量数据在 stringLiteralDataOffset 指向的 blob 里。
"""
import os, struct, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe"
raw = open(os.path.join(OUT, "bin", "global-metadata.dat"), "rb").read()

magic, ver = struct.unpack_from("<II", raw, 0)
print("magic=0x%08X version=%d" % (magic, ver))

# 头字段顺序（IL2CPP v24-v31 一致）
NAMES = ["sanity", "version",
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
         "assembliesOffset", "assembliesCount"]
hdr = {}
for i, n in enumerate(NAMES):
    if 8 + i * 4 + 4 <= len(raw):
        hdr[n] = struct.unpack_from("<I", raw, 8 + i * 4)[0]

for k in ("stringLiteralOffset", "stringLiteralCount", "stringLiteralDataOffset",
          "stringLiteralDataCount", "stringOffset", "stringCount",
          "typeDefinitionsOffset", "typeDefinitionsCount"):
    print("  %-26s %s" % (k, hdr.get(k)))

sloff, slcnt = hdr["stringLiteralOffset"], hdr["stringLiteralCount"]
sdoff, sdcnt = hdr["stringLiteralDataOffset"], hdr["stringLiteralDataCount"]
print("\n字面量条目 %d 个，数据段 %d 字节" % (slcnt, sdcnt))

lits = []
for i in range(slcnt):
    o = sloff + i * 8
    if o + 8 > len(raw):
        break
    ln, di = struct.unpack_from("<Ii", raw, o)
    if ln <= 0 or ln > 4000:
        continue
    s = sdoff + di
    if s + ln > len(raw):
        continue
    try:
        lits.append(raw[s:s + ln].decode("utf-8"))
    except Exception:
        pass

print("解出字面量: %d" % len(lits))
uniq = sorted(set(lits))
print("去重后: %d" % len(uniq))

open(os.path.join(OUT, "out", "string_literals.txt"), "w", encoding="utf-8").write("\n".join(uniq))

print("\n=== 含 URL 的字面量 ===")
for s in uniq:
    if "http" in s.lower() and len(s) < 200:
        print("   " + s)

print("\n=== 含 .com/.bingo/.io 的字面量 ===")
for s in uniq:
    if any(k in s for k in (".com", ".bingo", ".io", ".net", ".cn")) and len(s) < 160:
        print("   " + s)

print("\n=== 形如 API 路径的字面量 ===")
for s in uniq:
    if s.startswith("/") and 2 < len(s) < 80 and " " not in s:
        print("   " + s)
