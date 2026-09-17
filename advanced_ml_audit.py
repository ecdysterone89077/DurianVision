import os
import sys
import cv2
import numpy as np
import time
from collections import Counter
import glob
import json
import warnings
warnings.filterwarnings('ignore')

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from ultralytics import YOLO
except ImportError:
    print("[ERROR] Ultralytics tidak terinstal.")
    exit(1)

print("="*60)
print(" 🔬 ADVANCED ML-OPS AUDIT — GUI Duren v2.0")
print("="*60)

# --- 1. MODEL INTROSPECTION ---
print("\n[1] MODEL INTROSPECTION (best.pt)")
model_path = r'd:\GUI Duren\GUI Duren\best.pt'
if not os.path.exists(model_path):
    print("Model tidak ditemukan.")
else:
    model = YOLO(model_path)
    info = model.info()
    print(f"  • Task      : {model.task}")
    print(f"  • Classes   : {len(model.names)}")
    print(f"  • Names     : {model.names}")
    
    # Estimasi parameter (dari info, tuple format: (layers, params, gradients, flops))
    try:
        layers, params, _, _ = info
        print(f"  • Layers    : {layers}")
        print(f"  • Params    : {params:,} (Sangat kecil, rentan underfitting)")
    except:
        pass

# --- 2. FALSE POSITIVE STRESS TEST ---
print("\n[2] ADVERSARIAL & FALSE POSITIVE STRESS TEST")
# Buat gambar sintetik
img_noise = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

# Buat gambar mirip terminal (Hitam dengan teks hijau & garis keras)
img_terminal = np.zeros((640, 640, 3), dtype=np.uint8)
cv2.rectangle(img_terminal, (50, 50), (590, 590), (0, 255, 0), 2)
for i in range(10):
    cv2.putText(img_terminal, f"root@server:~# processing data line {i}...", (60, 100 + (i*40)), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

# Uji Noise
res_noise = model(img_noise, verbose=False)[0]
print(f"  • Uji Random Noise  : Ditemukan {len(res_noise.boxes)} objek.")
for box in res_noise.boxes:
    cls_id = int(box.cls[0].item())
    print(f"      -> Terdeteksi: {model.names[cls_id]} (Conf: {box.conf[0].item():.2f})")

# Uji Terminal
res_term = model(img_terminal, verbose=False)[0]
print(f"  • Uji Terminal Mock : Ditemukan {len(res_term.boxes)} objek.")
for box in res_term.boxes:
    cls_id = int(box.cls[0].item())
    print(f"      -> Terdeteksi: {model.names[cls_id]} (Conf: {box.conf[0].item():.2f})")

# --- 3. DATASET IMBALANCE SCANNER ---
print("\n[3] DATASET LABEL INTEGRITY SCAN")
dataset_path = r'd:\GUI Duren\GUI Duren\training\dataset\train\labels'
if os.path.exists(dataset_path):
    labels = glob.glob(os.path.join(dataset_path, '*.txt'))
    print(f"  • Ditemukan {len(labels)} file anotasi training.")
    
    class_counts = Counter()
    for lbl_file in labels:
        with open(lbl_file, 'r') as f:
            for line in f.readlines():
                parts = line.strip().split()
                if parts:
                    class_counts[int(parts[0])] += 1
    
    print("  • Distribusi Objek Aktual di Training Set:")
    total_objects = sum(class_counts.values())
    for cls_id in sorted(class_counts.keys()):
        count = class_counts[cls_id]
        pct = (count / total_objects) * 100
        name = model.names.get(cls_id, f"Class {cls_id}")
        bar = "█" * int(pct / 2)
        print(f"      [{cls_id}] {name:15} : {count:5} kotak ({pct:5.1f}%) | {bar}")
    
    if 0 in class_counts and 4 in class_counts:
        ratio = class_counts[0] / class_counts[4]
        print(f"\n  ⚠️ KESIMPULAN: Rasio Bawor vs Musang King adalah {ratio:.1f} : 1")
else:
    print("  • Folder dataset tidak ditemukan.")

# --- 4. LATENCY & MEMORY PROFILE ---
print("\n[4] INFERENCE PROFILING (100 frames)")
times = []
for _ in range(100):
    start = time.perf_counter()
    _ = model(img_noise, verbose=False)
    times.append(time.perf_counter() - start)

avg_ms = np.mean(times) * 1000
fps = 1000 / avg_ms
print(f"  • Rata-rata waktu inferensi (CPU) : {avg_ms:.1f} ms")
print(f"  • Estimasi Maksimum FPS (CPU)     : {fps:.1f} FPS")

print("\n" + "="*60)
print(" AUDIT SELESAI")
print("="*60)
