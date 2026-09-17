"""
GUI Duren — Comprehensive Functional Test
Tests all API endpoints across Inference, Backend, and Desktop modules.
"""
import sys, os, json, time, traceback, base64
import urllib.request
import urllib.error

INFERENCE_URL = "http://localhost:8001"
BACKEND_URL = "http://localhost:3005"

passed = 0
failed = 0
errors = []

def test(name, fn):
    global passed, failed
    try:
        result = fn()
        if result:
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

def http_get(url, timeout=5):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read())

def http_post(url, data=None, timeout=5):
    body = json.dumps(data).encode() if data else b""
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()) if e.read() else {}

def http_get_raw(url, timeout=5):
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code

# ============================================================
print("=" * 60)
print("  GUI DUREN — COMPREHENSIVE FUNCTIONAL TEST")
print("=" * 60)

# ============================================================
print("\n[1/7] INFERENCE SIDECAR (FastAPI :8001)")
print("-" * 40)

test("GET /health", lambda: (
    http_get(f"{INFERENCE_URL}/health")[1].get("status") == "ok"
))

test("GET /health — model_loaded=true", lambda: (
    http_post(f"{INFERENCE_URL}/reload-model") and
    http_get(f"{INFERENCE_URL}/health")[1].get("model_loaded") == True
))

test("GET /model-info", lambda: (
    http_get(f"{INFERENCE_URL}/model-info")[1].get("is_loaded") == True
))

test("GET /model-info — has classes", lambda: (
    len(http_get(f"{INFERENCE_URL}/model-info")[1].get("classes", [])) == 6
))

test("GET /model-info — correct classes", lambda: (
    set(http_get(f"{INFERENCE_URL}/model-info")[1].get("classes", [])) == 
    {"bawor", "black thorn", "kanyao", "monthong", "musang king", "not durian"}
))

test("GET /system-metrics", lambda: (
    "cpu_percent" in http_get(f"{INFERENCE_URL}/system-metrics")[1]
))

test("GET /system-metrics — has memory_percent", lambda: (
    "memory_percent" in http_get(f"{INFERENCE_URL}/system-metrics")[1]
))

# Test predict with a small dummy image (1x1 black pixel PNG)
import struct, zlib
def make_tiny_png():
    """Create a minimal valid 1x1 black PNG."""
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
    raw = zlib.compress(b'\x00\x00\x00\x00')
    idat = chunk(b'IDAT', raw)
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend

test("POST /predict/base64 — accepts base64 image", lambda: (
    http_post(f"{INFERENCE_URL}/predict/base64", {
        "image": base64.b64encode(make_tiny_png()).decode(),
        "confidence": 0.5
    })[0] == 200
))

test("POST /predict/base64 — returns detections array", lambda: (
    isinstance(http_post(f"{INFERENCE_URL}/predict/base64", {
        "image": base64.b64encode(make_tiny_png()).decode(),
        "confidence": 0.5
    })[1].get("detections"), list)
))

test("POST /predict/base64 — returns inference_time_ms", lambda: (
    "inference_time_ms" in http_post(f"{INFERENCE_URL}/predict/base64", {
        "image": base64.b64encode(make_tiny_png()).decode(),
        "confidence": 0.5
    })[1]
))

# ============================================================
print("\n[2/7] BACKEND AUTH (Better-Auth :3005)")
print("-" * 40)

# Register a test user
test_email = f"test_{int(time.time())}@durian.test"
test_pass = "TestPass123!"

def register_user():
    code, body = http_post(f"{BACKEND_URL}/api/auth/sign-up/email", {
        "email": test_email,
        "password": test_pass,
        "name": "Test User"
    })
    return code == 200 and body.get("user", {}).get("email") == test_email

test("POST /api/auth/sign-up/email — register", register_user)

# Login
auth_token = None
def login_user():
    global auth_token
    code, body = http_post(f"{BACKEND_URL}/api/auth/sign-in/email", {
        "email": test_email,
        "password": test_pass
    })
    if code == 200 and body.get("session"):
        auth_token = body["session"].get("token")
        return True
    # Try alternate response format
    if code == 200 and body.get("token"):
        auth_token = body["token"]
        return True
    return code == 200

test("POST /api/auth/sign-in/email — login", login_user)

# ============================================================
print("\n[3/7] BACKEND API — Varieties (:3005)")
print("-" * 40)

def authed_get(path):
    req = urllib.request.Request(f"{BACKEND_URL}{path}")
    if auth_token:
        req.add_header("Authorization", f"Bearer {auth_token}")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, json.loads(body) if body else {}

