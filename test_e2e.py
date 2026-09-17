"""
GUI Duren — End-to-End Interaction Test
Tests complete user workflows across all components.
"""
import sys, os, json, time, base64, struct, zlib
import urllib.request, urllib.error

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

INFERENCE = "http://localhost:8001"
BACKEND = "http://localhost:3005"

passed = 0
failed = 0
errors = []
auth_cookie = None

def test(name, fn):
    global passed, failed
    try:
        result = fn()
        if result:
            print(f"  [PASS] {name}")
            passed += 1
        else:
            print(f"  [FAIL] {name} -- returned False")
            failed += 1
            errors.append(name)
    except Exception as e:
        print(f"  [FAIL] {name} -- {type(e).__name__}: {e}")
        failed += 1
        errors.append(f"{name}: {e}")

def post(url, data=None, cookie=None):
    body = json.dumps(data).encode() if data else b""
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            sc = getattr(resp, 'headers', {})
            set_cookie = resp.headers.get("Set-Cookie", "")
            return resp.status, json.loads(resp.read()), set_cookie
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, json.loads(body) if body else {}, ""

def get(url, cookie=None):
    req = urllib.request.Request(url)
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, json.loads(body) if body else {}

def patch(url, data=None, cookie=None):
    body = json.dumps(data).encode() if data else b""
    req = urllib.request.Request(url, data=body, method="PATCH")
    req.add_header("Content-Type", "application/json")
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, json.loads(body) if body else {}

def put(url, data=None, cookie=None):
    body = json.dumps(data).encode() if data else b""
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Content-Type", "application/json")
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, json.loads(body) if body else {}

def delete(url, cookie=None):
    req = urllib.request.Request(url, method="DELETE")
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, json.loads(body) if body else {}

def make_test_png(w=100, h=100):
    """Create a small valid PNG for testing."""
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    scanlines = b''
    for y in range(h):
        scanlines += b'\x00' + bytes([y % 256, (y*2) % 256, (y*3) % 256]) * w
    raw = zlib.compress(scanlines)
    idat = chunk(b'IDAT', raw)
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend

# ============================================================
print("=" * 60)
print("  GUI DUREN -- END-TO-END INTERACTION TEST")
print("=" * 60)

# ============================================================
print("\n[FLOW 1] AUTH: Register -> Login -> Session")
print("-" * 45)

test_email = f"e2e_{int(time.time())}@durian.test"
test_pass = "E2eTest123!"

def flow_register():
    code, body, cookie = post(f"{BACKEND}/api/auth/sign-up/email", {
        "email": test_email, "password": test_pass, "name": "E2E Tester"
    })
    return code == 200 and "user" in body
test("1.1 Register new user", flow_register)

def flow_login():
    global auth_cookie
    code, body, cookie = post(f"{BACKEND}/api/auth/sign-in/email", {
        "email": test_email, "password": test_pass
    })
    if cookie:
        auth_cookie = cookie.split(";")[0]
    elif body.get("session", {}).get("token"):
        auth_cookie = f"better-auth.session_token={body['session']['token']}"
    return code == 200 and auth_cookie is not None
test("1.2 Login and get session", flow_login)

def flow_wrong_password():
    code, body, _ = post(f"{BACKEND}/api/auth/sign-in/email", {
        "email": test_email, "password": "WrongPass999!"
    })
    return code in (400, 401, 403)
test("1.3 Reject wrong password", flow_wrong_password)

def flow_protected_without_auth():
    code, body = get(f"{BACKEND}/api/varieties")
    return code == 401
test("1.4 Protected route rejects unauthenticated", flow_protected_without_auth)

def flow_protected_with_auth():
    code, body = get(f"{BACKEND}/api/varieties", cookie=auth_cookie)
    return code == 200
test("1.5 Protected route accepts authenticated", flow_protected_with_auth)

