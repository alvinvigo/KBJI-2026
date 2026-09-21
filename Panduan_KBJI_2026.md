# Panduan KBJI 2026: ekstraksi PDF menjadi CSV hierarkis

Paket Python lokal untuk mengekstraksi publikasi **Klasifikasi Baku Jabatan Indonesia (KBJI) 2026**, Volume 1, terbitan Badan Pusat Statistik dan Kementerian Ketenagakerjaan Republik Indonesia (katalog 1302037, nomor publikasi 03100.26011).

Tidak membutuhkan API berbayar, akun AI, Cloudflare Workers, basis data, atau GPU. Internet hanya diperlukan saat mengunduh Python dan memasang satu dependensi. Setelah terpasang, seluruh pemrosesan berjalan lokal; PDF dan isinya tidak dikirim ke layanan mana pun.

Paket ini sudah dijalankan pada PDF sumber. Hasilnya tersedia di folder `output/`. Ini adalah pekerjaan transkripsi teknis atas publikasi resmi, bukan penerbitan resmi BPS/Kementerian Ketenagakerjaan.

---

## 1. Prinsip yang mengikat

Data KBJI adalah data ketenagakerjaan yang dirujuk dalam ketentuan perundang-undangan. Karena itu paket ini bekerja di bawah aturan berikut, dan aturan ini tidak boleh dilonggarkan:

1. **Transkripsi, bukan penyuntingan.** Kode, nama, dan uraian ditulis persis sebagaimana tercetak. Tidak ada koreksi ejaan, penyeragaman istilah, penerjemahan, penambahan sinonim, atau penggabungan.
2. **Tidak pernah mengarang kode.** Bila jumlah hasil ekstraksi berbeda dari angka acuan pada publikasi, selisih itu dilaporkan apa adanya. Tidak ada entri yang dibuat, disalin, atau dihapus untuk membuat angka cocok.
3. **Tidak ada angka acuan yang diam-diam diubah.** Acuan publikasi tetap ditulis sebagaimana tercetak pada Tabel 3 dan Tabel 25–34, termasuk ketika angka itu tidak cocok dengan isi publikasi itu sendiri.
4. **Setiap klaim harus dapat ditelusuri.** Setiap entri membawa nomor halaman PDF dan halaman cetak. Setiap baris teks sumber tercatat pada berkas audit beserta koordinat dan perannya.
5. **Kolom turunan dipisahkan dari kolom resmi.** Kolom bantu seperti jalur hierarki dan teks pencarian dihitung dari kolom resmi dan dapat dihitung ulang; kolom resmi tidak pernah diubah untuk kenyamanan pemakaian.

---

## 2. Status hasil

Dijalankan pada PDF dengan SHA-256 `19690c6c53f386ecd3f1f057a6159c06ad7bf87ec597f3e07cc7b83d426b43cf` (1.110 halaman, 30.368.071 bita).

| Status | Nilai |
|---|---|
| Status ekstraksi | **LENGKAP_DAN_KONSISTEN** — 0 temuan |
| Status dokumen sumber | **ADA_INKONSISTENSI_DOKUMEN_SUMBER** — 3 temuan |
| Catatan informasi | 47 |
| Total entri | 3.010 |
| Kode keluar (exit code) | 3 |

| Tingkat | Acuan publikasi (Tabel 3) | Hasil ekstraksi | Selisih |
|---|---:|---:|---:|
| Golongan pokok (1 digit) | 10 | 10 | 0 |
| Subgolongan pokok (2 digit) | 43 | 43 | 0 |
| Golongan (3 digit) | 130 | 130 | 0 |
| Subgolongan (4 digit) | 449 | **447** | **−2** |
| Jabatan (6 digit) | 2.380 | 2.380 | 0 |

### Selisih 447 vs 449 adalah ketidaksesuaian di dalam publikasi, bukan kegagalan ekstraksi

Empat pemeriksaan yang saling bebas menghasilkan angka yang sama, 447:

1. **Daftar Isi** (halaman PDF 11–26) memuat 447 kode subgolongan.
2. **Bagian uraian** (halaman PDF 103–1108) memuat 447 judul subgolongan.
3. **Pemindaian seluruh fragmen teks pada kolom kode** di seluruh bagian uraian, tanpa memakai aturan huruf tebal, menemukan 447 kode empat digit. Selain itu tidak ada satu pun kode empat digit lain yang tercetak di kolom kode; 429 angka empat digit lain yang ditemukan seluruhnya adalah nomor halaman pada margin bawah.
4. **Daftar subgolongan di dalam uraian golongan**: 173 entri induk mencantumkan daftar kode anaknya, total 584 rujukan. Seluruhnya memiliki judul sendiri; tidak ada satu pun kode anak yang disebut tetapi tidak diuraikan.

Selain itu, Daftar Isi dan bagian uraian cocok seluruhnya untuk 630 kode tingkat 1–4 digit: **kode, nama, dan nomor halaman cetak identik pada ketiganya**.

Angka 449 hanya muncul pada narasi halaman PDF 44, Tabel 3 (halaman PDF 45), dan Tabel 19 (halaman PDF 86). Rinciannya:

