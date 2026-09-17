"""Verifikasi perbaikan audit DurianVision — perilaku fix yang tidak tercakup suite lama."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import tempfile

passed = 0
failed = 0

def check(name, fn):
    global passed, failed
    try:
        ok = fn()
        if ok is False:
            raise AssertionError('returned False')
        print(f"  [OK] {name}")
        passed += 1
    except Exception as e:
        print(f"  [GAGAL] {name} — {type(e).__name__}: {e}")
        failed += 1

print("=" * 60)
print("  VERIFIKASI PERBAIKAN AUDIT DURIANVISION")
print("=" * 60)

print("\n[A] Settings save-dir (ui/app.py)")
from ui.app import DurianVisionApp
from core.paths import get_user_data_dir

def t_resolve_relative():
    d = DurianVisionApp._resolve_dir('dv_test_tmp_dir', get_user_data_dir())
    assert os.path.isabs(d) and os.path.isdir(d), d
    os.rmdir(d)
    return True

def t_resolve_default():
    return DurianVisionApp._resolve_dir('', get_user_data_dir()) == get_user_data_dir()

def t_resolve_abs():
    tmp = tempfile.mkdtemp()
    d = DurianVisionApp._resolve_dir(tmp, get_user_data_dir())
    assert d == tmp and os.path.isdir(tmp)
    os.rmdir(tmp)
    return True

check("A1 save-dir relatif -> absolut & dibuat", t_resolve_relative)
check("A2 save-dir kosong -> default", t_resolve_default)
check("A3 save-dir absolut dipertahankan", t_resolve_abs)

print("\n[B] Global hotkeys guard (core/global_hotkeys.py)")
from core.global_hotkeys import GlobalHotkeys, _typing_context

check("B1 Space -> <space>", lambda: GlobalHotkeys._convert_hotkey_format('Space') == '<space>')
check("B2 Ctrl+Shift+D -> <ctrl>+<shift>+d", lambda: GlobalHotkeys._convert_hotkey_format('Ctrl+Shift+D') == '<ctrl>+<shift>+d')
check("B3 bare key terdeteksi", lambda: GlobalHotkeys._is_bare_key('<space>') and not GlobalHotkeys._is_bare_key('<ctrl>+<shift>+d'))
check("B4 typing-context aman dipanggil", lambda: isinstance(_typing_context(), bool))

print("\n[C] YOLO engine (core/yolo_engine.py)")
from core.yolo_engine import YOLOEngine

engine = YOLOEngine('best.pt', device='cpu')

check("C1 model termuat", lambda: engine.is_loaded)
check("C2 DirectML -> CPU (tidak brick)", lambda: engine._resolve_device('directml') == 'cpu')
check("C3 CUDA tanpa GPU -> CPU", lambda: engine._resolve_device('cuda') == 'cpu')
check("C4 lock inference tersedia", lambda: hasattr(engine, '_lock'))
check("C5 two-stage fallback tanpa classifier", lambda: engine.is_two_stage is False)
check("C6 predict aman saat kosong", lambda: engine.predict(None, 0.5, 416) == [])

print("\n[D] Snapshot manager (core/snapshot_manager.py)")
from core.snapshot_manager import SnapshotManager

def t_wait_workers():
    return callable(getattr(SnapshotManager, 'wait_for_workers', None))

check("D1 wait_for_workers tersedia", t_wait_workers)

print("\n[E] Backend API (butuh server :3005)")
import json
import urllib.request
import urllib.error
import http.cookiejar

def _server_up():
    try:
        urllib.request.urlopen('http://localhost:3005/api/auth/get-session', timeout=3)
        return True
    except Exception:
        return False

def t_api_pagination():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    def post(url, data=None):
        req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None,
                                     headers={'Content-Type': 'application/json', 'Origin': 'http://localhost:5173'}, method='POST')
        return op.open(req)
    def get(url):
        return op.open(urllib.request.Request(url, headers={'Origin': 'http://localhost:5173'}))
    creds = {'email': 'faunas@gmail.com', 'password': 'faunas123'}
    try:
        post('http://localhost:3005/api/auth/sign-in/email', creds)
    except Exception:
        post('http://localhost:3005/api/auth/sign-up/email', {'name': 'Faunas Test', **creds})
        post('http://localhost:3005/api/auth/sign-in/email', creds)
    r = json.loads(get('http://localhost:3005/api/logs?page=1&limit=2').read())
    assert 'meta' in r and 'totalPages' in r['meta'] and 'total' in r['meta'], r.get('meta')
    v = json.loads(get('http://localhost:3005/api/varieties').read())
    names = [x['name'] for x in v['data']]
    assert 'Black Thorn' in names, names
    return True

if _server_up():
    check("E1 pagination meta + varieties Black Thorn", t_api_pagination)
else:
    print("  [SKIP] E1 server :3005 tidak berjalan")

print("\n" + "=" * 60)
print(f"  RESULTS: {passed} passed, {failed} failed")
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
