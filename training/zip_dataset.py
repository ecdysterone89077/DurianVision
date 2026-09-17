"""
Script pembantu: Zip dataset untuk diupload ke Google Drive.
Jalankan di laptop sebelum membuka Colab.

Cara pakai:
  cd "d:\GUI Duren\GUI Duren\training"
  python zip_dataset.py

Hasil: dataset.zip siap upload ke Google Drive.
"""
import os
import sys
import zipfile
from pathlib import Path

DATASET_DIR = Path(__file__).parent / "dataset"
OUTPUT_ZIP = Path(__file__).parent / "dataset.zip"

def main():
    print("=" * 50)
    print("  🍈 DurianVision — Zip Dataset untuk Colab")
    print("=" * 50)

    if not DATASET_DIR.exists():
        print(f"\n❌ Folder dataset tidak ditemukan: {DATASET_DIR}")
        sys.exit(1)

    # Cek struktur
    required = ['data.yaml', 'train/images', 'train/labels', 'valid/images', 'valid/labels']
    for r in required:
        p = DATASET_DIR / r
        status = "✅" if p.exists() else "❌"
        print(f"  {status} {r}")
        if not p.exists():
            print(f"\n❌ Struktur dataset tidak lengkap!")
            sys.exit(1)

    # Hitung file
    img_count = 0
    lbl_count = 0
    for split in ['train', 'valid', 'test']:
        img_dir = DATASET_DIR / split / 'images'
        lbl_dir = DATASET_DIR / split / 'labels'
        if img_dir.exists():
            imgs = len([f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            img_count += imgs
        if lbl_dir.exists():
            lbls = len([f for f in os.listdir(lbl_dir) if f.endswith('.txt')])
            lbl_count += lbls

    print(f"\n  Total: {img_count} gambar, {lbl_count} label")

    # Zip
    print(f"\n📦 Membuat {OUTPUT_ZIP.name}...")

    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    file_count = 0
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(DATASET_DIR):
            for file in files:
                filepath = Path(root) / file
                arcname = filepath.relative_to(DATASET_DIR)
                zf.write(filepath, arcname)
                file_count += 1

    size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
    print(f"\n✅ Selesai!")
    print(f"   File : {OUTPUT_ZIP}")
    print(f"   Ukuran: {size_mb:.1f} MB")
    print(f"   Isi  : {file_count} file")

    print(f"\n📋 Langkah selanjutnya:")
    print(f"   1. Upload {OUTPUT_ZIP.name} ke Google Drive")
    print(f"   2. Buka DurianVision_Training_Colab.ipynb di Google Colab")
    print(f"   3. Pastikan Runtime → GPU (T4)")
    print(f"   4. Jalankan semua cell dari atas ke bawah")
    print(f"   5. Download best.pt hasil training")
    print(f"   6. Timpa d:\\GUI Duren\\GUI Duren\\best.pt dengan yang baru")

if __name__ == '__main__':
    main()
