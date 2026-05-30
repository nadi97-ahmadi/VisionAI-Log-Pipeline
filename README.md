# VisionLog AI

**AI-powered Multimodal Field Inspection & Automated Reporting Platform**

VisionLog AI completely automates the manual paperwork bottleneck for field technicians and infrastructure service companies. By merging Edge Computer Vision and Automatic Speech Recognition (ASR), the platform transforms raw phone footage and spoken observations directly into standard compliance-ready PDF logs in seconds. **Optimized entirely for local CPU deployment—no expensive cloud API dependency or GPU hardware required.**

### 🌐 [Live Web App Demo](https://share.streamlit.io)

---

## 🏗️ System Architecture & Workflow

The web application coordinates an asynchronous multimodal processing pipeline across three core layers:

```
              ┌──────────────────────────────────────────────┐
              │          Streamlit Web Dashboard             │
              │   (File Dropzones / Live Browser Cam & Mic)  │
              └──────┬────────────────────────────────┬──────┘
                     │                                │
             [ Inspection Video ]             [ Operator Voice Note ]
                     │                                │
                     ▼                                ▼
           ┌───────────────────┐            ┌───────────────────┐
           │  OpenCV Decoding  │            │  FFmpeg Ingestion │
           └─────────┬─────────┘            └─────────┬─────────┘
                     │                                │
                     ▼                                ▼
           ┌───────────────────┐            ┌───────────────────┐
           │ YOLOv8 Nano (CPU) │            │ Whisper Tiny (CPU)│
           │  Object/Anomaly   │            │   ASR Text Engine │
           │   Bounding Boxes  │            │   + Timestamps    │
           └─────────┬─────────┘            └─────────┬─────────┘
                     │                                │
                     └────────────────┬───────────────┘
                                      │
                                      ▼
                           ┌────────────────────┐
                           │ PyMuPDF Generator  │
                           │   Asset Compiler   │
                           └──────────┬─────────┘
                                      │
                                      ▼
                           ┌────────────────────┐
                           │ Audit-Ready PDF Log│
                           │  & Inline Preview  │
                           └────────────────────┘
```

### Multimodal Engine Blueprint

| Component | Technology | Optimization / Runtime Notes |
| :--- | :--- | :--- |
| **User Interface** | Streamlit Architecture | Native responsive layout collapsing dynamically for laptop and mobile screens. |
| **Speech-to-Text** | `openai-whisper` (Tiny) | Dispatches localized automated transcripts on CPU in <5s. |
| **Computer Vision** | `ultralytics` YOLOv8 (Nano) | Real-time structural flaw tracking running at <1s/frame on standard CPUs. |
| **Document Compiler** | `PyMuPDF` (`fitz`) | Compiles dynamic image extractions, metadata, and tables with zero third-party dependencies. |

---

## 🚀 Key Features

* **Responsive Field Hub:** Clean dashboard interface built with specialized high-visibility HTML/CSS styling keeping typography crisp, accessible, and high-contrast across all modern mobile and desktop web browsers.
* **Live In-Browser Capture:** Technicians can upload media files directly or use real-time hardware recording layers via integrated browser webcam (`st.camera_input`) and microphone (`st.audio_input`) fields.
* **On-the-Fly Configurations:** Adjustable slider controls allow users to dynamically calibrate YOLO confidence thresholds and switch Whisper weights (`tiny`, `base`, `small`) depending on device limits.
* **Instant Inline Verification:** Generates embedded base64 data-URI previews allowing operators to visually check their PDF records inside the web interface before distributing links.

---

## 💻 Local Quick Start

### 1. Environment & Framework Setup
Clone the workspace structure and set up a clean Python virtual environment:
```bash
git clone https://github.com/YOUR_USERNAME/VisionLog.git
cd VisionLog

python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Dependency Ingestion
Install core requirements using the CPU-isolated PyTorch wheel distribution mirror:
```bash
pip install -r requirements.txt --index-url https://download.pytorch.org/whl/cpu
```
> **Note:** Ensure `ffmpeg` is available on your local system path (`winget install ffmpeg` on Windows or `brew install ffmpeg` on macOS).

### 3. Launching the App Platforms
You can execute VisionLog either as a standalone CLI processing script or via the updated interface server:

**To run the responsive Web App UI:**
```bash
streamlit run webapp/streamlit_app.py
```

**To run the local network link for testing on your phone browser:**
```bash
streamlit run webapp/streamlit_app.py --server.address 0.0.0.0
```

**To process assets directly via the Core CLI Engine:**
```bash
python app.py --video data/sample.mp4 --audio data/sample.wav --confidence 0.35
```

---

## 📂 Repository Structure
```
VisionLog/
├── data/                          ← Local media testing directory
├── models/                        ← Model initialization configs
├── output/                        ← Generated reports & frame captures
├── src/                           ← Core architectural module layers
│   ├── pipeline.py                ← Orchestration engine (YOLO + Whisper)
│   └── report_generator.py        ← Production PyMuPDF compiler layout
├── webapp/
│   └── streamlit_app.py           ← High-contrast, responsive UI dashboard
├── app.py                         ← Original CLI structural execution portal
├── requirements.txt               ← Deployment package dependencies list
└── LICENSE                        ← Proprietary ownership protection details
```

---

## 📊 Business & Operational Impact

**Eliminates the Documentation Bottleneck:** Reduces manual report filing overhead for technical inspection teams by up to 70%. By turning an operator's real-time field description and raw footage into a standardized, audit-ready compliance log immediately, companies save 1–2 hours of manual administration per technician every shift, while keeping corporate workflows fully contained on-device.

---

## 📄 License & Terms of Use

Copyright © 2026 Nadira Ahmadi. All rights reserved.

This project is developed strictly as a professional portfolio asset. The underlying source architecture, user interface styles, and asset collection methods are proprietary and confidential.

Permission is granted to view and evaluate the source code for hiring and engineering reference purposes only. No part of this repository may be copied, redistributed, modified, or re-used within secondary personal or commercial software applications without explicit prior written consent from the author.

For commercial usage inquiries or project authorization requests, please reach out via GitHub or LinkedIn.
