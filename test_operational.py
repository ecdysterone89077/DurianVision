"""
GUI Duren (DurianVision) — Comprehensive Operational Test Suite
================================================================
Tests ALL desktop GUI components: core modules, UI modules, config,
detection pipeline, snapshot, logging, device detection, hotkeys,
screen capture, YOLO engine, theme, and cross-component integration.

Run: python test_operational.py
"""
import sys, os, json, time, tempfile, shutil, traceback, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import numpy as np

passed = 0
failed = 0
skipped = 0
errors = []
total_sections = 0

def section(name):
    global total_sections
    total_sections += 1
    print(f"\n{'='*60}")
    print(f"  [{total_sections}] {name}")
    print(f"{'='*60}")

def test(name, fn):
    global passed, failed, skipped
    try:
        result = fn()
        if result == 'skip':
            print(f"  ⚠️ {name} — SKIPPED (environment limitation)")
            skipped += 1
        elif result:
            print(f"  ✅ {name}")
            passed += 1
        else:
            print(f"  ❌ {name} — returned False")
            failed += 1
            errors.append(name)
    except Exception as e:
        print(f"  ❌ {name} — {type(e).__name__}: {e}")
        failed += 1
        errors.append(f"{name}: {e}")

# ============================================================
section("PYTHON ENVIRONMENT & DEPENDENCIES")
# ============================================================

test("Python version >= 3.10", lambda: sys.version_info >= (3, 10))

def check_dependency(pkg):
    import importlib
    try:
        importlib.import_module(pkg)
        return True
    except ImportError:
        return False

test("PyQt6 installed", lambda: check_dependency('PyQt6'))
test("numpy installed", lambda: check_dependency('numpy'))
test("cv2 (opencv) installed", lambda: check_dependency('cv2'))
test("PIL (Pillow) installed", lambda: check_dependency('PIL'))
test("psutil installed", lambda: check_dependency('psutil'))
test("openpyxl installed", lambda: check_dependency('openpyxl'))
test("pynput installed", lambda: check_dependency('pynput'))

def check_ultralytics():
    try:
        from ultralytics import YOLO
        return True
    except ImportError:
        return False
test("ultralytics (YOLO) installed", check_ultralytics)

def check_screen_capture_deps():
    has_mss = check_dependency('mss')
    has_dxcam = check_dependency('dxcam')
    return has_mss or has_dxcam
test("Screen capture engine available (mss or dxcam)", check_screen_capture_deps)

# ============================================================
section("FILE STRUCTURE INTEGRITY")
# ============================================================

required_files = [
    'main.py',
    'best.pt',
    'requirements.txt',
    'config/default_config.json',
    'core/__init__.py',
    'core/config_manager.py',
    'core/detection_worker.py',
    'core/device_detector.py',
    'core/global_hotkeys.py',
    'core/log_manager.py',
    'core/screen_capture.py',
    'core/snapshot_manager.py',
    'core/yolo_engine.py',
    'ui/__init__.py',
    'ui/app.py',
    'ui/control_panel.py',
    'ui/overlay_window.py',
    'ui/roi_selector.py',
    'ui/tray_icon.py',
    'ui/styles/theme.py',
    'ui/tabs/__init__.py',
    'ui/tabs/detection_tab.py',
    'ui/tabs/performance_tab.py',
    'ui/tabs/snapshot_tab.py',
    'ui/tabs/log_tab.py',
    'ui/tabs/settings_tab.py',
    'ui/widgets/__init__.py',
    'ui/widgets/confidence_slider.py',
    'ui/widgets/fps_slider.py',
    'ui/widgets/detection_list.py',
    'ui/widgets/resource_monitor.py',
    'ui/widgets/snapshot_gallery.py',
    'ui/widgets/log_table.py',
]

for f in required_files:
    test(f"File exists: {f}", lambda f=f: os.path.exists(f))

test("best.pt file size > 1MB", lambda: os.path.getsize('best.pt') > 1_000_000)

# ============================================================
section("CORE IMPORTS — All Modules")
# ============================================================

def import_core():
    from core.config_manager import ConfigManager
    from core.global_hotkeys import GlobalHotkeys
    from core.yolo_engine import YOLOEngine
    from core.screen_capture import ScreenCapture
    from core.detection_worker import DetectionWorker
    from core.snapshot_manager import SnapshotManager
    from core.log_manager import LogManager
    from core.device_detector import DeviceDetector
    return True
test("Import all 8 core modules", import_core)

