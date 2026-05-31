# src/pipeline.py
# Handles:
#   - Audio  → Whisper Tiny (CPU) → text transcript with timestamps
#   - Video  → YOLOv8 PCB Defect Segmentation (Hugging Face / CPU) → detected defects + annotated frames
import torch 
import cv2
import whisper
import datetime
from pathlib import Path
from ultralytics import YOLO


class InspectionPipeline:
    def __init__(self, confidence_threshold: float = 0.25):
        self.confidence_threshold = confidence_threshold
        self.whisper_model = None
        self.vision_model = None
        
        try:
            import torch.serialization
            # Allow both standard detection and segment models to load safely
            torch.serialization.add_safe_globals([
                'ultralytics.nn.tasks.DetectionModel', 
                'ultralytics.nn.tasks.SegmentationModel'
            ])
            print("PyTorch safe globals updated successfully.")
        except AttributeError:
            pass

    # ------------------------------------------------------------------
    # Internal: model loading
    # ------------------------------------------------------------------

    def _load_whisper(self):
        print("\n[1/3] Loading Whisper Tiny  (downloads ~150 MB on first run)...")
        self.whisper_model = whisper.load_model("tiny", device="cpu")
        print("      ✓ Whisper ready")

    def _load_yolo(self):
        print("[2/3] Loading Specialized PCB Defect Model from Hugging Face...")
        hf_model_id = "keremberke/yolov8n-pcb-defect-segmentation"
        
        try:
            # Ultralytics natively handles downloading directly via Hugging Face repo strings
            self.vision_model = YOLO(hf_model_id)
            
            # Configure model detection parameter overrides
            self.vision_model.overrides['conf'] = self.confidence_threshold
            self.vision_model.overrides['iou'] = 0.45
            self.vision_model.overrides['agnostic_nms'] = False
            self.vision_model.overrides['max_det'] = 1000
            
            print("      ✓ PCB Defect Segmentation Model ready")
        except Exception as e:
            print(f"      ⚠️ Failed to load Hugging Face model ({e}). Falling back to default yolov8n.pt")
            self.vision_model = YOLO("yolov8n.pt")

    # ------------------------------------------------------------------
    # Audio transcription
    # ------------------------------------------------------------------

    def transcribe_audio(self, audio_path: str) -> dict:
        """
        Transcribe a voice note to text.

        Returns:
            {
              "full_text": str,
              "segments":  [{"start": float, "end": float, "text": str}, ...],
              "language":  str
            }
        """
        print("\n      → Transcribing audio note...")

        result = self.whisper_model.transcribe(
            audio_path,
            fp16=False,
            verbose=False,
        )

        segments = []
        for seg in result.get("segments", []):
            segments.append(
                {
                    "start": round(seg["start"], 1),
                    "end":   round(seg["end"],   1),
                    "text":  seg["text"].strip(),
                }
            )

        print(f"      ✓ Transcribed {len(segments)} segment(s)")

        return {
            "full_text": result["text"].strip(),
            "segments":  segments,
            "language":  result.get("language", "unknown"),
        }

    # ------------------------------------------------------------------
    # Video defect / object detection
    # ------------------------------------------------------------------

    def analyze_video(self, video_path: str) -> dict:
        """
        Scan video frames with the specialized PCB model.

        Strategy:
          - Skips every 10 frames for speed on CPU
          - Saves up to 5 annotated frames where components or defect masks are detected
          - Records timestamp, label name, and confidence per detection
        """
        print("      → Scanning video frames...")

        Path("output").mkdir(exist_ok=True)

        cap = cv2.VideoCapture(video_path)

        fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_sec = round(total_frames / fps, 1)

        detections   = []
        saved_frames = []
        frame_idx    = 0
        SKIP         = 10
        MAX_CAPTURES = 5

        while cap.isOpened() and len(saved_frames) < MAX_CAPTURES:
            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1

            if frame_idx % SKIP != 0:
                continue

            results = self.vision_model(frame, verbose=False)

            for result in results:
                if len(result.boxes) == 0:
                    continue

                for box in result.boxes:
                    conf = float(box.conf[0])

                    if conf < self.confidence_threshold:
                        continue

                    cls_id    = int(box.cls[0])
                    cls_name  = self.vision_model.names[cls_id]
                    timestamp = round(frame_idx / fps, 1)

                    frame_path = f"output/frame_{frame_idx:06d}.jpg"
                    annotated  = result.plot()  # Automatically renders bounding boxes or masks
                    cv2.imwrite(frame_path, annotated)
                    saved_frames.append(frame_path)

                    detections.append(
                        {
                            "frame":         frame_idx,
                            "timestamp_sec": timestamp,
                            "class":         cls_name,
                            "confidence":    round(conf, 3),
                            "frame_path":    frame_path,
                        }
                    )
                    break

        cap.release()

        print(
            f"      ✓ Scanned {frame_idx} frames — "
            f"{len(saved_frames)} circuit board frame(s) captured"
        )

        return {
            "total_frames": total_frames,
            "duration_sec": duration_sec,
            "fps":          round(fps, 1),
            "detections":   detections,
            "saved_frames": saved_frames,
        }

    # ------------------------------------------------------------------
    # Public: run full pipeline
    # ------------------------------------------------------------------

    def run(self, video_path: str, audio_path: str) -> dict:
        """Run the full pipeline: load models → transcribe → detect."""
        self._load_whisper()
        self._load_yolo()

        print("\n[3/3] Running analysis...")

        audio_data = self.transcribe_audio(audio_path)
        video_data = self.analyze_video(video_path)

        return {
            "timestamp":  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "video_path": video_path,
            "audio_path": audio_path,
            "audio":      audio_data,
            "video":      video_data,
        }
