"""Bounded raw reader and independent Bingo evidence checks (no UI or controller import).

Protocol observations are NOT accepted-state confirmations. No live mapping is
certified yet; tests explicitly use synthetic fixtures, never real acceptance.
"""
import json
import re
import time
from collections import Counter
from pathlib import Path

from bv_proto import parse
from bv_ws2 import parse_frame

VERSION = "task0039-r2-v4"


def fields(body):
    result = parse(body)
    if any(k is None or k < 1 or isinstance(v, str) and
           (w == 0 or c is None) for k, w, v, c in result):
        raise ValueError("malformed_protobuf")
    return result


def round_id(body):
    ids = []
    for k, w, v, c in fields(body):
        if k == 1 and w == 2:
            try:
                text = c.decode("utf-8")
            except UnicodeError:
                continue  # nested snapshot, not a direct round string
            if text.startswith("BINGO_HALL"):
                ids.append(text)
    return ids[0] if len(ids) == 1 else None


def decode(data, rec, source):
    frame = parse_frame(data)
    if not frame.get("ok"):
        raise ValueError("malformed_frame")
    if len(data) != rec.get("len") or any(
        frame[k] != rec.get("hdr", {}).get(k) for k in ("cmd", "seq", "flags")
    ):
        raise ValueError("body_index_mismatch")
    base = {"source_ref": source, "source_file": rec["file"],
            "received_at": rec.get("ts_utc", rec.get("ts")),
            "legacy_timezone": "+08:00" if 'ts_utc' not in rec else None,
            "received_ns": rec.get("received_ns"),
            "epoch": rec.get("epoch"), "connection": rec.get("connection"),
            "sequence": frame["seq"], "direction": rec.get("dir"),
            "parser_version": VERSION, "evidence_level": "client_observation",
            "cmd": frame["cmd"], "message_id":frame["message_id"], "type": "frame"}
    if frame["message_id"] not in (100003,100006,100007,100009):
        return base
    body = frame["body"]
    rid = round_id(body)
    base["round_id"] = rid
    fs = fields(body)
    if frame["message_id"] == 100009 and rec.get("dir") == "S->C":
        windows = [list(c) for k, w, v, c in fs if k == 2 and w == 2]
        if rid and (not windows or windows == [[]]):
            base.update(type="empty_ball_window", window=[], evidence_level="server_observation")
            return base  # repeated protobuf field omitted; not proof of round close
        if len(windows) != 1 or not rid or not windows[0] or any(
            not 1 <= n <= 75 for n in windows[0]
        ):
            raise ValueError("invalid_ball_window")
        base.update(type="balls", window=windows[0], evidence_level="server_observation")
    elif frame["message_id"] == 100007 and rec.get("dir") == "C->S":
        envelopes = [c for k, w, v, c in fs if k == 2 and w == 2]
        if len(envelopes) != 1 or not rid:
            raise ValueError("ambiguous_action")
        inner = fields(envelopes[0])
        subs = [v for k, w, v, c in inner if k == 1 and w == 0]
        if len(subs) != 1:
            raise ValueError("ambiguous_subtype")
        base["subtype"] = subs[0]
        if subs[0] == 1:
            cells = [fields(c) for k, w, v, c in inner if k == 3 and w == 2]
            if len(cells) != 1:
                raise ValueError("ambiguous_cell")
            values = {k: v for k, w, v, c in cells[0] if w == 0}
            if len(values) != len(cells[0]) or not set(values) <= {1,2,3,4,5}:
                raise ValueError("missing_cell_identity")
            # Named client ActionReq logs independently expose omitted protobuf zeros.
            # This only resolves identity, never promotes the request to accepted fill.
            cell,card=values.get(1,0),values.get(2,0)
            if not (0<=cell<25 and 0<=card<4):raise ValueError("cell_identity_out_of_range")
            base.update(type="cell_observation", card_id=card + 1, cell_index=cell)
        elif subs[0] == 9:
            states = [c.decode("ascii") for k, w, v, c in inner if k == 2 and w == 2]
            if len(states) != 1:
                raise ValueError("ambiguous_state")
            base.update(type="state_observation", state=states[0])
    return base


class RawTail:
    """Complete lines only; body delay bounded; rotation and parse failures explicit."""
    def __init__(self, path, bodies=None, body_wait=2.0, end=None, start=0):
        self.path = Path(path)
        self.bodies = Path(bodies) if bodies else self.path.parent / "bv_bodies"
        self.pos = start
        self.end = end
        self.body_wait = body_wait
        self.pending = []
        self.errors = Counter()
        self.seen_files = set()
        self.identity = None
        self.prefix = None

    def poll(self, now=None, limit=512):
        now = time.monotonic() if now is None else now
        st = self.path.stat()
        with self.path.open("rb") as stream:
            prefix = stream.read(min(64, st.st_size))
            identity = (st.st_dev, st.st_ino)
            if self.identity is not None and (identity != self.identity or st.st_size < self.pos or
                    self.prefix and not prefix.startswith(self.prefix)):
                self.errors["index_rotation"] += 1
                raise ValueError("index_rotation")
            self.identity = identity
            self.prefix = prefix
            stream.seek(self.pos)
            for _ in range(limit):
                if self.end is not None and self.pos >= self.end:
                    break
                line = stream.readline()
                if not line or not line.endswith(b"\n"):
                    break
                if self.end is not None and stream.tell() > self.end:
                    break
                offset = self.pos
                self.pos = stream.tell()
                try:
                    rec = json.loads(line)
                    name = rec.get("file")
                    if not isinstance(name, str) or Path(name).name != name or "/" in name or "\\" in name:
                        raise ValueError("invalid_body_path")
                    if name in self.seen_files:
                        raise ValueError("duplicate_body_reference")
                    self.seen_files.add(name)
                    self.pending.append((now, offset, rec))
                except (ValueError, TypeError, AttributeError):
                    self.errors["invalid_index_record"] += 1
        events = []
        waiting = []
        for first, offset, rec in self.pending:
            path = self.bodies / rec["file"]
            try:
                data = path.read_bytes()
                if len(data) < rec.get("len", 0) and now - first < self.body_wait:
                    waiting.append((first, offset, rec))
                    continue
                source = {"index": str(self.path), "offset": offset, "body": str(path)}
                events.append(decode(data, rec, source))
            except FileNotFoundError:
                if now - first < self.body_wait:
                    waiting.append((first, offset, rec))
                else:
                    self.errors["missing_body"] += 1
            except (ValueError, UnicodeError, TypeError, OSError) as exc:
                self.errors[str(exc) if isinstance(exc, ValueError) else type(exc).__name__] += 1
        self.pending = waiting
        return events


