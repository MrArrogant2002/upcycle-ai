"""
app.py — AI Upcycle · Main Streamlit entry point.

Aesthetic: Organic Futurism — dark forest floors lit by bioluminescent green.
Models:    YOLOv8n · YOLOv11n · YOLOv12n (user-selectable)
LLM:       Gemini 2.0 Flash via Google AI Studio
"""

from __future__ import annotations

import streamlit as st
from PIL import Image

# ─────────────────────────────────────────────────────────────────────────────
# Page config (MUST be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Upcycle",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS — full design system injection
# ─────────────────────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
/* ── Google Fonts ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Design tokens ────────────────────────────────────────────────────────── */
:root {
  --bg-primary:   #0D1511;
  --bg-surface:   #131F18;
  --bg-elevated:  #1A2B20;
  --accent:       #4AFF7C;
  --accent-muted: #2A6644;
  --amber:        #F4A227;
  --text:         #EAE2D0;
  --text-muted:   #6B8A72;
  --border:       #1E3328;
  --radius-sm:    6px;
  --radius-md:    12px;
}

/* ── Global reset ─────────────────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.stApp { background-color: var(--bg-primary) !important; }
.stApp > div { background-color: var(--bg-primary) !important; }

/* Grain overlay */
.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 9999;
}

section[data-testid="stSidebar"] { background: var(--bg-surface) !important; }

/* Block container */
.block-container {
  padding: 0 !important;
  max-width: 100% !important;
}

/* ── Typography ───────────────────────────────────────────────────────────── */
body, .stMarkdown, .stText, p, li, label {
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text) !important;
}
h1, h2, h3, h4, h5, h6 {
  font-family: 'Instrument Serif', serif !important;
  color: var(--text) !important;
}
code, pre {
  font-family: 'JetBrains Mono', monospace !important;
}

/* ── Scrollbar ────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-surface); }
::-webkit-scrollbar-thumb { background: var(--accent-muted); border-radius: 3px; }

/* ── Navigation bar ───────────────────────────────────────────────────────── */
.nav-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 32px;
  background: rgba(13,21,17,0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}
.nav-logo {
  font-family: 'DM Sans', sans-serif;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 0.06em;
  color: var(--text);
}
.nav-logo span { color: var(--accent); }
.nav-link {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: none;
  border: 1px solid var(--border);
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  transition: all 200ms ease;
}
.nav-link:hover { border-color: var(--accent-muted); color: var(--accent); }

/* ── Hero section ─────────────────────────────────────────────────────────── */
.hero-section {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 32px 14px;
  overflow: hidden;
  border-bottom: 1px solid var(--border);
}
.hero-glow {
  position: absolute;
  top: 50%;
  left: 30%;
  transform: translate(-50%, -50%);
  width: 400px;
  height: 120px;
  background: radial-gradient(ellipse at center, rgba(42,102,68,0.14) 0%, transparent 70%);
  pointer-events: none;
}
.hero-headline {
  font-family: 'Instrument Serif', serif !important;
  font-size: clamp(22px, 3vw, 30px) !important;
  line-height: 1.1 !important;
  letter-spacing: -0.01em !important;
  color: var(--text) !important;
  margin: 0 !important;
  position: relative;
  z-index: 1;
}
.hero-headline em {
  font-style: italic;
  color: var(--accent);
}
.hero-sub {
  font-family: 'DM Sans', sans-serif;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0;
  position: relative;
  z-index: 1;
}

/* ── Marquee strip ────────────────────────────────────────────────────────── */
.marquee-wrapper {
  overflow: hidden;
  border-bottom: 1px solid var(--border);
  padding: 7px 0;
  background: var(--bg-surface);
}
.marquee-track {
  display: flex;
  width: max-content;
  animation: marquee 30s linear infinite;
}
.marquee-item {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--text-muted);
  padding: 0 24px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.marquee-item span { color: var(--accent); margin-right: 12px; }
@keyframes marquee {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}

