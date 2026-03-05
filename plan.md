# 🌿 AI Upcycle — Build Plan

> **Project:** AI-powered web app that detects household waste objects and suggests eco-friendly upcycling DIY ideas.
> **Stack:** Python · Streamlit · YOLOv8 · Claude API (via `anthropic` SDK)

---

## 📐 Architecture Overview

```
User (Browser)
     │
     ▼
┌─────────────────────────────────┐
│        Streamlit Frontend        │
│  - Image upload / camera input  │
│  - Results display (markdown)   │
└────────────┬────────────────────┘
             │ image bytes
             ▼
┌─────────────────────────────────┐
│        Detection Layer          │
│  YOLOv8 (ultralytics)           │
│  - Runs inference on image      │
│  - Returns: labels + bboxes     │
│  - Draws annotated image        │
└────────────┬────────────────────┘
             │ detected object names
             ▼
┌─────────────────────────────────┐
│        LLM Layer                │
│  Claude API (claude-3-haiku)    │
│  - Receives object list         │
│  - Returns structured upcycle   │
│    ideas with step-by-step DIY  │
└────────────┬────────────────────┘
             │ markdown response
             ▼
┌─────────────────────────────────┐
│     Display Layer (Streamlit)   │
│  - Annotated image              │
│  - Detected objects list        │
│  - DIY ideas in rich cards      │
└─────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
ai-upcycle/
│
├── app.py                  # Main Streamlit entry point
├── requirements.txt        # All Python dependencies
├── .env                    # API keys (not committed)
├── .gitignore
│
├── modules/
│   ├── __init__.py
│   ├── detector.py         # YOLOv8 detection logic
│   ├── llm.py              # Claude API integration
│   └── utils.py            # Image helpers, formatting
│
├── assets/
│   └── logo.png            # App branding (optional)
│
└── README.md
```

---

## 🔩 Phase-by-Phase Build Plan

---

### Phase 1 — Project Setup

**Goal:** Get a runnable skeleton with all dependencies installed.

**Tasks:**
1. Create the project folder structure above.
2. Create `requirements.txt`:
   ```
   streamlit>=1.35.0
   ultralytics>=8.2.0
   anthropic>=0.28.0
   opencv-python-headless>=4.9.0
   Pillow>=10.0.0
   python-dotenv>=1.0.0
   numpy>=1.26.0
   ```
3. Create `.env` file:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```
4. Create `.gitignore` to exclude `.env` and `__pycache__/`.
5. Verify `pip install -r requirements.txt` runs cleanly.

**Deliverable:** Clean installable project skeleton.

---

### Phase 2 — Detection Module (`modules/detector.py`)

**Goal:** Accept an image, return detected object labels + annotated image.

**Key decisions:**
- Use **YOLOv8n** (nano) — fastest, lightest, works offline, detects 80 COCO classes (bottles, cups, books, chairs, etc.)
- Model downloads automatically on first run via `ultralytics`.
- Draw bounding boxes with labels on the image for visual feedback.

**Interface:**
```python
def detect_objects(image: PIL.Image) -> tuple[list[str], PIL.Image]:
    """
    Args:
        image: PIL Image from user upload or camera.
    Returns:
        labels: Deduplicated list of detected class names.
                e.g. ["bottle", "cup", "book"]
        annotated_img: PIL Image with bounding boxes drawn.
    """
```

**Implementation notes:**
- Load model once using `@st.cache_resource` in Streamlit to avoid reloading on every interaction.
- Filter detections by confidence threshold (default: 0.35).
- Deduplicate labels — if 3 bottles detected, return `["bottle"]` not `["bottle", "bottle", "bottle"]`.
- Map COCO class names to friendlier display names where needed (e.g., `"cell phone"` → `"mobile phone"`).

**Deliverable:** `detector.py` that takes a PIL image and returns `(labels, annotated_image)`.

---

### Phase 3 — LLM Module (`modules/llm.py`)

**Goal:** Send detected objects to Claude and get structured upcycling ideas back.

**Model choice:** `claude-haiku-4-5` — fast, cheap, excellent for this task.

**Prompt design:**

```
System:
You are an eco-friendly upcycling expert and creative DIY guide.
Given a list of detected household waste objects, you will suggest
practical and creative ways to upcycle them into useful items.
For each idea, provide: a title, required materials, and clear
numbered steps. Format your response in Markdown.

User:
The following objects were detected in the image:
{objects_list}

For each object (or combination of objects), suggest 1–2 upcycling
ideas. Include:
- 🛠️ What to make
- 📦 Materials needed (using detected items + common household supplies)
- 📋 Step-by-step instructions (numbered, clear, beginner-friendly)
- ✅ Final use / benefit

Keep the tone friendly, encouraging, and eco-conscious. 🌿
```

**Interface:**
```python
def get_upcycle_ideas(detected_objects: list[str]) -> str:
    """
    Args:
        detected_objects: List of object names from YOLO.
    Returns:
        markdown_response: Rich markdown string with DIY ideas.
    """
