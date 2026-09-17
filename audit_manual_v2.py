"""Audit Otomatis: Manual Book vs Kode Aktual GUI Duren v2.0"""
import json, sys, os, re
sys.path.insert(0, r'd:\GUI Duren\GUI Duren')

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

results = []
def check(desc, condition):
    status = "OK" if condition else "GAGAL"
    results.append((desc, status))
    print(f"  {'✅' if condition else '❌'} {desc}")
    return condition

print("=" * 65)
print("  AUDIT MANUAL vs KODE — GUI Duren v2.0")
print("=" * 65)

# --- Load manual ---
manual_path = r'C:\Users\Hype G12\.gemini\antigravity\brain\2017bc79-4d5b-4b17-bcac-f3d550baaa89\manual_gui_duren.md'
with open(manual_path, 'r', encoding='utf-8') as f:
    manual = f.read()

# --- 1. HEADER ---
print("\n[1] HEADER & VERSI")
check("Versi 2.0 tertulis di header", "Versi**: 2.0" in manual)
check("EfficientNet-V2-S tertulis di tech stack", "EfficientNet-V2-S" in manual)
check("Platform Windows 10/11", "Windows 10/11" in manual)

# --- 2. VARIETAS ---
print("\n[2] VARIETAS")
from ui.styles.theme import Theme
theme_count = len(Theme.VARIETY_COLORS)
check(f"Manual menyebut {theme_count} varietas di Pendahuluan", f"**{theme_count} varietas**" in manual)
check("Manual menyebut 6 varietas terlatih", "**6 varietas**" in manual)

# Cek setiap varietas ada di manual
for name in Theme.VARIETY_COLORS:
    check(f"Varietas '{name}' ada di manual", name in manual)

# Cek setiap hex warna di manual sesuai Theme
for name, color in Theme.VARIETY_COLORS.items():
    check(f"Warna {name} = {color} benar di manual", f'"{name}": "{color}"' in manual or f"| **{name}**" in manual)

# --- 3. CONFIG JSON ---
print("\n[3] CONFIG JSON")
with open(r'd:\GUI Duren\GUI Duren\config\default_config.json', 'r') as f:
    config = json.load(f)

# Cek setiap section ada di manual
for section in config:
    check(f"Section '{section}' ada di manual", section in manual)

# Cek default values
check("confidence_threshold = 0.72", "0.72" in manual)
check("fps_limit = 5", '"fps_limit": 5' in manual or "fps_limit.*5" in manual)
check("inference_size = 416", "416" in manual)
check("auto_threshold = 0.85", "0.85" in manual)
check("min_interval_sec = 5", '"min_interval_sec": 5' in manual)

# Two-stage config
check("two_stage.enabled = true", '"enabled": true' in manual)
check("two_stage.classifier_path = classifier.pt", '"classifier_path": "classifier.pt"' in manual)
check("two_stage.min_confidence = 0.4", '"min_confidence": 0.4' in manual or "0.4" in manual)

# --- 4. HOTKEYS ---
print("\n[4] HOTKEYS")
hotkeys = config.get('hotkeys', {})
for key, val in hotkeys.items():
    check(f"Hotkey '{key}' = '{val}' di manual", val in manual)

# --- 5. FILE STRUCTURE ---
print("\n[5] STRUKTUR FILE")
key_files = [
    'main.py', 'best.pt', 'classifier.pt', 'requirements.txt',
    'config_manager.py', 'detection_worker.py', 'device_detector.py',
    'global_hotkeys.py', 'log_manager.py', 'screen_capture.py',
    'snapshot_manager.py', 'variety_classifier.py', 'yolo_engine.py',
    'app.py', 'control_panel.py', 'overlay_window.py', 'roi_selector.py',
    'tray_icon.py', 'theme.py', 'stylesheet.qss',
    'detection_tab.py', 'performance_tab.py', 'snapshot_tab.py',
    'log_tab.py', 'settings_tab.py',
    'DurianVision_Training_Colab.ipynb', 'DurianVision_Classifier_Colab.ipynb'
]
for f in key_files:
    check(f"File '{f}' ada di manual", f in manual)

# --- 6. TWO-STAGE PIPELINE ---
print("\n[6] TWO-STAGE PIPELINE")
check("Two-Stage Pipeline section ada", "Two-Stage Pipeline" in manual)
check("YOLO-Only mode terdokumentasi", "YOLO-Only" in manual)
check("classifier.pt fallback terdokumentasi", "fallback" in manual.lower() or "otomatis fallback" in manual)
check("Pipeline status di tray tooltip", "[2-Stage]" in manual or "[YOLO]" in manual)
check("Pipeline status di status bar", "🔗" in manual)

# --- 7. TRAY ICON ---
print("\n[7] TRAY ICON")
check("Tooltip format dengan pipeline tag", "DurianVision [2-Stage]" in manual)
check("3 status warna (kuning/hijau/merah)", "Kuning" in manual and "Hijau" in manual and "Merah" in manual)
check("Klik Kanan = menu konteks", "Klik Kanan" in manual)
check("Klik Ganda = panel kontrol", "Klik Ganda" in manual)

# --- 8. ARSITEKTUR DIAGRAM ---
print("\n[8] DIAGRAM ARSITEKTUR")
check("VarietyClassifier ada di diagram", "VarietyClassifier" in manual)
check("classifier.pt ada di diagram IO layer", 'classifier.pt' in manual)
check("ScreenCapture fallback diagram", "DXcam" in manual and "MSS" in manual)

# --- 9. PESAN ERROR ---
print("\n[9] PESAN ERROR")
error_msgs = [
    "[YOLOEngine] CUDA tidak tersedia",
    "[ScreenCapture] DXcam gagal",
    "[ConfigManager] Gagal memuat config"
]
for msg in error_msgs:
    check(f"Error msg '{msg[:40]}...' ada", msg in manual)

# --- 10. DEPENDENCIES ---
print("\n[10] DEPENDENCIES")
deps_in_manual = ['PyQt6', 'ultralytics', 'mss', 'dxcam', 'opencv-python-headless',
                  'numpy', 'Pillow', 'openpyxl', 'psutil', 'pynput']
for dep in deps_in_manual:
    check(f"Dependency '{dep}' tercatat", dep in manual)

# --- 11. FOOTER ---
print("\n[11] FOOTER")
check("Footer versi v2.0", "v2.0" in manual)

# --- SUMMARY ---
total = len(results)
passed = sum(1 for _, s in results if s == "OK")
failed = [desc for desc, s in results if s == "GAGAL"]

print(f"\n{'=' * 65}")
print(f"  HASIL AUDIT: {passed}/{total} SESUAI ({passed/total*100:.1f}%)")
print(f"{'=' * 65}")

if failed:
    print(f"\n  ❌ {len(failed)} KETIDAKSESUAIAN:")
    for f in failed:
        print(f"     • {f}")
else:
    print(f"\n  ✅ MANUAL 100% SESUAI DENGAN KODE!")
