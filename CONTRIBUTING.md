# Berkontribusi

Terima kasih. Satu hal yang perlu dipahami lebih dulu, karena menentukan bentuk hampir semua kontribusi di sini.

## Aturan yang mengikat

Repositori ini **mentranskripsi** publikasi resmi, bukan menyuntingnya. Data KBJI dirujuk dalam ketentuan perundang-undangan ketenagakerjaan, sehingga aturan berikut tidak dapat dilonggarkan:

1. **Kolom resmi tidak boleh diubah.** `kode`, `nama_resmi`, dan `uraian_resmi` harus persis seperti tercetak — termasuk ejaan yang tampak keliru, tanda hubung, dan pergantian baris.
2. **Tidak boleh menambah atau menghapus entri.** Bila jumlah hasil berbeda dari acuan publikasi, selisih itu dilaporkan, bukan ditutup.
3. **Angka acuan tidak boleh diubah.** Nilai pada `config/kbji_2026.json` ditranskripsi dari Tabel 3 dan Tabel 25–34 beserta rujukan halamannya.
4. **Setiap klaim harus dapat ditelusuri** ke halaman PDF.

Pull request yang "memperbaiki" ejaan sumber, menambah kode agar jumlahnya pas, atau mengubah 449 menjadi 447 pada profil akan ditolak. Bila menurut Anda ada kesalahan pada publikasi, buka isu dengan rujukan halaman — perbaikannya ada di tangan BPS, bukan di repositori ini.

## Yang paling dibutuhkan

| Prioritas | Pekerjaan |
|---|---|
| Tinggi | **Verifikasi manual redaksi.** 2.380 nama jabatan enam digit belum punya pembanding independen di dalam publikasi, karena Daftar Isi tidak memuat tingkat enam digit. Pemeriksaan per bab sangat berguna. |
| Tinggi | **Tabel konversi KBJI 2014 → 2026** (Tabel 9–18, halaman PDF 49–85). Sudah diuji keterbacaannya, tetapi tabel sumbernya tidak konsisten secara tipografi. Lihat [CATATAN_PEMERIKSAAN.md](CATATAN_PEMERIKSAAN.md) bagian 5. Perlu peninjauan per baris. |
| Sedang | Aksesibilitas dan terjemahan antarmuka. |
| Sedang | Klien untuk bahasa lain yang memakai API. |
| Rendah | Perapian kode, tanpa mengubah perilaku ekstraksi. |

## Menyiapkan lingkungan

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

Di Windows gunakan `.venv\Scripts\python.exe`.

PDF sumber tidak disertakan dan tidak boleh dikomit. Unduh dari situs resmi BPS, lalu letakkan di `input/`. Fingerprint yang diuji ada pada `config/kbji_2026.json`.

Untuk bagian web:

```bash
cd web
npm install
python bangun_data.py     # membangun ulang web/public/data dari ../output
npm run dev               # wrangler dev di http://127.0.0.1:8787
```

## Sebelum membuka pull request

1. `python -m unittest discover -s tests -v` — 26 tes harus lulus.
2. Bila mengubah pipeline ekstraksi, jalankan ulang penuh dan bandingkan:
   ```bash
   python kbji.py extract --pdf "input/<berkas>.pdf" --out output_baru
   python - <<'PY'
   import csv
   lama = {r['kode']: r for r in csv.DictReader(open('output/kbji_2026_hierarki.csv', encoding='utf-8-sig'))}
   baru = {r['kode']: r for r in csv.DictReader(open('output_baru/kbji_2026_hierarki.csv', encoding='utf-8-sig'))}
   assert set(lama) == set(baru), 'Himpunan kode berubah.'
   for k in lama:
       for f in ('nama_resmi', 'uraian_resmi', 'halaman_pdf_mulai', 'halaman_cetak_mulai'):
           assert lama[k][f] == baru[k][f], f'{k}.{f} berubah'
   print('Kolom resmi tidak berubah.')
   PY
   ```
   **Kolom resmi tidak boleh berubah** kecuali PR-nya memang memperbaiki cacat transkripsi yang terbukti — sertakan rujukan halaman PDF dan cuplikan bukti.
3. `python kbji.py validate --csv output/kbji_2026_hierarki.csv --out .validasi` harus menghasilkan exit code `3` dengan 0 temuan berkelas `ekstraksi`.
4. Perbarui `CHANGELOG.md`.

## Gaya

- Dokumentasi, nama fungsi, dan pesan berbahasa Indonesia, mengikuti berkas yang ada.
- Python: baku, tanpa dependensi baru. Satu-satunya dependensi adalah PyMuPDF, dipatok versinya.
- Web: tanpa kerangka kerja dan tanpa langkah bangun. JavaScript biasa, CSS biasa.
- Komentar menjelaskan **mengapa**, bukan mengulang kode.

## Isu

Sertakan halaman PDF, kode KBJI yang terkait, isi yang diharapkan, isi yang diperoleh, serta versi `kbji.py` dan SHA-256 berkas PDF Anda.
