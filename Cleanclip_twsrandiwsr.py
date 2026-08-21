# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np

# -------------------------- 基础设置 --------------------------
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['grid.linestyle'] = '-'
plt.rcParams['grid.alpha'] = 0.4
plt.rcParams['grid.color'] = 'lightgray'

# -------------------------- 数据区（CoMoMark vs CleanCLIP，0-29 epoch）--------------------------
epoch_full = np.arange(30)
epoch_ticks = [0, 5, 10, 15, 20, 25, 30]

I_WSR_CoMoMark = [
    0.00, 0.01, 0.02, 0.02, 0.02, 0.03, 0.03, 0.03, 0.03, 0.03, 0.02, 0.02,
    0.02, 0.02, 0.02, 0.03, 0.02, 0.03, 0.02, 0.03, 0.03, 0.03, 0.03, 0.02, 
    0.02, 0.02, 0.02, 0.02, 0.01, 0.01]
T_WSR_CoMoMark = [
    0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
    0.02, 0.02, 0.02, 0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
    0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01
]

# 与微调图同一套学术配色：钢蓝 / 焦橙（色相约差 176°，两条近距离曲线也分得开）
series_defs = [
    (r'$\mathrm{WSR}_\mathrm{I}$', I_WSR_CoMoMark, '#2E75B6', 'v'),
    (r'$\mathrm{WSR}_\mathrm{T}$', T_WSR_CoMoMark, '#C55A11', '*'),
]

# -------------------------- 绘图 --------------------------
fig, ax = plt.subplots(figsize=(4.5, 3))

for label, values, color, marker in series_defs:
    ax.plot(
        epoch_full, values,
        color=color, linewidth=1.8,
        marker=marker, markersize=3 if marker == '*' else 2,
        markerfacecolor='white',
        markeredgecolor=color,
        markeredgewidth=2,
        label=label,
    )

ax.set_xticks(epoch_ticks)
ax.tick_params(axis='both', labelsize=18)
ax.set_xlabel('Epoch', fontsize=20)
ax.set_ylim(-0.1, 0.5)
ax.grid(True, color='lightgray', linewidth=0.6)

ax.legend(
    loc='upper left',
    #bbox_to_anchor=(0.5, 1.18),
    ncol=2,
    fontsize=19,
    frameon=True,
    edgecolor='lightgray',
    handlelength=1.6,
    columnspacing=0.8,
)

fig.subplots_adjust(top=0.82)
fig.savefig(r'C:\Users\91906\Desktop\cleanclip_IWSR_TWSR.pdf', dpi=300, bbox_inches='tight')
plt.show()
