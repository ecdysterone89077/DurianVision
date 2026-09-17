"""
Variety Classifier for DurianVision — Level 3 Two-Stage Pipeline.

Stage 2 classifier: takes a cropped durian image from YOLO detection
and classifies it into a specific variety using EfficientNet-V2-S.

Falls back gracefully to YOLO-only if classifier model is not available.
"""

import os
import time

import numpy as np

try:
    import torch
    from torch import nn
    from torchvision import models, transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

import cv2


class VarietyClassifier:
    """EfficientNet-based durian variety classifier (Stage 2)."""

    # Default class names — must match training order
    DEFAULT_CLASSES = [
        'Bawor', 'Black Thorn', 'Kani', 'Monthong', 'Musang King', 'Lainnya'
    ]

    def __init__(self, model_path: str = 'classifier.pt', device: str = 'auto'):
        """
        Initialize the variety classifier.
        
        Args:
            model_path: Path to the classifier .pt file
            device: 'auto', 'cuda', or 'cpu'
        """
        self.model_path = model_path
        self._model = None
        self._is_loaded = False
        self._load_error = ''
        self._last_inference_ms = 0.0
        self.class_names = self.DEFAULT_CLASSES.copy()
        self.num_classes = len(self.class_names)

        # Resolve device
        if device == 'auto':
            self.device = 'cuda' if (TORCH_AVAILABLE and torch.cuda.is_available()) else 'cpu'
        else:
            self.device = device

        # Image preprocessing — matches EfficientNet training
        if TORCH_AVAILABLE:
            self._transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                ),
            ])

        # Try to load model
        self.load_model(model_path)

    def load_model(self, path: str) -> bool:
        """Load the classifier model."""
        self.model_path = path
        self._load_error = ''

        if not TORCH_AVAILABLE:
            self._load_error = 'PyTorch tidak terinstal'
            return False

        if not os.path.exists(path):
            self._load_error = f'File classifier tidak ditemukan: {path}'
            print(f"[Classifier] {self._load_error} — menggunakan YOLO-only mode")
            return False

        try:
            checkpoint = torch.load(path, map_location=self.device, weights_only=False)

            # Extract class names from checkpoint if available
            if isinstance(checkpoint, dict):
                if 'class_names' in checkpoint:
                    self.class_names = checkpoint['class_names']
                    self.num_classes = len(self.class_names)

                state_dict = checkpoint.get('model_state_dict', checkpoint.get('state_dict', checkpoint))
                arch = checkpoint.get('arch', 'efficientnet_v2_s')
            else:
                # Assume it's a raw state_dict
                state_dict = checkpoint
                arch = 'efficientnet_v2_s'

            # Build model architecture
            self._model = self._build_model(arch, self.num_classes)
            self._model.load_state_dict(state_dict)
            self._model.to(self.device)
            self._model.eval()
            self._is_loaded = True

            print(f"[Classifier] Model dimuat: {path} ({arch}, {self.num_classes} kelas, {self.device})")
            return True

        except Exception as e:
            self._load_error = f'Gagal memuat classifier: {e}'
            print(f"[Classifier] {self._load_error}")
            return False

    def _build_model(self, arch: str, num_classes: int) -> 'nn.Module':
        """Build the model architecture."""
        if arch == 'efficientnet_v2_s':
            model = models.efficientnet_v2_s(weights=None)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        elif arch == 'resnet50':
            model = models.resnet50(weights=None)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        elif arch == 'mobilenet_v3_large':
            model = models.mobilenet_v3_large(weights=None)
            model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
        else:
            # Default to EfficientNet
            model = models.efficientnet_v2_s(weights=None)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

        return model

    def classify(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        """
        Classify a cropped durian image.
        
        Args:
            crop_bgr: BGR numpy array of the cropped durian
            
        Returns:
            (variety_name, confidence) tuple
        """
        if not self._is_loaded or self._model is None:
            return ('Lainnya', 0.0)

        if crop_bgr is None or crop_bgr.size == 0:
            return ('Lainnya', 0.0)

        try:
            start = time.perf_counter()

            # BGR -> RGB
            crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)

            # Preprocess
            tensor = self._transform(crop_rgb).unsqueeze(0).to(self.device)

            # Inference
            with torch.no_grad():
                outputs = self._model(tensor)
                probs = torch.softmax(outputs, dim=1)
                conf, pred_idx = torch.max(probs, dim=1)

            self._last_inference_ms = (time.perf_counter() - start) * 1000

            variety = self.class_names[pred_idx.item()]
            confidence = conf.item()

            return (variety, confidence)

        except Exception as e:
            print(f"[Classifier] Error: {e}")
            return ('Lainnya', 0.0)

    def classify_batch(self, crops_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        """
        Classify multiple crops in a single batch for efficiency.
        
        Args:
            crops_bgr: List of BGR numpy arrays
            
        Returns:
            List of (variety_name, confidence) tuples
        """
        if not self._is_loaded or self._model is None:
            return [('Lainnya', 0.0)] * len(crops_bgr)

        if not crops_bgr:
            return []

        try:
            start = time.perf_counter()

            # Preprocess all crops
            tensors = []
            valid_indices = []
            for i, crop in enumerate(crops_bgr):
                if crop is not None and crop.size > 0:
                    rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                    tensors.append(self._transform(rgb))
                    valid_indices.append(i)

            if not tensors:
                return [('Lainnya', 0.0)] * len(crops_bgr)

            # Batch inference
            batch = torch.stack(tensors).to(self.device)

            with torch.no_grad():
                outputs = self._model(batch)
                probs = torch.softmax(outputs, dim=1)
                confs, pred_indices = torch.max(probs, dim=1)

            self._last_inference_ms = (time.perf_counter() - start) * 1000

            # Build results
            results = [('Lainnya', 0.0)] * len(crops_bgr)
            for j, orig_idx in enumerate(valid_indices):
                variety = self.class_names[pred_indices[j].item()]
                confidence = confs[j].item()
                results[orig_idx] = (variety, confidence)

            return results

        except Exception as e:
            print(f"[Classifier] Batch error: {e}")
            return [('Lainnya', 0.0)] * len(crops_bgr)

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def load_error(self) -> str:
        return self._load_error

    @property
    def last_inference_ms(self) -> float:
        return self._last_inference_ms
