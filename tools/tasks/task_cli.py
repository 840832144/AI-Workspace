#!/usr/bin/env python3
"""Deterministic Task registry, allocation, and Candidate tooling.

The implementation intentionally uses only the Python standard library.  Task
Markdown remains canonical; TASK_REGISTRY.yaml is generated and byte-compared
to detect drift. Allocation reservations use atomically created remote Git refs
for cross-clone/Host exclusion, with token-gated local metadata for lifecycle
operations.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
import uuid
from typing import Iterable, Sequence


REGISTRY_SCHEMA_VERSION = "1.0"
POLICY = "global-task-id-with-project-key-and-optional-alias"
ACTIVE_STATUSES = {"draft", "ready", "in progress", "review", "changes requested"}
KNOWN_STATUSES = {
    "draft",
    "ready",
    "in progress",
    "review",
    "accepted",
    "changes requested",
    "cancelled",
    "complete",
}
CANONICAL_HEADING_RE = re.compile(r"^# (TASK-\d{4}) — (.+?)\s*$")
CANONICAL_FILE_RE = re.compile(r"^(TASK-\d{4})-(.+)\.md$")
CANDIDATE_HEADING_RE = re.compile(r"^# (CANDIDATE-\d{8}-[A-Z0-9-]+) — (.+?)\s*$")
CANDIDATE_FILE_RE = re.compile(r"^(CANDIDATE-\d{8}-[A-Z0-9-]+)\.md$")
TASK_ID_RE = re.compile(r"TASK-\d{4}")
FIELD_RE = re.compile(r"^- ([A-Za-z][A-Za-z0-9 _/-]*?):\s*(.*?)\s*$")
SECTION_RE = re.compile(r"^## (.+?)\s*$")
SAFE_SLUG_RE = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")
RESERVATION_REF_PREFIX = "refs/heads/task-reservations/"
# Audited pre-policy canonicals that may omit Project key. No future ID may be
# added implicitly; changing this map is a governance change subject to review.
LEGACY_PROJECT_KEYS = {
    "TASK-0014": "WORKSPACE",
    "TASK-0015": "HUUUGE",
    "TASK-0016": "WORKSPACE",
    "TASK-0017": "WORKSPACE",
    "TASK-0018": "HUUUGE",
    "TASK-0019": "WORKSPACE",
}


class TaskError(RuntimeError):
    """A fail-closed validation or allocation error."""


@dataclasses.dataclass(frozen=True)
class Record:
    id: str
    canonical_file: str
    file: str
    title: str
    status: str
    project_key: str
    human_alias: str
    owner: str
    executor: str
    priority: str
    created_date: str
    updated_date: str
    related_tasks: tuple[str, ...]
    kind: str
    goal: str

    def registry_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "canonical_file": self.canonical_file,
            "file": self.file,
            "title": self.title,
            "status": self.status,
            "project_key": self.project_key,
            "human_alias": self.human_alias,
            "owner": self.owner,
            "executor": self.executor,
            "priority": self.priority,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "related_tasks": list(self.related_tasks),
            "kind": self.kind,
        }


@dataclasses.dataclass
class ScanResult:
    records: list[Record]
    errors: list[str]
    warnings: list[str]

    @property
    def canonical(self) -> list[Record]:
        return [record for record in self.records if record.kind == "canonical"]


@dataclasses.dataclass(frozen=True)
class Reservation:
    task_id: str
    token: str
    path: Path
    remote_ref: str
    oid: str


def emit(status: str, **values: object) -> None:
    print(json.dumps({"status": status, **values}, ensure_ascii=False, sort_keys=True))


def normalize_field_name(value: str) -> str:
    return re.sub(r"[-_/ ]+", "-", value.strip().lower())


def parse_document(path: Path) -> tuple[str, dict[str, str], dict[str, str], str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise TaskError(f"cannot read UTF-8 Markdown: {path.name}: {type(exc).__name__}") from exc
    if "\x00" in text:
        raise TaskError(f"NUL byte is not allowed: {path.name}")
    lines = text.splitlines()
    heading = next((line.strip() for line in lines if line.strip()), "")
    fields: dict[str, str] = {}
    for line in lines:
        match = FIELD_RE.match(line)
        if match:
            key = normalize_field_name(match.group(1))
            fields.setdefault(key, match.group(2).strip())
    sections: dict[str, list[str]] = {}
    current = ""
    for line in lines:
        match = SECTION_RE.match(line)
        if match:
            current = normalize_field_name(match.group(1))
            sections.setdefault(current, [])
        elif current:
            sections[current].append(line)
    compact_sections = {key: "\n".join(value).strip() for key, value in sections.items()}
    return heading, fields, compact_sections, text


def clean_markdown(value: str) -> str:
    value = re.sub(r"[`*_]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_status(value: str) -> str:
    value = clean_markdown(value)
    if " / " in value:
        return value.split(" / ", 1)[0].strip()
    return value


def infer_project_key(title: str, fields: dict[str, str], path: Path) -> tuple[str, str]:
    """Best-effort classification for non-canonical records only."""
    explicit = clean_markdown(fields.get("project-key", "")).strip().upper()
    if explicit:
        return explicit, "explicit"
    corpus = " ".join(
        [title, path.name, fields.get("target-game", ""), fields.get("implementation-source", "")]
    ).lower()
    if "cash frenzy" in corpus:
        return "CASH-FRENZY", "legacy-inference"
    if "huuuge" in corpus or "lottery" in corpus:
        return "HUUUGE", "legacy-inference"
    return "WORKSPACE", "legacy-default"


def canonical_project_key(
    task_id: str, fields: dict[str, str], relative: str
) -> tuple[str, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    raw = clean_markdown(fields.get("project-key", "")).strip()
    if raw:
        if raw != raw.upper() or not SAFE_SLUG_RE.fullmatch(raw):
            errors.append(
                f"{relative}: Project key must use uppercase A-Z, 0-9, and single hyphens"
            )
        return raw.upper(), errors, warnings
    grandfathered = LEGACY_PROJECT_KEYS.get(task_id)
    if grandfathered:
        warnings.append(
            f"{relative}: project_key={grandfathered} supplied by audited legacy grandfather map"
        )
        return grandfathered, errors, warnings
    errors.append(f"{relative}: missing '- Project key:' field")
    return "", errors, warnings


def extract_related(text: str, own_id: str) -> tuple[str, ...]:
    return tuple(sorted({match for match in TASK_ID_RE.findall(text) if match != own_id}))


def section_value(sections: dict[str, str], *names: str) -> str:
    for name in names:
        value = sections.get(normalize_field_name(name), "")
        if value:
            return clean_markdown(value.splitlines()[0])
    return ""


def canonical_reference(fields: dict[str, str]) -> str:
    raw = fields.get("canonical-task", "") or fields.get("canonical-design", "")
    match = re.search(r"(?:tasks/)?(TASK-\d{4}[^`)\s]*\.md)", raw)
    if match:
        return "tasks/" + Path(match.group(1)).name
    match = TASK_ID_RE.search(raw)
    return match.group(0) if match else ""


def parse_root_task(path: Path, root: Path) -> tuple[Record | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    heading, fields, sections, text = parse_document(path)
    relative = path.relative_to(root).as_posix()
    file_match = CANONICAL_FILE_RE.match(path.name)
    if not file_match:
        errors.append(f"{relative}: TASK file name must match TASK-NNNN-<slug>.md")
        return None, errors, warnings
    filename_id = file_match.group(1)
    heading_match = CANONICAL_HEADING_RE.match(heading)
    explicit_kind = clean_markdown(fields.get("kind", "")).lower()
    if explicit_kind and explicit_kind not in {"canonical", "companion"}:
        errors.append(f"{relative}: root Task Kind must be canonical or companion")
        return None, errors, warnings
    # A root Task is canonical by default. Companion classification must be
    # explicit so malformed canonical headings cannot silently escape checks.
    kind = explicit_kind or "canonical"
    if kind == "canonical":
        if not heading_match:
            errors.append(f"{relative}: canonical heading must be '# TASK-NNNN — Title'")
            return None, errors, warnings
        heading_id, title = heading_match.groups()
        if filename_id != heading_id:
            errors.append(f"{relative}: filename ID {filename_id} does not match heading ID {heading_id}")
        task_id = heading_id
        required_fields = ("status", "owner", "executor", "priority", "date")
        for field in required_fields:
            if not fields.get(field, "").strip():
                errors.append(f"{relative}: missing '- {field.replace('-', ' ').title()}:' field")
        if not section_value(sections, "goal"):
            errors.append(f"{relative}: missing non-empty Goal section")
        raw_status = fields.get("status", "")
        status = normalize_status(raw_status)
        if status.lower() not in KNOWN_STATUSES:
            errors.append(f"{relative}: unsupported status '{clean_markdown(raw_status)}'")
        canonical_file = relative
        project_key, key_errors, key_warnings = canonical_project_key(task_id, fields, relative)
        errors.extend(key_errors)
        warnings.extend(key_warnings)
    else:
        task_id = filename_id
        title = heading.removeprefix("# ").strip() or path.stem
        status = normalize_status(fields.get("status", "Companion"))
        canonical_file = canonical_reference(fields)
        if not canonical_file:
            errors.append(f"{relative}: companion must declare Canonical task/design")
        project_key, _ = infer_project_key(title, fields, path)
    goal = section_value(sections, "goal", "decision", "context")
    created = fields.get("created", "") or fields.get("date", "")
    updated = fields.get("updated", "") or created
    record = Record(
        id=task_id,
        canonical_file=canonical_file,
        file=relative,
        title=clean_markdown(title),
        status=status,
        project_key=project_key,
        human_alias=clean_markdown(fields.get("human-alias", "")),
        owner=clean_markdown(fields.get("owner", "")),
        executor=clean_markdown(fields.get("executor", "")),
        priority=clean_markdown(fields.get("priority", "")),
        created_date=clean_markdown(created),
        updated_date=clean_markdown(updated),
        related_tasks=extract_related(text, task_id),
        kind=kind,
        goal=goal,
    )
    return record, errors, warnings


def parse_candidate(path: Path, root: Path) -> tuple[Record | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    heading, fields, sections, text = parse_document(path)
    relative = path.relative_to(root).as_posix()
    filename_match = CANDIDATE_FILE_RE.match(path.name)
    heading_match = CANDIDATE_HEADING_RE.match(heading)
    if not filename_match:
        errors.append(f"{relative}: Candidate filename must be CANDIDATE-YYYYMMDD-<PROJECT>-<SLUG>.md")
        return None, errors, warnings
    if not heading_match:
        errors.append(f"{relative}: Candidate heading must match '# CANDIDATE-... — Title'")
        return None, errors, warnings
    candidate_id, title = heading_match.groups()
    if candidate_id != filename_match.group(1):
        errors.append(f"{relative}: Candidate filename and heading ID differ")
    if clean_markdown(fields.get("kind", "candidate")).lower() != "candidate":
        errors.append(f"{relative}: Candidate Kind must be candidate")
    for field in ("status", "project-key", "suggested-priority", "user-decision", "source", "created"):
        if not fields.get(field, "").strip():
            errors.append(f"{relative}: missing Candidate field '{field}'")
    goal = section_value(sections, "goal")
    if not goal:
        errors.append(f"{relative}: missing non-empty Goal section")
    status = normalize_status(fields.get("status", "Candidate"))
    migrated_to = fields.get("migrated-to", "")
    related = extract_related(text, "")
    canonical_file = ""
    if migrated_to:
        target_match = TASK_ID_RE.search(migrated_to)
        if not target_match:
            errors.append(f"{relative}: Migrated to must reference TASK-NNNN")
        else:
            related = tuple(sorted(set(related) | {target_match.group(0)}))
    project_key = clean_markdown(fields.get("project-key", "")).strip().upper()
    if not SAFE_SLUG_RE.fullmatch(project_key):
        errors.append(f"{relative}: Candidate Project key is invalid")
    record = Record(
        id=candidate_id,
        canonical_file=canonical_file,
        file=relative,
        title=clean_markdown(title),
        status=status,
        project_key=project_key,
        human_alias=clean_markdown(fields.get("human-alias", "")),
        owner=clean_markdown(fields.get("owner", "User / ChatGPT")),
        executor=clean_markdown(fields.get("executor", "none")),
        priority=clean_markdown(fields.get("suggested-priority", "")),
        created_date=clean_markdown(fields.get("created", "")),
        updated_date=clean_markdown(fields.get("updated", "") or fields.get("created", "")),
        related_tasks=related,
        kind="candidate",
        goal=goal,
    )
    return record, errors, warnings


def parse_review(path: Path, root: Path, canonical_by_id: dict[str, str]) -> tuple[Record, list[str], list[str]]:
    heading, fields, sections, text = parse_document(path)
    relative = path.relative_to(root).as_posix()
    match = TASK_ID_RE.search(path.name) or TASK_ID_RE.search(heading)
    task_id = match.group(0) if match else ""
    errors = [] if task_id else [f"{relative}: Review must reference TASK-NNNN"]
    project_key, _ = infer_project_key(heading, fields, path)
    return Record(
        id=task_id,
        canonical_file=canonical_by_id.get(task_id, ""),
        file=relative,
        title=clean_markdown(heading.removeprefix("# ")),
        status=clean_markdown(fields.get("decision", "") or fields.get("result", "Review")),
        project_key=project_key,
        human_alias="",
        owner=clean_markdown(fields.get("reviewer", "ChatGPT")),
        executor="none",
        priority="",
        created_date=clean_markdown(fields.get("review-date", "") or fields.get("date", "")),
        updated_date=clean_markdown(fields.get("review-date", "") or fields.get("date", "")),
        related_tasks=extract_related(text, task_id),
        kind="review",
        goal=section_value(sections, "required fixes", "passed", "context"),
    ), errors, []


def scan_repository(root: Path) -> ScanResult:
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        return ScanResult([], ["tasks directory is missing"], [])
    records: list[Record] = []
    errors: list[str] = []
    warnings: list[str] = []
    try:
        root_task_files = sorted(tasks_dir.glob("TASK-*.md"))
        candidate_dir = tasks_dir / "candidates"
        candidate_files = sorted(candidate_dir.glob("*.md")) if candidate_dir.exists() else []
    except OSError as exc:
        return ScanResult([], [f"cannot enumerate complete tasks directory: {exc}"], [])
    for path in root_task_files:
        try:
            record, item_errors, item_warnings = parse_root_task(path, root)
        except TaskError as exc:
            record, item_errors, item_warnings = None, [str(exc)], []
        if record:
            records.append(record)
        errors.extend(item_errors)
        warnings.extend(item_warnings)
    for path in candidate_files:
        if path.name.lower() == "readme.md":
            continue
        try:
            record, item_errors, item_warnings = parse_candidate(path, root)
        except TaskError as exc:
            record, item_errors, item_warnings = None, [str(exc)], []
        if record:
            records.append(record)
        errors.extend(item_errors)
        warnings.extend(item_warnings)
    canonical_records = [record for record in records if record.kind == "canonical"]
    canonical_by_id = {record.id: record.file for record in canonical_records}
    canonical_record_by_id = {record.id: record for record in canonical_records}
    canonical_record_by_file = {record.file: record for record in canonical_records}
    normalized_records: list[Record] = []
    for record in records:
        if record.kind != "companion":
            normalized_records.append(record)
            continue
        target = (
            canonical_record_by_file.get(record.canonical_file)
            if record.canonical_file.startswith("tasks/")
            else canonical_record_by_id.get(record.canonical_file)
        )
        if target is None:
            errors.append(
                f"{record.file}: companion canonical reference does not resolve to an existing canonical Task"
            )
            normalized_records.append(record)
            continue
        if record.id != target.id:
            errors.append(
                f"{record.file}: companion filename ID {record.id} does not match canonical ID {target.id}"
            )
        normalized_records.append(
            dataclasses.replace(
                record, canonical_file=target.file
            )
        )
    records = normalized_records
    reviews_dir = root / "reviews"
    if reviews_dir.exists():
        for path in sorted(reviews_dir.glob("TASK-*.md")):
            try:
                record, item_errors, item_warnings = parse_review(path, root, canonical_by_id)
                records.append(record)
                errors.extend(item_errors)
                warnings.extend(item_warnings)
            except TaskError as exc:
                errors.append(str(exc))
    canonical_ids: dict[str, list[str]] = {}
    for record in records:
        if record.kind == "canonical":
            canonical_ids.setdefault(record.id, []).append(record.file)
    for task_id, paths in sorted(canonical_ids.items()):
        if len(paths) > 1:
            errors.append(f"duplicate canonical ID {task_id}: {', '.join(paths)}")
    records.sort(key=lambda item: (item.kind, item.id, item.file))
    return ScanResult(records, errors, warnings)


def yaml_string(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_registry(result: ScanResult) -> str:
    lines = [
        f"schema_version: {yaml_string(REGISTRY_SCHEMA_VERSION)}",
        'generated_from: "tasks Markdown; do not edit this Registry by hand"',
        f"policy: {yaml_string(POLICY)}",
        "entries:",
    ]
    for record in result.records:
        item = record.registry_dict()
        lines.append(f"  - id: {yaml_string(item['id'])}")
        for key in (
            "canonical_file", "file", "title", "status", "project_key", "human_alias",
            "owner", "executor", "priority", "created_date", "updated_date",
        ):
            lines.append(f"    {key}: {yaml_string(item[key])}")
        lines.append(f"    related_tasks: {json.dumps(item['related_tasks'], ensure_ascii=False)}")
        lines.append(f"    kind: {yaml_string(item['kind'])}")
    return "\n".join(lines) + "\n"


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run_git(
    root: Path,
    arguments: Sequence[str],
    check: bool = True,
    *,
    input_text: str | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    if extra_env:
        environment.update(extra_env)
    process = subprocess.run(
        ["git", *arguments], cwd=root, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=input_text, env=environment,
    )
    if check and process.returncode:
        raise TaskError(f"git {' '.join(arguments)} failed")
    return process


def is_git_repository(root: Path) -> bool:
    return run_git(root, ["rev-parse", "--is-inside-work-tree"], check=False).stdout.strip() == "true"


def ensure_git_latest(
    root: Path, *, require_linked_worktree: bool = False, require_write_branch: bool = False
) -> dict[str, str]:
    if not is_git_repository(root):
        raise TaskError("allocation requires a Git worktree")
    branch = run_git(root, ["branch", "--show-current"]).stdout.strip()
    if require_write_branch and (not branch or branch in {"main", "master"}):
        raise TaskError("allocation writes require a non-main branch")
    common_dir = Path(run_git(root, ["rev-parse", "--path-format=absolute", "--git-common-dir"]).stdout.strip()).resolve()
    git_dir = Path(run_git(root, ["rev-parse", "--path-format=absolute", "--git-dir"]).stdout.strip()).resolve()
    if require_linked_worktree and common_dir == git_dir:
        raise TaskError("allocation writes require an independent linked worktree")
    origin = run_git(root, ["remote", "get-url", "origin"], check=False)
    if origin.returncode:
        raise TaskError("origin remote is required to prove latest main")
    fetched = run_git(root, ["fetch", "--quiet", "origin", "main"], check=False)
    if fetched.returncode:
        raise TaskError("cannot fetch origin/main; latest state is unproven")
    remote_ref = run_git(root, ["rev-parse", "--verify", "origin/main"], check=False)
    if remote_ref.returncode:
        raise TaskError("origin/main is unavailable")
    ancestor = run_git(root, ["merge-base", "--is-ancestor", "origin/main", "HEAD"], check=False)
    if ancestor.returncode:
        raise TaskError("current branch does not contain latest origin/main")
    return {"branch": branch, "head": run_git(root, ["rev-parse", "HEAD"]).stdout.strip(), "common_dir": str(common_dir)}


class AllocationLock:
    def __init__(self, common_dir: Path, timeout_seconds: float = 5.0):
        self.path = common_dir / "ai-workspace-task-allocator" / "allocation.lock"
        self.timeout_seconds = timeout_seconds
        self.acquired = False

    def __enter__(self) -> "AllocationLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.timeout_seconds
        payload = json.dumps({"pid": os.getpid(), "created_at": utc_now()}) + "\n"
        while True:
            try:
                descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    handle.write(payload)
                self.acquired = True
                return self
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise TaskError("task allocation lock is busy")
                time.sleep(0.05)

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.acquired:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def reservation_dir(common_dir: Path) -> Path:
    return common_dir / "ai-workspace-task-allocator" / "reservations"


def reserved_ids(common_dir: Path) -> set[str]:
    directory = reservation_dir(common_dir)
    if not directory.exists():
        return set()
    return {path.stem for path in directory.glob("TASK-*.json") if re.fullmatch(r"TASK-\d{4}", path.stem)}


def remote_reservations(root: Path) -> dict[str, str]:
    result = run_git(
        root,
        ["ls-remote", "--heads", "origin", f"{RESERVATION_REF_PREFIX}TASK-*"],
        check=False,
    )
    if result.returncode:
        raise TaskError("cannot inspect remote allocation reservations")
    reservations: dict[str, str] = {}
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) != 2 or not parts[1].startswith(RESERVATION_REF_PREFIX):
            continue
        task_id = parts[1].removeprefix(RESERVATION_REF_PREFIX)
        if re.fullmatch(r"TASK-\d{4}", task_id):
            reservations[task_id] = parts[0]
    return reservations


def next_available_id(records: Iterable[Record], reservations: set[str]) -> str:
    occupied = {record.id for record in records if record.kind == "canonical"} | reservations
    numeric = sorted(int(value.split("-", 1)[1]) for value in occupied if re.fullmatch(r"TASK-\d{4}", value))
    candidate = (numeric[-1] + 1) if numeric else 1
    while f"TASK-{candidate:04d}" in occupied:
        candidate += 1
    if candidate > 9999:
        raise TaskError("TASK namespace exhausted")
    return f"TASK-{candidate:04d}"


def reserve_next_id(
    root: Path,
    common_dir: Path,
    records: Iterable[Record],
    head: str,
    purpose: str,
) -> Reservation:
    occupied = reserved_ids(common_dir) | set(remote_reservations(root))
    for _ in range(32):
        task_id = next_available_id(records, occupied)
        try:
            return create_reservation(root, common_dir, task_id, head, purpose)
        except TaskError as exc:
            if "remote allocation reservation conflict" not in str(exc):
                raise
            occupied.add(task_id)
    raise TaskError("remote allocation contention did not stabilize")


def reservation_commit(root: Path, task_id: str, head: str, purpose: str, token: str) -> str:
    tree = run_git(root, ["rev-parse", f"{head}^{{tree}}"]).stdout.strip()
    timestamp = utc_now()
    message = json.dumps(
        {
            "schema_version": REGISTRY_SCHEMA_VERSION,
            "task_id": task_id,
            "token_sha256": hashlib.sha256(token.encode("ascii")).hexdigest(),
            "head": head,
            "purpose": purpose,
            "created_at": timestamp,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    identity = {
        "GIT_AUTHOR_NAME": "AI-Workspace Task Allocator",
        "GIT_AUTHOR_EMAIL": "allocator@local.invalid",
        "GIT_COMMITTER_NAME": "AI-Workspace Task Allocator",
        "GIT_COMMITTER_EMAIL": "allocator@local.invalid",
    }
    result = run_git(
        root,
        ["commit-tree", tree, "-p", head],
        input_text=message + "\n",
        extra_env=identity,
    )
    return result.stdout.strip()


def create_reservation(
    root: Path, common_dir: Path, task_id: str, head: str, purpose: str
) -> Reservation:
    token = uuid.uuid4().hex
    path = reservation_dir(common_dir) / f"{task_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    remote_ref = f"{RESERVATION_REF_PREFIX}{task_id}"
    oid = reservation_commit(root, task_id, head, purpose, token)
    pushed = run_git(
        root,
        ["push", f"--force-with-lease={remote_ref}:", "origin", f"{oid}:{remote_ref}"],
        check=False,
    )
    if pushed.returncode:
        raise TaskError(f"remote allocation reservation conflict for {task_id}")
    payload = {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "task_id": task_id,
        "token_sha256": hashlib.sha256(token.encode("ascii")).hexdigest(),
        "head": head,
        "purpose": purpose,
        "created_at": utc_now(),
        "remote_ref": remote_ref,
        "reservation_oid": oid,
        "state": "pending-main",
    }
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        delete_remote_reservation(root, remote_ref, oid)
        raise TaskError(f"allocation reservation already exists for {task_id}") from exc
    try:
        if os.environ.get("AI_WORKSPACE_TASK_FAULT_INJECTION") == "after-remote-reservation":
            if not (root / ".task-test-allow-faults").exists():
                raise TaskError("fault injection is restricted to marked disposable test fixtures")
            raise TaskError("injected failure after remote reservation")
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        path.unlink(missing_ok=True)
        delete_remote_reservation(root, remote_ref, oid)
        raise
    return Reservation(task_id, token, path, remote_ref, oid)


def read_reservation(path: Path, token: str) -> dict[str, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise TaskError(f"cannot read reservation {path.name}: {exc}") from exc
    expected = payload.get("token_sha256", "")
    actual = hashlib.sha256(token.encode("ascii")).hexdigest()
    if not expected or actual != expected:
        raise TaskError("reservation token does not match")
    required = ("task_id", "remote_ref", "reservation_oid")
    if any(not isinstance(payload.get(key), str) or not payload[key] for key in required):
        raise TaskError("reservation metadata is incomplete")
    return payload


def delete_remote_reservation(root: Path, remote_ref: str, expected_oid: str) -> None:
    observed = run_git(root, ["ls-remote", "origin", remote_ref], check=False)
    if observed.returncode:
        raise TaskError("cannot verify remote allocation reservation")
    lines = [line.split() for line in observed.stdout.splitlines() if line.strip()]
    if len(lines) != 1 or lines[0][0] != expected_oid:
        raise TaskError("remote allocation reservation ownership changed or is missing")
    deleted = run_git(
        root,
        [
            "push",
            f"--force-with-lease={remote_ref}:{expected_oid}",
            "origin",
            f":{remote_ref}",
        ],
        check=False,
    )
    if deleted.returncode:
        raise TaskError("remote allocation reservation changed; refusing deletion")


def release_reservation(root: Path, path: Path, token: str) -> dict[str, str]:
    payload = read_reservation(path, token)
    delete_remote_reservation(root, payload["remote_ref"], payload["reservation_oid"])
    path.unlink()
    return payload


def origin_main_canonical(root: Path, task_id: str) -> tuple[str, str] | None:
    listing = run_git(
        root,
        ["ls-tree", "-r", "--name-only", "origin/main", "--", "tasks"],
        check=False,
    )
    if listing.returncode:
        raise TaskError("cannot inspect canonical Tasks in origin/main")
    candidates = [
        item
        for item in listing.stdout.splitlines()
        if re.fullmatch(rf"tasks/{re.escape(task_id)}-.+\.md", item)
    ]
    canonicals: list[tuple[str, str]] = []
    for relative in candidates:
        shown = run_git(root, ["show", f"origin/main:{relative}"], check=False)
        if shown.returncode:
            raise TaskError(f"cannot read {relative} from origin/main")
        lines = shown.stdout.splitlines()
        heading = next((line.strip() for line in lines if line.strip()), "")
        heading_match = CANONICAL_HEADING_RE.match(heading)
        fields: dict[str, str] = {}
        for line in lines:
            match = FIELD_RE.match(line)
            if match:
                fields.setdefault(normalize_field_name(match.group(1)), match.group(2).strip())
        explicit_kind = clean_markdown(fields.get("kind", "")).lower()
        if heading_match and heading_match.group(1) == task_id and explicit_kind != "companion":
            project_key, errors, _ = canonical_project_key(task_id, fields, relative)
            if errors:
                raise TaskError("origin/main canonical is invalid: " + "; ".join(errors))
            canonicals.append((relative, project_key))
    if len(canonicals) > 1:
        raise TaskError(f"origin/main contains duplicate canonical ID {task_id}")
    return canonicals[0] if canonicals else None


def local_has_canonical(result: ScanResult, task_id: str) -> bool:
    return any(record.kind == "canonical" and record.id == task_id for record in result.records)


def validate_result(root: Path, result: ScanResult, *, check_git: bool) -> tuple[list[str], list[str], dict[str, str] | None]:
    errors = list(result.errors)
    warnings = list(result.warnings)
    registry_path = root / "tasks" / "TASK_REGISTRY.yaml"
    expected = render_registry(result)
    if not registry_path.exists():
        errors.append("tasks/TASK_REGISTRY.yaml is missing; run scan --write-registry")
    else:
        try:
            actual = registry_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read tasks/TASK_REGISTRY.yaml: {exc}")
        else:
            if actual != expected:
                errors.append("tasks/TASK_REGISTRY.yaml drift detected; rebuild from Task Markdown")
    git_state: dict[str, str] | None = None
    if check_git:
        try:
            git_state = ensure_git_latest(root)
        except TaskError as exc:
            errors.append(str(exc))
    return errors, warnings, git_state


def normalized_goal(value: str) -> set[str]:
    value = unicodedata.normalize("NFKC", value).lower()
    return {token for token in re.findall(r"[\w\u3400-\u9fff]+", value) if len(token) > 1}


def overlap_records(candidate: Record, records: Iterable[Record]) -> list[tuple[Record, float]]:
    candidate_tokens = normalized_goal(candidate.title + " " + candidate.goal)
    overlaps: list[tuple[Record, float]] = []
    if not candidate_tokens:
        return overlaps
    for record in records:
        if record.kind != "canonical" or record.status.lower() not in ACTIVE_STATUSES:
            continue
        other = normalized_goal(record.title + " " + record.goal)
        if not other:
            continue
        score = len(candidate_tokens & other) / len(candidate_tokens | other)
        if score >= 0.60:
            overlaps.append((record, score))
    return sorted(overlaps, key=lambda pair: (-pair[1], pair[0].id))


def approved_decision(value: str) -> bool:
    normalized = clean_markdown(value).lower()
    return normalized in {"approved", "confirmed", "user approved", "user confirmed", "已批准", "已确认"}


def candidate_template(candidate_id: str, title: str, project_key: str, priority: str, user_decision: str, source: str, goal: str, dependencies: str, risks: str) -> str:
    today = dt.date.today().isoformat()
    return f"""# {candidate_id} — {title}