| Golongan pokok | Rujukan | Acuan | Hasil | Keterangan |
|---|---|---:|---:|---|
| 2 Profesional | Tabel 27, halaman cetak 62 / PDF 94 | 94 | 93 | Daftar Isi dan uraian sama-sama 93 |
| 6 Pekerja Terampil Pertanian, Kehutanan, dan Perikanan | Tabel 31, halaman cetak 64 / PDF 96 | 19 | 18 | Daftar Isi dan uraian sama-sama 18 |

Jumlah subgolongan pada Tabel 25–34 berjumlah 449 apabila dijumlahkan, jadi tabel ringkasan konsisten satu sama lain tetapi tidak konsisten dengan isi publikasi.

**Tindak lanjut yang disarankan:** konfirmasikan kepada tim penyusun BPS dan Kementerian Ketenagakerjaan apakah Tabel 3, Tabel 19, Tabel 27, dan Tabel 31 perlu diralat menjadi 447, atau memang ada dua subgolongan yang seharusnya tercetak tetapi luput dari Daftar Isi maupun bagian uraian. Sampai ada keputusan penyusun, dataset ini memuat 447 subgolongan karena itulah yang tercetak.

### Catatan sumber lain yang ditemukan

- **Kode 5412 tidak dipakai.** Golongan 541 Tenaga Usaha Jasa Perlindungan memuat 5411, 5413, 5414, dan 5419. Kode 5412 tidak muncul di mana pun dalam publikasi. Ini satu-satunya celah penomoran interior pada seluruh 130 golongan; 128 golongan lain bernomor urut tanpa celah, dan 26 golongan bersubgolongan tunggal seluruhnya memakai konvensi akhiran 0.
- **Tabel 1 Hubungan antara Tingkat Keterampilan dengan KBJI 2026** (halaman PDF 38) mengosongkan sel tingkat keterampilan untuk golongan pokok 5, 6, 7, dan 8. Sel itu tidak diisi pada hasil ekstraksi; lihat `output/referensi/tingkat_keterampilan.csv`.
- **Tabel 19** (halaman PDF 86) menyebut KBJI 2014 memiliki 446 subgolongan. Angka ini tidak diverifikasi oleh paket ini karena publikasi KBJI 2014 bukan sumber di sini.
- 23 halaman pada rentang uraian tidak memuat teks isi: 9 pembatas bab (masing-masing satu gambar halaman penuh) dan 14 halaman kosong. Seluruhnya diverifikasi otomatis dari isi PDF, bukan dari daftar manual.

---

## 3. Yang dibutuhkan

1. Windows, macOS, atau Linux.
2. Python 3.10 atau lebih baru. Hasil pada `output/` dibuat dengan versi yang tercatat di `output/metadata.json`.
3. Satu dependensi: `PyMuPDF==1.26.6`, tercantum pada `requirements.txt`.
4. PDF sumber yang sama, sekitar 30 MB.
5. Ruang disk sekitar 500 MB sebagai kelonggaran untuk lingkungan Python, PDF, dan hasil.

Tidak diperlukan pandas, OCR, Java, Node.js, Microsoft Office, maupun Poppler. GPU tidak diperlukan.

Unduh Python melalui <https://www.python.org/downloads/> apabila belum terpasang. Di Windows, aktifkan opsi penambahan Python ke PATH saat pemasangan. Perintah di bawah memakai Command Prompt (CMD) agar tidak perlu mengubah execution policy PowerShell.

---

## 4. Langkah menjalankan di Windows

### Langkah 1 — Siapkan folder

Ekstrak paket, misalnya ke `C:\KBJI\kbji_2026_python`. Buka folder tersebut, ketik `cmd` di bilah alamat File Explorer, lalu tekan Enter. Pastikan `kbji.py`, `requirements.txt`, dan folder `config` terlihat.

### Langkah 2 — Masukkan PDF

Salin PDF sumber ke folder `input`. Nama berkas bebas; pemeriksaan memakai SHA-256, bukan nama. Jangan mencetak ulang, mengompres, atau menyunting PDF jika ingin memakai profil yang telah diuji.

### Langkah 3 — Periksa Python

```bat
py -3 --version
```

Jika `py` tidak tersedia tetapi `python` tersedia, ganti `py -3` dengan `python` pada langkah berikutnya.

### Langkah 4 — Buat lingkungan Python

```bat
py -3 -m venv .venv
```

Lingkungan tidak perlu diaktifkan secara manual; perintah selanjutnya memanggil Python di dalam `.venv` secara langsung.

### Langkah 5 — Pasang dependensi

```bat
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Langkah ini membutuhkan internet pada pemasangan pertama. Tidak ada API key atau biaya langganan.

### Langkah 6 — Jalankan pemeriksaan skrip

```bat
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Hasil yang diharapkan: `Ran 26 tests` dan `OK`. Pengujian ini memeriksa perilaku parser, kolom turunan, dan seluruh validator, bukan memverifikasi isi PDF.

### Langkah 7 — Ekstrak PDF

```bat
.venv\Scripts\python.exe kbji.py extract --pdf "input\klasifikasi-baku-jabatan-indonesia--kbji--2026.pdf" --out "output_baru"
```

Gunakan nama folder baru, karena `output` pada paket sudah berisi hasil resmi dan skrip menolak menimpa folder yang tidak kosong. Untuk pengulangan berikutnya gunakan `output_baru_2`, dan seterusnya.

