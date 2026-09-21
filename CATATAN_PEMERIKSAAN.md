# Catatan pemeriksaan

Sumber: **Klasifikasi Baku Jabatan Indonesia (KBJI) 2026**, Volume 1, 2026. Badan Pusat Statistik dan Kementerian Ketenagakerjaan Republik Indonesia. Katalog 1302037, nomor publikasi 03100.26011.

| | |
|---|---|
| Berkas | 1.110 halaman PDF, 30.368.071 bita |
| SHA-256 | `19690c6c53f386ecd3f1f057a6159c06ad7bf87ec597f3e07cc7b83d426b43cf` |
| Alat | Python 3.13.14, PyMuPDF 1.26.6, `kbji.py` 2.0.0 |
| Bagian uraian | Halaman PDF 103–1108 (halaman cetak 71–1076) |
| Daftar Isi | Halaman PDF 11–26 |

Status akhir: **ekstraksi LENGKAP_DAN_KONSISTEN (0 temuan)**, **dokumen sumber ADA_INKONSISTENSI (3 temuan)**, 47 catatan informasi.

---

## 1. Hasil ekstraksi

| Tingkat | Hasil | Acuan Tabel 3 |
|---|---:|---:|
| Golongan pokok (1 digit) | 10 | 10 |
| Subgolongan pokok (2 digit) | 43 | 43 |
| Golongan (3 digit) | 130 | 130 |
| Subgolongan (4 digit) | **447** | **449** |
| Jabatan (6 digit) | 2.380 | 2.380 |
| **Total entri** | **3.010** | 3.012 |

Kode terkecil dan terbesar sesuai narasi halaman PDF 44–45: subgolongan `0111`–`9629`, jabatan `0111.01`–`9629.99`.

---

## 2. Bukti bahwa selisih 447 vs 449 berasal dari dokumen sumber

Empat jalur pemeriksaan yang tidak saling bergantung menghasilkan angka yang sama.

### 2.1 Daftar Isi — 447

Daftar Isi diurai ulang secara terpisah dari bagian uraian, memakai posisi kolom kode pada halaman PDF 11–26. Hasilnya 630 entri: 10 golongan pokok, 43 subgolongan pokok, 130 golongan, **447 subgolongan**. Tidak ada kode ganda.

### 2.2 Judul pada bagian uraian — 447

Pembacaan bagian uraian menghasilkan 447 judul subgolongan.

### 2.3 Pemindaian kolom kode tanpa aturan huruf tebal — 447

Seluruh fragmen teks (span) pada halaman PDF 103–1108 yang isinya persis sebuah kode KBJI dan berada pada kolom kiri isi dipindai ulang, tanpa memakai syarat huruf tebal yang dipakai parser. Hasilnya **persis 3.010 kode, identik dengan hasil parsing** — tidak ada satu pun kode yang terlewat, dan tidak ada satu pun kode yang diciptakan.

Pemindaian yang lebih longgar, yaitu seluruh baris pada bagian uraian yang diawali empat angka, menemukan 484 token. Setelah 37 nomor halaman pada margin bawah dikeluarkan, sisanya tepat 447 kode subgolongan. Pemindaian pada tingkat span menemukan 429 angka empat digit tambahan di kolom kode; seluruhnya berada pada koordinat `y ≈ 681` yaitu baris nomor halaman, di luar batas bawah isi (`y = 670`).

### 2.4 Daftar anak di dalam uraian induk — konsisten

Uraian golongan pokok, subgolongan pokok, dan golongan sering memuat daftar kode anaknya. Sebanyak 173 entri induk memuat daftar seperti itu, dengan total 584 rujukan kode anak. **Seluruh 584 kode tersebut memiliki judul sendiri pada bagian uraian.** Tidak ada satu pun kode yang disebut sebagai anak tetapi tidak diuraikan.

### 2.5 Kecocokan Daftar Isi dengan bagian uraian

Untuk seluruh 630 kode tingkat 1–4 digit, Daftar Isi dan bagian uraian cocok pada tiga hal sekaligus:

- himpunan kode identik;
- **nama identik** pada setiap kode;
- **nomor halaman cetak identik** pada setiap kode.

Nol perbedaan. Rekamannya ada pada `output/audit/rekonsiliasi_daftar_isi.csv`.

### 2.6 Letak angka 449 di dalam publikasi

Pencarian teks pada seluruh 1.110 halaman menemukan angka 449 sebagai jumlah subgolongan hanya pada tiga tempat:

| Halaman PDF | Halaman cetak | Konteks |
|---|---|---|
| 44 | 12 | Narasi: "…membentuk tingkatan disagregasi yang lebih rinci menjadi 449 subgolongan" dan "Pengelompokan subgolongan ini berjumlah 449, mempunyai kode 0111 sampai dengan 9629" |
| 45 | 13 | Tabel 3 Banyaknya Golongan Pokok, Subgolongan Pokok, Golongan, Subgolongan, dan Jabatan pada KBJI 2026 |
| 86 | 54 | Tabel 19 Perbandingan Nama Struktur dan Jumlah Struktur KBJI 2014 dengan KBJI 2026 |

