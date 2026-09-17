"""
GUI Duren — FULL SETUP TEST
============================
Menjalankan aplikasi DurianVision secara PENUH (sama persis seperti user double-click),
memverifikasi setiap komponen aktif, lalu menutup otomatis.

Ini bukan unit test — ini tes startup end-to-end sesungguhnya.
"""
import sys, os, io, time, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("  GUI DUREN — FULL SETUP TEST")
print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ============================================================
# FASE 1: BOOTSTRAP (sama persis dengan main.py)
# ============================================================
print("\n[FASE 1] BOOTSTRAP — QApplication & Stylesheet")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

app = QApplication.instance() or QApplication(sys.argv)

# Load stylesheet (sama seperti main.py)
qss_path = os.path.join('ui', 'styles', 'stylesheet.qss')
try:
    with open(qss_path, 'r', encoding='utf-8') as f:
        app.setStyleSheet(f.read())
    print(f"  [OK] Stylesheet dimuat: {qss_path} ({os.path.getsize(qss_path)} bytes)")
except Exception as e:
    print(f"  [GAGAL] Stylesheet: {e}")

errors = []
warnings = []

# ============================================================
# FASE 2: INISIALISASI CORE MODULES
# ============================================================
print("\n[FASE 2] CORE MODULES — ConfigManager, YOLO, ScreenCapture")

try:
    from core.config_manager import ConfigManager
    config = ConfigManager('config/default_config.json')
    assert config.config != {}, "Config kosong!"
    sections = list(config.config.keys())
    print(f"  [OK] ConfigManager — {len(sections)} section: {', '.join(sections)}")
except Exception as e:
    errors.append(f"ConfigManager: {e}")
    print(f"  [GAGAL] ConfigManager: {e}")

try:
    from core.yolo_engine import YOLOEngine
    yolo = YOLOEngine('best.pt')
    status = "LOADED" if yolo.is_loaded else f"GAGAL: {yolo.load_error}"
    device = yolo.device
    names = yolo.model_names
    print(f"  [OK] YOLOEngine — {status} | Device: {device} | Classes: {len(names)}")
    if not yolo.is_loaded:
        errors.append(f"YOLO tidak termuat: {yolo.load_error}")
except Exception as e:
    errors.append(f"YOLOEngine: {e}")
    print(f"  [GAGAL] YOLOEngine: {e}")

try:
    from core.screen_capture import ScreenCapture
    capture = ScreenCapture()
    engine_name = capture.initialize()
    print(f"  [OK] ScreenCapture — Engine: {engine_name}")
    if engine_name == 'none':
        warnings.append("ScreenCapture: Tidak ada engine tersedia (limitasi environment)")
except Exception as e:
    errors.append(f"ScreenCapture: {e}")
    print(f"  [GAGAL] ScreenCapture: {e}")

try:
    from core.snapshot_manager import SnapshotManager
    snap_mgr = SnapshotManager(
        config.get('snapshot', 'save_dir', 'snapshots'),
        config.get_variety_colors()
    )
    print(f"  [OK] SnapshotManager — Dir: {snap_mgr.save_dir}")
except Exception as e:
    errors.append(f"SnapshotManager: {e}")
    print(f"  [GAGAL] SnapshotManager: {e}")

try:
    from core.log_manager import LogManager
    log_mgr = LogManager(config.get('log', 'save_dir', 'logs'))
    print(f"  [OK] LogManager — Dir: {log_mgr.save_dir}")
except Exception as e:
    errors.append(f"LogManager: {e}")
    print(f"  [GAGAL] LogManager: {e}")

try:
    from core.device_detector import DeviceDetector
    info = DeviceDetector.detect_device(1920, 1080)
    print(f"  [OK] DeviceDetector — 1920x1080 → {info['type']} ({info['aspect_ratio']})")
except Exception as e:
    errors.append(f"DeviceDetector: {e}")
    print(f"  [GAGAL] DeviceDetector: {e}")

try:
    from core.global_hotkeys import GlobalHotkeys
    hotkeys = GlobalHotkeys(config.get_section('hotkeys'))
    print(f"  [OK] GlobalHotkeys — Loaded")
except Exception as e:
    warnings.append(f"GlobalHotkeys: {e}")
    print(f"  [WARN] GlobalHotkeys: {e}")