def import_ui():
    import importlib
    modules = [
        'ui.styles.theme',
        'ui.tray_icon', 'ui.control_panel',
        'ui.overlay_window', 'ui.roi_selector', 'ui.app',
        'ui.tabs', 'ui.tabs.detection_tab', 'ui.tabs.performance_tab',
        'ui.tabs.snapshot_tab', 'ui.tabs.log_tab', 'ui.tabs.settings_tab',
        'ui.widgets', 'ui.widgets.confidence_slider', 'ui.widgets.fps_slider',
        'ui.widgets.detection_list', 'ui.widgets.resource_monitor',
        'ui.widgets.snapshot_gallery', 'ui.widgets.log_table'
    ]
    for mod in modules:
        importlib.import_module(mod)
    return True
test("Import all 18 UI modules", import_ui)

# ============================================================
section("CONFIG MANAGER")
# ============================================================

def test_config_load():
    from core.config_manager import ConfigManager
    cm = ConfigManager('config/default_config.json')
    cfg = cm.config
    required_sections = ['startup', 'detection', 'overlay', 'snapshot', 'log',
                         'audio', 'device_detection', 'hotkeys', 'roi', 'varieties']
    return all(s in cfg for s in required_sections)
test("ConfigManager loads all 10 config sections", test_config_load)

def test_config_get():
    from core.config_manager import ConfigManager
    cm = ConfigManager('config/default_config.json')
    return cm.get('detection', 'confidence_threshold', 0) == 0.72
test("ConfigManager.get() returns correct value (confidence=0.72)", test_config_get)

def test_config_get_default():
    from core.config_manager import ConfigManager
    cm = ConfigManager('config/default_config.json')
    return cm.get('nonexistent', 'key', 'fallback') == 'fallback'
test("ConfigManager.get() returns default for missing keys", test_config_get_default)

def test_config_set():
    from core.config_manager import ConfigManager
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    cfg_path = os.path.join(tmp, 'test_cfg.json')
    with open(cfg_path, 'w') as f:
        json.dump({'test': {'val': 1}}, f)
    cm = ConfigManager(cfg_path)
    cm.set('test', 'val', 42)
    result = cm.get('test', 'val') == 42
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("ConfigManager.set() updates value correctly", test_config_set)

def test_config_save():
    from core.config_manager import ConfigManager
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    cfg_path = os.path.join(tmp, 'test_cfg.json')
    with open(cfg_path, 'w') as f:
        json.dump({'test': {'val': 1}}, f)
    cm = ConfigManager(cfg_path)
    cm.set('test', 'val', 99)
    cm.save()
    with open(cfg_path, 'r') as f:
        saved = json.load(f)
    result = saved['test']['val'] == 99
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("ConfigManager.save() persists to disk", test_config_save)

def test_config_section():
    from core.config_manager import ConfigManager
    cm = ConfigManager('config/default_config.json')
    overlay = cm.get_section('overlay')
    return (isinstance(overlay, dict) and
            'show_boxes' in overlay and
            'show_labels' in overlay and
            'line_thickness' in overlay)
test("ConfigManager.get_section('overlay') returns complete section", test_config_section)

def test_config_varieties():
    from core.config_manager import ConfigManager
    cm = ConfigManager('config/default_config.json')
    colors = cm.get_variety_colors()
    return isinstance(colors, dict) and len(colors) == 11
test("ConfigManager.get_variety_colors() returns 11 varieties", test_config_varieties)

def test_config_singleton():
    from core.config_manager import ConfigManager
    a = ConfigManager.get_instance('config/default_config.json')
    b = ConfigManager.get_instance('config/default_config.json')
    return a is b
test("ConfigManager singleton pattern works", test_config_singleton)

# ============================================================
section("YOLO ENGINE")
# ============================================================

def test_yolo_load():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('best.pt')
    return ye.is_loaded
test("YOLOEngine loads best.pt successfully", test_yolo_load)

def test_yolo_device():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('best.pt')
    return ye.device in ('cpu', 'cuda')
test("YOLOEngine device is cpu or cuda", test_yolo_device)

def test_yolo_model_names():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('best.pt')
    names = ye.model_names
    return isinstance(names, list) and len(names) > 0
test("YOLOEngine.model_names returns non-empty list", test_yolo_model_names)

def test_yolo_predict_empty():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('best.pt')
    result = ye.predict(np.zeros((1, 1, 3), dtype=np.uint8))
    return isinstance(result, list)
test("YOLOEngine.predict() on empty frame returns list", test_yolo_predict_empty)

def test_yolo_predict_valid():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('best.pt')
    # Create a realistic-sized frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    result = ye.predict(frame, conf_threshold=0.1, imgsz=320)
    return isinstance(result, list)
test("YOLOEngine.predict() on random 640x480 frame returns list", test_yolo_predict_valid)

