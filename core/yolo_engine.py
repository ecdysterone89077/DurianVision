"""
YOLO Engine module for DurianVision.
Handles model loading and inference with graceful error handling.
Supports two-stage pipeline: YOLO detect → Classifier classify.
"""

import threading
import time

import numpy as np

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from core.variety_classifier import VarietyClassifier


class YOLOEngine:
    """YOLO inference engine with optional two-stage classification."""
    
    # Mapping from YOLO model class names to UI display names
    MODEL_CLASS_MAP = {
        'bawor': 'Bawor',
        'd24': 'D24',
        'duri hitam': 'Duri Hitam',
        'lokal': 'Lokal',
        'merah': 'Merah',
        'montong': 'Montong',
        'musang king': 'Musang King',
        'pelangi': 'Pelangi',
        'sane': 'Sane',
        'sunan': 'Sunan',
        'super tembaga': 'Super Tembaga',
    }
    
    def __init__(self, model_path: str = 'best.pt', device: str = 'cuda',
                 classifier_path: str = 'classifier.pt',
                 two_stage_enabled: bool = True,
                 classifier_min_confidence: float = 0.4) -> None:
        """
        Initialize the YOLO engine with optional two-stage classifier.
        
        Args:
            model_path: Path to YOLO model
            device: Compute device ('cuda' or 'cpu')
            classifier_path: Path to classifier model (.pt)
            two_stage_enabled: Enable two-stage pipeline
            classifier_min_confidence: Minimum classifier confidence to override YOLO
        """
        self.model_path = model_path
        self._lock = threading.RLock()
        self.device = self._resolve_device(device)
        self._model = None
        self._is_loaded = False
        self._load_error: str = ''
        self._last_inference_ms: float = 0.0
        
        # Two-stage pipeline
        self.two_stage_enabled = two_stage_enabled
        self.classifier_min_confidence = classifier_min_confidence
        self._classifier: VarietyClassifier | None = None
        self._classifier_path = classifier_path
        
        self.default_varieties = [
            'Bawor', 'D24', 'Duri Hitam', 'Lokal', 'Merah', 'Montong',
            'Musang King', 'Pelangi', 'Sane', 'Sunan', 'Super Tembaga',
        ]
        
        self.load_model(self.model_path)
        
        # Initialize classifier (graceful — won't fail if not available)
        if self.two_stage_enabled:
            self._init_classifier()

    def _resolve_device(self, requested: str) -> str:
        """Resolve the best available device (CUDA -> CPU fallback)."""
        req = (requested or '').lower()
        if req in ('cuda', 'gpu') or req.startswith('cuda:'):
            if TORCH_AVAILABLE and torch.cuda.is_available():
                return req if req.startswith('cuda') else 'cuda'
            print("[YOLOEngine] CUDA tidak tersedia, menggunakan CPU")
            return 'cpu'
        if req in ('directml', 'dml'):
            print("[YOLOEngine] DirectML tidak didukung ultralytics, menggunakan CPU")
            return 'cpu'
        return req or 'cpu'

    def _init_classifier(self) -> None:
        """Initialize the Stage 2 variety classifier (graceful)."""
        try:
            self._classifier = VarietyClassifier(
                model_path=self._classifier_path,
                device=self.device
            )
            if self._classifier.is_loaded:
                print("[YOLOEngine] Two-stage mode AKTIF — classifier loaded")
            else:
                print(f"[YOLOEngine] Two-stage mode NONAKTIF — {self._classifier.load_error}")
                self._classifier = None
        except Exception as e:
            print(f"[YOLOEngine] Classifier init gagal: {e} — menggunakan YOLO-only")
            self._classifier = None

    @staticmethod
    def _crop_detection(frame: np.ndarray, det: dict, padding: float = 0.1) -> np.ndarray | None:
        """
        Crop a detection region from frame with padding for context.
        
        Args:
            frame: Full BGR frame
            det: Detection dict with x1,y1,x2,y2
            padding: Fractional padding around the bbox (0.1 = 10%)
            
        Returns:
            Cropped BGR image or None
        """
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = det['x1'], det['y1'], det['x2'], det['y2']
        
        # Add padding
        bw = x2 - x1
        bh = y2 - y1
        pad_x = int(bw * padding)
        pad_y = int(bh * padding)
        
        cx1 = max(0, x1 - pad_x)
        cy1 = max(0, y1 - pad_y)
        cx2 = min(w, x2 + pad_x)
        cy2 = min(h, y2 + pad_y)
        
        crop = frame[cy1:cy2, cx1:cx2]
        if crop.size == 0:
            return None
        return crop

    def load_model(self, path: str) -> bool:
        """Load the YOLO model from the given path (thread-safe)."""
        with self._lock:
            return self._load_model_locked(path)

    def _load_model_locked(self, path: str) -> bool:
        """Load the YOLO model from the given path."""
        self.model_path = path
        self._load_error = ''
        
        if not ULTRALYTICS_AVAILABLE:
            self._is_loaded = False
            self._load_error = 'Library ultralytics tidak terinstal'
            print(f"[YOLOEngine] {self._load_error}")
            return False
            
        try:
            import os
            if not os.path.exists(path):
                self._is_loaded = False
                self._load_error = f'File model tidak ditemukan: {path}'
                print(f"[YOLOEngine] {self._load_error}")
                return False
                
            self._model = YOLO(path)
            self._model.to(self.device)
            self._is_loaded = True
            print(f"[YOLOEngine] Model dimuat: {path} pada {self.device}")
            return True
        except Exception as e:
            self._is_loaded = False
            self._load_error = f'Gagal memuat model: {e}'
            print(f"[YOLOEngine] {self._load_error}")
            return False

    def predict(self, frame: np.ndarray, conf_threshold: float = 0.5, imgsz: int = 640) -> list[dict]:
        """Thread-safe wrapper: serializes inference against model swaps."""
        with self._lock:
            return self._predict_locked(frame, conf_threshold, imgsz)

    def _predict_locked(self, frame: np.ndarray, conf_threshold: float = 0.5, imgsz: int = 640) -> list[dict]:
        """
        Run inference on a frame and return detections.
        
        Two-stage pipeline (if classifier is available):
          1. YOLO detects objects (durian/not-durian)
          2. For each durian detection, crop and classify variety
          3. Override YOLO class with classifier result if confident enough
        """
        if not self.is_loaded or self._model is None:
            return []
        
        if frame is None or frame.size == 0:
            return []
            
        try:
            start_time = time.perf_counter()
            
            # Stage 1: YOLO Detection
            results = self._model.predict(
                frame, 
                conf=conf_threshold, 
                imgsz=imgsz, 
                verbose=False
            )
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                for i in range(len(boxes)):
                    import math
                    xyxy = boxes.xyxy[i].cpu().numpy()
                    
                    # Phase 4.1: Protection against NaN/Inf tensor anomalies
                    if any(math.isnan(x) or math.isinf(x) for x in xyxy):
                        continue
                        
                    conf = float(boxes.conf[i].cpu().numpy())
                    cls_id = int(boxes.cls[i].cpu().numpy())
                    cls_name = result.names.get(cls_id, 'Lainnya')
                    
                    # Map model class name to UI display name
                    display_name = self.MODEL_CLASS_MAP.get(cls_name, cls_name)
                    
                    detections.append({
                        'x1': int(xyxy[0]),
                        'y1': int(xyxy[1]),
                        'x2': int(xyxy[2]),
                        'y2': int(xyxy[3]),
                        'confidence': conf,
                        'class_id': cls_id,
                        'class_name': display_name
                    })
            
            # Stage 2: Classifier Refinement (if available)
            if self._classifier is not None and self._classifier.is_loaded and detections:
                self._refine_with_classifier(frame, detections)
            
            self._last_inference_ms = (time.perf_counter() - start_time) * 1000
            return detections
            
        except Exception as e:
            print(f"[YOLOEngine] Error inferensi: {e}")
            return []

    def _refine_with_classifier(self, frame: np.ndarray, detections: list[dict]) -> None:
        """
        Stage 2: Refine variety classification using the dedicated classifier.
        Modifies detections in-place.
        
        Only processes detections that are NOT 'Lainnya' (i.e., actual durian detections).
        Only overrides YOLO class when classifier confidence > threshold.
        """
        # Collect durian crops (skip 'Lainnya')
        durian_indices = []
        crops = []
        
        for i, det in enumerate(detections):
            if det['class_name'] != 'Lainnya':
                crop = self._crop_detection(frame, det, padding=0.1)
                if crop is not None:
                    durian_indices.append(i)
                    crops.append(crop)
        
        if not crops:
            return
        
        # Batch classify all durian crops
        results = self._classifier.classify_batch(crops)
        
        # Override YOLO class with classifier result if confident enough
        for j, det_idx in enumerate(durian_indices):
            cls_name, cls_conf = results[j]
            
            if cls_conf >= self.classifier_min_confidence and cls_name != 'Lainnya':
                detections[det_idx]['class_name'] = cls_name
                # Use the higher confidence between YOLO and classifier
                detections[det_idx]['confidence'] = max(
                    detections[det_idx]['confidence'],
                    cls_conf
                )

    def change_device(self, device: str) -> None:
        """Move model to a different compute device (thread-safe)."""
        with self._lock:
            self._change_device_locked(device)

    def _change_device_locked(self, device: str) -> None:
        """Move model to a different compute device."""
        new_device = self._resolve_device(device)
        if new_device == self.device and self._is_loaded:
            return
        self.device = new_device
        if self._model is not None:
            try:
                self._model.to(self.device)
            except Exception as e:
                print(f"Failed to move model to {self.device}: {e}")
                self.device = 'cpu'
                self.load_model(self.model_path)
        # Also move classifier
        if self._classifier is not None and self._classifier.is_loaded:
            try:
                self._classifier._model.to(self.device)
            except Exception:
                pass

    @property
    def is_loaded(self) -> bool:
        """Check if the YOLO model is successfully loaded."""
        return self._is_loaded

    @property
    def load_error(self) -> str:
        """Get the last load error message."""
        return self._load_error

    @property
    def last_inference_ms(self) -> float:
        """Get inference time of last prediction in milliseconds."""
        return self._last_inference_ms

    @property
    def model_names(self) -> list[str]:
        """Get class names from the model or default list."""
        if self.is_loaded and self._model is not None and hasattr(self._model, 'names'):
            return list(self._model.names.values())
        return self.default_varieties

    @property
    def is_two_stage(self) -> bool:
        """Check if the two-stage pipeline is active."""
        return (self._classifier is not None and self._classifier.is_loaded)

    @property
    def pipeline_status(self) -> str:
        """Get human-readable pipeline status."""
        if self.is_two_stage:
            return f"Two-Stage (YOLO + Classifier, {self._classifier.num_classes} kelas)"
        return "YOLO-Only"
