"""
TransNetV2 Deep Shot Boundary Detector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Temporal Convolutional Network for detecting hard cuts, transitions,
and shot boundaries in video files. Includes graceful PySceneDetect fallback.
"""

from typing import List, Tuple, Optional
import os

try:
    import torch
    from transnetv2_pytorch import TransNetV2
except ImportError:
    torch = None
    TransNetV2 = None

try:
    from scenedetect import detect, ContentDetector
except ImportError:
    detect = None
    ContentDetector = None


class ShotBoundaryDetector:
    """
    Shot boundary transition detector using TransNetV2 with PySceneDetect fallback.
    """

    def __init__(self, device: Optional[str] = None):
        self._model = None
        if torch is not None:
            self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = "cpu"

    def _load_transnet(self) -> bool:
        """Initializes TransNetV2 neural weights if installed."""
        if self._model is not None:
            return True
        if TransNetV2 is not None and torch is not None:
            try:
                self._model = TransNetV2(device=self.device)
                self._model.eval()
                return True
            except Exception:
                self._model = None
        return False

    def detect_scenes(self, video_path: str, threshold: float = 0.50) -> List[Tuple[float, float]]:
        """
        Detects video scenes returning a list of (start_seconds, end_seconds) intervals.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Attempt TransNetV2 inference
        if self._load_transnet():
            try:
                with torch.no_grad():
                    scenes = self._model.detect_scenes(video_path)
                if scenes:
                    intervals = []
                    for s in scenes:
                        intervals.append((float(s["start_time"]), float(s["end_time"])))
                    return intervals
            except Exception:
                pass

        # Fallback: PySceneDetect ContentDetector
        if detect is not None and ContentDetector is not None:
            try:
                scene_list = detect(video_path, ContentDetector(threshold=27.0))
                intervals = []
                for start_frame, end_frame in scene_list:
                    intervals.append((start_frame.get_seconds(), end_frame.get_seconds()))
                if intervals:
                    return intervals
            except Exception:
                pass

        # If no detector is installed, return video as single scene
        return []