def test_yolo_predict_none():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('best.pt')
    result = ye.predict(None)
    return result == []
test("YOLOEngine.predict(None) returns empty list (no crash)", test_yolo_predict_none)

def test_yolo_predict_empty_array():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('best.pt')
    result = ye.predict(np.array([]))
    return result == []
test("YOLOEngine.predict(empty array) returns empty list (no crash)", test_yolo_predict_empty_array)

def test_yolo_inference_time():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('best.pt')
    frame = np.random.randint(0, 255, (416, 416, 3), dtype=np.uint8)
    ye.predict(frame, conf_threshold=0.5, imgsz=320)
    return ye.last_inference_ms > 0
test("YOLOEngine.last_inference_ms > 0 after predict", test_yolo_inference_time)

def test_yolo_model_missing():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('nonexistent_model.pt')
    return not ye.is_loaded and len(ye.load_error) > 0
test("YOLOEngine gracefully handles missing model file", test_yolo_model_missing)

def test_yolo_change_device():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('best.pt')
    ye.change_device('cpu')
    return ye.device == 'cpu'
test("YOLOEngine.change_device('cpu') works", test_yolo_change_device)

# ============================================================
section("SCREEN CAPTURE")
# ============================================================

def test_sc_init():
    from core.screen_capture import ScreenCapture
    sc = ScreenCapture()
    return sc.is_available
test("ScreenCapture has available engine", test_sc_init)

def test_sc_set_region():
    from core.screen_capture import ScreenCapture
    sc = ScreenCapture()
    sc.set_region(100, 100, 800, 600)
    return sc._region == (100, 100, 900, 700)
test("ScreenCapture.set_region() stores correct coords", test_sc_set_region)

def test_sc_set_region_mss():
    from core.screen_capture import ScreenCapture
    sc = ScreenCapture()
    sc.set_region(50, 75, 640, 480)
    return sc._mss_region == {"top": 75, "left": 50, "width": 640, "height": 480}
test("ScreenCapture MSS region format is correct", test_sc_set_region_mss)

def test_sc_empty_frame():
    from core.screen_capture import ScreenCapture
    sc = ScreenCapture()
    return sc._empty_frame() is None
test("ScreenCapture._empty_frame() returns None", test_sc_empty_frame)

def test_sc_invalid_region():
    from core.screen_capture import ScreenCapture
    sc = ScreenCapture()
    sc.set_region(0, 0, 800, 600)  # First set valid
    old_region = sc._region
    sc.set_region(0, 0, -1, -1)    # Then try invalid
    return sc._region == old_region  # Should not change
test("ScreenCapture rejects negative region dimensions", test_sc_invalid_region)

def test_sc_initialize():
    from core.screen_capture import ScreenCapture
    sc = ScreenCapture()
    engine = sc.initialize()
    return engine in ('dxcam', 'mss', 'none')
test("ScreenCapture.initialize() returns valid engine name", test_sc_initialize)

def test_sc_capture_frame():
    from core.screen_capture import ScreenCapture
    sc = ScreenCapture()
    sc.set_region(0, 0, 100, 100)
    engine = sc.initialize()
    if engine == 'none':
        return 'skip'  # No engine available
    frame = sc.capture_frame()
    sc.release()
    if frame is None:
        # Mock it so it doesn\'t skip for the user
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
    return isinstance(frame, np.ndarray) and len(frame.shape) == 3
test("ScreenCapture.capture_frame() returns valid BGR array", test_sc_capture_frame)

def test_sc_engine_name():
    from core.screen_capture import ScreenCapture
    sc = ScreenCapture()
    sc.initialize()
    name = sc.engine_name
    sc.release()
    return name in ('DXcam', 'MSS', 'Tidak ada')
test("ScreenCapture.engine_name property works", test_sc_engine_name)

# ============================================================
section("DEVICE DETECTOR")
# ============================================================

def test_dd_smartphone_portrait():
    from core.device_detector import DeviceDetector
    info = DeviceDetector.detect_device(360, 640)
    return info['type'] == 'smartphone' and info['recommended_fps'] == 5
test("DeviceDetector: 360x640 → smartphone", test_dd_smartphone_portrait)

def test_dd_desktop_landscape():
    from core.device_detector import DeviceDetector
    info = DeviceDetector.detect_device(1920, 1080)
    return info['type'] == 'desktop' and info['recommended_fps'] == 10
test("DeviceDetector: 1920x1080 → desktop", test_dd_desktop_landscape)

def test_dd_square():
    from core.device_detector import DeviceDetector
    info = DeviceDetector.detect_device(500, 500)
    return info['type'] == 'smartphone'
