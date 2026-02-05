# 多模态触发器生成与条件后门训练（CLIP/OpenCLIP）

本仓库包含一套面向多模态模型的触发器生成与条件后门训练/测试流程，覆盖图像触发器（Patch）与文本触发器（Prompt）协同优化，并支持多个常见视觉数据集。本文档提供最小可复现的使用说明与配置指引，避免泄露任何个人信息。

## 功能概览

- **图像触发器生成**：基于 CLIP 图像特征，采用 PGD 形式优化固定位置 Patch。
- **文本触发器生成**：基于连续提示学习（Prompt Learning）优化触发文本嵌入。
- **跨模态协同优化**：交替优化图像/文本触发器以增强联合触发效果。
- **条件后门训练/测试**：同时评估常规样本、仅图像触发、仅文本触发、双触发四种模式。
- **多数据集支持**：COCO、Caltech101、DTD、OxfordPets、Food101、Flowers102、EuroSAT 等。

## 运行环境

建议使用具备 GPU 的环境（CUDA 可用）。基本依赖包括：

- Python 3.8+
- PyTorch、torchvision
- open_clip、transformers
- accelerate、tqdm、numpy、Pillow
- scikit-learn、pycocotools（COCO 用）
- scipy（Flowers102 用）

示例安装命令（根据实际环境调整）：

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install open_clip_torch transformers accelerate tqdm numpy pillow scikit-learn pycocotools scipy
```

## 数据集配置

训练与测试依赖一个 JSON 配置文件，示例如下（按需裁剪）：

```json
{
  "caltech101": {
    "name": "Caltech101",
    "root_dir": "/path/to/caltech101",
    "image_dir": "101_ObjectCategories",
    "test_size": 0.2
  },
  "coco": {
    "name": "COCO",
    "root_dir": "/path/to/coco",
    "train_images": "train2017",
    "val_images": "val2017",
    "captions_train": "annotations/captions_train2017.json",
    "captions_val": "annotations/captions_val2017.json",
    "instances_train": "annotations/instances_train2017.json",
    "instances_val": "annotations/instances_val2017.json",
    "class_names": ["person", "bicycle", "car"]
  }
}
```

在命令行参数中通过 `--config` 指定该文件路径。

## 关键路径与占位符

代码中存在若干需要手动替换的占位符（如 `xxxxxx`），请在运行前统一配置，常见位置包括：

- OpenCLIP 权重路径（`pretrained`）
- 图像触发器保存/加载路径
- 文本触发器保存/加载路径
- 训练输出目录（模型与中间结果）

建议将这些路径集中整理，避免散落硬编码导致遗漏。

## 训练

```bash
python main.py \
  --mode train \
  --dataset caltech101 \
  --config /path/to/datasets_config.json \
  --batch_size 32 \
  --num_epochs 20 \
  --learning_rate 5e-5
```

训练流程包括：

1. 加载 OpenCLIP 模型与数据集。
2. 生成或加载图像/文本触发器。
3. 条件后门训练（四种样本类型联合优化）。
4. 保存模型与触发器。

## 测试

```bash
python main.py \
  --mode test \
  --dataset caltech101 \
  --config /path/to/datasets_config.json \
  --model_path /path/to/clip_backdoor_model.pth \
  --test_samples 50
```

测试会输出以下指标（按样本类型分别统计）：

- 常规样本准确率
- 仅图像触发准确率
- 仅文本触发准确率
- 双触发准确率
- I-WSR / T-WSR（仅触发攻击成功率）

## 复现与稳定性建议

- 设置固定随机种子（代码已包含 `set_seed`）。
- 确保数据预处理一致（统一 Resize 到 224×224）。
- 使用相同的 CLIP 权重与 tokenizer。
- 触发器位置与尺寸需与训练配置一致。

## 备注

该实现用于研究目的，请在合法合规与伦理框架下使用。若用于论文复现，请明确记录所用权重、数据集版本与关键超参数。
