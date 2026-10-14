# -*- coding: utf-8 -*-
"""从截图自动标定 bingo 卡位 —— 与卡片数量、排布解耦。

锚点：每张卡顶部的 5 个纯色列头块。它们是最稳定的特征：
    B (255, 60, 41)   红
    I (255,188, 55)   橙黄
    N ( 88,215, 24)   绿
    G (  0,185,228)   青蓝
    O (239, 43,192)   品红

用 RGB 距离匹配（不用色调区间 —— O 的色调是 314°，
按区间容易漏，实测踩过）。找到列头就能推出整张卡：

    列 x = 5 个色块中心 x
    行 y = 列头底边 + (i+0.5) * 列间距      （格子近似正方形）

不管屏幕上摆 1/2/3/4/5 张卡、怎么排，都能算出来。

用法：
    python bv_cardgrid.py <截图>                 # 打印标定结果
    python bv_cardgrid.py <截图> --overlay       # 另存叠加图，人工核验
    python bv_cardgrid.py --all                  # 扫 stalls 下全部截图
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from PIL import Image, ImageDraw

STALLS = r"D:\BingoVoyageProbe\stalls"
OUT = r"D:\BingoVoyageProbe\out"

# 列头纯色（实测取样）
HEADER = [("B", (255, 60, 41)), ("I", (255, 188, 55)), ("N", (88, 215, 24)),
          ("G", (0, 185, 228)), ("O", (239, 43, 192))]
COLOR_TOL = 46           # RGB 欧氏距离阈值
MIN_RUN = 15             # 行内连续段最短宽度
MIN_AREA = 400           # 色块最小像素数
BAND_W = (40, 120)       # 列头块宽度合理范围
BAND_H = (12, 70)        # 列头块高度合理范围


def mask_of(a, rgb, tol=COLOR_TOL):
    d = np.sqrt(((a - np.array(rgb, dtype=np.float32)) ** 2).sum(axis=-1))
    return d <= tol


def row_runs(row, min_run=MIN_RUN):
    out, x, n = [], 0, len(row)
    while x < n:
        if row[x]:
            x0 = x
            while x < n and row[x]:
                x += 1
            if x - x0 >= min_run:
                out.append((x0, x - 1))
        else:
            x += 1
    return out


def components(mask, min_area=MIN_AREA, max_gap=2):
    comps = []
    # Enumerate the identical horizontal runs in NumPy, preserving row order.
    # The former Python loop visited every pixel five times per screenshot and
    # consumed much of the final ball's short input window.
    edges=np.diff(np.pad(np.asarray(mask,dtype=np.int8),((0,0),(1,1))),axis=1)
    ys,starts=np.nonzero(edges==1);_,ends=np.nonzero(edges==-1)
    for y,x0,end in zip(ys,starts,ends):
        if end-x0>=MIN_RUN:
            y,x0,x1=int(y),int(x0),int(end)-1
            hit = False
            for c in comps:
                if y - c[3] <= max_gap:
                    ov = min(c[1], x1) - max(c[0], x0) + 1
                    if ov > 0.5 * min(c[1] - c[0] + 1, x1 - x0 + 1):
                        c[0], c[1] = min(c[0], x0), max(c[1], x1)
                        c[3] = y
                        c[4] += x1 - x0 + 1
                        hit = True
                        break
            if not hit:
                comps.append([x0, x1, y, y, x1 - x0 + 1])
    return [tuple(c) for c in comps if c[4] >= min_area]


def find_bands(img):
    """返回 [(name, x0, x1, y0, y1)]，只保留尺寸合理的列头块"""
    a = np.asarray(img).astype(np.float32)
    out = []
    for nm, rgb in HEADER:
        for x0, x1, y0, y1, area in components(mask_of(a, rgb)):
            w, h = x1 - x0 + 1, y1 - y0 + 1
            if BAND_W[0] <= w <= BAND_W[1] and BAND_H[0] <= h <= BAND_H[1]:
                out.append((nm, x0, x1, y0, y1))
    return out


def group_cards(bands):
    """把色块按行分组，每组凑齐连续的 B I N G O 才算一张卡"""
    bands = sorted(bands, key=lambda t: (t[3], t[1]))
    used = set()
    cards = []
    for i, (nm, x0, x1, y0, y1) in enumerate(bands):
        if i in used or nm != "B":
            continue
        row, cur_x, ytop, ybot = [(nm, x0, x1, y0, y1)], x0, y0, y1
        ok = True
        for want in ("I", "N", "G", "O"):
            best = None
            for j, (nm2, a0, a1, b0, b1) in enumerate(bands):
                if j in used or nm2 != want:
                    continue
                if abs(b0 - ytop) > 14:          # 同一列头行
                    continue
                if a0 <= cur_x:                  # 必须在上一个色块右侧
                    continue
                if best is None or a0 < best[1]:
                    best = (j, a0, a1, b0, b1)
            if best is None:
                ok = False
                break
            j, a0, a1, b0, b1 = best
            used.add(j)
            row.append((want, a0, a1, b0, b1))
            cur_x = a0
            ybot = max(ybot, b1)
        if ok:
            used.add(i)
            cards.append(row_to_card(row, ytop, ybot))
    return cards


def row_to_card(row, ytop, ybot):
    cols = [(c[1] + c[2]) / 2.0 for c in row]
    sp = (cols[-1] - cols[0]) / 4.0
    rows = [ybot + (k + 0.5) * sp for k in range(5)]
    return {"cols": cols, "rows": rows, "spacing": sp,
            "header_top": ytop, "header_bottom": ybot,
            "header_x0": row[0][1], "header_x1": row[-1][2]}


def regular_rows(centers):
    """Fit observed row bands; one animated band may lose its upper/lower paint.

    Four independent centers must support the same pitch within two pixels.
    No fixed coordinates or acceptance of an entirely unobserved row extent.
    """
    if len(centers) != 5:
        return None
    fits = []
    for omitted in range(5):
        ids = [i for i in range(5) if i != omitted]
        pitch, origin = np.polyfit(ids, [centers[i] for i in ids], 1)
        predicted = [float(origin + i*pitch) for i in range(5)]
        residual = max(abs(predicted[i]-centers[i]) for i in ids)
        if (35 <= pitch <= 125 and residual <= 2
                and abs(predicted[omitted]-centers[omitted]) <= pitch*.25):
            fits.append((residual, predicted))
    return min(fits, key=lambda item:item[0])[1] if fits else None


def refine_rows(img, card):
    """用「卡体亮色区域」实测行区高度，再五等分。

    为什么要这一步：原来 rows 是用「列间距 sp」当行间距推的
    （rows = ybot + (k+0.5)*sp）。1 张卡时列间距 114、实际行间距约 86，
    越往下漂得越多（第 4 行差 ~74px，直接掉到格子缝上），点击必然打空。
    """
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    H, W = a.shape[:2]
    sp = card["spacing"]
    x0 = int(max(0, card["cols"][0] - sp * 0.5))
    x1 = int(min(W, card["cols"][-1] + sp * 0.5))
    y0 = int(max(0, card["header_bottom"]))
    y1 = int(min(H, card["header_bottom"] + 5.6 * sp))
    if x1 - x0 < 10 or y1 - y0 < 10:
        return card
    sub = a[y0:y1, x0:x1]
    r, g, b = sub[:, :, 0], sub[:, :, 1], sub[:, :, 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    # 格子是奶油白：整体很亮且饱和度低；橙线/彩色背景都会被排除
    bright = (mn > 205) & ((mx - mn) < 55)
    frac = bright.mean(axis=1)
    on = frac > 0.15
    if not on.any():
        return card
    # ★ 按「亮带」切行：行间橙线会把亮带切开，只允许极小间隙桥接抗噪。
    #   之前用 0.18*sp(≈20px) 的容差，把橙线也桥接了，量出的格区偏高，
    #   行间距被摊大（110 vs 实际 100），第 4/5 行累计漂到 30px+，点中缝。
    runs, cur, gap = [], None, 0
    for i, v in enumerate(on):
        if v:
            if cur is None:
                cur = i
            gap = 0
        elif cur is not None:
            gap += 1
            if gap > 2:
                runs.append((cur, i - gap))
                cur = None
    if cur is not None:
        runs.append((cur, len(on) - 1 - gap))
    runs = [(s, e) for (s, e) in runs if (e - s) >= 0.35 * sp]
    if len(runs) >= 5:
        if len(runs) > 5:                      # 取最高的 5 段，再按 y 排回顺序
            runs = sorted(sorted(runs, key=lambda x: -(x[1] - x[0]))[:5])
        else:
            runs.sort()
        measured = [y0 + (s + e) / 2.0 for (s, e) in runs]
        card["observed_rows"] = measured
        fitted = regular_rows(measured)
        card["rows"] = fitted or measured
        card["row_spacing"] = (card["rows"][-1] - card["rows"][0]) / 4.0
        card["cell_area"] = (y0 + runs[0][0], y0 + runs[-1][1])
        card["row_mode"] = "bands"
        return card

    # 兜底：整块格区五等分（只在切不出 5 个亮带时用）
    start = int(np.argmax(on))
    gap_max = max(6, int(0.18 * sp))
    end, gap = start, 0
    for i in range(start, len(on)):
        if on[i]:
            end, gap = i, 0
        else:
            gap += 1
            if gap > gap_max:
                break
    top, bot = y0 + start, y0 + end
    if (bot - top) < 2.5 * sp:
        return card
    h = bot - top
    card["rows"] = [top + (k + 0.5) * h / 5.0 for k in range(5)]
    card["row_spacing"] = h / 5.0
    card["cell_area"] = (top, bot)
    card["row_mode"] = "extent"
    return card


def cell_geometry(img, card):
    """Measure cell shapes, never numbers or fill state.

    Pale/yellow tiles and red round tokens supply geometric edges. A Bingo paint
    change must not turn a visible row into a shorter card. At least four whole
    bands on each axis, including both ends, must independently fit five slots.
    Local face support gates each cell; a modal/animation is not click-through.
    """
    a = np.asarray(img.convert('RGB')).astype(np.int16)
    sp = card['spacing']; h, w = a.shape[:2]
    x0=max(0,int(card['header_x0']-4));x1=min(w,int(card['header_x1']+5))
    y0=max(0,int(card['header_bottom']+2));y1=min(h,int(y0+5.4*sp))
    a=a[y0:y1,x0:x1]
    if not a.size:return None
    lo=a.min(axis=2);hi=a.max(axis=2)
    face=((lo>205)&(hi-lo<55))|((a[:,:,0]>200)&(a[:,:,1]<130)&(a[:,:,2]<130))
    face|=(a[:,:,0]>210)&(a[:,:,1]>170)&(a[:,:,2]<150)&(a[:,:,0]>=a[:,:,1])
    def axis(frac, offset, threshold=.25):
        runs=row_runs(frac>threshold,min_run=max(20,int(.6*sp)))
        if not 4<=len(runs)<=5:return None
        centers=[(s+e)/2+offset for s,e in runs]
        pitch=(centers[-1]-centers[0])/4
        if not .8*sp<=pitch<=1.2*sp:return None
        ids=[round((v-centers[0])/pitch) for v in centers]
        if len(set(ids))!=len(ids) or ids[0]!=0 or ids[-1]!=4:return None
        pitch,origin=np.polyfit(ids,centers,1)
        if max(abs(origin+i*pitch-v) for i,v in zip(ids,centers))>2:return None
        return [float(origin+i*pitch) for i in range(5)]
    rows=axis(face.mean(axis=1),y0);cols=axis(face.mean(axis=0),x0)
    if rows is not None and cols is None:
        # Bingo paint can join adjacent columns in the full-height projection.
        # Recover from at least two independently visible row bands. Each must
        # still fit four/five whole cells including both ends; header/cached
        # coordinates alone never authorize a target.
        candidates=[]
        half=(rows[-1]-rows[0])/4*.44
        for y in rows:
            strip=face[max(0,int(y-y0-half)):int(y-y0+half)+1]
            for threshold in (.25,.35,.45):
                fit=axis(strip.mean(axis=0),x0,threshold)
                if fit is not None:
                    candidates.append(fit);break
        if len(candidates)>=2 and max(np.ptp(np.asarray(candidates),axis=0))<=2:
            cols=np.mean(candidates,axis=0).tolist()
    if rows is None or cols is None:return None
    reachable=[]
    for col,x in enumerate(cols):
        for row,y in enumerate(rows):
            dx=(cols[-1]-cols[0])/4*.4;dy=(rows[-1]-rows[0])/4*.4
            patch=face[max(0,int(y-y0-dy)):int(y-y0+dy)+1,
                       max(0,int(x-x0-dx)):int(x-x0+dx)+1]
            if patch.size:
                # Numbers/icons can occupy the center while all four tile
                # edges remain visible. Require support on every edge; a
                # single exposed corner or a fully covered tile cannot pass.
                edge=max(2,int(min(patch.shape)*.125))
                sides=[patch[:edge,:],patch[-edge:,:],patch[:,:edge],patch[:,-edge:]]
                perimeter=patch.mean()>=.25 and all(side.mean()>=.4 for side in sides)
                if patch.mean()>=.35 or perimeter:reachable.append(col*5+row)
    return dict(cols=cols,rows=rows,reachable_cells=reachable,source='visible_cell_shapes')


def detect(img, dbg=False):
    cards = group_cards(find_bands(img))
    # 视觉顺序：先上后下、先左后右
    cards.sort(key=lambda c: (round(c["header_top"] / 60.0), c["cols"][0]))
    for i, c in enumerate(cards):
        c["index"] = i
        refine_rows(img, c)
    if dbg:
        for c in cards:
            print("  卡%d 列头 y=%.0f..%.0f x=%.0f..%.0f 列间距=%.1f 行间距=%.1f"
                  % (c["index"], c["header_top"], c["header_bottom"],
                     c["header_x0"], c["header_x1"], c["spacing"],
                     c.get("row_spacing", c["spacing"])))
    return cards


def overlay(img, cards, path):
    im = img.copy()
    d = ImageDraw.Draw(im)
    for c in cards:
        for ri, y in enumerate(c["rows"]):
            for ci, x in enumerate(c["cols"]):
                d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=(0, 255, 0), width=3)
                d.text((x - 6, y - 6), "%d%d" % (c["index"], ri + 1), fill=(0, 0, 0))
        d.rectangle([c["header_x0"] - 2, c["header_top"] - 2,
                     c["header_x1"] + 2, c["header_bottom"] + 2], outline=(255, 0, 0), width=3)
    im.save(path)
    return path


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        for n in sorted(f for f in os.listdir(STALLS) if f.endswith(".png")):
            try:
                cards = detect(Image.open(os.path.join(STALLS, n)).convert("RGB"))
            except Exception as e:
                print("%-30s ERR %s" % (n, e))
                continue
            if cards:
                print("%-30s %d 张  首卡列头 y=%.0f  列=[%s] 行=[%s]"
                      % (n, len(cards), cards[0]["header_top"],
                         ",".join("%.0f" % x for x in cards[0]["cols"]),
                         ",".join("%.0f" % y for y in cards[0]["rows"])))
        return
    name = sys.argv[1] if len(sys.argv) > 1 else "s58_round.png"
    img = Image.open(os.path.join(STALLS, name)).convert("RGB")
    cards = detect(img, dbg=True)
    print("识别出 %d 张卡" % len(cards))
    for c in cards:
        print("  卡%d cols=[%s]" % (c["index"], ", ".join("%.0f" % x for x in c["cols"])))
        print("       rows=[%s]" % ", ".join("%.0f" % y for y in c["rows"]))
    if "--overlay" in sys.argv:
        os.makedirs(OUT, exist_ok=True)
        p = overlay(img, cards, os.path.join(OUT, "grid_overlay_%s" % name))
        print("叠加图 -> %s" % p)


if __name__ == "__main__":
    main()
