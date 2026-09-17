"""
==============================================================================
  DurianVision — YOLOv11 Training Script
==============================================================================
  Script untuk melatih model YOLOv11 mendeteksi varietas durian menggunakan
  dataset dari Roboflow.

  CARA PAKAI:
  -----------
  1. Download dataset dari Roboflow dalam format "YOLOv11" atau "YOLOv8"
     (formatnya sama — folder images/ dan labels/ dengan file data.yaml)

  2. Ekstrak ke folder: d:\GUI Duren\training\dataset\
     Struktur harus seperti ini:
     
     training/
     └── dataset/
         ├── data.yaml          ← File konfigurasi dataset dari Roboflow
         ├── train/
         │   ├── images/        ← Gambar training (.jpg/.png)
         │   └── labels/        ← Label YOLO (.txt)
         ├── valid/
         │   ├── images/        ← Gambar validasi
         │   └── labels/        ← Label validasi
         └── test/              ← (opsional)
             ├── images/
             └── labels/

  3. Jalankan script:
     cd d:\GUI Duren\training
     python train.py

  4. Hasil training akan ada di:
     training/runs/detect/durian-yolov11/weights/best.pt

  CATATAN:
  - Pastikan NVIDIA GPU driver + CUDA sudah terinstall
  - Untuk cek GPU: python -c "import torch; print(torch.cuda.is_available())"
  - Training ~100 epoch dengan dataset kecil (~500 gambar) butuh ~30-60 menit
==============================================================================
"""

import os
import sys
import yaml
import shutil
from pathlib import Path
from datetime import datetime

# =============================================================================
# KONFIGURASI TRAINING — UBAH SESUAI KEBUTUHAN
# =============================================================================

# Model base YOLOv11 (dari kecil ke besar, makin besar makin akurat tapi lambat)
# Pilihan: "yolo11n.pt" (nano), "yolo11s.pt" (small), "yolo11m.pt" (medium),
#          "yolo11l.pt" (large), "yolo11x.pt" (extra-large)
BASE_MODEL = "yolo11n.pt"  # Nano — cepat & ringan, cocok untuk real-time

# Jumlah epoch (putaran training). Lebih banyak = lebih akurat, tapi lebih lama.
# Rekomendasi: 100-300 untuk dataset kecil, 50-100 untuk dataset besar
EPOCHS = 150

# Ukuran gambar saat training (px). Harus kelipatan 32.
# 640 = standar, 416 = lebih cepat (untuk smartphone), 320 = tercepat
IMAGE_SIZE = 640

# Batch size — tergantung VRAM GPU Anda:
# RTX 3060 (12GB): batch 16
# RTX 3070/3080 (8-10GB): batch 8-12
# RTX 4090 (24GB): batch 32
# Jika CUDA OOM error, kurangi angka ini
BATCH_SIZE = 16

# Device: 0 = GPU pertama, "cpu" = tanpa GPU (sangat lambat)
DEVICE = 0

# Patience untuk early stopping — berhenti otomatis jika tidak ada perbaikan
# setelah N epoch berturut-turut
PATIENCE = 30

# Learning rate awal
LEARNING_RATE = 0.01

# Workers untuk data loading (sesuaikan dengan jumlah CPU core)
WORKERS = 4

# Nama project & run
PROJECT_NAME = "runs/detect"
RUN_NAME = "durian-yolov11"

# Path dataset
DATASET_DIR = Path(__file__).parent / "dataset"
DATA_YAML = DATASET_DIR / "data.yaml"

# =============================================================================
# DAFTAR VARIETAS DURIAN (10 kelas)
# Pastikan urutan ini SAMA dengan yang ada di data.yaml dari Roboflow!
# =============================================================================

EXPECTED_CLASSES = [
    "Bawor",
    "Montong",
    "Musang King",
    "Petruk",
    "Monthong",
    "Sunan",
    "Kani",
    "Matahari",
    "Sitokong",
    "Lainnya",
]


