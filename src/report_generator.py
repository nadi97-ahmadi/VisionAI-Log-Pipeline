# src/report_generator.py
# Builds a professional A4 PDF report using PyMuPDF (fitz).
# No external rendering engine needed — pure Python.

import fitz  # PyMuPDF
from pathlib import Path


class ReportGenerator:
    """
    Converts pipeline results into a structured A4 PDF inspection report.

    Sections:
      1. Header banner
      2. Inspection metadata
      3. Full audio transcript
      4. Timestamped transcript segments
      5. AI detection summary table
      6. Annotated frame images (up to 4, 2-per-row)
      7. Automated recommendations
      8. Footer
    """

    BRAND_BLUE   = (0.06, 0.38, 0.70)
    BRAND_DARK   = (0.10, 0.12, 0.18)
    GRAY         = (0.45, 0.45, 0.45)
    LIGHT_GRAY   = (0.93, 0.93, 0.94)
    ACCENT_RED   = (0.82, 0.18, 0.18)
    ACCENT_GREEN = (0.10, 0.55, 0.25)
    WHITE        = (1.00, 1.00, 1.00)

    PAGE_W = 595
    PAGE_H = 842
    MARGIN = 28

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _header(self, page):
        w = self.PAGE_W
        page.draw_rect(fitz.Rect(0, 0, w, 78), color=None, fill=self.BRAND_BLUE)
        page.insert_text((self.MARGIN, 32), "VISIONLOG",
                         fontsize=22, color=self.WHITE, fontname="helv")
        page.insert_text((self.MARGIN, 52), "AI-Powered Video + Audio Inspection Report",
                         fontsize=8.5, color=(0.78, 0.88, 0.97), fontname="helv")
        page.insert_text((w - self.MARGIN - 90, 32), "Field Inspection Log",
                         fontsize=9, color=self.WHITE, fontname="helv")

    def _section_title(self, page, y: float, text: str) -> float:
        page.insert_text((self.MARGIN, y), text.upper(),
                         fontsize=7.5, color=self.BRAND_BLUE, fontname="helv")
        page.draw_line(fitz.Point(self.MARGIN, y + 5),
                       fitz.Point(self.PAGE_W - self.MARGIN, y + 5),
                       color=self.LIGHT_GRAY, width=0.5)
        return y + 18

    def _kv_row(self, page, y: float, key: str, value: str, value_color=None) -> float:
        if value_color is None:
            value_color = self.BRAND_DARK
        page.insert_text((self.MARGIN, y), key + ":",
                         fontsize=8.5, color=self.GRAY, fontname="helv")
        page.insert_text((165, y), str(value),
                         fontsize=8.5, color=value_color, fontname="helv")
        return y + 15

    def _wrap_text(self, text: str, max_chars: int = 88) -> list:
        words, lines, current = text.split(), [], ""
        for word in words:
            if len(current) + len(word) + 1 <= max_chars:
                current += (" " if current else "") + word
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def build(self, results: dict, output_path: str = "output/VisionLog_Report.pdf") -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        doc  = fitz.open()
        page = doc.new_page(width=self.PAGE_W, height=self.PAGE_H)

        audio      = results["audio"]
        video      = results["video"]
        detections = video["detections"]

        # 1. Header
        self._header(page)
        y = 96

        # 2. Metadata
        y = self._section_title(page, y, "Inspection Metadata")
        y = self._kv_row(page, y, "Report Generated",  results["timestamp"])
        y = self._kv_row(page, y, "Video File",        Path(results["video_path"]).name)
        y = self._kv_row(page, y, "Audio File",        Path(results["audio_path"]).name)
        y = self._kv_row(page, y, "Video Duration",    f"{video['duration_sec']} s  ({video['fps']} fps)")
        y = self._kv_row(page, y, "Total Frames",      str(video["total_frames"]))
        y = self._kv_row(page, y, "Detected Language", audio["language"].title())
        status_text  = f"{len(detections)} anomal{'y' if len(detections)==1 else 'ies'} detected"
        status_color = self.ACCENT_RED if detections else self.ACCENT_GREEN
        y = self._kv_row(page, y, "AI Vision Status",  status_text, value_color=status_color)
        y += 8

        # 3. Full transcript
        y = self._section_title(page, y, "Technician Audio Transcript")
        transcript = audio["full_text"] or "[No speech detected in audio file]"
        for line in self._wrap_text(transcript):
            page.insert_text((self.MARGIN, y), line,
                             fontsize=9.5, color=self.BRAND_DARK, fontname="helv")
            y += 13
        y += 8

        # 4. Timestamped segments
        if audio["segments"]:
            y = self._section_title(page, y, "Timestamped Transcript Segments")
            for seg in audio["segments"][:10]:
                ts = f"[{seg['start']}s – {seg['end']}s]"
                page.insert_text((self.MARGIN, y), ts,
                                 fontsize=7.5, color=self.BRAND_BLUE, fontname="helv")
                page.insert_text((105, y), seg["text"],
                                 fontsize=8.5, color=self.BRAND_DARK, fontname="helv")
                y += 12
            y += 8

        # 5. Detection table
        y = self._section_title(page, y, "AI Vision Detection Summary")
        if not detections:
            page.insert_text((self.MARGIN, y),
                             "No objects detected above the confidence threshold.",
                             fontsize=9, color=self.GRAY, fontname="helv")
            y += 20
        else:
            header_cols = [
                (self.MARGIN, "Time (s)"),
                (90,          "Frame #"),
                (150,         "Detected Object / Class"),
                (320,         "Confidence"),
            ]
            page.draw_rect(
                fitz.Rect(self.MARGIN - 4, y - 10, self.PAGE_W - self.MARGIN, y + 5),
                color=None, fill=self.LIGHT_GRAY)
            for col_x, col_label in header_cols:
                page.insert_text((col_x, y), col_label,
                                 fontsize=7.5, color=self.GRAY, fontname="helv")
            y += 14

            for i, det in enumerate(detections[:12]):
                if i % 2 == 0:
                    page.draw_rect(
                        fitz.Rect(self.MARGIN - 4, y - 9, self.PAGE_W - self.MARGIN, y + 5),
                        color=None, fill=self.LIGHT_GRAY)
                page.insert_text((self.MARGIN, y), str(det["timestamp_sec"]),
                                 fontsize=8.5, color=self.BRAND_DARK, fontname="helv")
                page.insert_text((90, y), str(det["frame"]),
                                 fontsize=8.5, color=self.BRAND_DARK, fontname="helv")
                page.insert_text((150, y), det["class"].replace("_", " ").title(),
                                 fontsize=8.5, color=self.BRAND_DARK, fontname="helv")
                conf_pct   = f"{det['confidence'] * 100:.1f}%"
                conf_color = self.ACCENT_RED if det["confidence"] >= 0.70 else self.BRAND_DARK
                page.insert_text((320, y), conf_pct,
                                 fontsize=8.5, color=conf_color, fontname="helv")
                y += 13
            y += 8

        # 6. Annotated frame images
        saved = video.get("saved_frames", [])
        if saved:
            y = self._section_title(page, y, "Captured Frames — AI Annotated Detections")
            IMG_W, IMG_H, GAP = 255, 148, 10
            col_xs  = [self.MARGIN, self.MARGIN + IMG_W + GAP]
            col_idx = 0
            for frame_path in saved[:4]:
                if not Path(frame_path).exists():
                    continue
                x_pos = col_xs[col_idx]
                try:
                    page.insert_image(
                        fitz.Rect(x_pos, y, x_pos + IMG_W, y + IMG_H),
                        filename=frame_path)
                    page.draw_rect(
                        fitz.Rect(x_pos, y, x_pos + IMG_W, y + IMG_H),
                        color=self.BRAND_BLUE, width=0.5)
                except Exception as e:
                    print(f"  [WARN] Could not embed frame: {e}")
                col_idx += 1
                if col_idx >= 2:
                    col_idx = 0
                    y += IMG_H + GAP
            if col_idx != 0:
                y += IMG_H + GAP
            y += 8

        # 7. Recommendations
        y = self._section_title(page, y, "Automated Recommendations")
        recs = (
            [
                "Review all flagged frames and cross-reference with the technician transcript.",
                "Schedule a follow-up physical inspection within 30 days.",
                "Archive this report and annotated frames in the compliance portal.",
                "If anomaly confidence exceeds 80%, escalate to senior engineer review.",
            ]
            if detections else
            [
                "No critical anomalies detected — system appears within normal parameters.",
                "Schedule routine re-inspection as per maintenance schedule.",
                "Archive this log for compliance records.",
            ]
        )
        for i, rec in enumerate(recs, 1):
            page.insert_text((self.MARGIN, y), f"{i}.  {rec}",
                             fontsize=9, color=self.BRAND_DARK, fontname="helv")
            y += 14

        # 8. Footer
        footer_y = self.PAGE_H - 22
        page.draw_line(fitz.Point(self.MARGIN, footer_y),
                       fitz.Point(self.PAGE_W - self.MARGIN, footer_y),
                       color=self.LIGHT_GRAY, width=0.5)
        page.insert_text((self.MARGIN, footer_y + 12),
                         "Generated by VisionLog AI Pipeline  |  Confidential — Internal Use Only",
                         fontsize=7, color=self.GRAY, fontname="helv")
        page.insert_text((self.PAGE_W - self.MARGIN - 44, footer_y + 12), "Page 1 of 1",
                         fontsize=7, color=self.GRAY, fontname="helv")

        doc.save(output_path)
        doc.close()
        print(" ✓ PDF compiled successfully")
        return output_path