<div align="center">

# KBJI 2026 → CSV, JSON, dan API

**Klasifikasi Baku Jabatan Indonesia 2026 dalam bentuk data terstruktur.**
Transkripsi terverifikasi dari publikasi PDF resmi, beserta alat ekstraksinya,
situs penelusuran, dan API JSON terbuka.

[![Uji](https://github.com/alvinvigo/KBJI-2026/actions/workflows/ci.yml/badge.svg)](https://github.com/alvinvigo/KBJI-2026/actions/workflows/ci.yml)
[![Lisensi kode: MIT](https://img.shields.io/badge/lisensi%20kode-MIT-blue.svg)](LICENSE)
[![Data: ketentuan BPS](https://img.shields.io/badge/data-ketentuan%20BPS-orange.svg)](KETENTUAN_DATA.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://www.python.org/downloads/)

[Situs](https://kbji-2026.sipk-paskerid.workers.dev) · [API](https://kbji-2026.sipk-paskerid.workers.dev/api/v1) · [Panduan](Panduan_KBJI_2026.md) · [Kamus data](KAMUS_DATA.md) · [Catatan pemeriksaan](CATATAN_PEMERIKSAAN.md)

</div>

---

## Apa ini

Publikasi KBJI 2026 terbit sebagai PDF 1.110 halaman. Bentuk itu sulit dipakai untuk pengkodean data
ketenagakerjaan. Repositori ini mengubahnya menjadi CSV dan JSON hierarkis **tanpa mengubah satu huruf
pun isinya**, lalu membuktikan bahwa hasilnya utuh.

| | |
|---|---|
| **Sumber** | Klasifikasi Baku Jabatan Indonesia (KBJI) 2026, Volume 1 — Badan Pusat Statistik dan Kementerian Ketenagakerjaan RI. Katalog 1302037, Nomor Publikasi 03100.26011 |
| **Berkas sumber** | 1.110 halaman, SHA-256 `19690c6c…b43cf` |
| **Hasil** | **3.010 entri** — 10 golongan pokok, 43 subgolongan pokok, 130 golongan, **447 subgolongan**, 2.380 jabatan |
| **Status transkripsi** | `LENGKAP_DAN_KONSISTEN` — 0 temuan |
| **Status dokumen sumber** | `ADA_INKONSISTENSI_DOKUMEN_SUMBER` — 3 temuan |
| **Dependensi** | Satu: `PyMuPDF`. Tanpa OCR, tanpa AI, tanpa layanan berbayar |

## Mengapa 447, bukan 449

Tabel 3 publikasi menyebut 449 subgolongan. Daftar Isi dan isi bukunya memuat 447. **Selisih ini berasal
dari dokumen sumber, bukan dari transkripsi**, dan tidak ditutup dengan menambahkan kode.

Empat pemeriksaan yang tidak saling bergantung menghasilkan angka yang sama:

| Jalur pemeriksaan | Hasil |
|---|---:|
| Daftar Isi publikasi (halaman PDF 11–26), diurai terpisah | 447 |
| Judul pada bagian uraian (halaman PDF 103–1108) | 447 |
| Pemindaian setiap fragmen teks pada kolom kode, tanpa aturan huruf tebal | 447 |
| Daftar kode anak di dalam uraian induk — 584 rujukan dari 173 entri | 0 yang tidak diuraikan |

Untuk seluruh 630 kode tingkat 1–4 digit, **kode, nama, dan nomor halaman cetak identik** antara Daftar
Isi dan bagian uraian — nol perbedaan. Angka 449 hanya muncul pada narasi halaman PDF 44, Tabel 3
(PDF 45), dan Tabel 19 (PDF 86). Selisihnya terletak pada golongan pokok 2 (93 vs 94, Tabel 27) dan
golongan pokok 6 (18 vs 19, Tabel 31).

Hal ini perlu dikonfirmasikan kepada tim penyusun. Bukti lengkapnya ada di
[CATATAN_PEMERIKSAAN.md](CATATAN_PEMERIKSAAN.md).

> **Bila Anda membagikan ulang data ini, sertakan catatan selisih tersebut.** Jangan menandai seluruh
> validasi lulus.

## Berkas hasil

Semuanya ada di [`output/`](output). UTF-8 dengan BOM, seluruh sel dikutip — impor kolom kode sebagai
**Text** agar nol depan tidak hilang.

| Berkas | Isi |
|---|---|
| `kbji_2026_hierarki.csv` | 3.010 entri seluruh tingkat, 30 kolom. Berkas utama |
| `kbji_2026_jabatan.csv` | 2.380 jabatan enam digit, sudah membawa nama seluruh leluhurnya |
| `kbji_2026_ringkas.csv` | Daftar kode ringan tanpa uraian, untuk validasi kode di aplikasi |
| `kbji_2026_hierarki.json` | Data sama dalam JSON; seluruh kode bertipe string |
| `kbji_2026_pohon.json` | Struktur bersarang untuk penelusuran taksonomi |
| `referensi/` | Transkripsi Daftar Isi, Tabel 1 tingkat keterampilan, dan angka acuan Tabel 3 serta 25–34 |
| `validasi/` | Laporan validasi dan temuan per kategori |
| `audit/` | Jejak lengkap: 34.913 baris teks sumber beserta koordinat, elemen yang dikeluarkan, dan tiga rekonsiliasi |

Definisi setiap kolom ada di [KAMUS_DATA.md](KAMUS_DATA.md).

```python
import csv
with open('output/kbji_2026_hierarki.csv', encoding='utf-8-sig', newline='') as f:
    kbji = list(csv.DictReader(f))
print(next(r for r in kbji if r['kode'] == '2521.01')['nama_resmi'])
# ADMINISTRATOR BASIS DATA
```

## API

Baca-saja, tanpa autentikasi, CORS terbuka.

```bash
curl https://kbji-2026.sipk-paskerid.workers.dev/api/v1/kode/2521.01
curl "https://kbji-2026.sipk-paskerid.workers.dev/api/v1/cari?q=analis%20data&tingkat=6"
curl https://kbji-2026.sipk-paskerid.workers.dev/api/v1/anak/252
```

Di **Windows PowerShell** tulis `curl.exe`, bukan `curl` — `curl` di PowerShell adalah alias
`Invoke-WebRequest` yang sintaksnya berbeda. Atau pakai perintah asli PowerShell:

```powershell
Invoke-RestMethod https://kbji-2026.sipk-paskerid.workers.dev/api/v1/kode/2521.01
```

Di **Command Prompt (CMD)** perintah `curl` di atas berjalan apa adanya. Cara paling mudah:
tempel saja alamatnya di peramban.

| Titik akhir | Keterangan |
|---|---|
| `/api/v1/meta` | Metadata sumber, status validasi, jumlah per tingkat |
| `/api/v1/kode/{kode}` | Satu entri lengkap beserta leluhur dan anak langsung |
| `/api/v1/anak/{kode}` | Anak langsung sebuah kode |
| `/api/v1/cari?q=` | Pencarian nama atau kode. Parameter: `q`, `tingkat`, `limit`, `offset` |
| `/api/v1/tingkat/{digit}` | Seluruh entri pada satu tingkat |

Rinciannya di [web/README.md](web/README.md).

## Menjalankan sendiri

PDF sumber tidak disertakan. Unduh dari situs resmi BPS, lalu letakkan di `input/`.

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v          # 26 tes
.venv/bin/python kbji.py extract --pdf "input/<berkas>.pdf" --out output_baru
```

Di Windows gunakan `.venv\Scripts\python.exe`. Langkah rincinya di
[Panduan_KBJI_2026.md](Panduan_KBJI_2026.md).

Kode keluar: `0` tanpa temuan · `1` gagal · `2` ada dugaan cacat ekstraksi · `3` ekstraksi lengkap dengan
ketidaksesuaian pada dokumen sumber. **PDF KBJI 2026 menghasilkan `3`.**

Hasilnya deterministik: dua kali jalan menghasilkan berkas yang identik bita demi bita.

## Cara kerja

Ekstraksi berbasis tata letak, bukan pencocokan pola teks. Judul dikenali sebagai kode bercetak tebal
pada kolom kiri, sehingga angka yang muncul di dalam uraian tidak ikut terbaca sebagai entri. Watermark
diagonal dikeluarkan berdasarkan arah teks, margin berdasarkan koordinat. Uraian lintas halaman
disambung sampai judul kode berikutnya.

Setelah itu dijalankan delapan pemeriksaan: struktur, hierarki, konsistensi kolom turunan, konvensi
penomoran, perbandingan jumlah, rekonsiliasi Daftar Isi, rujukan induk–anak, dan pemindaian kolom kode.

**Prinsip yang mengikat:** kolom resmi ditranskripsi apa adanya, termasuk ejaan yang tampak keliru.
Contohnya uraian `2521.02` memuat frasa "coon basis data" persis seperti tercetak pada halaman PDF 449.
Tidak ada entri yang ditambahkan atau dihapus, dan angka acuan publikasi tidak pernah diubah.

## Ketentuan

**Kode program** — lisensi MIT, lihat [LICENSE](LICENSE).

**Data KBJI 2026** — hak cipta ©Badan Pusat Statistik. Halaman hak cipta publikasi menyatakan: *dilarang
mereproduksi dan/atau menggandakan sebagian atau seluruh isi buku untuk tujuan komersial tanpa izin
tertulis dari Badan Pusat Statistik.* Ketentuan itu berlaku penuh atas folder `output/` dan
`web/public/data/`. Repositori ini **tidak menerbitkan lisensi apa pun** atas isi KBJI dan tidak dapat
memberikan hak yang tidak dimilikinya. Selengkapnya di [KETENTUAN_DATA.md](KETENTUAN_DATA.md).

**Sifat repositori** — proyek sumber terbuka yang dikerjakan secara mandiri. **Bukan penerbitan resmi
KBJI 2026** dan tidak mewakili lembaga mana pun. Penerbitan resminya adalah publikasi cetak dan digital
yang dikeluarkan Badan Pusat Statistik. Setiap perbedaan antara berkas di sini dan publikasi harus
diselesaikan dengan memenangkan publikasi. Permintaan penghapusan dari Badan Pusat Statistik akan
dipenuhi dalam 7 hari kerja — lihat [SECURITY.md](SECURITY.md).

## Berkontribusi

Baca [CONTRIBUTING.md](CONTRIBUTING.md) lebih dulu — aturan "tidak boleh mengubah kolom resmi" menentukan
bentuk hampir semua kontribusi. Yang paling dibutuhkan: verifikasi manual redaksi jabatan enam digit, dan
ekstraksi tabel konversi KBJI 2014 → 2026.
