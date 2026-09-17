"""
Main coordinator application for DurianVision.
Connects UI components with core processing modules.
"""
import os
import threading
import time
import winsound
from datetime import datetime

import cv2
import numpy as np
import psutil
from PyQt6.QtCore import QObject, QTimer, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication

from core.config_manager import ConfigManager
from core.detection_worker import DetectionWorker
from core.device_detector import DeviceDetector
from core.global_hotkeys import GlobalHotkeys
from core.log_manager import LogManager
from core.paths import get_meipass_dir, get_user_data_dir, get_user_media_dir
from core.screen_capture import ScreenCapture
from core.snapshot_manager import SnapshotManager
from core.yolo_engine import YOLOEngine
from ui.control_panel import ControlPanel
from ui.overlay_window import OverlayWindow
from ui.roi_selector import RoISelectorWindow
from ui.styles.theme import Theme
from ui.tray_icon import TrayIcon


class DurianVisionApp(QObject):
    """Main application coordinator."""
    
    def __init__(self, app_instance: QApplication, autostart: bool = False, minimize: bool = False):
        super().__init__()
        self.app = app_instance
        self.app.setQuitOnLastWindowClosed(False)  # Keep running in system tray
        
        # State
        self.is_detecting = False
        self.current_device_info = {}
        self.last_snapshot_time = 0
        self.auto_capture_settings = {'enabled': False, 'threshold': 85, 'interval': 3}
        self._last_ui_update = 0
        self._pending_autostart = False
        self._started_minimized = minimize
        
        self.session_start_time = None
        self.session_frames = 0
        self.session_distribution = {}
        
        appdata_dir = get_user_data_dir()
        
        # 1. Initialize Core Modules
        config_path = os.path.join(appdata_dir, 'config', 'default_config.json')
        self.config = ConfigManager.get_instance(config_path)
        self.hotkeys = GlobalHotkeys(self.config.get_section('hotkeys'))
        
        # Initialize YOLO engine with two-stage config
        two_stage_cfg = self.config.get_section('two_stage')
        
        # We assume models are in the MEIPASS directory (packaged with pyinstaller)
        base_dir = str(get_meipass_dir())
        yolo_path = os.path.join(base_dir, 'best.pt')
        classifier_path = os.path.join(base_dir, two_stage_cfg.get('classifier_path', 'classifier.pt'))
        
        self.yolo = YOLOEngine(
            yolo_path,
            classifier_path=classifier_path,
            two_stage_enabled=two_stage_cfg.get('enabled', True),
            classifier_min_confidence=two_stage_cfg.get('min_confidence', 0.4)
        )
        self.capture = ScreenCapture()
        
        # Worker gets injected dependencies
        self.worker = DetectionWorker(self.capture, self.yolo, self.config.config)
        
        # Setup Snapshots Directory (Documents for user-friendly access)
        safe_snapshots_dir = get_user_media_dir()
        cfg_snapshot_dir = self.config.get('snapshot', 'save_dir', safe_snapshots_dir)
        if not os.path.isabs(cfg_snapshot_dir) and cfg_snapshot_dir == 'snapshots':
            # Override legacy relative 'snapshots' to user media dir
            cfg_snapshot_dir = safe_snapshots_dir
        elif not os.path.isabs(cfg_snapshot_dir):
            cfg_snapshot_dir = os.path.join(appdata_dir, cfg_snapshot_dir)
            
        self.snapshot_mgr = SnapshotManager(
            save_dir=cfg_snapshot_dir, 
            variety_colors=self.config.get_variety_colors()
        )
        self.snapshot_mgr.snapshot_saved.connect(self._on_snapshot_saved)
        
        # Setup Logs Directory (AppData for hidden logs)
        safe_logs_dir = os.path.join(appdata_dir, 'logs')
        cfg_log_dir = self.config.get('log', 'save_dir', safe_logs_dir)
        if not os.path.isabs(cfg_log_dir):
            cfg_log_dir = os.path.join(appdata_dir, cfg_log_dir)
            
        self.log_mgr = LogManager(cfg_log_dir)
        
        # Sound Settings
        self._sound_enabled = self.config.get('audio', 'enabled', True)
        self._last_sound_time = 0
        
        # 2. Initialize UI Components
        self.tray = TrayIcon()
        self.control_panel = ControlPanel()
        self.overlay = OverlayWindow()
        self.roi_selector = RoISelectorWindow()
        
        # Initial config sync to UI
        self.control_panel.settings_tab.load_settings(self.config.config)
        self.overlay.update_display_settings(self.config.get_section('overlay'))
        self.control_panel.snapshot_tab.gallery.load_from_directory(self.snapshot_mgr.save_dir)
        
        # Sync confidence slider with config
        initial_conf = int(self.config.get('detection', 'confidence_threshold', 0.5) * 100)
        self.control_panel.detection_tab.conf_slider.set_value(initial_conf)
        
        # 3. Connect Signals
        self._connect_signals()
        
        # 4. Start background services
        self.hotkeys.start()
        self.tray.show()
        
        self._restore_saved_roi()
        
        if not minimize:
            self.control_panel.show()
            
        if autostart:
            self._pending_autostart = True
            QTimer.singleShot(500, self.roi_selector.select_fullscreen)

    def _connect_signals(self) -> None:
        """Connect all signals between UI and Core."""
        
        # -- Tray Icon Signals --
        self.tray.panel_requested.connect(self._handle_show_panel)
        self.tray.start_requested.connect(self.start_detection)
        self.tray.stop_requested.connect(self.stop_detection)
        self.tray.roi_requested.connect(self._handle_select_roi)
        self.tray.snapshot_requested.connect(self._handle_manual_snapshot)
        self.tray.quit_requested.connect(self.quit_app)
        self.tray.fullscreen_requested.connect(self.roi_selector.select_fullscreen)
        self.tray.sound_toggled.connect(self._handle_sound_toggled)
        
        # -- Global Hotkey Signals --
        self.hotkeys.snapshot_triggered.connect(self._handle_manual_snapshot)
        self.hotkeys.toggle_detection_triggered.connect(self._handle_toggle_detection)
        self.hotkeys.select_roi_triggered.connect(self._handle_select_roi)
        self.hotkeys.hide_triggered.connect(self.control_panel.hide)
        
        # -- Control Panel: Detection Tab --
        dt = self.control_panel.detection_tab
        dt.start_requested.connect(self.start_detection)
        dt.stop_requested.connect(self.stop_detection)
        dt.roi_requested.connect(self._handle_select_roi)
        dt.fullscreen_requested.connect(self.roi_selector.select_fullscreen)
        dt.confidence_changed.connect(lambda v: self.worker.set_confidence(v / 100.0))
        
        # -- Control Panel: Performance Tab --
        pt = self.control_panel.performance_tab
        pt.fps_limit_changed.connect(self.worker.set_fps_limit)
        pt.model_changed.connect(self.yolo.load_model)
        pt.inference_size_changed.connect(self.worker.set_inference_size)
        pt.device_changed.connect(self.yolo.change_device)
        
        # -- Control Panel: Snapshot Tab --
        st = self.control_panel.snapshot_tab
        st.snapshot_requested.connect(self._handle_manual_snapshot)
        st.auto_settings_changed.connect(self._handle_auto_snapshot_settings)
        st.open_folder_requested.connect(self._open_snapshot_folder)
        
        # -- Control Panel: Log Tab --
        lt = self.control_panel.log_tab
        lt.export_csv_requested.connect(self._export_csv)
        lt.export_xlsx_requested.connect(self._export_xlsx)
        lt.clear_requested.connect(self.log_mgr.clear)
        lt.clear_requested.connect(lt.clear_logs)
        
        # -- Control Panel: Settings Tab --
        self.control_panel.settings_tab.settings_changed.connect(self._handle_settings_changed)
        
        # -- ROI Selector --
        # FIX: The crash occurred here previously because the signal emitted 5 args but the slot accepted 1
        self.roi_selector.roi_selected.connect(self._handle_roi_selected)
        self.roi_selector.roi_cancelled.connect(self._handle_roi_cancelled)
        
        # -- Detection Worker --
        self.worker.frame_processed.connect(self._handle_frame_processed)
        self.worker.error_occurred.connect(self._handle_worker_error)

    def _restore_saved_roi(self) -> None:
        w = self.config.get('roi', 'width', 0)
        if w > 0:
            x = self.config.get('roi', 'x', 0)
            y = self.config.get('roi', 'y', 0)
            h = self.config.get('roi', 'height', 0)
            device_info = DeviceDetector.detect_device(w, h)
            self._handle_roi_selected(x, y, w, h, device_info)

    @pyqtSlot(int, int, int, int, dict)
    def _handle_roi_selected(self, x: int, y: int, w: int, h: int, device_info: dict) -> None:
        """Handle area selection from ROI tool."""
        mode = self.config.get('device_detection', 'mode', 'auto')
        if mode != 'auto':
            device_info = DeviceDetector.detect_device(w, h, mode)

        self.config.set('roi', 'x', x)
        self.config.set('roi', 'y', y)
        self.config.set('roi', 'width', w)
        self.config.set('roi', 'height', h)
        
        self.capture.set_region(x, y, w, h)
        self.overlay.set_roi_offset(x, y)
        self.current_device_info = device_info
        
        # Update UI displays
        dt = self.control_panel.detection_tab
        dt.update_area_info(x, y, w, h)
        dt.update_status(self.is_detecting, device_info.get('type', 'Unknown').title())
        
        pt = self.control_panel.performance_tab
        pt.update_device_info(device_info)
        
        # Apply recommended settings automatically
        rec_fps = device_info.get('recommended_fps', 15)
        rec_size = device_info.get('recommended_inference_size', 416)
        
        pt.fps_slider.set_value(rec_fps)
        self.worker.set_fps_limit(rec_fps)
        
        idx = pt.size_combo.findText(f"{rec_size}x{rec_size}")
        if idx >= 0:
            pt.size_combo.setCurrentIndex(idx)
            
        # Update overlay styling from device recommendations
        overlay_settings = self.config.get_section('overlay')
        overlay_settings['line_thickness'] = device_info.get('line_thickness', 2)
        overlay_settings['font_size'] = device_info.get('font_size', 12)
        overlay_settings['show_mini_status'] = device_info.get('show_mini_status', True)
        self.overlay.update_display_settings(overlay_settings)

        self.control_panel.update_status_bar({'area': f"{w}×{h}"})
        if not self._started_minimized:
            self.control_panel.show()
        if self._pending_autostart:
            self._pending_autostart = False
            QTimer.singleShot(200, self.start_detection)

    @pyqtSlot()
    def _handle_roi_cancelled(self) -> None:
        """Batal memilih area — kembalikan panel kontrol."""
        self._pending_autostart = False
        if not self._started_minimized:
            self.control_panel.show()

    def start_detection(self) -> None:
        """Start the detection worker and overlay."""
        if not self.yolo.is_loaded:
            # Graceful handling when model is missing
            self.control_panel.detection_tab.device_type_lbl.setText("Error: Model belum dimuat!")
            self.control_panel.detection_tab.device_type_lbl.setStyleSheet("color: #EF4444; font-weight: bold;")
            return
            
        if self.is_detecting:
            return

        # Fallback: belum pernah pilih ROI -> pakai layar utama penuh
        if self.config.get('roi', 'width', 0) <= 0:
            screen = QApplication.primaryScreen()
            if screen is not None:
                geom = screen.geometry()
                device_info = DeviceDetector.detect_device(
                    geom.width(), geom.height(),
                    self.config.get('device_detection', 'mode', 'auto')
                )
                self._handle_roi_selected(geom.x(), geom.y(), geom.width(), geom.height(), device_info)

        self.is_detecting = True
        self.session_start_time = time.time()
        self.session_frames = 0
        self.session_distribution = {}
        self.tray.set_status(TrayIcon.Status.DETECTING)
        
        dt = self.control_panel.detection_tab
        device_str = self.current_device_info.get('type', 'Unknown').title()
        dt.update_status(True, device_str)
        
        self.control_panel.update_status_bar({
            'status': 'detecting',
            'device': self.yolo.device.upper(),
            'pipeline': self.yolo.pipeline_status
        })
        
        self.control_panel.showMinimized()
        
        self.overlay.show_overlay()
        self.worker.start()

    def stop_detection(self) -> None:
        """Stop the detection worker and overlay."""
        if not self.is_detecting:
            return
            
        self.is_detecting = False
        self.tray.set_status(TrayIcon.Status.IDLE)
        
        dt = self.control_panel.detection_tab
        device_str = self.current_device_info.get('type', 'Unknown').title()
        dt.update_status(False, device_str)
        
        self.control_panel.update_status_bar({'status': 'idle'})
        
        self.worker.stop()
        self.overlay.hide_overlay()

    @pyqtSlot()
    def _handle_toggle_detection(self) -> None:
        if self.is_detecting:
            self.stop_detection()
        else:
            self.start_detection()

    @pyqtSlot()
    def _handle_show_panel(self) -> None:
        self.control_panel.show()
        self.control_panel.raise_()
        self.control_panel.activateWindow()

    @pyqtSlot()
    def _handle_select_roi(self) -> None:
        # Phase 1.3: Prevent Select ROI while detecting
        if self.is_detecting:
            self.stop_detection()
            
        self.control_panel.hide()
        self.roi_selector.show()

    def _play_detection_sound(self):
        volume = float(self.config.get('audio', 'volume', 0.5))
        if volume <= 0:
            return

        def play(vol: float) -> None:
            import math
            import struct
            rate, duration, freq = 22050, 0.15, 1000
            n = int(rate * duration)
            amp = int(32767 * vol)
            samples = struct.pack(
                f'<{n}h',
                *[int(amp * math.sin(2 * math.pi * freq * i / rate)) for i in range(n)]
            )
            header = (
                b'RIFF' + struct.pack('<I', 36 + len(samples)) + b'WAVEfmt ' +
                struct.pack('<IHHIIHH', 16, 1, 1, rate, rate * 2, 2, 16) +
                b'data' + struct.pack('<I', len(samples))
            )
            winsound.PlaySound(header + samples, winsound.SND_MEMORY)

        threading.Thread(target=play, args=(volume,), daemon=True).start()

    @pyqtSlot(bool)
    def _handle_sound_toggled(self, enabled: bool) -> None:
        """Handle sound toggle from tray menu."""
        self._sound_enabled = enabled

    @pyqtSlot(list, float, np.ndarray)
    def _handle_frame_processed(self, detections: list[dict], fps: float, frame: np.ndarray) -> None:
        """Process results from the background worker."""
        if not self.is_detecting:
            return
            
        # Sound notification
        if detections and self._sound_enabled:
            current_time = time.time()
            if current_time - self._last_sound_time > 2.0:
                self._play_detection_sound()
                self._last_sound_time = current_time

        # Session duration tracking for overlay
        if hasattr(self.overlay, 'session_duration'):
            duration_s = int(time.time() - self.session_start_time) if self.session_start_time else 0
            hrs, rem = divmod(duration_s, 3600)
            mins, secs = divmod(rem, 60)
            self.overlay.session_duration = f"{hrs:02d}:{mins:02d}:{secs:02d}"

        # Live tray tooltip with pipeline status
        pipeline_tag = "2-Stage" if self.yolo.is_two_stage else "YOLO"
        self.tray.setToolTip(f"DurianVision [{pipeline_tag}] | FPS: {fps:.1f} | 🍈 {len(detections)} objek")

        # 1. Group detections by class for UI counting
        counts = {}
        for det in detections:
            name = det.get('class_name', 'Lainnya')
            if name not in counts:
                counts[name] = {'count': 0, 'max_conf': 0.0, 'color': Theme.get_variety_color(name)}
            counts[name]['count'] += 1
            counts[name]['max_conf'] = max(counts[name]['max_conf'], det.get('confidence', 0.0))
            
        # Format for DetectionList widget
        det_list_data = [
            {'name': name, 'count': data['count'], 'conf': data['max_conf'], 'color': data['color']}
            for name, data in counts.items()
        ]
        
        self.session_frames += 1
        for name, data in counts.items():
            self.session_distribution[name] = self.session_distribution.get(name, 0) + data['count']
        
        # 2. Update Overlay
        self.overlay.update_detections(detections)
        self.overlay.update_stats(fps, self.current_device_info.get('type', 'Unknown').title(), len(detections))
        
        # 3. Update Control Panel UI (limit rate to avoid UI lag)
        current_time = time.time()
        if hasattr(self, '_last_ui_update'):
            if current_time - self._last_ui_update > 0.1:  # Max 10fps UI updates
                self._update_ui_stats(det_list_data, fps, frame)
                self._update_session_summary()
                self._last_ui_update = current_time
        else:
            self._update_ui_stats(det_list_data, fps, frame)
            self._update_session_summary()
            self._last_ui_update = current_time
            
        # 4. Handle logging
        timestamp = datetime.now().strftime('%H:%M:%S')
        for det_data in det_list_data:
            self.log_mgr.add_entry(timestamp, det_data['name'], det_data['conf'] * 100, det_data['count'])
            self.control_panel.log_tab.add_log_entry(timestamp, det_data['name'], det_data['conf'] * 100, det_data['count'])
            
        # 5. Handle Auto Snapshot
        self._check_auto_snapshot(frame, detections, counts)

    def _update_ui_stats(self, det_list_data: list, fps: float, frame: np.ndarray) -> None:
        """Update tabs with real-time stats."""
        # Detection Tab
        self.control_panel.detection_tab.update_detections(det_list_data)
        
        # Generate thumbnail for preview
        if frame is not None and frame.size > 0:
            thumb = cv2.resize(frame, (160, 120))
            h, w, c = thumb.shape
            bytes_per_line = 3 * w
            q_img = QImage(thumb.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
            self.control_panel.detection_tab.update_preview(QPixmap.fromImage(q_img))
            
        # Performance Tab
        # Mock RAM/CPU stats for UI display purpose, since psutil can be heavy
        cpu_pct = psutil.cpu_percent()
        ram_pct = psutil.virtual_memory().percent
        self.control_panel.performance_tab.update_stats(
            fps=fps,
            inference_ms=self.yolo.last_inference_ms,
            cpu=int(cpu_pct),
            gpu=0,  # Changed from mock 50 to 0
            ram=int(ram_pct)
        )
        
        # Status bar
        self.control_panel.update_status_bar({'fps': fps})

    def _update_session_summary(self) -> None:
        if not self.session_start_time:
            return
        duration_s = int(time.time() - self.session_start_time)
        hrs, rem = divmod(duration_s, 3600)
        mins, secs = divmod(rem, 60)
        duration_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        
        total_dets = sum(self.session_distribution.values())
        dist_dict = {}
        for name, count in self.session_distribution.items():
            pct = (count / total_dets * 100) if total_dets > 0 else 0
            dist_dict[name] = {'pct': pct, 'color': Theme.get_variety_color(name)}
            
        device = self.current_device_info.get('type', 'Unknown').title()
        self.control_panel.log_tab.update_session_summary(
            duration_str, self.session_frames, device, dist_dict
        )

    def _check_auto_snapshot(self, frame: np.ndarray, detections: list, counts: dict) -> None:
        """Check if conditions are met for an automatic snapshot."""
        if not self.auto_capture_settings['enabled'] or not detections:
            return
            
        current_time = time.time()
        interval = self.auto_capture_settings['interval']
        
        # Check cooldown
        if current_time - self.last_snapshot_time < interval:
            return
            
        # Check threshold
        threshold = self.auto_capture_settings['threshold'] / 100.0
        best_conf = max(data['max_conf'] for data in counts.values())
        
        if best_conf >= threshold:
            self._take_snapshot(frame, detections)
            self.last_snapshot_time = current_time

    @pyqtSlot()
    def _handle_manual_snapshot(self) -> None:
        if not self.is_detecting:
            return
        # Get the latest frame and detections from overlay state
        frame = self.capture.capture_frame()
        if frame is not None:
            self._take_snapshot(frame, self.overlay.detections)

    def _take_snapshot(self, frame: np.ndarray, detections: list) -> None:
        """Save snapshot async to prevent UI freeze."""
        overlay_cfg = self.config.get_section('overlay')
        self.snapshot_mgr.save_snapshot_async(
            frame, detections, 
            metadata={'device_type': self.current_device_info.get('type', '')},
            line_thickness=overlay_cfg.get('line_thickness', 2),
            font_scale=overlay_cfg.get('font_size', 12) / 20.0
        )
        
    @pyqtSlot(str, list)
    def _on_snapshot_saved(self, filepath: str, detections: list) -> None:
        """Update gallery UI after snapshot is saved in background."""
        if filepath and os.path.exists(filepath):
            # Update Gallery
            best_det = None
            if detections:
                best_det = max(detections, key=lambda d: d.get('confidence', 0))
                
            variety = best_det.get('class_name', 'Unknown') if best_det else 'Unknown'
            conf = f"{best_det.get('confidence', 0)*100:.1f}%" if best_det else "0%"
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            pixmap = QPixmap(filepath)
            
            # Show in control panel gallery
            self.control_panel.snapshot_tab.add_snapshot(pixmap, variety, conf, timestamp)
            
            # Show toast notification
            self.overlay.show_toast(f"Snapshot tersimpan: {os.path.basename(filepath)}")

    @pyqtSlot(dict)
    def _handle_auto_snapshot_settings(self, settings: dict) -> None:
        self.auto_capture_settings = settings

    @pyqtSlot(dict)
    def _handle_settings_changed(self, settings: dict) -> None:
        """Save settings and apply them to components."""
        for section, values in settings.items():
            for key, val in values.items():
                self.config.set(section, key, val, save_now=False)
        self.config.save()
        
        self.overlay.update_display_settings(settings.get('overlay', {}))

        snapshot_settings = settings.get('snapshot')
        if snapshot_settings is not None:
            self.snapshot_mgr.save_dir = self._resolve_dir(
                snapshot_settings.get('save_dir', ''), get_user_media_dir()
            )
        log_settings = settings.get('log')
        if log_settings is not None:
            self.log_mgr.save_dir = self._resolve_dir(
                log_settings.get('save_dir', ''), os.path.join(get_user_data_dir(), 'logs')
            )
        audio = settings.get('audio')
        if audio is not None:
            self._sound_enabled = bool(audio.get('enabled', True))
            self.tray.sound_enabled = self._sound_enabled
            self.tray.sound_action.setText(
                '🔇 Matikan Suara' if self._sound_enabled else '🔊 Aktifkan Suara'
            )
        hotkeys = settings.get('hotkeys')
        if hotkeys:
            self.hotkeys.update_hotkeys(hotkeys)

    @staticmethod
    def _resolve_dir(path: str, default_dir: str) -> str:
        """Ubah path folder (absolut / relatif / legacy) menjadi folder absolut yang valid."""
        if not path:
            resolved = default_dir
        elif os.path.isabs(path):
            resolved = path
        elif path == 'snapshots':
            resolved = default_dir
        else:
            resolved = os.path.join(get_user_data_dir(), path)
        os.makedirs(resolved, exist_ok=True)
        return resolved

    @pyqtSlot(str)
    def _handle_worker_error(self, err_msg: str) -> None:
        """Handle errors from background worker."""
        print(f"[Worker Error] {err_msg}")
        self.stop_detection()
        self.tray.set_status(TrayIcon.Status.ERROR)
        self.control_panel.update_status_bar({'status': 'error'})
        self.control_panel.detection_tab.device_type_lbl.setText(f"Error: {err_msg}")
        self.control_panel.detection_tab.device_type_lbl.setStyleSheet("color: #EF4444;")

    @pyqtSlot()
    def _export_csv(self) -> None:
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self.control_panel, "Ekspor CSV", "", "CSV Files (*.csv)")
        if path:
            self.log_mgr.export_csv(path)

    @pyqtSlot()
    def _export_xlsx(self) -> None:
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self.control_panel, "Ekspor XLSX", "", "Excel Files (*.xlsx)")
        if path:
            self.log_mgr.export_xlsx(path)

    @pyqtSlot()
    def _open_snapshot_folder(self) -> None:
        import platform
        import subprocess
        path = os.path.abspath(self.snapshot_mgr.save_dir)
        os.makedirs(path, exist_ok=True)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    @pyqtSlot()
    def quit_app(self) -> None:
        """Clean up and exit application."""
        self.stop_detection()
        self.hotkeys.stop()
        self.snapshot_mgr.wait_for_workers()
        self.tray.hide()
        self.config.save()
        QApplication.quit()
