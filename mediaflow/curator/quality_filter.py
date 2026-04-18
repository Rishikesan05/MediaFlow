"""
OpenCV Quality Gate & Metadata Scanner
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Performs high-throughput initial screening of raw media assets using OpenCV:
- File integrity and minimum dimension/size screening.
- Grayscale mean luminance check to reject dark / underexposed captures.
- Laplacian operator variance calculation for edge blur detection.
- Timestamp parsing via regex patterns and fallback to filesystem metadata.
"""

import os
import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

try:
    import cv2
except ImportError:
    cv2 = None

from mediaflow.config import QualityGateConfig

DATE_PATTERNS = [
    re.compile(r'IMG-(\d{8})-'),
    re.compile(r'(\d{4})(\d{2})(\d{2})_'),
    re.compile(r'(\d{4})-(\d{2})-(\d{2})'),
]

@dataclass
class PhotoRecord:
    """Metadata container for an ingested photo undergoing pipeline stages."""
    name: str
    path: str
    timestamp: datetime
    file_size_kb: float
    brightness: float = 0.0
    blur_score: float = 0.0
    quality_score: float = 1.0
    relevance: float = 0.0
    max_pos: float = 0.0
    max_neg: float = 0.0
    cluster_id: Optional[int] = None
    is_curated: bool = False
    attributes: Dict[str, Any] = field(default_factory=dict)

    def get_curator_score(self) -> float:
        """
        Computes composite ranking score prioritizing semantic relevance
        while penalizing marginal optical quality.
        """
        return self.relevance * (0.3 + 0.7 * self.quality_score)


class QualityGate:
    """
    OpenCV-powered quality screening filter.
    Rejects substandard raw captures before passing to GPU-intensive models.
    """

    def __init__(self, config: Optional[QualityGateConfig] = None):
        self.config = config or QualityGateConfig()

    def parse_timestamp(self, file_path: str) -> datetime:
        """Extracts creation date from filename regex or file modification time."""
        filename = os.path.basename(file_path)
        for pattern in DATE_PATTERNS:
            match = pattern.search(filename)
            if match:
                try:
                    if len(match.groups()) == 1:
                        return datetime.strptime(match.group(1), "%Y%m%d")
                    elif len(match.groups()) == 3:
                        y, m, d = match.groups()
                        return datetime(int(y), int(m), int(d))
                except ValueError:
                    pass
        return datetime.fromtimestamp(os.path.getmtime(file_path))

    def evaluate_image(self, file_path: str) -> Tuple[bool, Optional[PhotoRecord], str]:
        """
        Evaluates a single image file for size, brightness, blur, and corruption.
        Returns: (passed: bool, record: Optional[PhotoRecord], reason: str)
        """
        if cv2 is None:
            raise ImportError(
                "OpenCV (cv2) is required for QualityGate. Install with: pip install opencv-python"
            )

        if not os.path.exists(file_path):
            return False, None, "File does not exist"

        file_size_kb = os.path.getsize(file_path) / 1024.0
        if file_size_kb < self.config.min_file_size_kb:
            return False, None, f"File too small ({file_size_kb:.1f} KB < {self.config.min_file_size_kb} KB)"

        # Read image with OpenCV
        image = cv2.imread(file_path)
        if image is None:
            return False, None, "Corrupted image file / decode failure"

        # Brightness assessment
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = float(gray.mean())
        if brightness < self.config.min_brightness:
            return False, None, f"Image underexposed / dark ({brightness:.1f} < {self.config.min_brightness})"

        # Blur assessment using Laplacian variance
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if blur_score < self.config.min_blur_score:
            return False, None, f"Image out-of-focus / blurry ({blur_score:.1f} < {self.config.min_blur_score})"

        # Normalized quality score [0.0, 1.0]
        norm_blur = min(blur_score / self.config.max_blur_normalize, 1.0)
        norm_bright = min(brightness / self.config.max_brightness_normalize, 1.0)
        quality_score = norm_blur * norm_bright

        record = PhotoRecord(
            name=os.path.basename(file_path),
            path=os.path.abspath(file_path),
            timestamp=self.parse_timestamp(file_path),
            file_size_kb=file_size_kb,
            brightness=brightness,
            blur_score=blur_score,
            quality_score=quality_score
        )
        return True, record, "PASSED"

    def filter_directory(self, folder_path: str) -> Tuple[List[PhotoRecord], Dict[str, int]]:
        """
        Scans a directory of raw images, applying the OpenCV quality filter.
        Returns passed PhotoRecords and diagnostic rejection metrics.
        """
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Directory not found: {folder_path}")

        files = [
            os.path.join(folder_path, f) for f in os.listdir(folder_path)
            if os.path.splitext(f)[1].lower() in self.config.supported_image_extensions
        ]

        passed_records: List[PhotoRecord] = []
        stats = {
            "total_scanned": len(files),
            "passed": 0,
            "rejected_small": 0,
            "rejected_dark": 0,
            "rejected_blur": 0,
            "rejected_corrupt": 0,
        }

        for path in files:
            passed, record, reason = self.evaluate_image(path)
            if passed and record:
                passed_records.append(record)
                stats["passed"] += 1
            else:
                if "small" in reason:
                    stats["rejected_small"] += 1
                elif "dark" in reason:
                    stats["rejected_dark"] += 1
                elif "blurry" in reason:
                    stats["rejected_blur"] += 1
                else:
                    stats["rejected_corrupt"] += 1

        return passed_records, stats