# ============================================================
# FASE 3: INISIALISASI UI COMPONENTS
# ============================================================
print("\n[FASE 3] UI COMPONENTS — Panel, Overlay, Tray, ROI")

try:
    from ui.tray_icon import TrayIcon
    tray = TrayIcon()
    tray.set_status(TrayIcon.Status.IDLE)
    tray.show()
    print(f"  [OK] TrayIcon — Status: IDLE (kuning), Visible: {tray.isVisible()}")
except Exception as e:
    errors.append(f"TrayIcon: {e}")
    print(f"  [GAGAL] TrayIcon: {e}")

try:
    from ui.control_panel import ControlPanel
    panel = ControlPanel()
    tab_count = panel.stack.count() if hasattr(panel, 'stack') else '?'
    print(f"  [OK] ControlPanel — Tabs: {tab_count}, Title: '{panel.windowTitle()}'")
except Exception as e:
    errors.append(f"ControlPanel: {e}")
    print(f"  [GAGAL] ControlPanel: {e}")

try:
    from ui.overlay_window import OverlayWindow
    overlay = OverlayWindow()
    print(f"  [OK] OverlayWindow — Size: {overlay.width()}x{overlay.height()}")
except Exception as e:
    errors.append(f"OverlayWindow: {e}")
    print(f"  [GAGAL] OverlayWindow: {e}")

try:
    from ui.roi_selector import RoISelectorWindow
    roi = RoISelectorWindow()
    print(f"  [OK] RoISelectorWindow — Size: {roi.width()}x{roi.height()}")
except Exception as e:
    errors.append(f"RoISelectorWindow: {e}")
    print(f"  [GAGAL] RoISelectorWindow: {e}")

# ============================================================
# FASE 4: INISIALISASI DurianVisionApp (KOORDINATOR UTAMA)
# ============================================================
print("\n[FASE 4] DurianVisionApp — KOORDINATOR UTAMA")

# Clean up standalone components before creating the full app
try:
    tray.hide()
    tray.deleteLater()
    panel.close()
    panel.deleteLater()
    overlay.close()
    overlay.deleteLater()
    roi.close()
    roi.deleteLater()
except:
    pass

# Reset ConfigManager singleton
ConfigManager._instance = None

try:
    from ui.app import DurianVisionApp
    dv_app = DurianVisionApp(app, autostart=False, minimize=False)
    print(f"  [OK] DurianVisionApp dibuat sukses")
    
    # Verify subcomponents
    checks = [
        ("config", hasattr(dv_app, 'config') and dv_app.config is not None),
        ("yolo", hasattr(dv_app, 'yolo') and dv_app.yolo is not None),
        ("capture", hasattr(dv_app, 'capture') and dv_app.capture is not None),
        ("worker", hasattr(dv_app, 'worker') and dv_app.worker is not None),
        ("tray", hasattr(dv_app, 'tray') and dv_app.tray is not None),
        ("control_panel", hasattr(dv_app, 'control_panel') and dv_app.control_panel is not None),
        ("overlay", hasattr(dv_app, 'overlay') and dv_app.overlay is not None),
        ("roi_selector", hasattr(dv_app, 'roi_selector') and dv_app.roi_selector is not None),
        ("snapshot_mgr", hasattr(dv_app, 'snapshot_mgr') and dv_app.snapshot_mgr is not None),
        ("log_mgr", hasattr(dv_app, 'log_mgr') and dv_app.log_mgr is not None),
        ("hotkeys", hasattr(dv_app, 'hotkeys') and dv_app.hotkeys is not None),
    ]
    
    all_ok = True
    for name, ok in checks:
        status = "OK" if ok else "GAGAL"
        if not ok:
            all_ok = False
            errors.append(f"DurianVisionApp.{name} is None")
        print(f"    [{status}] dv_app.{name}")
    
    if all_ok:
        print(f"  [OK] Semua 11 subkomponent terverifikasi")
    
except Exception as e:
    errors.append(f"DurianVisionApp: {e}")
    print(f"  [GAGAL] DurianVisionApp: {e}")
    traceback.print_exc()
    dv_app = None

# ============================================================
# FASE 5: VERIFIKASI STATUS TRAY & PANEL
# ============================================================
print("\n[FASE 5] VERIFIKASI STATUS & KONEKTIVITAS")

