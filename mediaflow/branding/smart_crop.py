"""
Edge-Aware Smart 1:1 Cropping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Calculates visual energy distribution using Sobel / edge gradients and
Gaussian smoothing, centering the square crop on the scene's focal center.
"""

from typing import Tuple
from PIL import Image, ImageFilter
import numpy as np


class SmartCropper:
    """
    Computes optimal center-of-interest 1:1 square crops for Instagram feeds.
    """

    @staticmethod
    def crop_1x1(image: Image.Image) -> Image.Image:
        """
        Extracts 1:1 square crop centered around visual edge energy.
        """
        width, height = image.size
        if width == height:
            return image

        crop_size = min(width, height)

        try:
            # Grayscale edge gradient detection
            gray = image.convert("L")
            edges = gray.filter(ImageFilter.FIND_EDGES)
            blurred = edges.filter(ImageFilter.GaussianBlur(radius=20))
            edge_array = np.array(blurred, dtype=np.float32)

            total_energy = edge_array.sum()
            if total_energy > 0:
                y_indices, x_indices = np.mgrid[0:edge_array.shape[0], 0:edge_array.shape[1]]
                cx = int((x_indices * edge_array).sum() / total_energy)
                cy = int((y_indices * edge_array).sum() / total_energy)
            else:
                cx, cy = width // 2, height // 2
        except Exception:
            cx, cy = width // 2, height // 2

        # Compute bounding box clamped to image edges
        left = max(0, min(cx - crop_size // 2, width - crop_size))
        top = max(0, min(cy - crop_size // 2, height - crop_size))
        right = left + crop_size
        bottom = top + crop_size

        return image.crop((left, top, right, bottom))