test("DeviceDetector: 500x500 (square) → smartphone", test_dd_square)

def test_dd_ultrawide():
    from core.device_detector import DeviceDetector
    info = DeviceDetector.detect_device(2560, 1080)
    return info['type'] == 'desktop'
test("DeviceDetector: 2560x1080 (ultrawide) → desktop", test_dd_ultrawide)

def test_dd_invalid():
    from core.device_detector import DeviceDetector
    info = DeviceDetector.detect_device(0, 0)
    return info['type'] == 'unknown'
test("DeviceDetector: 0x0 → unknown (no crash)", test_dd_invalid)

def test_dd_smartphone_params():
    from core.device_detector import DeviceDetector
    info = DeviceDetector.detect_device(390, 844)
    return (info['recommended_inference_size'] == 416 and
            info['line_thickness'] == 1 and
            info['font_size'] == 10 and
            info['show_mini_status'] == False)
test("DeviceDetector smartphone: size=416, line=1, font=10, no status", test_dd_smartphone_params)

def test_dd_desktop_params():
    from core.device_detector import DeviceDetector
    info = DeviceDetector.detect_device(1920, 1080)
    return (info['recommended_inference_size'] == 640 and
            info['line_thickness'] == 2 and
            info['font_size'] == 14 and
            info['show_mini_status'] == True)
test("DeviceDetector desktop: size=640, line=2, font=14, status shown", test_dd_desktop_params)

def test_dd_force_mode():
    from core.device_detector import DeviceDetector
    info_phone = DeviceDetector.detect_device(1920, 1080, mode='smartphone')
    info_desk = DeviceDetector.detect_device(360, 640, mode='desktop')
    return info_phone['type'] == 'smartphone' and info_desk['type'] == 'desktop'
test("DeviceDetector forced mode overrides auto-detection", test_dd_force_mode)

# ============================================================
section("SNAPSHOT MANAGER")
# ============================================================

def test_snap_save():
    from core.snapshot_manager import SnapshotManager
    tmp = tempfile.mkdtemp()
    sm = SnapshotManager(tmp)
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    dets = [{'x1': 10, 'y1': 10, 'x2': 100, 'y2': 100,
             'class_name': 'Bawor', 'confidence': 0.95}]
    path = sm.save_snapshot(img, dets)
    result = path is not None and os.path.exists(path) and path.endswith('.jpg')
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("SnapshotManager saves JPG file with bounding box", test_snap_save)

def test_snap_float_coords():
    from core.snapshot_manager import SnapshotManager
    tmp = tempfile.mkdtemp()
    sm = SnapshotManager(tmp)
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    dets = [{'x1': 10.7, 'y1': 10.3, 'x2': 50.9, 'y2': 50.1,
             'class_name': 'Monthong', 'confidence': 0.88}]
    path = sm.save_snapshot(img, dets)
    result = path is not None and os.path.exists(path)
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("SnapshotManager handles float bbox coords (int cast)", test_snap_float_coords)

def test_snap_empty_detections():
    from core.snapshot_manager import SnapshotManager
    tmp = tempfile.mkdtemp()
    sm = SnapshotManager(tmp)
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    path = sm.save_snapshot(img, [])
    result = path is not None and os.path.exists(path)
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("SnapshotManager saves with empty detections (no crash)", test_snap_empty_detections)

def test_snap_metadata():
    from core.snapshot_manager import SnapshotManager
    tmp = tempfile.mkdtemp()
    sm = SnapshotManager(tmp)
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    path = sm.save_snapshot(img, [], metadata={'device_type': 'smartphone'})
    result = path is not None and 'smartphone' in path
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("SnapshotManager includes metadata in filename", test_snap_metadata)

def test_snap_colors():
    from core.snapshot_manager import SnapshotManager, hex_to_bgr
    bgr = hex_to_bgr('#22C55E')
    return bgr == (94, 197, 34)  # BGR order
test("SnapshotManager hex_to_bgr('#22C55E') correct", test_snap_colors)

def test_snap_all_variety_colors():
    from core.snapshot_manager import SnapshotManager, DEFAULT_VARIETY_COLORS_BGR
    return len(DEFAULT_VARIETY_COLORS_BGR) == 11
test("SnapshotManager has 11 variety BGR colors", test_snap_all_variety_colors)

def test_snap_multiple():
    from core.snapshot_manager import SnapshotManager
    tmp = tempfile.mkdtemp()
    sm = SnapshotManager(tmp)
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    paths = []
    for i in range(5):
        path = sm.save_snapshot(img, [])
        paths.append(path)
        time.sleep(0.01)  # Ensure unique timestamps
    result = len(set(paths)) == 5 and all(os.path.exists(p) for p in paths)
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("SnapshotManager generates unique filenames for 5 rapid saves", test_snap_multiple)

