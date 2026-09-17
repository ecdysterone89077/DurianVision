from pathlib import Path
from ultralytics import YOLO

BASE = Path(__file__).resolve().parent
model = YOLO(str(BASE / 'models' / 'best.pt'))
results = model(str(BASE.parent.parent / 'duren ngetes.jpeg'))

for r in results:
    for box in r.boxes:
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        conf = float(box.conf[0])
        print(f'Detected: {cls_name} (Confidence: {conf:.2f})')
