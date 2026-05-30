# Usage:
#   python app.py
#   python app.py --video data/myvideo.mp4 --audio data/mynote.wav
#   python app.py --confidence 0.3

import argparse
from pathlib import Path
from src.pipeline import InspectionPipeline
from src.report_generator import ReportGenerator


def main():
    parser = argparse.ArgumentParser(
        description="VisionLog — AI-powered Video + Audio Inspection Report Generator"
    )
    parser.add_argument(
        "--video",
        type=str,
        default="data/inspection_video.mp4",
        help="Path to your inspection video file",
    )
    parser.add_argument(
        "--audio",
        type=str,
        default="data/technician_note.mp4",
        help="Path to your voice recording (.mp4)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/VisionLog_Report.pdf",
        help="Where to save the generated PDF report",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.40,
        help="Detection confidence threshold 0.0–1.0 (default: 0.40)",
    )
    args = parser.parse_args()

    video_path = Path(args.video)
    audio_path = Path(args.audio)

    print("\n" + "=" * 55)
    print("   VisionLog — AI Inspection Report Generator")
    print("=" * 55)

    if not video_path.exists():
        print(f"\n[ERROR] Video file not found: {video_path}")
        print("  Place your inspection video at: data/inspection_video.mp4")
        print("  Or pass a custom path:  --video path/to/video.mp4\n")
        return

    if not audio_path.exists():
        print(f"\n[ERROR] Audio file not found: {audio_path}")
        print("  Place your voice note at: data/technician_note.mp4")
        print("  Or pass a custom path:  --audio path/to/note.mp4\n")
        return

    # Step 1: Running AI pipeline (transcription + detection)
    pipeline = InspectionPipeline(confidence_threshold=args.confidence)
    results = pipeline.run(
        video_path=str(video_path),
        audio_path=str(audio_path),
    )

    # Step 2: Building the PDF report from results
    generator = ReportGenerator()
    output_path = generator.build(results, output_path=args.output)

    print(f"\n{'=' * 55}")
    print(f"  Done!  Report saved to: {output_path}")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    main()