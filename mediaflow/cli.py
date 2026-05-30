"""
MediaFlow Unified Command-Line Interface (CLI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides terminal commands for photo curation, video scene intelligence,
watermarking, and story generation.
"""

import argparse
import sys
import os
import shutil
from typing import List

from mediaflow.config import MediaFlowConfig
from mediaflow.curator.quality_filter import QualityGate, PhotoRecord
from mediaflow.curator.semantic_scorer import SemanticScorer
from mediaflow.curator.deduplicator import VisualDeduplicator
from mediaflow.curator.timeline_selector import TimelineCurator
from mediaflow.curator.contact_sheet import ContactSheetGenerator
from mediaflow.core.clip_manager import CLIPManager
from mediaflow.video.scene_splitter import SceneSplitter
from mediaflow.video.scene_ranker import SceneRanker
from mediaflow.branding.watermark import WatermarkEngine
from mediaflow.branding.story_builder import StoryCompositor
from PIL import Image


def cmd_curate(args):
    """Executes end-to-end intelligent photo curation."""
    input_dir = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output or os.path.join(input_dir, "02_Curated"))
    target_count = args.target

    print("\n" + "=" * 65)
    print(f"  MediaFlow Curation Engine: Ingesting '{input_dir}'")
    print("=" * 65)

    config = MediaFlowConfig()
    gate = QualityGate(config.quality)

    print("\n[Phase 1] Executing OpenCV Quality Gate...")
    records, stats = gate.filter_directory(input_dir)
    print(f"  • Total Scanned : {stats['total_scanned']}")
    print(f"  • Passed Gate   : {stats['passed']}")
    print(f"  • Rejections    : Blur: {stats['rejected_blur']} | Dark: {stats['rejected_dark']} | Small: {stats['rejected_small']}")

    if not records:
        print("[-] No photos passed initial quality check. Exiting.")
        sys.exit(0)

    print("\n[Phase 2] Initializing CLIP Zero-Shot Semantic Scorer...")
    clip_mgr = CLIPManager(config.semantic.model_name, device=args.device)
    scorer = SemanticScorer(clip_mgr, config.semantic)
    semantic_passed, sem_rejected = scorer.score_batch(records)
    print(f"  • Semantic Alignment Passed: {len(semantic_passed)} (Filtered {sem_rejected} irrelevant/clutter photos)")

    print("\n[Phase 3] Computing Visual Embeddings & Temporal Deduplication...")
    dedup = VisualDeduplicator(clip_mgr, config.dedup)
    survivors = dedup.deduplicate(semantic_passed)
    print(f"  • Unique Non-Duplicate Candidates: {len(survivors)} (Eliminated {len(semantic_passed) - len(survivors)} redundant bursts)")

    print(f"\n[Phase 4] Partitioning Timeline into {target_count} Milestone Epochs...")
    curator = TimelineCurator(target_count=target_count)
    final_curated = curator.curate(survivors, target_count=target_count)
    print(f"  • Final Shortlist: Exactly {len(final_curated)} photos selected for storytelling.")

    # Write output files sequentially
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n[Phase 5] Saving Curated Media to '{output_dir}'...")
    for idx, p in enumerate(final_curated):
        ext = os.path.splitext(p.path)[1]
        out_name = f"Photo_{idx + 1:03d}{ext}"
        dest = os.path.join(output_dir, out_name)
        shutil.copy2(p.path, dest)

    # Generate contact sheet
    contact_sheet_path = os.path.join(output_dir, "00_Curated_Contact_Sheet.jpg")
    sheet_gen = ContactSheetGenerator()
    sheet_gen.generate(final_curated, contact_sheet_path)
    print(f"  ✓ Saved Contact Proof Sheet: '{os.path.basename(contact_sheet_path)}'")
    print("\n[✓] MediaFlow Curation Pipeline Finished Successfully!\n")