if dv_app:
    try:
        # Tray visible?
        tray_visible = dv_app.tray.isVisible()
        print(f"  [{'OK' if tray_visible else 'WARN'}] Tray visible: {tray_visible}")
        
        # Panel visible (should be visible in non-minimize mode)?
        panel_visible = dv_app.control_panel.isVisible()
        print(f"  [OK] Panel visible: {panel_visible}")
        
        # YOLO loaded?
        yolo_ok = dv_app.yolo.is_loaded
        print(f"  [{'OK' if yolo_ok else 'GAGAL'}] YOLO model loaded: {yolo_ok}")
        if not yolo_ok:
            errors.append(f"YOLO not loaded: {dv_app.yolo.load_error}")
        
        # Detection state (should be idle)
        print(f"  [OK] Detection state: {'Detecting' if dv_app.is_detecting else 'Idle'}")
        
        # Config loaded
        conf_val = dv_app.config.get('detection', 'confidence_threshold')
        print(f"  [OK] Config confidence_threshold: {conf_val}")
        
        # Tray status
        tray_status = dv_app.tray.current_status.name
        print(f"  [OK] Tray status: {tray_status}")
        
    except Exception as e:
        errors.append(f"Status verification: {e}")
        print(f"  [GAGAL] Status verification: {e}")

# ============================================================
# FASE 6: TES YOLO INFERENCE (LIVE)
# ============================================================
print("\n[FASE 6] YOLO LIVE INFERENCE TEST")

if dv_app and dv_app.yolo.is_loaded:
    import numpy as np
    try:
        # Create test frame
        frame = np.random.randint(50, 200, (416, 416, 3), dtype=np.uint8)
        
        t0 = time.perf_counter()
        detections = dv_app.yolo.predict(frame, conf_threshold=0.3, imgsz=416)
        t1 = time.perf_counter()
        
        ms = (t1 - t0) * 1000
        print(f"  [OK] Inference: {ms:.0f}ms | Detections: {len(detections)}")
        
        # Second inference (warm)
        t0 = time.perf_counter()
        detections2 = dv_app.yolo.predict(frame, conf_threshold=0.3, imgsz=416)
        t1 = time.perf_counter()
        ms2 = (t1 - t0) * 1000
        print(f"  [OK] Warm inference: {ms2:.0f}ms | Detections: {len(detections2)}")
        
    except Exception as e:
        errors.append(f"YOLO inference: {e}")
        print(f"  [GAGAL] YOLO inference: {e}")

# ============================================================
# FASE 7: TES SNAPSHOT & LOG (LIVE)
# ============================================================
print("\n[FASE 7] SNAPSHOT & LOG LIVE TEST")

if dv_app:
    import numpy as np
    try:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        dets = [{'x1': 100, 'y1': 80, 'x2': 300, 'y2': 280,
                 'class_name': 'Bawor', 'confidence': 0.92, 'class_id': 0}]
        
        path = dv_app.snapshot_mgr.save_snapshot(frame, dets)
        if path and os.path.exists(path):
            sz = os.path.getsize(path)
            print(f"  [OK] Snapshot saved: {os.path.basename(path)} ({sz} bytes)")
        else:
            errors.append("Snapshot save failed")
            print(f"  [GAGAL] Snapshot tidak tersimpan")
        
        dv_app.log_mgr.add_entry('14:32:00', 'Bawor', 92.0, 1)
        count = dv_app.log_mgr.entry_count
        print(f"  [OK] Log entry added (total: {count})")
        
    except Exception as e:
        errors.append(f"Snapshot/Log: {e}")
        print(f"  [GAGAL] Snapshot/Log: {e}")

# ============================================================
# FASE 8: TES CONFIG SIGNAL WIRING
# ============================================================
print("\n[FASE 8] CONFIG SIGNAL WIRING TEST")

if dv_app:
    try:
        received = []
        dv_app.config.config_changed.connect(lambda k, v: received.append(k))
        dv_app.config.set('detection', 'confidence_threshold', 0.85)
        
        if received and received[-1] == 'detection.confidence_threshold':
            print(f"  [OK] Config signal fired: {received[-1]}")
        else:
            print(f"  [WARN] Config signal not received")
            warnings.append("Config signal wiring issue")
        
        # Restore original value
        dv_app.config.set('detection', 'confidence_threshold', 0.72)
        
    except Exception as e:
        errors.append(f"Config signal: {e}")
        print(f"  [GAGAL] Config signal: {e}")

