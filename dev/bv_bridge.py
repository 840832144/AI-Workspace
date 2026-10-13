"""把设备上「绕过系统代理的直连」桥接进 mitmproxy（HTTP CONNECT 隧道）。

原理：
  设备上 iptables -t nat -A OUTPUT -d <目标IP> -p tcp --dport 443
        -j REDIRECT --to-ports <本机端口>
  → adb reverse 把设备 127.0.0.1:<本机端口> 转给宿主 127.0.0.1:<本机端口>
  → 本脚本在此监听，每条连接向 mitmproxy(:8099) 发 CONNECT <upstream>
  → 双向透传，mitmproxy 就能解密并落盘

用法：
    python bv_bridge.py 9443 bingo2.superbgame.net 443
    python bv_bridge.py 9444 logan.voyage.bingo 443
    python bv_bridge.py 9445 entry.bingo.elitescastle.com 443
"""
import socket
import sys
import threading
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8099


def pump(a, b, tag):
    try:
        while True:
            data = a.recv(65536)
            if not data:
                break
            b.sendall(data)
    except Exception:
        pass
    finally:
        for s in (a, b):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass


def handle(client, addr, upstream_host, upstream_port, seq):
    tag = "#%d %s:%d" % (seq, upstream_host, upstream_port)
    try:
        up = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=15)
    except Exception as e:
        print("[%s] 连不上 mitmproxy: %r" % (tag, e))
        client.close()
        return
    try:
        req = ("CONNECT %s:%d HTTP/1.1\r\nHost: %s:%d\r\n"
               "Proxy-Connection: Keep-Alive\r\n\r\n") % (
            upstream_host, upstream_port, upstream_host, upstream_port)
        up.sendall(req.encode())
        up.settimeout(15)
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = up.recv(4096)
            if not chunk:
                raise IOError("proxy closed during CONNECT")
            buf += chunk
        head = buf.split(b"\r\n\r\n", 1)[0].decode("latin-1")
        if not head.startswith("HTTP/1.1 200") and "200" not in head.split("\r\n")[0]:
            print("[%s] CONNECT 失败: %s" % (tag, head.split("\r\n")[0]))
            up.close()
            client.close()
            return
        rest = buf.split(b"\r\n\r\n", 1)[1]
        if rest:
            client.sendall(rest)
        print("[%s] 隧道建立 (%s)" % (tag, time.strftime("%H:%M:%S")))
        up.settimeout(None)
        t = threading.Thread(target=pump, args=(client, up, tag), daemon=True)
        t.start()
        pump(up, client, tag)
        t.join(timeout=5)
    except Exception as e:
        print("[%s] 错误 %r" % (tag, e))
    finally:
        for s in (client, up):
            try:
                s.close()
            except Exception:
                pass
        print("[%s] 隧道关闭" % tag)


def main():
    listen_port = int(sys.argv[1])
    upstream_host = sys.argv[2]
    upstream_port = int(sys.argv[3]) if len(sys.argv) > 3 else 443
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", listen_port))
    srv.listen(64)
    print("bridge :%d -> mitmproxy:%d -> %s:%d" % (
        listen_port, PROXY_PORT, upstream_host, upstream_port))
    seq = 0
    while True:
        try:
            client, addr = srv.accept()
        except Exception:
            break
        seq += 1
        threading.Thread(target=handle,
                         args=(client, addr, upstream_host, upstream_port, seq),
                         daemon=True).start()


if __name__ == "__main__":
    main()