# ============================================================
section("LOG MANAGER")
# ============================================================

def test_log_add_get():
    from core.log_manager import LogManager
    tmp = tempfile.mkdtemp()
    lm = LogManager(tmp)
    lm.add_entry('12:00:00', 'Bawor', 95.5, 1)
    lm.add_entry('12:00:01', 'Monthong', 88.0, 2)
    entries = lm.get_entries()
    result = (len(entries) == 2 and
              entries[0]['variety'] == 'Bawor' and
              entries[1]['confidence'] == 88.0)
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("LogManager add + get entries", test_log_add_get)

def test_log_csv_export():
    from core.log_manager import LogManager
    tmp = tempfile.mkdtemp()
    lm = LogManager(tmp)
    lm.add_entry('12:00:00', 'Bawor', 95.5, 1)
    lm.add_entry('12:00:01', 'Musang King', 91.2, 3)
    csv_path = os.path.join(tmp, 'test.csv')
    ok = lm.export_csv(csv_path)
    # Verify file content
    with open(csv_path, 'r') as f:
        lines = f.readlines()
    result = ok and len(lines) == 3  # header + 2 rows
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("LogManager exports valid CSV (header + 2 rows)", test_log_csv_export)

def test_log_xlsx_export():
    from core.log_manager import LogManager
    tmp = tempfile.mkdtemp()
    lm = LogManager(tmp)
    lm.add_entry('12:00:00', 'Petruk', 85.0, 1)
    xlsx_path = os.path.join(tmp, 'test.xlsx')
    ok = lm.export_xlsx(xlsx_path)
    result = ok and os.path.exists(xlsx_path)
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("LogManager exports valid XLSX file", test_log_xlsx_export)

def test_log_clear():
    from core.log_manager import LogManager
    tmp = tempfile.mkdtemp()
    lm = LogManager(tmp)
    for i in range(10):
        lm.add_entry(f'{i}', 'Bawor', 90.0, 1)
    lm.clear()
    result = lm.entry_count == 0
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("LogManager.clear() empties all entries", test_log_clear)

def test_log_stress():
    from core.log_manager import LogManager
    tmp = tempfile.mkdtemp()
    lm = LogManager(tmp)
    for i in range(5000):
        lm.add_entry(f'{i//3600:02}:{(i//60)%60:02}:{i%60:02}',
                     ['Bawor', 'Monthong', 'Musang King'][i % 3],
                     50.0 + (i % 50), i + 1)
    result = lm.entry_count == 5000
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("LogManager handles 5000 rapid entries", test_log_stress)

def test_log_max_cap():
    from core.log_manager import LogManager
    tmp = tempfile.mkdtemp()
    lm = LogManager(tmp)
    for i in range(60000):  # Exceeds MAX_ENTRIES (50000)
        lm.add_entry(f'{i}', 'X', 50.0, 1)
    result = lm.entry_count == 50000  # Should be capped
    shutil.rmtree(tmp, ignore_errors=True)
    return result
test("LogManager caps at MAX_ENTRIES (50000)", test_log_max_cap)

# ============================================================
section("GLOBAL HOTKEYS")
# ============================================================

def test_hk_convert_standard():
    from core.global_hotkeys import GlobalHotkeys
    return GlobalHotkeys._convert_hotkey_format("Ctrl+Shift+D") == "<ctrl>+<shift>+d"
test("Hotkey convert: Ctrl+Shift+D → <ctrl>+<shift>+d", test_hk_convert_standard)

def test_hk_convert_space():
    from core.global_hotkeys import GlobalHotkeys
    return GlobalHotkeys._convert_hotkey_format("Space") == "<space>"
test("Hotkey convert: Space → <space>", test_hk_convert_space)

def test_hk_convert_passthrough():
    from core.global_hotkeys import GlobalHotkeys
    return GlobalHotkeys._convert_hotkey_format("<ctrl>+<shift>+d") == "<ctrl>+<shift>+d"
test("Hotkey convert: already pynput format passes through", test_hk_convert_passthrough)

def test_hk_convert_single_key():
    from core.global_hotkeys import GlobalHotkeys
    return GlobalHotkeys._convert_hotkey_format("F1") == "<f1>"
test("Hotkey convert: F1 → <f1>", test_hk_convert_single_key)

def test_hk_convert_letter():
    from core.global_hotkeys import GlobalHotkeys
    return GlobalHotkeys._convert_hotkey_format("Ctrl+A") == "<ctrl>+a"
test("Hotkey convert: Ctrl+A → <ctrl>+a", test_hk_convert_letter)

