"""检查数值方案是否包含最基本的可复核章节。"""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_TERMS = {
    "数据源": ("数据源", "口径"),
    "假设": ("假设", "约束"),
    "推导": ("推导", "公式"),
    "校验": ("校验", "边界", "敏感性"),
    "结论": ("结论", "配置建议"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    text = args.document.read_text(encoding="utf-8")
    missing = [
        label
        for label, alternatives in REQUIRED_TERMS.items()
        if not any(term in text for term in alternatives)
    ]
    if missing:
        print("缺少可复核章节：" + "、".join(missing))
        return 1
    print("通过：文档包含数据源、假设、推导、校验和结论。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