Progres ditampilkan setiap 200 halaman. Untuk PDF yang sama, hasil akhirnya:

```text
status_ekstraksi: LENGKAP_DAN_KONSISTEN
status_sumber: ADA_INKONSISTENSI_DOKUMEN_SUMBER
total_entri: 3010
temuan_ekstraksi: 0
temuan_sumber: 3
temuan_informasi: 47
```

Waktu proses sekitar dua sampai empat menit pada laptop biasa.

### Langkah 8 — Baca laporan

| Berkas | Isi |
|---|---|
| `output_baru\validasi\LAPORAN_VALIDASI.md` | Ringkasan status dan seluruh temuan, dipisah antara temuan ekstraksi dan temuan sumber |
| `output_baru\validasi\semua_temuan.csv` | Temuan dalam bentuk tabel |
| `output_baru\kbji_2026_hierarki.csv` | Seluruh 3.010 entri, semua tingkat |
| `output_baru\kbji_2026_jabatan.csv` | 2.380 jabatan enam digit |

### Langkah 9 — Validasi ulang CSV bila diperlukan

```bat
.venv\Scripts\python.exe kbji.py validate --csv "output_baru\kbji_2026_hierarki.csv" --out "validasi_ulang"
```

Perintah ini memeriksa struktur, hierarki, konsistensi kolom turunan, dan jumlah pada CSV. Perintah ini **tidak** membaca ulang PDF, sehingga rekonsiliasi Daftar Isi, rujukan induk–anak, dan pemindaian kolom kode tidak dijalankan. Gunakan CSV hierarki lengkap; CSV jabatan saja tidak memuat entri induk tingkat 1–4 digit.

### Kode keluar (exit code)

| Kode | Arti |
|---|---|
| `0` | Tidak ada temuan sama sekali |
| `1` | Proses gagal; tidak ada berkas hasil yang dapat dipercaya |
| `2` | **Ada dugaan cacat pada ekstraksi.** Hasil tetap ditulis, tetapi harus ditinjau sebelum dipakai |
| `3` | **Ekstraksi terverifikasi lengkap; yang ditemukan adalah ketidaksesuaian di dalam dokumen sumber.** Inilah kode yang dihasilkan PDF KBJI 2026 ini |

Kode `3` bukan kegagalan. Jangan menyamakan kode `2` atau `3` dengan kegagalan menghasilkan CSV.

---

