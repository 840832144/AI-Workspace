"""沿 elitescastle.com 深挖全部 URL 与 API 路径。"""
import os, re, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe"
RAW = open(os.path.join(OUT, "bin", "global-metadata.dat"), "rb").read()
print("metadata %.1f MB" % (len(RAW) / 1e6))

# 在原始字节里抓 URL（保留上下文，因为字符串是紧密拼接的）
txt = RAW.decode("latin-1")
URL = re.compile(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]{6,220}")

urls = URL.findall(txt)
print("抓到 URL 总数: %d" % len(urls))

byhost = defaultdict(set)
for u in urls:
    m = re.match(r"https?://([^/]+)", u)
    if not m:
        continue
    host = m.group(1)
    if any(k in host for k in ("microsoft", "w3.org", "xmlsoap", "unity3d", "unity.com",
                               "esotericsoftware", "schemas", "stackoverflow", "github",
                               "nuget", "newtonking", "opencoding", "amazonaws", "gstatic",
                               "googleapis", "windows.net", "chinacloudapi", "usgovcloud")):
        continue
    byhost[host].add(u)

print("\n=== 非库域名（按出现量）===")
for h in sorted(byhost, key=lambda x: -len(byhost[x])):
    print("  %-54s %d 条" % (h, len(byhost[h])))

print("\n=== elitescastle / bingo / joycastle 相关全部 URL ===")
key = [u for u in set(urls) if any(k in u for k in
       ("elitescastle", "joycastle", "bingo.", "entry.", "staging."))]
for u in sorted(key):
    print("   " + u[:200])

# ── API 路径片段 ──────────────────────────────────────────
print("\n=== 疑似 API 路径（/xxx/yyy 形态）===")
PATH = re.compile(r"/(?:api|v\d|rest|graphql|user|player|game|bingo|room|card|ball|"
                  r"login|auth|config|reward|shop|store|pay|order|rank|club|team|task|"
                  r"mail|friend|gift|event|activity|season|pass)[A-Za-z0-9_/\-]{1,80}")
paths = set(PATH.findall(txt))
paths = {p for p in paths if 5 < len(p) < 90 and "/" in p[1:]}
for p in sorted(paths)[:80]:
    print("   " + p)
print("  ... 共 %d 个" % len(paths))

os.makedirs(os.path.join(OUT, "out"), exist_ok=True)
with open(os.path.join(OUT, "out", "api_urls.txt"), "w", encoding="utf-8") as fh:
    for u in sorted(set(urls)):
        fh.write(u + "\n")
with open(os.path.join(OUT, "out", "api_paths.txt"), "w", encoding="utf-8") as fh:
    for p in sorted(paths):
        fh.write(p + "\n")
print("\n产出: out/api_urls.txt, out/api_paths.txt")