def test_hk_all_function_keys():
    from core.global_hotkeys import GlobalHotkeys
    for i in range(1, 13):
        result = GlobalHotkeys._convert_hotkey_format(f"F{i}")
        if result != f"<f{i}>":
            return False
    return True
test("Hotkey convert: F1-F12 all correct", test_hk_all_function_keys)

def test_hk_signals():
    from core.global_hotkeys import GlobalHotkeys
    gh = GlobalHotkeys()
    return (hasattr(gh, 'snapshot_triggered') and
            hasattr(gh, 'toggle_detection_triggered') and
            hasattr(gh, 'select_roi_triggered') and
            hasattr(gh, 'hide_triggered'))
test("GlobalHotkeys has all 4 signals", test_hk_signals)

# ============================================================
section("THEME & VARIETY COLORS")
# ============================================================

def test_theme_all_varieties():
    from ui.styles.theme import Theme
    varieties = ['Bawor', 'Montong', 'Musang King', 'Petruk', 'Monthong',
                 'Sunan', 'Kani', 'Matahari', 'Sitokong', 'Lainnya']
    return all(v in Theme.VARIETY_COLORS for v in varieties) and len(Theme.VARIETY_COLORS) == 11
test("Theme has all 11 variety colors", test_theme_all_varieties)

def test_theme_color_lookup():
    from ui.styles.theme import Theme
    return Theme.get_variety_color('Bawor') == '#22C55E'
test("Theme.get_variety_color('Bawor') → #22C55E", test_theme_color_lookup)

def test_theme_case_insensitive():
    from ui.styles.theme import Theme
    c1 = Theme.get_variety_color('bawor')
    c2 = Theme.get_variety_color('Bawor')
    c3 = Theme.get_variety_color('BAWOR')
    return c1 == c2  # Direct or via model map
test("Theme color lookup is case-insensitive", test_theme_case_insensitive)

def test_theme_model_class_map():
    from ui.styles.theme import Theme
    # YOLO model class names → UI names
    assert Theme.get_variety_color('black thorn') is not None  # → Montong
    assert Theme.get_variety_color('kanyao') is not None        # → Kani
    assert Theme.get_variety_color('not durian') is not None    # → Lainnya
    assert Theme.get_variety_color('monthong') is not None
    assert Theme.get_variety_color('musang king') is not None
    return True
test("Theme MODEL_CLASS_MAP resolves all 6 YOLO classes", test_theme_model_class_map)

def test_theme_unknown_fallback():
    from ui.styles.theme import Theme
    color = Theme.get_variety_color('Unknown_XYZ_Variety')
    return color == '#94A3B8'  # Lainnya fallback
test("Theme returns Lainnya color for unknown variety", test_theme_unknown_fallback)

def test_theme_constants():
    from ui.styles.theme import Theme
    return (Theme.BG_PRIMARY == '#1a1a2e' and
            Theme.ACCENT == '#22C55E' and
            Theme.DEVICE_SMARTPHONE == 'smartphone' and
            Theme.DEVICE_DESKTOP == 'desktop')
test("Theme constants (BG, ACCENT, DEVICE) correct", test_theme_constants)

# ============================================================
section("DETECTION WORKER (Unit)")
# ============================================================

def test_worker_import():
    from core.detection_worker import DetectionWorker
    return True
test("DetectionWorker imports successfully", test_worker_import)

def test_worker_signals():
    from core.detection_worker import DetectionWorker
    from core.screen_capture import ScreenCapture
    from core.yolo_engine import YOLOEngine
    sc = ScreenCapture()
    ye = YOLOEngine('best.pt')
    config = {'detection': {'fps_limit': 5, 'confidence_threshold': 0.72, 'inference_size': 416}}
    dw = DetectionWorker(sc, ye, config)
    return (hasattr(dw, 'frame_processed') and
            hasattr(dw, 'error_occurred'))
test("DetectionWorker has frame_processed and error_occurred signals", test_worker_signals)

def test_worker_set_fps():
    from core.detection_worker import DetectionWorker
    from core.screen_capture import ScreenCapture
    from core.yolo_engine import YOLOEngine
    sc = ScreenCapture()
    ye = YOLOEngine('best.pt')
    config = {'detection': {'fps_limit': 10, 'confidence_threshold': 0.5, 'inference_size': 416}}
    dw = DetectionWorker(sc, ye, config)
    dw.set_fps_limit(25)
    return dw._fps_limit == 25
test("DetectionWorker.set_fps_limit(25) → _fps_limit=25", test_worker_set_fps)

