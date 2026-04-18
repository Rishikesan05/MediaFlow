"""
Unit Tests for OpenCV Quality Gate
"""

import os
import tempfile
from datetime import datetime

from mediaflow.curator.quality_filter import QualityGate, PhotoRecord
from mediaflow.config import QualityGateConfig

def test_date_parser():
    gate = QualityGate()
    ts1 = gate.parse_timestamp("IMG-20260415-WA0001.jpg")
    assert ts1 == datetime(2026, 4, 15)

    ts2 = gate.parse_timestamp("20260520_143022.jpg")
    assert ts2 == datetime(2026, 5, 20)

def test_quality_gate_filtering():
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("[SKIP] cv2 / numpy not installed in current environment; skipping image raster tests.")
        return

    gate = QualityGate(QualityGateConfig(min_file_size_kb=1.0, min_brightness=20.0, min_blur_score=10.0))
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a sharp, well-lit test image
        sharp_img = np.zeros((400, 400, 3), dtype=np.uint8)
        cv2.rectangle(sharp_img, (50, 50), (350, 350), (220, 220, 220), -1)
        cv2.line(sharp_img, (50, 50), (350, 350), (0, 0, 0), 10)
        sharp_path = os.path.join(tmp_dir, "IMG-20260401-sharp.jpg")
        cv2.imwrite(sharp_path, sharp_img)

        # Create a dark image
        dark_img = np.full((400, 400, 3), 10, dtype=np.uint8)
        dark_path = os.path.join(tmp_dir, "IMG-20260402-dark.jpg")
        cv2.imwrite(dark_path, dark_img)

        # Create a completely blurry/flat image
        blur_img = np.full((400, 400, 3), 120, dtype=np.uint8)
        blur_path = os.path.join(tmp_dir, "IMG-20260403-blur.jpg")
        cv2.imwrite(blur_path, blur_img)

        # Test evaluation
        passed_sharp, rec_sharp, _ = gate.evaluate_image(sharp_path)
        assert passed_sharp is True
        assert rec_sharp is not None
        assert rec_sharp.blur_score > 10.0
        assert rec_sharp.brightness > 20.0

        passed_dark, _, reason_dark = gate.evaluate_image(dark_path)
        assert passed_dark is False
        assert "dark" in reason_dark

        passed_blur, _, reason_blur = gate.evaluate_image(blur_path)
        assert passed_blur is False
        assert "blurry" in reason_blur

if __name__ == "__main__":
    test_date_parser()
    test_quality_gate_filtering()
    print("Quality Gate tests passed successfully!")
