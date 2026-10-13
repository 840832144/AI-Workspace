"""POST 探测 logan 埋点服务 + 深挖 API 路径。"""
import json, re, sys, urllib.error, urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = ("Mozilla/5.0 (Linux; Android 9; SM-G998B) AppleWebKit/537.36 "
      "Chrome/120.0.0.0 Mobile Safari/537.36")


def call(url, method="POST", data=None, timeout=15):
    hdrs = {"User-Agent": UA, "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json"}
    body = json.dumps(data if data is not None else {}).encode()
    req = urllib.request.Request(url, headers=hdrs, method=method, data=body)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read().decode("utf-8", "replace")
        except Exception:
            return e.code, ""
    except Exception as e:
        return 0, str(e)[:130]


print("=== POST logan.voyage.bingo ===")
for p in ["/", "/v1/event", "/v1/events", "/event", "/log", "/api/v1/event",
          "/v1/report", "/v1/track", "/v2/event"]:
    c, b = call("https://logan.voyage.bingo" + p)
    print("  %-18s http=%-4s %s" % (p, c, b[:170].replace("\n", " ")))

print("\n=== POST staging.hay.elitescastle.com ===")
for p in ["/v1/event", "/v1/auth", "/v2/auth", "/v1/config", "/v1/ping"]:
    c, b = call("https://staging.hay.elitescastle.com" + p)
    print("  %-18s http=%-4s %s" % (p, c, b[:170].replace("\n", " ")))

# ── 深挖路径：扫元数据 + libil2cpp ────────────────────────
print("\n=== 元数据里的短路径串（按形态过滤）===")
raw = open(r"D:\BingoVoyageProbe\bin\global-metadata.dat", "rb").read()
txt = raw.decode("latin-1")
PATH = re.compile(r"/(?:v[0-9]|api|bingo|game|player|user|login|auth|config|event|logan|"
                  r"entry|reward|room|card|ball|club|team|task|mail|gift|shop|store|pay|"
                  r"rank|season|pass|activity)[A-Za-z0-9_/\-]{0,60}")
cand = {}
for m in PATH.finditer(txt):
    p = m.group(0)
    if 5 < len(p) < 70:
        cand[p] = cand.get(p, 0) + 1
for p in sorted(cand, key=lambda x: -cand[x])[:70]:
    print("   %-52s ×%d" % (p, cand[p]))

# ── 反查 hosts ────────────────────────────────────────────
print("\n=== 所有 *.elitescastle.com / *.voyage.bingo 片段 ===")
HOST = re.compile(r"([a-z0-9][a-z0-9\-]{1,30}(?:\.[a-z0-9\-]{1,30})*\.(?:elitescastle\.com|voyage\.bingo))")
hosts = {}
for m in HOST.finditer(txt):
    hosts[m.group(1)] = hosts.get(m.group(1), 0) + 1
for h in sorted(hosts, key=lambda x: -hosts[x]):
    print("   %-52s ×%d" % (h, hosts[h]))