def check_environment():
    """Periksa apakah environment sudah siap untuk training."""
    print("=" * 60)
    print("  🍈 DurianVision — YOLOv11 Training Environment Check")
    print("=" * 60)

    # Check Python version
    py_ver = sys.version_info
    print(f"\n✅ Python {py_ver.major}.{py_ver.minor}.{py_ver.micro}")

    # Check PyTorch + CUDA
    try:
        import torch

        print(f"✅ PyTorch {torch.__version__}")
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_mem / (1024**3)
            print(f"✅ CUDA tersedia — GPU: {gpu_name} ({vram:.1f} GB VRAM)")
        else:
            print("⚠️  CUDA TIDAK tersedia — training akan SANGAT LAMBAT di CPU!")
            response = input("   Lanjutkan dengan CPU? (y/n): ")
            if response.lower() != "y":
                sys.exit(1)
    except ImportError:
        print("❌ PyTorch tidak terinstall!")
        print("   Jalankan: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
        sys.exit(1)

    # Check ultralytics
    try:
        import ultralytics

        print(f"✅ Ultralytics {ultralytics.__version__}")
    except ImportError:
        print("❌ Ultralytics tidak terinstall!")
        print("   Jalankan: pip install ultralytics")
        sys.exit(1)

    print()


def validate_dataset():
    """Validasi struktur dataset dari Roboflow."""
    print("=" * 60)
    print("  📁 Validasi Dataset")
    print("=" * 60)

    # Check data.yaml exists
    if not DATA_YAML.exists():
        print(f"\n❌ File data.yaml tidak ditemukan di: {DATA_YAML}")
        print(f"   Pastikan dataset Roboflow sudah diekstrak ke: {DATASET_DIR}")
        print()
        print("   Struktur yang diharapkan:")
        print("   training/dataset/")
        print("   ├── data.yaml")
        print("   ├── train/")
        print("   │   ├── images/")
        print("   │   └── labels/")
        print("   └── valid/")
        print("       ├── images/")
        print("       └── labels/")
        sys.exit(1)

    # Read and validate data.yaml
    with open(DATA_YAML, "r", encoding="utf-8") as f:
        data_config = yaml.safe_load(f)

    print(f"\n✅ data.yaml ditemukan")

    # Check number of classes
    nc = data_config.get("nc", 0)
    names = data_config.get("names", [])
    print(f"   Jumlah kelas: {nc}")
    print(f"   Nama kelas: {names}")

    # Check train/valid folders
    for split in ["train", "valid"]:
        img_dir = DATASET_DIR / split / "images"
        lbl_dir = DATASET_DIR / split / "labels"

        if not img_dir.exists():
            # Try alternative structure (some Roboflow exports use different paths)
            alt_img_dir = DATASET_DIR / split
            if alt_img_dir.exists():
                print(f"⚠️  Folder {split}/images/ tidak ada, cek struktur alternatif...")
            else:
                print(f"❌ Folder {split}/images/ tidak ditemukan!")
                sys.exit(1)
        else:
            img_count = len(list(img_dir.glob("*.[jJ][pP][gG]")) + list(img_dir.glob("*.[pP][nN][gG]")))
            lbl_count = len(list(lbl_dir.glob("*.txt"))) if lbl_dir.exists() else 0
            print(f"   {split}: {img_count} gambar, {lbl_count} label")

    # Fix data.yaml paths to be absolute
    fix_data_yaml(data_config)

    print(f"\n✅ Dataset valid!")
    print()

    return data_config


def fix_data_yaml(data_config: dict):
    """
    Perbaiki path di data.yaml agar menggunakan absolute path.
    Roboflow sering export dengan relative path yang salah.
    """
    # Build corrected config
    corrected = data_config.copy()

    # Fix paths
    train_path = DATASET_DIR / "train" / "images"
    valid_path = DATASET_DIR / "valid" / "images"
    test_path = DATASET_DIR / "test" / "images"

    corrected["train"] = str(train_path) if train_path.exists() else str(DATASET_DIR / "train")
    corrected["val"] = str(valid_path) if valid_path.exists() else str(DATASET_DIR / "valid")

    if test_path.exists():
        corrected["test"] = str(test_path)
    elif (DATASET_DIR / "test").exists():
        corrected["test"] = str(DATASET_DIR / "test")

    # Write corrected data.yaml
    corrected_path = DATASET_DIR / "data_corrected.yaml"
    with open(corrected_path, "w", encoding="utf-8") as f:
        yaml.dump(corrected, f, default_flow_style=False, allow_unicode=True)

    print(f"   📝 Path diperbaiki → {corrected_path}")

    return corrected_path


def train():
    """Jalankan training YOLOv11."""
    from ultralytics import YOLO

    print("=" * 60)
    print("  🚀 Mulai Training YOLOv11")
    print("=" * 60)
    print(f"\n  Model dasar : {BASE_MODEL}")
    print(f"  Epochs      : {EPOCHS}")
    print(f"  Image size  : {IMAGE_SIZE}")
    print(f"  Batch size  : {BATCH_SIZE}")
    print(f"  Device      : {'GPU' if DEVICE != 'cpu' else 'CPU'}")
    print(f"  Patience    : {PATIENCE}")
    print(f"  LR          : {LEARNING_RATE}")
    print()

    # Path to corrected data.yaml
    data_yaml_path = DATASET_DIR / "data_corrected.yaml"
    if not data_yaml_path.exists():
        data_yaml_path = DATA_YAML

    # Load base model (auto-downloads if not present)
    print(f"📥 Memuat model dasar {BASE_MODEL}...")
    model = YOLO(BASE_MODEL)

    # Start training
    print("\n🏋️ Training dimulai...\n")
    start_time = datetime.now()

    results = model.train(
        data=str(data_yaml_path),
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        device=DEVICE,
        patience=PATIENCE,
        lr0=LEARNING_RATE,
        project=PROJECT_NAME,
        name=RUN_NAME,
        exist_ok=True,
        # Augmentasi data
        hsv_h=0.015,       # Variasi hue
        hsv_s=0.7,         # Variasi saturasi
        hsv_v=0.4,         # Variasi brightness
        degrees=10.0,      # Rotasi ±10°
        translate=0.1,      # Translasi
        scale=0.5,          # Skala
        fliplr=0.5,         # Flip horizontal 50%
        flipud=0.0,         # Tidak flip vertikal (durian punya orientasi)
        mosaic=1.0,         # Mosaic augmentation
        mixup=0.1,          # Mixup augmentation
        # Optimisasi
        optimizer="auto",
        cos_lr=True,        # Cosine learning rate scheduler
        close_mosaic=10,    # Matikan mosaic di 10 epoch terakhir
        # Output
        save=True,
        save_period=25,     # Simpan checkpoint setiap 25 epoch
        plots=True,         # Buat grafik training
        verbose=True,
    )

    elapsed = datetime.now() - start_time
    print(f"\n{'=' * 60}")
    print(f"  ✅ Training selesai dalam {elapsed}")
    print(f"{'=' * 60}")

    return results


def validate_and_export(results):
    """Validasi model dan copy best.pt ke lokasi yang mudah ditemukan."""
    from ultralytics import YOLO

    # Path ke best.pt
    best_pt = Path(PROJECT_NAME) / RUN_NAME / "weights" / "best.pt"

    if not best_pt.exists():
        print(f"❌ best.pt tidak ditemukan di {best_pt}")
        return

    print(f"\n📊 Menjalankan validasi pada model terbaik...")
    model = YOLO(str(best_pt))

    # Validate
    data_yaml_path = DATASET_DIR / "data_corrected.yaml"
    if not data_yaml_path.exists():
        data_yaml_path = DATA_YAML

    metrics = model.val(data=str(data_yaml_path))

    print(f"\n{'=' * 60}")
    print(f"  📊 Hasil Validasi")
    print(f"{'=' * 60}")
    print(f"  mAP50     : {metrics.box.map50:.4f}")
    print(f"  mAP50-95  : {metrics.box.map:.4f}")
    print(f"  Precision : {metrics.box.mp:.4f}")
    print(f"  Recall    : {metrics.box.mr:.4f}")

    # Copy best.pt to easy-to-find location
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    output_pt = output_dir / "best.pt"
    shutil.copy2(best_pt, output_pt)

    # Also copy to inference package location if it exists
    inference_models = Path(__file__).parent.parent / "packages" / "inference" / "models"
    if inference_models.parent.exists():
        inference_models.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_pt, inference_models / "best.pt")
        print(f"\n  📦 Model disalin ke: {inference_models / 'best.pt'}")

    print(f"\n  💾 Model terbaik disalin ke: {output_pt}")
    print(f"  📁 Grafik & log training di: {Path(PROJECT_NAME) / RUN_NAME}")
    print()
    print(f"  🎯 Gunakan file ini untuk DurianVision:")
    print(f"     {output_pt.resolve()}")
    print()


def main():
    """Main training pipeline."""
    print()
    print("  🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈")
    print("  🍈                                        🍈")
    print("  🍈   DurianVision — YOLOv11 Trainer       🍈")
    print("  🍈   Deteksi 10 Varietas Durian           🍈")
    print("  🍈                                        🍈")
    print("  🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈🍈")
    print()

    # Step 1: Check environment
    check_environment()

    # Step 2: Validate dataset
    data_config = validate_dataset()

    # Step 3: Confirm before training
    print("=" * 60)
    print("  ⚡ Siap untuk training!")
    print("=" * 60)
    response = input("\n  Mulai training? (y/n): ")
    if response.lower() != "y":
        print("  Dibatalkan.")
        return

    # Step 4: Train
    results = train()

    # Step 5: Validate & export
    validate_and_export(results)

    print("  🎉 Selesai! Model best.pt siap digunakan.")
    print()


if __name__ == "__main__":
    main()
