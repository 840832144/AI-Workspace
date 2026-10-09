"""Render an approved controlled model with the existing spreadsheet runtime."""
import argparse
import os
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', required=True, type=Path)
    parser.add_argument('--runtime-node-modules', required=True, type=Path)
    parser.add_argument('model', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    adapter = Path(__file__).with_suffix('.mjs')
    env = os.environ.copy()
    env['CR_REPORT_NODE_MODULES'] = str(args.runtime_node_modules.resolve())
    return subprocess.run([str(args.node), str(adapter), str(args.model), str(args.output)], env=env, check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
