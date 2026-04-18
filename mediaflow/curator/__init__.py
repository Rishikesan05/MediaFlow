"""
MediaFlow Curator Subpackage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Modules for photo ingestion, OpenCV quality filtering, CLIP semantic relevance
ranking, visual deduplication, timeline curation, and contact sheet generation.
"""

from .quality_filter import QualityGate, PhotoRecord

__all__ = ["QualityGate", "PhotoRecord"]
