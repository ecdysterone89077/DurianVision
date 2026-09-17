"""
FPS limit slider widget for DurianVision.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSlider, QWidget


class FPSSlider(QWidget):
    """Horizontal slider for FPS limit with value label."""
    
    value_changed = pyqtSignal(int)
    
    def __init__(self, min_fps: int = 1, max_fps: int = 30, initial: int = 15, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_fps, max_fps)
        self.slider.setValue(initial)
        
        self.val_label = QLabel(f"{initial} FPS")
        self.val_label.setFixedWidth(55)
        
        layout.addWidget(self.slider)
        layout.addWidget(self.val_label)
        
        self.slider.valueChanged.connect(self._on_value_changed)
        
    def _on_value_changed(self, val: int) -> None:
        self.val_label.setText(f"{val} FPS")
        self.value_changed.emit(val)
    
    def set_value(self, val: int) -> None:
        """Set slider value programmatically."""
        self.slider.setValue(val)
