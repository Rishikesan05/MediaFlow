"""
Contact Sheet Generator
~~~~~~~~~~~~~~~~~~~~~~~
Generates high-resolution thumbnail grid contact sheets with sequential index
labels for rapid executive review and client sign-off.
"""

import os
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont

from mediaflow.curator.quality_filter import PhotoRecord


class ContactSheetGenerator:
    """
    Renders structured multi-column proof sheets of curated photo candidates.
    """

    def __init__(
        self,
        columns: int = 7,
        thumbnail_size: int = 200,
        padding: int = 6,
        label_height: int = 22,
        background_color: Tuple[int, int, int] = (30, 30, 30),
    ):
        self.columns = columns
        self.thumbnail_size = thumbnail_size
        self.padding = padding
        self.label_height = label_height
        self.background_color = background_color

    def generate(self, photos: List[PhotoRecord], output_path: str) -> str:
        """
        Renders and saves a contact sheet JPEG from a list of curated PhotoRecords.
        """
        if not photos:
            raise ValueError("No photos provided for contact sheet generation.")

        cols = self.columns
        rows = (len(photos) + cols - 1) // cols

        cell_w = self.thumbnail_size + self.padding
        cell_h = self.thumbnail_size + self.padding + self.label_height

        sheet_w = cols * cell_w + self.padding
        sheet_h = rows * cell_h + self.padding

        sheet = Image.new("RGB", (sheet_w, sheet_h), self.background_color)
        draw = ImageDraw.Draw(sheet)

        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except (IOError, OSError):
            font = ImageFont.load_default()

        for idx, photo in enumerate(photos):
            r = idx // cols
            c = idx % cols
            x = self.padding + c * cell_w
            y = self.padding + r * cell_h

            try:
                with Image.open(photo.path) as img:
                    img_thumb = img.copy()
                    img_thumb.thumbnail((self.thumbnail_size, self.thumbnail_size))
                    tw, th = img_thumb.size
                    tx = x + (self.thumbnail_size - tw) // 2
                    ty = y + (self.thumbnail_size - th) // 2
                    sheet.paste(img_thumb, (tx, ty))
            except Exception:
                draw.rectangle(
                    [x, y, x + self.thumbnail_size, y + self.thumbnail_size],
                    fill=(90, 20, 20)
                )

            label = f"Photo {idx + 1:03d}"
            draw.text(
                (x + 4, y + self.thumbnail_size + 2),
                label,
                fill=(240, 240, 240),
                font=font
            )

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        sheet.save(output_path, "JPEG", quality=90)
        return output_path
