"""
Detection list widget for DurianVision.
Displays currently detected objects with colors and counts.
"""
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.styles.theme import Theme


class DetectionList(QWidget):
    """Scrollable list of current detections with variety colors."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.layout_main.setSpacing(5)
        self.layout_main.addStretch()

    def update_items(self, detections: list[dict]) -> None:
        """
        Update the detection list.
        Each dict: {'name': str, 'conf': float, 'count': int, 'color': str}
        """
        # Clear existing items except stretch
        while self.layout_main.count() > 1:
            item = self.layout_main.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for det in detections:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 3, 5, 3)
            
            color = det.get('color', Theme.ACCENT)
            
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color};")
            
            name_lbl = QLabel(det.get('name', 'Unknown'))
            name_lbl.setStyleSheet("font-weight: bold;")
            conf_lbl = QLabel(f"{int(det.get('conf', 0) * 100)}%")
            count_lbl = QLabel(f"x{det.get('count', 0)}")
            count_lbl.setStyleSheet(f"color: {color}; font-weight: bold;")
            
            item_layout.addWidget(dot)
            item_layout.addWidget(name_lbl)
            item_layout.addStretch()
            item_layout.addWidget(conf_lbl)
            item_layout.addWidget(count_lbl)
            
            self.layout_main.insertWidget(self.layout_main.count() - 1, item_widget)
    
    def clear_items(self) -> None:
        """Remove all detection items."""
        while self.layout_main.count() > 1:
            item = self.layout_main.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
