# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np

# -------------------------- 基础设置 --------------------------
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7
plt.rcParams['grid.color'] = 'lightgray'

# -------------------------- 数据区（CoMoMark vs CleanCLIP，0-30 epoch）--------------------------
epoch_full = [0, 5, 10, 15, 20]
epoch_ticks = [0, 5, 10, 15, 20]

# TODO: 将 ACC / I-ACC / T-ACC 替换为真实实验数据（各 31 个值）
ACC_CoMoMark = [
    0.94, 0.96, 0.98, 0.98, 0.96]
I_ACC_CoMoMark = [
    0.95, 0.94, 0.94, 0.94, 0.94]
T_ACC_CoMoMark = [
    0.92, 0.98, 0.98, 0.98, 1.00]
WSR_CoMoMark = [
    1.00, 0.92, 0.94, 0.94, 0.90]

series_defs = [
    ('ACC', ACC_CoMoMark, '#2E75B6', 's', '-'),
    (r'$\mathrm{ACC}_\mathrm{I}$', I_ACC_CoMoMark, '#C55A11', 's', '-'),
    (r'$\mathrm{ACC}_\mathrm{T}$', T_ACC_CoMoMark, '#548235', 's', '-'),
    ('WSR', WSR_CoMoMark, '#7030A0', 's', '-'),
]

# -------------------------- 绘图 --------------------------
fig, ax = plt.subplots(figsize=(5, 3.2))

for label, values, color, marker, linestyle in series_defs:
    ax.plot(
        epoch_full, values,
        color=color, linestyle=linestyle, linewidth=3,
        marker=marker, markersize=8,
        markerfacecolor=color,
        markeredgewidth=0,
        label=label,
    )

ax.set_xticks(epoch_ticks)
ax.set_xlim(-1, 21)
ax.tick_params(axis='both', labelsize=18)
ax.set_xlabel('Epoch', fontsize=20)
ax.set_ylim(0.5, 1.05)
ax.grid(True, color='lightgray', linewidth=0.6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.legend(
    loc='lower left',
    ncol=2,
    fontsize=18,
    frameon=True,
    edgecolor='lightgray',
    handlelength=2.0,
    columnspacing=0.8,
)

fig.subplots_adjust(top=0.88)

fig.savefig(r'C:\Users\91906\Desktop\finetuning1_CoMoMark.pdf', dpi=300, bbox_inches='tight')
plt.show()