## 5. Menjalankan pada macOS/Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python kbji.py extract --pdf "input/klasifikasi-baku-jabatan-indonesia--kbji--2026.pdf" --out output_baru
```

---

## 6. Isi paket

| Berkas/folder | Fungsi |
|---|---|
| `kbji.py` | Skrip lengkap dengan perintah `extract` dan `validate` |
| `requirements.txt` | Dependensi yang dipatok pada versi yang diuji |
| `config/kbji_2026.json` | Profil sumber: fingerprint, rentang halaman, batas tata letak, acuan jumlah beserta rujukan tabelnya, transkripsi Tabel 1, selisih sumber yang sudah diverifikasi, dan daftar halaman tanpa isi |
| `tests/test_kbji.py` | 26 pengujian regresi |
| `input/` | Tempat PDF sumber; PDF tidak disertakan dalam distribusi kode |
| `web/` | Situs referensi dan API JSON untuk Cloudflare Workers. Lihat `web/README.md` |
| `.github/workflows/ci.yml` | Uji otomatis: regresi, validasi ulang CSV, dan pemeriksaan Worker |
| `dokumen/surat-pemberitahuan-bps.md` | Draf surat pemberitahuan dan permohonan izin kepada BPS |
| `Panduan_KBJI_2026.md` | Dokumen ini: rencana, cara pakai, status hasil, dan langkah publikasi |
| `README.md` | Halaman muka repositori |
| `KAMUS_DATA.md` | Definisi setiap kolom dan cara memakainya |
| `CATATAN_PEMERIKSAAN.md` | Rincian audit, bukti, dan batas pemeriksaan |
| `KETENTUAN_DATA.md` | Ketentuan penggunaan data KBJI dan cara mengutip |
| `LICENSE` | Lisensi MIT untuk kode program saja |
| `CITATION.cff` | Keterangan sitasi yang dapat dibaca mesin |
| `CONTRIBUTING.md` | Aturan kontribusi, termasuk larangan mengubah kolom resmi |
| `SECURITY.md` | Pelaporan kerentanan dan permintaan penghapusan data |
| `CHANGELOG.md` | Riwayat perubahan |
| `.gitignore` | Mengecualikan lingkungan Python, PDF, `node_modules`, dan folder hasil percobaan |

### Isi folder `output/`

| Berkas | Isi |
|---|---|
| `kbji_2026_hierarki.csv` | 3.010 entri seluruh tingkat, 30 kolom. Berkas utama |
| `kbji_2026_jabatan.csv` | 2.380 jabatan enam digit, kolom sama, sudah membawa seluruh nama leluhurnya |
| `kbji_2026_ringkas.csv` | Daftar kode ringan tanpa uraian, untuk validasi kode dan tabel referensi aplikasi |
| `kbji_2026_hierarki.json` | Data yang sama dalam JSON; seluruh kode tetap bertipe string |
| `kbji_2026_pohon.json` | Struktur bersarang untuk penelusuran taksonomi; tanpa uraian agar ringan |
| `metadata.json` | Fingerprint sumber, versi alat, waktu proses, dan seluruh profil yang dipakai |
| `referensi/daftar_isi.csv` | Transkripsi Daftar Isi: 630 kode, nama, dan halaman cetak |
| `referensi/tingkat_keterampilan.csv` | Transkripsi Tabel 1 apa adanya, termasuk sel yang kosong pada sumber |
| `referensi/jumlah_acuan_publikasi.csv` | Angka acuan Tabel 3 dan Tabel 25–34 beserta rujukan halamannya |
| `validasi/LAPORAN_VALIDASI.md` | Laporan utama |
| `validasi/ringkasan.json` | Status dan rekap dalam bentuk mesin |
| `validasi/semua_temuan.csv` dan satu berkas per kategori | Temuan; berkas tanpa temuan tetap dibuat berisi header saja |
| `validasi/jumlah_per_tingkat.csv`, `validasi/jumlah_per_golongan_pokok.csv` | Perbandingan jumlah hasil dengan acuan publikasi |
| `audit/baris_sumber.jsonl` | 34.913 baris teks isi beserta halaman, koordinat, ketebalan huruf, id entri, dan perannya |
| `audit/elemen_dikeluarkan.csv` | 1.991 elemen yang dikeluarkan: 1.006 watermark diagonal dan 985 baris margin |
| `audit/cakupan_halaman.csv` | Status setiap halaman pada rentang uraian |
| `audit/rekonsiliasi_daftar_isi.csv` | Perbandingan kode, nama, dan halaman antara Daftar Isi dan bagian uraian |
| `audit/rekonsiliasi_anak_induk.csv` | Perbandingan kode anak yang disebut pada uraian induk dengan judul yang benar-benar ada |
| `audit/pindaian_kolom_kode.csv` | Hasil pemindaian independen kolom kode terhadap hasil parsing |

---

## 7. Cara kerja dan batas ekstraksi

1. Memeriksa SHA-256 PDF. Nama berkas boleh berbeda; isinya harus sama dengan sumber yang diuji.
2. Memproses halaman PDF 103–1108. Halaman tercetak = nomor halaman PDF dikurangi 32 pada rentang ini.
3. Membaca teks beserta koordinat, arah, dan font.
4. Mengeluarkan watermark diagonal berdasarkan arah teks, serta margin atas/bawah berdasarkan koordinat.
5. Menggabungkan fragmen yang berada pada baris horizontal yang sama.
6. Mengenali judul sebagai kode bercetak tebal pada kolom kiri, bukan setiap angka yang muncul di dalam uraian.
7. Menggabungkan judul multibaris dan uraian lintas halaman sampai judul kode berikutnya.
8. Membentuk relasi induk secara struktural: `0111.01 → 0111 → 011 → 01 → 0`.
9. Menghitung kolom turunan: kode dan nama leluhur, jalur hierarki, jumlah anak, jumlah jabatan turunan, penanda kelompok sisa, dan teks pencarian.
10. Menjalankan pemeriksaan: struktur, hierarki, konsistensi kolom turunan, konvensi penomoran, perbandingan jumlah, rekonsiliasi Daftar Isi, rujukan induk–anak, pemindaian kolom kode, dan klasifikasi halaman tanpa isi.
11. Menulis semua entri apa adanya, termasuk bila ditemukan masalah, beserta laporan yang sesuai.

Nama dipertahankan kapital sebagaimana judul PDF. Pemisah baris pada judul menjadi spasi. Uraian mempertahankan pergantian baris PDF. Daftar contoh, catatan, pengecualian, dan tugas yang tercantum di bawah suatu kode tetap berada di uraian kode tersebut. Uraian induk tidak disalin ke anaknya.

Kata yang terpotong dengan tanda hubung tetap seperti sumber. Untuk kebutuhan pencarian, gunakan kolom turunan `nama_pencarian` dan jangan mengubah kolom resmi.

Profil ini khusus untuk susunan PDF yang diuji, bukan konverter untuk sembarang PDF KBJI. Hasil pindai (OCR) atau PDF yang sudah dicetak ulang dapat memiliki font dan posisi berbeda. Tidak ada OCR pada paket ini.

Opsi `--allow-different-pdf` tersedia untuk pengembang yang sudah menyesuaikan profil. Opsi ini menandai hasil sebagai perlu tinjauan dan menonaktifkan pemeriksaan halaman tanpa isi berbasis fingerprint. Opsi ini bukan jaminan bahwa tata letak PDF lain dapat diproses dengan aturan yang sama.

---

## 8. Membuka CSV dengan benar

CSV berformat UTF-8 dengan BOM, delimiter koma, dan seluruh sel dikutip. Uraian dapat memuat koma, tanda kutip, dan pergantian baris. Gunakan pembaca CSV; jangan memecah teks dengan `split(',')` atau menghitung baris fisik berkas.

**Excel:** Data → From Text/CSV → Transform Data. Tetapkan `kode`, `kode_normalisasi`, `kode_induk`, `kode_golongan_pokok`, `kode_subgolongan_pokok`, `kode_golongan`, `kode_subgolongan`, dan `versi_kbji` menjadi tipe **Text** sebelum pemuatan. Hapus langkah Changed Type otomatis bila langkah itu sudah mengubah kode menjadi angka. Jangan menyimpan ulang dari Excel sebelum memastikan nol depan masih utuh.

CSV tidak membawa definisi tipe data. Tanda kutip tidak menjamin Excel mempertahankan nol depan ketika berkas dibuka dengan klik ganda.

**Python, tanpa pandas:**

```python
import csv
with open('output/kbji_2026_hierarki.csv', encoding='utf-8-sig', newline='') as f:
    data = list(csv.DictReader(f))
