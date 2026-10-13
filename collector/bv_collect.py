"""Bingo Voyage 采集器 —— 一键起停抓包链路（自包含，不依赖 dev/ 目录）。

子命令：
    check    环境自检（adb / 设备 / root / 端口 / python 包 / 现有产物）
    start    建立抓包链路（CA + 代理 + iptables 重定向 + mitmdump + SNI 桥）
    stop     完全还原（撤销重定向 + 卸载 CA + 清代理 + 停两个后台进程）
    status   链路状态
    play     启动 game + 打开应用
    round    以固定时长跑协议驱动自动 daub（有上限，非常驻）

用法：
    python collector\\bv_collect.py check
    python collector\\bv_collect.py start
    python collector\\bv_collect.py stop
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))
ADB = CFG["device"]["adb"]
SER = CFG["device"]["serial"]
PKG = CFG["package"]
PP = CFG["capture"]["proxy_port"]
BP = CFG["capture"]["bridge_port"]
OUT = CFG["paths"]["out"]
TMP = "/data/local/tmp"

# ---------- 设备上执行的脚本（内嵌，避免 PowerShell 引号与换行坑） ----------

INSTALL_CA = """#!/system/bin/sh
# 在只读分区上用 tmpfs bind-mount 装入 mitmproxy 系统级 CA
# Android 14+ 起应用真正读的是 conscrypt apex 里的 cacerts，两个位置都要挂
set -e
MNT=/data/local/tmp/cacerts
CA=/data/local/tmp/bv_ca.0
umount /system/etc/security/cacerts 2>/dev/null || true
umount /apex/com.android.conscrypt/cacerts 2>/dev/null || true
for REAL in /system/etc/security/cacerts /apex/com.android.conscrypt/cacerts; do
  [ -d "$REAL" ] || continue
  rm -rf "$MNT"; mkdir -p "$MNT"
  cp "$REAL"/* "$MNT"/ 2>/dev/null || true
  cp "$CA" "$MNT/$(basename $CA)"
  chmod 644 "$MNT"/*.0
  chown 0:0 "$MNT"/*.0
  chcon u:object_r:system_security_cacerts_file:s0 "$MNT"/*.0 2>/dev/null || true
  mount --bind "$MNT" "$REAL" 2>/dev/null || { echo "BIND-FAIL $REAL"; continue; }
  echo "CA-OK $REAL $(ls $REAL | wc -l) certs"
done
"""

TEARDOWN_CA = """#!/system/bin/sh
umount /system/etc/security/cacerts 2>/dev/null && echo "CA unmounted(system)" || true
umount /apex/com.android.conscrypt/cacerts 2>/dev/null && echo "CA unmounted(apex)" || true
rm -rf /data/local/tmp/cacerts
"""

SETUP_REDIRECT = """#!/system/bin/sh
# 出站 443 全部重定向到本地桥端口（排除 127/8，避免碰系统代理自身）
set -e
PORT=__BP__
sh /data/local/tmp/bv_teardown_redirect.sh 2>/dev/null || true
iptables -t nat -A OUTPUT -p tcp --dport 443 ! -d 127.0.0.0/8 \\
  -j REDIRECT --to-ports $PORT
iptables -t nat -L OUTPUT -n -v --line-numbers
echo "REDIRECT-OK -> :$PORT"
"""

TEARDOWN_REDIRECT = """#!/system/bin/sh
PORT=__BP__
iptables -t nat -D OUTPUT -p tcp --dport 443 ! -d 127.0.0.0/8 \\
  -j REDIRECT --to-ports $PORT 2>/dev/null || true
iptables -t nat -L OUTPUT -n --line-numbers
echo "REDIRECT-OFF"
"""

BRIDGE = r'''"""SNI 感知的透明 TLS 桥：peek ClientHello 取 SNI，向 mitmproxy 发 CONNECT。"""
import socket, struct, sys, threading
PROXY_HOST, PROXY_PORT = "127.0.0.1", __PP__
DEFAULT_UP = "__UP__"

def parse_sni(buf):
    try:
        if len(buf) < 6 or buf[0] != 0x16 or buf[5] != 0x01:
            return None
        i = 9 + 2 + 32
        i += 1 + buf[i]
        i += 2 + struct.unpack_from(">H", buf, i)[0]
        i += 1 + buf[i]
        ext_total = struct.unpack_from(">H", buf, i)[0]; i += 2
        end = min(len(buf), i + ext_total)
        while i + 4 <= end:
            etype, elen = struct.unpack_from(">HH", buf, i); i += 4
            if etype == 0x0000:
                ntype = buf[i + 2]
                nlen = struct.unpack_from(">H", buf, i + 3)[0]
                if ntype == 0:
                    return buf[i + 5:i + 5 + nlen].decode("ascii", "replace")
            i += elen
    except Exception:
        return None
    return None

def pump(a, b):
    try:
        while True:
            d = a.recv(65536)
            if not d:
                break
            b.sendall(d)
    except Exception:
        pass
    finally:
        for s in (a, b):
            try: s.shutdown(socket.SHUT_RDWR)
            except Exception: pass

def handle(client, up_port, up_default, seq):
    up = None
    try:
        client.settimeout(20); head = b""
        while len(head) < 5:
            c = client.recv(1)
            if not c: raise IOError("closed")
            head += c
        if head[0] == 0x16:
            need = 5 + struct.unpack_from(">H", head, 3)[0]
            while len(head) < need:
                c = client.recv(need - len(head))
                if not c: break
                head += c
        sni = parse_sni(head)
        target = ("%s:443" % sni) if sni else up_default
        up = socket.create_connection((PROXY_HOST, up_port), timeout=15)
        up.sendall(("CONNECT %s HTTP/1.1\r\nHost: %s\r\n\r\n" % (target, target)).encode())
        up.settimeout(15); buf = b""
        while b"\r\n\r\n" not in buf:
            c = up.recv(4096)
            if not c: raise IOError("proxy closed")
            buf += c
        if "200" not in buf.split(b"\r\n", 1)[0].decode("latin-1"):
            print("[#%d] CONNECT failed %s" % (seq, target)); return
        rest = buf.split(b"\r\n\r\n", 1)[1]
        if rest: client.sendall(rest)
        if head: up.sendall(head)
        print("[#%d] tunnel %s" % (seq, target))
        client.settimeout(None)
        t = threading.Thread(target=pump, args=(client, up), daemon=True); t.start()
        pump(up, client); t.join(timeout=5)
    except Exception as e:
        print("[#%d] err %r" % (seq, e))
    finally:
        for s in (client, up):
            if s is not None:
                try: s.close()
                except Exception: pass

def main():
    port = int(sys.argv[1])
    srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port)); srv.listen(128)
    print("SNI bridge :%d -> mitmproxy:%d (default %s)" % (port, PROXY_PORT, DEFAULT_UP))
    seq = 0
    while True:
        try: c, a = srv.accept()
        except Exception: break
        seq += 1
        threading.Thread(target=handle, args=(c, PROXY_PORT, DEFAULT_UP, seq), daemon=True).start()

main()
'''

DUMP_ADDON = r'''"""mitmproxy addon：HTTP + WebSocket 全量落盘（Bingo Voyage 采集器）。"""
import base64, json, os, struct, time
OUT = r"__OUT__"
os.makedirs(OUT, exist_ok=True)
JSONL = os.path.join(OUT, "bv_flows.jsonl")
WS_JSONL = os.path.join(OUT, "bv_ws.jsonl")
BODIES = os.path.join(OUT, "bv_bodies")
os.makedirs(BODIES, exist_ok=True)
_seq = [0]

def _save(data, tag):
    if not data: return None
    _seq[0] += 1
    name = "%04d_%s.bin" % (_seq[0], tag)
    with open(os.path.join(BODIES, name), "wb") as f: f.write(data)
    return name

def _msg(m):
    raw = m.content
    try:
        t = raw.decode("utf-8")
        ok = all(c.isprintable() or c in "\r\n\t" for c in t[:2000])
    except Exception:
        t, ok = None, False
    return {"content_type": (m.headers.get("content-type") or ""), "len": len(raw),
            "text": t if ok else None,
            "b64": base64.b64encode(raw).decode() if raw else None}

def response(flow):
    try:
        req, resp = flow.request, flow.response
        if resp is None: return
        rec = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "method": req.method,
               "host": req.host, "port": req.port, "path": req.path,
               "url": req.pretty_url, "status": resp.status_code,
               "req_headers": dict(req.headers), "resp_headers": dict(resp.headers),
               "req": _msg(req), "resp": _msg(resp)}
        if req.content: rec["req_file"] = _save(req.content, "req")
        if resp.content: rec["resp_file"] = _save(resp.content, "resp")
        with open(JSONL, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print("[FLOW] %s %s%s -> %s" % (req.method, req.host, req.path, resp.status_code))
    except Exception as e:
        print("[ERR] %r" % (e,))

def websocket_message(flow):
    ws = getattr(flow, "websocket", None)
    if ws is None or not ws.messages: return
    m = ws.messages[-1]
    rec = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "dir": "C->S" if m.from_client else "S->C",
           "text": bool(m.is_text), "len": len(m.content),
           "url": flow.request.pretty_url if flow.request else ""}
    if m.content:
        rec["file"] = _save(m.content, "ws_cs" if m.from_client else "ws_sc")
        if len(m.content) >= 9:
            try:
                pkt = struct.unpack_from("<I", m.content, 0)[0]
                rec["hdr"] = {"pkt": pkt & 0xFF, "pkt_hi": pkt >> 24,
                              "seq": struct.unpack_from("<H", m.content, 4)[0],
                              "flags": struct.unpack_from("<H", m.content, 6)[0],
                              "cmd": m.content[8]}
            except Exception: pass
    with open(WS_JSONL, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    h = rec.get("hdr")
    if h: print("[WS %s] %dB cmd=%d" % (rec["dir"], rec["len"], h["cmd"]))
'''


# ---------- 工具 ----------

def sh(*args, t=120):
    return subprocess.run([ADB, "-s", SER] + list(args),
                          capture_output=True, timeout=t)


_ROOT_MODE = None


def root_mode():
    """判断怎么拿 root：能直接是 uid=0 就直接跑，否则退回 su -c。

    Android 15 的 MuMu Nx 里没有 su 二进制（su: inaccessible or not found），
    但 `adb root` 之后 adbd 本身就是 root —— 这种情况直接执行即可。
    """
    global _ROOT_MODE
    if _ROOT_MODE is None:
        try:
            r = subprocess.run([ADB, "-s", SER, "shell", "id"],
                               capture_output=True, timeout=30)
            _ROOT_MODE = "direct" if b"uid=0" in (r.stdout or b"") else "su"
        except Exception:
            _ROOT_MODE = "su"
    return _ROOT_MODE


def sh_su(cmd, t=180):
    """设备上以 root 执行"""
    if root_mode() == "direct":
        return subprocess.run([ADB, "-s", SER, "shell", cmd],
                              capture_output=True, timeout=t)
    return subprocess.run([ADB, "-s", SER, "shell", "su -c '%s'" % cmd],
                          capture_output=True, timeout=t)


def push_text(content, remote):
    p = os.path.join(HERE, "_tmp_push")
    # 同时支持 str（脚本）与 bytes（CA 证书，二进制绝不能被改写）
    if isinstance(content, bytes):
        blob = content
    else:
        blob = content.replace("\r\n", "\n").encode("utf-8")
    with open(p, "wb") as f:
        f.write(blob)
    r = subprocess.run([ADB, "-s", SER, "push", p, remote],
                       capture_output=True, timeout=120)
    os.remove(p)
    return r


def out(*a):
    print(*a)


def port_free(p):
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", p)); return True
    except OSError:
        return False
    finally:
        s.close()


def find_mitmdump():
    for c in (os.path.expandvars(r"%APPDATA%\Python\Python312\Scripts\mitmdump.exe"),
              os.path.expandvars(r"%APPDATA%\Python\Python311\Scripts\mitmdump.exe")):
        if os.path.exists(c):
            return c
    return "mitmdump"


def ca_file():
    d = os.path.expandvars(r"%USERPROFILE%\.mitmproxy")
    if not os.path.isdir(d):
        return None
    for f in os.listdir(d):
        # mitmproxy 的 hash 命名是 <8 hex>.0 = 10 字符
        if len(f) == 10 and f.endswith(".0"):
            return os.path.join(d, f)
    # 兜底：mitmproxy-ca-cert.pem
    p = os.path.join(d, "mitmproxy-ca-cert.pem")
    return p if os.path.exists(p) else None


def our_processes():
    """返回本项目的宿主进程 (mitmdump/bridge) 数量"""
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "
                        "'bv_dump.py|bv_bridge_sni.py' }).Count"],
                       capture_output=True, timeout=60)
    try:
        return int(r.stdout.decode(errors="replace").strip() or 0)
    except ValueError:
        return 0


# ---------- 子命令 ----------

def cmd_check():
    ok = True
    out("=== Bingo Voyage 采集器 环境自检 ===\n")
    out("[adb] %s" % ADB)
    if not os.path.exists(ADB):
        out("  ✗ adb 不存在"); ok = False
    else:
        out("  ✓ 存在")
    r = sh("get-state")
    dev = r.stdout.decode(errors="replace").strip()
    out("[device] %s -> %s" % (SER, dev or "(无)"))
    if dev != "device":
        out("  ✗ 设备未连接"); ok = False
    else:
        out("  ✓ %s" % sh("shell", "getprop", "ro.product.cpu.abi").stdout.decode(errors="replace").strip())
    ru = sh_su("id")
    is_root = b"uid=0" in ru.stdout
    out("[root] %s" % ("✓ 有 root" if is_root else "✗ 无 root（需要 MuMu root_permission=true）"))
    if not is_root:
        ok = False
    out("[python 包]")
    try:
        import mitmproxy  # noqa
        out("  ✓ mitmproxy")
    except Exception:
        out("  ✗ mitmproxy 未安装 (pip install mitmproxy)"); ok = False
    ca = ca_file()
    out("[mitmproxy CA] %s" % (ca or "✗ 未生成（跑一次 mitmdump 会生成）"))
    if not ca:
        ok = False
    out("[端口]")
    running = our_processes()
    for p, n in ((PP, "mitmproxy"), (BP, "SNI 桥")):
        if port_free(p):
            out("  %d (%s) free" % (p, n))
        else:
            out("  %d (%s) 占用中%s" % (p, n, "  ← 本项目已在运行" if running else "  ← 被别的程序占用！"))
    out("[py 脚本解析]")
    for n in ("bv_ws2.py", "bv_proto.py"):
        p = os.path.join(ROOT, n)
        out("  %s %s" % ("✓" if os.path.exists(p) else "✗", p))
    out("\n结果: %s" % ("READY" if ok else "有阻塞项"))
    return 0 if ok else 1


def cmd_start():
    out("=== 1. 校验 ===")
    ca = ca_file()
    if not ca:
        out("✗ 找不到 mitmproxy CA，先手动跑一次 mitmdump 生成"); return 1
    if not port_free(PP):
        out("✗ 端口 %d 被占用（宿主的 8080 常被 llama-server 占用，本项目用 %d）" % (PP, PP))
        return 1
    if not port_free(BP):
        out("✗ 端口 %d 被占用" % BP); return 1

    out("=== 2. 推 CA 与设备脚本 ===")
    push_text(open(ca, "rb").read(), TMP + "/bv_ca.0")
    push_text(INSTALL_CA, TMP + "/bv_install_ca.sh")
    push_text(TEARDOWN_CA, TMP + "/bv_teardown_ca.sh")
    push_text(SETUP_REDIRECT.replace("__BP__", str(BP)), TMP + "/bv_setup_redirect.sh")
    push_text(TEARDOWN_REDIRECT.replace("__BP__", str(BP)), TMP + "/bv_teardown_redirect.sh")

    out("=== 3. adb reverse ===")
    sh("reverse", "--remove-all")
    for p in (PP, BP):
        sh("reverse", "tcp:%d" % p, "tcp:%d" % p)
    out(sh("reverse", "--list").stdout.decode(errors="replace").strip())

    out("=== 4. 装系统 CA ===")
    out(sh_su("sh %s/bv_install_ca.sh" % TMP).stdout.decode(errors="replace").strip())

    out("=== 5. 出站 443 重定向 ===")
    out(sh_su("sh %s/bv_setup_redirect.sh" % TMP).stdout.decode(errors="replace").strip())

    out("=== 6. 设备全局代理 ===")
    sh("shell", "settings", "put", "global", "http_proxy", "127.0.0.1:%d" % PP)
    out("  http_proxy = %s" % sh("shell", "settings", "get", "global", "http_proxy")
        .stdout.decode(errors="replace").strip())

    out("=== 7. 写 addon / 桥 / 启动器 ===")
    os.makedirs(OUT, exist_ok=True)
    addon = os.path.join(HERE, "bv_dump.py")
    with open(addon, "w", encoding="utf-8") as f:
        f.write(DUMP_ADDON.replace("__OUT__", OUT))
    bridge = os.path.join(HERE, "bv_bridge_sni.py")
    with open(bridge, "w", encoding="utf-8") as f:
        f.write(BRIDGE.replace("__PP__", str(PP))
                .replace("__UP__", CFG["capture"]["http_api"] + ":443"))
    for name, args in (
        ("bv_mitm.log", [find_mitmdump(), "-s", addon, "--listen-host", "127.0.0.1",
                         "--listen-port", str(PP), "--set",
                         "confdir=" + os.path.expandvars(r"%USERPROFILE%\.mitmproxy"),
                         "--set", "flow_detail=0", "-w", os.path.join(OUT, "bv_flows.mitm")]),
        ("bv_bridge.log", [sys.executable, bridge, str(BP)]),
    ):
        DETACHED = 0x00000008 | 0x00000200
        with open(os.path.join(OUT, name), "wb") as lf:
            subprocess.Popen(args, stdout=lf, stderr=lf,
                             creationflags=DETACHED, close_fds=True)
        out("  已后台启动 -> %s" % name)

    time.sleep(4)
    out("\n=== 8. 校验 ===")
    for p, n in ((PP, "mitmproxy"), (BP, "SNI 桥")):
        out("  %-10s :%d %s" % (n, p, "✓ 监听中" if not port_free(p) else "✗ 未监听"))
    out("\n链路已建立。现在在游戏里玩一局，然后：")
    out("  python collector\\bv_extract.py   # 结构化抽取")
    out("  python collector\\bv_report.py    # 生成数值拆解")
    return 0


def cmd_stop():
    out("=== 还原 ===")
    out(sh_su("sh %s/bv_teardown_redirect.sh" % TMP).stdout.decode(errors="replace").strip())
    out(sh_su("sh %s/bv_teardown_ca.sh" % TMP).stdout.decode(errors="replace").strip())
    sh("shell", "settings", "put", "global", "http_proxy", ":0")
    out("  http_proxy = %s" % sh("shell", "settings", "get", "global", "http_proxy")
        .stdout.decode(errors="replace").strip())
    sh("reverse", "--remove-all")
    out("  adb reverse 已清空")
    # 停掉本项目的两个宿主进程
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'bv_dump.py|bv_bridge_sni.py' } "
                        "| ForEach-Object { Stop-Process -Id $_.ProcessId -Force; $_.ProcessId }"],
                       capture_output=True, timeout=120)
    out("  已停止宿主进程: %s" % r.stdout.decode(errors="replace").split() or "(无)")
    out("\n已完全还原。")
    return 0


def cmd_status():
    out("=== 链路状态 ===")
    out("设备      : %s (%s)" % (SER, sh("get-state").stdout.decode(errors="replace").strip()))
    out("游戏 pid  : %s" % sh("shell", "pidof", PKG).stdout.decode(errors="replace").strip())
    out("http_proxy: %s" % sh("shell", "settings", "get", "global", "http_proxy")
        .stdout.decode(errors="replace").strip())
    out("CA        : %s" % sh_su("ls /system/etc/security/cacerts/ | wc -l")
        .stdout.decode(errors="replace").strip() + " certs")
    out("重定向    : %s" % sh_su("iptables -t nat -L OUTPUT -n")
        .stdout.decode(errors="replace").count("REDIRECT") and "ON" or "OFF")
    out("reverse   : %s" % " | ".join(sh("reverse", "--list").stdout.decode(errors="replace").split()))
    out("mitmproxy : %s" % ("✓ :%d" % PP if not port_free(PP) else "✗ 未跑"))
    out("SNI 桥    : %s" % ("✓ :%d" % BP if not port_free(BP) else "✗ 未跑"))
    ws = os.path.join(OUT, "bv_ws.jsonl")
    fl = os.path.join(OUT, "bv_flows.jsonl")
    for p, n in ((ws, "WS 帧"), (fl, "HTTP flow")):
        if os.path.exists(p):
            out("%-10s: %d 条 (%d bytes)" % (n, sum(1 for _ in open(p, encoding="utf-8", errors="replace")), os.path.getsize(p)))
        else:
            out("%-10s: 无" % n)
    return 0


def cmd_play():
    sh("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    out("已启动 %s" % PKG)
    return 0


def cmd_round():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=60)
    a, _ = ap.parse_known_args()
    r = subprocess.run([sys.executable, os.path.join(ROOT, "bv_autodaub.py"),
                        "--seconds", str(min(a.seconds, 180))])
    return r.returncode


if __name__ == "__main__":
    cmds = {"check": cmd_check, "start": cmd_start, "stop": cmd_stop,
            "status": cmd_status, "play": cmd_play, "round": cmd_round}
    c = sys.argv[1] if len(sys.argv) > 1 else "check"
    if c not in cmds:
        print("用法: python bv_collect.py {%s}" % "|".join(cmds))
        sys.exit(2)
    sys.exit(cmds[c]())
