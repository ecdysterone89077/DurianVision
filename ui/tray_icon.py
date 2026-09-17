from enum import Enum

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    """
    System tray icon with context menu for the app.
    """
    
    class Status(Enum):
        IDLE = 1
        DETECTING = 2
        ERROR = 3

    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    roi_requested = pyqtSignal()
    snapshot_requested = pyqtSignal()
    panel_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    fullscreen_requested = pyqtSignal()
    sound_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_status = self.Status.IDLE
        self.is_detecting = False
        self.sound_enabled = True
        
        self.icons = {
            self.Status.IDLE: self._create_icon(QColor('#EAB308')),     # Yellow
            self.Status.DETECTING: self._create_icon(QColor('#22C55E')), # Green
            self.Status.ERROR: self._create_icon(QColor('#EF4444'))      # Red
        }
        
        self._setup_menu()
        self.set_status(self.Status.IDLE)
        self.activated.connect(self._on_activated)

    def _create_icon(self, color: QColor) -> QIcon:
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 32, 32)
        painter.end()
        return QIcon(pixmap)

    def _setup_menu(self):
        self.menu = QMenu()
        
        title_action = self.menu.addAction('─── DurianVision ───')
        title_action.setEnabled(False)
        
        self.toggle_action = self.menu.addAction('▶ Mulai Deteksi')
        self.toggle_action.triggered.connect(self._toggle_detection)
        
        roi_action = self.menu.addAction('📐 Pilih Area Layar')
        roi_action.triggered.connect(self.roi_requested.emit)
        
        fullscreen_action = self.menu.addAction('🖥️ Layar Penuh')
        fullscreen_action.triggered.connect(self.fullscreen_requested.emit)
        
        self.menu.addSeparator()
        
        snapshot_action = self.menu.addAction('📸 Ambil Snapshot [Spasi]')
        snapshot_action.triggered.connect(self.snapshot_requested.emit)
        
        self.sound_action = self.menu.addAction('🔇 Matikan Suara')
        self.sound_action.triggered.connect(self._toggle_sound)
        
        self.menu.addSeparator()
        
        panel_action = self.menu.addAction('📊 Buka Panel Kontrol')
        panel_action.triggered.connect(self.panel_requested.emit)
        
        self.menu.addSeparator()
        
        quit_action = self.menu.addAction('❌ Keluar')
        quit_action.triggered.connect(self.quit_requested.emit)
        
        self.setContextMenu(self.menu)

    def _toggle_detection(self):
        if self.is_detecting:
            self.stop_requested.emit()
        else:
            self.start_requested.emit()

    def set_status(self, status: Status):
        self.current_status = status
        self.setIcon(self.icons[status])
        
        if status == self.Status.IDLE:
            self.is_detecting = False
            self.toggle_action.setText('▶ Mulai Deteksi')
            self.setToolTip('DurianVision - Menunggu')
        elif status == self.Status.DETECTING:
            self.is_detecting = True
            self.toggle_action.setText('⏹ Hentikan Deteksi')
            self.setToolTip('DurianVision - Mendeteksi')
        elif status == self.Status.ERROR:
            self.is_detecting = False
            self.toggle_action.setText('▶ Mulai Deteksi')
            self.setToolTip('DurianVision - Error')

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.panel_requested.emit()

    def _toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.sound_action.setText('🔇 Matikan Suara')
        else:
            self.sound_action.setText('🔊 Aktifkan Suara')
        self.sound_toggled.emit(self.sound_enabled)

    def update_live_stats(self, fps: float, count: int, duration: str) -> None:
        self.setToolTip(f"DurianVision | FPS: {fps:.1f} | 🍈 {count} objek | ⏱ {duration}")
