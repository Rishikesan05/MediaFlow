"""
CLIP Video Scene Importance Ranker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Evaluates extracted scene keyframes against domain construction importance prompts
vs low-importance prompts, assigning priority tiers (HIGH / MED / LOW).
"""

from typing import List, Optional
from PIL import Image
import numpy as np

from mediaflow.config import VideoIntelligenceConfig
from mediaflow.core.clip_manager import CLIPManager
from mediaflow.video.scene_splitter import VideoScene


class SceneRanker:
    """
    Ranks extracted video scenes using CLIP zero-shot keyframe scoring.
    """

    def __init__(self, clip_manager: CLIPManager, config: Optional[VideoIntelligenceConfig] = None):
        self.clip_mgr = clip_manager
        self.config = config or VideoIntelligenceConfig()
        self._imp_embs: Optional[np.ndarray] = None
        self._low_embs: Optional[np.ndarray] = None

    def _init_prompt_embeddings(self):
        """Precomputes text embeddings for video importance prompts."""
        if self._imp_embs is None:
            self._imp_embs = self.clip_mgr.encode_texts(self.config.importance_prompts)
        if self._low_embs is None:
            self._low_embs = self.clip_mgr.encode_texts(self.config.low_importance_prompts)

    def rank_scenes(self, scenes: List[VideoScene]) -> List[VideoScene]:
        """
        Evaluates scene keyframes and assigns importance scores and labels.
        """
        if not scenes:
            return []

        self._init_prompt_embeddings()

        for scene in scenes:
            if not scene.keyframe_path:
                scene.importance_score = 0.5
                scene.importance_label = "MED"
                continue

            try:
                with Image.open(scene.keyframe_path) as img:
                    img_emb = self.clip_mgr.encode_images([img.convert("RGB")])[0]

                high_sim = float((img_emb @ self._imp_embs.T).mean())
                low_sim = float((img_emb @ self._low_embs.T).mean())

                net_score = high_sim - low_sim
                # Normalize score to [0.0, 1.0]
                normalized = max(0.0, min(1.0, (net_score + 0.1) / 0.3))

                if normalized >= self.config.high_importance_cutoff:
                    label = "HIGH"
                elif normalized >= self.config.med_importance_cutoff:
                    label = "MED"
                else:
                    label = "LOW"

                scene.importance_score = normalized
                scene.importance_label = label

            except Exception:
                scene.importance_score = 0.5
                scene.importance_label = "MED"

        # Sort scenes by importance descending
        return sorted(scenes, key=lambda s: s.importance_score, reverse=True)