/* ── Section wrapper ─────────────────────────────────────────────────────── */
.section-wrap {
  max-width: 1280px;
  margin: 0 auto;
  padding: 16px 24px 24px;
}
.section-title {
  font-family: 'Instrument Serif', serif !important;
  font-size: 11px !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  color: var(--text-muted) !important;
  margin: 0 0 10px !important;
}
.section-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 14px 0;
}

/* ── Input zone ──────────────────────────────────────────────────────────── */
.input-zone {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 28px;
  margin-bottom: 24px;
}

/* ── Upload drop zone override ────────────────────────────────────────────── */
[data-testid="stFileUploader"] > div:first-child {
  background: var(--bg-surface) !important;
  border: 2px dashed var(--accent-muted) !important;
  border-radius: var(--radius-md) !important;
}
[data-testid="stFileUploader"] > div:first-child:hover {
  border-color: var(--accent) !important;
  box-shadow: inset 0 0 30px rgba(74,255,124,0.05) !important;
}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p {
  color: var(--text-muted) !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* Camera input */
[data-testid="stCameraInput"] div {
  border: 2px dashed var(--accent-muted) !important;
  border-radius: var(--radius-md) !important;
  background: var(--bg-elevated) !important;
}

/* ── Primary CTA button ───────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
  background: transparent !important;
  border: 1.5px solid var(--accent) !important;
  color: var(--accent) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important;
  font-size: 14px !important;
  letter-spacing: 0.04em !important;
  padding: 10px 20px !important;
  border-radius: var(--radius-sm) !important;
  transition: background 200ms ease, color 200ms ease !important;
  animation: ctaPulse 3s ease infinite !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--accent) !important;
  color: var(--bg-primary) !important;
  animation: none !important;
}

/* ── Secondary button (unselected model cards) ────────────────────────────── */
.stButton > button[kind="secondary"] {
  background: transparent !important;
  border: 1.5px solid var(--border) !important;
  color: var(--text-muted) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 400 !important;
  font-size: 13px !important;
  letter-spacing: 0.03em !important;
  padding: 8px 16px !important;
  border-radius: var(--radius-sm) !important;
  transition: border-color 200ms ease, color 200ms ease !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: var(--accent-muted) !important;
  color: var(--text) !important;
}

@keyframes ctaPulse {
  0%   { box-shadow: 0 0 0 0   rgba(74,255,124,0.4); }
  70%  { box-shadow: 0 0 0 12px rgba(74,255,124,0); }
  100% { box-shadow: 0 0 0 0   rgba(74,255,124,0); }
}

/* ── Image panels ─────────────────────────────────────────────────────────── */
.img-panel {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
  padding: 0;
}
.img-panel-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.10em;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: 10px 14px 8px;
  border-bottom: 1px solid var(--border);
}
[data-testid="stImage"] { border-radius: var(--radius-md); }

/* ── Object tags ──────────────────────────────────────────────────────────── */
.tag-pill {
  display: inline-block;
  margin: 4px 6px 4px 0;
  padding: 4px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--accent-muted);
  border-radius: 999px;
  color: var(--accent);
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  letter-spacing: 0.03em;
  transition: border-color 200ms ease, background 200ms ease;
}
.tag-pill:hover {
  border-color: var(--accent);
  background: var(--border);
}

/* ── Progress bar ─────────────────────────────────────────────────────────── */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--accent-muted), var(--accent)) !important;
  transition: width 400ms ease-out !important;
}
.stProgress > div > div {
  background: var(--bg-elevated) !important;
  height: 4px !important;
  border-radius: 999px !important;
}

/* ── Spinner ──────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div {
  border-color: var(--accent) transparent transparent transparent !important;
}
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] label {
  color: var(--text-muted) !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ── Idea cards ───────────────────────────────────────────────────────────── */
