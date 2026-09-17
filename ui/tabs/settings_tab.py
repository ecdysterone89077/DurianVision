"""
Settings tab for DurianVision control panel.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ui.styles.theme import Theme

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


class SettingsTab(QWidget):
    """Tab for application settings."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        
        # 1. TAMPILAN OVERLAY
        overlay_group = QGroupBox("TAMPILAN OVERLAY")
        overlay_group.setStyleSheet(GROUP_BOX_STYLE)
        overlay_layout = QVBoxLayout(overlay_group)
        
        self.chk_box = QCheckBox("Tampilkan Kotak Pembatas (Bounding Boxes)")
        self.chk_box.setChecked(True)
        self.chk_lbl = QCheckBox("Tampilkan Label")
        self.chk_lbl.setChecked(True)
        self.chk_conf = QCheckBox("Tampilkan Persentase Akurasi")
        self.chk_conf.setChecked(True)
        
        line_layout = QHBoxLayout()
        line_layout.addWidget(QLabel("Ketebalan Garis:"))
        self.combo_line = QComboBox()
        self.combo_line.addItems(["1px", "2px", "3px", "4px", "5px"])
        self.combo_line.setCurrentIndex(1)  # Default 2px
        line_layout.addWidget(self.combo_line)
        line_layout.addStretch()
        
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Ukuran Font:"))
        self.combo_font = QComboBox()
        self.combo_font.addItems([f"{i}px" for i in range(10, 21)])
        self.combo_font.setCurrentIndex(4)  # Default 14px
        font_layout.addWidget(self.combo_font)
        font_layout.addStretch()
        
        overlay_layout.addWidget(self.chk_box)
        overlay_layout.addWidget(self.chk_lbl)
        overlay_layout.addWidget(self.chk_conf)
        overlay_layout.addLayout(line_layout)
        overlay_layout.addLayout(font_layout)
        content_layout.addWidget(overlay_group)
        
        # 2. NOTIFIKASI & SUARA
        sound_group = QGroupBox("NOTIFIKASI & SUARA")
        sound_group.setStyleSheet(GROUP_BOX_STYLE)
        sound_layout = QVBoxLayout(sound_group)
        
        self.chk_sound = QCheckBox("Aktifkan Peringatan Suara")
        self.chk_sound.setChecked(True)
        
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Volume:"))
        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(50)
        self.vol_label = QLabel("50%")
        self.slider_vol.valueChanged.connect(lambda v: self.vol_label.setText(f"{v}%"))
        vol_layout.addWidget(self.slider_vol)
        vol_layout.addWidget(self.vol_label)
        
        sound_layout.addWidget(self.chk_sound)
        sound_layout.addLayout(vol_layout)
        content_layout.addWidget(sound_group)
        
        # 3. DETEKSI PERANGKAT
        dev_group = QGroupBox("DETEKSI PERANGKAT")
        dev_group.setStyleSheet(GROUP_BOX_STYLE)
        dev_layout = QHBoxLayout(dev_group)
        
        self.radio_auto = QRadioButton("Otomatis")
        self.radio_auto.setChecked(True)
        self.radio_phone = QRadioButton("Paksa Smartphone")
        self.radio_desk = QRadioButton("Paksa Desktop")
        
        self.dev_btn_group = QButtonGroup()
        self.dev_btn_group.addButton(self.radio_auto)
        self.dev_btn_group.addButton(self.radio_phone)
        self.dev_btn_group.addButton(self.radio_desk)
        
        dev_layout.addWidget(self.radio_auto)
        dev_layout.addWidget(self.radio_phone)
        dev_layout.addWidget(self.radio_desk)
        content_layout.addWidget(dev_group)
        
        # 4. PENYIMPANAN
        storage_group = QGroupBox("PENYIMPANAN")
        storage_group.setStyleSheet(GROUP_BOX_STYLE)
        storage_layout = QVBoxLayout(storage_group)
        
        snap_layout = QHBoxLayout()
        snap_layout.addWidget(QLabel("Folder Snapshot:"))
        self.txt_snap = QLineEdit("snapshots")
        self.btn_snap_dir = QPushButton("📂 Pilih Folder")
        self.btn_snap_dir.clicked.connect(self._select_snap_dir)
        snap_layout.addWidget(self.txt_snap)
        snap_layout.addWidget(self.btn_snap_dir)
        
        log_layout = QHBoxLayout()
        log_layout.addWidget(QLabel("Folder Catatan:"))
        self.txt_log = QLineEdit("logs")
        self.btn_log_dir = QPushButton("📂 Pilih Folder")
        self.btn_log_dir.clicked.connect(self._select_log_dir)
        log_layout.addWidget(self.txt_log)
        log_layout.addWidget(self.btn_log_dir)
        
        storage_layout.addLayout(snap_layout)
        storage_layout.addLayout(log_layout)
        content_layout.addWidget(storage_group)
        
        # 5. TOMBOL PINTAS
        hk_group = QGroupBox("TOMBOL PINTAS")
        hk_group.setStyleSheet(GROUP_BOX_STYLE)
        hk_layout = QVBoxLayout(hk_group)
        
        self.hks = {}
        hotkey_defaults = {
            "Snapshot": "Space",
            "Mulai/Berhenti": "Ctrl+Shift+D",
            "Pilih Area": "Ctrl+Shift+R",
            "Sembunyikan": "Ctrl+Shift+H"
        }
        for action, default_key in hotkey_defaults.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(action))
            txt = QLineEdit(default_key)
            row.addWidget(txt)
            self.hks[action] = txt
            hk_layout.addLayout(row)
            
        content_layout.addWidget(hk_group)
        
        # Save Button
        self.btn_save = QPushButton("💾 Simpan Pengaturan")
        self.btn_save.clicked.connect(self._on_save)
        content_layout.addWidget(self.btn_save)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def _select_snap_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Snapshot")
        if folder:
            self.txt_snap.setText(folder)
    
    def _select_log_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Catatan")
        if folder:
            self.txt_log.setText(folder)
        
    def _on_save(self) -> None:
        self.settings_changed.emit(self.get_settings())
        
    def load_settings(self, config: dict) -> None:
        """Apply config dictionary to UI elements."""
        overlay = config.get('overlay', {})
        self.chk_box.setChecked(overlay.get('show_boxes', True))
        self.chk_lbl.setChecked(overlay.get('show_labels', True))
        self.chk_conf.setChecked(overlay.get('show_confidence', True))
        
        line_thick = overlay.get('line_thickness', 2)
        idx = max(0, line_thick - 1)
        if idx < self.combo_line.count():
            self.combo_line.setCurrentIndex(idx)
        
        font_size = overlay.get('font_size', 14)
        font_idx = max(0, font_size - 10)
        if font_idx < self.combo_font.count():
            self.combo_font.setCurrentIndex(font_idx)
        
        audio = config.get('audio', {})
        self.chk_sound.setChecked(audio.get('enabled', True))
        self.slider_vol.setValue(int(audio.get('volume', 0.5) * 100))
        
        snapshot = config.get('snapshot', {})
        self.txt_snap.setText(snapshot.get('save_dir', 'snapshots'))
        
        log = config.get('log', {})
        self.txt_log.setText(log.get('save_dir', 'logs'))
        
        hotkeys = config.get('hotkeys', {})
        if 'Snapshot' in self.hks:
            self.hks['Snapshot'].setText(hotkeys.get('snapshot', 'Space'))
        if 'Mulai/Berhenti' in self.hks:
            self.hks['Mulai/Berhenti'].setText(hotkeys.get('toggle_detection', 'Ctrl+Shift+D'))
        if 'Pilih Area' in self.hks:
            self.hks['Pilih Area'].setText(hotkeys.get('select_roi', 'Ctrl+Shift+R'))
        if 'Sembunyikan' in self.hks:
            self.hks['Sembunyikan'].setText(hotkeys.get('hide', 'Ctrl+Shift+H'))
            
        # Device detection mode
        device_mode = config.get('device_detection', {}).get('mode', 'auto')
        if device_mode == 'smartphone':
            self.radio_phone.setChecked(True)
        elif device_mode == 'desktop':
            self.radio_desk.setChecked(True)
        else:
            self.radio_auto.setChecked(True)
        
    def get_settings(self) -> dict:
        """Extract settings dictionary from UI elements."""
        line_thickness = int(self.combo_line.currentText().replace('px', ''))
        font_size = int(self.combo_font.currentText().replace('px', ''))
        
        return {
            'overlay': {
                'show_boxes': self.chk_box.isChecked(),
                'show_labels': self.chk_lbl.isChecked(),
                'show_confidence': self.chk_conf.isChecked(),
                'line_thickness': line_thickness,
                'font_size': font_size,
            },
            'audio': {
                'enabled': self.chk_sound.isChecked(),
                'volume': self.slider_vol.value() / 100.0,
            },
            'snapshot': {
                'save_dir': self.txt_snap.text(),
            },
            'log': {
                'save_dir': self.txt_log.text(),
            },
            'device_detection': {
                'mode': 'smartphone' if self.radio_phone.isChecked() else 'desktop' if self.radio_desk.isChecked() else 'auto'
            },
            'hotkeys': {
                'snapshot': self.hks['Snapshot'].text() if 'Snapshot' in self.hks else '',
                'toggle_detection': self.hks['Mulai/Berhenti'].text() if 'Mulai/Berhenti' in self.hks else '',
                'select_roi': self.hks['Pilih Area'].text() if 'Pilih Area' in self.hks else '',
                'hide': self.hks['Sembunyikan'].text() if 'Sembunyikan' in self.hks else '',
            },
        }