Angka 447 tidak pernah disebut sebagai jumlah subgolongan di dalam publikasi.

### 2.7 Rincian per golongan pokok

Jumlah pada Tabel 25–34 konsisten satu sama lain: dijumlahkan menghasilkan tepat 449. Selisihnya terletak pada dua golongan pokok.

| Golongan pokok | Rujukan | Acuan | Daftar Isi | Uraian |
|---|---|---:|---:|---:|
| 2 Profesional | Tabel 27, halaman cetak 62 / PDF 94 | 94 | 93 | 93 |
| 6 Pekerja Terampil Pertanian, Kehutanan, dan Perikanan | Tabel 31, halaman cetak 64 / PDF 96 | 19 | 18 | 18 |

Delapan golongan pokok lainnya cocok seluruhnya. **Seluruh jumlah jabatan enam digit per golongan pokok cocok sempurna dengan tabel ringkasannya**, total 2.380. Jumlah golongan pokok, subgolongan pokok, dan golongan juga cocok seluruhnya.

Karena setiap subgolongan pada publikasi ini memiliki sedikitnya satu jabatan, dua subgolongan yang "hilang" tidak dapat dijelaskan sebagai subgolongan tanpa jabatan.

### 2.8 Kesimpulan

Ketidaksesuaian ada di dalam publikasi: tabel ringkasan menyebut 449 sedangkan Daftar Isi dan isi buku memuat 447. Tidak ditemukan dasar apa pun di dalam dokumen untuk menyebut dua kode tertentu sebagai kode yang hilang. Tidak ada kode dugaan yang ditambahkan, dan angka acuan tidak diubah menjadi 447 untuk memperoleh status lulus.

**Perlu dikonfirmasikan kepada tim penyusun** apakah Tabel 3, Tabel 19, Tabel 27, dan Tabel 31 perlu diralat, atau ada dua subgolongan yang seharusnya tercetak.

---

## 3. Temuan lain pada dokumen sumber

### 3.1 Kode 5412 tidak dipakai

Golongan 541 Tenaga Usaha Jasa Perlindungan memuat 5411, 5413, 5414, dan 5419. Kode **5412 tidak muncul sama sekali** dalam 1.110 halaman publikasi. Ini satu-satunya celah penomoran interior pada seluruh 130 golongan.

Pemeriksaan konvensi penomoran pada 130 golongan menunjukkan:

- 129 golongan tidak memiliki celah penomoran interior;
- 26 golongan bersubgolongan tunggal seluruhnya memakai konvensi akhiran 0 (`1120`, `5120`, `6210`, dan seterusnya) sesuai penjelasan pada halaman PDF 46;
- tidak ada golongan yang memakai kode berakhiran 0 bersama subgolongan lain;
- seluruh 447 subgolongan memiliki sedikitnya satu jabatan;
- setiap subgolongan yang hanya memiliki satu jabatan memakai akhiran `.00`, sesuai contoh `5120.00` pada halaman PDF 46. Nol pengecualian.

### 3.2 Tabel 1 mengosongkan tingkat keterampilan untuk golongan pokok 5–8

Pada Tabel 1 (halaman PDF 38), kolom Tingkat Keterampilan terisi untuk golongan pokok 0, 1, 2, 3, 4, dan 9, tetapi kosong untuk 5, 6, 7, dan 8. Pemeriksaan garis tabel menunjukkan sel-sel itu memang sel terpisah yang kosong, bukan sel gabungan. Nilai tersebut **tidak diisi** pada `output/referensi/tingkat_keterampilan.csv`; kolom `catatan_sumber` menjelaskan alasannya.

### 3.3 Penamaan kelompok sisa

Ada 23 entri yang penanda kelompok sisanya berdasarkan kode berbeda dari penamaannya, misalnya nama berbunyi "… LAINNYA" sementara kodenya tidak berakhiran 9. Seluruhnya tercatat pada `output/validasi/penanda_sisa.csv` sebagai catatan informasi. Tidak ada nama maupun kode yang diubah.

### 3.4 Tabel 19 menyebut KBJI 2014 memiliki 446 subgolongan

Angka ini tidak diverifikasi oleh paket ini karena publikasi KBJI 2014 bukan sumber di sini.

---

## 4. Pemeriksaan teknis yang dijalankan

