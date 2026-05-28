"""
Integration Tests for MediaFlow Pipeline Architecture
"""

from datetime import datetime, timedelta
from mediaflow.config import MediaFlowConfig
from mediaflow.curator.quality_filter import QualityGate, PhotoRecord
from mediaflow.curator.timeline_selector import TimelineCurator
from mediaflow.branding.watermark import WatermarkEngine

def test_full_configuration():
    config = MediaFlowConfig()
    assert config.quality.min_brightness == 35.0
    assert config.dedup.target_curation_count == 45
    assert len(config.semantic.positive_prompts) > 0
    assert len(config.semantic.negative_prompts) > 0
    assert config.branding.story_width == 1080
    assert config.branding.story_height == 1920

def test_curation_pipeline_flow():
    base_time = datetime(2026, 4, 1, 8, 0, 0)
    photos = []
    # Simulate a stream of 2,000 photos
    for i in range(2000):
        ts = base_time + timedelta(minutes=i * 20)
        relevance = 0.2 + (i % 50) * 0.015
        rec = PhotoRecord(
            name=f"IMG_{i:04d}.jpg",
            path=f"/dummy/path/IMG_{i:04d}.jpg",
            timestamp=ts,
            file_size_kb=800.0,
            brightness=75.0,
            blur_score=110.0,
            quality_score=0.9,
            relevance=relevance
        )
        photos.append(rec)

    # 1. Timeline curation to exact target
    curator = TimelineCurator(target_count=45)
    curated = curator.curate(photos, target_count=45)

    assert len(curated) == 45
    for i in range(len(curated) - 1):
        assert curated[i].timestamp <= curated[i + 1].timestamp

def test_watermark_engine_initialization():
    engine = WatermarkEngine()
    assert engine.config.watermark_text == "HOUSEFIX.LK"

if __name__ == "__main__":
    test_full_configuration()
    test_curation_pipeline_flow()
    test_watermark_engine_initialization()
    print("All MediaFlow integration tests passed successfully!")
