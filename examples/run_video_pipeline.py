"""
Example: Video Scene Splitting & Importance Ranking with MediaFlow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Demonstrates how to detect scenes, mute audio, extract keyframes, and score priorities.
"""

import os
from mediaflow.config import MediaFlowConfig
from mediaflow.core import CLIPManager
from mediaflow.video import SceneSplitter, SceneRanker

def main():
    video_path = r"E:\02_Work_Projects\HOUSEFIX.LK\03_Social_Media_Projects\Project_01\01_Raw\site_walkthrough.mp4"
    output_dir = r"E:\02_Work_Projects\HOUSEFIX.LK\03_Social_Media_Projects\Project_01\02_Processed_By_MediaFlow\scenes"

    if not os.path.exists(video_path):
        print(f"Sample video '{video_path}' not found. Please provide a valid video file.")
        return

    # Step 1: Detect scene boundaries and split clips
    splitter = SceneSplitter()
    scenes = splitter.process_video(video_path, output_dir, mute_audio=True)
    print(f"Extracted {len(scenes)} distinct scene clips.")

    # Step 2: Rank scene importance via CLIP
    config = MediaFlowConfig()
    clip_mgr = CLIPManager(config.semantic.model_name)
    ranker = SceneRanker(clip_mgr, config.video)
    ranked_scenes = ranker.rank_scenes(scenes)

    for s in ranked_scenes:
        print(f"Scene {s.scene_id:02d}: {s.importance_label} priority (Score: {s.importance_score:.2f}) -> {s.clip_path}")

if __name__ == "__main__":
    main()