print(next(r for r in data if r['kode'] == '0111.01'))
```

**Dengan pandas:**

```python
import pandas as pd
kbji = pd.read_csv('output/kbji_2026_hierarki.csv', dtype=str,
                   keep_default_na=False, encoding='utf-8-sig')
```

Pandas tidak diperlukan oleh paket. Kolom kode pada JSON juga bertipe string sehingga aman dipakai di JavaScript tanpa inferensi angka.

---

## 9. Memakai hasil sebagai dasar pengklasifikasian data

1. **Daftar kandidat.** Gunakan `kbji_2026_jabatan.csv` sebagai himpunan kandidat 2.380 jabatan. Setiap baris sudah membawa kode dan nama seluruh leluhurnya, sehingga tidak perlu join terpisah untuk menampilkan konteks.
2. **Validasi kode.** Gunakan `kbji_2026_ringkas.csv` sebagai tabel referensi aplikasi. Setiap kode hasil pemetaan wajib diuji keberadaannya pada tabel ini sebelum disimpan.
3. **Agregasi.** Gunakan `kode_golongan_pokok`, `kode_subgolongan_pokok`, `kode_golongan`, dan `kode_subgolongan` untuk meringkas data tanpa memotong string kode secara manual.
4. **Penelusuran antarmuka.** Gunakan `kbji_2026_pohon.json` untuk menu bertingkat atau penelusuran taksonomi.
5. **Pencocokan teks.** Gunakan `nama_pencarian` sebagai kunci pencocokan awal, lalu nilai kecocokannya dengan `uraian_resmi`. Kesamaan judul saja sering tidak cukup; uraian memuat tugas, contoh jabatan, dan pengecualian yang membedakan kode yang judulnya mirip.
6. **Kelompok sisa.** Kolom `kelompok_sisa` menandai kode sisa/lainnya menurut aturan penomoran. Dalam pemetaan otomatis, kode sisa sebaiknya dipakai hanya bila tidak ada kode spesifik yang cocok.
7. **Data tambahan disimpan terpisah.** Sinonim, istilah bahasa Inggris, hasil pencocokan, skor, dan koreksi pengguna disimpan pada tabel lain yang merujuk `kode`. Jangan menambah kolom ke berkas resmi.
8. **Kunci.** Gabungan `versi_kbji` dan `kode` dapat dipakai sebagai kunci setelah memastikan laporan duplikat kosong. Pada hasil ini laporan duplikat kosong.

Paket ini tidak menyediakan model klasifikasi lowongan dan tidak mengklaim akurasi pemetaan apa pun.

---

## 10. Pekerjaan lanjutan yang sudah diidentifikasi

**Tabel konversi KBJI 2014 → KBJI 2026 (Tabel 9–18, halaman PDF 49–85) belum diekstraksi.** Tabel ini berguna untuk memigrasikan data lama, dan sudah diuji keterbacaannya: 37 halaman terbaca sebagai grid lima kolom dengan total 647 baris. Namun tabel sumber tidak konsisten secara tipografi:

- 146 baris menuliskan kode di dalam sel judul, bukan di kolom kode;
- 58 baris menempatkan teks kolom Keterangan di kolom sebelahnya.

Merapikannya membutuhkan penilaian manusia per baris. Karena hasil paket ini harus dapat dipertanggungjawabkan tanpa tafsir, tabel tersebut tidak diterbitkan sebagai data pada rilis ini. Pengerjaannya memerlukan tahap peninjauan manual tersendiri dengan pengesahan penyusun.

Pekerjaan lain yang belum dilakukan:

- Pembacaan manual seluruh 3.010 redaksi uraian.
- Pemetaan ke ISCO-08 per entri. Publikasi hanya menyajikan perbedaan strukturnya pada Tabel 24, bukan padanan lengkap.
- Pengisian tingkat keterampilan untuk golongan pokok 5–8, yang sel sumbernya kosong.

---

## 11. Ketentuan hukum sebelum dipublikasikan

Halaman hak cipta publikasi (halaman PDF 4) berbunyi:

> ©Badan Pusat Statistik — "Dilarang mereproduksi dan/atau menggandakan sebagian atau seluruh isi buku ini untuk **tujuan komersial** tanpa izin tertulis dari Badan Pusat Statistik."

Konsekuensinya, dan ini yang paling mudah keliru:

1. **Kode program boleh berlisensi MIT. Data tidak boleh.** Lisensi MIT, Apache, maupun CC0 memberikan hak penggunaan komersial. Hak itu bukan milik Anda untuk diberikan. Karena itu `LICENSE` dibatasi tegas pada kode, dan `KETENTUAN_DATA.md` mengutip ketentuan BPS apa adanya tanpa menerbitkan lisensi baru atas isi KBJI.
2. **PDF sumber tidak boleh dikomit.** Selain berukuran 30 MB, berkas itu adalah publikasi berhak cipta secara utuh. `.gitignore` sudah mengecualikan `*.pdf`. Ilustrasi kover bersumber dari Freepik.com dan Canva dan tidak ikut ditranskripsi.
3. **Atribusi wajib terlihat**, bukan hanya di berkas lisensi. README, situs, dan tanggapan API semuanya mencantumkan sumber dan menegaskan bahwa ini bukan penerbitan resmi KBJI 2026.
4. **Sertakan selalu catatan selisih 447 vs 449.** Jangan menandai seluruh validasi lulus.
5. **Sediakan jalur penghapusan.** `SECURITY.md` menjanjikan penghapusan dalam 7 hari kerja bila BPS atau Kementerian Ketenagakerjaan berkeberatan. Janji itu harus benar-benar ditepati.
6. **Kirim pemberitahuan ke BPS.** Draf suratnya ada di `dokumen/surat-pemberitahuan-bps.md`. Surat itu sekaligus melaporkan ketidaksesuaian 447 vs 449, yang memang perlu diketahui penyusun. Biayanya nyaris nol dan risikonya hilang.

Hasil pemeriksaan kesiapan: tidak ada kredensial, token, maupun kunci API dalam repositori; tidak ada alamat surel atau data pribadi di dalam folder `output/`; berkas terbesar 7,2 MB sehingga jauh di bawah batas GitHub; total yang masuk git sekitar 26 MB.

---

## 12. Langkah publikasi ke GitHub

### Berkas yang dikomit

**Dikomit** — seluruh isi repositori kecuali yang tercantum pada `.gitignore`:

```
kbji.py  requirements.txt  config/  tests/  input/README.md
output/                 (±22 MB, 47 berkas — data hasil beserta validasi dan audit)
web/                    (kecuali node_modules/ dan .wrangler/; termasuk web/public/data/ ±5 MB)
.github/workflows/ci.yml   dokumen/
README.md  Panduan_KBJI_2026.md  KAMUS_DATA.md  CATATAN_PEMERIKSAAN.md
KETENTUAN_DATA.md  LICENSE  CITATION.cff  CONTRIBUTING.md  SECURITY.md  CHANGELOG.md
.gitignore
```

**Tidak dikomit:** `input/*.pdf`, `.venv/`, `__pycache__/`, `node_modules/`, `.wrangler/`, dan folder percobaan `output_baru*/`.

Folder `output/` dan `web/public/data/` sengaja dikomit supaya data langsung dapat dipakai tanpa menjalankan ekstraksi, dan supaya penyebaran dari GitHub berjalan tanpa Python. Keduanya hanya berubah bila BPS menerbitkan revisi.

### Langkah 1 — Isi tempat yang masih kosong

Sebagian besar sudah terisi: pemegang hak cipta, nama pemelihara, dan URL repositori. Sisa yang perlu
diisi sendiri:

| Berkas | Isi | Kapan |
|---|---|---|
| `README.md` | Alamat situs — sudah terisi `https://kbji-2026.sipk-paskerid.workers.dev` | Selesai |

