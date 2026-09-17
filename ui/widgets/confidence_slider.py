"""
Confidence threshold slider widget for DurianVision.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSlider, QWidget


class ConfidenceSlider(QWidget):
    """Horizontal slider for confidence threshold with value label."""
    
    value_changed = pyqtSignal(int)  # Emits 0-100
    
    def __init__(self, initial_value: int = 60, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(initial_value)
        
        self.val_label = QLabel(f"{initial_value}%")
        self.val_label.setFixedWidth(45)
        
        layout.addWidget(self.slider)
        layout.addWidget(self.val_label)
        
        self.slider.valueChanged.connect(self._on_value_changed)
        
    def _on_value_changed(self, val: int) -> None:
        self.val_label.setText(f"{val}%")
        self.value_changed.emit(val)
    
    def set_value(self, val: int) -> None:
        """Set slider value programmatically."""
        self.slider.setValue(val)
