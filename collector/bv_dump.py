"""mitmproxy addon：HTTP + WebSocket 全量落盘（Bingo Voyage 采集器）。"""
import base64, json, os, struct, time
import uuid
import datetime
OUT = r"D:\BingoVoyageProbe\out"
JSONL = os.path.join(OUT, "bv_flows.jsonl")
WS_JSONL = os.path.join(OUT, "bv_ws.jsonl")
BODIES = os.path.join(OUT, "bv_bodies")
_seq = [0]
_RUN = uuid.uuid4().hex

def _save(data, tag):
    os.makedirs(BODIES, exist_ok=True)
    if not data: return None
    _seq[0] += 1
    name = "%s_%06d_%s.bin" % (_RUN, _seq[0], tag)
    with open(os.path.join(BODIES, name), "xb") as f: f.write(data)
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
    os.makedirs(OUT, exist_ok=True)
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
    os.makedirs(OUT, exist_ok=True)
    ws = getattr(flow, "websocket", None)
    if ws is None or not ws.messages: return
    m = ws.messages[-1]
    received_ns = time.time_ns()
    received_mono_ns = time.monotonic_ns()
    rec = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "dir": "C->S" if m.from_client else "S->C",
           "text": bool(m.is_text), "len": len(m.content),
           "url": flow.request.pretty_url if flow.request else ""}
    rec.update(epoch=_RUN, connection=str(flow.id), received_ns=received_ns,
               monotonic_ns=received_mono_ns,
               ts_utc=datetime.datetime.fromtimestamp(received_ns/1e9, datetime.timezone.utc).isoformat())
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
