"""
MediaFlow Core Subpackage
~~~~~~~~~~~~~~~~~~~~~~~~~
Neural network managers and foundational utilities:
- CLIPManager: Zero-shot visual and text embedding generation.
- ShotBoundaryDetector: Deep shot boundary and scene transition detection.
- FFmpegUtils: Lossless stream extraction, audio muting, and frame queries.
"""

from .clip_manager import CLIPManager
from .ffmpeg_utils import FFmpegUtils
from .transnet_detector import ShotBoundaryDetector

__all__ = ["CLIPManager", "FFmpegUtils", "ShotBoundaryDetector"]
