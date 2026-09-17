from ultralytics import YOLO

model = YOLO(r'D:\GUI Duren\durian-yolov11-results\weights\best.pt')
results = model(r'D:\GUI Duren\duren ngetes.jpeg')

for r in results:
    for box in r.boxes:
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        conf = float(box.conf[0])
        print(f'Detected: {cls_name} (Confidence: {conf:.2f})')

