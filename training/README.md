# 🍈 DurianVision — Panduan Training YOLOv11

## ⭐ Rekomendasi: Google Colab (Gratis GPU)

Karena PC lokal tidak punya CUDA GPU, gunakan **Google Colab** yang menyediakan GPU T4 gratis.

### Cara Pakai Google Colab:

**1.** Upload notebook ke Colab:
   - Buka [Google Colab](https://colab.research.google.com)
   - Klik `File` → `Upload notebook`
   - Pilih file: `training/DurianVision_YOLOv11_Training.ipynb`

**2.** Aktifkan GPU:
   - Klik `Runtime` → `Change runtime type`
   - Pilih **T4 GPU** → Save

**3.** Siapkan dataset Roboflow:
   - Buka project di [Roboflow](https://app.roboflow.com)
   - Export dataset → format **YOLOv11** → **Download zip**
   - Simpan file zip di PC Anda

**4.** Jalankan semua cell di notebook:
   - Cell akan meminta upload file zip dataset Anda
   - Training otomatis berjalan (~30-60 menit)
   - Di akhir, download file `best.pt`

**5.** Simpan `best.pt`:
   - Taruh di `d:\GUI Duren\training\output\best.pt`
   - Atau langsung di `d:\GUI Duren\packages\inference\models\best.pt`

---

## File yang Tersedia

| File | Fungsi |
|------|--------|
| `DurianVision_YOLOv11_Training.ipynb` | ⭐ **Notebook Google Colab** — upload ini ke Colab |
| `train.py` | Script training lokal (butuh NVIDIA GPU) |
| `requirements.txt` | Dependencies Python |

---

## Konfigurasi di Notebook Colab

Di cell **4.1 Pengaturan Training**, Anda bisa ubah:

| Parameter | Default | Penjelasan |
|-----------|---------|------------|
| `BASE_MODEL` | `yolo11n.pt` | Ukuran model. `n`=nano (cepat), `s`=small, `m`=medium |
| `EPOCHS` | `150` | Jumlah epoch. Lebih banyak = lebih akurat |
| `IMAGE_SIZE` | `640` | Ukuran gambar. `416` lebih cepat |
| `BATCH_SIZE` | `16` | Kurangi ke 8 jika GPU kehabisan memori |
| `PATIENCE` | `30` | Auto-stop jika tidak ada perbaikan |

---

## Hasil yang Didapat

Setelah training selesai, Anda akan download:

```
best.pt          ← Model terbaik (GUNAKAN INI)
last.pt          ← Model terakhir (backup)
results.zip      ← Grafik loss, mAP, confusion matrix, dll
```

### Metrik yang Ditampilkan:
- **mAP50** — Akurasi deteksi (target: > 0.75)
- **mAP50-95** — Akurasi rata-rata di berbagai IoU threshold
- **Precision** — Seberapa tepat prediksi
- **Recall** — Seberapa lengkap deteksi

---

## Troubleshooting

### Colab disconnected / session timeout
→ Colab gratis punya batas ~12 jam. Kurangi `EPOCHS` jika training terlalu lama.

### CUDA Out of Memory di Colab
→ Kurangi `BATCH_SIZE` ke 8 atau `IMAGE_SIZE` ke 416

### Dataset error / class mismatch
→ Pastikan format export Roboflow adalah **YOLOv11** atau **YOLOv8**
