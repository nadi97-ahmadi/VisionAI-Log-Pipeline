# webapp/streamlit_app.py
# VisionLog — Streamlit Web App
#
# Run with:
#   streamlit run webapp/streamlit_app.py
    
import streamlit as st
import tempfile
import base64
import time
import os
from pathlib import Path

# ── must be first streamlit call ──────────────────────────────────────────────
st.set_page_config(
    page_title="VisionLog AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── import pipeline (lives in src/) ──────────────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.pipeline import InspectionPipeline
from src.report_generator import ReportGenerator

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Hide default streamlit header/footer */
  #MainMenu, footer, header { visibility: hidden; }

  /* Clear layout background */
  .stApp { 
    background-color: #fafbfc !important; 
  }

  /* --- FIXING GENERAL TEXT READABILITY --- */
  /* Force all standard body text and markdown to be a crisp charcoal black */
  .stApp, .stApp p, .stMarkdown p {
    color: #111827 !important;
    font-size: 1rem;
    line-height: 1.6;
  }

  /* Force all standard headers to be deep dark blue */
  .stApp h1, .stApp h2, .stApp h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #0f2d59 !important;
    font-weight: 700 !important;
  }

  /* Explicitly make Streamlit widget labels dark and visible */
  .stApp label, .stApp .stSlider, .stSelectbox, .stTab {
    color: #111827 !important;
    font-weight: 600 !important;
  }

  /* --- BANNER OVERRIDES --- */
  .vl-header {
    background: linear-gradient(135deg, #0a62b5 0%, #0f2d59 100%);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 24px;
    box-shadow: 0 4px 12px rgba(15, 45, 89, 0.15);
  }
  .vl-header h1 { font-size: 2.4rem; font-weight: 800; margin: 0; letter-spacing: -1px; color: #ffffff !important; }
  .vl-header p  { font-size: 1.05rem; opacity: 0.95; margin: 6px 0 0; color: #f0f4ff !important; }

  /* --- INDUSTRIAL CARDS LAYOUT --- */
  .vl-card {
    background-color: #ffffff !important;
    border-radius: 14px;
    padding: 24px 28px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
    border: 1px solid #e5e7eb;
  }
  .vl-card h3 { 
    font-size: 1.1rem; 
    font-weight: 700; 
    color: #0a62b5 !important; 
    margin: 0 0 16px; 
    text-transform: uppercase; 
    letter-spacing: 0.5px; 
  }
  /* Ensure text inside cards is explicitly dark gray/black */
  .vl-card p, .vl-card span, .vl-card div { 
    color: #111827 !important; 
  }

  /* --- STREAMLIT NATIVE COMPONENTS PROTECTION --- */
  /* Keep file uploader text readable */
  .stFileUploader section div {
    color: #4b5563 !important;
  }
  
  /* Keep warnings, info boxes, and alerts perfectly clear */
  .stAlert div, .stAlert p {
    color: #1f2937 !important;
    font-weight: 600 !important;
  }

  /* --- BADGES & RECOVERY INTERFACE ELEMENTS --- */
  .badge-green { background-color: #d1fae5 !important; color: #065f46 !important; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; display: inline-block; }
  .badge-blue  { background-color: #dbeafe !important; color: #1e40af !important; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; display: inline-block; }
  .badge-red   { background-color: #fee2e2 !important; color: #991b1b !important; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; display: inline-block; }

  /* Transcript Display block styles */
  .transcript-box {
    background-color: #f8fafc !important;
    border-left: 4px solid #0a62b5;
    border-radius: 0 10px 10px 0;
    padding: 16px 20px;
    font-size: 1rem;
    line-height: 1.7;
    color: #111827 !important;
    margin: 8px 0 16px;
    font-weight: 500 !important;
    border-top: 1px solid #e5e7eb;
    border-right: 1px solid #e5e7eb;
    border-bottom: 1px solid #e5e7eb;
  }

  /* Tables formatting rules */
  .det-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; margin-top: 10px; }
  .det-table th { background-color: #f1f5f9 !important; color: #0f2d59 !important; padding: 12px; text-align: left; font-weight: 700; border-bottom: 2px solid #0a62b5; }
  .det-table td { padding: 10px 12px; border-bottom: 1px solid #e5e7eb; color: #111827 !important; font-weight: 500; }
  .conf-high { color: #dc2626 !important; font-weight: 700 !important; }
  .conf-mid  { color: #d97706 !important; font-weight: 700 !important; }
  .conf-low  { color: #059669 !important; font-weight: 700 !important; }

  /* Share Link Display block text tracking */
  .share-box {
    background-color: #f1f5f9 !important;
    border: 1.5px dashed #0a62b5;
    border-radius: 10px;
    padding: 14px 18px;
    font-family: monospace;
    font-size: 0.88rem;
    color: #0f2d59 !important;
    word-break: break-all;
    margin-top: 12px;
  }

  /* Download Button Styling override */
  .dl-btn {
    display: inline-block;
    background-color: #0a62b5;
    color: #ffffff !important;
    text-decoration: none !important;
    padding: 12px 28px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 1rem;
    margin-top: 8px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  .dl-btn:hover { background-color: #0f2d59; }

  /* Divider line structure */
  .vl-divider { border: none; border-top: 2px solid #e5e7eb; margin: 16px 0 24px; }

  /* Progress Stepper Tracking elements UI */
  .progress-row { display: flex; gap: 8px; align-items: center; margin: 12px 0; }
  .progress-step { flex: 1; padding: 12px; border-radius: 8px; text-align: center; font-size: 0.85rem; font-weight: 700; }
  .step-done    { background-color: #d1fae5 !important; color: #065f46 !important; border: 1px solid #a7f3d0; }
  .step-active  { background-color: #0a62b5 !important; color: #ffffff !important; }
  .step-waiting { background-color: #f3f4f6 !important; color: #9ca3af !important; border: 1px solid #e5e7eb; }
</style>
""", unsafe_allow_html=True)

# ── helpers ───────────────────────────────────────────────────────────────────

def pdf_to_base64(pdf_path: str) -> str:
    with open(pdf_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def make_download_link(pdf_path: str, label: str = "⬇️ Download PDF Report") -> str:
    b64 = pdf_to_base64(pdf_path)
    return (
        f'<a class="dl-btn" href="data:application/pdf;base64,{b64}" '
        f'download="VisionLog_Report.pdf">{label}</a>'
    )

def make_share_link(pdf_path: str) -> str:
    b64 = pdf_to_base64(pdf_path)
    return f"data:application/pdf;base64,{b64}"

def conf_class(conf: float) -> str:
    if conf >= 0.70: return "conf-high"
    if conf >= 0.50: return "conf-mid"
    return "conf-low"

@st.cache_resource(show_spinner=False)
def load_pipeline():
    return InspectionPipeline(confidence_threshold=0.35)

def save_upload(uploaded_file, suffix: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded_file.read())
    tmp.flush()
    return tmp.name


# ── session state defaults ────────────────────────────────────────────────────
for key in ["results", "pdf_path", "processing_done"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "processing_done" not in st.session_state:
    st.session_state.processing_done = False


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="vl-header">
  <h1>🔍 VisionLog AI</h1>
  <p>Upload or record your inspection video & voice note — get an AI-generated PDF report instantly.</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# INPUT SECTION — two columns
# ══════════════════════════════════════════════════════════════════════════════
col1, col2 = st.columns(2, gap="large")

# ── VIDEO column ──────────────────────────────────────────────────────────────
with col1:
    st.markdown('<div class="vl-card">', unsafe_allow_html=True)
    st.markdown('<h3>📹 Inspection Video</h3>', unsafe_allow_html=True)

    video_tab1, video_tab2 = st.tabs(["📁 Upload video", "🎥 Record from camera"])

    with video_tab1:
        uploaded_video = st.file_uploader(
            "Drop your video here",
            type=["mp4", "mov", "avi", "mkv", "webm"],
            key="video_upload",
            label_visibility="collapsed",
        )
        if uploaded_video:
            st.video(uploaded_video)
            st.markdown('<span class="badge-green">✓ Video ready</span>', unsafe_allow_html=True)

    with video_tab2:
        st.info("📱 **Tip:** Use your phone camera for best results — then upload via the Upload tab above.\n\nOr use the recorder below (browser webcam):")
        recorded_video = st.camera_input("📷 Take a photo / record", key="cam_video")
        if recorded_video:
            st.markdown('<span class="badge-green">✓ Camera capture ready</span>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── AUDIO column ──────────────────────────────────────────────────────────────
with col2:
    st.markdown('<div class="vl-card">', unsafe_allow_html=True)
    st.markdown('<h3>🎙️ Technician Voice Note</h3>', unsafe_allow_html=True)

    audio_tab1, audio_tab2 = st.tabs(["📁 Upload audio", "🎤 Record voice note"])

    with audio_tab1:
        uploaded_audio = st.file_uploader(
            "Drop your audio here",
            type=["wav", "mp3", "m4a", "ogg", "flac", "mp4"],
            key="audio_upload",
            label_visibility="collapsed",
        )
        if uploaded_audio:
            st.audio(uploaded_audio)
            st.markdown('<span class="badge-green">✓ Audio ready</span>', unsafe_allow_html=True)

    with audio_tab2:
        st.info("🎙️ Click the mic button below to record your voice note directly in the browser:")
        recorded_audio = st.audio_input("🎤 Record voice note", key="mic_audio")
        if recorded_audio:
            st.audio(recorded_audio)
            st.markdown('<span class="badge-green">✓ Voice note recorded</span>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ── SETTINGS row ──────────────────────────────────────────────────────────────
with st.expander("⚙️ Advanced settings"):
    conf_threshold = st.slider(
        "Detection confidence threshold",
        min_value=0.10,
        max_value=0.90,
        value=0.35,
        step=0.05,
        help="Lower = detects more objects. Higher = only highly confident detections.",
    )
    whisper_size = st.selectbox(
        "Whisper model size",
        ["tiny", "base", "small"],
        index=0,
        help="Tiny is fastest. Base is more accurate. Small is best but slowest on CPU.",
    )


# ══════════════════════════════════════════════════════════════════════════════
# RUN BUTTON
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<hr class='vl-divider'>", unsafe_allow_html=True)

final_video = uploaded_video or recorded_video
final_audio = uploaded_audio or recorded_audio

ready = final_video is not None and final_audio is not None

if not ready:
    missing = []
    if final_video is None: missing.append("video")
    if final_audio is None: missing.append("audio")
    st.warning(f"⚠️ Please provide: **{' and '.join(missing)}** to generate the report.")

run_btn = st.button(
    "🚀 Generate Inspection Report",
    disabled=not ready,
    use_container_width=True,
    type="primary",
)


# ══════════════════════════════════════════════════════════════════════════════
# PROCESSING
# ══════════════════════════════════════════════════════════════════════════════
if run_btn and ready:
    st.session_state.processing_done = False
    st.session_state.results = None
    st.session_state.pdf_path = None

    video_suffix = "." + (final_video.name.split(".")[-1] if hasattr(final_video, "name") else "mp4")
    audio_suffix = "." + (final_audio.name.split(".")[-1] if hasattr(final_audio, "name") else "wav")

    video_tmp = save_upload(final_video, video_suffix)
    audio_tmp = save_upload(final_audio, audio_suffix)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    pdf_out = str(output_dir / "VisionLog_Report.pdf")

    progress_placeholder = st.empty()
    status_placeholder   = st.empty()

    def update_progress(step: int, label: str):
        steps = ["Loading models", "Transcribing audio", "Analysing video", "Building PDF"]
        html  = '<div class="progress-row">'
        for i, s in enumerate(steps):
            if i < step:
                html += f'<div class="progress-step step-done">✓ {s}</div>'
            elif i == step:
                html += f'<div class="progress-step step-active">⏳ {s}</div>'
            else:
                html += f'<div class="progress-step step-waiting">{s}</div>'
        html += "</div>"
        progress_placeholder.markdown(html, unsafe_allow_html=True)
        status_placeholder.info(f"**{label}**")

    try:
        update_progress(0, "Loading Whisper + YOLOv8 models...")
        pipeline = InspectionPipeline(confidence_threshold=conf_threshold)
        pipeline._load_whisper()
        pipeline._load_yolo()

        update_progress(1, "Transcribing your voice note with Whisper...")
        audio_data = pipeline.transcribe_audio(audio_tmp)

        update_progress(2, "Scanning video frames with YOLOv8...")
        video_data = pipeline.analyze_video(video_tmp)

        import datetime
        results = {
            "timestamp":  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "video_path": final_video.name if hasattr(final_video, "name") else "recorded_video",
            "audio_path": final_audio.name if hasattr(final_audio, "name") else "recorded_audio",
            "audio":      audio_data,
            "video":      video_data,
        }

        update_progress(3, "Compiling PDF report...")
        generator = ReportGenerator()
        generator.build(results, output_path=pdf_out)

        st.session_state.results   = results
        st.session_state.pdf_path  = pdf_out
        st.session_state.processing_done = True

        progress_placeholder.empty()
        status_placeholder.success("✅ Report generated successfully!")

    except Exception as e:
        progress_placeholder.empty()
        status_placeholder.error(f"❌ Error during processing: {e}")
        st.exception(e)
    finally:
        for f in [video_tmp, audio_tmp]:
            try: os.unlink(f)
            except: pass


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS SECTION
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.processing_done and st.session_state.results:
    results    = st.session_state.results
    pdf_path   = st.session_state.pdf_path
    audio_data = results["audio"]
    video_data = results["video"]
    detections = video_data["detections"]

    st.markdown("---")
    st.markdown("## 📋 Inspection Report")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Duration",      f"{video_data['duration_sec']} s")
    m2.metric("Frames scanned", video_data["total_frames"])
    m3.metric("Detections",    len(detections))
    m4.metric("Language",      audio_data["language"].upper())

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="vl-card">', unsafe_allow_html=True)
        st.markdown('<h3>🎙️ Audio Transcript</h3>', unsafe_allow_html=True)
        transcript = audio_data["full_text"] or "_No speech detected._"
        st.markdown(f'<div class="transcript-box">{transcript}</div>', unsafe_allow_html=True)

        if audio_data["segments"]:
            st.markdown("<p style='font-weight:700;color:#0d3f75;'>Timestamped segments:</p>", unsafe_allow_html=True)
            for seg in audio_data["segments"][:8]:
                st.markdown(
                    f'<div style="margin-bottom:6px;"><span style="color:#0a62b5;font-weight:700;margin-right:8px;">'
                    f'[{seg["start"]}s – {seg["end"]}s]</span><span style="color:#1a2030;font-weight:600;">{seg["text"]}</span></div>',
                    unsafe_allow_html=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="vl-card">', unsafe_allow_html=True)
        st.markdown('<h3>🤖 AI Vision Detections</h3>', unsafe_allow_html=True)
        if not detections:
            st.markdown("_No objects detected above threshold._")
        else:
            rows = ""
            for d in detections[:12]:
                pct  = f"{d['confidence']*100:.1f}%"
                cls  = conf_class(d["confidence"])
                rows += (
                    f"<tr>"
                    f"<td>{d['timestamp_sec']}s</td>"
                    f"<td>{d['frame']}</td>"
                    f"<td>{d['class'].replace('_',' ').title()}</td>"
                    f"<td class='{cls}'>{pct}</td>"
                    f"</tr>"
                )
            st.markdown(
                f"""<table class="det-table">
                  <thead><tr>
                    <th>Time</th><th>Frame</th>
                    <th>Object Class</th><th>Confidence</th>
                  </tr></thead>
                  <tbody>{rows}</tbody>
                </table>""",
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="vl-card">', unsafe_allow_html=True)
        st.markdown('<h3>🖼️ Annotated Frames</h3>', unsafe_allow_html=True)
        saved = video_data.get("saved_frames", [])
        if saved:
            cols = st.columns(2)
            for i, fp in enumerate(saved[:4]):
                if Path(fp).exists():
                    cols[i % 2].image(fp, use_container_width=True)
        else:
            st.markdown("_No frames captured._")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="vl-card">', unsafe_allow_html=True)
    st.markdown('<h3>📥 Download & Share Report</h3>', unsafe_allow_html=True)

    dl_col, share_col = st.columns([1, 2])

    with dl_col:
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_file,
                file_name="VisionLog_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
        st.markdown(make_download_link(pdf_path, "📄 Open PDF in browser"), unsafe_allow_html=True)

    with share_col:
        st.markdown("<p style='font-weight:700;color:#0d3f75;margin:0;'>🔗 Shareable link:</p>", unsafe_allow_html=True)
        share_link = make_share_link(pdf_path)
        st.markdown(f'<div class="share-box">{share_link[:120]}...</div>', unsafe_allow_html=True)
        st.code(share_link, language=None)
        
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("👁️ Preview PDF inline"):
        b64 = pdf_to_base64(pdf_path)
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" '
            f'width="100%" height="700px" style="border-radius:10px;border:none;"></iframe>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Start new inspection", use_container_width=True):
        for key in ["results", "pdf_path", "processing_done"]:
            st.session_state[key] = None
        st.rerun()


# ── footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<br><br>
<div style="text-align:center;color:#7f8c8d;font-size:0.85rem;font-weight:700;padding-bottom:20px">
  VisionLog AI — Built with Whisper + YOLOv8 + Streamlit &nbsp;|&nbsp; CPU-only · No GPU required
</div>
""", unsafe_allow_html=True)
