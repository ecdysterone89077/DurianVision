"""
Log tab for DurianVision control panel.
"""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.styles.theme import Theme
from ui.widgets.log_table import LogTable

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


class LogTab(QWidget):
    """Tab for detection logs, export, and session summary."""
    
    export_csv_requested = pyqtSignal()
    export_xlsx_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 1. CATATAN DETEKSI
        log_group = QGroupBox("CATATAN DETEKSI")
        log_group.setStyleSheet(GROUP_BOX_STYLE)
        log_layout = QVBoxLayout(log_group)
        
        self.log_table = LogTable()
        
        btn_layout = QHBoxLayout()
        self.btn_csv = QPushButton("📥 Ekspor CSV")
        self.btn_csv.clicked.connect(self.export_csv_requested.emit)
        self.btn_xlsx = QPushButton("📥 Ekspor XLSX")
        self.btn_xlsx.clicked.connect(self.export_xlsx_requested.emit)
        self.btn_clear = QPushButton("🗑️ Hapus Semua Catatan")
        self.btn_clear.clicked.connect(self.clear_requested.emit)
        
        btn_layout.addWidget(self.btn_csv)
        btn_layout.addWidget(self.btn_xlsx)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_clear)
        
        log_layout.addWidget(self.log_table)
        log_layout.addLayout(btn_layout)
        main_layout.addWidget(log_group)
        
        # 2. RINGKASAN SESI
        summary_group = QGroupBox("RINGKASAN SESI")
        summary_group.setStyleSheet(GROUP_BOX_STYLE)
        self.summary_layout = QVBoxLayout(summary_group)
        
        self.lbl_duration = QLabel("Durasi Sesi: 00:00:00")
        self.lbl_frames = QLabel("Frame Diproses: 0")
        self.lbl_device = QLabel("Perangkat: -")
        
        self.summary_layout.addWidget(self.lbl_duration)
        self.summary_layout.addWidget(self.lbl_frames)
        self.summary_layout.addWidget(self.lbl_device)
        
        self.dist_layout = QVBoxLayout()
        self.summary_layout.addLayout(self.dist_layout)
        
        main_layout.addWidget(summary_group)
        
    def add_log_entry(self, timestamp: str, variety: str, 
                      confidence: float, count: int) -> None:
        """Add a new log entry."""
        self.log_table.add_entry(
            timestamp, variety, f"{confidence:.0f}%", str(count)
        )

    def clear_logs(self) -> None:
        """Clear all log entries."""
        self.log_table.clear_entries()
        
    def update_session_summary(self, duration: str, frames: int, 
                               device: str, distribution_dict: dict) -> None:
        """Update session summary section."""
        self.lbl_duration.setText(f"Durasi Sesi: {duration}")
        self.lbl_frames.setText(f"Frame Diproses: {frames}")
        self.lbl_device.setText(f"Perangkat: {device}")
        
        # Clear previous distribution bars
        while self.dist_layout.count():
            item = self.dist_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for var_name, data in distribution_dict.items():
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            lbl = QLabel(var_name)
            lbl.setFixedWidth(100)
            
            bar = QProgressBar()
            bar.setValue(int(data.get('pct', 0)))
            color = data.get('color', Theme.ACCENT)
            bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
            
            pct_lbl = QLabel(f"{int(data.get('pct', 0))}%")
            
            row_layout.addWidget(lbl)
            row_layout.addWidget(bar)
            row_layout.addWidget(pct_lbl)
            
            self.dist_layout.addWidget(row)
