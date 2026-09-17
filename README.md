# DurianVision — GUI Deteksi Durian (YOLOv11)

Monorepo sistem deteksi durian: **aplikasi desktop PyQt6** (deliverable utama), **dashboard web**
(React + Express + FastAPI), dan **pipeline training YOLO** (notebook Colab + skrip).

Model aktif: `best.pt` — YOLOv11, 6 kelas (`bawor`, `black thorn`, `kanyao`, `monthong`,
`musang king`, `not durian`), mAP50 0.98. Installer: `Output/DurianVision_Setup_v1.exe`.

---

## Arsitektur

| Komponen | Teknologi | Port | Entri |
|---|---|---|---|
| Desktop app | PyQt6 + ultralytics (DXcam/MSS screen capture) | - | `main.py` |
| Inference service | FastAPI + YOLO | 8001 | `packages/inference/main.py` |
| Backend API | Express + Better Auth + Drizzle/SQLite + Socket.IO | 3005 | `packages/backend/src/index.ts` |
| Web dashboard | React 19 + Vite + TanStack Query | 5173 | `apps/durian-vision-web` |

Alur web: webcam → socket `/detection` (butuh login) → backend → FastAPI `:8001` → hasil + log
tersimpan ke SQLite (batch flush 2 detik / 50 baris). Aplikasi desktop berdiri sendiri
(tidak butuh web stack).

---

## Prasyarat (Windows 10/11)

- **Python 3.12** — di mesin ini: `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`
  (tidak ada di PATH; gunakan path lengkap atau tambahkan ke PATH).
- **Node 24+** — `npm.ps1` diblokir execution policy; gunakan `npm.cmd`.
- **Inno Setup 6** (hanya untuk build installer) — `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`.
- GPU opsional; tanpa CUDA otomatis fallback ke CPU.

---

## Menjalankan

### Aplikasi desktop

```powershell
python main.py               # panel kontrol + tray
python main.py --autostart   # langsung pilih layar penuh lalu mulai deteksi
python main.py --minimize    # mulai tersembunyi di tray
```

Klik tray dua kali untuk membuka panel. Alur: **Pilih Area → Konfirmasi → Mulai Deteksi**.
Snapshot tersimpan di `Documents\DurianVision_Snapshots`, log di `%APPDATA%\DurianVision`.

### Web stack (urut)

```powershell
# 1) Inference (dari packages/inference agar models/best.pt ditemukan)
.\venv\Scripts\python.exe main.py

# 2) Backend (dari packages/backend)
npm.cmd run dev        # http://localhost:3005

# 3) Web (dari apps/durian-vision-web)
npm.cmd run dev        # http://localhost:5173, login via /login
```

Setup DB dari nol: `npm.cmd run db:push; npm.cmd run db:seed` (dari `packages/backend`).

---

## Testing

Desktop (tidak butuh server, butuh sesi GUI Windows):

```powershell
python test_operational.py     # 125 tes komponen inti
python test_protocol_b.py      # 58 tes blind-spot widget/IO
python test_full_setup.py      # boot aplikasi nyata 10 fase
python verify_level1.py; python verify_level3.py; python verify_final.py
python verify_fixes.py         # regresi perbaikan audit (save-dir, hotkey, device, API)
```

Web (butuh ketiga service hidup):

```powershell
python test_all.py; python test_e2e.py; python test_advanced.py; python test_ultra.py
node packages/backend/test-all.mjs
node packages/backend/test-end-to-end.mjs
node packages/backend/test_e2e_web.js     # socket + verifikasi log masuk DB
```

Hasil verifikasi terakhir: lihat `LAPORAN-VERIFIKASI.md` (semua 100% hijau).

---

## Build installer

```powershell
python auto_build.py
```

Pipeline 5 langkah: Bandit+Flake8 → bersihkan `build/dist/Output` → PyInstaller (onedir) →
scan `warn-DurianVision.txt` → kompilasi Inno Setup. Artefak:
`dist/DurianVision/DurianVision.exe` dan `Output/DurianVision_Setup_v1.exe`.

---

## Struktur folder

```
main.py                  # entri desktop
ui/                      # PyQt6: panel, overlay, tray, tab, widget
core/                    # engine: yolo, capture, worker, config, snapshot, log, hotkey
config/default_config.json
training/                # notebook Colab + train.py/train_v2.py + dataset (tidak di-git)
durian-yolov11-results/  # artefak training (results.csv, kurva, weights)
packages/inference/      # FastAPI sidecar + models/best.pt
packages/backend/        # Express + auth + socket + SQLite
apps/durian-vision-web/  # dashboard React
test_*.py verify_*.py    # suite verifikasi
```

---

## Catatan & gap yang diketahui

- `classifier.pt` (two-stage) belum ada — aplikasi otomatis **YOLO-only**. Latih via
  `training/DurianVision_Classifier_Colab.ipynb`, taruh di root, lalu aktifkan
  `two_stage.enabled`. Build berikutnya akan membundelnya.
- Model punya 6 kelas; UI memetakan ke 11 varietas (`ui/styles/theme.py` → `MODEL_CLASS_MAP`).
  Backend memakai mapping yang sama (`packages/backend/src/utils/labels.ts`).
- Dataset & file besar tidak masuk git (`*.zip`, `training/dataset/`, `*.pt` kecuali model
  utama yang di-force-add, `dist/`, `build/`, `Output/`). Backup sumber ada di
  `%TEMP%\opencode\durian-bak-20260917`.
- Hotkey `Space` (snapshot) dijaga agar tidak mencuri ketikan di aplikasi lain
  (`core/global_hotkeys.py` memeriksa caret window aktif).
- Socket `/detection` mewajibkan session login; frame tanpa sesi valid tidak ditulis ke DB.
- Mesin ini tanpa CUDA (`torch 2.13.0+cpu`) — semua inferensi berjalan di CPU.
