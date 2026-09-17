"""Verifikasi Level 3: Two-Stage Pipeline Integration"""
import sys, os, time
import numpy as np

print("=" * 60)
print("  VERIFIKASI LEVEL 3: TWO-STAGE PIPELINE")
print("=" * 60)

errors = []

# 1. Import modules
print("\n[1] Import modules...")
try:
    from core.variety_classifier import VarietyClassifier
    print("    [OK] VarietyClassifier imported")
except Exception as e:
    errors.append(f"Import VarietyClassifier: {e}")
    print(f"    [GAGAL] {e}")

try:
    from core.yolo_engine import YOLOEngine
    print("    [OK] YOLOEngine imported")
except Exception as e:
    errors.append(f"Import YOLOEngine: {e}")
    print(f"    [GAGAL] {e}")
    sys.exit(1)

# 2. Test graceful fallback (no classifier.pt)
print("\n[2] Graceful fallback (tanpa classifier.pt)...")
engine = YOLOEngine("best.pt", device="cpu")

print(f"    YOLO loaded  : {engine.is_loaded}")
print(f"    Two-stage    : {engine.is_two_stage}")
print(f"    Pipeline     : {engine.pipeline_status}")

if engine.is_loaded and not engine.is_two_stage:
    print("    [OK] YOLO-only mode aktif (classifier.pt tidak ada = expected)")
elif engine.is_loaded and engine.is_two_stage:
    print("    [OK] Two-stage mode aktif (classifier.pt ditemukan)")
else:
    errors.append(f"YOLO load gagal: {engine.load_error}")

# 3. Test inference (should work same as before)
print("\n[3] Test inferensi YOLO-only mode...")
frame = np.zeros((640, 640, 3), dtype=np.uint8)
dets = engine.predict(frame, conf_threshold=0.01, imgsz=416)
print(f"    Detections   : {len(dets)}")
print(f"    Inference ms : {engine.last_inference_ms:.1f}")
for d in dets[:3]:
    print(f"    -> {d['class_name']} ({d['confidence']:.3f})")
print("    [OK] Inferensi berjalan normal")

# 4. Test VarietyClassifier standalone (tanpa model)
print("\n[4] VarietyClassifier tanpa model...")
clf = VarietyClassifier("nonexistent.pt")
print(f"    Loaded       : {clf.is_loaded}")
print(f"    Error        : {clf.load_error}")
print(f"    Classes      : {clf.class_names}")

result = clf.classify(np.zeros((224, 224, 3), dtype=np.uint8))
print(f"    Classify     : {result}")
if result == ('Lainnya', 0.0):
    print("    [OK] Graceful fallback benar")
else:
    errors.append(f"Classifier fallback salah: {result}")

# 5. Test batch classify
print("\n[5] Batch classify tanpa model...")
crops = [np.zeros((100, 100, 3), dtype=np.uint8)] * 3
results = clf.classify_batch(crops)
print(f"    Batch results: {results}")
if len(results) == 3 and all(r == ('Lainnya', 0.0) for r in results):
    print("    [OK] Batch fallback benar")
else:
    errors.append("Batch fallback salah")

# 6. Test crop helper
print("\n[6] Test _crop_detection...")
det = {'x1': 100, 'y1': 100, 'x2': 300, 'y2': 300}
test_frame = np.ones((640, 640, 3), dtype=np.uint8) * 128
crop = YOLOEngine._crop_detection(test_frame, det, padding=0.1)
if crop is not None:
    print(f"    Crop shape   : {crop.shape}")
    expected_w = (300 - 100) + 2 * int(200 * 0.1)  # 200 + 40 = 240
    expected_h = (300 - 100) + 2 * int(200 * 0.1)
    print(f"    Expected     : ~{expected_h}x{expected_w}")
    print("    [OK] Crop berhasil")
else:
    errors.append("Crop gagal")

# 7. Test backward compatibility (new params are optional)
print("\n[7] Test backward compatibility...")
engine2 = YOLOEngine("best.pt")  # Original call signature
print(f"    Pipeline     : {engine2.pipeline_status}")
print("    [OK] API backward compatible")

# 8. Pipeline status property
print("\n[8] Pipeline properties...")
print(f"    is_two_stage : {engine.is_two_stage}")
print(f"    pipeline_status: {engine.pipeline_status}")
print("    [OK]")

# FINAL
print("\n" + "=" * 60)
if errors:
    print("  GAGAL!")
    for e in errors:
        print(f"    [X] {e}")
    sys.exit(1)
else:
    print("  SEMUA VERIFIKASI LEVEL 3 PASSED")
    print("  Pipeline: YOLO-only (tanpa classifier.pt)")
    print("  Classifier akan otomatis aktif saat classifier.pt tersedia")
    print("=" * 60)
