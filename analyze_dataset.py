import os, collections

label_dir = 'training/dataset/train/labels'
class_counts = collections.Counter()
total_annotations = 0

for f in os.listdir(label_dir):
    if f.endswith('.txt'):
        with open(os.path.join(label_dir, f)) as fh:
            for line in fh:
                parts = line.strip().split()
                if parts:
                    class_counts[int(parts[0])] += 1
                    total_annotations += 1

names = {0: 'bawor', 1: 'black thorn', 2: 'kanyao', 3: 'monthong', 4: 'musang king', 5: 'not durian'}

print(f"Total annotations: {total_annotations}")
for cls_id in sorted(class_counts):
    n = class_counts[cls_id]
    pct = n / total_annotations * 100
    bar = "#" * int(pct / 2)
    name = names.get(cls_id, "unknown")
    print(f"  [{cls_id}] {name:15s}: {n:5d} ({pct:5.1f}%) {bar}")

# Also check bbox sizes
print("\nAvg bbox sizes per class (width x height as % of image):")
bbox_sizes = collections.defaultdict(list)
for f in os.listdir(label_dir):
    if f.endswith('.txt'):
        with open(os.path.join(label_dir, f)) as fh:
            for line in fh:
                parts = line.strip().split()
                if len(parts) >= 5:
                    cls_id = int(parts[0])
                    w = float(parts[3]) * 100
                    h = float(parts[4]) * 100
                    bbox_sizes[cls_id].append((w, h))

for cls_id in sorted(bbox_sizes):
    sizes = bbox_sizes[cls_id]
    avg_w = sum(s[0] for s in sizes) / len(sizes)
    avg_h = sum(s[1] for s in sizes) / len(sizes)
    name = names.get(cls_id, "unknown")
    print(f"  [{cls_id}] {name:15s}: {avg_w:5.1f}% x {avg_h:5.1f}% (avg {len(sizes)} boxes)")