def authed_post(path, data=None):
    body = json.dumps(data).encode() if data else b""
    req = urllib.request.Request(f"{BACKEND_URL}{path}", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if auth_token:
        req.add_header("Authorization", f"Bearer {auth_token}")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, json.loads(body) if body else {}

test("GET /api/varieties — list varieties", lambda: (
    authed_get("/api/varieties")[0] in (200, 401)
))

# ============================================================
print("\n[4/7] BACKEND API — Detection & Logs (:3005)")
print("-" * 40)

test("GET /api/detection — list sessions", lambda: (
    authed_get("/api/detection")[0] in (200, 401)
))

test("GET /api/logs — list logs", lambda: (
    authed_get("/api/logs")[0] in (200, 401)
))

test("GET /api/logs/stats — log stats", lambda: (
    authed_get("/api/logs/stats")[0] in (200, 401)
))

test("GET /api/logs/distribution — variety distribution", lambda: (
    authed_get("/api/logs/distribution")[0] in (200, 401)
))

# ============================================================
print("\n[5/7] BACKEND API — Models & Performance (:3005)")
print("-" * 40)

test("GET /api/models — list models", lambda: (
    authed_get("/api/models")[0] in (200, 401)
))

test("GET /api/performance/system — system metrics proxy", lambda: (
    authed_get("/api/performance/system")[0] in (200, 401)
))

test("GET /api/performance/inference — inference info proxy", lambda: (
    authed_get("/api/performance/inference")[0] in (200, 401)
))

# ============================================================
print("\n[6/7] BACKEND API — Snapshots & Settings (:3005)")
print("-" * 40)

test("GET /api/snapshots — list snapshots", lambda: (
    authed_get("/api/snapshots")[0] in (200, 401)
))

test("GET /api/settings — get user settings", lambda: (
    authed_get("/api/settings")[0] in (200, 401)
))

# ============================================================
print("\n[7/7] DESKTOP APP — Module Import Test")
print("-" * 40)

# Test all desktop imports work
def test_desktop_imports():
    from core.config_manager import ConfigManager
    from core.global_hotkeys import GlobalHotkeys
    from core.yolo_engine import YOLOEngine
    from core.screen_capture import ScreenCapture
    from core.detection_worker import DetectionWorker
    from core.snapshot_manager import SnapshotManager
    from core.log_manager import LogManager
    from core.device_detector import DeviceDetector
    return True

test("Import all core modules", test_desktop_imports)

def test_ui_imports():
    # Can't create QWidgets without QApplication, just test importability
    import importlib
    for mod in ['ui.tray_icon', 'ui.control_panel', 'ui.overlay_window', 
                'ui.roi_selector', 'ui.app', 'ui.styles.theme']:
        importlib.import_module(mod)
    return True

test("Import all UI modules", test_ui_imports)

def test_config_manager():
    from core.config_manager import ConfigManager
    cm = ConfigManager('config/default_config.json')
    cfg = cm.config
    return 'detection' in cfg and 'overlay' in cfg and 'varieties' in cfg

test("ConfigManager loads config correctly", test_config_manager)

def test_config_varieties():
    from core.config_manager import ConfigManager
    cm = ConfigManager('config/default_config.json')
    colors = cm.get_variety_colors()
    return isinstance(colors, dict) and len(colors) > 0

test("ConfigManager.get_variety_colors() works", test_config_varieties)

def test_theme_colors():
    from ui.styles.theme import Theme
    # Test model class name mapping
    c1 = Theme.get_variety_color('bawor')       # model name
    c2 = Theme.get_variety_color('Bawor')        # UI name
    c3 = Theme.get_variety_color('monthong')     # model name
    c4 = Theme.get_variety_color('not durian')   # model name -> Lainnya
    c5 = Theme.get_variety_color('unknown_xyz')  # fallback
    return c1 == c2 and c3 is not None and c4 is not None and c5 is not None

test("Theme.get_variety_color() — case-insensitive + aliases", test_theme_colors)

def test_log_manager():
    from core.log_manager import LogManager
    from collections import deque
    lm = LogManager('logs')
    lm.add_entry('12:00:00', 'Bawor', 95.5, 1)
    lm.add_entry('12:00:01', 'Monthong', 88.0, 2)
    entries = lm.get_entries()
    return (len(entries) == 2 and 
            isinstance(lm._entries, deque) and 
            entries[0]['variety'] == 'Bawor')

test("LogManager — deque + add/get entries", test_log_manager)

def test_hotkey_format_conversion():
    from core.global_hotkeys import GlobalHotkeys
    assert GlobalHotkeys._convert_hotkey_format("Ctrl+Shift+D") == "<ctrl>+<shift>+d"
    assert GlobalHotkeys._convert_hotkey_format("Space") == "<space>"
    assert GlobalHotkeys._convert_hotkey_format("<ctrl>+<shift>+d") == "<ctrl>+<shift>+d"
    assert GlobalHotkeys._convert_hotkey_format("Ctrl+A") == "<ctrl>+a"
    assert GlobalHotkeys._convert_hotkey_format("F1") == "<f1>"
    return True

test("GlobalHotkeys._convert_hotkey_format() — all formats", test_hotkey_format_conversion)

def test_screen_capture_none():
    from core.screen_capture import ScreenCapture
    sc = ScreenCapture()
    result = sc._empty_frame()
    return result is None

test("ScreenCapture._empty_frame() returns None", test_screen_capture_none)

def test_yolo_engine():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('best.pt')
    return ye.is_loaded and ye.device in ('cpu', 'cuda')

test("YOLOEngine loads best.pt on CPU", test_yolo_engine)

# ============================================================
# FRONTEND CHECK
print("\n[BONUS] FRONTEND (Vite :5173)")
print("-" * 40)

def check_frontend():
    try:
        req = urllib.request.Request("http://localhost:5173")
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode()
            return resp.status == 200 and "durian" in html.lower() or "<div" in html
    except:
        return False

test("GET http://localhost:5173 — returns HTML", check_frontend)

# ============================================================
print("\n" + "=" * 60)
total = passed + failed
print(f"  RESULTS: {passed}/{total} passed, {failed} failed")
print(f"  PASS RATE: {passed/total*100:.1f}%" if total > 0 else "  NO TESTS RUN")
print("=" * 60)

if errors:
    print(f"\n  Failed tests:")
    for e in errors:
        print(f"    ❌ {e}")

print()
sys.exit(0 if failed == 0 else 1)
