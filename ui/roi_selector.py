"""
RoI Selector window for DurianVision.
Allows user to select a region of interest on the screen.
"""
from PyQt6.QtCore import QPoint, QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QKeyEvent, QMouseEvent, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.device_detector import DeviceDetector


class RoISelectorWindow(QWidget):
    """Fullscreen overlay for selecting a screen region of interest."""
    
    roi_selected = pyqtSignal(int, int, int, int, dict)  # x, y, w, h, device_info
    roi_cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        screens = QApplication.screens()
        if screens:
            rect = QRect()
            for screen in screens:
                rect = rect.united(screen.geometry())
            self.setGeometry(rect)
            
        self.setCursor(Qt.CursorShape.CrossCursor)
        
        self.state = "IDLE"  # IDLE, SELECTING, SELECTED
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.current_rect = QRect()
        
        self.setup_ui()

    def setup_ui(self) -> None:
        """Create the control panel (hidden by default)."""
        self.panel = QFrame(self)
        self.panel.setObjectName("ControlPanel")
        self.panel.setStyleSheet("""
            QFrame#ControlPanel {
                background-color: rgba(30, 41, 59, 230);
                border-radius: 8px;
                border: 1px solid #334155;
            }
            QLabel {
                color: white;
                font-family: Arial;
                font-size: 12px;
            }
            QPushButton {
                background-color: #334155;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton#ConfirmBtn {
                background-color: #22C55E;
            }
            QPushButton#ConfirmBtn:hover {
                background-color: #16A34A;
            }
            QPushButton#CancelBtn {
                background-color: #EF4444;
            }
            QPushButton#CancelBtn:hover {
                background-color: #DC2626;
            }
        """)
        
        layout = QVBoxLayout(self.panel)
        
        self.info_label = QLabel("Info")
        layout.addWidget(self.info_label)
        
        btn_layout = QHBoxLayout()
        self.btn_confirm = QPushButton("✅ Konfirmasi")
        self.btn_confirm.setObjectName("ConfirmBtn")
        self.btn_full = QPushButton("🖥️ Layar Penuh")
        self.btn_cancel = QPushButton("❌ Batal")
        self.btn_cancel.setObjectName("CancelBtn")
        
        btn_layout.addWidget(self.btn_confirm)
        btn_layout.addWidget(self.btn_full)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        
        self.btn_confirm.clicked.connect(self.confirm_selection)
        self.btn_full.clicked.connect(self.select_fullscreen)
        self.btn_cancel.clicked.connect(self.cancel_selection)
        
        self.panel.hide()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.state = "SELECTING"
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.current_rect = QRect(self.start_point, self.end_point).normalized()
            self.panel.hide()
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.state == "SELECTING":
            self.end_point = event.pos()
            self.current_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.state == "SELECTING":
            self.end_point = event.pos()
            self.current_rect = QRect(self.start_point, self.end_point).normalized()
            
            if self.current_rect.width() > 10 and self.current_rect.height() > 10:
                self.state = "SELECTED"
                self.show_panel()
            else:
                self.state = "IDLE"
            self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_selection()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.state == "SELECTED":
                self.confirm_selection()
        else:
            super().keyPressEvent(event)

    def _get_device_info(self, w: int, h: int) -> dict:
        """Get device info from DeviceDetector."""
        return DeviceDetector.detect_device(w, h)

    def show_panel(self) -> None:
        """Show the confirmation panel below the selected area."""
        w, h = self.current_rect.width(), self.current_rect.height()
        device_info = self._get_device_info(w, h)
            
        emoji = "📱" if device_info.get('type', '') == 'smartphone' else "🖥️"
        info_text = (
            f"Perangkat: {emoji} {device_info.get('type', 'Unknown').title()} "
            f"({device_info.get('aspect_ratio', '?')})\n"
            f"Resolusi: {w} × {h} px\n"
            f"Rekomendasi FPS: {device_info.get('recommended_fps', 10)} fps"
        )
        self.info_label.setText(info_text)
        
        self.panel.adjustSize()
        
        # Position panel below rect or above if no space
        px = self.current_rect.center().x() - self.panel.width() // 2
        py = self.current_rect.bottom() + 10
        if py + self.panel.height() > self.height():
            py = self.current_rect.top() - self.panel.height() - 10
            
        # Keep inside screen bounds
        px = max(10, min(px, self.width() - self.panel.width() - 10))
        py = max(10, min(py, self.height() - self.panel.height() - 10))
        
        self.panel.move(px, py)
        self.panel.show()
        
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def select_fullscreen(self) -> None:
        """Select the entire primary screen."""
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.geometry()
            widget_geom = self.geometry()
            
            x = geom.x() - widget_geom.x()
            y = geom.y() - widget_geom.y()
            
            self.current_rect = QRect(x, y, geom.width(), geom.height())
            self.state = "SELECTED"
            self.show_panel()
            self.update()

    def confirm_selection(self) -> None:
        """Emit the selected ROI and close."""
        if self.state == "SELECTED":
            w, h = self.current_rect.width(), self.current_rect.height()
            device_info = self._get_device_info(w, h)
            
            # Convert to absolute screen coordinates
            abs_x = self.current_rect.x() + self.geometry().x()
            abs_y = self.current_rect.y() + self.geometry().y()
            
            self.roi_selected.emit(abs_x, abs_y, w, h, device_info)
            self.close()

    def cancel_selection(self) -> None:
        """Cancel selection and close."""
        self.roi_cancelled.emit()
        self.close()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dark overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 153))
        
        if self.state == "IDLE":
            text = "📐 Klik dan seret untuk memilih area pemantauan\nTekan ESC untuk batal"
            painter.setPen(Qt.GlobalColor.white)
            font = QFont("Arial", 16, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)
            
        elif self.state in ("SELECTING", "SELECTED"):
            # Clear the selected area
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.current_rect, Qt.GlobalColor.transparent)
            
            # Draw border
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor("#22C55E"), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.current_rect)
            
            # Draw dimensions while selecting
            if self.state == "SELECTING":
                dim_text = f"{self.current_rect.width()} × {self.current_rect.height()} px"
                painter.setPen(Qt.GlobalColor.white)
                font = QFont("Arial", 10, QFont.Weight.Bold)
                painter.setFont(font)
                
                fm = painter.fontMetrics()
                text_rect = fm.boundingRect(dim_text)
                
                bg_rect = QRect(
                    self.current_rect.center().x() - text_rect.width() // 2 - 5,
                    self.current_rect.bottom() + 5,
                    text_rect.width() + 10,
                    text_rect.height() + 4
                )
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(0, 0, 0, 150))
                painter.drawRoundedRect(bg_rect, 4, 4)
                
                painter.setPen(Qt.GlobalColor.white)
                painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, dim_text)
