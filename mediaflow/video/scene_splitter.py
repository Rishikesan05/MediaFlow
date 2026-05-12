"""
Video Scene Splitter & Ingestion Engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Automates video audio muting, neural shot boundary detection, and sub-clip
generation via FFmpeg stream operations.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from mediaflow.core.ffmpeg_utils import FFmpegUtils
from mediaflow.core.transnet_detector import ShotBoundaryDetector


@dataclass
class VideoScene:
    """Metadata container for an extracted video scene."""
    scene_id: int
    source_video: str
    clip_path: str
    keyframe_path: Optional[str]
    start_sec: float
    end_sec: float
    duration: float
    importance_score: float = 0.5
    importance_label: str = "MED"


class SceneSplitter:
    """
    Orchestrates video muting, scene segmentation, and keyframe extraction.
    """

    def __init__(self, detector: Optional[ShotBoundaryDetector] = None):
        self.detector = detector or ShotBoundaryDetector()

    def process_video(
        self,
        video_path: str,
        output_dir: str,
        mute_audio: bool = True,
        min_scene_sec: float = 1.0
    ) -> List[VideoScene]:
        """
        Splits a video into detected scenes and extracts the representative mid-frame.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]

        # Step 1: Lossless audio muting
        working_video = video_path
        if mute_audio:
            muted_path = os.path.join(output_dir, f"{base_name}_muted.mp4")
            if FFmpegUtils.mute_video_lossless(video_path, muted_path):
                working_video = muted_path

        # Step 2: Boundary detection
        total_dur, _ = FFmpegUtils.get_video_metadata(working_video)
        intervals = self.detector.detect_scenes(working_video)

        # Fallback if no cuts detected: treat entire video as one scene
        if not intervals:
            if total_dur > 0:
                intervals = [(0.0, total_dur)]
            else:
                return []

        scenes: List[VideoScene] = []
        for idx, (start, end) in enumerate(intervals):
            dur = end - start
            if dur < min_scene_sec:
                continue

            clip_filename = f"{base_name}_scene_{idx + 1:03d}.mp4"
            clip_path = os.path.join(output_dir, clip_filename)
            keyframe_filename = f"{base_name}_scene_{idx + 1:03d}_mid.jpg"
            keyframe_path = os.path.join(output_dir, keyframe_filename)

            # Split subclip
            FFmpegUtils.extract_clip(working_video, start, end, clip_path)

            # Extract keyframe from midpoint of scene
            mid_sec = start + (dur / 2.0)
            FFmpegUtils.extract_keyframe(working_video, mid_sec, keyframe_path)

            scenes.append(VideoScene(
                scene_id=idx + 1,
                source_video=video_path,
                clip_path=clip_path,
                keyframe_path=keyframe_path if os.path.exists(keyframe_path) else None,
                start_sec=start,
                end_sec=end,
                duration=dur
            ))

        return scenes
