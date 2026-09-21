# Panduan KBJI 2026

Cara menjalankan alat ekstraksi, memahami keluarannya, dan menyebarkan situsnya.
Bukti pemeriksaan ada di [CATATAN_PEMERIKSAAN.md](CATATAN_PEMERIKSAAN.md), definisi kolom di
[KAMUS_DATA.md](KAMUS_DATA.md), dan ketentuan data di [KETENTUAN_DATA.md](KETENTUAN_DATA.md).

---

## 1. Status hasil

Sumber: PDF 1.110 halaman, SHA-256 `19690c6c…b43cf`.

| Tingkat | Acuan Tabel 3 | Hasil | Selisih |
|---|---:|---:|---:|
| Golongan pokok | 10 | 10 | 0 |
| Subgolongan pokok | 43 | 43 | 0 |
| Golongan | 130 | 130 | 0 |
| Subgolongan | 449 | **447** | **−2** |
| Jabatan | 2.380 | 2.380 | 0 |

Status ekstraksi `LENGKAP_DAN_KONSISTEN` (0 temuan). Status dokumen sumber
`ADA_INKONSISTENSI_DOKUMEN_SUMBER` (3 temuan). Total 3.010 entri.

Selisih 447 vs 449 berasal dari publikasi, bukan dari transkripsi: Daftar Isi, bagian uraian,
pemindaian kolom kode, dan daftar kode anak di dalam uraian induk semuanya menghasilkan 447.
Bukti lengkapnya di [CATATAN_PEMERIKSAAN.md](CATATAN_PEMERIKSAAN.md) bagian 2.

## 2. Prinsip yang mengikat

1. **Transkripsi, bukan penyuntingan.** Kode, nama, dan uraian ditulis persis sebagaimana tercetak — termasuk ejaan yang tampak keliru.
2. **Tidak pernah mengarang kode.** Selisih jumlah dilaporkan, tidak ditutup.
3. **Angka acuan publikasi tidak diubah**, meski tidak cocok dengan isi publikasi itu sendiri.
4. **Setiap entri dapat ditelusuri** ke nomor halaman cetak dan halaman PDF.
5. **Kolom turunan terpisah dari kolom resmi**, dan dapat dihitung ulang.

## 3. Menjalankan

Butuh Python 3.10+ dan satu dependensi (`PyMuPDF==1.26.6`). Tidak perlu OCR, pandas, Java,
Node.js, atau GPU. PDF sumber tidak disertakan — unduh dari situs resmi BPS lalu letakkan di `input/`.
Nama berkas bebas; pemeriksaan memakai SHA-256.

**Windows (CMD):**

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe kbji.py extract --pdf "input\kbji_2026.pdf" --out output_baru
```

**macOS/Linux:**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python kbji.py extract --pdf input/kbji_2026.pdf --out output_baru
```

Gunakan nama folder baru; skrip menolak menimpa folder yang tidak kosong. Proses memakan dua
sampai empat menit dan menampilkan progres tiap 200 halaman. Pengujian diharapkan `Ran 26 tests` dan `OK`.

Untuk memeriksa ulang CSV tanpa membaca PDF:

```bat
.venv\Scripts\python.exe kbji.py validate --csv "output\kbji_2026_hierarki.csv" --out validasi_ulang
```

Perintah itu memeriksa struktur, hierarki, konsistensi kolom turunan, dan jumlah. Rekonsiliasi
Daftar Isi, rujukan induk–anak, dan pemindaian kolom kode hanya berjalan pada `extract`.

### Kode keluar

| Kode | Arti |
|---|---|
| `0` | Tidak ada temuan |
| `1` | Proses gagal |
| `2` | **Ada dugaan cacat ekstraksi.** Hasil tetap ditulis, tetapi harus ditinjau |
| `3` | **Ekstraksi lengkap; yang ditemukan ketidaksesuaian di dalam dokumen sumber.** Inilah hasil untuk PDF ini |

Kode `3` bukan kegagalan.

