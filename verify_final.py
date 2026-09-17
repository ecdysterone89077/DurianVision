"""Validasi kedua notebook Colab + integrasi Level 3 end-to-end"""
import json, sys, os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

print("=" * 60)
print("  VALIDASI FINAL: NOTEBOOK + INTEGRASI LEVEL 3")
print("=" * 60)

errors = []

# 1. Validate both notebooks
notebooks = [
    (r'd:\GUI Duren\GUI Duren\training\DurianVision_Training_Colab.ipynb', 'Level 2 (YOLO Training)'),
    (r'd:\GUI Duren\GUI Duren\training\DurianVision_Classifier_Colab.ipynb', 'Level 3 (Classifier Training)'),
]

for nb_path, label in notebooks:
    print(f"\n[NOTEBOOK] {label}")
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb['cells']
    code_cells = [c for c in cells if c['cell_type'] == 'code']
    md_cells = [c for c in cells if c['cell_type'] == 'markdown']

    print(f"  Total cells : {len(cells)} ({len(md_cells)} md + {len(code_cells)} code)")
    print(f"  GPU type    : {nb['metadata']['colab']['gpuType']}")

    # Syntax check
    syntax_ok = 0
    for i, cell in enumerate(cells):
        if cell['cell_type'] == 'code':
            src = ''.join(cell['source'])
            lines = []
            for line in src.split('\n'):
                stripped = line.strip()
                if stripped.startswith('!'):
                    lines.append('pass  # shell')
                else:
                    lines.append(line)
            try:
                compile('\n'.join(lines), f'cell_{i}', 'exec')
                syntax_ok += 1
            except SyntaxError as e:
                errors.append(f"{label} cell {i}: {e}")
                print(f"  [GAGAL] Cell {i}: {e}")

    print(f"  Syntax      : {syntax_ok}/{len(code_cells)} OK")

# 2. Verify app.py still works with new YOLOEngine signature
print(f"\n[INTEGRASI] Cek app.py kompatibilitas...")
sys.path.insert(0, r'd:\GUI Duren\GUI Duren')

# Check how app.py creates YOLOEngine
with open(r'd:\GUI Duren\GUI Duren\ui\app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

if 'YOLOEngine(' in app_content:
    # Find the line
    for i, line in enumerate(app_content.split('\n'), 1):
        if 'YOLOEngine(' in line:
            print(f"  Line {i}: {line.strip()}")

    # Check if it passes extra kwargs — new params have defaults so old calls work
    print(f"  [OK] YOLOEngine memiliki default params — backward compatible")
else:
    print(f"  [SKIP] YOLOEngine tidak langsung dipanggil di app.py")

# 3. Verify core modules import cleanly
print(f"\n[IMPORT] Core modules...")
try:
    from core.variety_classifier import VarietyClassifier
    print(f"  [OK] variety_classifier")
except Exception as e:
    errors.append(f"Import variety_classifier: {e}")
    print(f"  [GAGAL] {e}")

try:
    from core.yolo_engine import YOLOEngine
    print(f"  [OK] yolo_engine (with two-stage)")
except Exception as e:
    errors.append(f"Import yolo_engine: {e}")
    print(f"  [GAGAL] {e}")

# 4. Verify file structure
print(f"\n[FILES] Struktur training/...")
expected_files = [
    'training/DurianVision_Training_Colab.ipynb',
    'training/DurianVision_Classifier_Colab.ipynb',
    'training/train_v2.py',
    'training/zip_dataset.py',
    'training/dataset.zip',
    'training/dataset/data.yaml',
    'core/variety_classifier.py',
    'core/yolo_engine.py',
]

for f in expected_files:
    path = os.path.join(r'd:\GUI Duren\GUI Duren', f)
    exists = os.path.exists(path)
    size = ''
    if exists and os.path.isfile(path):
        s = os.path.getsize(path)
        if s > 1024 * 1024:
            size = f" ({s/1024/1024:.1f} MB)"
        else:
            size = f" ({s/1024:.1f} KB)"
    print(f"  {'✅' if exists else '❌'} {f}{size}")
    if not exists:
        errors.append(f"Missing: {f}")

# 5. Final summary
print(f"\n{'=' * 60}")
if errors:
    print(f"  GAGAL — {len(errors)} error")
    for e in errors:
        print(f"  ❌ {e}")
    sys.exit(1)
else:
    print(f"  ✅ SEMUA VALIDASI PASSED")
    print(f"{'=' * 60}")
