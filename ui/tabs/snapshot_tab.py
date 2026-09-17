"""
Snapshot tab for DurianVision control panel.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ui.styles.theme import Theme
from ui.widgets.snapshot_gallery import SnapshotGallery

GROUP_BOX_STYLE = f"""
    QGroupBox {{
        font-weight: bold;
        border: 1px solid {Theme.BORDER};
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 15px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        color: {Theme.ACCENT};
    }}
"""


class SnapshotTab(QWidget):
    """Tab for snapshot controls and gallery."""
    
    snapshot_requested = pyqtSignal()
    auto_settings_changed = pyqtSignal(dict)
    open_folder_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 1. SNAPSHOT MANUAL
        manual_group = QGroupBox("SNAPSHOT & TANGKAPAN OTOMATIS")
        manual_group.setStyleSheet(GROUP_BOX_STYLE)
        manual_layout = QVBoxLayout(manual_group)
        
        self.hotkey_lbl = QLabel("Tombol Pintas: Space")
        self.btn_snap = QPushButton("📸 Ambil Snapshot Sekarang")
        self.btn_snap.clicked.connect(self.snapshot_requested.emit)
        
        manual_layout.addWidget(self.hotkey_lbl)
        manual_layout.addWidget(self.btn_snap)
        main_layout.addWidget(manual_group)
        
        # 2. TANGKAPAN OTOMATIS
        auto_group = QGroupBox("TANGKAPAN OTOMATIS")
        auto_group.setStyleSheet(GROUP_BOX_STYLE)
        auto_layout = QVBoxLayout(auto_group)
        
        self.chk_auto = QCheckBox("Aktifkan Tangkapan Otomatis")
        self.chk_auto.stateChanged.connect(self._emit_auto_settings)
        
        thresh_layout = QHBoxLayout()
        thresh_lbl = QLabel("Ambang Batas:")
        self.thresh_slider = QSlider(Qt.Orientation.Horizontal)
        self.thresh_slider.setRange(0, 100)
        self.thresh_slider.setValue(85)
        self.thresh_val = QLabel("85%")
        self.thresh_slider.valueChanged.connect(lambda v: self.thresh_val.setText(f"{v}%"))
        self.thresh_slider.valueChanged.connect(self._emit_auto_settings)
        
        thresh_layout.addWidget(thresh_lbl)
        thresh_layout.addWidget(self.thresh_slider)
        thresh_layout.addWidget(self.thresh_val)
        
        interval_layout = QHBoxLayout()
        interval_lbl = QLabel("Interval:")
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1 detik", "2 detik", "3 detik", "5 detik", "10 detik", "15 detik", "30 detik"])
        self.interval_combo.currentIndexChanged.connect(self._emit_auto_settings)
        
        interval_layout.addWidget(interval_lbl)
        interval_layout.addWidget(self.interval_combo)
        
        auto_layout.addWidget(self.chk_auto)
        auto_layout.addLayout(thresh_layout)
        auto_layout.addLayout(interval_layout)
        main_layout.addWidget(auto_group)
        
        # 3. GALERI TANGKAPAN TERAKHIR
        gallery_group = QGroupBox("GALERI TANGKAPAN TERAKHIR")
        gallery_group.setStyleSheet(GROUP_BOX_STYLE)
        gallery_layout = QVBoxLayout(gallery_group)
        
        self.gallery = SnapshotGallery()
        gallery_layout.addWidget(self.gallery)
        main_layout.addWidget(gallery_group)
        
        # Open Folder Button
        self.btn_open_folder = QPushButton("📂 Buka Folder Snapshot")
        self.btn_open_folder.clicked.connect(self.open_folder_requested.emit)
        main_layout.addWidget(self.btn_open_folder)
        
    def _emit_auto_settings(self) -> None:
        interval_str = self.interval_combo.currentText().split()[0]
        self.auto_settings_changed.emit({
            'enabled': self.chk_auto.isChecked(),
            'threshold': self.thresh_slider.value(),
            'interval': int(interval_str)
        })
        
    def add_snapshot(self, pixmap: QPixmap, variety: str, 
                     confidence: str, timestamp: str) -> None:
        """Add a snapshot to the gallery."""
        self.gallery.add_snapshot(pixmap, variety, confidence, timestamp)
        
    def clear_gallery(self) -> None:
        """Clear all snapshots from gallery."""
        self.gallery.clear_gallery()
