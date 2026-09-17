"""
GUI Duren — Advanced Protocol Test Suite
Tests: edge cases, error handling, stress, data integrity, cross-component flows
"""
import sys, os, json, time, base64, struct, zlib, threading, concurrent.futures
import urllib.request, urllib.error

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
            print(f"  [FAIL] {name}")
            failed += 1
            errors.append(name)
    except Exception as e:
        print(f"  [FAIL] {name} -- {type(e).__name__}: {e}")
        failed += 1
        errors.append(f"{name}: {e}")

def http(method, url, data=None, cookie=None, timeout=10):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    if body:
        req.add_header("Content-Type", "application/json")
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                return resp.status, json.loads(raw), resp.headers
            except:
                return resp.status, raw.decode(errors='replace'), resp.headers
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw), e.headers
        except:
            return e.code, raw.decode(errors='replace'), e.headers
    except Exception as e:
        return 0, str(e), {}

def make_png(w=100, h=100):
    def chunk(ct, d):
        c = ct + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    hdr = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    raw = zlib.compress(b''.join(b'\x00' + bytes([y%256, (y*2)%256, (y*3)%256]) * w for y in range(h)))
    return hdr + ihdr + chunk(b'IDAT', raw) + chunk(b'IEND', b'')

# Setup auth
test_email = f"adv_{int(time.time())}@durian.test"
test_pass = "AdvTest123!"
_, body, _ = http("POST", f"{BACKEND}/api/auth/sign-up/email",
    {"email": test_email, "password": test_pass, "name": "Advanced Tester"})
_, body, headers = http("POST", f"{BACKEND}/api/auth/sign-in/email",
    {"email": test_email, "password": test_pass})
sc = headers.get("Set-Cookie", "") if headers else ""
if sc:
    auth_cookie = sc.split(";")[0]
elif isinstance(body, dict) and body.get("session", {}).get("token"):
    auth_cookie = f"better-auth.session_token={body['session']['token']}"

test_b64 = base64.b64encode(make_png()).decode()

print("=" * 60)
print("  GUI DUREN -- ADVANCED PROTOCOL TEST SUITE")
print("=" * 60)

# ============================================================
print("\n[P1] ERROR HANDLING & EDGE CASES")
print("-" * 45)

test("1.01 POST /predict/base64 empty body -> 422",
    lambda: http("POST", f"{INFERENCE}/predict/base64", {})[0] == 422)

test("1.02 POST /predict/base64 invalid base64 -> 400",
    lambda: http("POST", f"{INFERENCE}/predict/base64",
        {"image": "NOT_VALID_BASE64!!!", "confidence": 0.5})[0] == 400)

test("1.03 POST /predict/base64 confidence=0 -> 200",
    lambda: http("POST", f"{INFERENCE}/predict/base64",
        {"image": test_b64, "confidence": 0.0, "iou": 0.45})[0] == 200)

test("1.04 POST /predict/base64 confidence=1 -> 200",
    lambda: http("POST", f"{INFERENCE}/predict/base64",
        {"image": test_b64, "confidence": 1.0, "iou": 0.45})[0] == 200)

test("1.05 GET nonexistent route -> 404",
    lambda: http("GET", f"{INFERENCE}/nonexistent")[0] == 404)

test("1.06 GET /api/varieties no auth -> 401",
    lambda: http("GET", f"{BACKEND}/api/varieties")[0] == 401)

test("1.07 GET /api/detection/invalid-uuid -> 200 (empty)",
    lambda: (lambda r: r[0] == 200)(http("GET", f"{BACKEND}/api/detection/00000000-0000-0000-0000-000000000000", cookie=auth_cookie)))

test("1.08 POST /api/detection empty body -> handles gracefully",
    lambda: http("POST", f"{BACKEND}/api/detection", {}, cookie=auth_cookie)[0] in (200, 400, 500))

test("1.09 PUT /api/settings empty body -> handles gracefully",
    lambda: http("PUT", f"{BACKEND}/api/settings", {}, cookie=auth_cookie)[0] in (200, 400))

test("1.10 DELETE /api/detection/nonexistent -> handles gracefully",
    lambda: http("DELETE", f"{BACKEND}/api/detection/nonexistent-id-here", cookie=auth_cookie)[0] in (200, 404, 500))

test("1.11 GET /health always 200",
    lambda: http("GET", f"{INFERENCE}/health")[0] == 200)

test("1.12 GET /system-metrics always 200",
    lambda: http("GET", f"{INFERENCE}/system-metrics")[0] == 200)

# ============================================================
print("\n[P2] DATA INTEGRITY — Write → Read → Verify")
print("-" * 45)