# ============================================================
print("\n[FLOW 2] VARIETIES: List & Verify Seeded Data")
print("-" * 45)

def flow_list_varieties():
    code, body = get(f"{BACKEND}/api/varieties", cookie=auth_cookie)
    varieties = body.get("data", [])
    return code == 200 and len(varieties) > 0
test("2.1 List varieties -- has data", flow_list_varieties)

def flow_variety_names():
    code, body = get(f"{BACKEND}/api/varieties", cookie=auth_cookie)
    varieties = body.get("data", [])
    names = [v.get("name", "").lower() for v in varieties]
    expected = ["bawor", "monthong", "musang king"]
    return all(any(e in n for n in names) for e in expected)
test("2.2 Varieties include Bawor, Monthong, Musang King", flow_variety_names)

# ============================================================
print("\n[FLOW 3] DETECTION SESSION: Create -> Start -> Predict -> Pause")
print("-" * 45)

session_id = None
def flow_create_session():
    global session_id
    code, body, _ = post(f"{BACKEND}/api/detection", {"name": "E2E Test Session"}, cookie=auth_cookie)
    if code == 200:
        data = body.get("data", body)
        session_id = data.get("id") if isinstance(data, dict) else None
    return code == 200 and session_id is not None
test("3.1 Create detection session", flow_create_session)

def flow_list_sessions():
    code, body = get(f"{BACKEND}/api/detection", cookie=auth_cookie)
    sessions = body.get("data", [])
    return code == 200 and len(sessions) > 0
test("3.2 List sessions -- has data", flow_list_sessions)

def flow_start_session():
    if not session_id: return False
    code, body, _ = post(f"{BACKEND}/api/detection/{session_id}/start", cookie=auth_cookie)
    return code == 200
test("3.3 Start session", flow_start_session)

def flow_pause_session():
    if not session_id: return False
    code, body, _ = post(f"{BACKEND}/api/detection/{session_id}/pause", cookie=auth_cookie)
    return code == 200
test("3.4 Pause session", flow_pause_session)

# ============================================================
print("\n[FLOW 4] INFERENCE: Predict with Image")
print("-" * 45)

test_png = make_test_png(100, 100)
test_b64 = base64.b64encode(test_png).decode()

def flow_predict_base64():
    code, body, _ = post(f"{INFERENCE}/predict/base64", {
        "image": test_b64, "confidence": 0.3, "iou": 0.45, "imgsz": 640
    })
    return code == 200 and "detections" in body and "inference_time_ms" in body
test("4.1 Predict base64 -- returns detections + timing", flow_predict_base64)

def flow_predict_low_confidence():
    code, body, _ = post(f"{INFERENCE}/predict/base64", {
        "image": test_b64, "confidence": 0.01, "iou": 0.45, "imgsz": 640
    })
    return code == 200 and isinstance(body.get("detections"), list)
test("4.2 Predict with low confidence -- returns list", flow_predict_low_confidence)

def flow_predict_different_sizes():
    for size in [320, 640]:
        code, body, _ = post(f"{INFERENCE}/predict/base64", {
            "image": test_b64, "confidence": 0.5, "imgsz": size
        })
        if code != 200: return False
    return True
test("4.3 Predict with different imgsz (320, 640)", flow_predict_different_sizes)

def flow_model_change_device():
    code, body, _ = post(f"{INFERENCE}/predict/base64", {
        "image": test_b64, "confidence": 0.5
    })
    return code == 200 and body.get("model_name") == "yolov11"
test("4.4 Predict returns model_name=yolov11", flow_model_change_device)

# ============================================================
print("\n[FLOW 5] LOGS & STATS")
print("-" * 45)

def flow_list_logs():
    code, body = get(f"{BACKEND}/api/logs", cookie=auth_cookie)
    return code == 200
test("5.1 List detection logs", flow_list_logs)

def flow_log_stats():
    code, body = get(f"{BACKEND}/api/logs/stats", cookie=auth_cookie)
    data = body.get("data", body)
    return code == 200 and isinstance(data, dict)