Tidak ada nama pribadi maupun nama instansi di dalam repositori. Pemegang hak cipta kode ditulis
`KBJI 2026 Open Source Contributors`, dan pelaporan diarahkan ke kanal GitHub, bukan ke alamat surel.
Atribusi kepada Badan Pusat Statistik dan Kementerian Ketenagakerjaan tetap dicantumkan sebagai
**sumber publikasi**, bukan sebagai penyusun repositori.

Periksa sisanya kapan saja:

```bash
grep -rn "<ISI \|<SUBDOMAIN>" --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=output --exclude-dir=dokumen .
```

### Langkah 2 — Siapkan repositori lokal

```bash
# ganti dengan lokasi folder proyek Anda
cd "C:\KBJI\kbji_2026_python"
git init -b main
git add .
git status --short
```

Periksa keluaran `git status`. **Pastikan berkas PDF tidak muncul.** Bila muncul, jangan lanjutkan;
periksa `.gitignore` lebih dulu. Cek juga ukurannya:

```bash
git count-objects -vH
```

### Langkah 3 — Komit pertama

```bash
git config user.name "<NAMA ANDA>"
git config user.email "<SUREL ANDA>"
git commit -m "KBJI 2026: transkripsi terverifikasi, alat ekstraksi, situs, dan API"
```

### Langkah 4 — Sambungkan ke repositori GitHub

Repositori sudah dibuat di <https://github.com/alvinvigo/KBJI-2026>.

```bash
git remote add origin https://github.com/alvinvigo/KBJI-2026.git
git remote -v
```

### Langkah 5 — Dorong

```bash
git push -u origin main
```

Bila repositori di GitHub sudah terisi berkas awal, misalnya README otomatis, tarik dulu:

```bash
git pull --rebase origin main
git push -u origin main
```

