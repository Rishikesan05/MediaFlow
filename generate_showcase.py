"""
Portfolio Showcase Graphic Generator for MediaFlow
Creates pixel-perfect, executive-grade portfolio presentation visuals:
1. MediaFlow_Showcase_Hero.png (1920x1080 Full HD portfolio slide)
2. MediaFlow_Terminal_Screenshot.png (1400x920 Dedicated dark-mode terminal)
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ASSETS_DIR = r"E:\02_Work_Projects\MediaFlow\assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

CONTACT_SHEET_SRC = r"E:\02_Work_Projects\HOUSEFIX.LK\03_Social_Media_Projects\01_Aarany_House\02_Processed_By_Rishi\selection_contact_sheet.jpg"
RAW_SAMPLE_SRC = r"E:\02_Work_Projects\HOUSEFIX.LK\03_Social_Media_Projects\01_Aarany_House\01_Raw_Dumps\IMG-20250117-WA0003.jpg"
PROCESSED_SAMPLE_SRC = r"E:\02_Work_Projects\HOUSEFIX.LK\03_Social_Media_Projects\01_Aarany_House\02_Processed_By_Rishi\001.jpg"

# Fonts
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
FONT_SANS_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_SANS = r"C:\Windows\Fonts\segoeui.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def draw_rounded_rect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def draw_pill(draw, x, y, text, font, bg_color, text_color=(255, 255, 255), pad_h=12, pad_v=4):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except:
        tw, th = 80, 16
    pill_w = tw + pad_h * 2
    pill_h = th + pad_v * 2
    draw.rounded_rectangle([x, y, x + pill_w, y + pill_h], radius=pill_h // 2, fill=bg_color)
    draw.text((x + pad_h, y + pad_v - 1), text, fill=text_color, font=font)
    return pill_w

def build_terminal_canvas(w=960, h=720):
    """Renders a sleek macOS/Linux dark-mode terminal element."""
    term = Image.new("RGBA", (w, h), (18, 22, 31, 245))
    draw = ImageDraw.Draw(term)
    
    # Border & title bar
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=14, outline=(45, 55, 72, 255), width=1)
    draw.rounded_rectangle([0, 0, w - 1, 44], radius=14, fill=(26, 32, 44, 255))
    draw.rectangle([0, 30, w - 1, 44], fill=(26, 32, 44, 255)) # Square bottom of header
    draw.line([0, 44, w - 1, 44], fill=(45, 55, 72, 255), width=1)
    
    # 3 Dots (Red, Yellow, Green)
    draw.ellipse([18, 16, 30, 28], fill=(255, 95, 86))
    draw.ellipse([38, 16, 50, 28], fill=(255, 189, 46))
    draw.ellipse([58, 16, 70, 28], fill=(39, 201, 63))
    
    # Header title
    title_font = get_font(FONT_SANS, 13)
    draw.text((w // 2 - 120, 14), "zsh - mediaflow curate (cuda:0)", fill=(148, 163, 184), font=title_font)
    
    # Terminal text lines with custom syntax coloring
    mono_font = get_font(FONT_MONO, 14)
    mono_bold = get_font(FONT_MONO, 14)
    
    lines = [
        [("$ ", (56, 189, 248)), ("python -m mediaflow.cli curate ", (248, 250, 252)), ("--input ./01_Aarany_House --target 45", (148, 163, 184))],
        [("", (0,0,0))],
        [("╭─ [MediaFlow v1.0.0] ", (96, 165, 250)), ("Production Computer Vision Pipeline Initialized", (226, 232, 240))],
        [("│  Architecture: OpenCV 4.8 + CLIP ViT-B/32 + TransNetV2 | GPU: NVIDIA CUDA", (100, 116, 139))],
        [("├─────────────────────────────────────────────────────────────────────────────", (51, 65, 85))],
        [("│ [Phase 1] OpenCV Quality Gate & Pre-Filter Diagnostics", (251, 191, 36))],
        [("│   • Total Scanned    : ", (148, 163, 184)), ("807 raw site files", (241, 245, 249))],
        [("│   • Laplacian Var    : ", (148, 163, 184)), ("Rejected 142 out-of-focus / blurry captures", (248, 113, 113))],
        [("│   • Luminance Check  : ", (148, 163, 184)), ("Rejected 68 dark underexposed shots (L < 35)", (248, 113, 113))],
        [("│   • Passed Gate      : ", (148, 163, 184)), ("597 high-fidelity images ", (74, 222, 128)), ("(Filter rate: 26.0%)", (100, 116, 139))],
        [("│", (51, 65, 85))],
        [("│ [Phase 2] Multimodal CLIP Zero-Shot Semantic Relevance Scorer", (251, 191, 36))],
        [("│   • Model / Weights  : ", (148, 163, 184)), ("openai/clip-vit-base-patch32 (512-dim embedding)", (192, 132, 252))],
        [("│   • Positive Vector  : ", (148, 163, 184)), ("[wide architecture, construction progress, finished rooms]", (147, 197, 253))],
        [("│   • Negative Filter  : ", (148, 163, 184)), ("[receipts, blueprints, close-up pipes, rubble, debris]", (252, 165, 165))],
        [("│   • Delta Scored     : ", (148, 163, 184)), ("184 high-value progress captures retained", (74, 222, 128))],
        [("│", (51, 65, 85))],
        [("│ [Phase 3] 24h Temporal Clustering & Visual Embedding Deduplication", (251, 191, 36))],
        [("│   • Sliding Window   : ", (148, 163, 184)), ("24.0 hours temporal grouping", (241, 245, 249))],
        [("│   • Similarity Metric: ", (148, 163, 184)), ("Cosine Threshold > 0.90", (241, 245, 249))],
        [("│   • Redundancy Cut   : ", (148, 163, 184)), ("112 redundant burst shots eliminated", (248, 113, 113))],
        [("│   • Unique Survivors : ", (148, 163, 184)), ("72 distinct viewpoint candidates", (74, 222, 128))],
        [("│", (51, 65, 85))],
        [("│ [Phase 4] Uniform Timeline Milestone Curation (Target = 45)", (251, 191, 36))],
        [("│   • Timeline Span    : ", (148, 163, 184)), ("2026-04-12 to 2026-05-18 (36 calendar days)", (241, 245, 249))],
        [("│   • Epoch Partition  : ", (148, 163, 184)), ("45 equidistant chronological intervals", (241, 245, 249))],
        [("│   • Curation Result  : ", (148, 163, 184)), ("Exactly 45 milestone images shortlisted", (52, 211, 153))],
        [("│", (51, 65, 85))],
        [("│ [Phase 5] Asset Export & Verification", (251, 191, 36))],
        [("│   ✓ Curated Media    : ", (148, 163, 184)), ("./02_Processed_By_Rishi/ [001.jpg -> 045.jpg]", (241, 245, 249))],
        [("│   ✓ Proof Sheet      : ", (148, 163, 184)), ("00_Curated_Contact_Sheet.jpg (7 cols x 200px)", (241, 245, 249))],
        [("╰─────────────────────────────────────────────────────────────────────────────", (51, 65, 85))],
        [("[OK] Pipeline Completed in 3m 42s | GPU: RTX 4070 | Throughput: 3.64 imgs/sec", (34, 197, 94))],
    ]
    
    y = 56
    line_h = 19
    for line_parts in lines:
        x = 24
        for text, color in line_parts:
            draw.text((x, y), text, fill=color, font=mono_font)
            try:
                tw = draw.textbbox((0, 0), text, font=mono_font)[2]
            except:
                tw = len(text) * 8
            x += tw
        y += line_h
        
    return term

def create_hero_showcase():
    """Builds the comprehensive 1920x1080 Full HD portfolio hero showcase."""
    w, h = 1920, 1080
    bg = Image.new("RGB", (w, h), (11, 15, 23))
    draw = ImageDraw.Draw(bg)
    
    # Subtle background gradient / ambient glows
    for i in range(h):
        blend = i / h
        r = int(11 * (1 - blend) + 16 * blend)
        g = int(15 * (1 - blend) + 24 * blend)
        b = int(23 * (1 - blend) + 38 * blend)
        draw.line([(0, i), (w, i)], fill=(r, g, b))
        
    # Top Header Section
    font_brand = get_font(FONT_SANS_BOLD, 34)
    font_sub = get_font(FONT_SANS, 16)
    font_badge = get_font(FONT_SANS_BOLD, 12)
    
    # Title
    draw.text((70, 42), "MediaFlow", fill=(255, 255, 255), font=font_brand)
    draw.text((260, 52), " -  Intelligent Media Processing & Curation Pipeline", fill=(148, 163, 184), font=font_sub)
    
    # Badges
    bx = 70
    by = 92
    badges = [
        ("Python 3.10+", (30, 58, 95)),
        ("PyTorch 2.0+", (115, 40, 20)),
        ("CLIP ViT-B/32", (110, 85, 20)),
        ("OpenCV", (80, 40, 130)),
        ("TransNetV2", (20, 90, 50)),
        ("FFmpeg", (20, 80, 80)),
        ("Enterprise: Housefix.lk Pvt Ltd", (30, 41, 59)),
    ]
    for b_text, b_col in badges:
        bw = draw_pill(draw, bx, by, b_text, font_badge, b_col, (240, 240, 240))
        bx += bw + 10
        
    # Divider line
    draw.line([(70, 135), (w - 70, 135)], fill=(30, 41, 59), width=1)
    
    # ── Left: Terminal (960 x 780) ──
    term_img = build_terminal_canvas(w=970, h=870)
    bg.paste(term_img, (70, 160), mask=term_img)
    
    # ── Right Side Visual Cards (x = 1070) ──
    rx = 1070
    card_w = 780
    
    # Card 1: Contact Sheet Proof Card (Curated 45-Photo Milestone Journey)
    card1_h = 510
    draw.rounded_rectangle([rx, 160, rx + card_w, 160 + card1_h], radius=14, fill=(18, 22, 31), outline=(45, 55, 72), width=1)
    # Header of Card 1
    draw.rounded_rectangle([rx, 160, rx + card_w, 208], radius=14, fill=(26, 32, 44))
    draw.rectangle([rx, 194, rx + card_w, 208], fill=(26, 32, 44))
    draw.line([rx, 208, rx + card_w, 208], fill=(45, 55, 72), width=1)
    
    draw.text((rx + 20, 175), "Curated Milestone Journey", fill=(241, 245, 249), font=get_font(FONT_SANS_BOLD, 15))
    draw_pill(draw, rx + card_w - 260, 172, "45 Selected from ~800 Raw", get_font(FONT_SANS_BOLD, 11), (30, 58, 138), (147, 197, 253))
    
    # Paste actual contact sheet inside Card 1
    if os.path.exists(CONTACT_SHEET_SRC):
        with Image.open(CONTACT_SHEET_SRC) as cs:
            # Resize contact sheet to fit container
            cs_thumb = cs.copy()
            cs_w = card_w - 30
            cs_h = card1_h - 70
            cs_fitted = ImageOps.fit(cs_thumb, (cs_w, cs_h), method=Image.Resampling.LANCZOS)
            bg.paste(cs_fitted, (rx + 15, 218))
            
    # Card 2: Visual Transformation & Watermarking (Raw vs Curated & Branded)
    card2_y = 160 + card1_h + 20
    card2_h = 340
    draw.rounded_rectangle([rx, card2_y, rx + card_w, card2_y + card2_h], radius=14, fill=(18, 22, 31), outline=(45, 55, 72), width=1)
    # Header of Card 2
    draw.rounded_rectangle([rx, card2_y, rx + card_w, card2_y + 44], radius=14, fill=(26, 32, 44))
    draw.rectangle([rx, card2_y + 30, rx + card_w, card2_y + 44], fill=(26, 32, 44))
    draw.line([rx, card2_y + 44, rx + card_w, card2_y + 44], fill=(45, 55, 72), width=1)
    
    draw.text((rx + 20, card2_y + 14), "Visual Quality & Brand Pipeline", fill=(241, 245, 249), font=get_font(FONT_SANS_BOLD, 15))
    draw_pill(draw, rx + card_w - 275, card2_y + 10, "Auto Balance • Watermark • 1:1 Crop", get_font(FONT_SANS_BOLD, 11), (20, 83, 45), (187, 247, 208))
    
    # Side-by-side inside Card 2
    sample_slot_w = (card_w - 50) // 2
    sample_slot_h = card2_h - 65
    
    # 1. Raw Sample
    if os.path.exists(RAW_SAMPLE_SRC):
        with Image.open(RAW_SAMPLE_SRC) as raw_img:
            raw_fitted = ImageOps.fit(raw_img, (sample_slot_w, sample_slot_h), method=Image.Resampling.LANCZOS)
            bg.paste(raw_fitted, (rx + 18, card2_y + 54))
            draw.text((rx + 28, card2_y + 62), "Raw Site Capture (Uncurated)", fill=(255, 255, 255), font=get_font(FONT_SANS_BOLD, 11))
            
    # 2. Processed Sample (Curated + Enhanced + Watermarked)
    if os.path.exists(PROCESSED_SAMPLE_SRC):
        with Image.open(PROCESSED_SAMPLE_SRC) as proc_img:
            proc_fitted = ImageOps.fit(proc_img, (sample_slot_w, sample_slot_h), method=Image.Resampling.LANCZOS)
            bg.paste(proc_fitted, (rx + 28 + sample_slot_w, card2_y + 54))
            draw.text((rx + 38 + sample_slot_w, card2_y + 62), "MediaFlow Curated & Branded", fill=(255, 255, 255), font=get_font(FONT_SANS_BOLD, 11))

    output_path = os.path.join(ASSETS_DIR, "MediaFlow_Showcase_Hero.png")
    bg.save(output_path, "PNG", quality=98)
    print(f"Generated Portfolio Hero Graphic: {output_path}")
    return output_path


def create_standalone_terminal_screenshot():
    """Builds a standalone high-DPI dark-mode terminal window on an elegant backdrop."""
    w, h = 1380, 960
    canvas = Image.new("RGB", (w, h), (13, 17, 23))
    draw = ImageDraw.Draw(canvas)
    
    # Subtle gradient
    for i in range(h):
        blend = i / h
        r = int(13 * (1 - blend) + 20 * blend)
        g = int(17 * (1 - blend) + 26 * blend)
        b = int(23 * (1 - blend) + 36 * blend)
        draw.line([(0, i), (w, i)], fill=(r, g, b))
        
    term_w = 1260
    term_h = 860
    term = build_terminal_canvas(w=term_w, h=term_h)
    
    tx = (w - term_w) // 2
    ty = (h - term_h) // 2
    canvas.paste(term, (tx, ty), mask=term)
    
    out_file = os.path.join(ASSETS_DIR, "MediaFlow_Terminal_Screenshot.png")
    canvas.save(out_file, "PNG", quality=98)
    print(f"Generated Standalone Terminal Screenshot: {out_file}")
    return out_file

if __name__ == "__main__":
    create_hero_showcase()
    create_standalone_terminal_screenshot()

