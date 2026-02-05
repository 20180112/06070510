# Multimodal Trigger Generation and Conditional Backdoor Training (CLIP/OpenCLIP)

This repository provides a pipeline for multimodal trigger generation and conditional backdoor training/testing. It supports image patch triggers and text prompt triggers with cross-modal co-optimization, and includes multiple common vision datasets. This README focuses on reproducible usage without exposing any personal information.

## Features

- **Image trigger generation**: Optimize a fixed-position patch using CLIP image features (PGD-style).
- **Text trigger generation**: Learn continuous prompt embeddings via prompt learning.
- **Cross-modal co-optimization**: Alternate between image and text trigger optimization.
- **Conditional backdoor training/testing**: Evaluate four modes (clean, image-only, text-only, both).
- **Multi-dataset support**: COCO, Caltech101, DTD, OxfordPets, Food101, Flowers102, EuroSAT.

## Environment

GPU is recommended (CUDA available). Core dependencies:

- Python 3.8+
- PyTorch, torchvision
- open_clip, transformers
- accelerate, tqdm, numpy, Pillow
- scikit-learn, pycocotools (for COCO)
- scipy (for Flowers102)

Example installation (adjust as needed):

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install open_clip_torch transformers accelerate tqdm numpy pillow scikit-learn pycocotools scipy
```

## Dataset Configuration

Training and testing rely on a JSON config file. Example (trim as needed):

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

Use `--config` to point to this file.

## Paths and Placeholders

The code contains placeholders like `xxxxxx` that must be replaced before running. Common items include:

- OpenCLIP weight path (`pretrained`)
- Image trigger save/load path
- Text trigger save/load path
- Output directories (models and intermediate artifacts)

It is recommended to centralize these paths to avoid missing any replacements.

## Training

```bash
python main.py \
  --mode train \
  --dataset caltech101 \
  --config /path/to/datasets_config.json \
  --batch_size 32 \
  --num_epochs 20 \
  --learning_rate 5e-5
```

The training flow includes:

1. Load OpenCLIP model and dataset.
2. Generate or load image/text triggers.
3. Train conditional backdoor with four sample types.
4. Save model and triggers.

## Testing

```bash
python main.py \
  --mode test \
  --dataset caltech101 \
  --config /path/to/datasets_config.json \
  --model_path /path/to/clip_backdoor_model.pth \
  --test_samples 50
```

Reported metrics (per sample type):

- Clean accuracy
- Image-trigger accuracy
- Text-trigger accuracy
- Dual-trigger accuracy
- I-WSR / T-WSR (attack success rate for single triggers)

## Reproducibility Tips

- Fix random seeds (`set_seed` is provided).
- Keep preprocessing consistent (resize to 224x224).
- Use the same CLIP weights and tokenizer.
- Keep trigger position and size consistent across phases.

## Notes

This implementation is for research use only. Ensure compliance with legal and ethical requirements. For paper reproducibility, record the model weights, dataset versions, and key hyperparameters used.
