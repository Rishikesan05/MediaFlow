"""
CLIP Semantic Relevance Scorer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Evaluates visual candidates against positive domain concepts (wide angles,
active progress, clean architectural finishes) and negative clutter concepts
(receipts, blueprints, close-up plumbing, debris, camera shake).
"""

from typing import List, Tuple, Optional
from PIL import Image
import numpy as np

from mediaflow.config import SemanticScorerConfig
from mediaflow.core.clip_manager import CLIPManager
from mediaflow.curator.quality_filter import PhotoRecord


class SemanticScorer:
    """
    Applies zero-shot CLIP prompt scoring to filter uncurated site photos.
    """

    def __init__(self, clip_manager: CLIPManager, config: Optional[SemanticScorerConfig] = None):
        self.clip_mgr = clip_manager
        self.config = config or SemanticScorerConfig()
        self._pos_embs: Optional[np.ndarray] = None
        self._neg_embs: Optional[np.ndarray] = None

    def _init_prompt_embeddings(self):
        """Computes and caches text embeddings for positive and negative prompt sets."""
        if self._pos_embs is None:
            self._pos_embs = self.clip_mgr.encode_texts(self.config.positive_prompts)
        if self._neg_embs is None:
            self._neg_embs = self.clip_mgr.encode_texts(self.config.negative_prompts)

    def score_batch(self, photos: List[PhotoRecord]) -> Tuple[List[PhotoRecord], int]:
        """
        Calculates semantic relevance score for a list of PhotoRecords.
        Relevance delta = max(Positive Cosine Similarity) - max(Negative Cosine Similarity).
        """
        self._init_prompt_embeddings()
        passed_photos: List[PhotoRecord] = []
        rejected_count = 0
        total = len(photos)
        batch_size = self.config.batch_size

        for i in range(0, total, batch_size):
            batch = photos[i:i + batch_size]
            pil_images = []
            valid_indices = []

            for idx, p in enumerate(batch):
                try:
                    img = Image.open(p.path)
                    pil_images.append(img.convert("RGB"))
                    valid_indices.append(idx)
                except Exception:
                    rejected_count += 1

            if not pil_images:
                continue

            img_embs = self.clip_mgr.encode_images(pil_images)

            for idx_in_batch, real_idx in enumerate(valid_indices):
                photo = batch[real_idx]
                emb = img_embs[idx_in_batch]

                pos_scores = emb @ self._pos_embs.T
                neg_scores = emb @ self._neg_embs.T

                max_pos = float(pos_scores.max())
                max_neg = float(neg_scores.max())
                relevance = max_pos - max_neg

                photo.relevance = relevance
                photo.max_pos = max_pos
                photo.max_neg = max_neg

                # Rejection criteria:
                # 1. Negative concept exceeds positive alignment.
                # 2. Positive signal is below minimum confidence threshold.
                if max_neg > max_pos or max_pos < self.config.min_positive_threshold:
                    rejected_count += 1
                else:
                    passed_photos.append(photo)

        return passed_photos, rejected_count
