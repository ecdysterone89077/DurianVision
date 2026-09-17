"""
Detection worker thread for DurianVision.
Runs screen capture and YOLO inference in a background thread.
"""

import threading
import time

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from .screen_capture import ScreenCapture
from .yolo_engine import YOLOEngine


class DetectionWorker(QThread):
    """Background worker that captures screen and runs YOLO inference."""
    
    # Signals
    frame_processed = pyqtSignal(list, float, np.ndarray)  # detections, fps, frame
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, screen_capture: ScreenCapture, yolo_engine: YOLOEngine, config: dict) -> None:
        """Initialize the detection worker."""
        super().__init__()
        self.screen_capture = screen_capture
        self.yolo_engine = yolo_engine
        
        # Configuration - read from proper nested structure
        detection_config = config.get('detection') or {}
        self._fps_limit = max(1, detection_config.get('fps_limit', 10))
        self._conf_threshold = detection_config.get('confidence_threshold', 0.5)
        self._imgsz = detection_config.get('inference_size', 640)
        
        self._is_running = False
        self._stop_event = threading.Event()
        
        # FPS smoothing (exponential moving average)
        self._fps_ema = 0.0
        self._fps_alpha = 0.3  # smoothing factor

    def set_fps_limit(self, fps: int) -> None:
        """Set the maximum frames per second."""
        self._fps_limit = max(1, min(fps, 120))

    def set_confidence(self, conf: float) -> None:
        """Set the confidence threshold for YOLO detections."""
        self._conf_threshold = max(0.0, min(1.0, conf))

    def set_inference_size(self, size: int) -> None:
        """Set the inference image size."""
        self._imgsz = size

    def stop(self) -> None:
        """Stop the worker thread (non-blocking interrupt)."""
        self._is_running = False
        self._stop_event.set()
        self.wait(3000)  # Wait max 3 seconds

    def run(self) -> None:
        """Main loop that captures frames, runs YOLO, and emits results."""
        self._is_running = True
        self._stop_event.clear()
        self._fps_ema = 0.0
        
        # Initialize screen capture in worker thread for thread safety
        engine_name = self.screen_capture.initialize()
        if engine_name == 'none':
            self.error_occurred.emit("Tidak ada engine tangkapan layar yang tersedia")
            return
        
        prev_time = time.perf_counter()
        
        try:
            while self._is_running:
                start_time = time.perf_counter()
                
                # 1. Capture frame
                frame = self.screen_capture.capture_frame()
                
                # 2. Validate frame
                if frame is None or frame.size == 0:
                    self._interruptible_sleep(0.1)
                    continue
                
                # 3. Run inference
                detections = self.yolo_engine.predict(
                    frame, 
                    self._conf_threshold, 
                    self._imgsz
                )
                
                # 4. Calculate smoothed FPS
                current_time = time.perf_counter()
                elapsed = current_time - prev_time
                instant_fps = 1.0 / elapsed if elapsed > 0 else 0.0
                self._fps_ema = (self._fps_alpha * instant_fps + 
                               (1 - self._fps_alpha) * self._fps_ema)
                prev_time = current_time
                
                # 5. Emit results with UI Throttling (max 30 FPS for GUI)
                # Emit max every 0.033 seconds to prevent Event Loop overload (Phase 1.2)
                if current_time - getattr(self, '_last_emit_time', 0) > 0.033:
                    self.frame_processed.emit(detections, round(self._fps_ema, 1), frame)
                    self._last_emit_time = current_time
                
                # 6. Respect FPS limit with interruptible sleep
                process_time = time.perf_counter() - start_time
                target_time = 1.0 / self._fps_limit
                if process_time < target_time:
                    self._interruptible_sleep(target_time - process_time)
        finally:
            # Phase 2.2: Release screen capture buffer to prevent RAM leaks
            if self.screen_capture:
                self.screen_capture.release()
    
    def _interruptible_sleep(self, seconds: float) -> None:
        """Sleep that can be interrupted by stop_event."""
        self._stop_event.wait(timeout=seconds)