test("5.2 Get log stats", flow_log_stats)

def flow_log_distribution():
    code, body = get(f"{BACKEND}/api/logs/distribution", cookie=auth_cookie)
    return code == 200
test("5.3 Get variety distribution", flow_log_distribution)

# ============================================================
print("\n[FLOW 6] MODELS MANAGEMENT")
print("-" * 45)

def flow_list_models():
    code, body = get(f"{BACKEND}/api/models", cookie=auth_cookie)
    return code == 200
test("6.1 List models", flow_list_models)

def flow_model_info_inference():
    # Ensure model is freshly loaded
    post(f"{INFERENCE}/reload-model")
    code, body = get(f"{INFERENCE}/model-info")
    return (code == 200 and body.get("is_loaded") == True and
            len(body.get("classes", [])) == 6)
test("6.2 Inference model-info -- loaded + 6 classes", flow_model_info_inference)

def flow_reload_model():
    code, body, _ = post(f"{INFERENCE}/reload-model")
    return code == 200 and body.get("status") == "success"
test("6.3 Reload model -- success", flow_reload_model)

def flow_model_still_loaded():
    code, body = get(f"{INFERENCE}/health")
    return code == 200 and body.get("model_loaded") == True
test("6.4 Model still loaded after reload", flow_model_still_loaded)

# ============================================================
print("\n[FLOW 7] PERFORMANCE MONITORING")
print("-" * 45)

def flow_system_metrics():
    code, body = get(f"{INFERENCE}/system-metrics")
    return (code == 200 and 
            body.get("cpu_percent") is not None and
            body.get("memory_percent") is not None and
            body.get("memory_used_mb") is not None)
test("7.1 System metrics -- CPU + RAM", flow_system_metrics)

def flow_system_via_backend():
    code, body = get(f"{BACKEND}/api/performance/system", cookie=auth_cookie)
    return code == 200
test("7.2 System metrics via backend proxy", flow_system_via_backend)

def flow_inference_via_backend():
    code, body = get(f"{BACKEND}/api/performance/inference", cookie=auth_cookie)
    return code == 200
test("7.3 Inference info via backend proxy", flow_inference_via_backend)

# ============================================================
print("\n[FLOW 8] SNAPSHOTS")
print("-" * 45)

def flow_list_snapshots():
    code, body = get(f"{BACKEND}/api/snapshots", cookie=auth_cookie)
    return code == 200
test("8.1 List snapshots", flow_list_snapshots)

# ============================================================
print("\n[FLOW 9] USER SETTINGS: Read -> Update -> Verify")
print("-" * 45)

def flow_get_settings():
    code, body = get(f"{BACKEND}/api/settings", cookie=auth_cookie)
    return code == 200
test("9.1 Get user settings", flow_get_settings)

def flow_update_settings():
    code, body = put(f"{BACKEND}/api/settings", {
        "confidenceThreshold": 0.7,
        "boxThickness": 3,
        "fontSize": 16,
        "showLabels": True,
        "autoCapture": False
    }, cookie=auth_cookie)
    return code == 200
test("9.2 Update settings", flow_update_settings)

def flow_verify_settings():
    code, body = get(f"{BACKEND}/api/settings", cookie=auth_cookie)
    data = body.get("data", body)
    if isinstance(data, dict):
        return data.get("confidenceThreshold") == 0.7 or data.get("confidence_threshold") == 0.7
    return code == 200
test("9.3 Verify settings persisted", flow_verify_settings)

# ============================================================
print("\n[FLOW 10] FRONTEND SERVING")
print("-" * 45)

def flow_frontend_html():
    req = urllib.request.Request("http://localhost:5173")
    with urllib.request.urlopen(req, timeout=5) as resp:
        html = resp.read().decode()
        return resp.status == 200 and len(html) > 100
