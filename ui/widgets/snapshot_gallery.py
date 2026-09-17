"""
Snapshot gallery widget for DurianVision.
Displays captured snapshots in a grid layout.
"""
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.styles.theme import Theme


class SnapshotCard(QFrame):
    """Individual snapshot card with image, variety, confidence, and timestamp."""
    
    def __init__(self, pixmap: QPixmap, variety: str, confidence: str, 
                 timestamp: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background-color: {Theme.BG_CARD}; "
            f"border: 1px solid {Theme.BORDER}; border-radius: 5px;"
        )
        layout = QVBoxLayout(self)
        
        img_lbl = QLabel()
        img_lbl.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        var_lbl = QLabel(variety)
        var_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        var_lbl.setStyleSheet("font-weight: bold;")
        
        conf_lbl = QLabel(f"Akurasi: {confidence}")
        conf_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        conf_lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 10px;")
        
        time_lbl = QLabel(timestamp)
        time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 10px;")
        
        layout.addWidget(img_lbl)
        layout.addWidget(var_lbl)
        layout.addWidget(conf_lbl)
        layout.addWidget(time_lbl)


class SnapshotGallery(QWidget):
    """Grid gallery of snapshot cards with scroll support."""
    
    COLUMNS = 3
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.gallery_widget = QWidget()
        self.grid = QGridLayout(self.gallery_widget)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.gallery_widget)
        
        self.placeholder_lbl = QLabel("Belum ada tangkapan")
        self.placeholder_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid.addWidget(self.placeholder_lbl, 0, 0, 1, self.COLUMNS)
        
        layout.addWidget(self.scroll)
        self.cards: list[SnapshotCard] = []
    
    def add_snapshot(self, pixmap: QPixmap, variety: str, 
                     confidence: str, timestamp: str) -> None:
        """Add a new snapshot card to the gallery."""
        if self.placeholder_lbl.isVisible():
            self.placeholder_lbl.setVisible(False)
            
        card = SnapshotCard(pixmap, variety, confidence, timestamp)
        self.cards.append(card)
        
        idx = len(self.cards) - 1
        row = idx // self.COLUMNS
        col = idx % self.COLUMNS
        self.grid.addWidget(card, row, col)
    
    def load_from_directory(self, directory: str, limit: int = 24) -> None:
        """Load existing snapshots from a directory (terbaru dulu, maksimal `limit`)."""
        if not os.path.isdir(directory):
            return
        names = [
            filename for filename in os.listdir(directory)
            if filename.lower().endswith(('.jpg', '.png', '.jpeg'))
        ]
        names.sort(reverse=True)
        for filename in names[:limit]:
            filepath = os.path.join(directory, filename)
            pixmap = QPixmap(filepath)
            if not pixmap.isNull():
                self.add_snapshot(pixmap, "", "", filename)
        
    def clear_gallery(self) -> None:
        """Remove all snapshot cards."""
        for card in self.cards:
            self.grid.removeWidget(card)
            card.deleteLater()
        self.cards.clear()
        self.placeholder_lbl.setVisible(True)
