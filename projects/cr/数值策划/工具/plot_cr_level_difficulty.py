"""TASK-0036升级难度图；只读既有模拟输出，不重算配置。

python plot_cr_level_difficulty.py --simulation <受控模拟目录> --level-inputs <受控level-inputs.json>
依赖matplotlib（本轮安装在受控目录plot-libs中，不修改全局Python）。
PNG/PDF含完整商业曲线，仅写受控目录；Git保存本生成器和脱敏验收。
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from matplotlib import font_manager, pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import PercentFormatter
import numpy as np

CF = '#2563EB'
CR = '#D97706'
FIT = '#8B5CF6'
INK = '#172B4D'


def style(ax: plt.Axes, title: str, ylabel: str) -> None:
    ax.set_title(title, loc='left', fontsize=14, weight='bold', pad=14)
    ax.set_xlabel('当前等级 L（计算 L → L+1）', labelpad=8)
    ax.set_ylabel(ylabel, labelpad=9)
    ax.grid(axis='y', color='#E2E8F0', linewidth=.8)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('#CBD5E1')
    ax.set_axisbelow(True)
    ax.tick_params(length=3, color='#94A3B8')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--simulation', type=Path, required=True)
    parser.add_argument('--level-inputs', type=Path, required=True)
    args = parser.parse_args()
    output = args.simulation/'charts'
    assert not any((p/'.git').exists() for p in (output.resolve(), *output.resolve().parents))
    output.mkdir(exist_ok=True)
    font = Path('C:/Windows/Fonts/msyh.ttc')
    assert font.is_file(), '需要支持中文的字体'
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family': font_manager.FontProperties(fname=font).get_name(),
                         'font.size': 11, 'axes.unicode_minus': False,
                         'text.color': INK, 'axes.labelcolor': INK,
                         'xtick.color': INK, 'ytick.color': INK,
                         'pdf.fonttype': 42, 'path.simplify': False})
    with (args.simulation/'CR_CF_first300.csv').open(encoding='utf-8-sig', newline='') as f:
        points = list(csv.DictReader(f))
    with (args.simulation/'CR_levels.csv').open(encoding='utf-8-sig', newline='') as f:
        full = list(csv.DictReader(f))
    inputs = json.loads(args.level_inputs.read_text(encoding='utf-8'))
    summary = json.loads((args.simulation/'simulation.json').read_text(encoding='utf-8'))
    x = np.array([int(r['level']) for r in points])
    cf = np.array([float(r['CF_net_usd']) for r in points])
    cr = np.array([float(r['CR_net_usd']) for r in points])
    deviation = np.array([float(r['cost_delta']) for r in points])
    fx = np.array([int(r['level']) for r in full])
    fc = np.array([float(r['net_usd']) for r in full])
    target = np.array([r[8] for r in inputs['rows'][:-1]], dtype=float)
    assert np.array_equal(x, np.arange(1, 301))
    assert np.array_equal(fx, np.arange(1, 5000))
    assert np.allclose(fc[:300], cr, rtol=1e-12, atol=1e-12)
    assert np.allclose(target[:300], cf, rtol=1e-12, atol=1e-12)
    assert np.allclose(cr/cf-1, deviation, rtol=1e-9, atol=1e-12)
    peak = int(np.argmax(deviation))
    cumulative = summary['first300']['cost_delta']
    line_checks = []

    def line(ax: plt.Axes, xx: np.ndarray, yy: np.ndarray, label: str, color: str,
             dashed: bool = False, width: float = 2.0) -> None:
        artist, = ax.plot(xx, yy, color=color, linewidth=width,
                          linestyle=(0, (5, 3)) if dashed else '-', label=label)
        assert np.array_equal(artist.get_xdata(), xx)
        assert np.array_equal(artist.get_ydata(), yy)
        line_checks.append({'series': label, 'points': len(xx)})

    fig = plt.figure(figsize=(15, 10.5), facecolor='white')
    grid = fig.add_gridspec(2, 2, height_ratios=[1.6, 1], left=.075, right=.965,
                           bottom=.135, top=.805, hspace=.49, wspace=.25)
    fig.text(.075, .958, 'CR × Cash Frenzy', fontsize=15, color='#64748B')
    fig.text(.075, .914, '升级难度曲线对比｜1–300级', fontsize=25, weight='bold')
    fig.text(.075, .874, '同级比较机器理论净耗 USD；橙线为 dev r7237 实际配置反算结果', fontsize=13)
    fig.text(.965, .953, f'前300次升级累计  +{cumulative:.2%}', ha='right', fontsize=14, color=CR)
    fig.text(.965, .920, f'单级最大  +{deviation[peak]:.2%}（L{x[peak]}）', ha='right', fontsize=12, color=CR)
    ax = fig.add_subplot(grid[0, :])
    style(ax, '全部300个逐级点 · 共用同一坐标轴', '单级升级难度（USD）')
    line(ax, x, cr, 'CR · 实际配置反算', CR, width=2.4)
    line(ax, x, cf, 'Cash Frenzy · 历史表基准', CF, dashed=True)
    ax.set(xlim=(1, 300), ylim=(0, max(cr.max(), cf.max())*1.10))
    ax.set_xticks([1, 50, 100, 150, 200, 250, 300])
    ax.legend(frameon=False, loc='upper left', ncol=2)
    early = fig.add_subplot(grid[1, 0])
    style(early, '早期放大 · 1–30级', '单级升级难度（USD）')
    line(early, x[:30], cr[:30], 'CR', CR, width=2.4)
    line(early, x[:30], cf[:30], 'Cash Frenzy', CF, dashed=True)
    early.set(xlim=(1, 30), ylim=(0, max(cr[:30].max(), cf[:30].max())*1.12))
    early.set_xticks([1, 5, 10, 15, 20, 25, 30])
    err = fig.add_subplot(grid[1, 1])
    style(err, '逐级偏差 · （CR ÷ CF − 1）', '相对CF的难度偏差')
    line(err, x, deviation, '逐级偏差', CR, width=1.1)
    err.fill_between(x, 0, deviation, color=CR, alpha=.10)
    err.axhline(0, color='#64748B', linewidth=.8)
    err.scatter([x[peak]], [deviation[peak]], color=CR, zorder=4, s=28)
    err.annotate(f'L{x[peak]}：+{deviation[peak]:.2%}', xy=(x[peak], deviation[peak]),
                 xytext=(x[peak]+40, deviation[peak]+.002), color=CR,
                 arrowprops={'arrowstyle': '-', 'color': CR}, fontsize=10)
    err.set(xlim=(1, 300), ylim=(-.001, .040))
    err.set_xticks([1, 50, 100, 150, 200, 250, 300])
    err.yaxis.set_major_formatter(PercentFormatter(1, decimals=1))
    fig.text(.075, .046, '来源：CR dev r7237 固定配置模拟；CashRoyal数值.xlsx / cashFrenzy等级。全部逐级点，无平滑、无抽样。', fontsize=10, color='#64748B')
    fig.text(.075, .020, '按既定95% / 85%成本模型比较；整数门槛取整误差单列。Spin数量不是本次对标指标；本图不是游戏实测。', fontsize=10, color='#64748B')

    tail = plt.figure(figsize=(15, 9.5), facecolor='white')
    grid2 = tail.add_gridspec(2, 1, height_ratios=[1.5, 1], left=.075, right=.965,
                            bottom=.14, top=.80, hspace=.52)
    tail.text(.075, .945, 'CR升级难度｜完整曲线与拟合边界', fontsize=25, weight='bold')
    tail.text(.075, .895, 'CF原始点仅覆盖1–300级；301–4999为CR拟合目标，5000级是终点', fontsize=13)
    for index, limits, title in [(0, (1, 5000), '完整升级区间 · 1→5000'),
                                  (1, (250, 400), '边界放大 · 250–400级')]:
        ax = tail.add_subplot(grid2[index])
        style(ax, title, '单级升级难度（USD）')
        ax.axvspan(300, limits[1], color='#F1F5F9', zorder=-2)
        line(ax, fx, fc, 'CR · 实际配置反算', CR, width=2.3)
        line(ax, fx[300:], target[300:], 'CR · 拟合目标（无CF同级数据）', FIT, dashed=True)
        line(ax, x, cf, 'CF · 原始基准（止于300级）', CF, dashed=True)
        ax.axvline(300, color='#64748B', linewidth=1, linestyle=':')
        selected = (fx >= limits[0]) & (fx <= limits[1])
        ax.set(xlim=limits, ylim=(0, max(fc[selected].max(), target[selected].max())*1.16))
        ax.text(.97, .88, '灰色区域：CR拟合段，不是CF实测曲线', transform=ax.transAxes,
                ha='right', color='#475569', fontsize=11)
        if index == 0:
            ax.legend(frameon=False, loc='upper left', ncol=3, fontsize=10)
    tail.text(.075, .045, '后段按CF250–300级的归一难度趋势拟合，再按CR保留的等级金币倍率还原；美元难度随倍率换档可下降。', fontsize=10, color='#64748B')
    tail.text(.075, .020, '来源：同一轮已验证模拟明细及等级拟合输入。本轮仅制图，未重算模型、修改配置或新增SVN提交。', fontsize=10, color='#64748B')
    paths = [output/'CR_vs_CF_升级难度_1-300.png', output/'CR_升级难度_后续拟合.png']
    for chart, path in zip([fig, tail], paths):
        chart.savefig(path, dpi=170, facecolor='white', metadata={'Software': 'TASK-0036'})
    with PdfPages(output/'CR_vs_CF_升级难度曲线对照.pdf', metadata={'Title': 'CR与CF升级难度曲线核验', 'Author': '', 'Creator': 'TASK-0036'}) as pdf:
        pdf.savefig(fig)
        pdf.savefig(tail)
    validation = {'comparison_points': 300, 'full_CR_points': 4999, 'CF_extension_points': 0,
                  'line_source_checks': line_checks, 'smoothing': False, 'path_simplification': False,
                  'config_writes': 0, 'model_rerun': False, 'visual_review': 'pending'}
    (output/'chart-validation.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'outputs': [p.name for p in paths], 'series_checks': len(line_checks),
                      'comparison_points': 300, 'full_CR_points': 4999}, ensure_ascii=False))
    plt.close('all')


if __name__ == '__main__':
    main()
