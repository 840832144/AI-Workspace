"""mitmproxy addon：把每个 flow 落盘成 JSONL（含 protobuf 原始字节 base64），
供后续离线解 protobuf。

启动：
    python -m mitmproxy.tools.dump -s D:\\BingoVoyageProbe\\dev\\bv_dump.py ^
        --listen-host 127.0.0.1 --listen-port 8080 ^
        -w D:\\BingoVoyageProbe\\out\\bv_flows.mitm
"""
import base64
import json
import os
import time
import uuid
import datetime

OUT = r"D:\BingoVoyageProbe\out"
JSONL = os.path.join(OUT, "bv_flows.jsonl")
WS_JSONL = os.path.join(OUT, "bv_ws.jsonl")
BODIES = os.path.join(OUT, "bv_bodies")

_seq = [0]
# ★ 关键：文件名必须全局唯一。
# 原来只用自增计数器（006_ws_sc.bin），addon 一重启计数器就归零，
# 后来的抓包会直接覆盖早先的 body 文件 —— 旧 jsonl 记录于是指向了别人的内容
# （实测 70683 条记录只有 65254 个文件，5355 个文件名被复用、10784 条记录受污染）。
_RUN = uuid.uuid4().hex


def _save_blob(data, tag):
    os.makedirs(BODIES, exist_ok=True)
    if not data:
        return None
    _seq[0] += 1
    name = "%s_%06d_%s.bin" % (_RUN, _seq[0], tag)
    p = os.path.join(BODIES, name)
    with open(p, "xb") as f:
        f.write(data)
    return name


def _decode_http_msg(msg):
    """尽量还原 body：处理 gzip/deflate，protobuf 无法还原时给 hex 摘要。"""
    raw = msg.content
    try:
        text = raw.decode("utf-8")
        is_text = all(c.isprintable() or c in "\r\n\t" for c in text[:2000])
    except Exception:
        text, is_text = None, False
    return {
        "content_type": (msg.headers.get("content-type") or msg.headers.get("Content-Type") or ""),
        "len": len(raw),
        "text": text if is_text else None,
        "b64": base64.b64encode(raw).decode() if raw else None,
    }


def request(flow):
    flow.metadata["t0"] = time.time()


def response(flow):
    os.makedirs(OUT, exist_ok=True)
    try:
        req, resp = flow.request, flow.response
        if resp is None:
            return
        rq_body = req.content or b""
        rs_body = resp.content or b""
        rec = {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "method": req.method,
            "scheme": req.scheme,
            "host": req.host,
            "port": req.port,
            "path": req.path,
            "url": req.pretty_url,
            "status": resp.status_code,
            "req_headers": dict(req.headers),
            "resp_headers": dict(resp.headers),
            "req": _decode_http_msg(req),
            "resp": _decode_http_msg(resp),
        }
        if rq_body:
            rec["req_file"] = _save_blob(rq_body, "req")
        if rs_body:
            rec["resp_file"] = _save_blob(rs_body, "resp")
        with open(JSONL, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print("[FLOW] %s %s%s -> %s (%d B req / %d B resp)" % (
            req.method, req.host, req.path, resp.status_code, len(rq_body), len(rs_body)))
    except Exception as e:  # 抓包失败不能影响游戏
        print("[ERR] %r" % (e,))


def _ws_log(flow, direction, content, kind):
    """把 WebSocket 帧落盘：原始字节 + 解析出的 10 字节帧头。"""
    rec = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "dir": direction,
        "kind": kind,          # text / binary
        "len": len(content),
        "url": flow.request.pretty_url if flow.request else "",
    }
    if content:
        rec["file"] = _save_blob(content, "ws_" + direction)
        # 解析游戏帧头：u32 type | u32 ver | u16 cmd | protobuf
        if len(content) >= 10:
            import struct as _s
            a, b, c = _s.unpack_from("<IIH", content, 0)
            rec["hdr"] = {"a": a, "b": b, "cmd": c, "payload_len": len(content) - 10}
    with open(WS_JSONL, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    h = rec.get("hdr")
    print("[WS %s] %s %dB %s" % (
        direction, kind, len(content),
        ("cmd=%d type=%d payload=%dB" % (h["cmd"], h["a"], h.get("payload_len", max(0, len(content)-9)))) if h else ""))


def _ws_data(flow):
    """mitmproxy 12：WS 流是 HTTPFlow，消息挂在 flow.websocket.messages。"""
    ws = getattr(flow, "websocket", None)
    if ws is None:
        return None
    return ws


def websocket_started(flow):
    ws = _ws_data(flow)
    print("[WS STARTED] %s" % (flow.request.pretty_url if flow.request else "?"))


def websocket_message(flow):
    os.makedirs(OUT, exist_ok=True)
    ws = _ws_data(flow)
    if ws is None or not ws.messages:
        return
    m = ws.messages[-1]
    received_ns = time.time_ns()
    received_mono_ns = time.monotonic_ns()
    content = m.content
    direction = "C->S" if m.from_client else "S->C"
    rec = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "dir": direction,
        "text": bool(m.is_text),
        "len": len(content),
        "url": flow.request.pretty_url if flow.request else "",
    }
    rec.update(epoch=_RUN, connection=str(flow.id), received_ns=received_ns,
               monotonic_ns=received_mono_ns,
               ts_utc=datetime.datetime.fromtimestamp(received_ns/1e9, datetime.timezone.utc).isoformat())
    if content:
        rec["file"] = _save_blob(content, "ws_" + direction.replace("->", "").lower())
        # 正确帧结构：u32 pkt | u16 seq | u16 flags | u8 cmd | varint len | topic | protobuf
        if len(content) >= 9:
            import struct as _s
            try:
                pkt = _s.unpack_from("<I", content, 0)[0]
                seq = _s.unpack_from("<H", content, 4)[0]
                flags = _s.unpack_from("<H", content, 6)[0]
                rec["hdr"] = {"pkt": pkt & 0xFF, "pkt_hi": pkt >> 24,
                              "seq": seq, "flags": flags, "cmd": content[8]}
            except Exception:
                pass
    with open(WS_JSONL, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    h = rec.get("hdr")
    print("[WS %s] %dB %s" % (
        direction, len(content),
        ("cmd=%d pkt=%d payload=%dB" % (h["cmd"], h["pkt"], h.get("payload_len", max(0, len(content)-9)))) if h else ""))


def websocket_end(flow):
    print("[WS END] %s" % (flow.request.pretty_url if flow.request else "?"))


def websocket_error(flow):
    print("[WS ERROR] %s" % (getattr(flow, "error", "?")))


def tcp_message(flow):
    m = flow.messages[-1]
    print("[TCP] %s:%s from_client=%s %d B" % (
        flow.server_conn.address[0] if flow.server_conn.address else "?",
        flow.server_conn.address[1] if flow.server_conn.address else "?",
        m.from_client, len(m.content)))
    if m.content:
        _save_blob(m.content, "tcp_c" if m.from_client else "tcp_s")