test("10.1 Frontend serves HTML", flow_frontend_html)

def flow_frontend_assets():
    req = urllib.request.Request("http://localhost:5173")
    with urllib.request.urlopen(req, timeout=5) as resp:
        html = resp.read().decode()
        return '<script' in html or 'src=' in html
test("10.2 Frontend includes JS assets", flow_frontend_assets)

# ============================================================
print("\n[FLOW 11] DESKTOP MODULE INTEGRATION")
print("-" * 45)

def flow_config_to_worker():
    from core.config_manager import ConfigManager
    from core.yolo_engine import YOLOEngine
    cm = ConfigManager('config/default_config.json')
    cfg = cm.config
    det = cfg.get('detection') or {}
    ye = YOLOEngine('best.pt')
    return (ye.is_loaded and 
            det.get('confidence_threshold') is not None and
            det.get('fps_limit') is not None)
test("11.1 ConfigManager -> YOLOEngine integration", flow_config_to_worker)

def flow_theme_all_varieties():
    from ui.styles.theme import Theme
    model_classes = ['bawor', 'black thorn', 'kanyao', 'monthong', 'musang king', 'not durian']
    colors = [Theme.get_variety_color(c) for c in model_classes]
    return all(c is not None for c in colors) and len(set(colors)) >= 4
test("11.2 Theme colors for all 6 model classes", flow_theme_all_varieties)

def flow_log_export():
    from core.log_manager import LogManager
    import tempfile
    lm = LogManager(tempfile.mkdtemp())
    lm.add_entry('12:00:00', 'Bawor', 95.5, 1)
    lm.add_entry('12:00:01', 'Monthong', 88.0, 2)
    lm.add_entry('12:00:02', 'Musang King', 91.2, 3)
    entries = lm.get_entries()
    csv_path = os.path.join(tempfile.mkdtemp(), 'test_export.csv')
    csv_ok = lm.export_csv(csv_path)
    return (len(entries) == 3 and
            entries[0]['variety'] == 'Bawor' and
            entries[2]['variety'] == 'Musang King' and
            csv_ok and os.path.exists(csv_path))
test("11.3 LogManager add + export CSV", flow_log_export)

def flow_snapshot_draw():
    import numpy as np
    from core.snapshot_manager import SnapshotManager
    import tempfile
    sm = SnapshotManager(tempfile.mkdtemp())
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    dets = [{'x1': 100.5, 'y1': 100.5, 'x2': 200.7, 'y2': 200.7, 
             'class_name': 'Bawor', 'confidence': 0.95}]
    # Test save_snapshot with float coords (verifies int cast fix)
    path = sm.save_snapshot(img, dets)
    return path is not None and os.path.exists(path)
test("11.4 SnapshotManager save with float bbox (bug fix verified)", flow_snapshot_draw)

def flow_hotkey_all_formats():
    from core.global_hotkeys import GlobalHotkeys
    tests = {
        "Ctrl+Shift+D": "<ctrl>+<shift>+d",
        "Alt+F4": "<alt>+<f4>",
        "Space": "<space>",
        "F12": "<f12>",
        "<ctrl>+a": "<ctrl>+a",
    }
    for inp, expected in tests.items():
        result = GlobalHotkeys._convert_hotkey_format(inp)
        if result != expected:
            return False
    return True
test("11.5 GlobalHotkeys format conversion all cases", flow_hotkey_all_formats)

# ============================================================
print("\n" + "=" * 60)
total = passed + failed
pct = passed / total * 100 if total > 0 else 0
status = "PERFECT" if failed == 0 else f"{failed} FAILED"
print(f"  RESULTS: {passed}/{total} passed -- {status}")
print(f"  PASS RATE: {pct:.1f}%")
print("=" * 60)

if errors:
    print(f"\n  Failed tests:")
    for e in errors:
        print(f"    [X] {e}")

print()
sys.exit(0 if failed == 0 else 1)
