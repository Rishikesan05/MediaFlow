"""
Timeline Milestone Curation Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Chronological epoch partitioning that guarantees uniform visual storytelling
across the total project lifecycle, shortlisting exactly target_count photos
(e.g., 45 photos from 2,000+ raw captures).
"""

from datetime import timedelta
from typing import List, Optional

from mediaflow.curator.quality_filter import PhotoRecord


class TimelineCurator:
    """
    Equidistant epoch sampling engine.
    Eliminates bias toward high-frequency capture days while ensuring every
    renovation phase is represented proportionally.
    """

    def __init__(self, target_count: int = 45):
        self.target_count = target_count

    def curate(self, photos: List[PhotoRecord], target_count: Optional[int] = None) -> List[PhotoRecord]:
        """
        Partitions the project timespan into equal intervals and selects
        the highest-scoring photo from each epoch.
        """
        target = target_count or self.target_count
        if not photos:
            return []

        if len(photos) <= target:
            return sorted(photos, key=lambda x: x.timestamp)

        # Sort chronologically
        photos_sorted = sorted(photos, key=lambda x: x.timestamp)
        first_date = photos_sorted[0].timestamp
        last_date = photos_sorted[-1].timestamp
        total_seconds = max(1.0, (last_date - first_date).total_seconds())

        interval_seconds = total_seconds / target
        interval_delta = timedelta(seconds=interval_seconds)

        intervals = []
        for i in range(target):
            start = first_date + i * interval_delta
            end = start + interval_delta if i < target - 1 else last_date + timedelta(seconds=1)
            intervals.append((start, end))

        selected: List[PhotoRecord] = []
        picked_indices = set()

        # Pass 1: Select the top-scoring candidate per epoch
        for start, end in intervals:
            interval_candidates = [
                (idx, p) for idx, p in enumerate(photos_sorted)
                if start <= p.timestamp < end and idx not in picked_indices
            ]
            if interval_candidates:
                best_idx, best_photo = max(
                    interval_candidates,
                    key=lambda item: item[1].get_curator_score()
                )
                best_photo.is_curated = True
                selected.append(best_photo)
                picked_indices.add(best_idx)

        # Pass 2: Backfill vacant epochs from top overall scoring unselected candidates
        if len(selected) < target:
            unselected = [
                (idx, p) for idx, p in enumerate(photos_sorted)
                if idx not in picked_indices
            ]
            unselected.sort(key=lambda item: item[1].get_curator_score(), reverse=True)
            needed = target - len(selected)

            for idx, photo in unselected[:needed]:
                photo.is_curated = True
                selected.append(photo)
                picked_indices.add(idx)

        # Final chronological presentation
        selected.sort(key=lambda x: x.timestamp)
        return selected
