"""Reusable UI widgets for DurianVision."""

from .confidence_slider import ConfidenceSlider
from .detection_list import DetectionList
from .fps_slider import FPSSlider
from .log_table import LogTable
from .resource_monitor import ResourceMonitor
from .snapshot_gallery import SnapshotCard, SnapshotGallery

__all__ = [
    'ConfidenceSlider',
    'DetectionList',
    'FPSSlider',
    'LogTable',
    'ResourceMonitor',
    'SnapshotCard',
    'SnapshotGallery',
]
