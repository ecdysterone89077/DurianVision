# Laporan Verifikasi — DurianVision (Audit & Perbaikan)

Tanggal: 2026-09-17
Lingkungan: Windows, Python 3.12 (`%LOCALAPPDATA%\Programs\Python\Python312`), Node v24.19.0,
torch 2.13.0+cpu (tanpa CUDA), Chrome 153 (headless untuk cek UI web).

## 1. Ringkasan

| Area | Sebelum | Sesudah |
|---|---|---|
| Suite desktop | 125/125, 58/58, 10/10 fase (31/08) | **125/125, 58/58, 10/10 fase** (re-run 17/09) |
| Suite web | 32/32, 36/36, 42/42, 37/37 (31/08) | **32/32, 36/36, 42/42, 37/37** (re-run final) |
| Script node backend | path usang, socket tanpa auth | **test-all, test-end-to-end, test_e2e_web lolos** |
| Regresi fix baru | - | **verify_fixes.py 15/15** |
| Installer | v1.0 208 MB (01/09) | **v1.0 rebuild 224.7 MB + smoke test exe OK** |
| Database | 61+ user test, 130+ sesi, model yatim | **0 user, 1 model aktif valid, 11 varietas** |
| Versioning | bukan git | **git repo + 4 commit checkpoint** |

## 2. Bukti hasil uji (state final)

