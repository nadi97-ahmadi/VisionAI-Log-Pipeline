# VisionLog AI

**AI-powered multimodal field inspection & automated reporting platform.**

VisionLog AI turns raw inspection footage and a spoken voice note into a clean, audit-ready PDF report in seconds. It combines computer vision (YOLOv8) with automatic speech recognition (Whisper) and a PDF generator, all running on CPU — no GPU or paid cloud API required.

Upload a video and an audio note, and the app returns detected defects with confidence scores, annotated frames, and a timestamped transcript, compiled into a downloadable report.

---

## Demo

> 🔗 **Live app:** [add your Streamlit Cloud URL here]
>
> 🎥 **Walkthrough video:** [add a link to your screen recording here]

*(Add 2–3 screenshots here: the upload screen, the detection table, and the annotated frames.)*

---

## How It Works

The app runs a three-stage multimodal pipeline:

```
        ┌──────────────────────────────────────────────┐
        │            Streamlit Web Dashboard            │
        │   (file upload + in-browser camera & mic)     │
        └──────┬─────────────────────────────────┬──────┘
               │                                 │
        [ Inspection Video ]            [ Operator Voice Note ]
               │                                 │
               ▼                                 ▼
       ┌───────────────┐                 ┌───────────────┐
       │ OpenCV decode │                 │  Audio decode │
       └───────┬───────┘                 └───────┬───────┘
               │                                 │
               ▼                                 ▼
       ┌───────────────┐                 ┌───────────────┐
       │ YOLOv8 Nano   │                 │ Whisper Tiny  │
       │ defect boxes  │                 │ transcript +  │
       │ + confidence  │                 │ timestamps    │
       └───────┬───────┘                 └───────┬───────┘
               │                                 │
               └───────────────┬─────────────────┘
                               ▼
                     ┌────────────────────┐
                     │ PyMuPDF generator  │
                     │ compiles PDF report│
                     └─────────┬──────────┘
                               ▼
                     ┌────────────────────┐
                     │  Audit-ready PDF   │
                     │  + inline preview  │
                     └────────────────────┘
```

| Layer | Technology | Notes |
|---|---|---|
| Web UI | Streamlit | Responsive layout for desktop and mobile browsers |
| Speech-to-text | openai-whisper (Tiny) | Runs locally on CPU |
| Computer vision | Ultralytics YOLOv8 (Nano) | CPU inference; frame sampling for speed |
| PDF compiler | PyMuPDF (fitz) | Builds tables, metadata, and embedded frames |

---

## Model & Dataset

