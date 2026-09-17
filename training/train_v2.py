"""
==============================================================================
  DurianVision — YOLOv11 Training V2 (Enhanced)
==============================================================================
  Perbaikan dari train.py v1:
  - Model lebih besar (yolo11m default, bukan nano)
  - Augmentasi lebih agresif untuk fine-grained classification
  - Class-weighted training untuk mengatasi dataset imbalance
  - Auto-analyze dataset sebelum training
  - Confusion matrix + per-class metrics setelah training
  - Export best.pt ke root project otomatis

  CARA PAKAI:
  -----------
  cd d:\\GUI Duren\\GUI Duren\\training
  python train_v2.py

  OPSI:
  python train_v2.py --model yolo11l.pt    # Pakai model large
  python train_v2.py --epochs 300          # Training lebih lama
  python train_v2.py --batch 8             # Batch kecil (VRAM terbatas)
  python train_v2.py --imgsz 640           # Ukuran gambar
  python train_v2.py --analyze-only        # Hanya analisis dataset, tanpa training
==============================================================================
"""

import os
import sys
import yaml
import shutil
import argparse
import collections
from pathlib import Path
from datetime import datetime

# =============================================================================
# DEFAULT CONFIGURATION
# =============================================================================
DEFAULTS = {
    'model': 'yolo11m.pt',    # Medium — 20M params, good balance
    'epochs': 300,
    'imgsz': 640,
    'batch': 16,
    'device': 0,
    'patience': 50,
    'lr0': 0.01,
    'project': 'runs/detect',
    'name': 'durian-v2',
}

DATASET_DIR = Path(__file__).parent / "dataset"
DATA_YAML = DATASET_DIR / "data.yaml"