- Kind: candidate
- Status: Candidate
- Project key: {project_key}
- Suggested priority: {priority}
- User decision: {user_decision}
- Source: {source}
- Created: {today}
- Updated: {today}
- Migrated to:
- Migrated at:

## Goal

{goal}

## Dependencies

{dependencies}

## Risks

{risks}

## Promotion Gate

- Candidate 不是可执行入口，也不占用 `TASK-XXXX`。
- 只有 User 明确批准后，才可通过 allocator 完整校验并晋升。
- 晋升前必须检查相关 active Task、最新 `origin/main` 和分配锁。
"""


def replace_field(text: str, name: str, value: str) -> str:
    pattern = re.compile(rf"^- {re.escape(name)}:[ \t]*.*$", re.M)
    replacement = f"- {name}: {value}"
    if not pattern.search(text):
        raise TaskError(f"Candidate missing field '{name}'")
    return pattern.sub(lambda _: replacement, text, count=1)


def render_promoted_task(candidate: Record, candidate_path: Path, candidate_text: str, task_id: str, relationship: str, related_task: str) -> str:
    heading, fields, sections, _ = parse_document(candidate_path)
    today = dt.date.today().isoformat()
    title = candidate.title
    related = sorted(set(candidate.related_tasks) | ({related_task} if related_task else set()))
    related_line = ", ".join(related) if related else "none"
    relationship_line = relationship if relationship else "new"
    original_sections = "\n\n".join(
        f"## {name}\n\n{content}" for name, content in (
            ("Goal", sections.get("goal", "")),
            ("Scope", sections.get("scope", "To be refined during Task review.")),
            ("Non-goals", sections.get("non-goals", "Do not expand beyond the approved Candidate.")),
            ("Deliverables", sections.get("deliverables", "Deliver the approved Candidate outcome with evidence.")),
            ("Safety", sections.get("safety", sections.get("safety-and-data-boundaries", "Follow repository and project safety rules."))),
            ("Validation", sections.get("validation", "Run deterministic validation and record evidence.")),
            ("Handoff", sections.get("handoff-required", "Update Task, CHANGELOG, and handoff/CODEX.md; commit and push for Review.")),
        )
    )
    return f"""# {task_id} — {title}

