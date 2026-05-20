"""
Dual-Layer Watermarking & Color Enhancement Engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Applies dynamic running-text anti-theft watermarks, bottom branding banner runners,
and automated color/lighting equalization to preserve brand identity across media.
"""

import os
from typing import Optional, Tuple
from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps,
    ImageStat,
)

from mediaflow.config import BrandingConfig

FONT_FALLBACKS = [
    r"C:\Windows\Fonts\Montserrat-Bold.ttf",
    r"C:\Windows\Fonts\bahnschriftbd.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arial.ttf",
]


class WatermarkEngine:
    """
    Renders subtle running text watermarks and brand banners onto images.
    """

    def __init__(self, config: Optional[BrandingConfig] = None):
        self.config = config or BrandingConfig()

    def _resolve_font(self, font_size: int) -> ImageFont.ImageFont:
        """Finds the best available TrueType font or falls back to default."""
        for path in FONT_FALLBACKS:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, font_size)
                except (IOError, OSError):
                    continue
        return ImageFont.load_default()

    def color_enhance(self, image: Image.Image) -> Image.Image:
        """
        Enhances lighting, contrast, white balance, and sharpness.
        """
        rgb_img = image.convert("RGB")

        # 1. White balance equalization
        r, g, b = rgb_img.split()
        r_avg = ImageStat.Stat(r).mean[0]
        g_avg = ImageStat.Stat(g).mean[0]
        b_avg = ImageStat.Stat(b).mean[0]
        avg = (r_avg + g_avg + b_avg) / 3.0

        if r_avg > 0 and g_avg > 0 and b_avg > 0:
            r = r.point(lambda x: min(255, int(x * (avg / r_avg))))
            g = g.point(lambda x: min(255, int(x * (avg / g_avg))))
            b = b.point(lambda x: min(255, int(x * (avg / b_avg))))
            rgb_img = Image.merge("RGB", (r, g, b))

        # 2. Autocontrast
        rgb_img = ImageOps.autocontrast(rgb_img, cutoff=0.5)

        # 3. Dynamic brightness adaptation
        gray = rgb_img.convert("L")
        lum = ImageStat.Stat(gray).mean[0]
        if lum < 50 or lum > 200:
            factor = max(0.75, min(1.35, 120.0 / max(lum, 1.0)))
            rgb_img = ImageEnhance.Brightness(rgb_img).enhance(factor)

        # 4. Color saturation & gentle sharpening
        rgb_img = ImageEnhance.Color(rgb_img).enhance(1.12)
        rgb_img = ImageEnhance.Sharpness(rgb_img).enhance(1.20)
        return rgb_img

    def apply_running_text(self, image: Image.Image) -> Image.Image:
        """
        Renders a subtle, semi-transparent diagonal/horizontal text chain across image center.
        """
        base = image.convert("RGBA")
        width, height = base.size

        font_size = int(width * self.config.watermark_font_ratio)
        font_size = max(self.config.watermark_min_font, min(font_size, self.config.watermark_max_font))
        font = self._resolve_font(font_size)

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        text = self.config.watermark_text
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except AttributeError:
            text_w, text_h = draw.textsize(text, font=font)

        center_y = (height - text_h) // 2
        spacing = max(40, int(text_w * 0.35))
        x_pos = -text_w

        op_main = self.config.watermark_opacity
        op_shadow = self.config.watermark_shadow_opacity

        while x_pos < width + text_w:
            # Shadow pass
            draw.text(
                (x_pos + 2, center_y + 2),
                text,
                font=font,
                fill=(255, 255, 255, op_shadow),
                stroke_width=1,
                stroke_fill=(255, 255, 255, max(8, op_shadow // 2)),
            )
            # Main pass
            draw.text(
                (x_pos, center_y),
                text,
                font=font,
                fill=(0, 0, 0, op_main),
                stroke_width=1,
                stroke_fill=(255, 255, 255, max(12, op_main // 3)),
            )
            x_pos += text_w + spacing

        return Image.alpha_composite(base, overlay).convert("RGB")

    def apply_banner(self, image: Image.Image, banner_path: str) -> Image.Image:
        """
        Scales and overlays a bottom branding banner.
        """
        if not os.path.exists(banner_path):
            return image

        with Image.open(banner_path) as banner:
            banner_rgba = banner.convert("RGBA")
            img_rgba = image.convert("RGBA")
            w, h = img_rgba.size

            aspect = banner_rgba.height / banner_rgba.width
            new_banner_w = w
            new_banner_h = int(new_banner_w * aspect)

            resized = banner_rgba.resize((new_banner_w, new_banner_h), Image.Resampling.LANCZOS)
            pos = (0, h - new_banner_h)
            img_rgba.paste(resized, pos, resized)
            return img_rgba.convert("RGB")
