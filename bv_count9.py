"""Freeze legacy raw references; report observations, never token fill rates.

Output must be a fresh directory outside the public repository.
"""
import argparse
import datetime as dt
import json
from collections import Counter
from pathlib import Path

from bv_evidence import VERSION, decode, expected_cells, measure, state_diagnostics


def audit(session, index, bodies, output):
    session, index, bodies, output = map(Path, (session, index, bodies, output))
    output.mkdir(parents=True, exist_ok=False)
    card_record = json.loads((session / "cards_in_round.json").read_text("utf-8"))
    rid, cards = card_record["round"], card_record["cards"]
    end = index.stat().st_size
    events, errors, names = [], Counter(), Counter()
    offset = 0
    with index.open("rb") as f:
        while offset < end:
            line = f.readline()
            at = offset
            offset = f.tell()
            if not line.endswith(b"\n") or offset > end:
                break
            try:
                rec = json.loads(line)
            except ValueError:
                errors["index_json_error"] += 1
                continue
            if rec.get("hdr", {}).get("cmd") not in (163, 166, 167, 169):
                continue
            name = rec.get("file", "")
            if not name or Path(name).name != name or "/" in name or "\\" in name:
                errors["invalid_body_path"] += 1
                continue
            names[name] += 1
            try:
                data = (bodies / name).read_bytes()
            except OSError:
                errors["missing_candidate_body"] += 1
                continue
            if rid.encode("utf-8") not in data:
                continue
            try:
                event = decode(data, rec, {"index": str(index), "offset": at, "body": str(bodies/name)})
                event["session_id"] = session.name
                if event.get("round_id") == rid:
                    events.append(event)
            except (ValueError, UnicodeError, TypeError) as exc:
                reason = str(exc) if isinstance(exc, ValueError) and str(exc).isidentifier() else type(exc).__name__
                errors["target_" + reason] += 1
    target_names = {e["source_file"] for e in events}
    reused = sum(names[n] > 1 for n in target_names)
    if reused:
        errors["target_body_reused"] += reused
    balls = set()
    reported = set()
    states = []
    for e in events:
        if e["type"] == "balls":
            balls.update(e["window"])
        elif e["type"] == "cell_observation":
            reported.add((e["card_id"], e["cell_index"]))
        elif e["type"] == "state_observation":
            states.append(state_diagnostics(e["state"]))
    expected = expected_cells(cards, balls)
    # Old captures have no proven terminal event or complete denominator.
    frozen = {"parser_version": VERSION, "evidence_kind": "observed-live",
              "instance": "legacy-unverified", "session_id": session.name,
              "round_id": rid, "cards": cards, "balls": sorted(balls),
              "start": 0, "end": 0, "closed": False, "denominator_complete": False,
              "terminal_complete": False, "verified_cells": [],
              "errors": sorted(errors), "source_index": str(index), "source_end": end,
              "frozen_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    result = measure(frozen)
    summary = {"result": result, "observed_ball_count": len(balls),
               "client_reported_distinct_cells": len(reported),
               "reported_outside_observed_targets": len(reported-expected),
               "state_diagnostics": states,
               "capture_errors": dict(errors), "source_records": len(events),
               "subtypes": dict(Counter(str(e["subtype"]) for e in events if "subtype" in e)),
               "note": "E is observed-only; no qualified rate or acceptance conclusion"}
    for name, value in (("frozen.json", frozen), ("summary.json", summary)):
        with (output/name).open("x", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
    with (output/"events.jsonl").open("x", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False)+"\n")
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("session")
    ap.add_argument("--index", type=Path, required=True)
    ap.add_argument("--bodies", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    summary = audit(a.session, a.index, a.bodies, a.output)
    print(json.dumps(summary, ensure_ascii=False))
    return 2 if summary["result"]["status"] == "Invalid" else 0


if __name__ == "__main__":
    raise SystemExit(main())
