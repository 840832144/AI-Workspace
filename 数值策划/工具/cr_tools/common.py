"""路径、哈希和 JSON 等通用逻辑。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def repository_root() -> Path:
    """返回 CR_design 仓库根目录。"""

    return Path(__file__).resolve().parents[3]


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """流式计算文件 SHA-256，避免一次载入大型工作簿。"""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    """以 UTF-8 读取 JSON 对象。"""

    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"JSON 根节点必须是对象：{path}")
    return value


def write_json(path: Path, value: Any) -> None:
    """以稳定格式写入 UTF-8 JSON。"""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

