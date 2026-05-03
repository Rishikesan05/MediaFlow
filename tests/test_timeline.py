"""
Unit Tests for Timeline Milestone Curator
"""

from datetime import datetime, timedelta
from mediaflow.curator.quality_filter import PhotoRecord
from mediaflow.curator.timeline_selector import TimelineCurator

def test_timeline_curator_exact_count():
    base_time = datetime(2026, 4, 1, 9, 0, 0)
    # Simulate 500 photos over a 30-day renovation project
    photos = []
    for i in range(500):
        t = base_time + timedelta(hours=i * 1.4)
        rec = PhotoRecord(
            name=f"test_{i:04d}.jpg",
            path=f"/fake/path/test_{i:04d}.jpg",
            timestamp=t,
            file_size_kb=500.0,
            brightness=80.0,
            blur_score=150.0,
            quality_score=0.85,
            relevance=0.4 + (i % 20) * 0.02
        )
        photos.append(rec)

    curator = TimelineCurator(target_count=45)
    curated = curator.curate(photos)

    assert len(curated) == 45, f"Expected 45 curated photos, got {len(curated)}"
    # Verify strict chronological ordering
    for i in range(len(curated) - 1):
        assert curated[i].timestamp <= curated[i + 1].timestamp

    # Check timespan coverage from start to finish
    assert (curated[0].timestamp - photos[0].timestamp).total_seconds() < 86400 * 2
    assert (curated[-1].timestamp - curated[0].timestamp).days >= 25

def test_timeline_curator_fewer_than_target():
    base_time = datetime(2026, 4, 1, 9, 0, 0)
    photos = [
        PhotoRecord(
            name=f"test_{i}.jpg",
            path=f"/fake/{i}.jpg",
            timestamp=base_time + timedelta(days=i),
            file_size_kb=200.0,
            relevance=0.5
        )
        for i in range(10)
    ]
    curator = TimelineCurator(target_count=45)
    curated = curator.curate(photos)
    assert len(curated) == 10

if __name__ == "__main__":
    test_timeline_curator_exact_count()
    test_timeline_curator_fewer_than_target()
    print("Timeline curator tests passed successfully!")