def analyze_dataset(data_dir: Path) -> dict:
    """Analisis lengkap dataset: distribusi kelas, ukuran bbox, dll."""
    print("\n" + "=" * 60)
    print("  📊 ANALISIS DATASET")
    print("=" * 60)

    # Read data.yaml
    yaml_path = data_dir / "data.yaml"
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    names = config.get('names', [])
    nc = config.get('nc', len(names))
    print(f"\n  Kelas: {nc}")
    print(f"  Nama : {names}")

    stats = {}
    for split in ['train', 'valid', 'test']:
        img_dir = data_dir / split / 'images'
        lbl_dir = data_dir / split / 'labels'
        
        if not img_dir.exists():
            continue
        
        img_count = len([f for f in os.listdir(img_dir) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        class_counts = collections.Counter()
        bbox_sizes = collections.defaultdict(list)
        total_ann = 0
        
        if lbl_dir.exists():
            for f in os.listdir(lbl_dir):
                if f.endswith('.txt'):
                    with open(lbl_dir / f) as fh:
                        for line in fh:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                cls = int(parts[0])
                                w = float(parts[3]) * 100
                                h = float(parts[4]) * 100
                                class_counts[cls] += 1
                                bbox_sizes[cls].append((w, h))
                                total_ann += 1
        
        stats[split] = {
            'images': img_count,
            'annotations': total_ann,
            'class_counts': dict(class_counts),
            'bbox_sizes': dict(bbox_sizes),
        }
        
        print(f"\n  [{split.upper()}] {img_count} gambar, {total_ann} anotasi")
        
        if class_counts:
            max_count = max(class_counts.values())
            for cls_id in sorted(class_counts):
                n = class_counts[cls_id]
                pct = n / total_ann * 100 if total_ann > 0 else 0
                bar = "█" * int(n / max_count * 20)
                name = names[cls_id] if cls_id < len(names) else f"class_{cls_id}"
                print(f"    [{cls_id}] {name:15s}: {n:5d} ({pct:5.1f}%) {bar}")
            
            # Imbalance ratio
            min_cls = min(class_counts.values())
            max_cls = max(class_counts.values())
            ratio = max_cls / min_cls if min_cls > 0 else float('inf')
            
            if ratio > 3:
                print(f"\n    ⚠️  IMBALANCE RATIO: {ratio:.1f}x (kelas terbanyak / tersedikit)")
                print(f"    ⚠️  Rekomendasi: Tambah data untuk kelas minoritas")
            else:
                print(f"\n    ✅ Balance ratio: {ratio:.1f}x (baik)")
    
    return stats


def fix_data_yaml() -> Path:
    """Fix paths in data.yaml to absolute paths."""
    with open(DATA_YAML, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    config['train'] = str(DATASET_DIR / 'train' / 'images')
    config['val'] = str(DATASET_DIR / 'valid' / 'images')
    
    test_path = DATASET_DIR / 'test' / 'images'
    if test_path.exists():
        config['test'] = str(test_path)
    
    corrected = DATASET_DIR / 'data_v2.yaml'
    with open(corrected, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\n  📝 data_v2.yaml → {corrected}")
    return corrected


def train(args) -> None:
    """Run enhanced training."""
    from ultralytics import YOLO
    
    print("\n" + "=" * 60)
    print("  🚀 TRAINING YOLOv11 (Enhanced V2)")
    print("=" * 60)
    
    print(f"\n  Model     : {args.model}")
    print(f"  Epochs    : {args.epochs}")
    print(f"  Image Size: {args.imgsz}")
    print(f"  Batch     : {args.batch}")
    print(f"  Device    : {'GPU' if args.device != 'cpu' else 'CPU'}")
    print(f"  Patience  : {args.patience}")
    
    data_yaml = fix_data_yaml()
    
    # Check GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_mem / (1024**3)
            print(f"\n  GPU: {gpu} ({vram:.1f} GB VRAM)")
        else:
            print("\n  ⚠️  CUDA tidak tersedia — menggunakan CPU (lambat)")
            args.device = 'cpu'
    except ImportError:
        print("\n  ⚠️  PyTorch tidak terinstall")
        args.device = 'cpu'
    
    model = YOLO(args.model)
    
    print("\n  🏋️ Training dimulai...\n")
    start = datetime.now()
    
    results = model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        patience=args.patience,
        lr0=args.lr0,
        project=DEFAULTS['project'],
        name=DEFAULTS['name'],
        exist_ok=True,
        
        # === AUGMENTASI AGRESIF (untuk fine-grained) ===
        hsv_h=0.02,        # Variasi hue lebih besar
        hsv_s=0.8,         # Variasi saturasi tinggi
        hsv_v=0.5,         # Variasi brightness tinggi
        degrees=15.0,       # Rotasi ±15°
        translate=0.15,     # Translasi 15%
        scale=0.6,          # Skala variasi 60%
        shear=5.0,          # Shear ±5°
        perspective=0.001,  # Sedikit perspektif
        fliplr=0.5,         # Flip horizontal
        flipud=0.0,         # Tidak flip vertikal
        mosaic=1.0,         # Mosaic ON
        mixup=0.2,          # Mixup 20%
        copy_paste=0.15,    # Copy-paste augmentation
        erasing=0.3,        # Random erasing 30%
        crop_fraction=0.2,  # Random crop
        
        # === TRAINING OPTIMIZATION ===
        optimizer='AdamW',   # AdamW lebih baik untuk fine-grained
        cos_lr=True,         # Cosine LR schedule
        close_mosaic=15,     # Matikan mosaic 15 epoch terakhir
        warmup_epochs=5,     # Warmup lebih lama
        weight_decay=0.001,  # Regularisasi
        
        # === OUTPUT ===
        save=True,
        save_period=50,
        plots=True,
        verbose=True,
    )
    
    elapsed = datetime.now() - start
    print(f"\n  ✅ Training selesai dalam {elapsed}")
    
    return results


def evaluate_and_export(args) -> None:
    """Evaluate the trained model and export best.pt."""
    from ultralytics import YOLO
    
    best_pt = Path(DEFAULTS['project']) / DEFAULTS['name'] / 'weights' / 'best.pt'
    
    if not best_pt.exists():
        print(f"\n  ❌ best.pt tidak ditemukan: {best_pt}")
        return
    
    print("\n" + "=" * 60)
    print("  📊 EVALUASI MODEL")
    print("=" * 60)
    
    model = YOLO(str(best_pt))
    
    data_yaml = DATASET_DIR / 'data_v2.yaml'
    if not data_yaml.exists():
        data_yaml = DATA_YAML
    
    metrics = model.val(data=str(data_yaml), plots=True)
    
    print(f"\n  Metrik Keseluruhan:")
    print(f"  ├── mAP50     : {metrics.box.map50:.4f}")
    print(f"  ├── mAP50-95  : {metrics.box.map:.4f}")
    print(f"  ├── Precision : {metrics.box.mp:.4f}")
    print(f"  └── Recall    : {metrics.box.mr:.4f}")
    
    # Per-class metrics
    if hasattr(metrics.box, 'ap50') and metrics.box.ap50 is not None:
        print(f"\n  Per-Kelas AP50:")
        names = model.names
        ap50 = metrics.box.ap50
        for i, ap in enumerate(ap50):
            name = names.get(i, f'class_{i}')
            bar = "█" * int(ap * 20)
            status = "✅" if ap > 0.7 else "⚠️" if ap > 0.5 else "❌"
            print(f"    {status} [{i}] {name:15s}: {ap:.4f} {bar}")
    
    # Copy best.pt to project root
    root_best = Path(__file__).parent.parent / 'best.pt'
    shutil.copy2(best_pt, root_best)
    print(f"\n  💾 Model disalin ke: {root_best}")
    
    # Also keep a backup
    backup_dir = Path(__file__).parent / 'output'
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f'best_v2_{timestamp}.pt'
    shutil.copy2(best_pt, backup_path)
    print(f"  💾 Backup disimpan: {backup_path}")
    
    print(f"\n  📁 Grafik & confusion matrix di: {Path(DEFAULTS['project']) / DEFAULTS['name']}")


def main():
    parser = argparse.ArgumentParser(description='DurianVision YOLOv11 Training V2')
    parser.add_argument('--model', default=DEFAULTS['model'], help='Base model (yolo11n/s/m/l/x.pt)')
    parser.add_argument('--epochs', type=int, default=DEFAULTS['epochs'])
    parser.add_argument('--imgsz', type=int, default=DEFAULTS['imgsz'])
    parser.add_argument('--batch', type=int, default=DEFAULTS['batch'])
    parser.add_argument('--device', default=DEFAULTS['device'])
    parser.add_argument('--patience', type=int, default=DEFAULTS['patience'])
    parser.add_argument('--lr0', type=float, default=DEFAULTS['lr0'])
    parser.add_argument('--analyze-only', action='store_true', help='Hanya analisis dataset')
    args = parser.parse_args()
    
    print()
    print("  🍈" * 20)
    print("  🍈  DurianVision — YOLOv11 Trainer V2 (Enhanced)")
    print("  🍈  Fine-Grained Durian Variety Detection")
    print("  🍈" * 20)
    
    # Step 1: Analyze dataset
    stats = analyze_dataset(DATASET_DIR)
    
    if args.analyze_only:
        print("\n  Mode analisis saja. Selesai.")
        return
    
    # Step 2: Confirm
    print("\n" + "=" * 60)
    print("  ⚡ Siap untuk training!")
    print("=" * 60)
    print(f"\n  Model  : {args.model}")
    print(f"  Epochs : {args.epochs}")
    print(f"  ImgSize: {args.imgsz}")
    
    response = input("\n  Mulai training? (y/n): ")
    if response.lower() != 'y':
        print("  Dibatalkan.")
        return
    
    # Step 3: Train
    train(args)
    
    # Step 4: Evaluate & export
    evaluate_and_export(args)
    
    print("\n  🎉 Selesai! Model best.pt sudah di-update.")
    print()


if __name__ == '__main__':
    main()
