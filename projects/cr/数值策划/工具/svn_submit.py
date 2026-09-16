"""安全地预检、添加、提交并核验 CR 数值资源库的 SVN 变更。"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from cr_tools.common import load_json, repository_root


DEFAULT_CONFIG = Path("数值策划/工具/config/svn_submit.json")
SVN_CANDIDATES = (
    Path(r"C:\Program Files\TortoiseSVN\bin\svn.exe"),
    Path(r"C:\Program Files\SlikSvn\bin\svn.exe"),
)
CONFLICT_ITEMS = {"conflicted", "obstructed", "incomplete"}
CHANGED_ITEMS = {
    "added",
    "conflicted",
    "deleted",
    "incomplete",
    "merged",
    "missing",
    "modified",
    "obstructed",
    "replaced",
    "unversioned",
}


@dataclass(frozen=True)
class StatusEntry:
    """一个 SVN 工作副本状态项。"""

    path: Path
    relative_path: str
    item: str
    properties: str
    tree_conflicted: bool


class SubmitError(RuntimeError):
    """可直接展示给使用者的安全提交错误。"""


def configure_console_encoding() -> None:
    """统一使用 UTF-8 输出，避免 Windows GBK 控制台损坏中文日志。"""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-m", "--message", help="SVN 提交说明；--execute 时必填。")
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="明确的公司 SVN 工作副本根目录；不得默认使用 Git 中的 CR 资料目录。",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="安全策略 JSON；默认使用仓库内的 svn_submit.json。",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="执行更新、添加和提交；不提供时仅做只读演练。",
    )
    parser.add_argument(
        "--allow-delete",
        action="store_true",
        help="明确允许提交已执行 svn delete 的文件；缺失但未登记删除仍会中止。",
    )
    parser.add_argument(
        "--skip-update",
        action="store_true",
        help="跳过提交前 svn update；仅用于已确认离线或网络受限的场景。",
    )
    return parser.parse_args()


def locate_svn() -> Path:
    """查找 SVN 命令行客户端，不依赖个人电脑路径配置。"""

    configured = os.environ.get("SVN_EXE")
    if configured:
        path = Path(configured).expanduser()
        if path.is_file():
            return path
        raise SubmitError(f"SVN_EXE 指向的文件不存在：{path}")

    discovered = shutil.which("svn")
    if discovered:
        return Path(discovered)

    for path in SVN_CANDIDATES:
        if path.is_file():
            return path
    raise SubmitError(
        "未找到 svn.exe。请安装 TortoiseSVN 的 command line client tools，"
        "或通过 SVN_EXE 环境变量指定客户端。"
    )


def run_command(
    command: Sequence[str],
    *,
    cwd: Path,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    """运行命令并保留 UTF-8 可解析的原始输出。"""

    environment = os.environ.copy()
    environment.setdefault("PYTHONIOENCODING", "utf-8")
    environment.setdefault("PYTHONUTF8", "1")
    result = subprocess.run(
        list(command),
        cwd=cwd,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        stdout = result.stdout.decode("utf-8", errors="replace").strip()
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        detail = stderr or stdout or f"退出码 {result.returncode}"
        raise SubmitError(f"命令执行失败：{' '.join(command[:2])}\n{detail}")
    return result


def svn_command(
    svn: Path,
    root: Path,
    *arguments: str,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    return run_command([str(svn), *arguments], cwd=root, check=check)


def ensure_working_copy(svn: Path, root: Path) -> None:
    result = svn_command(svn, root, "info", "--xml", str(root))
    try:
        document = ET.fromstring(result.stdout)
    except ET.ParseError as error:
        raise SubmitError(f"无法解析 svn info 输出：{error}") from error
    if document.find("entry") is None:
        raise SubmitError(f"不是有效的 SVN 工作副本：{root}")


def normalize_status_path(root: Path, raw_path: str) -> tuple[Path, str]:
    path = Path(raw_path)
    absolute = path.resolve() if path.is_absolute() else (root / path).resolve()
    try:
        relative = absolute.relative_to(root).as_posix()
    except ValueError as error:
        raise SubmitError(f"SVN 状态包含工作副本外路径：{absolute}") from error
    return absolute, relative


def read_status(svn: Path, root: Path) -> list[StatusEntry]:
    result = svn_command(
        svn,
        root,
        "status",
        "--xml",
        "--ignore-externals",
        str(root),
    )
    try:
        document = ET.fromstring(result.stdout)
    except ET.ParseError as error:
        raise SubmitError(f"无法解析 svn status 输出：{error}") from error

    entries: list[StatusEntry] = []
    for node in document.findall(".//entry"):
        status = node.find("wc-status")
        if status is None:
            continue
        item = status.get("item", "none")
        properties = status.get("props", "none")
        tree_conflicted = status.get("tree-conflicted", "false") == "true"
        if (
            item not in CHANGED_ITEMS
            and properties in {"none", "normal"}
            and not tree_conflicted
        ):
            continue
        absolute, relative = normalize_status_path(root, node.get("path", ""))
        entries.append(
            StatusEntry(
                path=absolute,
                relative_path=relative,
                item=item,
                properties=properties,
                tree_conflicted=tree_conflicted,
            )
        )
    return sorted(entries, key=lambda entry: entry.relative_path.casefold())


def matches_any(name: str, patterns: Sequence[str]) -> bool:
    folded = name.casefold()
    return any(fnmatch.fnmatch(folded, pattern.casefold()) for pattern in patterns)


def validate_status(
    entries: Sequence[StatusEntry],
    config: dict[str, object],
    *,
    allow_delete: bool,
) -> None:
    forbidden_patterns = [
        str(value) for value in config.get("forbidden_name_patterns", [])
    ]
    problems: list[str] = []
    for entry in entries:
        if (
            entry.item in CONFLICT_ITEMS
            or entry.tree_conflicted
            or entry.properties == "conflicted"
        ):
            problems.append(f"存在冲突或阻塞：{entry.relative_path} [{entry.item}]")
        if entry.item == "missing":
            problems.append(
                f"文件已从磁盘缺失但未执行 svn delete：{entry.relative_path}"
            )
        elif entry.item == "deleted" and not allow_delete:
            problems.append(
                f"检测到删除；确认后使用 --allow-delete：{entry.relative_path}"
            )
        if matches_any(Path(entry.relative_path).name, forbidden_patterns):
            problems.append(f"禁止提交的临时/其他项目文件：{entry.relative_path}")
        if entry.item == "unversioned" and entry.path.is_dir():
            for child in entry.path.rglob("*"):
                if child.is_file() and matches_any(child.name, forbidden_patterns):
                    child_relative = child.relative_to(entry.path).as_posix()
                    problems.append(
                        "未版本化目录内含禁止提交文件："
                        f"{entry.relative_path}/{child_relative}"
                    )
    if problems:
        detail = "\n".join(f"- {problem}" for problem in problems[:80])
        remaining = len(problems) - 80
        if remaining > 0:
            detail += f"\n- 另有 {remaining} 项"
        raise SubmitError(f"安全检查未通过：\n{detail}")


def run_validations(root: Path, config: dict[str, object]) -> None:
    commands = config.get("validation_commands", [])
    if not isinstance(commands, list):
        raise SubmitError("svn_submit.json 的 validation_commands 必须是数组。")
    replacements = {"{python}": sys.executable, "{root}": str(root)}
    for raw_command in commands:
        if not isinstance(raw_command, list) or not raw_command:
            raise SubmitError("validation_commands 中存在无效命令。")
        command = [replacements.get(str(value), str(value)) for value in raw_command]
        print(f"[校验] {' '.join(command)}")
        result = run_command(command, cwd=root, check=False)
        stdout = result.stdout.decode("utf-8", errors="replace").strip()
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
        if result.returncode != 0:
            raise SubmitError(f"仓库校验失败，退出码 {result.returncode}。")


def add_unversioned(
    svn: Path,
    root: Path,
    entries: Sequence[StatusEntry],
) -> None:
    if any(entry.item == "unversioned" for entry in entries):
        # 只传递 ASCII 的当前目录，避免 Windows SVN CLI 对中文 argv 二次转码。
        # svn add --force 会递归添加未版本化项，并继续遵守 svn:ignore。
        svn_command(svn, root, "add", "--parents", "--force", ".")


def summarize(entries: Sequence[StatusEntry], max_paths: int) -> None:
    counts = Counter(entry.item for entry in entries)
    summary = "，".join(f"{key}={counts[key]}" for key in sorted(counts))
    print(f"[状态] 共 {len(entries)} 项变更" + (f"：{summary}" if summary else "。"))
    for entry in entries[:max_paths]:
        property_mark = (
            f", props={entry.properties}"
            if entry.properties not in {"none", "normal"}
            else ""
        )
        print(f"  {entry.item:12} {entry.relative_path}{property_mark}")
    if len(entries) > max_paths:
        print(f"  ... 另有 {len(entries) - max_paths} 项")


def working_copy_revision(svn: Path, root: Path) -> str:
    svnversion = svn.with_name("svnversion.exe")
    if svnversion.is_file():
        result = run_command([str(svnversion), str(root)], cwd=root)
        return result.stdout.decode("utf-8", errors="replace").strip()
    result = svn_command(svn, root, "info", "--show-item", "revision", str(root))
    return result.stdout.decode("utf-8", errors="replace").strip()


def load_policy(root: Path, configured_path: Path | None) -> dict[str, object]:
    path = configured_path or (root / DEFAULT_CONFIG)
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        raise SubmitError(f"找不到 SVN 提交策略：{path}")
    policy = load_json(path)
    if policy.get("schema_version") != 1:
        raise SubmitError(f"不支持的 SVN 提交策略版本：{policy.get('schema_version')}")
    return policy


def main() -> int:
    configure_console_encoding()
    args = parse_args()
    root = args.root.resolve()
    try:
        if args.execute and (not args.message or len(args.message.strip()) < 8):
            raise SubmitError("--execute 时提交说明必填，且至少 8 个字符。")

        svn = locate_svn()
        policy = load_policy(root, args.config)
        max_paths = int(policy.get("max_display_paths", 80))
        ensure_working_copy(svn, root)
        version = svn_command(svn, root, "--version", "--quiet").stdout.decode(
            "utf-8", errors="replace"
        ).strip()
        print(f"[环境] SVN {version}：{svn}")
        print(f"[工作副本] {root}")

        if args.execute and not args.skip_update:
            print("[更新] 拉取仓库最新版本，冲突时保留现场并中止。")
            svn_command(
                svn,
                root,
                "update",
                "--accept",
                "postpone",
                "--non-interactive",
                str(root),
            )

        run_validations(root, policy)
        entries = read_status(svn, root)
        summarize(entries, max_paths)
        validate_status(
            entries,
            policy,
            allow_delete=args.allow_delete,
        )

        if not args.execute:
            print("[演练] 安全检查通过；未添加、未提交任何文件。")
            return 0

        add_unversioned(svn, root, entries)
        entries = read_status(svn, root)
        validate_status(
            entries,
            policy,
            allow_delete=args.allow_delete,
        )
        if not entries:
            print("[完成] 工作副本没有可提交变更。")
            return 0

        print(f"[提交] {args.message.strip()}")
        log_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                prefix="cr-svn-log-",
                suffix=".txt",
                delete=False,
            ) as stream:
                stream.write(args.message.strip())
                stream.write("\n")
                log_path = Path(stream.name)
            result = svn_command(
                svn,
                root,
                "commit",
                "--non-interactive",
                "--encoding",
                "UTF-8",
                "--file",
                str(log_path),
                str(root),
            )
        finally:
            if log_path is not None:
                log_path.unlink(missing_ok=True)
        output = result.stdout.decode("utf-8", errors="replace").strip()
        if output:
            print(output)

        remaining = read_status(svn, root)
        if remaining:
            summarize(remaining, max_paths)
            raise SubmitError("提交后工作副本仍有变更，请检查以上项目。")

        revision = working_copy_revision(svn, root)
        match = re.findall(r"\d+", revision)
        newest = match[-1] if match else revision
        print(f"[完成] SVN 提交成功；工作副本无待提交变更；最新版本 r{newest}。")
        return 0
    except (OSError, ValueError, json.JSONDecodeError, SubmitError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
