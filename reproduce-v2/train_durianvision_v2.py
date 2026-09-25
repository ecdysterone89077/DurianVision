# DurianVision v2 — skrip latih reproduksibel (cermin Tabel 3 naskah)
# Pakai: python train_durianvision_v2.py --data <path>/data.yaml [--epochs 100 --batch 16 --imgsz 640]
import argparse
from ultralytics import YOLO

SEED = 0  # seed naskah; deterministic=True di bawah

def main():
    ap = argparse.ArgumentParser(description='Latih YOLOv11n DurianVision v2 (11 varietas)')
    ap.add_argument('--data', required=True, help='path data.yaml ekspor Roboflow v2')
    ap.add_argument('--epochs', type=int, default=100)
    ap.add_argument('--batch', type=int, default=16)
    ap.add_argument('--imgsz', type=int, default=640)
    ap.add_argument('--name', default='durianvision-v2')
    a = ap.parse_args()
    model = YOLO('yolo11n.pt')
    model.train(
        data=a.data, epochs=a.epochs, patience=20, batch=a.batch, imgsz=a.imgsz,
        optimizer='auto', amp=True, seed=SEED, deterministic=True,
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, fliplr=0.5, scale=0.5, translate=0.1,
        erasing=0.4, auto_augment='randaugment', name=a.name,
    )

if __name__ == '__main__':
    main()
