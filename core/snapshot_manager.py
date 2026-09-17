"""
Snapshot manager for DurianVision.
Handles saving images with bounding boxes.
"""

import os
from datetime import datetime
import threading
from typing import Optional

import cv2
import numpy as np


def hex_to_bgr(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to BGR tuple."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (b, g, r)


# All varieties with correct BGR values from hex
DEFAULT_VARIETY_COLORS_BGR = {
    'Bawor': hex_to_bgr('#22C55E'),       # (94, 197, 34)
    'Black Thorn': hex_to_bgr('#10B981'), # (129, 185, 16)
    'Montong': hex_to_bgr('#3B82F6'),     # (246, 130, 59)
    'Musang King': hex_to_bgr('#EAB308'), # (8, 179, 234)
    'Petruk': hex_to_bgr('#A855F7'),      # (247, 85, 168)
    'Monthong': hex_to_bgr('#EC4899'),    # (153, 72, 236)
    'Sunan': hex_to_bgr('#F97316'),       # (22, 115, 249)
    'Kani': hex_to_bgr('#06B6D4'),        # (212, 182, 6)
    'Matahari': hex_to_bgr('#EF4444'),    # (68, 68, 239)
    'Sitokong': hex_to_bgr('#84CC16'),    # (22, 204, 132)
    'Lainnya': hex_to_bgr('#94A3B8'),     # (184, 163, 148)
}


from PyQt6.QtCore import QObject, QThread, pyqtSignal

class SnapshotWorker(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, frame: np.ndarray, detections: list[dict], 
                 colors_bgr: dict, default_color: tuple, save_dir: str, 
                 metadata: dict | None, line_thickness: int, font_scale: float, max_snapshots: int):
        super().__init__()
        self.frame = frame
        self.detections = detections
        self.colors_bgr = colors_bgr
        self.default_color = default_color
        self.save_dir = save_dir
        self.metadata = metadata
        self.line_thickness = line_thickness
        self.font_scale = font_scale
        self.max_snapshots = max_snapshots
        
    def run(self):
        img_copy = self.frame
        img_h, img_w = img_copy.shape[:2]
        
        for det in self.detections:
            x1 = int(max(0, det.get('x1', 0)))
            y1 = int(max(0, det.get('y1', 0)))
            x2 = int(min(img_w, det.get('x2', 0)))
            y2 = int(min(img_h, det.get('y2', 0)))
            class_name = det.get('class_name', 'Lainnya')
            conf = det.get('confidence', 0.0)
            
            color = self.colors_bgr.get(class_name, self.default_color)
            
            # Draw bounding box
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, self.line_thickness)
            
            # Draw label
            label = f"{class_name} {conf:.2f}"
            (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, 1)
            
            # Position label: above the box if space, below otherwise
            label_y_top = y1 - th - baseline - 4
            if label_y_top < 0:
                label_y_top = y2 + 2  # Move below box
            
            cv2.rectangle(img_copy, (x1, label_y_top), (x1 + tw + 4, label_y_top + th + baseline + 4), color, -1)
            cv2.putText(img_copy, label, (x1 + 2, label_y_top + th + 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, (255, 255, 255), 1, cv2.LINE_AA)
            
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        suffix = ''
        if self.metadata and self.metadata.get('device_type'):
            suffix = f"_{self.metadata['device_type']}"
        
        filename = f"snapshot_{timestamp}{suffix}.jpg"
        filepath = os.path.join(self.save_dir, filename)
        
        try:
            cv2.imwrite(filepath, img_copy)
        except Exception as e:
            print(f"[SnapshotManager] Gagal save snapshot: {e}")
            self.finished.emit("")
            return
            
        import glob
        files = sorted(glob.glob(os.path.join(self.save_dir, '*.jpg')), key=os.path.getmtime)
        while len(files) > self.max_snapshots:
            try:
                os.remove(files.pop(0))
            except OSError as e:
                print(f"[SnapshotManager] Warning - gagal menghapus {e}")
                
        self.finished.emit(filepath)

class SnapshotManager(QObject):
    """Manages saving detection snapshots with bounding boxes asymmetrically."""
    
    snapshot_saved = pyqtSignal(str, list)  # Emit (filepath, detections) when done
    MAX_SNAPSHOTS = 1000  # Maximum snapshots to keep
    
    def __init__(self, save_dir: str = 'snapshots', variety_colors: Optional[dict] = None) -> None:
        super().__init__()
        self.save_dir = save_dir
        self.variety_colors = variety_colors or {}
        
        try:
            os.makedirs(self.save_dir, exist_ok=True)
        except PermissionError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Error Akses", 
                f"Tidak memiliki izin untuk membuat folder di:\n{self.save_dir}\n\n"
                "Harap jalankan aplikasi sebagai Administrator atau ubah lokasi penyimpanan.")
            
            # Fallback ke folder Documents yang aman
            self.save_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'DurianVision_Snapshots')
            os.makedirs(self.save_dir, exist_ok=True)
            
        self._lock = threading.Lock()
        
        if self.variety_colors:
            self.colors_bgr = {name: hex_to_bgr(hex_val) for name, hex_val in self.variety_colors.items()}
        else:
            self.colors_bgr = DEFAULT_VARIETY_COLORS_BGR.copy()
        
        self._default_color = hex_to_bgr('#94A3B8')
        
        # Keep references to prevent GC
        self._workers = []

    def save_snapshot_async(self, frame: np.ndarray, detections: list[dict], 
                      metadata: dict | None = None,
                      line_thickness: int = 2, font_scale: float = 0.5) -> None:
        """
        Draw bounding boxes and save the frame in a background QThread.
        """
        worker = SnapshotWorker(frame.copy(), detections.copy(), self.colors_bgr, 
                                self._default_color, self.save_dir, metadata, 
                                line_thickness, font_scale, self.MAX_SNAPSHOTS)
        
        # Store detections in the worker object so we can pass it back
        worker.original_detections = detections.copy()
        
        def on_finished(filepath):
            if filepath:
                self.snapshot_saved.emit(filepath, worker.original_detections)
            self._workers.remove(worker)
            
        worker.finished.connect(on_finished)
        self._workers.append(worker)
        worker.start()

    def save_snapshot(self, frame: np.ndarray, detections: list[dict], 
                      metadata: dict | None = None,
                      line_thickness: int = 2, font_scale: float = 0.5) -> str:
        """
        Draw bounding boxes and save the frame synchronously. Returns filepath or empty string on error.
        """
        img_copy = frame.copy()
        img_h, img_w = img_copy.shape[:2]
        
        for det in detections:
            x1 = int(max(0, det.get('x1', 0)))
            y1 = int(max(0, det.get('y1', 0)))
            x2 = int(min(img_w, det.get('x2', 0)))
            y2 = int(min(img_h, det.get('y2', 0)))
            class_name = det.get('class_name', 'Lainnya')
            conf = det.get('confidence', 0.0)
            
            color = self.colors_bgr.get(class_name, self._default_color)
            
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, line_thickness)
            
            label = f"{class_name} {conf:.2f}"
            (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
            
            label_y_top = y1 - th - baseline - 4
            if label_y_top < 0:
                label_y_top = y2 + 2
            
            cv2.rectangle(img_copy, (x1, label_y_top), (x1 + tw + 4, label_y_top + th + baseline + 4), color, -1)
            cv2.putText(img_copy, label, (x1 + 2, label_y_top + th + 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 1, cv2.LINE_AA)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        suffix = ''
        if metadata and metadata.get('device_type'):
            suffix = f"_{metadata['device_type']}"
        
        filename = f"snapshot_{timestamp}{suffix}.jpg"
        filepath = os.path.join(self.save_dir, filename)
        
        try:
            cv2.imwrite(filepath, img_copy)
        except Exception as e:
            print(f"[SnapshotManager] Gagal save snapshot: {e}")
            return ""
            
        import glob
        files = sorted(glob.glob(os.path.join(self.save_dir, '*.jpg')), key=os.path.getmtime)
        while len(files) > self.MAX_SNAPSHOTS:
            try:
                os.remove(files.pop(0))
            except OSError as e:
                print(f"[SnapshotManager] Warning - gagal menghapus {e}")
                
        return filepath

