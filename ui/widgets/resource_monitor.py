"""
Resource monitor widget for DurianVision.
Displays CPU, GPU, RAM usage bars.
"""
from PyQt6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget


class ResourceMonitor(QWidget):
    """Displays real-time resource usage (CPU, GPU, RAM)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        self.lbl_fps = QLabel("FPS Aktual: 0")
        self.lbl_inference = QLabel("Waktu Inferensi: 0 ms")
        
        layout.addWidget(self.lbl_fps)
        layout.addWidget(self.lbl_inference)
        
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setFormat("CPU: %p%")
        self.gpu_bar = QProgressBar()
        self.gpu_bar.setFormat("GPU: %p%")
        self.ram_bar = QProgressBar()
        self.ram_bar.setFormat("RAM: %p%")
        
        layout.addWidget(self.cpu_bar)
        layout.addWidget(self.gpu_bar)
        layout.addWidget(self.ram_bar)
    
    def update_stats(self, fps: float = 0, inference_ms: float = 0,
                     cpu: int = 0, gpu: int = 0, ram: int = 0) -> None:
        """Update all resource metrics."""
        self.lbl_fps.setText(f"FPS Aktual: {fps:.1f}")
        self.lbl_inference.setText(f"Waktu Inferensi: {inference_ms:.1f} ms")
        self.cpu_bar.setValue(min(100, cpu))
        self.gpu_bar.setValue(min(100, gpu))
        self.ram_bar.setValue(min(100, ram))
