# Pemeriksa pra-latih: hitungan split, 11 kelas, versi pustaka. Gagal = jangan latih dulu.
import argparse, sys
import yaml
ap = argparse.ArgumentParser()
ap.add_argument('--data', required=True)
ap.add_argument('--weights', default=None)
a = ap.parse_args()
d = yaml.safe_load(open(a.data))
from pathlib import Path
ok = True
def check(cond, msg):
    global ok
    print(('OK  ' if cond else 'GAGAL'), msg)
    ok = ok and cond
tr = list(Path(d['train']).glob('*.*')); va = list(Path(d['val']).glob('*.*')); te = list(Path(d['test']).glob('*.*'))
check(len(tr) == 301, f'latih {len(tr)}==301')
check(len(va) == 87, f'validasi {len(va)}==87')
check(len(te) == 42, f'uji {len(te)}==42')
check(d.get('nc') == 11 and len(d.get('names', [])) == 11, 'nc==11 dan 11 nama')
import ultralytics, torch
check(ultralytics.__version__ == '8.4.131', f'ultralytics==8.4.131 (ini {ultralytics.__version__})')
check(torch.__version__.startswith('2.13.0+cpu'), f'torch==2.13.0+cpu (ini {torch.__version__})')
if a.weights:
    from ultralytics import YOLO
    names = YOLO(a.weights).names
    vals = list(names.values()) if isinstance(names, dict) else list(names)
    check(len(vals) == 11, f'best.pt 11 kelas (ini {len(vals)})')
sys.exit(0 if ok else 1)