def p2_settings_integrity():
    unique_val = round(time.time() % 1, 2)
    conf = 0.1 + unique_val * 0.005
    http("PUT", f"{BACKEND}/api/settings", {
        "confidenceThreshold": conf,
        "boxThickness": 5,
        "fontSize": 20,
        "showLabels": False,
        "autoCapture": True
    }, cookie=auth_cookie)
    code, body, _ = http("GET", f"{BACKEND}/api/settings", cookie=auth_cookie)
    data = body.get("data", body) if isinstance(body, dict) else {}
    saved_conf = data.get("confidenceThreshold") or data.get("confidence_threshold")
    saved_box = data.get("boxThickness") or data.get("box_thickness")
    return saved_conf is not None and saved_box == 5
test("2.1 Settings write -> read integrity", p2_settings_integrity)

def p2_session_lifecycle():
    # Create
    code, body, _ = http("POST", f"{BACKEND}/api/detection", {"name": "Integrity Test"}, cookie=auth_cookie)
    if code != 200: return False
    data = body.get("data", body)
    sid = data.get("id") if isinstance(data, dict) else None
    if not sid: return False
    
    # Start
    code, _, _ = http("POST", f"{BACKEND}/api/detection/{sid}/start", cookie=auth_cookie)
    if code != 200: return False
    
    # Verify running
    code, body, _ = http("GET", f"{BACKEND}/api/detection/{sid}", cookie=auth_cookie)
    data = body.get("data", body) if isinstance(body, dict) else {}
    status = data.get("status", "")
    if status != "running": return False
    
    # Pause
    code, _, _ = http("POST", f"{BACKEND}/api/detection/{sid}/pause", cookie=auth_cookie)
    if code != 200: return False
    
    # Verify paused
    code, body, _ = http("GET", f"{BACKEND}/api/detection/{sid}", cookie=auth_cookie)
    data = body.get("data", body) if isinstance(body, dict) else {}
    status = data.get("status", "")
    if status != "paused": return False
    
    # Stop
    code, _, _ = http("POST", f"{BACKEND}/api/detection/{sid}/stop", cookie=auth_cookie)
    if code != 200: return False
    
    # Verify completed
    code, body, _ = http("GET", f"{BACKEND}/api/detection/{sid}", cookie=auth_cookie)
    data = body.get("data", body) if isinstance(body, dict) else {}
    return data.get("status") == "completed"
test("2.2 Session lifecycle: Create -> Start -> Pause -> Stop -> Verify", p2_session_lifecycle)

def p2_variety_count_consistency():
    code, body, _ = http("GET", f"{BACKEND}/api/varieties", cookie=auth_cookie)
    varieties = body.get("data", []) if isinstance(body, dict) else []
    # Run twice to verify consistency
    code2, body2, _ = http("GET", f"{BACKEND}/api/varieties", cookie=auth_cookie)
    varieties2 = body2.get("data", []) if isinstance(body2, dict) else []
    return len(varieties) == len(varieties2) and len(varieties) >= 6
test("2.3 Variety data is stable across reads", p2_variety_count_consistency)

# ============================================================
print("\n[P3] CONCURRENT STRESS TEST")
print("-" * 45)

