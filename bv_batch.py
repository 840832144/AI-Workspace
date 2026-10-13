"""Registered-batch verification. Public summaries are never verification input."""
import json
from pathlib import Path

IDENTITY = ("batch_id", "instance", "code_version", "parser_version", "metric_version")


def check_batch(registration, starts, rounds):
    """Structural/arithmetic checks; this function never grants live acceptance."""
    errors = []
    if registration.get("purpose") != "acceptance" or registration.get("planned_rounds") != 10:
        errors.append("acceptance_registration_required")
    if len(starts) != 10 or len(rounds) != len(starts):
        errors.append("all_ten_started_rounds_required")
    if any(not registration.get(k) for k in IDENTITY):
        errors.append("registration_identity_missing")
    seen_rounds, seen_sessions, seen_refs = set(), set(), set()
    last_end = registration.get("registered_ns", -1)
    last_source_end = registration.get("source_start", -1)
    for i, (start, r) in enumerate(zip(starts, rounds), 1):
        if start.get("ordinal") != i:
            errors.append("started_round_order_or_gap")
        if any(r.get(k) != registration.get(k) or start.get(k) != registration.get(k) for k in IDENTITY):
            errors.append("mixed_version_or_instance")
        for key, seen in (("round_id", seen_rounds), ("session_id", seen_sessions), ("frozen_ref", seen_refs)):
            value = r.get(key)
            if not value or value in seen:
                errors.append("missing_or_duplicate_"+key)
            seen.add(value)
        if r.get("session_id") != start.get("session_id") or r.get("frozen_ref") != start.get("frozen_ref"):
            errors.append("round_not_registered")
        if not r.get("cardset_ref") or not r.get("sources_rebuilt"):
            errors.append("raw_sources_not_rebuilt")
        if not (isinstance(start.get("started_ns"), int) and isinstance(r.get("ended_ns"), int)
                and last_end <= start["started_ns"] < r["ended_ns"]):
            errors.append("time_order_invalid")
        else:
            last_end = r["ended_ns"]
        if not (type(r.get("source_start")) is int and type(r.get("source_end")) is int
                and last_source_end <= r["source_start"] < r["source_end"]
                and r["source_start"] == start.get("source_start")):
            errors.append("source_range_overlap_or_gap")
        else:
            last_source_end = r["source_end"]
        if r.get("manual_takeover") or r.get("status") not in ("exact", "verified_lower_bound"):
            errors.append("incomplete_or_failed_round")
        n, d, u, missed = (r.get(k) for k in ("N", "E", "Unknown", "confirmed_unfilled"))
        if not (all(type(x) is int for x in (n,d,u,missed)) and 0 <= n <= d
                and u >= 0 and missed >= 0 and n+u+missed == d and d > 0):
            errors.append("invalid_integer_counts")
    valid = not errors
    n = sum(r.get("N", 0) for r in rounds if type(r.get("N")) is int)
    d = sum(r.get("E", 0) for r in rounds if type(r.get("E")) is int)
    return {"status": "valid" if valid else "Invalid", "errors": sorted(set(errors)),
            "batch_id": registration.get("batch_id"), "started_rounds": len(starts),
            "registered_rounds": registration.get("planned_rounds"), "N": n, "E": d,
            "qualified": valid, "acceptance_pass": False, "hard_pass": False,
            "arithmetic_pass": valid and all(10*r["N"] > 9*r["E"] for r in rounds),
            "optimization_pass": False, "optimization_arithmetic_pass": valid and 20*n >= 19*d,
            "weighted_rate": n/d if valid else None,
            "minimum_rate": min(r["N"]/r["E"] for r in rounds) if valid else None,
            "full_fill_rounds": sum(r["N"] == r["E"] for r in rounds) if valid else 0,
            "Unknown": sum(r.get("Unknown", 0) for r in rounds if type(r.get("Unknown")) is int),
            "rounds": rounds}


def verify_batch(folder):
    from bv_live import verify_round,CONTROL,Budget
    folder = Path(folder).resolve()
    try:
        registration = json.loads((folder/"registration.json").read_text(encoding="utf-8"))
        starts = [json.loads(line) for line in (folder/"starts.jsonl").read_text(encoding="utf-8").splitlines()]
        if folder.parent!=CONTROL.resolve() or folder.name!=registration['batch_id']:
            raise ValueError('unregistered_batch_path')
        ledger=Budget().records()
        registered=[r for r in ledger if r['kind']=='batch_registered' and r['batch_id']==registration['batch_id']]
        launched=[r for r in ledger if r['kind']=='batch_round_start' and r['batch_id']==registration['batch_id']]
        if len(registered)!=1 or any(registered[0].get(k)!=v for k,v in registration.items()):
            raise ValueError('batch_registration_mismatch')
        if len(launched)!=len(starts) or any(any(l.get(k)!=v for k,v in s.items()) for l,s in zip(launched,starts)):
            raise ValueError('started_rounds_deleted_or_changed')
        rounds = []
        for start in starts:
            ref = (folder/start["frozen_ref"]).resolve()
            if folder not in ref.parents:
                raise ValueError("frozen_path_outside_batch")
            verified=verify_round(ref)
            verified['frozen_ref']=str(ref.relative_to(folder))
            settlement=json.loads((ref.parent/'settlement.json').read_text(encoding='utf-8'))
            if settlement.get('navigation_ready') is not True:
                verified.update(status='Insufficient evidence',evidence_valid=False)
            rounds.append(verified)
        result = check_batch(registration, starts, rounds)
        live = result["qualified"] and all(r.get("evidence_valid") is True for r in rounds)
        result.update(qualified=live, acceptance_pass=live and result["arithmetic_pass"],
                      hard_pass=live and result["arithmetic_pass"],
                      optimization_pass=live and result["optimization_arithmetic_pass"])
        if not live:
            result.update(status="Invalid", weighted_rate=None, minimum_rate=None)
            result["errors"] = sorted(set(result["errors"]+["live_source_verification_failed"]))
        return result
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"status":"Invalid", "qualified":False, "acceptance_pass":False,
                "hard_pass":False, "optimization_pass":False, "weighted_rate":None,
                "errors":["registered_batch_or_sources_unavailable",type(exc).__name__]}
