"""
Detection tab for DurianVision control panel.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.styles.theme import Theme
from ui.widgets.confidence_slider import ConfidenceSlider
from ui.widgets.detection_list import DetectionList

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


class DetectionTab(QWidget):
    """Tab for detection controls, ROI preview, and detection list."""
    
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    roi_requested = pyqtSignal()
    fullscreen_requested = pyqtSignal()
    confidence_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 1. KONTROL DETEKSI
        control_group = QGroupBox("KONTROL DETEKSI")
        control_group.setStyleSheet(GROUP_BOX_STYLE)
        control_layout = QVBoxLayout(control_group)
        
        status_layout = QHBoxLayout()
        self.status_lbl = QLabel("● Nonaktif")
        self.status_lbl.setStyleSheet("color: red; font-weight: bold;")
        self.device_type_lbl = QLabel("Perangkat: -")
        status_layout.addWidget(self.status_lbl)
        status_layout.addStretch()
        status_layout.addWidget(self.device_type_lbl)
        
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ MULAI DETEKSI")
        self.btn_start.clicked.connect(self.start_requested.emit)
        self.btn_stop = QPushButton("⏹ BERHENTI")
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        
        control_layout.addLayout(status_layout)
        control_layout.addLayout(btn_layout)
        main_layout.addWidget(control_group)
        
        # 2. AREA PEMANTAUAN
        area_group = QGroupBox("AREA PEMANTAUAN")
        area_group.setStyleSheet(GROUP_BOX_STYLE)
        area_layout = QVBoxLayout(area_group)
        
        self.area_dims_lbl = QLabel("Dimensi: 0x0")
        self.area_pos_lbl = QLabel("Posisi: (0, 0)")
        
        self.thumbnail = QLabel("Tidak Ada Pratinjau")
        self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail.setStyleSheet(
            f"background-color: {Theme.BG_CARD}; border: 1px solid {Theme.BORDER};"
        )
        self.thumbnail.setMinimumHeight(120)
        
        area_btn_layout = QHBoxLayout()
        self.btn_roi = QPushButton("📐 Ubah Area")
        self.btn_roi.clicked.connect(self.roi_requested.emit)
        self.btn_full = QPushButton("🖥️ Layar Penuh")
        self.btn_full.clicked.connect(self.fullscreen_requested.emit)
        area_btn_layout.addWidget(self.btn_roi)
        area_btn_layout.addWidget(self.btn_full)
        
        area_layout.addWidget(self.area_dims_lbl)
        area_layout.addWidget(self.area_pos_lbl)
        area_layout.addWidget(self.thumbnail)
        area_layout.addLayout(area_btn_layout)
        main_layout.addWidget(area_group)
        
        # 3. AMBANG BATAS AKURASI
        conf_group = QGroupBox("AMBANG BATAS AKURASI")
        conf_group.setStyleSheet(GROUP_BOX_STYLE)
        conf_layout = QVBoxLayout(conf_group)
        self.conf_slider = ConfidenceSlider(initial_value=72)
        self.conf_slider.value_changed.connect(self.confidence_changed.emit)
        conf_layout.addWidget(self.conf_slider)
        main_layout.addWidget(conf_group)
        
        # 4. DETEKSI SAAT INI
        det_group = QGroupBox("DETEKSI SAAT INI")
        det_group.setStyleSheet(GROUP_BOX_STYLE)
        det_layout = QVBoxLayout(det_group)
        
        self.det_list = DetectionList()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.det_list)
        scroll.setMinimumHeight(150)
        
        self.total_obj_lbl = QLabel("Total Objek: 0")
        
        det_layout.addWidget(scroll)
        det_layout.addWidget(self.total_obj_lbl)
        main_layout.addWidget(det_group)
        
        main_layout.addStretch()

    def update_status(self, is_detecting: bool, device_info: str) -> None:
        """Update detection status display."""
        if is_detecting:
            self.status_lbl.setText("● Aktif")
            self.status_lbl.setStyleSheet(f"color: {Theme.ACCENT}; font-weight: bold;")
        else:
            self.status_lbl.setText("● Nonaktif")
            self.status_lbl.setStyleSheet("color: red; font-weight: bold;")
        self.device_type_lbl.setText(f"Perangkat: {device_info}")

    def update_preview(self, pixmap: QPixmap) -> None:
        """Update ROI preview thumbnail."""
        if not pixmap.isNull():
            self.thumbnail.setPixmap(
                pixmap.scaled(self.thumbnail.size(), Qt.AspectRatioMode.KeepAspectRatio)
            )

    def update_area_info(self, x: int, y: int, w: int, h: int) -> None:
        """Update area dimension and position labels."""
        self.area_dims_lbl.setText(f"Dimensi: {w}x{h}")
        self.area_pos_lbl.setText(f"Posisi: ({x}, {y})")

    def update_detections(self, detections: list[dict]) -> None:
        """Update the detection list and total count."""
        self.det_list.update_items(detections)
        total = sum(d.get('count', 0) for d in detections)
        self.total_obj_lbl.setText(f"Total Objek: {total}")