def cmd_video(args):
    """Executes video scene detection, splitting, and CLIP ranking."""
    video_path = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output or os.path.join(os.path.dirname(video_path), "scenes"))

    print("\n" + "=" * 65)
    print(f"  MediaFlow Video Intelligence: Processing '{video_path}'")
    print("=" * 65)

    splitter = SceneSplitter()
    print("\n[Phase 1 & 2] Detecting Scene Boundaries and Extracting Keyframes...")
    scenes = splitter.process_video(video_path, output_dir, mute_audio=not args.keep_audio)
    print(f"  • Detected and Segmented: {len(scenes)} distinct scene shots.")

    if not scenes:
        print("[-] No scenes detected or video extraction failed.")
        sys.exit(0)

    print("\n[Phase 3] Scoring Keyframe Importance via CLIP...")
    config = MediaFlowConfig()
    clip_mgr = CLIPManager(config.semantic.model_name, device=args.device)
    ranker = SceneRanker(clip_mgr, config.video)
    ranked_scenes = ranker.rank_scenes(scenes)

    print("\n  [Scene Ranking Summary]:")
    for s in ranked_scenes:
        print(f"    • Scene {s.scene_id:03d} [{s.start_sec:05.1f}s - {s.end_sec:05.1f}s] Duration: {s.duration:04.1f}s | Priority: {s.importance_label} (Score: {s.importance_score:.2f})")

    print(f"\n[✓] Video Scenes Exported to: '{output_dir}'\n")


def cmd_watermark(args):
    """Applies running-text and banner watermarks to an image or directory."""
    input_path = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output or os.path.join(os.path.dirname(input_path), "watermarked"))
    banner_path = os.path.abspath(args.banner) if args.banner else None

    engine = WatermarkEngine()
    os.makedirs(output_dir, exist_ok=True)

    if os.path.isfile(input_path):
        paths = [input_path]
    else:
        paths = [
            os.path.join(input_path, f) for f in os.listdir(input_path)
            if os.path.splitext(f)[1].lower() in ('.jpg', '.jpeg', '.png', '.webp')
        ]

    print(f"\nApplying watermarking to {len(paths)} assets...")
    for p in paths:
        with Image.open(p) as img:
            enhanced = engine.color_enhance(img)
            watermarked = engine.apply_running_text(enhanced)
            if banner_path:
                watermarked = engine.apply_banner(watermarked, banner_path)

            out_file = os.path.join(output_dir, os.path.basename(p))
            watermarked.save(out_file, "JPEG", quality=92)
    print(f"[✓] Watermarked media saved to: {output_dir}\n")


def cmd_story(args):
    """Composites a 1080x1920 Instagram Story from two photos."""
    compositor = StoryCompositor()
    out_file = compositor.build_story(
        top_image_path=args.top,
        bottom_image_path=args.bottom,
        output_path=args.output,
        banner_path=args.banner
    )
    print(f"[✓] Story successfully generated at: {out_file}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="mediaflow",
        description="MediaFlow - Intelligent Media Processing & Curation Pipeline"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Curation subcommand
    p_curate = subparsers.add_parser("curate", help="Run full photo curation and deduplication")
    p_curate.add_argument("--input", "-i", required=True, help="Input directory of raw photos")
    p_curate.add_argument("--output", "-o", help="Output directory for curated photos")
    p_curate.add_argument("--target", "-t", type=int, default=45, help="Target curated photo count (default: 45)")
    p_curate.add_argument("--device", choices=["cuda", "cpu"], default=None, help="Inference device")
    p_curate.set_defaults(func=cmd_curate)

    # Video subcommand
    p_video = subparsers.add_parser("video", help="Run video scene detection and importance ranking")
    p_video.add_argument("--input", "-i", required=True, help="Input video file path")
    p_video.add_argument("--output", "-o", help="Output directory for scene clips")
    p_video.add_argument("--keep-audio", action="store_true", help="Preserve audio track instead of muting")
    p_video.add_argument("--device", choices=["cuda", "cpu"], default=None, help="Inference device")
    p_video.set_defaults(func=cmd_video)

    # Watermark subcommand
    p_wm = subparsers.add_parser("watermark", help="Apply running text and banner watermark")
    p_wm.add_argument("--input", "-i", required=True, help="Input image file or folder")
    p_wm.add_argument("--output", "-o", help="Output directory")
    p_wm.add_argument("--banner", "-b", help="Path to branding banner image")
    p_wm.set_defaults(func=cmd_watermark)

    # Story subcommand
    p_story = subparsers.add_parser("story", help="Generate 1080x1920 social story")
    p_story.add_argument("--top", required=True, help="Top photo path")
    p_story.add_argument("--bottom", required=True, help="Bottom photo path")
    p_story.add_argument("--output", "-o", required=True, help="Output story file path")
    p_story.add_argument("--banner", "-b", help="Path to middle banner runner")
    p_story.set_defaults(func=cmd_story)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