def state_diagnostics(state, card_count=4):
    """Strip proven wrapper syntax; do NOT infer cell meaning from nonempty tokens."""
    raw = state.split("|")
    stripped = re.sub(r"@[^|#]*#", "", state).split("|")
    return {"token_count": len(raw), "shape_valid": len(raw) == 24 * card_count + 1,
            "legacy_nonempty": [sum(bool(t) for t in raw[i*24:(i+1)*24]) for i in range(card_count)],
            "payload_nonempty": [sum(bool(t) for t in stripped[i*24:(i+1)*24]) for i in range(card_count)],
            "special_markers": sum(t not in ("", "1::", "@", "@Z") for t in stripped),
            "semantic_status": "Unknown"}


def expected_cells(cards, balls):
    if len(cards) != 4 or {c["slot"] for c in cards} != {1, 2, 3, 4}:
        raise ValueError("not_four_distinct_cards")
    result = set()
    for c in cards:
        vals = c["vals"]
        if len(vals) != 25:
            raise ValueError("invalid_card_size")
        for col in range(5):
            numbers = [v for i, v in enumerate(vals) if i // 5 == col and i != 12]
            if len(set(numbers)) != len(numbers) or any(type(v) is not int or
                    not col * 15 < v <= (col + 1) * 15 for v in numbers):
                raise ValueError("invalid_card_band")
        result.update((c["slot"], k) for k, n in enumerate(vals) if k != 12 and n in balls)
    return result


def measure(frozen):
    """Independent set arithmetic. Live decoder cannot produce verified_cells yet.

    Evidence qualification is separate from counting. Synthetic fixtures exercise
    arithmetic but are marked synthetic and cannot pass a real batch.
    """
    expected = expected_cells(frozen["cards"], set(frozen["balls"]))
    confirmed = set()
    unfilled = set()
    errors = list(frozen.get("errors", []))
    synthetic = frozen.get("evidence_kind") == "synthetic"
    for e in frozen.get("verified_cells", []):
        # No production semantic adapter has been validated; refuse user-set flags.
        if not synthetic:
            errors.append("production_semantics_unverified")
            continue
        if (e.get("round_id"), e.get("session_id"), e.get("instance")) != (
            frozen["round_id"], frozen["session_id"], frozen["instance"]):
            errors.append("identity_mismatch")
            continue
        key = (e.get("card_id"), e.get("cell_index"))
        if not frozen["start"] <= e.get("at", -1) <= frozen["end"] or key not in expected:
            errors.append("outside_target_or_window")
            continue
        if e.get("filled") is True:
            confirmed.add(key)
        elif e.get("filled") is False:
            unfilled.add(key)
    if confirmed & unfilled:
        errors.append("contradictory_state")
    if not frozen.get("denominator_complete"):
        errors.append("denominator_incomplete")
    if not frozen.get("closed"):
        errors.append("round_close_unverified")
    if not synthetic:
        errors.append("production_semantics_unverified")
    n, d = len(expected & confirmed), len(expected)
    status = "Invalid" if errors else ("N/A" if not d else
             "exact" if frozen.get("terminal_complete") and expected <= confirmed | unfilled
             else "verified_lower_bound")
    arithmetic_pass = not errors and d > 0 and 10*n > 9*d
    return {"status": status, "evidence_kind": "synthetic" if synthetic else "unqualified",
            **{k: frozen.get(k) for k in ("batch_id", "instance", "session_id", "round_id",
                "cardset_ref", "frozen_ref", "code_version", "parser_version", "metric_version", "start", "end")},
            "N": n, "E": d, "Unknown": len(expected - confirmed - unfilled),
            "confirmed_unfilled": len(unfilled), "errors": sorted(set(errors)),
            "arithmetic_pass": arithmetic_pass,
            "evidence_valid": False, "acceptance_pass": False, "hard_pass": False,
            "rate": n/d if not errors and d else None,
            "per_card": [{"card": i, "E": sum(k[0] == i for k in expected),
                          "N": sum(k[0] == i for k in expected & confirmed),
                          "confirmed_unfilled": sum(k[0] == i for k in unfilled),
                          "Unknown": sum(k[0] == i for k in expected - confirmed - unfilled)}
                         for i in range(1, 5)]}


def aggregate(results, registered_count=10):
    """Production aggregation accepts a registered directory, never caller summaries."""
    if isinstance(results, (str, Path)):
        from bv_batch import verify_batch
        return verify_batch(Path(results))
    return {"status": "Invalid", "qualified": False, "hard_pass": False,
            "acceptance_pass": False, "optimization_pass": False, "weighted_rate": None,
            "errors": ["registered_batch_and_raw_sources_required"],
            "started_rounds": len(results), "registered_rounds": registered_count}