| Suite | Hasil | File bukti (`%TEMP%\opencode\durian-verify-20260917\`) |
|---|---|---|
| test_operational.py | 125/125 (100%) | `60_operational_final.txt` |
| verify_level1.py | PASSED | `61_level1_final.txt` |
| verify_level3.py | PASSED | `62_level3_final.txt` |
| verify_final.py | PASSED | `63_final_final.txt` |
| test_protocol_b.py | 58/58 (100%) | `64_protocol_b_final.txt` |
| test_full_setup.py | 10/10 fase | `65_full_setup_final.txt` |
| test_all.py | 32/32 (100%) | `66_all_final.txt` |
| test_e2e.py | 36/36 (100%) | `67_e2e_final.txt` |
| test_advanced.py | 42/42 (100%) | `68_advanced_final.txt` |
| test_ultra.py | 37/37 (100%) | `69_ultra_final.txt` |
| test-all.mjs | ALL PASSED | `70_node_all_final.txt` |
| test_e2e_web.js | logs 3 baris terverifikasi masuk DB | `72_node_socket_final.txt` |
| verify_fixes.py | 15/15 (100%) | `50_verify_fixes.txt` |
| auto_build.py | 5/5 langkah lolos | `40_auto_build.txt` |

Verifikasi browser (Chrome headless): login → dashboard menampilkan metrik nyata (CPU/RAM,
device, distribusi), socket terhubung dengan cookie auth, halaman ROI fungsional
(tombol Confirm disabled sampai area dipilih), console tanpa error selain kamera headless.

## 3. Perbaikan yang diterapkan

**Desktop (`core/`, `ui/`)**

| Fix | File |
|---|---|
| Save-dir pengaturan diselesaikan ke absolut + auto-`makedirs` (sebelumnya relatif → snapshot/log nyasar) | `ui/app.py` |
| Autostart menunggu ROI dikonfirmasi; batal ROI mengembalikan panel; mulai tanpa ROI memakai layar penuh | `ui/app.py`, `ui/roi_selector.py` |
| DirectML tidak lagi mematikan engine (fallback CPU + opsi dinonaktifkan) | `core/yolo_engine.py`, `ui/tabs/performance_tab.py` |
| Race ganti model/device vs inferensi diserialisasi (RLock) | `core/yolo_engine.py` |
| Hotkey tombol polos (Space) tidak mencuri ketikan (cek caret window aktif) | `core/global_hotkeys.py` |
| Volume suara benar-benar berfungsi (PCM WAV sesuai volume) + sinkron tray | `ui/app.py` |
| "Paksa Smartphone/Desktop" diterapkan pada semua alur ROI | `ui/app.py`, `core/device_detector.py` |
| Combo model YOLO berfungsi (path absolut + signal) | `ui/tabs/performance_tab.py` |
| Galeri memuat snapshot lama saat start (24 terbaru) | `ui/widgets/snapshot_gallery.py`, `ui/app.py` |
| Worker snapshot aman-thread + ditunggu saat quit | `core/snapshot_manager.py`, `ui/app.py` |
| Status bar menampilkan ukuran area | `ui/app.py`, `ui/control_panel.py` |

**Web (`packages/`, `apps/`)**

| Fix | File |
|---|---|
| Mapping label model → tampilan UI (6 kelas → nama Indonesia konsisten desktop) | `packages/backend/src/utils/labels.ts` (+ dipakai di socket & predict) |
| Pagination log benar (`page`, `offset`, `meta.total/totalPages`) | `log.routes.ts`, `log.service.ts` |
| Socket `/detection` wajib login (session Better Auth) | `socket/index.ts` |
| Frame dengan `sessionId` tidak valid tidak lagi gagal FK diam-diam (cache validasi sesi) | `socket/index.ts` |
| Status socket konsisten (`completed`), `iouThreshold` diteruskan ke inference | `socket/index.ts`, `DetectionStream.tsx` |
| Auto-snapshot web → `POST /api/snapshots` (multipart) | `DetectionStream.tsx`, `services/api.ts` |
| Halaman ROI fungsional (drag area, deteksi device, simpan `roi_*` ke sesi) | `ROISelector.tsx` |
| Footer dashboard memakai metrik nyata (hapus hardcode RTX 4090) | `Dashboard.tsx` |
| Seed varietas selaras UI (tambah Black Thorn, 11 varietas) | `db/seed.ts` |
| Type error `Blob(Buffer)` diperbaiki (tsc bersih) | `inference.service.ts` |

**Tooling & data**

- Path usang diperbaiki: `packages/backend/test-all.mjs`, `test-end-to-end.mjs`,
  `packages/inference/test_yolo.py` (sekarang relatif terhadap repo).
- Encoding output suite di-UTF8-kan (sebelumnya crash `charmap cp1252` saat di-redirect):
  10 skrip di root.
- `test_e2e_web.js` kini login + memakai sesi nyata + memverifikasi log masuk DB.
- `verify_fixes.py` baru: regresi khusus perbaikan audit.
- DB: user/sesi/log test dibersihkan (backup: `sqlite.db.pre-cleanup`), model aktif
  di-upload ulang via API dan hot-reload terverifikasi
  (`/performance/inference` → `is_loaded: true`, device `cpu`).
- Git: repo diinisialisasi + commit checkpoint; backup sumber 77 MB di
  `%TEMP%\opencode\durian-bak-20260917`.

## 4. Build installer (rebuild penuh)

- Static scan: Bandit (HIGH) + Flake8 (E9/F63/F7/F82) lolos.
- PyInstaller onedir: `dist/DurianVision/DurianVision.exe` 56.8 MB (17/09 16:56) — bundle
  memuat `ui/app.py` versi baru (diverifikasi `_resolve_dir`) dan guard hotkey.
- Artefak scan: tidak ada dependensi kritis hilang.
- Inno Setup: `Output/DurianVision_Setup_v1.exe` 224.7 MB (17/09 17:10).
- Smoke test exe: `--help` OK; GUI berjalan 12 detik tanpa crash log baru.

## 5. Risiko / catatan tersisa

1. `classifier.pt` belum dilatih → two-stage nonaktif (fallback otomatis, bukan bug).
   Butuh GPU/Colab: `training/DurianVision_Classifier_Colab.ipynb`.
2. Semua inferensi CPU di mesin ini; angka FPS/latensi berbeda di mesin ber-GPU.
3. Dataset & file besar tidak masuk git (by design); training artifacts tetap di
   `durian-yolov11-results/` dan `training/dataset.zip`.
4. Uji kamera webcam UI web tidak bisa dilakukan di Chrome headless (kamera ditolak);
   komponen socket/ROI/log tetap tervalidasi lewat API + node.
5. Hotkey `Space` tetap default sesuai manual; perilaku mencuri ketikan sudah dijaga
   lewat heuristik caret (bukan penggantian hotkey).
