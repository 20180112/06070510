"""
两张配对散点对比图（每张图合并为单个子图）：
  图1 — full vs noperservation：clean 与 patch_only（自动范围）
  图2 — full vs noseparation：正方形坐标，x 至少覆盖 [-0.5, 0.5]，y 包含全部数据
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "full_final": "OxfordPets_full_iter03_final_flow_records.npz",
    "noperservation_final": "OxfordPets_noperservation_iter03_final_flow_records.npz",
    "noseparation_final": "OxfordPets_noseparation_iter03_final_flow_records.npz",
}

FIG_SIZE = (7, 7)
FIG2_XLIM = (-0.5, 0.5)
LABEL_SIZE = 30
TICK_SIZE = 30
LEGEND_SIZE = 25
POINT_SIZE = 50

# USENIX Security 投稿配色（CrossMarker 原珊瑚红保持不变）：
# w/o pre 用 ColorBrewer Set1 蓝，避免原先发闷的青绿；
# w/o sep 用偏蓝的靛紫，与珊瑚红/橙拉开色相（旧橙仅差约 30°）。
COLOR_CROSSMARKER = "#f45c5c"  # 原色，不改
COLOR_WO_PRE = "#377EB8"       # Set1 蓝，替换 #40717c
COLOR_WO_SEP = "#5E4CB0"       # 靛紫，替换与 CrossMarker 过近的 #f4a454


def load_npz(key):
    path = os.path.join(BASE_DIR, FILES[key])
    return np.load(path)


def _axis_lim(vals_list, pad=0.05):
    vals = np.concatenate([np.asarray(v).reshape(-1) for v in vals_list])
    vals = vals[np.isfinite(vals)]
    lo, hi = float(vals.min()), float(vals.max())
    margin = (hi - lo) * pad if hi > lo else 0.05
    return lo - margin, hi + margin


def _square_lim_for_fig2(all_vals, x_bounds=FIG2_XLIM, pad=0.05):
    """
    图2 正方形范围：xlim == ylim。
    lo = min(x_bounds左端, 数据最小值)，hi = max(x_bounds右端, 数据最大值)，
    既保证 x 覆盖 [-0.5, 0.5]，又保证 y 方向数据不被裁切。
    """
    vals = np.concatenate([np.asarray(v).reshape(-1) for v in all_vals])
    vals = vals[np.isfinite(vals)]
    data_lo, data_hi = float(vals.min()), float(vals.max())
    margin = (data_hi - data_lo) * pad if data_hi > data_lo else 0.05
    data_lo -= margin
    data_hi += margin

    lo = min(x_bounds[0], data_lo)
    hi = max(x_bounds[1], data_hi)
    return (lo, hi)


def _style_axes(ax, xlabel, ylabel):
    ax.set_xlabel(xlabel, fontsize=LABEL_SIZE)
    ax.set_ylabel(ylabel, fontsize=LABEL_SIZE)
    ax.tick_params(axis="both", labelsize=TICK_SIZE)
    ax.legend(
        loc="upper left", fontsize=LEGEND_SIZE, framealpha=0.9,
        markerscale=1.2, handletextpad=0.25, handlelength=0.8,
    )
    ax.grid(True, alpha=0.25)


def pairwise_distance(x, y):
    """统一距离指标：每个样本到 y=x 的竖直距离 |y-x|，再取均值。"""
    x = np.asarray(x).reshape(-1)
    y = np.asarray(y).reshape(-1)
    return float(np.mean(np.abs(y - x)))


def _add_series(ax, d, y_key, color, marker, label):
    x = d["sim_clean"]
    y = d[y_key]
    dist = pairwise_distance(x, y)
    ax.scatter(
        x, y, c=color, marker=marker, s=POINT_SIZE, alpha=0.5,
        edgecolors="none", label=f"{label}",
    )
    return x, y


def _finalize_axes(ax, lim, xlabel, ylabel):
    lo, hi = lim
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=1.8, alpha=0.55, label="_nolegend_")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_aspect("equal", adjustable="box")
    _style_axes(ax, xlabel, ylabel)


def _save_figure(fig, filename, tight=True):
    out = os.path.join(BASE_DIR, filename)
    if tight:
        fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print(f"已保存: {out}")


def plot_preservation_comparison():
    """图1：full vs noperservation"""
    full = load_npz("full_final")
    no_p = load_npz("noperservation_final")

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    all_vals = []

    for d, y_key, color, marker, label in [
        (full, "sim_patch_only", COLOR_CROSSMARKER, "o", "CrossMarker"),
        (no_p, "sim_patch_only", COLOR_WO_PRE, "o", "CrossMarker w/o $\ell_{pre}$"),
    ]:
        x, y = _add_series(ax, d, y_key, color, marker, label)
        all_vals.extend([x, y])

    lim = _axis_lim(all_vals)
    _finalize_axes(ax, lim, "Clean pairs", "Image only pairs")
    fig.tight_layout()
    axes_rect = ax.get_position().frozen()
    _save_figure(fig, "scatter_01_preservation_full_vs_noperservation.pdf", tight=False)
    return lim, axes_rect


def plot_separation_comparison(axes_rect):
    """图2：正方形坐标，绘图区与图1一致"""
    full = load_npz("full_final")
    no_s = load_npz("noseparation_final")

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    all_vals = []

    for d, y_key, color, marker, label in [
        (full, "sim_double_trigger", COLOR_CROSSMARKER, "o", "CrossMarker"),
        (no_s, "sim_double_trigger", COLOR_WO_SEP, "o", "CrossMarker w/o $\ell_{sep}$"),
    ]:
        x, y = _add_series(ax, d, y_key, color, marker, label)
        all_vals.extend([x, y])

    lim = _square_lim_for_fig2(all_vals)
    _finalize_axes(ax, lim, "Clean pairs", "Watermarked pairs")
    ax.set_position(axes_rect)
    _save_figure(fig, "scatter_02_separation_full_vs_noseparation.pdf", tight=False)
    return lim


def main():
    lim1, axes_rect = plot_preservation_comparison()
    lim2 = plot_separation_comparison(axes_rect)
    print(f"图1 坐标范围: [{lim1[0]:.4f}, {lim1[1]:.4f}]（自动正方形）")
    print(f"图2 坐标范围: [{lim2[0]:.4f}, {lim2[1]:.4f}]（正方形，x 覆盖 [-0.5, 0.5]）")
    print("\n2 张对比散点图已生成完毕。")


if __name__ == "__main__":
    main()