### Langkah 6 — Rapikan halaman repositori

1. **About** (ikon roda gigi di kanan atas): isi deskripsi, tambahkan situs setelah Worker jalan, dan topik: `kbji`, `indonesia`, `ketenagakerjaan`, `occupation-classification`, `isco-08`, `bps`, `open-data`.
2. **Settings → Features**: nyalakan *Issues*. Matikan *Wikis* dan *Projects* bila tidak dipakai.
3. **Settings → Branches**: tambahkan aturan perlindungan untuk `main` — wajib lewat pull request, dan wajib lulus pemeriksaan `Uji`.
4. **Actions**: pastikan alur kerja `Uji` hijau. Alur ini menjalankan 26 tes pada Python 3.10–3.13, memvalidasi ulang CSV yang dikomit, memastikan nol temuan berkelas `ekstraksi`, dan memastikan `web/public/data/` sama dengan hasil pembangunan ulang.
5. **Releases → Create a new release**: tag `v2.0.0`, judul "KBJI 2026 v2.0.0", isi dari `CHANGELOG.md`. Lampirkan `kbji_2026_hierarki.csv` dan `kbji_2026_jabatan.csv` sebagai aset agar dapat diunduh tanpa mengkloning repositori.

### Langkah 7 — Kirim pemberitahuan ke BPS

Lengkapi `dokumen/surat-pemberitahuan-bps.md`, kirim, lalu catat hasilnya di `KETENTUAN_DATA.md` dan `CHANGELOG.md`.

---

## 13. Langkah menyebarkan ke Cloudflare Workers

Situs dan API berada di folder `web/`. Arsitekturnya: satu Worker kecil untuk `/api/*` dan `/sitemap.xml`, sisanya berkas statis. Tanpa basis data. Muat di paket gratis.

### Prasyarat

- Akun Cloudflare gratis — <https://dash.cloudflare.com/sign-up>
- Node.js 20 atau lebih baru — `node --version`
- Folder `web/public/data/` sudah terisi. Bila kosong: `python web/bangun_data.py`

### Langkah 1 — Pasang wrangler

```bash
cd web
npm install
```

Bila npm memblokir skrip pemasangan `esbuild` dan `workerd`, jalankan `npm install-scripts approve esbuild workerd && npm rebuild esbuild workerd`.

### Langkah 2 — Coba lokal lebih dulu

```bash
npx wrangler dev
```

Buka <http://127.0.0.1:8787>. Periksa lima hal:

```bash
curl http://127.0.0.1:8787/api/v1/meta
curl http://127.0.0.1:8787/api/v1/kode/2521.01
curl "http://127.0.0.1:8787/api/v1/cari?q=analis%20data"
curl -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8787/kode/2521.01   # 200, tautan dalam
curl -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8787/sitemap.xml     # 200
```

Hentikan dengan Ctrl+C.

### Langkah 3 — Masuk ke akun Cloudflare

```bash
npx wrangler login
```

Peramban akan terbuka untuk memberi izin. Verifikasi dengan `npx wrangler whoami`.

### Langkah 4 — Tentukan nama Worker

Nama menentukan alamatnya: `https://<nama>.<subdomain-akun>.workers.dev`. Ubah `name` pada `web/wrangler.jsonc` bila `kbji-2026` sudah dipakai orang lain.

```jsonc
{
  "name": "kbji-2026",
  "main": "src/index.js",
  "compatibility_date": "2025-09-15",
  "assets": { "directory": "./public", "binding": "ASSETS" },
  "observability": { "enabled": true }
}
```

### Langkah 5 — Uji kering

```bash
npx wrangler deploy --dry-run --outdir /tmp/worker-build
```

Tidak ada yang dikirim. Langkah ini hanya memastikan skrip dapat dibundel.

### Langkah 6 — Sebarkan

```bash
npx wrangler deploy
```

Wrangler mengunggah 457 berkas aset dan satu skrip Worker, lalu menampilkan alamatnya. Penyebaran pertama biasanya selesai dalam satu hingga dua menit; unggahan berikutnya hanya mengirim berkas yang berubah.

### Langkah 7 — Verifikasi produksi

Alamat situs muncul di akhir keluaran `wrangler deploy` dan pada halaman Worker di dashboard.
Untuk penyebaran ini: `https://kbji-2026.sipk-paskerid.workers.dev`.

**Paling mudah: tempel alamatnya di peramban.** JSON tampil rapi di Chrome maupun Edge.

**Windows PowerShell.** Tulis `curl.exe`, bukan `curl`. Di PowerShell, `curl` adalah alias
`Invoke-WebRequest` yang sintaksnya berbeda, sehingga `curl -s ...` akan ditolak. Perintah asli
PowerShell lebih nyaman karena JSON-nya langsung diurai:

```powershell
$situs = "https://kbji-2026.sipk-paskerid.workers.dev"
Invoke-RestMethod "$situs/api/v1/meta"
Invoke-RestMethod "$situs/api/v1/kode/0111.01"
(Invoke-WebRequest "$situs/kode/2521.01").StatusCode
(Invoke-WebRequest "$situs/").Headers["content-security-policy"]
```

**Command Prompt (CMD).** Di sini `curl` memang curl asli:

