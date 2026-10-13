"""在元数据字符串里精确定位游戏自己的 API 域名与路径。"""
import os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe"
strs = open(os.path.join(OUT, "out", "meta_strings_all.txt"), encoding="utf-8").read().splitlines()
print("字符串池: %d" % len(strs))

KNOWN_CDN = ("spine-unity", "microsoft.com", "w3.org", "xmlsoap", "unity3d.com", "unity.com",
             "stackoverflow", "github.com", "nuget.org", "newtonking", "opencoding",
             "esotericsoftware", "facebook.com", "google.com", "gstatic", "amazonaws",
             "sentry.io", "uniwebview", "discord", "twitter", "bitbucket", "pages.dev",
             "windows.net", "chinacloudapi", "usgovcloud", "googleapis")


def is_noise(s):
    return any(k in s for k in KNOWN_CDN)


print("\n=== 含 https:// 且非库噪声的 ===")
seen = set()
for s in strs:
    if "https://" in s or "http://" in s:
        for part in re.split(r"\s+", s):
            if part.startswith(("http://", "https://")) and not is_noise(part):
                if part not in seen and len(part) < 160:
                    seen.add(part)
                    print("   " + part)

print("\n=== 疑似游戏自有域名（cluster 里的域名去噪后）===")
doms = Counter()
for s in strs:
    for m in re.finditer(r"\b([a-z0-9][a-z0-9\-]{2,40}(?:\.[a-z0-9\-]{2,40})+)\b", s):
        d = m.group(1)
        if is_noise(d) or d.endswith((".dll", ".cs", ".json", ".xml", ".png", ".asset")):
            continue
        if d.count(".") > 3:
            continue
        doms[d] += 1
for d, c in doms.most_common(50):
    print("   %-52s ×%d" % (d, c))

print("\n=== elitescastle 上下文 ===")
for s in strs:
    if "elitescastle" in s.lower():
        print("   " + s[:170])

print("\n=== 形如 API 跳的字符串 ===")
KEYS = ("api", "Api", "API", "endpoint", "Endpoint", "baseUrl", "BaseUrl", "serverUrl",
        "host", "Host", "domain", "Domain", "url", "Url", "URL")
hits = [s for s in strs if 6 <= len(s) <= 90 and any(k in s for k in KEYS)
        and re.match(r"^[A-Za-z0-9_./:\-]+$", s)]
for s in sorted(set(hits))[:60]:
    print("   " + s)