## 4. Isi folder keluaran

| Berkas | Isi |
|---|---|
| `kbji_2026_hierarki.csv` | 3.010 entri seluruh tingkat, 30 kolom. Berkas utama |
| `kbji_2026_jabatan.csv` | 2.380 jabatan enam digit, sudah membawa nama seluruh leluhurnya |
| `kbji_2026_ringkas.csv` | Daftar kode ringan tanpa uraian, untuk validasi kode di aplikasi |
| `kbji_2026_hierarki.json` | Data sama dalam JSON; kode tetap string |
| `kbji_2026_pohon.json` | Struktur bersarang untuk penelusuran taksonomi |
| `metadata.json` | Fingerprint sumber, versi alat, waktu proses, dan profil yang dipakai |
| `referensi/` | Transkripsi Daftar Isi, Tabel 1 tingkat keterampilan, dan angka acuan Tabel 3 serta 25–34 |
| `validasi/` | `LAPORAN_VALIDASI.md`, `ringkasan.json`, `semua_temuan.csv`, dan satu berkas per kategori |
| `audit/` | 34.913 baris teks sumber beserta koordinat, elemen yang dikeluarkan, dan tiga rekonsiliasi |

## 5. Cara kerja dan batasnya

Ekstraksi berbasis tata letak. Judul dikenali sebagai kode bercetak tebal pada kolom kiri,
sehingga angka di dalam uraian tidak terbaca sebagai entri. Watermark diagonal dikeluarkan
berdasarkan arah teks, margin berdasarkan koordinat. Uraian lintas halaman disambung sampai judul
kode berikutnya. Relasi induk dibentuk secara struktural: `0111.01 → 0111 → 011 → 01 → 0`.

Setelah itu dijalankan delapan pemeriksaan: struktur, hierarki, konsistensi kolom turunan,
konvensi penomoran, perbandingan jumlah, rekonsiliasi Daftar Isi, rujukan induk–anak, dan
pemindaian kolom kode.

Nama dipertahankan kapital sesuai judul PDF; pemisah baris judul menjadi spasi. Uraian
mempertahankan pergantian baris PDF. Kata yang terpotong tanda hubung tetap seperti sumber.
Untuk pencarian, gunakan kolom turunan `nama_pencarian` dan jangan mengubah kolom resmi.

Profil ini khusus untuk tata letak PDF yang diuji, bukan konverter untuk sembarang PDF KBJI.
Hasil pindai tidak didukung; tidak ada OCR. Opsi `--allow-different-pdf` menandai hasil sebagai
perlu tinjauan dan bukan jaminan PDF lain dapat diproses dengan aturan yang sama.

## 6. Membuka CSV dengan benar

UTF-8 dengan BOM, delimiter koma, seluruh sel dikutip. Uraian memuat koma, tanda kutip, dan
pergantian baris — gunakan pembaca CSV, jangan `split(',')`.

**Excel:** Data → From Text/CSV → Transform Data, lalu tetapkan semua kolom kode dan `versi_kbji`
sebagai tipe **Text** sebelum pemuatan. Hapus langkah Changed Type otomatis bila sudah mengubah
kode menjadi angka. Tanda kutip tidak menjamin Excel mempertahankan nol depan saat berkas dibuka
dengan klik ganda.

```python
import csv
with open('output/kbji_2026_hierarki.csv', encoding='utf-8-sig', newline='') as f:
    kbji = list(csv.DictReader(f))
```

```python
import pandas as pd
kbji = pd.read_csv('output/kbji_2026_hierarki.csv', dtype=str,
                   keep_default_na=False, encoding='utf-8-sig')
```

## 7. Memakai hasil untuk pengklasifikasian data

