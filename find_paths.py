"""定位 API 路径上下文 + Logan 报文格式线索。"""
import os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = r"D:\BingoVoyageProbe"
raw = open(os.path.join(OUT, "bin", "global-metadata.dat"), "rb").read()
txt = raw.decode("latin-1")

print("=== /api/system 的出现上下文 ===")
for m in list(re.finditer(r"/api/system", txt))[:6]:
    a, b = max(0, m.start() - 120), min(len(txt), m.end() + 120)
    seg = re.sub(r"[^\x20-\x7e]", " ", txt[a:b])
    print("   ...%s..." % seg)

print("\n=== Logan 相关标识符 ===")
ids = open(os.path.join(OUT, "out", "meta_idents.txt"), encoding="utf-8").read().splitlines()
for s in [x for x in ids if "logan" in x.lower()][:40]:
    print("   " + s)

print("\n=== 网络/请求相关标识符（找 API 客户端）===")
KEY = re.compile(r"(HttpClient|ApiClient|RestClient|WebRequest|NetworkManager|RequestBuilder|"
                 r"ApiService|Endpoint|BaseUri|ApiBase|ServerConfig|EnvConfig|LoginFlow|"
                 r"AuthService|TokenService|SessionManager)", re.I)
for s in [x for x in ids if KEY.search(x)][:50]:
    print("   " + s)

print("\n=== 环境/域名配置相关 ===")
KEY2 = re.compile(r"(Environment|EnvType|Region|ServerList|HostList|DomainList|UrlBuilder|"
                  r"ConfigUrl|RemoteConfig|GameConfig|BalanceConfig)", re.I)
for s in [x for x in ids if KEY2.search(x)][:50]:
    print("   " + s)

print("\n=== protobuf 相关（logan 报文可能是 pb）===")
KEY3 = re.compile(r"(protobuf|ProtoBuf|Protobuf|\.pb\b|MessagePack|FlatBuffer|CodedOutput|"
                  r"CodedInput|WireFormat|ByteBuf)", re.I)
for s in [x for x in ids if KEY3.search(x)][:30]:
    print("   " + s)
