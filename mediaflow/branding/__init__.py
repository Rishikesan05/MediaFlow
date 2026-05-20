"""
MediaFlow Branding & Social Production Subpackage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Modules for dual-layer watermarking, edge-aware smart cropping, and
1080x1920 Instagram/Facebook Story composition.
"""

from .watermark import WatermarkEngine
from .smart_crop import SmartCropper
from .story_builder import StoryCompositor

__all__ = ["WatermarkEngine", "SmartCropper", "StoryCompositor"]