.idea-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 24px;
  margin-bottom: 16px;
  transition: border-color 250ms ease, box-shadow 250ms ease;
  animation: fadeInUp 400ms ease both;
}
.idea-card:hover {
  border-color: var(--accent-muted);
  box-shadow: 0 0 40px rgba(74,255,124,0.06);
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Markdown inside idea cards */
.ideas-output h1, .ideas-output h2, .ideas-output h3 {
  font-family: 'Instrument Serif', serif !important;
  color: var(--text) !important;
}
.ideas-output p, .ideas-output li {
  color: var(--text-muted) !important;
  line-height: 1.7 !important;
}
.ideas-output strong { color: var(--text) !important; }
.ideas-output code   { color: var(--accent) !important; background: var(--bg-elevated) !important; }
.ideas-output hr     { border-color: var(--border) !important; }

/* ── Tabs override ────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
  background: var(--bg-surface) !important;
  border-bottom: 1px solid var(--border) !important;
  padding: 0 4px;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  gap: 4px;
}
[data-testid="stTabs"] [role="tab"] {
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text-muted) !important;
  border-radius: var(--radius-sm) !important;
  padding: 8px 16px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--accent) !important;
  border-bottom: 2px solid var(--accent) !important;
  background: transparent !important;
}
[data-testid="stTabs"] [role="tabpanel"] {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
  padding: 24px !important;
}

/* ── Select / radio boxes ─────────────────────────────────────────────────── */
[data-testid="stRadio"] label,
[data-testid="stSelectbox"] label {
  color: var(--text-muted) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label {
  background: var(--bg-surface) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  padding: 8px 14px !important;
  transition: border-color 150ms ease !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label:hover {
  border-color: var(--accent-muted) !important;
}
[data-testid="stSelectbox"] > div > div {
  background: var(--bg-surface) !important;
  border: 1.5px solid var(--border) !important;
  color: var(--text) !important;
}

/* ── Alert / info boxes ───────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  background: var(--bg-elevated) !important;
  border-left: 3px solid var(--accent) !important;
  color: var(--text) !important;
}

/* ── Multiselect ──────────────────────────────────────────────────────────── */
[data-testid="stMultiSelect"] > div > div {
  background: var(--bg-surface) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
}
[data-testid="stMultiSelect"] > div > div:focus-within {
  border-color: var(--accent-muted) !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--accent-muted) !important;
  border-radius: 999px !important;
  color: var(--accent) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 12px !important;
}
[data-testid="stMultiSelect"] input {
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stMultiSelect"] label {
  font-size: 12px !important;
  color: var(--text-muted) !important;
}

/* ── Text input ───────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] > div > div > input {
  background: var(--bg-surface) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
}
[data-testid="stTextInput"] > div > div > input:focus {
  border-color: var(--accent-muted) !important;
  box-shadow: 0 0 0 1px var(--accent-muted) !important;
}

/* ── Footer ───────────────────────────────────────────────────────────────── */
.app-footer {
  text-align: center;
  padding: 32px 16px 40px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  border-top: 1px solid var(--border);
  margin-top: 48px;
}
.app-footer span { color: var(--accent); }

/* ── Scanline animation ───────────────────────────────────────────────────── */
.scan-container {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-md);
}
.scan-container::after {
  content: "";
  position: absolute;
  left: 0;
  width: 100%;
  height: 2px;
  background: rgba(74,255,124,0.25);
  animation: scanLine 2s linear infinite;
  pointer-events: none;
}
@keyframes scanLine {
  from { top: 0%; }
  to   { top: 100%; }
}

/* ── Download button ─────────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] button {
  background: transparent !important;
  border: 1px solid var(--accent-muted) !important;
  color: var(--text-muted) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 14px !important;
}
[data-testid="stDownloadButton"] button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
}

/* ── Reduced motion ───────────────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
  }
}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Lazy imports
# ─────────────────────────────────────────────────────────────────────────────

from modules.detector import YOLO_MODELS, DEFAULT_MODEL, CONFIDENCE_THRESHOLD as _DEFAULT_CONF, detect_objects, _load_model
from modules.llm import get_upcycle_ideas
from modules.utils import pil_to_bytes, object_tags_html, save_ideas_as_bytes

# ─────────────────────────────────────────────────────────────────────────────
# Cached model loader
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def cached_load_model(model_key: str):
    weights = YOLO_MODELS[model_key]["weights"]
    return _load_model(weights)

# ─────────────────────────────────────────────────────────────────────────────
# Compact inline hero  (nav + headline + tagline in one bar)
# ─────────────────────────────────────────────────────────────────────────────

MARQUEE_ITEMS = [
    "bottle", "cardboard", "glass", "newspaper", "plastic",
    "tin can", "fabric", "wood", "paper", "wire", "cork", "pallet",
]
items_html = "".join(
    f'<span class="marquee-item"><span>✦</span>{item}</span>'
    for item in MARQUEE_ITEMS * 4
)

st.markdown(
    f"""
    <nav class="nav-bar">
      <div class="nav-logo"><span>♻</span> AI UPCYCLE</div>
      <a class="nav-link" href="https://github.com" target="_blank">GitHub ↗</a>
    </nav>
    <div class="hero-section">
      <div class="hero-glow"></div>
      <div style="z-index:1;">
        <h1 class="hero-headline">See the <em>Second Life</em> in Every Object.</h1>
        <p class="hero-sub">Point your camera at waste · Get instant upcycling ideas</p>
      </div>
    </div>
    <div class="marquee-wrapper"><div class="marquee-track">{items_html}</div></div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────────────────────────────────────

if "selected_model" not in st.session_state:
    st.session_state.selected_model = DEFAULT_MODEL

# ─────────────────────────────────────────────────────────────────────────────
# Two-panel layout — LEFT: controls  |  RIGHT: results
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-wrap">', unsafe_allow_html=True)

left, right = st.columns([1, 1.55], gap="large")

# ═══════════════════════════════════════════════════════════════════════════
# LEFT PANEL — Model, Confidence, Image Input, Button
# ═══════════════════════════════════════════════════════════════════════════

with left:

    # ── Model selection ────────────────────────────────────────────────────
    st.markdown('<p class="section-title">① Detection Model</p>', unsafe_allow_html=True)

    model_names = list(YOLO_MODELS.keys())
    coco_models  = [n for n in model_names if YOLO_MODELS[n]["group"] == "coco"]
    taco_models  = [n for n in model_names if YOLO_MODELS[n]["group"] == "taco"]

    def _render_model_row(names: list[str]) -> None:
        row_cols = st.columns(3, gap="small")
        for rcol, name in zip(row_cols, names):
            info = YOLO_MODELS[name]
            is_active = name == st.session_state.selected_model
            bc  = "#4AFF7C" if is_active else "#1E3328"
            bg  = "#1A2B20" if is_active else "#131F18"
            glow = "box-shadow:0 0 20px rgba(74,255,124,0.10);" if is_active else ""
            bdc = "#4AFF7C" if is_active else ("#F4A227" if info["group"]=="taco" else "#2A6644")
            bdbg = "rgba(74,255,124,0.07)" if is_active else "transparent"
            ck  = "<span style='float:right;font-size:11px;color:#4AFF7C;'>✔</span>" if is_active else ""
            badge_color_text = "#F4A227" if info["group"]=="taco" and not is_active else bdc
            with rcol:
                st.markdown(
                    f"""<div style="background:{bg};border:1.5px solid {bc};border-radius:10px;
                        padding:11px 13px 10px;{glow}cursor:default;">
                      <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
                                  font-weight:600;color:#4AFF7C;margin-bottom:4px;">{name}{ck}</div>
                      <div style="font-size:11px;color:#6B8A72;line-height:1.35;margin-bottom:8px;">
                        {info['description']}</div>
                      <span style="font-family:'JetBrains Mono',monospace;font-size:9px;
                        color:{badge_color_text};background:{bdbg};border:1px solid {badge_color_text};
                        border-radius:3px;padding:1px 5px;text-transform:uppercase;
                        letter-spacing:0.05em;">{info['badge']}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
                if st.button(
                    "✔ Active" if is_active else "Select",
                    key=f"sel_{name}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    if not is_active:
                        st.session_state.selected_model = name
                        for k in ("labels", "annotated_img", "ideas", "orig_img"):
                            st.session_state.pop(k, None)
                        st.rerun()

    # Row 1 — COCO
    st.markdown(
        "<p style='font-size:10px;letter-spacing:0.12em;text-transform:uppercase;"
        "color:#6B8A72;margin:0 0 6px;'>COCO — 80 general classes</p>",
        unsafe_allow_html=True,
    )
    _render_model_row(coco_models)

    # Row 2 — TACO
    st.markdown(
        "<p style='font-size:10px;letter-spacing:0.12em;text-transform:uppercase;"
        "color:#F4A227;margin:10px 0 6px;'>TACO — 18 waste-specific classes 🟡</p>",
        unsafe_allow_html=True,
    )
    _render_model_row(taco_models)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Confidence slider ─────────────────────────────────────────────────
    st.markdown('<p class="section-title">② Confidence Threshold</p>', unsafe_allow_html=True)

    conf_threshold = st.slider(
        "conf",
        min_value=0.10, max_value=0.75,
        value=st.session_state.get("conf_threshold", _DEFAULT_CONF),
        step=0.05, format="%.2f",
        label_visibility="collapsed",
        help="Lower → detects more objects (may include noise). Higher → fewer but surer.",
    )
    st.session_state.conf_threshold = conf_threshold

    if conf_threshold <= 0.20:
        hint_icon, hint_color, hint_text = "⚠️", "#F4A227", "Very sensitive — expect noise"
    elif conf_threshold <= 0.30:
        hint_icon, hint_color, hint_text = "🟡", "#F4A227", "Good for cluttered scenes"
    elif conf_threshold <= 0.45:
        hint_icon, hint_color, hint_text = "🟢", "#4AFF7C", "Balanced — works for most images"
    else:
        hint_icon, hint_color, hint_text = "🔵", "#6B8A72", "Strict — high-confidence only"
    st.markdown(
        f"<p style='margin:2px 0 0;font-size:12px;color:{hint_color};'>"
        f"{hint_icon} {hint_text}</p>",
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Image input ───────────────────────────────────────────────────────
    st.markdown('<p class="section-title">③ Image Input</p>', unsafe_allow_html=True)

    source_image: Image.Image | None = None
    input_tab, camera_tab = st.tabs(["📁 Upload", "📷 Camera"])

    with input_tab:
        uploaded = st.file_uploader(
            "Drag & drop or click to upload",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )
        if uploaded:
            source_image = Image.open(uploaded).convert("RGB")
            st.session_state.orig_img = source_image

    with camera_tab:
        camera_snap = st.camera_input("Take a photo", label_visibility="collapsed")
        if camera_snap:
            source_image = Image.open(camera_snap).convert("RGB")
            st.session_state.orig_img = source_image

    # Compact thumbnail preview
    if source_image is not None:
        st.image(source_image, caption="Preview", width=260)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Detect button ─────────────────────────────────────────────────────
    run_analysis = st.button(
        "🔍  Detect & Upcycle",
        disabled=(source_image is None),
        use_container_width=True,
        type="primary",
    )
    if source_image is None:
        st.markdown(
            "<p style='font-size:12px;color:#6B8A72;margin:6px 0 0;'>"
            "Upload or capture an image to begin.</p>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<p style='font-size:12px;color:#6B8A72;margin:6px 0 0;'>"
            f"Model: <span style='color:#4AFF7C;'>{st.session_state.selected_model}</span>"
            f" · conf {conf_threshold:.2f}</p>",
            unsafe_allow_html=True,
        )

# ═══════════════════════════════════════════════════════════════════════════
# Pipeline execution (runs before right panel renders)
# ═══════════════════════════════════════════════════════════════════════════

if run_analysis and source_image is not None:
    progress = st.progress(0, text="Loading model…")
    model = cached_load_model(st.session_state.selected_model)
    progress.progress(20, text=f"Running {st.session_state.selected_model}…")

    with st.spinner(f"Detecting…"):
        labels, annotated = detect_objects(
            source_image, model,
            conf=st.session_state.get("conf_threshold", _DEFAULT_CONF),
        )
        st.session_state.labels = labels
        st.session_state.annotated_img = annotated
        # Initialise effective list from fresh detection; clear any stale ideas
        st.session_state.effective_labels = list(labels)
        st.session_state._last_scan_labels = list(labels)
        st.session_state.pop("ideas", None)

    progress.progress(100, text="Detection complete!")
    progress.empty()
    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — Results
# ═══════════════════════════════════════════════════════════════════════════

with right:
    has_results = "labels" in st.session_state and "annotated_img" in st.session_state

    if not has_results:
        # Empty state
        st.markdown(
            """
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                        min-height:420px;border:1.5px dashed #1E3328;border-radius:12px;
                        background:#131F18;text-align:center;padding:40px 24px;">
              <div style="font-size:40px;margin-bottom:16px;opacity:0.4;">♻</div>
              <p style="font-family:'Instrument Serif',serif;font-size:20px;
                        color:#EAE2D0;margin:0 0 8px;">Results appear here</p>
              <p style="font-size:13px;color:#6B8A72;max-width:280px;line-height:1.5;margin:0;">
                Select a model, set confidence, upload an image and click
                <strong style="color:#4AFF7C;">Detect & Upcycle</strong>.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        orig_img: Image.Image = st.session_state.get("orig_img", source_image)
        ann_img: Image.Image  = st.session_state.annotated_img
        labels: list[str]     = st.session_state.labels

        # ── Image panels ────────────────────────────────────────────────
        st.markdown('<p class="section-title">Detection Results</p>', unsafe_allow_html=True)
        img_l, img_r = st.columns(2, gap="small")
        with img_l:
            st.markdown(
                '<div class="img-panel"><div class="img-panel-label">ORIGINAL</div>',
                unsafe_allow_html=True,
            )
            if orig_img:
                st.image(orig_img, width="stretch")
            st.markdown("</div>", unsafe_allow_html=True)
        with img_r:
            st.markdown(
                f'<div class="img-panel"><div class="img-panel-label">'
                f'ANNOTATED — {st.session_state.selected_model}</div>',
                unsafe_allow_html=True,
            )
            st.image(ann_img, width="stretch")
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Detected tags + manual editor ────────────────────────────────
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Objects (edit before generating ideas)</p>', unsafe_allow_html=True)

        # Initialise effective_labels from YOLO results (only on fresh scan)
        if "effective_labels" not in st.session_state or \
                st.session_state.get("_last_scan_labels") != labels:
            st.session_state.effective_labels = list(labels)
            st.session_state._last_scan_labels = list(labels)

        # Show what YOLO found as read-only reference pills
        if labels:
            st.markdown(
                "<p style='font-size:11px;color:#6B8A72;margin:0 0 4px;letter-spacing:0.06em;"
                "text-transform:uppercase;'>Detected by YOLO</p>",
                unsafe_allow_html=True,
            )
            st.markdown(object_tags_html(labels), unsafe_allow_html=True)
        else:
            st.markdown(
                "<p style='color:#6B8A72;font-style:italic;font-size:12px;margin-bottom:6px;'>"
                "Nothing detected — you can still add objects manually below.</p>",
                unsafe_allow_html=True,
            )

        # ── Deselect detected / add from suggestions ─────────────────────
        COMMON_WASTE = [
            "bottle", "plastic bag", "cardboard", "newspaper", "glass", "can",
            "tin can", "cup", "carton", "aluminium foil", "straw", "bottle cap",
            "styrofoam", "paper", "fabric", "wood plank", "wire", "cork",
            "pallet", "rubber", "ceramic", "metal sheet", "rope", "cd/dvd",
            "light bulb", "battery", "paint can", "egg carton", "jar", "bowl",
        ]
        # Include any custom-added objects so they appear as valid options
        all_options = sorted(set(
            labels + COMMON_WASTE + st.session_state.get("effective_labels", [])
        ))

        # Explicitly pre-initialize the multiselect widget state before rendering.
        # Using `default=` with `key=` is unreliable — Streamlit ignores `default`
        # if the key already exists in session_state. Pre-initializing here ensures
        # detected + custom objects are always shown as selected on every render.
        if "multiselect_objects" not in st.session_state:
            st.session_state["multiselect_objects"] = [
                l for l in st.session_state.effective_labels if l in all_options
            ]

        # on_change syncs multiselect → effective_labels ONLY when the user
        # actually interacts with it (add/remove), not on every plain rerun.
        def _sync_multiselect():
            st.session_state.effective_labels = list(dict.fromkeys(
                st.session_state.get("multiselect_objects", [])
            ))

        st.multiselect(
            "Active object list (uncheck to remove, pick from list to add):",
            options=all_options,
            key="multiselect_objects",
            on_change=_sync_multiselect,
            label_visibility="visible",
        )

        # ── Free-text custom input ────────────────────────────────────────
        st.markdown(
            "<p style='font-size:11px;color:#6B8A72;margin:8px 0 2px;letter-spacing:0.06em;"
            "text-transform:uppercase;'>Add a custom object not in the list</p>",
            unsafe_allow_html=True,
        )
        add_col, btn_col = st.columns([4, 1], gap="small")
        with add_col:
            custom_input = st.text_input(
                "custom_obj",
                placeholder="e.g. wooden crate, old mirror…",
                label_visibility="collapsed",
                key="custom_obj_input",
            )
        with btn_col:
            add_clicked = st.button("＋ Add", use_container_width=True, key="add_custom_btn")

        if add_clicked and custom_input.strip():
            new_obj = custom_input.strip().lower()
            current = list(st.session_state.get("effective_labels", []))
            if new_obj not in current:
                current.append(new_obj)
            st.session_state.effective_labels = current
            # Drop the widget key so it re-initializes with the updated list on next render
            st.session_state.pop("multiselect_objects", None)
            st.session_state.pop("custom_obj_input", None)
            st.rerun()

        # Show current effective list
        effective = st.session_state.effective_labels
        if effective:
            st.markdown(
                "<p style='font-size:11px;color:#6B8A72;margin:8px 0 4px;letter-spacing:0.06em;"
                "text-transform:uppercase;'>Final list sent to AI</p>",
                unsafe_allow_html=True,
            )
            st.markdown(object_tags_html(effective), unsafe_allow_html=True)
        else:
            st.markdown(
                "<p style='color:#F4A227;font-size:12px;margin:6px 0;'>"
                "⚠️ No objects in list — add at least one to generate ideas.</p>",
                unsafe_allow_html=True,
            )

        # ── Ideas ────────────────────────────────────────────────────────
        if "ideas" in st.session_state:
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">Upcycling Ideas</p>', unsafe_allow_html=True)
            st.markdown('<div class="ideas-output">', unsafe_allow_html=True)
            st.markdown(st.session_state.ideas)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Actions row ──────────────────────────────────────────────────
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        act_l, act_mid, act_r = st.columns(3, gap="small")
        with act_l:
            regen_clicked = st.button(
                "✨ Regenerate Ideas",
                use_container_width=True,
                type="primary",
                disabled=(not effective),
                key="regen_btn",
            )
        with act_mid:
            if "ideas" in st.session_state:
                st.download_button(
                    label="⬇ Download (.md)",
                    data=save_ideas_as_bytes(st.session_state.ideas),
                    file_name="upcycle_ideas.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
        with act_r:
            if st.button("↩ Scan Again", use_container_width=True):
                for k in ("labels", "annotated_img", "ideas", "orig_img",
                          "effective_labels", "_last_scan_labels"):
                    st.session_state.pop(k, None)
                st.rerun()

        # Regenerate on button click
        if regen_clicked and effective:
            with st.spinner("Regenerating ideas…"):
                from modules.llm import get_upcycle_ideas as _get_ideas
                st.session_state.ideas = _get_ideas(effective)
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("</div>", unsafe_allow_html=True)  # close .section-wrap

st.markdown(
    f"""
    <div class="app-footer">
      Powered by <span>{st.session_state.get('selected_model', DEFAULT_MODEL)}</span>
      &nbsp;·&nbsp; <span>Gemini 2.0 Flash</span>
      &nbsp;·&nbsp; Built for sustainable living 🌍
    </div>
    """,
    unsafe_allow_html=True,
)
