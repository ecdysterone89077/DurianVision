# REPRODUCE — paket produksi ulang DurianVision v2 (11 varietas)
Sumber kebenaran: naskah 01-MANUSKRIP.md (§3.5/3.6, Tabel 2–3). Cara pakai: salin isi
folder ini ke repo DurianVision (timpa training lama), lalu unggah best.pt 11-kelas.

## 1) Dataset (tidak disertakan — unduh dari sumber terbuka)
- Roboflow Universe (publik, CC BY 4.0, terverifikasi live 25 Sep 2026):
  https://universe.roboflow.com/penelitian-yolo-identifikasi-jenis-pisang/deteksi-jenis-durian-lmkb4/dataset/2
- Isi yang diharapkan: 430 citra (301 latih / 87 validasi / 42 uji), 11 kelas,
  anotasi poligon, praproses auto-orient + stretch-resize 640×640, tanpa augmentasi ekspor.
- Setelah unduh + ekstrak, pakai `data.yaml` bawaan ekspor (urutan kelas = kebenaran
  untuk pemetaan label). Contoh kerangka: `data.v2.yaml` di folder ini.

## 2) Lingkungan (sesuai Tabel 2 naskah)
- Windows 10/11, CPU (tanpa CUDA) untuk evaluasi; GPU untuk pelatihan (Colab T4 OK).
- `pip install -r requirements.lock` → ultralytics==8.4.131, torch==2.13.0+cpu.

## 3) Pelatihan (sesuai Tabel 3 naskah)
```
python train_durianvision_v2.py --data <path>/data.yaml --epochs 100 --batch 16 --imgsz 640
```
Konfigurasi terkunci di skrip: patience 20, optimizer auto, AMP aktif, seed 0 +
deterministik, augmentasi (mosaic, HSV h 0,015/s 0,7/v 0,4, flip 0,5, skala 0,5,
translasi 0,1, erasing 0,4, RandAugment). Naskah: berhenti epoch 71, terbaik epoch 51.

## 4) Angka yang harus direproduksi (± toleransi run-to-run kecil, seed sama → identik)
- Validasi: P 0,911 R 0,766 mAP50 0,937 mAP50-95 0,927
- Uji (42 citra): P 0,937 R 0,995 mAP50 0,995 mAP50-95 0,978
- Bootstrap n=1000: mAP50 0,94 [0,87–0,99]
- `python verify_reproduce.py --data <path>/data.yaml --weights <best.pt>` memeriksa
  hitungan split, 11 kelas, dan versi pustaka sebelum latih.

## 5) Yang WAJIB diunggah ke repo agar klaim naskah benar
- [x] `best.pt` 11-kelas (epoch 51) ke `packages/inference/models/` + root (sudah dipasang commit ini) — HANYA penulis
      yang punya (hasil latih mesin penulis); tanpa ini klaim "bobot aktif di repo" salah.
- [ ] `training/` diganti isi folder ini (skrip + lock + yaml + README ini).
- [x] Pemetaan label 11 kelas disamakan di: aplikasi desktop, backend
      (`packages/backend/src/utils/labels.ts`), layanan inferensi (`packages/inference/engine.py`)
      — cocokkan persis dengan `model.names` (lihat `labels-11.json`).
- [ ] Perintah latih + tautan dataset ditambahkan ke README repo.

## 6) Yang TIDAK bisa direproduksi pihak ketiga (keterbatasan tercatat di naskah)
- Split acak Roboflow (seed split tak dipublikasikan) — gunakan split bawaan ekspor.
- Seluruh sesi tersebar di ketiga split → angka uji optimistis (sudah dinyatakan).
- 4 kelas uji ber-support tunggal (D24, Lokal, Pelangi, Sane).
