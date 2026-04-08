"""
MediaFlow Configuration & Preset Registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Centralized settings for photo quality thresholds, semantic CLIP prompts,
video scene detection parameters, and brand watermarking presets.
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import os

@dataclass
class QualityGateConfig:
    """Thresholds for initial computer vision quality screening."""
    min_file_size_kb: float = 15.0
    min_brightness: float = 35.0          # Grayscale mean luminance floor
    min_blur_score: float = 30.0          # cv2.Laplacian variance floor
    max_blur_normalize: float = 200.0
    max_brightness_normalize: float = 120.0
    supported_image_extensions: Tuple[str, ...] = (
        ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"
    )

@dataclass
class SemanticScorerConfig:
    """CLIP model configuration and domain-specific prompt embeddings."""
    model_name: str = "openai/clip-vit-base-patch32"
    batch_size: int = 32
    min_positive_threshold: float = 0.18
    
    # Positive domain prompts for progress, wide architecture, and active construction
    positive_prompts: List[str] = field(default_factory=lambda: [
        "a wide-angle photograph showing the progress of a house renovation",
        "a nice overall view of a building exterior or interior room",
        "a well-composed photograph of a house renovation journey",
        "an establishing shot of a house under construction",
        "workers actively doing construction work on site",
        "finished modern interior room with clean lighting",
        "architectural renovation before and after progress",
    ])
    
    # Negative domain prompts for document screenshots, close-ups, and site clutter
    negative_prompts: List[str] = field(default_factory=lambda: [
        "a screenshot of a phone, chart, drawing, or document",
        "a blurry dark low quality photo",
        "a selfie or portrait photo of a person with no construction context",
        "a photo of text, receipt, bill, or paper document",
        "a close-up photo of building materials, bricks, sand, cement bags, or timber",
        "a close-up shot of pipes, plumbing, electrical wires, switchboards, or tools",
        "a photo of trash, debris, clutter, rubble, or garbage on a construction site",
        "an extreme close-up of a wall texture, floor tile, paint stroke, or small detail",
        "a boring close-up of a single tool, bucket, or machine",
        "a photo with drawing, markup, circles, arrows, or annotations on it",
        "a photo with a timestamp, date, time sticker, or digital text printed on it",
    ])

@dataclass
class DeduplicationConfig:
    """Parameters for temporal clustering and embedding cosine similarity."""
    temporal_window_hours: float = 24.0
    cosine_similarity_threshold: float = 0.90
    target_curation_count: int = 45

@dataclass
class VideoIntelligenceConfig:
    """Parameters for scene boundary detection and keyframe ranking."""
    supported_video_extensions: Tuple[str, ...] = (
        ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".3gp", ".m4v"
    )
    transnet_threshold: float = 0.50
    pyscenedetect_threshold: float = 27.0
    high_importance_cutoff: float = 0.65
    med_importance_cutoff: float = 0.35
    
    importance_prompts: List[str] = field(default_factory=lambda: [
        "workers actively working on construction site",
        "house renovation progress with wide view",
        "high quality construction machinery in action",
        "beautiful architectural transformation",
    ])
    low_importance_prompts: List[str] = field(default_factory=lambda: [
        "an empty dark scene",
        "extreme close up of dirt, sand, or rubble",
        "static shaky blurry video with nothing happening",
        "camera pointed at the floor or ground",
    ])

@dataclass
class BrandingConfig:
    """Brand design tokens, watermark parameters, and canvas dimensions."""
    story_width: int = 1080
    story_height: int = 1920
    
    # Palette tokens (Housefix.lk standard)
    color_navy: Tuple[int, int, int] = (15, 32, 51)         # #0F2033
    color_navy_dark: Tuple[int, int, int] = (10, 22, 38)     # #0A1626
    color_brand_blue: Tuple[int, int, int] = (42, 111, 212)  # #2A6FD4
    color_blue_light: Tuple[int, int, int] = (61, 133, 232)  # #3D85E8
    color_silver: Tuple[int, int, int] = (168, 180, 191)     # #A8B4BF
    
    watermark_text: str = "HOUSEFIX.LK"
    watermark_opacity: int = 65
    watermark_shadow_opacity: int = 22
    watermark_font_ratio: float = 0.038
    watermark_min_font: int = 24
    watermark_max_font: int = 76

@dataclass
class MediaFlowConfig:
    """Master configuration container for MediaFlow."""
    quality: QualityGateConfig = field(default_factory=QualityGateConfig)
    semantic: SemanticScorerConfig = field(default_factory=SemanticScorerConfig)
    dedup: DeduplicationConfig = field(default_factory=DeduplicationConfig)
    video: VideoIntelligenceConfig = field(default_factory=VideoIntelligenceConfig)
    branding: BrandingConfig = field(default_factory=BrandingConfig)