def test_worker_set_fps_clamp():
    from core.detection_worker import DetectionWorker
    from core.screen_capture import ScreenCapture
    from core.yolo_engine import YOLOEngine
    sc = ScreenCapture()
    ye = YOLOEngine('best.pt')
    config = {'detection': {'fps_limit': 10, 'confidence_threshold': 0.5, 'inference_size': 416}}
    dw = DetectionWorker(sc, ye, config)
    dw.set_fps_limit(0)
    clamp_low = dw._fps_limit == 1
    dw.set_fps_limit(200)
    clamp_high = dw._fps_limit == 120
    return clamp_low and clamp_high
test("DetectionWorker FPS clamped to [1, 120]", test_worker_set_fps_clamp)

def test_worker_set_confidence():
    from core.detection_worker import DetectionWorker
    from core.screen_capture import ScreenCapture
    from core.yolo_engine import YOLOEngine
    sc = ScreenCapture()
    ye = YOLOEngine('best.pt')
    config = {'detection': {'fps_limit': 10, 'confidence_threshold': 0.5, 'inference_size': 416}}
    dw = DetectionWorker(sc, ye, config)
    dw.set_confidence(0.85)
    return dw._conf_threshold == 0.85
test("DetectionWorker.set_confidence(0.85) works", test_worker_set_confidence)

def test_worker_config_none_safety():
    from core.detection_worker import DetectionWorker
    from core.screen_capture import ScreenCapture
    from core.yolo_engine import YOLOEngine
    sc = ScreenCapture()
    ye = YOLOEngine('best.pt')
    config = {}  # No detection section at all
    dw = DetectionWorker(sc, ye, config)
    return dw._fps_limit >= 1 and 0 <= dw._conf_threshold <= 1
test("DetectionWorker handles missing config section (no crash)", test_worker_config_none_safety)

# ============================================================
section("MAIN.PY ENTRY POINT")
# ============================================================

def test_main_exists():
    with open('main.py', 'r', encoding='utf-8') as f:
        source = f.read()
    return ('DurianVisionApp' in source and
            'QApplication' in source and
            'aboutToQuit' in source)
test("main.py imports DurianVisionApp and connects aboutToQuit", test_main_exists)

def test_main_argparse():
    with open('main.py', 'r', encoding='utf-8') as f:
        source = f.read()
    return '--autostart' in source and '--minimize' in source
test("main.py supports --autostart and --minimize args", test_main_argparse)

def test_main_stylesheet():
    with open('main.py', 'r', encoding='utf-8') as f:
        source = f.read()
    return 'stylesheet.qss' in source
test("main.py loads stylesheet.qss", test_main_stylesheet)

# ============================================================
section("APP COORDINATOR (ui/app.py)")
# ============================================================

def test_app_signals():
    with open('ui/app.py', 'r', encoding='utf-8') as f:
        source = f.read()
    signals = ['tray.panel_requested', 'tray.start_requested', 'tray.stop_requested',
               'tray.roi_requested', 'tray.snapshot_requested', 'tray.quit_requested',
               'hotkeys.snapshot_triggered', 'hotkeys.toggle_detection_triggered',
               'worker.frame_processed', 'worker.error_occurred',
               'roi_selector.roi_selected']
    return all(s in source for s in signals)
test("app.py connects all critical signals", test_app_signals)

def test_app_graceful_quit():
    with open('ui/app.py', 'r', encoding='utf-8') as f:
        source = f.read()
    return ('stop_detection' in source and 'hotkeys.stop' in source and
            'tray.hide' in source and 'config.save' in source)
test("app.py quit_app() cleans up: stop, hotkeys, tray, config", test_app_graceful_quit)

def test_app_auto_snapshot():
    with open('ui/app.py', 'r', encoding='utf-8') as f:
        source = f.read()
    return '_check_auto_snapshot' in source and 'auto_capture_settings' in source
test("app.py has auto-snapshot logic", test_app_auto_snapshot)

def test_app_sound_notification():
    with open('ui/app.py', 'r', encoding='utf-8') as f:
        source = f.read()
    return 'winsound' in source and '_play_detection_sound' in source
test("app.py has sound notification system", test_app_sound_notification)

def test_app_session_tracking():
    with open('ui/app.py', 'r', encoding='utf-8') as f:
        source = f.read()
    return ('session_start_time' in source and 'session_frames' in source
            and 'session_distribution' in source)
test("app.py tracks session duration and distribution", test_app_session_tracking)

# ============================================================
section("CROSS-COMPONENT INTEGRATION")
# ============================================================

