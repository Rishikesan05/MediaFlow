"""
CLIP Inference & Embedding Engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Hardware-accelerated embedding generation using OpenAI's CLIP architecture
(ViT-B/32). Generates L2-normalized representations in shared multimodal space.
"""

from typing import List, Optional
import numpy as np
from PIL import Image

try:
    import torch
    from transformers import CLIPModel, CLIPProcessor
except ImportError:
    torch = None
    CLIPModel = None
    CLIPProcessor = None


class CLIPManager:
    """
    Manages loading, device placement, and batch inference for CLIP ViT-B/32.
    """

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", device: Optional[str] = None):
        self.model_name = model_name
        self._model = None
        self._processor = None
        
        if torch is not None:
            self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = "cpu"

    def _ensure_loaded(self):
        """Lazy loader for PyTorch and Transformers model weights."""
        if self._model is not None and self._processor is not None:
            return

        if torch is None or CLIPModel is None or CLIPProcessor is None:
            raise ImportError(
                "PyTorch and Transformers are required for CLIP inference. "
                "Install with: pip install torch torchvision transformers"
            )

        self._processor = CLIPProcessor.from_pretrained(self.model_name)
        self._model = CLIPModel.from_pretrained(self.model_name).to(self.device)
        self._model.eval()

    def encode_images(self, pil_images: List[Image.Image]) -> np.ndarray:
        """
        Generates L2-normalized 512-dim visual embeddings for a batch of PIL Images.
        """
        self._ensure_loaded()
        inputs = self._processor(images=pil_images, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            vision_outputs = self._model.vision_model(**inputs)
            emb = self._model.visual_projection(vision_outputs.pooler_output)
            emb = emb / emb.norm(dim=-1, keepdim=True)
        return emb.cpu().numpy()

    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generates L2-normalized 512-dim text embeddings for a list of prompt strings.
        """
        self._ensure_loaded()
        inputs = self._processor(text=texts, return_tensors="pt", padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            text_outputs = self._model.text_model(**inputs)
            emb = self._model.text_projection(text_outputs.pooler_output)
            emb = emb / emb.norm(dim=-1, keepdim=True)
        return emb.cpu().numpy()
