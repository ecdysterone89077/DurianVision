from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget

from ui.styles.theme import Theme


class OverlayWindow(QWidget):
    """Transparent click-through overlay for displaying bounding boxes with modern visuals."""
    
    def __init__(self):
        super().__init__()
        
        # Frameless, always on top, click-through
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        # Cover all screens
        screens = QApplication.screens()
        if screens:
            rect = QRect()
            for screen in screens:
                rect = rect.united(screen.geometry())
            self.setGeometry(rect)
            
        self.detections: list[dict] = []
        self.fps: float = 0.0
        self.device_type: str = "Desktop"
        self.object_count: int = 0
        self.roi_offset_x: int = 0
        self.roi_offset_y: int = 0
        
        self.session_duration: str = "00:00:00"
        
        # Configurable display settings
        self.show_boxes: bool = True
        self.show_labels: bool = True
        self.show_confidence: bool = True
        self.line_thickness: int = 2
        self.font_size: int = 10
        self.show_mini_status: bool = True

    def update_detections(self, detections: list[dict]) -> None:
        """Update the list of detections to draw."""
        self.detections = detections
        self.object_count = len(detections)
        self.update()

    def update_stats(self, fps: float, device_type: str, count: int) -> None:
        """Update statistics display."""
        self.fps = fps
        self.device_type = device_type
        self.object_count = count
        self.update()

    def set_roi_offset(self, x: int, y: int) -> None:
        """Set ROI offset for coordinate mapping."""
        self.roi_offset_x = x
        self.roi_offset_y = y
        self.update()

    def update_display_settings(self, settings: dict) -> None:
        """Update display settings from config."""
        self.show_boxes = settings.get('show_boxes', True)
        self.show_labels = settings.get('show_labels', True)
        self.show_confidence = settings.get('show_confidence', True)
        self.line_thickness = settings.get('line_thickness', 2)
        self.font_size = settings.get('font_size', 10)
        self.show_mini_status = settings.get('show_mini_status', True)
        self.update()

    def show_overlay(self) -> None:
        """Show the overlay window."""
        self.show()

    def hide_overlay(self) -> None:
        """Hide the overlay window."""
        self.hide()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.show_boxes:
            return

        # Pre-calculate class counts for the badges
        class_counts = {}
        for det in self.detections:
            cls_name = det.get("class_name", "Lainnya")
            class_counts[cls_name] = class_counts.get(cls_name, 0) + 1

        # Draw ROI region border if detections exist
        if self.detections:
            min_x = float('inf')
            min_y = float('inf')
            max_x = float('-inf')
            max_y = float('-inf')
            
            for det in self.detections:
                x1 = det.get("x1", 0) + self.roi_offset_x - self.geometry().x()
                y1 = det.get("y1", 0) + self.roi_offset_y - self.geometry().y()
                x2 = det.get("x2", 0) + self.roi_offset_x - self.geometry().x()
                y2 = det.get("y2", 0) + self.roi_offset_y - self.geometry().y()
                min_x = min(min_x, x1)
                min_y = min(min_y, y1)
                max_x = max(max_x, x2)
                max_y = max(max_y, y2)
            
            roi_pad = 15
            roi_rect = QRect(int(min_x) - roi_pad, int(min_y) - roi_pad, 
                             int(max_x - min_x) + roi_pad * 2, int(max_y - min_y) + roi_pad * 2)
            
            roi_pen = QPen(QColor(46, 204, 113, 150), 2, Qt.PenStyle.DashLine)
            painter.setPen(roi_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(roi_rect, 8, 8)

        # Draw bounding boxes and labels
        for det in self.detections:
            cls_name = det.get("class_name", "Lainnya")
            conf = det.get("confidence", 0.0)
            x1 = det.get("x1", 0) + self.roi_offset_x - self.geometry().x()
            y1 = det.get("y1", 0) + self.roi_offset_y - self.geometry().y()
            x2 = det.get("x2", 0) + self.roi_offset_x - self.geometry().x()
            y2 = det.get("y2", 0) + self.roi_offset_y - self.geometry().y()
            
            color_str = Theme.get_variety_color(cls_name)
            base_color = QColor(color_str)
            
            # Confidence color gradient (intensity varies by confidence)
            alpha_val = int(255 * (0.4 + 0.6 * conf))
            bbox_color = QColor(base_color)
            bbox_color.setAlpha(alpha_val)
            
            # Glow effect
            glow_color = QColor(base_color)
            glow_color.setAlpha(int(alpha_val * 0.3))
            painter.setPen(QPen(glow_color, self.line_thickness + 4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(int(x1) - 2, int(y1) - 2, int(x2 - x1) + 4, int(y2 - y1) + 4, 8, 8)
            
            # Main Bounding box
            pen = QPen(bbox_color, self.line_thickness)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(int(x1), int(y1), int(x2 - x1), int(y2 - y1), 6, 6)
            
            # Label
            if self.show_labels:
                label_parts = [cls_name]
                if self.show_confidence:
                    label_parts.append(f"{conf*100:.1f}%")
                label_text = " ".join(label_parts)
                
                font = QFont("Arial", self.font_size + 1, QFont.Weight.Bold)
                painter.setFont(font)
                fm = painter.fontMetrics()
                text_rect = fm.boundingRect(label_text)
                
                pad_x, pad_y = 8, 4
                bg_rect = QRect(
                    int(x1), int(y1) - text_rect.height() - pad_y * 2 - 4, 
                    text_rect.width() + pad_x * 2, text_rect.height() + pad_y * 2
                )
                
                # Keep label on screen
                if bg_rect.top() < 0:
                    bg_rect.moveTop(int(y2) + 4)
                
                bg_color = QColor(base_color)
                bg_color.setAlpha(200)
                painter.setBrush(QBrush(bg_color))
                painter.setPen(Qt.PenStyle.NoPen)
                
                # Pill-shaped background
                radius = bg_rect.height() / 2.0
                painter.drawRoundedRect(bg_rect, radius, radius)
                
                painter.setPen(Qt.GlobalColor.white)
                painter.drawText(
                    bg_rect,
                    Qt.AlignmentFlag.AlignCenter, label_text
                )
                
            # Detection count badge (bottom-right of bbox)
            count_text = str(class_counts.get(cls_name, 1))
            badge_font = QFont("Arial", max(8, self.font_size - 1), QFont.Weight.Bold)
            painter.setFont(badge_font)
            fm_badge = painter.fontMetrics()
            badge_rect = fm_badge.boundingRect(count_text)
            
            badge_size = max(badge_rect.width(), badge_rect.height()) + 8
            badge_bg_rect = QRect(int(x2) - badge_size + 4, int(y2) - badge_size + 4, badge_size, badge_size)
            
            painter.setBrush(QBrush(QColor(40, 40, 40, 220)))
            painter.setPen(QPen(base_color, 1))
            painter.drawEllipse(badge_bg_rect)
            
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(badge_bg_rect, Qt.AlignmentFlag.AlignCenter, count_text)

        # Modern glassmorphism status panel
        if self.show_mini_status and "smartphone" not in self.device_type.lower():
            panel_text = f"DurianVision | FPS: {self.fps:.1f} | 🎯 {self.object_count} objects | ⏱ {self.session_duration}"
            font = QFont("Arial", 12, QFont.Weight.Bold)
            painter.setFont(font)
            fm = painter.fontMetrics()
            text_rect = fm.boundingRect(panel_text)
            
            margin = 15
            padding_x = 20
            padding_y = 12
            
            # Additional space for the icon/dot
            dot_size = 10
            dot_spacing = 8
            
            panel_w = text_rect.width() + padding_x * 2 + dot_size + dot_spacing
            panel_h = text_rect.height() + padding_y * 2
            
            panel_x = self.width() - panel_w - margin
            panel_y = margin
            
            panel_rect = QRect(panel_x, panel_y, panel_w, panel_h)
            
            # Glass background
            painter.setBrush(QColor(20, 20, 25, 180))
            painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
            painter.drawRoundedRect(panel_rect, 10, 10)
            
            # Status Dot
            dot_color = QColor(46, 204, 113) if self.object_count > 0 else QColor(231, 76, 60)
            painter.setBrush(QBrush(dot_color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            dot_x = panel_x + padding_x
            dot_y = panel_y + (panel_h - dot_size) // 2
            painter.drawEllipse(dot_x, dot_y, dot_size, dot_size)
            
            # Text
            text_draw_rect = QRect(dot_x + dot_size + dot_spacing, panel_y, text_rect.width(), panel_h)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(text_draw_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, panel_text)