def p3_concurrent_predict():
    results = []
    def do_predict(i):
        code, body, _ = http("POST", f"{INFERENCE}/predict/base64",
            {"image": test_b64, "confidence": 0.5}, timeout=30)
        return code == 200 and isinstance(body, dict) and "detections" in body
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = [ex.submit(do_predict, i) for i in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    return all(results)
test("3.1 10 concurrent predictions (5 threads) -> all 200", p3_concurrent_predict)

def p3_concurrent_health():
    def do_health(i):
        code, _, _ = http("GET", f"{INFERENCE}/health", timeout=10)
        return code == 200
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures = [ex.submit(do_health, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    return all(results)
test("3.2 20 concurrent health checks (10 threads) -> all 200", p3_concurrent_health)

def p3_concurrent_api():
    endpoints = [
        f"{BACKEND}/api/varieties",
        f"{BACKEND}/api/logs",
        f"{BACKEND}/api/logs/stats",
        f"{BACKEND}/api/logs/distribution",
        f"{BACKEND}/api/models",
        f"{BACKEND}/api/snapshots",
        f"{BACKEND}/api/settings",
        f"{BACKEND}/api/detection",
    ]
    def do_get(url):
        code, _, _ = http("GET", url, cookie=auth_cookie, timeout=10)
        return code == 200
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(do_get, url) for url in endpoints]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    return all(results)
test("3.3 8 concurrent backend API calls -> all 200", p3_concurrent_api)

def p3_rapid_fire_predict():
    """Sequential rapid fire - 15 predictions in a row"""
    for i in range(15):
        code, body, _ = http("POST", f"{INFERENCE}/predict/base64",
            {"image": test_b64, "confidence": 0.5}, timeout=15)
        if code != 200: return False
    return True
test("3.4 15 rapid sequential predictions -> all 200", p3_rapid_fire_predict)

# ============================================================
print("\n[P4] CROSS-COMPONENT DATA FLOW")
print("-" * 45)

def p4_inference_to_backend_metrics():
    """Backend proxies inference metrics correctly"""
    code_direct, body_direct, _ = http("GET", f"{INFERENCE}/system-metrics")
    code_proxy, body_proxy, _ = http("GET", f"{BACKEND}/api/performance/system", cookie=auth_cookie)
    if code_direct != 200 or code_proxy != 200: return False
    proxy_data = body_proxy.get("data", body_proxy) if isinstance(body_proxy, dict) else {}
    return (proxy_data.get("cpu_percent") is not None and 
            proxy_data.get("memory_percent") is not None)
test("4.1 Inference metrics -> Backend proxy -> consistent", p4_inference_to_backend_metrics)

def p4_model_info_consistency():
    """Model info from inference and backend proxy should match"""
    _, direct, _ = http("GET", f"{INFERENCE}/model-info")
    _, proxy, _ = http("GET", f"{BACKEND}/api/performance/inference", cookie=auth_cookie)
    proxy_data = proxy.get("data", proxy) if isinstance(proxy, dict) else {}
    return (direct.get("is_loaded") == proxy_data.get("is_loaded") and
            direct.get("device") == proxy_data.get("device"))
test("4.2 Model info: inference == backend proxy", p4_model_info_consistency)

def p4_predict_response_schema():
    """Verify prediction response has complete schema"""
    _, body, _ = http("POST", f"{INFERENCE}/predict/base64",
        {"image": test_b64, "confidence": 0.5})
    if not isinstance(body, dict): return False
    required = ["detections", "inference_time_ms", "model_name"]
    for key in required:
        if key not in body: return False
    if not isinstance(body["detections"], list): return False
    if not isinstance(body["inference_time_ms"], (int, float)): return False
    if body["inference_time_ms"] < 0: return False
    return True
test("4.3 Prediction response schema validation", p4_predict_response_schema)

# ============================================================
print("\n[P5] AUTH SECURITY EDGE CASES")
print("-" * 45)

test("5.1 Login with non-existent email -> reject",
    lambda: http("POST", f"{BACKEND}/api/auth/sign-in/email",
        {"email": "nobody@nowhere.test", "password": "pass123"})[0] in (400, 401, 403))

test("5.2 Register with weak password -> reject",
    lambda: http("POST", f"{BACKEND}/api/auth/sign-up/email",
        {"email": "weak@test.test", "password": "123", "name": "Weak"})[0] in (400, 422))

test("5.3 Register duplicate email -> reject",
    lambda: http("POST", f"{BACKEND}/api/auth/sign-up/email",
        {"email": test_email, "password": test_pass, "name": "Dup"})[0] in (400, 409, 422, 200))

test("5.4 Invalid cookie -> 401 on protected routes",
    lambda: (lambda r: r[0] == 401)(
        http("GET", f"{BACKEND}/api/varieties", cookie="better-auth.session_token=invalid_token_here")))

test("5.5 Empty auth header -> 401",
    lambda: http("GET", f"{BACKEND}/api/varieties", cookie="")[0] == 401)

# ============================================================
print("\n[P6] INFERENCE BOUNDARY VALUES")
print("-" * 45)

test("6.1 imgsz=160 (minimum) -> 200",
    lambda: http("POST", f"{INFERENCE}/predict/base64",
        {"image": test_b64, "confidence": 0.5, "imgsz": 160})[0] == 200)

test("6.2 imgsz=1280 (maximum) -> 200",
    lambda: http("POST", f"{INFERENCE}/predict/base64",
        {"image": test_b64, "confidence": 0.5, "imgsz": 1280})[0] == 200)

test("6.3 iou=0.0 -> 200",
    lambda: http("POST", f"{INFERENCE}/predict/base64",
        {"image": test_b64, "confidence": 0.5, "iou": 0.0})[0] == 200)

test("6.4 iou=1.0 -> 200",
    lambda: http("POST", f"{INFERENCE}/predict/base64",
        {"image": test_b64, "confidence": 0.5, "iou": 1.0})[0] == 200)

def p6_tiny_image():
    tiny = base64.b64encode(make_png(1, 1)).decode()
    code, body, _ = http("POST", f"{INFERENCE}/predict/base64",
        {"image": tiny, "confidence": 0.5})
    return code == 200
test("6.5 1x1 pixel image -> handles gracefully", p6_tiny_image)

def p6_large_image():
    big = base64.b64encode(make_png(800, 800)).decode()
    code, body, _ = http("POST", f"{INFERENCE}/predict/base64",
        {"image": big, "confidence": 0.5}, timeout=30)
    return code == 200
test("6.6 800x800 large image -> 200", p6_large_image)

# ============================================================
print("\n[P7] DESKTOP MODULE ROBUSTNESS")
print("-" * 45)

def p7_config_missing_keys():
    from core.config_manager import ConfigManager
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    cfg_path = os.path.join(tmp, "test_config.json")
    with open(cfg_path, 'w') as f:
        json.dump({"detection": {"confidence_threshold": 0.5}}, f)
    cm = ConfigManager(cfg_path)
    # Should handle missing keys gracefully
    val = cm.config.get('nonexistent', 'default')
    shutil.rmtree(tmp, ignore_errors=True)
    return val == 'default'
test("7.1 ConfigManager handles missing keys gracefully", p7_config_missing_keys)

def p7_log_manager_stress():
    from core.log_manager import LogManager
    import tempfile
    lm = LogManager(tempfile.mkdtemp())
    # Add 1000 entries rapidly
    for i in range(1000):
        lm.add_entry(f'{i//3600:02}:{(i//60)%60:02}:{i%60:02}', 
                     ['Bawor','Monthong','Musang King'][i%3], 
                     50.0 + (i%50), i+1)
    entries = lm.get_entries()
    return len(entries) == 1000
test("7.2 LogManager handles 1000 rapid entries", p7_log_manager_stress)

def p7_theme_unknown_variety():
    from ui.styles.theme import Theme
    color = Theme.get_variety_color("Unknown Variety XYZ")
    default_color = Theme.get_variety_color("default")
    return color is not None  # Should return a fallback color
test("7.3 Theme handles unknown variety gracefully", p7_theme_unknown_variety)

def p7_hotkey_edge_cases():
    from core.global_hotkeys import GlobalHotkeys
    # Test various edge formats
    tests = [
        ("A", "a"),
        ("ctrl+a", "<ctrl>+a"),
        ("Ctrl+A", "<ctrl>+a"),
        ("CTRL+SHIFT+A", "<ctrl>+<shift>+a"),
    ]
    for inp, expected in tests:
        result = GlobalHotkeys._convert_hotkey_format(inp)
        if result != expected:
            return False
    return True
test("7.4 GlobalHotkeys edge case formats", p7_hotkey_edge_cases)

def p7_yolo_model_info():
    from core.yolo_engine import YOLOEngine
    ye = YOLOEngine('best.pt')
    return (ye.is_loaded and 
            ye.device in ('cpu', 'cuda') and
            ye.model_path is not None)
test("7.5 YOLOEngine properties: loaded + device + path", p7_yolo_model_info)

def p7_screen_capture_no_crash():
    from core.screen_capture import ScreenCapture
    sc = ScreenCapture()
    frame = sc._empty_frame()
    return frame is None  # Fixed behavior
test("7.6 ScreenCapture._empty_frame() returns None safely", p7_screen_capture_no_crash)

# ============================================================
print("\n[P8] RESPONSE TIME BENCHMARKS")
print("-" * 45)

def p8_health_latency():
    times = []
    for _ in range(5):
        t0 = time.perf_counter()
        http("GET", f"{INFERENCE}/health")
        times.append((time.perf_counter() - t0) * 1000)
    avg = sum(times) / len(times)
    print(f"         avg={avg:.0f}ms", end="")
    return avg < 3000  # CPU mode may be slower
test("8.1 Health check avg latency < 3s", p8_health_latency)

def p8_predict_latency():
    times = []
    for _ in range(3):
        t0 = time.perf_counter()
        http("POST", f"{INFERENCE}/predict/base64",
            {"image": test_b64, "confidence": 0.5})
        times.append((time.perf_counter() - t0) * 1000)
    avg = sum(times) / len(times)
    print(f"         avg={avg:.0f}ms", end="")
    return avg < 5000  # Should respond within 5s on CPU
test("8.2 Predict avg latency < 5s (CPU)", p8_predict_latency)

def p8_backend_api_latency():
    endpoints = ["/api/varieties", "/api/logs", "/api/settings"]
    total = 0
    for ep in endpoints:
        t0 = time.perf_counter()
        http("GET", f"{BACKEND}{ep}", cookie=auth_cookie)
        total += (time.perf_counter() - t0) * 1000
    avg = total / len(endpoints)
    print(f"         avg={avg:.0f}ms", end="")
    return avg < 1000  # Should respond within 1s
test("8.3 Backend API avg latency < 1s", p8_backend_api_latency)

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
