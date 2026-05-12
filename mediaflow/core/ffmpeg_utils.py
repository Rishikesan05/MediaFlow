"""
FFmpeg & FFprobe Utility Subsystem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Cross-platform binary discovery, lossless stream manipulation, audio stripping,
and precise frame extraction without generational transcoding loss.
"""

import os
import shutil
import subprocess
import json
from pathlib import Path
from typing import Optional, Tuple


class FFmpegUtils:
    """
    Wrapper for FFmpeg and FFprobe command execution.
    """

    @staticmethod
    def get_ffmpeg_path() -> Optional[str]:
        """Discovers FFmpeg binary from PATH or standard system installation locations."""
        cmd = shutil.which("ffmpeg")
        if cmd:
            return cmd

        # Common Windows WinGet / custom locations
        local_app = os.environ.get("LOCALAPPDATA", "")
        candidates = [
            os.path.join(local_app, "Microsoft", "WinGet", "Packages"),
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
            r"C:\tools\ffmpeg\bin",
        ]
        for base_dir in candidates:
            if os.path.isdir(base_dir):
                for p in Path(base_dir).rglob("ffmpeg.exe"):
                    return str(p)
        return None

    @staticmethod
    def get_ffprobe_path() -> Optional[str]:
        """Discovers FFprobe binary alongside FFmpeg or from PATH."""
        ffmpeg = FFmpegUtils.get_ffmpeg_path()
        if ffmpeg:
            probe_same_dir = os.path.join(os.path.dirname(ffmpeg), "ffprobe.exe")
            if os.path.exists(probe_same_dir):
                return probe_same_dir
        return shutil.which("ffprobe")

    @classmethod
    def get_video_metadata(cls, video_path: str) -> Tuple[float, float]:
        """
        Retrieves video duration (seconds) and frame rate (FPS) using FFprobe JSON output.
        Returns: (duration: float, fps: float)
        """
        ffprobe = cls.get_ffprobe_path()
        if not ffprobe or not os.path.exists(video_path):
            return 0.0, 30.0

        try:
            cmd = [
                ffprobe,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                "-select_streams", "v:0",
                video_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)

            duration = float(data.get("format", {}).get("duration", 0.0))
            fps = 30.0
            for stream in data.get("streams", []):
                fps_raw = stream.get("r_frame_rate", "30/1")
                if "/" in fps_raw:
                    num, den = fps_raw.split("/")
                    fps = float(num) / max(float(den), 1.0)
                else:
                    fps = float(fps_raw)
            return duration, fps
        except Exception:
            return 0.0, 30.0

    @classmethod
    def mute_video_lossless(cls, input_path: str, output_path: str) -> bool:
        """
        Strips audio stream using zero-transcode stream copy (-c:v copy -an).
        """
        ffmpeg = cls.get_ffmpeg_path()
        if not ffmpeg:
            raise FileNotFoundError("FFmpeg executable not found on system.")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        cmd = [
            ffmpeg,
            "-y",
            "-i", input_path,
            "-map_metadata", "0",
            "-map", "0:v:0",
            "-c:v", "copy",
            "-an",
            "-movflags", "+faststart",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0 and os.path.exists(output_path)

    @classmethod
    def extract_clip(cls, input_path: str, start_sec: float, end_sec: float, output_path: str) -> bool:
        """
        Extracts sub-clip between timestamps using fast stream copy with re-encode fallback.
        """
        ffmpeg = cls.get_ffmpeg_path()
        if not ffmpeg:
            raise FileNotFoundError("FFmpeg executable not found on system.")

        duration = max(0.1, end_sec - start_sec)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Primary: stream copy
        cmd = [
            ffmpeg,
            "-y",
            "-ss", f"{start_sec:.3f}",
            "-i", input_path,
            "-t", f"{duration:.3f}",
            "-map", "0:v:0",
            "-c:v", "copy",
            "-an",
            "-movflags", "+faststart",
            output_path,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode == 0 and os.path.exists(output_path):
            return True

        # Fallback: re-encode with high quality CRF 18
        cmd_fallback = [
            ffmpeg,
            "-y",
            "-ss", f"{start_sec:.3f}",
            "-i", input_path,
            "-t", f"{duration:.3f}",
            "-map", "0:v:0",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-an",
            "-movflags", "+faststart",
            output_path,
        ]
        res_fb = subprocess.run(cmd_fallback, capture_output=True, text=True, timeout=240)
        return res_fb.returncode == 0 and os.path.exists(output_path)

    @classmethod
    def extract_keyframe(cls, video_path: str, timestamp_sec: float, output_path: str) -> bool:
        """
        Extracts a single high-quality RGB frame at timestamp_sec.
        """
        ffmpeg = cls.get_ffmpeg_path()
        if not ffmpeg:
            raise FileNotFoundError("FFmpeg executable not found on system.")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        cmd = [
            ffmpeg,
            "-y",
            "-ss", f"{timestamp_sec:.3f}",
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            output_path,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return res.returncode == 0 and os.path.exists(output_path)
