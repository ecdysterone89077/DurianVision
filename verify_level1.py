"""Verifikasi Level 1 Fix — mapping, colors, config"""
import sys, os, json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

print("=" * 60)
print("  VERIFIKASI LEVEL 1 FIX")
print("=" * 60)

errors = []

# 1. Theme VARIETY_COLORS
from ui.styles.theme import Theme
print("\n[1] Theme VARIETY_COLORS:")
for name, color in Theme.VARIETY_COLORS.items():
    print(f"    {name:15s} -> {color}")
total = len(Theme.VARIETY_COLORS)
print(f"    Total: {total} varietas")
if "Black Thorn" not in Theme.VARIETY_COLORS:
    errors.append("Black Thorn MISSING dari VARIETY_COLORS")
else:
    print("    [OK] Black Thorn ada")

# 2. Theme MODEL_CLASS_MAP
print("\n[2] Theme MODEL_CLASS_MAP:")
for model_name, ui_name in Theme.MODEL_CLASS_MAP.items():
    print(f"    {model_name:15s} -> {ui_name}")
bt_map = Theme.MODEL_CLASS_MAP.get("black thorn")
if bt_map == "Montong":
    errors.append("black thorn MASIH dimapping ke Montong!")
elif bt_map == "Black Thorn":
    print("    [OK] black thorn -> Black Thorn (FIXED)")
else:
    errors.append(f"black thorn mapped to unexpected: {bt_map}")

# 3. YOLOEngine mapping
from core.yolo_engine import YOLOEngine
print("\n[3] YOLOEngine MODEL_CLASS_MAP:")
for model_name, ui_name in YOLOEngine.MODEL_CLASS_MAP.items():
    print(f"    {model_name:15s} -> {ui_name}")
if YOLOEngine.MODEL_CLASS_MAP.get("black thorn") != "Black Thorn":
    errors.append("YOLOEngine mapping salah")
else:
    print("    [OK] Engine mapping benar")

# 4. Config JSON
with open("config/default_config.json", "r") as f:
    cfg = json.load(f)
print("\n[4] Config varieties:")
for name, color in cfg["varieties"].items():
    print(f"    {name:15s} -> {color}")
cfg_total = len(cfg["varieties"])
if "Black Thorn" not in cfg["varieties"]:
    errors.append("Black Thorn MISSING dari config")
else:
    print(f"    [OK] Black Thorn ada ({cfg_total} total)")

# 5. Snapshot colors
from core.snapshot_manager import DEFAULT_VARIETY_COLORS_BGR
print("\n[5] Snapshot BGR colors:")
snap_total = len(DEFAULT_VARIETY_COLORS_BGR)
if "Black Thorn" not in DEFAULT_VARIETY_COLORS_BGR:
    errors.append("Black Thorn MISSING dari snapshot colors")
else:
    print(f"    [OK] Black Thorn ada ({snap_total} total)")

# 6. End-to-end color resolution
print("\n[6] End-to-end color resolution (model name -> UI name -> hex color):")
test_names = ["bawor", "black thorn", "kanyao", "monthong", "musang king", "not durian"]
for name in test_names:
    mapped = YOLOEngine.MODEL_CLASS_MAP.get(name, name)
    color = Theme.get_variety_color(mapped)
    print(f"    {name:15s} -> {mapped:15s} -> {color}")
    if color is None:
        errors.append(f"No color for {name}")

# 7. Test live inference mapping
print("\n[7] YOLO Live Inference Mapping Test:")
yolo = YOLOEngine("best.pt")
if yolo.is_loaded:
    import numpy as np
    frame = np.zeros((416, 416, 3), dtype=np.uint8)
    dets = yolo.predict(frame, conf_threshold=0.01, imgsz=416)
    print(f"    Detections: {len(dets)}")
    for d in dets[:5]:
        cn = d["class_name"]
        color = Theme.get_variety_color(cn)
        print(f"    -> class_name='{cn}', conf={d['confidence']:.3f}, color={color}")
        if cn in ["bawor", "black thorn", "monthong", "musang king", "kanyao", "not durian"]:
            errors.append(f"class_name '{cn}' is raw model name, should be UI name!")
    print("    [OK] Inference mapping verified")
else:
    print(f"    [SKIP] YOLO not loaded: {yolo.load_error}")

# FINAL
print("\n" + "=" * 60)
if errors:
    print("  GAGAL!")
    for e in errors:
        print(f"    [X] {e}")
    sys.exit(1)
else:
    print("  SEMUA VERIFIKASI LEVEL 1 PASSED")
    print("=" * 60)
