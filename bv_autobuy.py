# -*- coding: utf-8 -*-
"""识别当前界面并自动买一局卡 —— 按钮位置靠像素扫描自己找，不写死坐标。

界面判定：
  round     卡面检测出 >=1 张卡
  lobby     大块 PLAY 绿在画面下半
  betpanel  中部有押注蓝面板
  congrats  结算橙条
用法：python bv_autobuy.py
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, r"D:\BingoVoyageProbe")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from PIL import Image  # noqa
import bv_cardgrid  # noqa

ADB = r"C:\platform-tools\adb.exe"
DEV = "127.0.0.1:16384"
SHOT = r"D:\BingoVoyageProbe\out\_buy.png"

GREEN = (15, 201, 2)      # 实测的游戏 PLAY 按钮绿
BLUE = (48, 165, 235)     # 押注面板蓝
ORANGE = (245, 124, 27)   # 结算橙条


def tap(x, y):
    subprocess.run([ADB, "-s", DEV, "shell", "input", "tap", str(int(x)), str(int(y))],
                   capture_output=True, timeout=30)


def grab():
    for _ in range(3):
        r = subprocess.run([ADB, "-s", DEV, "exec-out", "screencap", "-p"],
                           capture_output=True, timeout=60)
        b = r.stdout or b""
        if b[:8] == b"\x89PNG\r\n\x1a\n" and len(b) > 4096:
            open(SHOT, "wb").write(b)
            return Image.open(SHOT).convert("RGB")
        time.sleep(0.6)
    return None


def find_green(im, yfrac=0.62):
    """扫出大块 PLAY 绿的重心。只在画面下部扫 —— 大厅/对局的绿色桌面、
    草地在画面中上部，会把重心带偏（实测偏到 (609,969)）。返回 (cx,cy,n)。"""
    w, h = im.size
    sw, sh = w // 3, h // 3
    px = im.resize((sw, sh)).load()
    y0 = int(sh * yfrac)
    xs, ys = [], []
    for y in range(y0, sh):
        for x in range(sw):
            r, g, b = px[x, y]
            if abs(r - GREEN[0]) < 70 and abs(g - GREEN[1]) < 70 and abs(b - GREEN[2]) < 70:
                xs.append(x)
                ys.append(y)
    if len(xs) < 100:
        return None
    return (sum(xs) / len(xs) * 3, sum(ys) / len(ys) * 3, len(xs))


def near(p, rgb, tol=45):
    return all(abs(p[i] - rgb[i]) <= tol for i in range(3))


def state(im):
    try:
        if bv_cardgrid.detect(im):
            return "round"
    except Exception:
        pass
    w, h = im.size
    g = find_green(im)
    if g and g[1] > h * 0.5:
        return "lobby"
    if near(im.getpixel((450, 700)), BLUE, 55):
        return "betpanel"
    if near(im.getpixel((450, 380)), ORANGE, 55):
        return "congrats"
    return "unknown"


if __name__ == "__main__":
    for step in range(12):
        im = grab()
        if im is None:
            print("截图失败")
            break
        st = state(im)
        g = find_green(im)
        print("步骤%d 状态=%-9s 绿块=%s" % (step, st, ("(%.0f,%.0f) n=%d" % g) if g else "无"))
        if st == "round":
            print(">>> 已在对局中，开自动玩")
            break
        if st == "congrats":
            tap(447, 1033)
            time.sleep(3.5)
        elif st in ("lobby", "betpanel"):
            if not g:
                print("    没找到绿 PLAY，跳过")
                time.sleep(2.0)
                continue
            tap(g[0], g[1])
            time.sleep(3.5)
        else:
            print("    （加载/未知，等）")
            time.sleep(3.0)
    else:
        print(">>> 12 步内没进对局")