- **Daftar kandidat:** `kbji_2026_jabatan.csv`, 2.380 jabatan, masing-masing sudah membawa kode dan nama seluruh leluhurnya.
- **Validasi kode:** `kbji_2026_ringkas.csv` sebagai tabel referensi aplikasi. Setiap kode hasil pemetaan wajib diuji keberadaannya sebelum disimpan.
- **Agregasi:** pakai `kode_golongan_pokok` sampai `kode_subgolongan`, jangan memotong string kode secara manual.
- **Pencocokan teks:** mulai dari `nama_pencarian`, lalu nilai kecocokannya dengan `uraian_resmi`. Kesamaan judul saja sering tidak cukup.
- **Kelompok sisa:** kode bertanda `kelompok_sisa = ya` dipakai hanya bila tidak ada kode spesifik yang cocok.
- **Data tambahan** — sinonim, skor, koreksi pengguna — disimpan di tabel terpisah yang merujuk `kode`. Jangan menambah kolom ke berkas resmi.

Paket ini tidak menyediakan model klasifikasi lowongan dan tidak mengklaim akurasi pemetaan.

## 8. Situs dan API

Antarmuka penelusuran dan API JSON ada di folder `web/`, disajikan sebagai berkas statis di
Cloudflare Workers. Dokumentasi teknisnya di [web/README.md](web/README.md).

Bila data diperbarui, bangun ulang berkas statisnya lalu sebarkan:

```bash
python web/bangun_data.py --out output --data web/public/data
cd web
npx wrangler deploy
```

### Menyebarkan dari GitHub

Cloudflare Dashboard → **Workers & Pages** → **Create** → **Import a repository**, pilih repositori,
lalu isi konfigurasi build:

| Kolom | Nilai |
|---|---|
| Root directory | **`web`** |
| Build command | *(kosongkan)* |
| Deploy command | `npx wrangler deploy` |

Root directory wajib `web` karena di situlah `wrangler.jsonc` berada. Build command dikosongkan
karena `web/public/data/` sudah dikomit sehingga Python tidak diperlukan saat build. Setelah
tersambung, setiap push ke `main` menyebar otomatis.

Paket gratis Cloudflare mencukupi: 100.000 permintaan Worker per hari, dan permintaan berkas
statis tidak dihitung. Penelusuran serta pencarian berjalan di peramban, sehingga kuota Worker
hanya terpakai oleh `/api/*`, `/sitemap.xml`, dan pembukaan tautan dalam.

## 9. Pemecahan masalah

| Kondisi | Langkah |
|---|---|
| `py` tidak dikenali | Pasang Python, atau gunakan `python -m venv .venv` |
| PyMuPDF belum tersedia | Jalankan pip dengan interpreter `.venv` yang sama |
| Fingerprint PDF berbeda | Pastikan PDF asli yang sama. Mengganti nama aman; mengubah isi tidak |
| Folder keluaran tidak kosong | Gunakan nama folder keluaran baru |
| Exit code `3` | Normal untuk PDF ini |
| Exit code `2` | Buka `validasi/LAPORAN_VALIDASI.md` bagian "Temuan proses ekstraksi" |
| Nol di depan hilang di Excel | Impor ulang CSV asli, tetapkan tipe Text sebelum memuat |
| PDF hasil pindai | Profil ini membutuhkan lapisan teks; OCR tidak didukung |
| Build Cloudflare: `Could not detect a directory containing static files` | Root directory belum diisi `web` |
| `curl -s ...` gagal di PowerShell | Tulis `curl.exe`, atau pakai `Invoke-RestMethod`. Jangan tempel alamat yang masih memuat `<...>` |

## 10. Pekerjaan lanjutan

- Pembacaan manual seluruh 3.010 redaksi uraian. Nama 2.380 jabatan enam digit belum punya pembanding independen di dalam publikasi.
- Tabel konversi KBJI 2014 → 2026 (Tabel 9–18, halaman PDF 49–85) belum diekstraksi; tabel sumbernya tidak konsisten secara tipografi. Lihat [CATATAN_PEMERIKSAAN.md](CATATAN_PEMERIKSAAN.md) bagian 5.
- Pemetaan per entri ke ISCO-08. Publikasi hanya menyajikan perbedaan strukturnya pada Tabel 24.
