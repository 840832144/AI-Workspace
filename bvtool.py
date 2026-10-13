"""Bingo Voyage 操作助手：tap / swipe / 截图 / 状态，统一走 MuMu(7555)。

用法：
    python bvtool.py shot name
    python bvtool.py tap X Y
    python bvtool.py swipe X1 Y1 X2 Y2 [ms]
    python bvtool.py status
"""
import os, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ADB = r"C:\platform-tools\adb.exe"
DEV = "127.0.0.1:16384"
PKG = "com.bingo.cruise.free.best.top.game"
DIR = r"D:\BingoVoyageProbe\stalls"
os.makedirs(DIR, exist_ok=True)


def run(*a, t=90):
    return subprocess.run([ADB, "-s", DEV] + list(a), capture_output=True,
                          stdin=subprocess.DEVNULL, timeout=t).stdout


def shot(name):
    b = run("exec-out", "screencap", "-p", t=60)
    p = os.path.join(DIR, name + ".png")
    open(p, "wb").write(b)
    print("shot -> %s (%d bytes)" % (p, len(b)))
    return p


def tap(x, y, hold=120, wait=1.2):
    run("shell", "input", "swipe", str(int(x)), str(int(y)), str(int(x)), str(int(y)), str(hold))
    time.sleep(wait)


def swipe(x1, y1, x2, y2, ms=300, wait=1.2):
    run("shell", "input", "swipe", str(int(x1)), str(int(y1)), str(int(x2)), str(int(y2)), str(ms))
    time.sleep(wait)


def status():
    pid = run("shell", "pidof", PKG).decode(errors="replace").strip()
    print("pid:", pid or "(not running)")
    print("size:", run("shell", "wm", "size").decode(errors="replace").strip())
    return pid


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "shot":
        shot(sys.argv[2])
    elif cmd == "tap":
        tap(int(sys.argv[2]), int(sys.argv[3]))
        shot("after_tap_%s_%s" % (sys.argv[2], sys.argv[3]))
    elif cmd == "swipe":
        swipe(*[int(v) for v in sys.argv[2:6]])
        shot("after_swipe")
    elif cmd == "status":
        status()
