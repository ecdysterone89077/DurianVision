"""
Screen capture module for DurianVision.
Uses DXcam as primary (high-performance) with MSS as fallback.
"""

import cv2
import numpy as np

try:
    import dxcam
    DXCAM_AVAILABLE = True
except ImportError:
    DXCAM_AVAILABLE = False

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


class ScreenCapture:
    """Screen capture with DXcam (primary) and MSS (fallback)."""
    
    def __init__(self) -> None:
        """Initialize the screen capture instance."""
        self._region: tuple[int, int, int, int] = (0, 0, 800, 600)  # (left, top, right, bottom) for dxcam
        self._mss_region: dict[str, int] = {"top": 0, "left": 0, "width": 800, "height": 600}
        self._camera = None
        self._use_dxcam = False
        self._sct = None  # MSS instance, created in worker thread
        self._initialized = False
    
    def initialize(self) -> str:
        """
        Initialize capture engine. Call this from the worker thread.
        Returns the engine name being used.
        """
        if self._initialized:
            return 'dxcam' if self._use_dxcam else 'mss'
            
        # Try DXcam first
        if DXCAM_AVAILABLE:
            try:
                self._camera = dxcam.create(output_color="BGR")
                self._use_dxcam = True
                self._initialized = True
                print("[ScreenCapture] Menggunakan DXcam (performa tinggi)")
                return 'dxcam'
            except Exception as e:
                print(f"[ScreenCapture] DXcam gagal: {e}, beralih ke MSS")
                self._camera = None
        
        # Fallback to MSS
        if MSS_AVAILABLE:
            try:
                self._sct = mss.mss()
                self._use_dxcam = False
                self._initialized = True
                print("[ScreenCapture] Menggunakan MSS (fallback)")
                return 'mss'
            except Exception as e:
                print(f"[ScreenCapture] MSS gagal: {e}")
        
        self._initialized = False
        print("[ScreenCapture] Tidak ada engine capture yang tersedia")
        return 'none'

    def set_region(self, x: int, y: int, width: int, height: int) -> None:
        """Store the capture region."""
        if width <= 0 or height <= 0:
            return
        self._region = (x, y, x + width, y + height)  # DXcam format: (left, top, right, bottom)
        self._mss_region = {"top": y, "left": x, "width": width, "height": height}

    def capture_frame(self) -> np.ndarray:
        """Capture the defined region and return as numpy array (BGR format)."""
        if not self._initialized:
            self.initialize()
        
        if self._use_dxcam and self._camera is not None:
            return self._capture_dxcam()
        elif self._sct is not None:
            return self._capture_mss()
        else:
            return self._empty_frame()
    
    def _capture_dxcam(self) -> np.ndarray:
        """Capture using DXcam."""
        try:
            frame = self._camera.grab(region=self._region)
            if frame is not None:
                return frame
            return self._empty_frame()
        except Exception:
            return self._empty_frame()
    
    def _capture_mss(self) -> np.ndarray:
        """Capture using MSS."""
        try:
            screenshot = self._sct.grab(self._mss_region)
            frame_bgra = np.array(screenshot)
            return cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)
        except Exception:
            return self._empty_frame()
    
    def _empty_frame(self) -> np.ndarray | None:
        """Return None when capture fails."""
        return None

    def release(self) -> None:
        """Release capture resources."""
        if self._camera is not None:
            try:
                # Phase 2.2: Properly stop and release DXcam to free RAM
                if hasattr(self._camera, 'is_capturing') and self._camera.is_capturing:
                    self._camera.stop()
                if hasattr(self._camera, 'release'):
                    self._camera.release()
                del self._camera
            except Exception as e:
                print(f"[ScreenCapture] Warning - error releasing DXcam: {e}")
            self._camera = None
        if self._sct is not None:
            try:
                self._sct.close()
            except Exception as e:
                print(f"[ScreenCapture] Warning - error releasing MSS: {e}")
            self._sct = None
        self._initialized = False

    @property
    def is_available(self) -> bool:
        """Check if any capture engine is available."""
        return DXCAM_AVAILABLE or MSS_AVAILABLE
    
    @property
    def engine_name(self) -> str:
        """Get the current capture engine name."""
        if self._use_dxcam:
            return 'DXcam'
        elif self._sct is not None:
            return 'MSS'
        return 'Tidak ada'
