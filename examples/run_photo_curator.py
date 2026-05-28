"""
Example: End-to-End Photo Curation with MediaFlow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Demonstrates how to run the multi-stage curation pipeline programmatically.
"""

import os
from mediaflow.config import MediaFlowConfig
from mediaflow.curator import QualityGate, SemanticScorer, VisualDeduplicator, TimelineCurator, ContactSheetGenerator
from mediaflow.core import CLIPManager

def main():
    raw_dir = r"E:\02_Work_Projects\HOUSEFIX.LK\03_Social_Media_Projects\Project_01\01_Raw"
    output_dir = r"E:\02_Work_Projects\HOUSEFIX.LK\03_Social_Media_Projects\Project_01\02_Processed_By_MediaFlow"

    if not os.path.exists(raw_dir):
        print(f"Sample directory '{raw_dir}' not found. Please provide a valid raw media folder.")
        return

    config = MediaFlowConfig()

    # Step 1: Quality Gate
    gate = QualityGate(config.quality)
    photos, stats = gate.filter_directory(raw_dir)
    print(f"Passed OpenCV Quality Screening: {len(photos)} / {stats['total_scanned']}")

    # Step 2: Semantic Relevance
    clip_mgr = CLIPManager(config.semantic.model_name)
    scorer = SemanticScorer(clip_mgr, config.semantic)
    semantic_photos, _ = scorer.score_batch(photos)
    print(f"Passed CLIP Relevance Filter: {len(semantic_photos)}")

    # Step 3: Deduplication
    dedup = VisualDeduplicator(clip_mgr, config.dedup)
    unique_photos = dedup.deduplicate(semantic_photos)
    print(f"Surviving Unique Photos: {len(unique_photos)}")

    # Step 4: Timeline Curation to 45 milestone images
    curator = TimelineCurator(target_count=45)
    final_curation = curator.curate(unique_photos, target_count=45)
    print(f"Final Curated Selection: {len(final_curation)} photos")

    # Step 5: Contact Sheet
    os.makedirs(output_dir, exist_ok=True)
    sheet_generator = ContactSheetGenerator()
    sheet_path = os.path.join(output_dir, "00_Curated_Contact_Sheet.jpg")
    sheet_generator.generate(final_curation, sheet_path)
    print(f"Generated Contact Sheet at: {sheet_path}")

if __name__ == "__main__":
    main()