| Pemeriksaan | Hasil |
|---|---|
| Fingerprint SHA-256 PDF | Cocok |
| Jumlah halaman | 1.110, sesuai profil |
| Baris teks isi terpetakan | 34.913 baris, seluruhnya memiliki `id_entri` dan peran (judul, lanjutan judul, atau uraian). Nol baris tidak terpetakan |
| Elemen dikeluarkan | 1.991: 1.006 watermark diagonal dan 985 baris margin kepala/kaki |
| Isi watermark | Seluruh 1.006 elemen diagonal berisi `https://www.bps.go.id`. Nol watermark tersisa di dalam data |
| Baris margin | Hanya 12 pola berbeda, seluruhnya judul berjalan dan nomor halaman. Tidak ada yang menyerupai judul kode |
| Cakupan halaman | 1.006 halaman: 983 terbaca, 9 pembatas bab, 14 halaman kosong |
| Kode duplikat | Nol |
| Kode tanpa induk | Nol |
| Nama kosong | Nol |
| Uraian kosong | Nol |
| Format kode tidak sah | Nol |
| Pola menyerupai judul yang tidak terpetakan | Nol |
| Konsistensi kolom turunan | Nol selisih; seluruh 3.010 baris dihitung ulang dan cocok |
| Urutan kode menurun | Nol |
| Rentang halaman dan nomor cetak | Nol pelanggaran |
| Karakter pengganti (U+FFFD) | Nol. Karakter non-ASCII yang muncul hanya em dash (10), en dash (3), dan tanda kutip tipografis (4) |
| Rekonsiliasi Daftar Isi | 630 kode; kode, nama, dan halaman cetak cocok seluruhnya |
| Rekonsiliasi rujukan induk–anak | 173 induk, 584 rujukan; nol yang tidak diuraikan |
| Pemindaian kolom kode | 3.010 kode; identik dengan hasil parsing |
| Halaman tanpa isi | 23 halaman terdeteksi otomatis, sama persis dengan daftar pada profil |
| Pengujian regresi | 26 tes lulus |
| Validasi ulang CSV | Membaca ulang CSV hasil dan menjalankan seluruh validator struktur: 0 temuan ekstraksi |
| Perlindungan folder keluaran | Diuji: proses menolak menimpa folder yang tidak kosong, keluar dengan kode 1 |

### Halaman tanpa teks isi

Diklasifikasikan otomatis dari isi PDF, bukan dari daftar manual, lalu dicocokkan dengan daftar pada profil. Keduanya identik.

- **Pembatas bab** (satu gambar halaman penuh, teks hanya judul berjalan atau tidak ada): PDF 159, 261, 509, 715, 757, 823, 869, 967, 1055.
- **Halaman kosong** (tanpa teks dan tanpa gambar): PDF 160, 260, 262, 510, 714, 716, 758, 824, 868, 870, 966, 968, 1054, 1056.

---

## 5. Batas pemeriksaan

- **Redaksi uraian belum dibaca manual satu per satu.** Yang diverifikasi adalah kelengkapan kode, ketepatan nama untuk 630 entri tingkat 1–4 digit melalui Daftar Isi, dan keutuhan struktur. Nama 2.380 jabatan enam digit tidak memiliki pembanding independen di dalam publikasi karena Daftar Isi tidak memuat tingkat enam digit.
- Pemisahan baris, ejaan, dan tanda hubung sumber dipertahankan, termasuk bila tampak keliru.
- Tabel konversi KBJI 2014 → 2026 (Tabel 9–18, halaman PDF 49–85) **belum diekstraksi**. Keterbacaannya sudah diuji: 37 halaman terbaca sebagai grid lima kolom, total 647 baris. Namun 146 baris menuliskan kode di dalam sel judul alih-alih kolom kode, dan 58 baris menempatkan teks kolom Keterangan di kolom sebelahnya. Merapikannya membutuhkan penilaian per baris, sehingga hasilnya tidak dapat dipertanggungjawabkan tanpa peninjauan manual. Tabel tersebut sengaja tidak diterbitkan sebagai data pada rilis ini.
- Tidak ada pemetaan per entri ke ISCO-08. Publikasi hanya menyajikan perbedaan strukturnya pada Tabel 24 (halaman PDF 91–92), bukan padanan lengkap.
- Profil ini khusus untuk tata letak PDF yang diuji. PDF hasil pindai atau cetak ulang dapat memiliki font dan koordinat berbeda.
- Paket ini tidak menyediakan model klasifikasi lowongan dan tidak mengklaim akurasi pemetaan.

---

## 6. Pernyataan

Transkripsi ini pekerjaan teknis atas publikasi resmi dan merupakan proyek sumber terbuka. Bukan penerbitan resmi KBJI 2026 dan tidak mewakili lembaga mana pun. Isi resmi tetap merujuk pada publikasi cetak dan digital yang diterbitkan Badan Pusat Statistik bersama Kementerian Ketenagakerjaan. Setiap perbedaan antara berkas ini dan publikasi harus diselesaikan dengan memenangkan publikasi, dan dilaporkan agar dapat diperbaiki.