```bat
curl -s https://kbji-2026.sipk-paskerid.workers.dev/api/v1/meta
curl -s https://kbji-2026.sipk-paskerid.workers.dev/api/v1/kode/0111.01
curl -o NUL -w "%{http_code}" https://kbji-2026.sipk-paskerid.workers.dev/kode/2521.01
```

**macOS/Linux:**

```bash
SITUS=https://kbji-2026.sipk-paskerid.workers.dev
curl -s $SITUS/api/v1/meta | head -20
curl -o /dev/null -w "%{http_code}
" $SITUS/kode/2521.01
```

Jangan pernah menempelkan alamat yang masih memuat tanda kurung sudut seperti `<subdomain>`.
Di CMD dan PowerShell, `<` dan `>` adalah operator pengalihan berkas, sehingga perintahnya gagal
dengan pesan sintaks, bukan karena situsnya bermasalah.

Lalu buka situsnya, coba pencarian, buka satu entri, dan periksa tampilannya di ponsel.

### Langkah 8 — Isi alamatnya ke repositori

Alamat pada `README.md` sudah terisi: `https://kbji-2026.sipk-paskerid.workers.dev`. Isi juga kolom **About → Website** di halaman repositori GitHub.

### Langkah 9 (opsional) — Domain sendiri

Bila domain Anda sudah berada di Cloudflare: **Workers & Pages → kbji-2026 → Settings → Domains & Routes → Add → Custom domain**, isi misalnya `kbji.example.id`. Sertifikat TLS dibuat otomatis dalam beberapa menit. Alamat `workers.dev` tetap berfungsi.

### Langkah 10 (opsional) — Sebar otomatis dari GitHub

**Workers & Pages → kbji-2026 → Settings → Build → Connect repository**, pilih repositori dan cabang `main`, lalu isi:

| Kolom | Nilai |
|---|---|
| Root directory | `web` |
| Build command | *(kosongkan)* |
| Deploy command | `npx wrangler deploy` |

Build command dikosongkan karena `web/public/data/` sudah dikomit dan tidak perlu Python. Setiap dorongan ke `main` akan menyebar otomatis.

### Bila data diperbarui

```bash
python web/bangun_data.py --out output --data web/public/data
cd web && npx wrangler deploy
git add web/public/data output && git commit -m "Perbarui data" && git push
```

### Biaya dan batas

| | Paket gratis |
|---|---|
| Permintaan Worker | 100.000 per hari |
| Permintaan berkas statis | Tidak dibatasi dan tidak dihitung sebagai permintaan Worker |
| Waktu CPU | 10 ms per permintaan; Worker ini jauh di bawahnya |
| Berkas aset | 20.000 berkas, 25 MiB per berkas. Terpakai 457 berkas, terbesar sekitar 152 KB |

Penelusuran dan pencarian di situs berjalan di peramban dan membaca berkas statis, sehingga tidak memakai kuota Worker sama sekali. Kuota 100.000 hanya terpakai oleh pemanggilan `/api/*`, `/sitemap.xml`, dan pembukaan tautan dalam seperti `/kode/2521.01`.

### Pemecahan masalah penyebaran

| Kondisi | Langkah |
|---|---|
| `A worker with this name already exists` | Ganti `name` pada `wrangler.jsonc` |
| `Authentication error` | Jalankan ulang `npx wrangler login` |
| `/api/*` mengembalikan HTML, bukan JSON | Pastikan `main` dan `assets.binding` ada pada `wrangler.jsonc`, dan `not_found_handling` tidak disetel ke `single-page-application` |
| Situs tampil tetapi data kosong | `web/public/data/` belum dibuat. Jalankan `python web/bangun_data.py` lalu sebarkan ulang |
| `Too many files` | Periksa tidak ada `node_modules` di dalam `web/public/` |
| Perubahan tidak terlihat | Tembolok peramban. Muat ulang dengan Ctrl+F5; berkas di `/data/` memakai `max-age=3600` |
| Ingin melihat log langsung | `npx wrangler tail` |

---

## 14. Pemecahan masalah

| Pesan/kondisi | Langkah |
|---|---|
| `py` tidak dikenali | Pasang Python atau gunakan `python -m venv .venv` |
| PyMuPDF belum tersedia | Jalankan pip dengan interpreter `.venv` yang sama dengan interpreter ekstraksi |
| Fingerprint PDF berbeda | Pastikan PDF asli yang sama. Mengganti nama aman; mengubah isi PDF tidak |
| Folder keluaran tidak kosong | Gunakan nama folder keluaran baru |
| Exit code `3` | Normal untuk PDF ini. Ekstraksi lengkap; yang ditemukan adalah ketidaksesuaian di dalam publikasi |
| Exit code `2` | Ada dugaan cacat ekstraksi. Buka `validasi/LAPORAN_VALIDASI.md` bagian "Temuan proses ekstraksi" |
| Nol di depan hilang di Excel | Impor ulang CSV asli dan tetapkan tipe Text sebelum memuat |
| `GAGAL: ... berkas tidak ditemukan` | Periksa lokasi CMD dan jalur PDF; gunakan tanda kutip untuk jalur berspasi |
| PDF hasil pindai | Profil ini membutuhkan lapisan teks dan font sumber; OCR tidak didukung |