```

**Implementation notes:**
- Use `anthropic.Anthropic()` client, load key from `.env`.
- Set `max_tokens=2048` — enough for 3–4 detailed ideas.
- Handle `anthropic.APIError` gracefully with a user-friendly error message.
- If no objects detected or list is empty, return a prompt asking the user to try a clearer image.

**Deliverable:** `llm.py` with a single clean function.

---

### Phase 4 — Streamlit Frontend (`app.py`)

**Goal:** Build a polished, intuitive UI that ties the pipeline together.

**Page layout:**

```
┌──────────────────────────────────────────────────┐
│  🌿  AI Upcycle  — Turn Waste into Something Wonderful │
├──────────────────────────────────────────────────┤
│                                                  │
│  [📷 Camera]  [📁 Upload Image]   ← Tab selector │
│                                                  │
│  ┌────────────────┐  ┌────────────────────────┐  │
│  │ Original Image │  │  Annotated Detection   │  │
│  └────────────────┘  └────────────────────────┘  │
│                                                  │
│  🔍 Detected Objects:  bottle · cup · cardboard  │
│                                                  │
│  ──────────────────────────────────────────────  │
│  💡 Upcycling Ideas                              │
│                                                  │
│  [Rich markdown cards rendered here]             │
│                                                  │
└──────────────────────────────────────────────────┘
```

**UI components:**
1. **Header** — App title, tagline, and a small eco badge.
2. **Input tabs** — Tab 1: Camera capture (`st.camera_input`). Tab 2: File uploader (`st.file_uploader`, accepts jpg/png/webp).
3. **Analyze button** — Triggers the pipeline only when clicked (avoid re-running on every state change).
4. **Two-column image display** — Original on left, YOLO-annotated on right.
5. **Detected objects pills** — Show each label as a colored badge/chip using `st.badge` or styled `st.markdown`.
6. **Ideas section** — Render the Claude response with `st.markdown()` (supports full markdown including headers, bold, lists).
7. **Download button** — `st.download_button` to download the ideas as a `.md` or `.txt` file.
8. **Footer** — "Powered by YOLOv8 + Claude | Built for sustainable living 🌍"

**Streamlit config (`st.set_page_config`):**
```python
st.set_page_config(
    page_title="AI Upcycle",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```

**State management:**
- Use `st.session_state` to store results so they persist across widget interactions without re-running detection.

**Deliverable:** Complete `app.py` with the full pipeline wired up.

---

### Phase 5 — Utilities (`modules/utils.py`)

**Goal:** Small helpers to keep other modules clean.

**Functions to include:**
```python
def pil_to_bytes(image: PIL.Image, format="JPEG") -> bytes
    # Convert PIL image to bytes for st.image display

def format_object_list(labels: list[str]) -> str
    # "bottle, cup, cardboard" → clean display string

def build_no_detection_message() -> str
    # Friendly message when YOLO finds nothing

def save_ideas_as_text(markdown: str) -> bytes
    # Encode markdown string for st.download_button
```

---

### Phase 6 — Polish & Edge Cases

**Goal:** Make the app robust and user-friendly.

**Edge cases to handle:**

| Scenario | Handling |
|---|---|
| No objects detected (confidence too low) | Show friendly "Try a clearer photo" message |
| Non-waste objects detected (person, car) | LLM prompt filters for "recyclable/waste items only" |
| API key missing | `st.error()` with setup instructions |
| Image too large | Resize to max 1024px before YOLO inference |
| Camera not available | Graceful fallback to upload-only tab |
| Network error to Claude API | Retry once, then show error with detected objects still visible |

**Performance optimisations:**
- Cache YOLOv8 model load with `@st.cache_resource`.
- Resize images before inference: `max(width, height) <= 1024px`.
- Show `st.spinner("Detecting objects...")` and `st.spinner("Generating ideas...")` during processing.

---

### Phase 7 — README & Documentation

**`README.md` sections:**
1. Project description + screenshot
2. Tech stack
3. Installation steps
4. `.env` setup
5. Run command: `streamlit run app.py`
6. Example output screenshot
7. How to extend (swap YOLO model, change LLM, add object classes)

---

## 🧩 Technology Choices — Rationale

| Component | Choice | Why |
|---|---|---|
| Frontend | Streamlit | Fastest path to a working web UI in Python; no JS needed |
| Object Detection | YOLOv8n (ultralytics) | State-of-art, 80-class detection, runs on CPU, auto-downloads |
| LLM | Claude API (Haiku) | Fast, affordable, excellent instruction following, rich markdown output |
| Image handling | Pillow + OpenCV | Industry standard; cv2 for YOLO, PIL for Streamlit display |
| Config | python-dotenv | Simple `.env` based API key management |

**Free alternative if no API key:**
- Use `ollama` with `llama3` running locally — swap `llm.py` to use `ollama.chat()` instead of `anthropic`. Zero cost, fully offline.

---

## 🚀 Run Instructions (Final)

```bash
# 1. Clone / create project
cd ai-upcycle

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# 4. Launch
streamlit run app.py
```

App opens at `http://localhost:8501` 🎉

---

## 🔮 Future Enhancements (Post-MVP)

| Feature | Description |
|---|---|
| Custom YOLO fine-tuning | Train on a waste-specific dataset (TACO dataset) for better accuracy on trash items |
| Idea history | Save past upcycling sessions to a local SQLite DB |
| Difficulty filter | Let user select Easy / Medium / Advanced DIY complexity |
| Multi-language support | Translate output for regional accessibility |
| Share button | Generate a shareable link or image card of the upcycling idea |
| Mobile PWA | Wrap Streamlit app as a Progressive Web App for phone use |

---

*Plan version 1.0 — AI Upcycle Project for Environmental Sustainable Development* 🌍♻️