VisionLog AI uses the open-source pretrained model
[`keremberke/yolov8n-pcb-defect-segmentation`](https://huggingface.co/keremberke/yolov8n-pcb-defect-segmentation).

- **Detects 4 classes:** `Dry_joint`, `Incorrect_installation`, `PCB_damage`, `Short_circuit`
- **Trained on:** the [`keremberke/pcb-defect-segmentation`](https://huggingface.co/datasets/keremberke/pcb-defect-segmentation) dataset (≈189 images), originally sourced from the [defects-2q87r](https://universe.roboflow.com/diplom-qz7q6/defects-2q87r) dataset on Roboflow Universe
- **Reported accuracy:** ~0.51 mAP@0.5 (this is a small/nano model — expect misses and occasional misclassification)

> **Note:** This model is trained specifically on PCB images. It will only detect the four PCB defect classes above. To use VisionLog in another domain, swap in a model trained on that domain's data (see [Extending to Other Domains](#extending-to-other-domains)).

### How to test it

1. Download a sample image from the [dataset viewer on Hugging Face](https://huggingface.co/datasets/keremberke/pcb-defect-segmentation) or the [Roboflow page](https://universe.roboflow.com/diplom-qz7q6/defects-2q87r).
2. Upload it in the app's video uploader (a single image works well as a quick test).
3. Set the **confidence slider to ~0.15** — this nano model produces low-confidence detections, so a low threshold avoids filtering out real hits.
4. Record a short voice note describing what you see, then generate the report.

---

## Features

- **File upload or live capture** — upload media, or record directly in the browser via webcam (`st.camera_input`) and microphone (`st.audio_input`).
- **Adjustable settings** — calibrate the YOLO confidence threshold and choose the Whisper model size (`tiny`, `base`, `small`) based on your device.
- **Inline PDF preview** — review the generated report inside the app before downloading or sharing.
- **CPU-only** — no GPU or paid API needed.

---

## Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/nadi97-ahmadi/VisionAI-Log-Pipeline.git
cd VisionAI-Log-Pipeline

# 2. Create a virtual environment
python -m venv venv
# Windows:  .\venv\Scripts\Activate.ps1
# macOS/Linux:  source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

**System dependency:** `ffmpeg` must be installed and on your PATH (Whisper uses it).
- Windows: `winget install ffmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`
  (On Streamlit Cloud this is handled automatically via `packages.txt`.)

### Run the web app

```bash
streamlit run webapp/streamlit_app.py
```

To test from your phone on the same network:

```bash
streamlit run webapp/streamlit_app.py --server.address 0.0.0.0
```

### Run the CLI (optional)

```bash
python app.py --video data/sample.mp4 --audio data/sample.wav --confidence 0.20
```

---

## Repository Structure

```
VisionAI-Log-Pipeline/
├── .devcontainer/         ← Dev container config
├── data/                  ← Local media for testing
├── models/                ← Model configs / weights
├── output/                ← Generated reports & frame captures
├── src/
│   ├── pipeline.py        ← Orchestration engine (YOLO + Whisper)
│   └── report_generator.py← PyMuPDF report builder
├── webapp/
│   └── streamlit_app.py   ← Streamlit web UI
├── app.py                 ← CLI entry point
├── streamlit_app.py       ← Root entry point for Streamlit Cloud
├── yolov8n.pt             ← Bundled YOLOv8 nano weights
├── packages.txt           ← System (apt) packages for Streamlit Cloud
├── requirements.txt       ← Python dependencies
└── LICENSE.txt            ← License
```

> **Note on entry points:** there are two `streamlit_app.py` files — one at the repo root and one in `webapp/`. Streamlit Cloud looks for `streamlit_app.py` at the root by default, so set your app's *Main file path* to whichever one you intend to deploy, and remove or ignore the other to avoid confusion.

---

## Deployment Notes (Streamlit Community Cloud)

- `packages.txt` installs the required system libraries (`ffmpeg`, `libgl1`, etc.).
- Loading Whisper + YOLOv8 + PyTorch is **memory-heavy**. Streamlit Community Cloud's free tier (~1 GB RAM) may run out of memory and restart the app when both models load. If that happens, it's a resource limit, not a code error — consider a host with more RAM (e.g. Hugging Face Spaces, Render) for reliable use.

---

## Extending to Other Domains

The architecture is domain-agnostic — only the vision model changes. By training or swapping a YOLO model on a relevant dataset, the same speech-+-vision-+-reporting workflow can support:

- **Manufacturing / electronics** — solder, assembly, and surface defects
- **Welding & metalwork** — weld seam inspection
- **Infrastructure** — concrete cracks, corrosion, structural flaws
- **Agriculture** — crop disease and pest detection
- **Pharma / packaging** — fill-level and seal inspection
- **Textiles** — fabric defect detection

The pipeline, UI, and reporting stay the same; you only replace the trained weights and class labels.

---

## Tech Stack

Python · Streamlit · Ultralytics YOLOv8 · OpenAI Whisper · OpenCV · PyMuPDF · PyTorch

---

## Acknowledgements & Third-Party Licenses

This project integrates open-source components, each under its own license:

- **Ultralytics YOLOv8** — [AGPL-3.0](https://github.com/ultralytics/ultralytics/blob/main/LICENSE)
- **OpenAI Whisper** — MIT
- **Pretrained PCB model** — `keremberke/yolov8n-pcb-defect-segmentation` (see model card)
- **Dataset** — `keremberke/pcb-defect-segmentation`, derived from the Roboflow "defects-2q87r" dataset by Diplom
- **PyMuPDF, OpenCV, Streamlit** — see their respective repositories

> ⚠️ Ultralytics YOLOv8 is licensed under **AGPL-3.0**. If you reuse or distribute this project, review that license, as it carries copyleft obligations. (A commercial Ultralytics license is available separately for closed-source use.)

---

## License

The original code in this repository — the pipeline integration, the Streamlit UI, and the report layout — is © 2026 Nadira Ahmadi. See [`LICENSE.txt`](LICENSE.txt) for terms.

This applies to the author's own code only and does **not** override the licenses of the third-party components listed above, which remain governed by their respective terms.

For questions or usage inquiries, reach out via GitHub or LinkedIn.
