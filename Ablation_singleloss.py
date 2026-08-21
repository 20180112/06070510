import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.patches import Patch

OUTPUT_DIR = Path(__file__).resolve().parent

# 数据与参数设置
n_series = 4  # 每个分组的4个柱形
n_models = 3  # 模型数量
n_groups_per_model = 2  # 每个模型的分组数

gap_between_bars = 0.01  # 柱形之间的固定间隙（数值越大，间隙越宽）
bar_width = 0.03  # 单个柱形的宽度（固定值，方便控制间隙）
# 计算每个分组的总宽度（柱形总宽 + 间隙总宽）
group_total_width = n_series * bar_width + (n_series - 1) * gap_between_bars
group_gap = 0.06  # 分组之间的间隙

# 柱形颜色：按参考图（浅青绿 / 雾蓝 / 陶土红；第四色同风格浅沙）
colors = ['#8DBB94', '#C4D4E9', '#CD7066', '#E6CFA3']
BAR_LABEL_SIZE = 20

# 数据
data = [
    # BLIP 模型
    [
        [6, 82, 100, 0],    # w/o L_eva
        [88, 90, 8, 0]      # w/ L_eva
    ],
    # SigLIP 模型
    [
        [6, 64, 100, 3],    # w/o L_eva
        [82, 82, 1, 1]      # w/ L_eva
    ],
    # CLIP 模型
    [
        [6, 75, 100, 4],    # w/o L_eva
        [95, 92, 0, 2]      # w/ L_eva
    ]
]

series_names = [r'$\mathrm{ACC}_\mathrm{I}$ (%)', r'$\mathrm{ACC}_\mathrm{T}$ (%)', r'$\mathrm{WSR}_\mathrm{I}$ (%)', r'$\mathrm{WSR}_\mathrm{T}$ (%)']
model_names = ['BLIP', 'SigLIP', 'CLIP']
group_labels = ['w/o $L_{eva}$', 'w/ $L_{eva}$']

# 创建图形（关闭共享y轴）
fig, axes = plt.subplots(1, n_models, figsize=(18, 5), sharey=False)

# 图例用无边框色块，避免把柱子的黑描边带进 legend
handles = [
    Patch(facecolor=colors[i], edgecolor='none')
    for i in range(n_series)
]

# 绘制每个模型的柱形
for model_idx in range(n_models):
    ax = axes[model_idx]
    indices = np.zeros(n_groups_per_model)
    for i in range(1, n_groups_per_model):
        indices[i] = indices[i-1] + group_total_width + group_gap

    for series_idx in range(n_series):
        y = [data[model_idx][group_idx][series_idx] for group_idx in range(n_groups_per_model)]
        x = indices + series_idx * (bar_width + gap_between_bars)
        # 绘制柱形并保存句柄（仅保存第一个子图的句柄）
        bar = ax.bar(
            x, y,
            width=bar_width,
            color=colors[series_idx],
            edgecolor='black',
            linewidth=1.6,
        )
        ax.bar_label(
            bar,
            labels=[str(v) for v in y],
            fontsize=BAR_LABEL_SIZE,
            padding=2,
        )

    # 网格线和边框设置
    ax.grid(axis='y', linestyle='--', alpha=0.5, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)

    # x轴标签
    ax.set_xticks(indices + group_total_width / 2)
    ax.set_xticklabels(group_labels, fontsize=25, ha='center')
    ax.tick_params(axis='x', length=0)

    # 模型名称
    ax.text(
        0.5, 1.00,
        model_names[model_idx],
        fontsize=27,
        #fontweight='bold',
        ha='center',
        va='bottom',
        transform=ax.transAxes
    )

    # y轴设置（两个子图都显示标签）
    ax.set_ylim(0, 110)
    ax.set_yticks(np.arange(0, 110, 20))  # 0,20,40,...,100
    # 调整y轴标签字体大小（重点）
    ax.tick_params(axis='y', labelsize=22)  # labelsize控制y轴数据字体大小

# 强制显示图例并放在最下方
fig.legend(
    handles=handles,
    labels=series_names,
    loc='upper center',  # 相对锚点的位置
    bbox_to_anchor=(0.5, 0.25),  # y=-0.15确保在最下方
    fontsize=22,
    ncol=4
)

# 调整布局，为底部图例预留更多空间（rect的底部设为0.2）
plt.tight_layout(rect=[0, 0.2, 1, 1])
out_path = OUTPUT_DIR / "singleloss.pdf"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"已保存: {out_path}")
plt.show()
