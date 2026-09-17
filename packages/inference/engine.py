import os
import threading
import time

import numpy as np
import torch
from ultralytics import YOLO


class YOLOv11Engine:
    VARIETY_CLASSES = ['bawor', 'black thorn', 'kanyao', 'monthong', 'musang king', 'not durian']

    def __init__(self, model_path: str = 'models/best.pt', device: str = 'auto'):
        self._lock = threading.Lock()
        self._model = None
        self._model_path = model_path
        self._device = self._resolve_device(device)
        self._is_loaded = False
        
        self.load_model(model_path)

    def _resolve_device(self, requested_device: str) -> str:
        if requested_device == 'auto':
            return 'cuda' if torch.cuda.is_available() else 'cpu'
        return requested_device

    def load_model(self, path: str) -> bool:
        """Dynamically load a new model at runtime."""
        with self._lock:
            try:
                if not os.path.exists(path):
                    print(f"Warning: Model file not found at {path}")
                    self._is_loaded = False
                    return False
                    
                if self._model is not None:
                    del self._model
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        
                self._model = YOLO(path)
                self._model.to(self._device)
                self._model_path = path
                self._is_loaded = True
                print(f"Successfully loaded model from {path} on {self._device}")
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                self._is_loaded = False
                return False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def predict(self, frame: np.ndarray, conf: float = 0.5, iou: float = 0.45, imgsz: int = 640) -> tuple[list[dict], float]:
        with self._lock:
            if not self._is_loaded or self._model is None:
                raise RuntimeError("Model is not loaded")
    
            start_time = time.perf_counter()
            
            results = self._model.predict(
                source=frame,
                conf=conf,
                iou=iou,
                imgsz=imgsz,
                verbose=False,
                device=self._device
            )
            
            end_time = time.perf_counter()
            inference_time_ms = (end_time - start_time) * 1000.0
            
            detections = []
            if len(results) > 0:
                result = results[0]
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        confidence = float(box.conf[0].item())
                        xyxy = box.xyxy[0].tolist()
                        xywh = box.xywh[0].tolist()
                        
                        class_name = result.names.get(cls_id, "Unknown")
                        if class_name == "Unknown" and 0 <= cls_id < len(self.VARIETY_CLASSES):
                            class_name = self.VARIETY_CLASSES[cls_id]
    
                        detections.append({
                            "class_id": cls_id,
                            "class_name": class_name,
                            "confidence": confidence,
                            "bbox": {
                                "x1": xyxy[0],
                                "y1": xyxy[1],
                                "x2": xyxy[2],
                                "y2": xyxy[3],
                                "w": xywh[2],
                                "h": xywh[3]
                            }
                        })
                        
            return detections, inference_time_ms

    def get_model_info(self) -> dict:
        classes = []
        if self._model is not None and hasattr(self._model, 'names'):
            classes = list(self._model.names.values())
        else:
            classes = self.VARIETY_CLASSES

        return {
            "path": self._model_path,
            "device": self._device,
            "classes": classes,
            "is_loaded": self._is_loaded,
            "framework": "ultralytics"
        }
