"""
utils.py — Shared helper utilities for AI Upcycle.
"""

from __future__ import annotations

import io
import base64
from PIL import Image


def pil_to_bytes(image: Image.Image, fmt: str = "JPEG") -> bytes:
    """Convert a PIL Image to raw bytes (for st.image or download)."""
    buf = io.BytesIO()
    if fmt.upper() == "JPEG" and image.mode != "RGB":
        image = image.convert("RGB")
    image.save(buf, format=fmt)
    return buf.getvalue()


def pil_to_base64(image: Image.Image, fmt: str = "PNG") -> str:
    """Encode PIL Image as a base64 data URI string."""
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode()
    mime = "image/png" if fmt.upper() == "PNG" else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def format_object_list(labels: list[str]) -> str:
    """Return a clean human-readable comma-separated string of object labels."""
    if not labels:
        return "—"
    return "  ·  ".join(lbl.capitalize() for lbl in labels)


def build_no_detection_message() -> str:
    """User-friendly message shown when YOLO finds no objects."""
    return (
        "## 🔍 No Objects Detected\n\n"
        "YOLO didn't find any recognisable objects above the confidence threshold.\n\n"
        "**Try:**\n"
        "- Better lighting\n"
        "- Moving closer to the object\n"
        "- A different angle\n"
    )


def save_ideas_as_bytes(markdown: str) -> bytes:
    """Encode a markdown string as UTF-8 bytes for st.download_button."""
    return markdown.encode("utf-8")


def object_tags_html(labels: list[str]) -> str:
    """Render object labels as styled pill tags (raw HTML for st.markdown)."""
    if not labels:
        return "<p style='color:#6B8A72;font-style:italic;'>No objects detected.</p>"
    pills = "".join(
        f"<span style='"
        f"display:inline-block;margin:4px 6px 4px 0;"
        f"padding:4px 14px;"
        f"background:#1A2B20;"
        f"border:1px solid #2A6644;"
        f"border-radius:999px;"
        f"color:#4AFF7C;"
        f"font-family:JetBrains Mono,monospace;"
        f"font-size:13px;"
        f"letter-spacing:0.03em;"
        f"'>{lbl}</span>"
        for lbl in labels
    )
    return f"<div style='margin:8px 0 16px;'>{pills}</div>"
