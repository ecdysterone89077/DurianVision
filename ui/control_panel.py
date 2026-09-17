"""
Control panel window for DurianVision.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.tabs import DetectionTab, LogTab, PerformanceTab, SettingsTab, SnapshotTab


class ControlPanel(QMainWindow):
    """Control Panel window with tabbed interface for DurianVision."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('🍈 DurianVision')
        self.setMinimumSize(420, 580)
        self.resize(420, 580)
        
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        )
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #e4e4e7;
            }
        """)
        
        # Create tab instances as named attributes for external access
        self.detection_tab = DetectionTab()
        self.performance_tab = PerformanceTab()
        self.snapshot_tab = SnapshotTab()
        self.log_tab = LogTab()
        self.settings_tab = SettingsTab()
        
        self._init_ui()

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Left Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(120)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #16213e;
                border-right: 1px solid #374151;
            }
            QPushButton {
                background: transparent;
                color: #a1a1aa;
                border: none;
                padding: 10px;
                text-align: left;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0f3460;
                color: #e4e4e7;
            }
            QPushButton[active="true"] {
                background-color: #0f3460;
                color: #22C55E;
                font-weight: bold;
                border-left: 3px solid #22C55E;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 10, 0, 0)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.tabs = QStackedWidget()
        self.buttons: list[QPushButton] = []
        
        tab_info = [
            ("🎯 Deteksi", self.detection_tab),
            ("⚡ Performa", self.performance_tab),
            ("📸 Snapshot", self.snapshot_tab),
            ("📋 Log", self.log_tab),
            ("⚙️ Pengaturan", self.settings_tab)
        ]
        
        for i, (btn_text, tab_widget) in enumerate(tab_info):
            btn = QPushButton(btn_text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda checked, index=i: self.switch_tab(index))
            
            sidebar_layout.addWidget(btn)
            self.buttons.append(btn)
            self.tabs.addWidget(tab_widget)
            
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.tabs)
        main_layout.addLayout(content_layout)
        
        # Bottom Status Bar
        self.status_bar_frame = QFrame()
        self.status_bar_frame.setFixedHeight(30)
        self.status_bar_frame.setStyleSheet("""
            QFrame {
                background-color: #0f3460;
                border-top: 1px solid #374151;
            }
            QLabel {
                font-size: 11px;
                color: #a1a1aa;
            }
        """)
        
        status_layout = QHBoxLayout(self.status_bar_frame)
        status_layout.setContentsMargins(10, 0, 10, 0)
        
        self.lbl_status_dot = QLabel("●")
        self.lbl_status_dot.setStyleSheet("color: #EAB308;")
        self.lbl_status = QLabel("Idle")
        self.lbl_fps = QLabel("0 FPS")
        self.lbl_device = QLabel("CPU")
        self.lbl_area = QLabel("Area: Full")
        self.lbl_pipeline = QLabel("")
        
        status_layout.addWidget(self.lbl_status_dot)
        status_layout.addWidget(self.lbl_status)
        status_layout.addStretch()
        status_layout.addWidget(self.lbl_pipeline)
        status_layout.addSpacing(10)
        status_layout.addWidget(self.lbl_fps)
        status_layout.addSpacing(10)
        status_layout.addWidget(self.lbl_device)
        status_layout.addSpacing(10)
        status_layout.addWidget(self.lbl_area)
        
        main_layout.addWidget(self.status_bar_frame)
        
        self.switch_tab(0)

    def switch_tab(self, index: int) -> None:
        """Switch to the specified tab index."""
        self.tabs.setCurrentIndex(index)
        for i, btn in enumerate(self.buttons):
            is_active = (i == index)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def update_status_bar(self, data: dict) -> None:
        """Update the bottom status bar."""
        if 'status' in data:
            status = data['status']
            if status == 'detecting':
                self.lbl_status_dot.setStyleSheet("color: #22C55E;")
                self.lbl_status.setText("Mendeteksi")
            elif status == 'error':
                self.lbl_status_dot.setStyleSheet("color: #EF4444;")
                self.lbl_status.setText("Error")
            else:
                self.lbl_status_dot.setStyleSheet("color: #EAB308;")
                self.lbl_status.setText("Idle")
                
        if 'fps' in data:
            self.lbl_fps.setText(f"{data['fps']:.1f} FPS")
        if 'device' in data:
            self.lbl_device.setText(data['device'])
        if 'area' in data:
            self.lbl_area.setText(f"Area: {data['area']}")
        if 'pipeline' in data:
            self.lbl_pipeline.setText(f"🔗 {data['pipeline']}")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Minimize to tray instead of closing."""
        event.ignore()
        self.hide()
