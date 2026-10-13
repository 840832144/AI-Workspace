# -*- coding: utf-8 -*-
"""把 bingo_voyage 采集器改成自包含：去掉绝对路径与越级引用。"""
import ast
import os
import re

D = r"D:\cr_design\Collector\collectors\bingo_voyage"

CFG_BLOCK = '''
HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))


def _P(key):
    """config.json 里的路径：相对路径按本目录解析，绝对路径原样使用。"""
    v = CFG["paths"][key]
    return v if os.path.isabs(v) else os.path.join(HERE, v)

'''

def patch(name, pairs, must=True):
    p = os.path.join(D, name)
    s = open(p, encoding="utf-8").read()
    for old, new in pairs:
        if old not in s:
            print("  [MISS] %s : %r" % (name, old[:70]))
            continue
        s = s.replace(old, new, 1)
        print("  [ok]   %s : %r" % (name, old[:50]))
    ast.parse(s)
    open(p, "w", encoding="utf-8").write(s)
    print("  -> %s 已写回" % name)


# ---------- bv_ws2.py ----------
patch("bv_ws2.py", [
    ('sys.path.insert(0, r"D:\\BingoVoyageProbe")\nfrom bv_proto import render  # noqa\n\n'
     'OUT = r"D:\\BingoVoyageProbe\\out"\n'
     'WS = os.path.join(OUT, "bv_ws.jsonl")\n'
     'BODIES = os.path.join(OUT, "bv_bodies")',
     'from bv_proto import render  # noqa\n' + CFG_BLOCK +
     'OUT = _P("out")\n'
     'WS = os.path.join(OUT, "bv_ws.jsonl")\n'
     'BODIES = os.path.join(OUT, "bv_bodies")'),
])

# ---------- bv_proto.py ----------
patch("bv_proto.py", [
    ('OUT = r"D:\\BingoVoyageProbe\\out"', CFG_BLOCK + 'OUT = _P("out")'),
])

# ---------- bv_extract.py ----------
patch("bv_extract.py", [
    ('ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n'
     'sys.path.insert(0, ROOT)\n'
     'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))',
     'HERE = os.path.dirname(os.path.abspath(__file__))\n'
     'sys.path.insert(0, HERE)'),
    ('CFG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),\n'
     '                                 "config.json"), encoding="utf-8"))\n'
     'OUT = CFG["paths"]["out"]\n'
     'DATA = CFG["paths"]["data"]',
     'CFG = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))\n'
     '\n'
     '\n'
     'def _P(key):\n'
     '    v = CFG["paths"][key]\n'
     '    return v if os.path.isabs(v) else os.path.join(HERE, v)\n'
     '\n'
     '\n'
     'OUT = _P("out")\n'
     'DATA = _P("data")'),
])

# ---------- bv_report.py ----------
patch("bv_report.py", [
    ('ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n'
     'sys.path.insert(0, ROOT)',
     'HERE = os.path.dirname(os.path.abspath(__file__))\n'
     'sys.path.insert(0, HERE)'),
    ('from collector import bv_extract as EX  # noqa: E402',
     'import bv_extract as EX  # noqa: E402'),
    ('CFG = EX.CFG\nDATA = CFG["paths"]["data"]\nOUT = CFG["paths"]["out"]',
     'CFG = EX.CFG\nDATA = EX.DATA\nOUT = EX.OUT'),
])

# ---------- bv_replay.py ----------
patch("bv_replay.py", [
    ('HERE = os.path.dirname(os.path.abspath(__file__))\n'
     'ROOT = os.path.dirname(HERE)\n'
     'sys.path.insert(0, ROOT)',
     'HERE = os.path.dirname(os.path.abspath(__file__))\n'
     'sys.path.insert(0, HERE)'),
    ('import collector.bv_extract as EX  # noqa: E402',
     'import bv_extract as EX  # noqa: E402'),
])

# ---------- bv_play.py ----------
patch("bv_play.py", [
    ('ROOT = r"D:\\BingoVoyageProbe"\nsys.path.insert(0, ROOT)',
     'ROOT = os.path.dirname(os.path.abspath(__file__))\nsys.path.insert(0, ROOT)'),
    ('from collector.bv_extract import extract_cards as _xcards, harvest_strings  # noqa: E402',
     'from bv_extract import extract_cards as _xcards, harvest_strings  # noqa: E402'),
    ('    from collector.bv_extract import build_grid, fields',
     '    from bv_extract import build_grid, fields'),
    ('WS = os.path.join(ROOT, "out", "bv_ws.jsonl")\nBODIES = os.path.join(ROOT, "out", "bv_bodies")',
     'CFG = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))\n'
     '\n'
     '\n'
     'def _P(key):\n'
     '    v = CFG["paths"][key]\n'
     '    return v if os.path.isabs(v) else os.path.join(ROOT, v)\n'
     '\n'
     '\n'
     'WS = os.path.join(_P("out"), "bv_ws.jsonl")\n'
     'BODIES = os.path.join(_P("out"), "bv_bodies")'),
])

# ---------- bv_collect.py ----------
patch("bv_collect.py", [
    ('HERE = os.path.dirname(os.path.abspath(__file__))\n'
     'ROOT = os.path.dirname(HERE)\n'
     'sys.path.insert(0, ROOT)',
     'HERE = os.path.dirname(os.path.abspath(__file__))\n'
     'ROOT = HERE\n'
     'sys.path.insert(0, ROOT)'),
    ('OUT = CFG["paths"]["out"]', 'OUT = CFG["paths"]["out"] if os.path.isabs(CFG["paths"]["out"]) \\\n    else os.path.join(HERE, CFG["paths"]["out"])'),
    ('    r = subprocess.run([sys.executable, os.path.join(ROOT, "bv_autodaub.py"),',
     '    r = subprocess.run([sys.executable, os.path.join(ROOT, "bv_play.py"),'),
    ('    ap.add_argument("--seconds", type=int, default=60)\n    a, _ = ap.parse_known_args()',
     '    ap.add_argument("--seconds", type=int, default=60)\n    a, _ = ap.parse_known_args()'),
    ('    for n in ("bv_ws2.py", "bv_proto.py"):\n        p = os.path.join(ROOT, n)',
     '    for n in ("bv_ws2.py", "bv_proto.py", "bv_extract.py", "bv_replay.py"):\n        p = os.path.join(ROOT, n)'),
])

print("\n--- 残留检查 ---")
for f in sorted(os.listdir(D)):
    if not f.endswith(".py"):
        continue
    s = open(os.path.join(D, f), encoding="utf-8").read()
    for pat in ("BingoVoyageProbe", "collector.bv_extract", "bv_autodaub", "dirname(ROOT)"):
        if pat in s:
            for i, ln in enumerate(s.splitlines(), 1):
                if pat in ln:
                    print("  %s:%d  %s" % (f, i, ln.strip()[:90]))
print("完成")
