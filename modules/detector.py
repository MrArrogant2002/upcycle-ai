"""
detector.py — Multi-model YOLO object detection with bounding box annotation.

Supported models:
  YOLOv8n   → yolov8n.pt
  YOLOv11n  → yolo11n.pt
  YOLOv12n  → yolo12n.pt
"""

from __future__ import annotations

from typing import Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

YOLO_MODELS: dict[str, dict] = {
    # ── General-purpose COCO models (80 classes) ───────────────────────────
    "YOLOv8n": {
        "weights": "yolov8n.pt",
        "description": "General-purpose — COCO 80 classes",
        "badge": "stable",
        "group": "coco",
    },
    "YOLOv11n": {
        "weights": "yolo11n.pt",
        "description": "Enhanced accuracy & speed balance",
        "badge": "recommended",
        "group": "coco",
    },
    "YOLOv12n": {
        "weights": "yolo12n.pt",
        "description": "Attention-centric architecture",
        "badge": "latest",
        "group": "coco",
    },
    # ── Custom TACO fine-tuned models (18 waste-specific classes) ──────────
    "TACO-Best": {
        "weights": "taco_yolov11n_best.pt",
        "description": "Fine-tuned on TACO waste dataset — 18 litter classes",
        "badge": "waste-tuned",
        "group": "taco",
    },
    "TACO-Trained": {
        "weights": "trained.pt",
        "description": "Full-epoch TACO checkpoint — 18 waste classes",
        "badge": "waste-tuned",
        "group": "taco",
    },
    "TACO-Last": {
        "weights": "last.pt",
        "description": "Final training checkpoint — 18 waste classes",
        "badge": "waste-tuned",
        "group": "taco",
    },
}

DEFAULT_MODEL = "TACO-Best"   # waste-specific model is more relevant for upcycling
CONFIDENCE_THRESHOLD = 0.25   # lowered from 0.35 — better coverage on occluded/piled objects
MAX_IMAGE_DIM = 1024

# Accent green used for bounding box overlays
BOX_COLOR = (74, 255, 124)          # #4AFF7C
LABEL_BG  = (13, 21, 17)            # #0D1511
LABEL_FG  = (74, 255, 124)


def _resize_if_needed(image: Image.Image) -> Image.Image:
    """Downscale image so the longest side ≤ MAX_IMAGE_DIM."""
    w, h = image.size
    if max(w, h) > MAX_IMAGE_DIM:
        scale = MAX_IMAGE_DIM / max(w, h)
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return image


def _load_model(weights: str):
    """Load YOLO model (called via cache wrapper in app.py)."""
    from ultralytics import YOLO  # deferred import keeps startup fast
    return YOLO(weights)


def detect_objects(
    image: Image.Image,
    model,                      # pre-loaded YOLO model
    conf: float = CONFIDENCE_THRESHOLD,
) -> tuple[list[str], Image.Image]:
    """
    Run YOLO inference on *image* and return detected labels + annotated image.

    Args:
        image:  PIL Image (any mode; converted to RGB internally).
        model:  Pre-loaded ultralytics YOLO model instance.
        conf:   Confidence threshold for filtering detections.

    Returns:
        labels:          Deduplicated sorted list of detected class names.
        annotated_img:   PIL Image with bounding boxes drawn in #4AFF7C.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")

    image = _resize_if_needed(image)
    img_array = np.array(image)

    results = model(img_array, conf=conf, verbose=False)

    # --- Collect detections ------------------------------------------------
    raw_labels: list[str] = []
    boxes: list[tuple[int, int, int, int, str, float]] = []

    for result in results:
        if result.boxes is None:
            continue
        for box in result.boxes:
            cls_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())
            class_name = model.names[cls_id]
            x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
            raw_labels.append(class_name)
            boxes.append((x1, y1, x2, y2, class_name, confidence))

    # --- Friendly name remapping -------------------------------------------
    remap = {
        "cell phone": "mobile phone",
        "dining table": "table",
        "potted plant": "plant",
        "wine glass": "glass",
    }
    labels = sorted({remap.get(lbl, lbl) for lbl in raw_labels})

    # --- Draw bounding boxes on a copy of the image ------------------------
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)

    try:
        font = ImageFont.truetype("arial.ttf", size=13)
    except Exception:
        font = ImageFont.load_default()

    for x1, y1, x2, y2, cls_name, conf_val in boxes:
        display_name = remap.get(cls_name, cls_name)
        # Box outline — 2 px thick by drawing twice
        draw.rectangle([x1, y1, x2, y2], outline=BOX_COLOR, width=2)

        # Label chip
        label_text = f"{display_name} {conf_val:.0%}"
        try:
            bbox = draw.textbbox((x1, y1 - 18), label_text, font=font)
            chip_x1, chip_y1 = bbox[0] - 4, bbox[1] - 2
            chip_x2, chip_y2 = bbox[2] + 4, bbox[3] + 2
        except Exception:
            chip_x1, chip_y1 = x1, max(0, y1 - 18)
            chip_x2, chip_y2 = x1 + len(label_text) * 7 + 8, y1

        draw.rectangle([chip_x1, chip_y1, chip_x2, chip_y2], fill=LABEL_BG)
        draw.text((chip_x1 + 4, chip_y1 + 2), label_text, fill=LABEL_FG, font=font)

    return labels, annotated
