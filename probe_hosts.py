"""从主机直接探测 Bingo Voyage 的服务端。"""
import json, socket, ssl, sys, urllib.error, urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = ("Mozilla/5.0 (Linux; Android 9; SM-G998B) AppleWebKit/537.36 "
      "Chrome/120.0.0.0 Mobile Safari/537.36")

HOSTS = [
    "entry.bingo.elitescastle.com",
    "logan.voyage.bingo",
    "staging.hay.elitescastle.com",
    "voyage.bingo",
    "www.voyage.bingo",
    "api.voyage.bingo",
    "bingo.elitescastle.com",
    "hay.elitescastle.com",
]

print("=== DNS 解析 ===")
for h in HOSTS:
    try:
        ip = socket.gethostbyname(h)
        print("  %-42s -> %s" % (h, ip))
    except Exception as e:
        print("  %-42s -> DNS 失败" % h)


def get(url, timeout=15):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9"})
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


PATHS = ["", "/", "/v1/event", "/v2/auth", "/v1/config", "/health", "/status",
         "/v1/game/config", "/api/system", "/v1/bingo/config"]

for h in HOSTS:
    print("\n" + "=" * 70)
    print(h)
    for p in PATHS:
        c, b = get("https://" + h + p)
        s = b[:150].replace("\n", " ")
        print("  %-22s http=%-4s %s" % (p or "(root)", c, s))
        if c == 200 and len(b) > 200:
            fn = "D:/BingoVoyageProbe/out/host_%s%s.json" % (h.replace(".", "_"),
                                                             p.replace("/", "_"))
            try:
                open(fn, "w", encoding="utf-8").write(b)
                print("     -> 已保存 %s" % fn)
            except Exception:
                pass
