"""SNI 感知的透明 TLS 桥：把设备上「绕过系统代理的直连」送进 mitmproxy。

原理：
  1) 设备上 iptables -t nat -A OUTPUT -p tcp --dport 443 ! -d 127.0.0.0/8 \\
         -j REDIRECT --to-ports 9443
  2) adb reverse tcp:9443 -> 宿主 127.0.0.1:9443（本脚本监听）
  3) 本脚本 peek 首个 ClientHello，从扩展里取出 SNI
  4) 向 mitmproxy(:8099) 发 CONNECT <SNI>:443，之后双向透传
  → mitmproxy 用系统 CA 签发的证书完成 MITM，WebSocket / HTTP 全部可见

用法：
    python bv_bridge_sni.py 9443 [默认上游:端口]
"""
import socket
import struct
import sys
import threading
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8099
DEFAULT_UPSTREAM = "bingo2.superbgame.net:443"


def parse_sni(buf):
    """从 TLS ClientHello 里取 SNI。失败返回 None。"""
    try:
        if len(buf) < 6 or buf[0] != 0x16 or buf[5] != 0x01:
            return None
        i = 9                                  # 跳过 record(5) + handshake(4)
        i += 2                                 # client_version
        i += 32                                # random
        sid_len = buf[i]
        i += 1 + sid_len
        cs_len = struct.unpack_from(">H", buf, i)[0]
        i += 2 + cs_len
        comp_len = buf[i]
        i += 1 + comp_len
        if i + 2 > len(buf):
            return None
        ext_total = struct.unpack_from(">H", buf, i)[0]
        i += 2
        end = min(len(buf), i + ext_total)
        while i + 4 <= end:
            etype, elen = struct.unpack_from(">HH", buf, i)
            i += 4
            if etype == 0x0000:                # server_name
                if i + 5 > len(buf):
                    return None
                ln = struct.unpack_from(">H", buf, i)[0]
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


def handle(client, addr, default_up, seq):
    up = None
    try:
        client.settimeout(20)
        head = b""
        while len(head) < 5:
            c = client.recv(1)
            if not c:
                raise IOError("client closed")
            head += c
        if head[0] == 0x16:
            rec_len = struct.unpack_from(">H", head, 3)[0]
            need = 5 + rec_len
            while len(head) < need:
                c = client.recv(need - len(head))
                if not c:
                    break
                head += c
        else:
            # 非 TLS：当作明文 HTTP，读一小段头
            while b"\r\n\r\n" not in head and len(head) < 8192:
                c = client.recv(4096)
                if not c:
                    break
                head += c

        sni = parse_sni(head)
        upstream = ("%s:443" % sni) if sni else default_up
        tag = "#%d %s" % (seq, upstream)

        up = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=15)
        req = ("CONNECT %s HTTP/1.1\r\nHost: %s\r\n"
               "Proxy-Connection: Keep-Alive\r\n\r\n") % (upstream, upstream)
        up.sendall(req.encode())
        up.settimeout(15)
        buf = b""
        while b"\r\n\r\n" not in buf:
            c = up.recv(4096)
            if not c:
                raise IOError("proxy closed during CONNECT")
            buf += c
        first = buf.split(b"\r\n", 1)[0].decode("latin-1")
        if "200" not in first:
            print("[%s] CONNECT 失败: %s" % (tag, first))
            return
        rest = buf.split(b"\r\n\r\n", 1)[1]
        if rest:
            client.sendall(rest)
        if head:
            up.sendall(head)
        print("[%s] 隧道建立 %s" % (tag, time.strftime("%H:%M:%S")))
        client.settimeout(None)
        t = threading.Thread(target=pump, args=(client, up), daemon=True)
        t.start()
        pump(up, client)
        t.join(timeout=5)
    except Exception as e:
        print("[#%d] 错误 %r" % (seq, e))
    finally:
        for s in (client, up):
            if s is not None:
                try:
                    s.close()
                except Exception:
                    pass
        print("[#%d] 隧道关闭" % seq)


def main():
    listen_port = int(sys.argv[1])
    default_up = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_UPSTREAM
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", listen_port))
    srv.listen(128)
    print("SNI-bridge :%d -> mitmproxy:%d (默认上游 %s)" % (
        listen_port, PROXY_PORT, default_up))
    seq = 0
    while True:
        try:
            client, addr = srv.accept()
        except Exception:
            break
        seq += 1
        threading.Thread(target=handle, args=(client, addr, default_up, seq),
                         daemon=True).start()


if __name__ == "__main__":
    main()