- Status: Ready
- Project key: {candidate.project_key}
- Human alias: {candidate.human_alias}
- Owner: {candidate.owner or 'User / ChatGPT'}
- Executor: Codex
- Priority: {candidate.priority}
- Date: {today}
- Updated: {today}
- Candidate provenance: `{candidate.file}`
- Allocation relationship: {relationship_line}
- Related tasks: {related_line}

{original_sections}
"""


def scan_command(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    result = scan_repository(root)
    if args.write_registry:
        if result.errors:
            emit("failed", errors=result.errors, warnings=result.warnings)
            return 1
        try:
            git_state = ensure_git_latest(root, require_linked_worktree=True, require_write_branch=True)
        except TaskError as exc:
            emit("failed", errors=[str(exc)], warnings=result.warnings)
            return 1
        atomic_write_text(root / "tasks" / "TASK_REGISTRY.yaml", render_registry(result))
    emit(
        "scanned" if not result.errors else "failed",
        canonical_count=len(result.canonical),
        collision_count=sum(1 for error in result.errors if error.startswith("duplicate canonical ID")),
        records=[record.registry_dict() for record in result.records],
        errors=result.errors,
        warnings=result.warnings,
        registry_written=bool(args.write_registry and not result.errors),
    )
    return 1 if result.errors else 0


def validate_command(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    result = scan_repository(root)
    bypass_allowed = args.no_git_check and (root / ".task-test-fixture").exists()
    errors, warnings, git_state = validate_result(root, result, check_git=not bypass_allowed)
    if args.no_git_check and not bypass_allowed:
        errors.append("--no-git-check is restricted to marked disposable test fixtures")
    public_git_state = None
    if git_state:
        public_git_state = {key: git_state[key] for key in ("branch", "head")}
    emit(
        "valid" if not errors else "failed",
        canonical_count=len(result.canonical), collision_count=sum("duplicate canonical ID" in item for item in errors),
        errors=errors, warnings=warnings, git=public_git_state,
    )
    return 1 if errors else 0


def next_command(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    result = scan_repository(root)
    errors, warnings, _ = validate_result(root, result, check_git=False)
    try:
        git_state = ensure_git_latest(
            root, require_linked_worktree=True, require_write_branch=True
        )
    except TaskError as exc:
        errors.append(str(exc))
        git_state = None
    if errors or git_state is None:
        emit("failed", errors=errors, warnings=warnings)
        return 1
    try:
        common_dir = Path(git_state["common_dir"])
        with AllocationLock(common_dir, args.lock_timeout):
            reservation = reserve_next_id(
                root, common_dir, result.records, git_state["head"], args.purpose
            )
        emit(
            "reserved",
            task_id=reservation.task_id,
            reservation_token=reservation.token,
            reservation_state="pending-main",
            branch=git_state["branch"],
            warnings=warnings,
        )
        return 0
    except TaskError as exc:
        emit("failed", errors=[str(exc)], warnings=warnings)
        return 1


def release_command(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    try:
        git_state = ensure_git_latest(
            root, require_linked_worktree=True, require_write_branch=True
        )
        common_dir = Path(git_state["common_dir"])
        path = reservation_dir(common_dir) / f"{args.id}.json"
        payload = read_reservation(path, args.token)
        if payload["task_id"] != args.id:
            raise TaskError("reservation metadata task ID does not match")
        result = scan_repository(root)
        errors, _, _ = validate_result(root, result, check_git=False)
        if errors:
            raise TaskError("cannot abandon while Task state is invalid: " + "; ".join(errors))
        if local_has_canonical(result, args.id) or origin_main_canonical(root, args.id):
            raise TaskError(
                "reservation has a canonical Task; merge it to main and use finalize"
            )
        release_reservation(root, path, args.token)
        emit("released-abandoned", task_id=args.id)
        return 0
    except TaskError as exc:
        emit("failed", errors=[str(exc)])
        return 1


def finalize_command(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    try:
        git_state = ensure_git_latest(
            root, require_linked_worktree=True, require_write_branch=True
        )
        common_dir = Path(git_state["common_dir"])
        result = scan_repository(root)
        errors, _, _ = validate_result(root, result, check_git=False)
        if errors:
            raise TaskError("cannot finalize while Task state is invalid: " + "; ".join(errors))
        path = reservation_dir(common_dir) / f"{args.id}.json"
        payload = read_reservation(path, args.token)
        if payload["task_id"] != args.id:
            raise TaskError("reservation metadata task ID does not match")
        canonical = origin_main_canonical(root, args.id)
        if canonical is None:
            raise TaskError("canonical Task is not yet present in latest origin/main")
        release_reservation(root, path, args.token)
        emit(
            "finalized",
            task_id=args.id,
            canonical_file=canonical[0],
            project_key=canonical[1],
        )
        return 0
    except TaskError as exc:
        emit("failed", errors=[str(exc)])
        return 1


def candidate_command(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    try:
        git_state = ensure_git_latest(root, require_linked_worktree=True, require_write_branch=True)
        before = scan_repository(root)
        before_errors, _, _ = validate_result(root, before, check_git=False)
        if before_errors:
            raise TaskError("pre-create validation failed: " + "; ".join(before_errors))
        if not SAFE_SLUG_RE.fullmatch(args.project_key) or not SAFE_SLUG_RE.fullmatch(args.slug):
            raise TaskError("project-key and slug must use uppercase A-Z, 0-9, and single hyphens")
        date_value = args.date or dt.date.today().strftime("%Y%m%d")
        if not re.fullmatch(r"\d{8}", date_value):
            raise TaskError("Candidate date must be YYYYMMDD")
        candidate_id = f"CANDIDATE-{date_value}-{args.project_key}-{args.slug}"
        path = root / "tasks" / "candidates" / f"{candidate_id}.md"
        common_dir = Path(git_state["common_dir"])
        with AllocationLock(common_dir, args.lock_timeout):
            if path.exists():
                raise TaskError(f"Candidate already exists: {path.relative_to(root).as_posix()}")
            content = candidate_template(candidate_id, args.title, args.project_key, args.priority, args.user_decision, args.source, args.goal, args.dependencies, args.risks)
            atomic_write_text(path, content)
            rescanned = scan_repository(root)
            if rescanned.errors:
                path.unlink(missing_ok=True)
                raise TaskError("post-create validation failed: " + "; ".join(rescanned.errors))
            atomic_write_text(root / "tasks" / "TASK_REGISTRY.yaml", render_registry(rescanned))
        emit("candidate-created", candidate_id=candidate_id, file=path.relative_to(root).as_posix(), task_id_allocated=False)
        return 0
    except TaskError as exc:
        emit("failed", errors=[str(exc)])
        return 1


def promote_command(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    candidate_path = (root / args.candidate).resolve()
    if root not in candidate_path.parents:
        emit("failed", errors=["Candidate must be inside repository"])
        return 1
    snapshots: dict[Path, bytes | None] = {}
    reservation: Reservation | None = None
    try:
        git_state = ensure_git_latest(root, require_linked_worktree=True, require_write_branch=True)
        result = scan_repository(root)
        errors, warnings, _ = validate_result(root, result, check_git=False)
        if errors:
            raise TaskError("pre-promotion validation failed: " + "; ".join(errors))
        candidate = next((record for record in result.records if Path(record.file) == candidate_path.relative_to(root)), None)
        if candidate is None or candidate.kind != "candidate":
            raise TaskError("Candidate is not registered")
        heading, fields, sections, candidate_text = parse_document(candidate_path)
        if fields.get("migrated-to", "").strip():
            raise TaskError("Candidate is already migrated")
        if not approved_decision(fields.get("user-decision", "")):
            raise TaskError("Candidate User decision is not explicitly approved")
        overlaps = overlap_records(candidate, result.records)
        if overlaps:
            if args.relationship != "subtask" or not args.related_task:
                details = [f"{record.id}:{score:.2f}" for record, score in overlaps]
                raise TaskError("active Task overlap requires explicit subtask decision: " + ", ".join(details))
            if args.related_task not in {record.id for record, _ in overlaps}:
                raise TaskError("related-task must identify one of the overlapping active Tasks")
        elif args.relationship == "subtask" and not args.related_task:
            raise TaskError("subtask relationship requires --related-task")
        common_dir = Path(git_state["common_dir"])
        with AllocationLock(common_dir, args.lock_timeout):
            refreshed = scan_repository(root)
            refreshed_errors, _, _ = validate_result(root, refreshed, check_git=False)
            if refreshed_errors:
                raise TaskError("locked validation failed: " + "; ".join(refreshed_errors))
            reservation = reserve_next_id(
                root,
                common_dir,
                refreshed.records,
                git_state["head"],
                f"promote:{candidate.id}",
            )
            task_id = reservation.task_id
            slug = re.sub(r"[^A-Z0-9]+", "-", unicodedata.normalize("NFKD", candidate.title).upper()).strip("-")
            if not slug:
                slug = "PROMOTED-CANDIDATE"
            target = root / "tasks" / f"{task_id}-{slug[:80]}.md"
            registry = root / "tasks" / "TASK_REGISTRY.yaml"
            for path in (candidate_path, target, registry):
                snapshots[path] = path.read_bytes() if path.exists() else None
            atomic_write_text(target, render_promoted_task(candidate, candidate_path, candidate_text, task_id, args.relationship, args.related_task))
            updated_candidate = replace_field(candidate_text, "Status", "Migrated")
            updated_candidate = replace_field(updated_candidate, "Updated", dt.date.today().isoformat())
            updated_candidate = replace_field(updated_candidate, "Migrated to", f"{task_id} (`{target.relative_to(root).as_posix()}`)")
            updated_candidate = replace_field(updated_candidate, "Migrated at", utc_now())
            atomic_write_text(candidate_path, updated_candidate)
            post = scan_repository(root)
            if post.errors:
                raise TaskError("post-promotion scan failed: " + "; ".join(post.errors))
            atomic_write_text(registry, render_registry(post))
            final = scan_repository(root)
            final_errors, _, _ = validate_result(root, final, check_git=False)
            if final_errors:
                raise TaskError("post-promotion validation failed: " + "; ".join(final_errors))
        emit(
            "promoted",
            task_id=task_id,
            file=target.relative_to(root).as_posix(),
            candidate=candidate.file,
            reservation_token=reservation.token,
            reservation_state="pending-main",
            warnings=warnings,
        )
        return 0
    except (TaskError, OSError) as exc:
        for path, content in reversed(list(snapshots.items())):
            try:
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content)
            except OSError:
                pass
        if reservation is not None and reservation.path.exists():
            try:
                release_reservation(root, reservation.path, reservation.token)
            except (OSError, TaskError):
                pass
        message = str(exc) if isinstance(exc, TaskError) else f"filesystem operation failed: {type(exc).__name__}"
        emit("failed", errors=[message])
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI-Workspace Task Registry and allocator")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="enumerate and classify Task records")
    scan.add_argument("--write-registry", action="store_true", help="rebuild TASK_REGISTRY.yaml after a clean scan")
    scan.set_defaults(func=scan_command)

    validate = subparsers.add_parser("validate", help="fail on collisions, format errors, registry drift, or stale Git")
    validate.add_argument("--no-git-check", action="store_true", help=argparse.SUPPRESS)
    validate.set_defaults(func=validate_command)

    next_parser = subparsers.add_parser("next", help="validate, reserve, and return the next globally available ID")
    next_parser.add_argument("--purpose", default="manual-task-allocation")
    next_parser.add_argument("--lock-timeout", type=float, default=5.0)
    next_parser.set_defaults(func=next_command)

    release = subparsers.add_parser("release", help="release an unused allocation reservation")
    release.add_argument("--id", required=True, choices=[f"TASK-{value:04d}" for value in range(1, 10000)])
    release.add_argument("--token", required=True)
    release.set_defaults(func=release_command)

    finalize = subparsers.add_parser(
        "finalize", help="release a reservation only after its canonical Task is in origin/main"
    )
    finalize.add_argument("--id", required=True, choices=[f"TASK-{value:04d}" for value in range(1, 10000)])
    finalize.add_argument("--token", required=True)
    finalize.set_defaults(func=finalize_command)

    candidate = subparsers.add_parser("candidate", help="create a non-executable Candidate without allocating TASK-NNNN")
    candidate.add_argument("--title", required=True)
    candidate.add_argument("--project-key", required=True, type=str.upper)
    candidate.add_argument("--slug", required=True, type=str.upper)
    candidate.add_argument("--priority", default="P2 candidate")
    candidate.add_argument("--user-decision", default="Pending")
    candidate.add_argument("--source", required=True)
    candidate.add_argument("--goal", required=True)
    candidate.add_argument("--dependencies", default="None recorded.")
    candidate.add_argument("--risks", default="Must be reviewed before promotion.")
    candidate.add_argument("--date")
    candidate.add_argument("--lock-timeout", type=float, default=5.0)
    candidate.set_defaults(func=candidate_command)

    promote = subparsers.add_parser("promote", help="promote an approved Candidate through validated allocation")
    promote.add_argument("candidate", help="repository-relative Candidate path")
    promote.add_argument("--relationship", choices=("new", "subtask"), default="new")
    promote.add_argument("--related-task", default="")
    promote.add_argument("--lock-timeout", type=float, default=5.0)
    promote.set_defaults(func=promote_command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        emit("failed", errors=["interrupted"])
        return 130
    except Exception as exc:  # fail closed without a traceback or local filesystem details
        emit("failed", errors=[f"unexpected failure: {type(exc).__name__}"])
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
