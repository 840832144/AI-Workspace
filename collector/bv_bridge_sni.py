"""SNI 感知的透明 TLS 桥：peek ClientHello 取 SNI，向 mitmproxy 发 CONNECT。"""
import socket, struct, sys, threading
PROXY_HOST, PROXY_PORT = "127.0.0.1", 8099
DEFAULT_UP = "bingo2.superbgame.net:443"

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