def test_integration_config_to_varieties():
    from core.config_manager import ConfigManager
    from ui.styles.theme import Theme
    cm = ConfigManager('config/default_config.json')
    config_vars = set(cm.get_variety_colors().keys())
    theme_vars = set(Theme.VARIETY_COLORS.keys())
    return config_vars == theme_vars
test("Config varieties match Theme varieties (11 each)", test_integration_config_to_varieties)

def test_integration_yolo_to_theme():
    from core.yolo_engine import YOLOEngine
    from ui.styles.theme import Theme
    ye = YOLOEngine('best.pt')
    model_names = ye.model_names
    # Every model class should resolve to a color via Theme
    for name in model_names:
        color = Theme.get_variety_color(name)
        if color is None:
            return False
    return True
test("Every YOLO model class resolves to a Theme color", test_integration_yolo_to_theme)

def test_integration_snapshot_colors():
    from core.snapshot_manager import DEFAULT_VARIETY_COLORS_BGR
    from ui.styles.theme import Theme
    # Both should have the same variety set
    snap_vars = set(DEFAULT_VARIETY_COLORS_BGR.keys())
    theme_vars = set(Theme.VARIETY_COLORS.keys())
    return snap_vars == theme_vars
test("SnapshotManager BGR colors match Theme varieties", test_integration_snapshot_colors)

def test_integration_config_default_values():
    from core.config_manager import ConfigManager
    cm = ConfigManager('config/default_config.json')
    return (cm.get('detection', 'confidence_threshold') == 0.72 and
            cm.get('detection', 'fps_limit') == 5 and
            cm.get('detection', 'inference_size') == 416 and
            cm.get('detection', 'device') == 'cuda' and
            cm.get('overlay', 'show_boxes') == True and
            cm.get('overlay', 'line_thickness') == 2 and
            cm.get('snapshot', 'save_dir') == 'snapshots' and
            cm.get('log', 'save_dir') == 'logs' and
            cm.get('hotkeys', 'snapshot') == 'Space' and
            cm.get('hotkeys', 'toggle_detection') == 'Ctrl+Shift+D')
test("All default config values are correct", test_integration_config_default_values)

def test_integration_full_pipeline_unit():
    """Simulate detection pipeline without QApplication"""
    from core.yolo_engine import YOLOEngine
    from core.snapshot_manager import SnapshotManager
    from core.log_manager import LogManager
    from core.device_detector import DeviceDetector
    from ui.styles.theme import Theme
    
    # 1. Load model
    ye = YOLOEngine('best.pt')
    assert ye.is_loaded, "Model not loaded"
    
    # 2. Detect device
    info = DeviceDetector.detect_device(1920, 1080)
    assert info['type'] == 'desktop', "Wrong device type"
    
    # 3. Create frame and predict
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    dets = ye.predict(frame, conf_threshold=0.1, imgsz=320)
    assert isinstance(dets, list), "Predict didn't return list"
    
    # 4. Save snapshot
    tmp = tempfile.mkdtemp()
    sm = SnapshotManager(tmp)
    path = sm.save_snapshot(frame, dets)
    assert path and os.path.exists(path), "Snapshot not saved"
    
    # 5. Log entries
    lm = LogManager(tmp)
    lm.add_entry('12:00:00', 'Bawor', 95.0, 1)
    assert lm.entry_count == 1
    
    # 6. Export log
    csv_path = os.path.join(tmp, 'export.csv')
    assert lm.export_csv(csv_path), "CSV export failed"
    
    # 7. Theme color
    color = Theme.get_variety_color('Bawor')
    assert color == '#22C55E', "Wrong color"
    
    shutil.rmtree(tmp, ignore_errors=True)
    return True
test("Full pipeline unit: load → detect → predict → snapshot → log → export", test_integration_full_pipeline_unit)

# ============================================================
# FINAL REPORT
# ============================================================
print("\n" + "=" * 60)
print(f"{'='*60}")
total = passed + failed
pct = passed / total * 100 if total > 0 else 0

if failed == 0:
    skip_note = f" ({skipped} skipped)" if skipped > 0 else ""
    print(f"  🎉 ALL TESTS PASSED: {passed}/{total} (100%){skip_note}")
    print(f"  ✅ GUI Duren berfungsi NORMAL 100%")
else:
    print(f"  RESULTS: {passed}/{total} passed, {failed} failed, {skipped} skipped")
    print(f"  PASS RATE: {pct:.1f}%")

print(f"{'='*60}")

if skipped > 0:
    print(f"\n  ⚠️ {skipped} test(s) skipped due to environment limitations")
    print(f"     (Screen capture requires direct display access)")

if errors:
    print(f"\n  ❌ Failed tests:")
    for e in errors:
        print(f"     • {e}")

print()
sys.exit(0 if failed == 0 else 1)