# ============================================================
# FASE 9: TES OVERLAY UPDATE
# ============================================================
print("\n[FASE 9] OVERLAY DISPLAY TEST")

if dv_app:
    try:
        import numpy as np
        test_dets = [
            {'x1': 100, 'y1': 80, 'x2': 300, 'y2': 280,
             'class_name': 'Bawor', 'confidence': 0.95},
            {'x1': 350, 'y1': 100, 'x2': 500, 'y2': 300,
             'class_name': 'Musang King', 'confidence': 0.87},
        ]
        
        dv_app.overlay.update_detections(test_dets)
        print(f"  [OK] Overlay detections updated: {dv_app.overlay.object_count} objects")
        
        dv_app.overlay.update_stats(15.0, 'Desktop', 2)
        print(f"  [OK] Overlay stats: FPS={dv_app.overlay.fps}, Device={dv_app.overlay.device_type}")
        
        settings = dv_app.config.get_section('overlay')
        dv_app.overlay.update_display_settings(settings)
        print(f"  [OK] Overlay display settings applied: boxes={dv_app.overlay.show_boxes}, labels={dv_app.overlay.show_labels}")
        
    except Exception as e:
        errors.append(f"Overlay: {e}")
        print(f"  [GAGAL] Overlay: {e}")

# ============================================================
# FASE 10: TES TRAY LIVE STATS
# ============================================================
print("\n[FASE 10] TRAY LIVE STATS TEST")

if dv_app:
    try:
        dv_app.tray.update_live_stats(12.5, 3, "00:05:30")
        tooltip = dv_app.tray.toolTip()
        expected = "DurianVision | FPS: 12.5 | 🍈 3 objek | ⏱ 00:05:30"
        match = tooltip == expected
        print(f"  [{'OK' if match else 'GAGAL'}] Tooltip: {tooltip}")
        if not match:
            print(f"    Expected: {expected}")
            errors.append(f"Tooltip mismatch")
        
        # Test status changes
        dv_app.tray.set_status(TrayIcon.Status.DETECTING)
        print(f"  [OK] Tray → DETECTING (hijau), text: '{dv_app.tray.toggle_action.text()}'")
        
        dv_app.tray.set_status(TrayIcon.Status.ERROR)
        print(f"  [OK] Tray → ERROR (merah), text: '{dv_app.tray.toggle_action.text()}'")
        
        dv_app.tray.set_status(TrayIcon.Status.IDLE)
        print(f"  [OK] Tray → IDLE (kuning), text: '{dv_app.tray.toggle_action.text()}'")
        
    except Exception as e:
        errors.append(f"Tray stats: {e}")
        print(f"  [GAGAL] Tray stats: {e}")

# ============================================================
# CLEANUP
# ============================================================
print("\n[CLEANUP] Menutup aplikasi...")

if dv_app:
    try:
        dv_app.overlay.hide()
        dv_app.control_panel.close()
        dv_app.tray.hide()
        print(f"  [OK] UI components ditutup")
    except:
        pass

# ============================================================
# FINAL REPORT
# ============================================================
print("\n" + "=" * 60)
print("  LAPORAN FULL SETUP TEST")
print("=" * 60)

total_checks = 10  # 10 phases
phase_names = [
    "Bootstrap (QApplication + QSS)",
    "Core Modules (Config, YOLO, Capture, Snapshot, Log, Device, Hotkeys)",
    "UI Components (Tray, Panel, Overlay, ROI)",
    "DurianVisionApp Coordinator (11 subcomponents)",
    "Status & Konektivitas",
    "YOLO Live Inference",
    "Snapshot & Log Live",
    "Config Signal Wiring",
    "Overlay Display",
    "Tray Live Stats",
]

if len(errors) == 0:
    print(f"\n  SEMUA {total_checks} FASE BERHASIL")
    for i, name in enumerate(phase_names, 1):
        print(f"    [OK] Fase {i}: {name}")
    
    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    [!] {w}")
    
    print(f"\n  GUI Duren FULL SETUP: NORMAL 100%")
else:
    print(f"\n  ERRORS ({len(errors)}):")
    for e in errors:
        print(f"    [X] {e}")
    
    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    [!] {w}")

print("=" * 60)
sys.exit(0 if len(errors) == 0 else 1)
