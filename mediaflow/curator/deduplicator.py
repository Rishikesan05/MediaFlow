"""
Visual Embedding Deduplicator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Temporal window clustering and cosine similarity thresholding to identify
and eliminate burst captures, near-identical viewpoints, and visual duplicates.
"""

from datetime import timedelta
from typing import List
from PIL import Image
import numpy as np

from mediaflow.config import DeduplicationConfig
from mediaflow.core.clip_manager import CLIPManager
from mediaflow.curator.quality_filter import PhotoRecord


class VisualDeduplicator:
    """
    Cluster-based visual deduplication engine powered by CLIP embeddings.
    """

    def __init__(self, clip_manager: CLIPManager, config: Optional[DeduplicationConfig] = None):
        self.clip_mgr = clip_manager
        self.config = config or DeduplicationConfig()

    def deduplicate(self, photos: List[PhotoRecord]) -> List[PhotoRecord]:
        """
        Sorts photos chronologically, clusters events within temporal windows,
        and eliminates near-duplicates exceeding the cosine similarity threshold.
        """
        if not photos:
            return []

        # Chronological sorting
        photos_sorted = sorted(photos, key=lambda x: x.timestamp)
        survivors: List[PhotoRecord] = []
        i = 0
        n = len(photos_sorted)
        window = timedelta(hours=self.config.temporal_window_hours)

        while i < n:
            current_time = photos_sorted[i].timestamp
            cluster_indices = [i]

            # Collect subsequent photos falling into the temporal window
            j = i + 1
            while j < n and (photos_sorted[j].timestamp - current_time) <= window:
                cluster_indices.append(j)
                j += 1

            # Single photo in window survives unconditionally
            if len(cluster_indices) == 1:
                survivors.append(photos_sorted[i])
                i += 1
                continue

            # Load images for cluster embedding computation
            cluster_pils = []
            valid_cluster_idx = []
            for c_idx in cluster_indices:
                try:
                    img = Image.open(photos_sorted[c_idx].path)
                    cluster_pils.append(img.convert("RGB"))
                    valid_cluster_idx.append(c_idx)
                except Exception:
                    pass

            if not cluster_pils:
                i = j
                continue

            # Compute pairwise visual similarities
            embs = self.clip_mgr.encode_images(cluster_pils)
            used_indices = set()

            for emb_idx, real_idx in enumerate(valid_cluster_idx):
                if real_idx in used_indices:
                    continue

                near_dups = [real_idx]
                emb_a = embs[emb_idx]

                for other_emb_idx, other_real_idx in enumerate(valid_cluster_idx):
                    if other_real_idx == real_idx or other_real_idx in used_indices:
                        continue
                    emb_b = embs[other_emb_idx]
                    sim = float(np.dot(emb_a, emb_b))

                    if sim >= self.config.cosine_similarity_threshold:
                        near_dups.append(other_real_idx)

                # Elect the candidate with the highest composite curator score
                best_photo = max(
                    near_dups,
                    key=lambda idx_val: photos_sorted[idx_val].get_curator_score()
                )
                survivors.append(photos_sorted[best_photo])

                for dup_idx in near_dups:
                    used_indices.add(dup_idx)

            i = j

        return survivors
