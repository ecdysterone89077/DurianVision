"""
Performance tab for DurianVision control panel.
"""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from ui.styles.theme import Theme
from ui.widgets.fps_slider import FPSSlider
from ui.widgets.resource_monitor import ResourceMonitor

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


class PerformanceTab(QWidget):
    """Tab for performance settings and resource monitoring."""
    
    fps_limit_changed = pyqtSignal(int)
    model_changed = pyqtSignal(str)
    inference_size_changed = pyqtSignal(int)
    device_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 1. PEMBATAS FPS
        fps_group = QGroupBox("PEMBATAS FPS")
        fps_group.setStyleSheet(GROUP_BOX_STYLE)
        fps_layout = QVBoxLayout(fps_group)
        
        self.fps_slider = FPSSlider(min_fps=1, max_fps=30, initial=15)
        self.fps_slider.value_changed.connect(self.fps_limit_changed.emit)
        
        self.fps_hint_lbl = QLabel("Rekomendasi untuk smartphone: 10-15 FPS")
        self.fps_hint_lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        
        fps_layout.addWidget(self.fps_slider)
        fps_layout.addWidget(self.fps_hint_lbl)
        main_layout.addWidget(fps_group)
        
        # 2. MODEL YOLO
        model_group = QGroupBox("MODEL YOLO")
        model_group.setStyleSheet(GROUP_BOX_STYLE)
        model_layout = QHBoxLayout(model_group)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["best.pt", "yolo11n.pt"])
        self.btn_change_model = QPushButton("📂 Ganti Model...")
        self.btn_change_model.clicked.connect(self._on_change_model)
        
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(self.btn_change_model)
        main_layout.addWidget(model_group)
        
        # 3. UKURAN INFERENSI
        size_group = QGroupBox("UKURAN INFERENSI")
        size_group.setStyleSheet(GROUP_BOX_STYLE)
        size_layout = QVBoxLayout(size_group)
        
        self.size_combo = QComboBox()
        self.size_combo.addItems(["320x320", "416x416", "640x640"])
        self.size_combo.setCurrentIndex(1)  # Default 416
        self.size_combo.currentIndexChanged.connect(self._on_size_changed)
        
        size_layout.addWidget(self.size_combo)
        main_layout.addWidget(size_group)
        
        # 4. MONITOR WAKTU-NYATA
        monitor_group = QGroupBox("MONITOR WAKTU-NYATA")
        monitor_group.setStyleSheet(GROUP_BOX_STYLE)
        monitor_layout = QVBoxLayout(monitor_group)
        
        self.resource_monitor = ResourceMonitor()
        monitor_layout.addWidget(self.resource_monitor)
        main_layout.addWidget(monitor_group)
        
        # 5. PERANGKAT INFERENSI
        device_group = QGroupBox("PERANGKAT INFERENSI")
        device_group.setStyleSheet(GROUP_BOX_STYLE)
        device_layout = QHBoxLayout(device_group)
        
        self.radio_cpu = QRadioButton("CPU")
        self.radio_cuda = QRadioButton("CUDA")
        self.radio_dml = QRadioButton("DirectML")
        self.radio_cpu.setChecked(True)
        
        self.dev_btn_group = QButtonGroup()
        self.dev_btn_group.addButton(self.radio_cpu, 1)
        self.dev_btn_group.addButton(self.radio_cuda, 2)
        self.dev_btn_group.addButton(self.radio_dml, 3)
        self.dev_btn_group.buttonClicked.connect(self._on_device_changed)
        
        device_layout.addWidget(self.radio_cpu)
        device_layout.addWidget(self.radio_cuda)
        device_layout.addWidget(self.radio_dml)
        main_layout.addWidget(device_group)
        
        # 6. INFO PERANGKAT TERDETEKSI
        info_group = QGroupBox("INFO PERANGKAT TERDETEKSI")
        info_group.setStyleSheet(GROUP_BOX_STYLE)
        info_layout = QVBoxLayout(info_group)
        
        self.lbl_type = QLabel("Tipe: Tidak Diketahui")
        self.lbl_ratio = QLabel("Rasio: -")
        self.lbl_res = QLabel("Resolusi: -")
        self.lbl_scale = QLabel("Skala: -")
        
        info_layout.addWidget(self.lbl_type)
        info_layout.addWidget(self.lbl_ratio)
        info_layout.addWidget(self.lbl_res)
        info_layout.addWidget(self.lbl_scale)
        main_layout.addWidget(info_group)
        
        main_layout.addStretch()
        
    def _on_change_model(self) -> None:
        import os
        file, _ = QFileDialog.getOpenFileName(
            self, "Pilih Model YOLO", "", "Model Files (*.pt *.onnx)"
        )
        if file:
            self.model_combo.addItem(os.path.basename(file))
            self.model_combo.setCurrentIndex(self.model_combo.count() - 1)
            self.model_changed.emit(file)
            
    def _on_size_changed(self, idx: int) -> None:
        size_str = self.size_combo.currentText().split('x')[0]
        self.inference_size_changed.emit(int(size_str))
        
    def _on_device_changed(self, btn) -> None:
        self.device_changed.emit(btn.text())
        
    def update_stats(self, fps: float, inference_ms: float, 
                     cpu: int, gpu: int, ram: int) -> None:
        """Update real-time performance stats."""
        self.resource_monitor.update_stats(fps, inference_ms, cpu, gpu, ram)
        
    def update_device_info(self, info_dict: dict) -> None:
        """Update detected device information."""
        self.lbl_type.setText(f"Tipe: {info_dict.get('type', 'Tidak Diketahui')}")
        self.lbl_ratio.setText(f"Rasio: {info_dict.get('aspect_ratio', '-')}")
        self.lbl_res.setText(f"Resolusi: {info_dict.get('resolution', '-')}")
        self.lbl_scale.setText(f"Skala: {info_dict.get('scale_factor', '-')}")
