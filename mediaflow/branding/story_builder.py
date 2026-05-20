"""
1080x1920 Story Canvas Compositor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generates branded vertical composite layouts for Instagram and Facebook Stories,
featuring dual photo splits, brand borders, typography headers, and runner bars.
"""

import os
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageOps, ImageFont

from mediaflow.config import BrandingConfig
from mediaflow.branding.watermark import WatermarkEngine


class StoryCompositor:
    """
    Builds production-ready 1080x1920 social story assets.
    """

    def __init__(self, config: Optional[BrandingConfig] = None):
        self.config = config or BrandingConfig()
        self.watermark_engine = WatermarkEngine(self.config)

    def _create_rounded_image(self, image: Image.Image, size: Tuple[int, int], radius: int = 18) -> Image.Image:
        """Resizes/crops image to fit dimensions with smooth rounded corners."""
        fitted = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, size[0], size[1]], radius=radius, fill=255)

        output = Image.new("RGBA", size, (0, 0, 0, 0))
        output.paste(fitted, (0, 0), mask=mask)
        return output

    def build_story(
        self,
        top_image_path: str,
        bottom_image_path: str,
        output_path: str,
        banner_path: Optional[str] = None
    ) -> str:
        """
        Composites a 1080x1920 dual-frame story with brand borders and runner bars.
        """
        w, h = self.config.story_width, self.config.story_height

        # Initialize canvas with dark navy background
        canvas = Image.new("RGB", (w, h), self.config.color_navy_dark)
        draw = ImageDraw.Draw(canvas)

        # Brand Blue outer border
        border_w = 6
        draw.rectangle([0, 0, w - 1, h - 1], outline=self.config.color_brand_blue, width=border_w)

        # Top header text
        try:
            header_font = ImageFont.truetype("arialbd.ttf", 22)
        except (IOError, OSError):
            header_font = ImageFont.load_default()

        header_text = self.config.watermark_text.upper()
        draw.text((30, 20), header_text, fill=self.config.color_silver, font=header_font)

        # Image slot dimensions
        slot_w = w - 40
        slot_h = (h - 220) // 2
        corner_r = 18

        # Load, enhance and round top image
        with Image.open(top_image_path) as top_img:
            enhanced_top = self.watermark_engine.color_enhance(top_img)
            watermarked_top = self.watermark_engine.apply_running_text(enhanced_top)
            rounded_top = self._create_rounded_image(watermarked_top, (slot_w, slot_h), radius=corner_r)
            canvas.paste(rounded_top, (20, 65), mask=rounded_top)

        # Load, enhance and round bottom image
        with Image.open(bottom_image_path) as btm_img:
            enhanced_btm = self.watermark_engine.color_enhance(btm_img)
            watermarked_btm = self.watermark_engine.apply_running_text(enhanced_btm)
            rounded_btm = self._create_rounded_image(watermarked_btm, (slot_w, slot_h), radius=corner_r)
            canvas.paste(rounded_btm, (20, 85 + slot_h), mask=rounded_btm)

        # Middle runner bar / banner
        if banner_path and os.path.exists(banner_path):
            with Image.open(banner_path) as banner:
                banner_rgba = banner.convert("RGBA")
                b_w = slot_w
                b_h = int(b_w * (banner_rgba.height / banner_rgba.width))
                resized_banner = banner_rgba.resize((b_w, min(b_h, 70)), Image.Resampling.LANCZOS)
                canvas.paste(resized_banner, (20, 70 + slot_h), mask=resized_banner)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        canvas.save(output_path, "JPEG", quality=92)
        return output_path
