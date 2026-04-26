"""
MediaFlow Core Subpackage
~~~~~~~~~~~~~~~~~~~~~~~~~
Neural network managers and foundational utilities:
- CLIPManager: Zero-shot visual and text embedding generation.
- TransNetDetector: Deep shot boundary and scene transition detection.
- FFmpegUtils: Lossless stream extraction, audio muting, and frame queries.
"""

from .clip_manager import CLIPManager

__all__ = ["CLIPManager"]
