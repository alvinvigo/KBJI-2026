# Kamus data

Unit observasi: satu entri kode KBJI pada satu tingkat hierarki. Kode enam digit ditampilkan dengan titik setelah digit keempat.

Seluruh berkas CSV berformat UTF-8 dengan BOM, delimiter koma, dan seluruh sel dikutip. **Impor semua kolom sebagai teks.** CSV tidak membawa definisi tipe; bila kolom kode dibaca sebagai angka, nol depan pada kode seperti `0111` akan hilang.

---

## 1. `output/kbji_2026_hierarki.csv`

Berkas utama. 3.010 baris, 30 kolom. `kbji_2026_jabatan.csv` memakai kolom yang sama tetapi hanya memuat 2.380 entri enam digit.

### Kolom resmi — transkripsi dari publikasi

Kolom ini adalah isi PDF apa adanya. Jangan diubah.

| Kolom | Tipe saat impor | Definisi |
|---|---|---|
| `kode` | teks | Kode seperti tercetak, termasuk nol depan dan titik. Contoh `0111.01` |
| `nama_resmi` | teks | Judul entri; kapital dan ejaan sumber dipertahankan. Judul yang tercetak dalam beberapa baris digabung dengan satu spasi |
| `uraian_resmi` | teks | Seluruh teks di bawah judul sampai judul kode berikutnya. Pergantian baris PDF dipertahankan. Dapat memuat daftar tugas, contoh jabatan, pengecualian, catatan, dan rujukan kode lain |
| `halaman_pdf_mulai` | integer | Halaman PDF (1-based) tempat judul entri dimulai |
| `halaman_pdf_selesai` | integer | Halaman PDF terakhir yang menyumbang judul atau uraian entri |
| `halaman_cetak_mulai` | integer | Nomor halaman tercetak; pada profil ini = halaman PDF − 32 |
| `halaman_cetak_selesai` | integer | Nomor halaman tercetak terakhir |

### Kolom struktural — dihitung dari kode

| Kolom | Tipe saat impor | Definisi |
|---|---|---|
| `versi_kbji` | teks | Tahun edisi, `2026` |
| `kode_normalisasi` | teks | Kode tanpa titik; `0111.01` menjadi `011101` |
| `jumlah_digit` | integer | 1, 2, 3, 4, atau 6 |
| `tingkat` | teks | Golongan pokok, Subgolongan pokok, Golongan, Subgolongan, atau Jabatan |
| `kedalaman` | integer | 1–5 mengikuti urutan tingkat; berguna untuk operasi pohon karena `jumlah_digit` melompat dari 4 ke 6 |
| `kode_induk` | teks | Kode satu tingkat di atasnya; kosong untuk golongan pokok |
| `id_entri` | teks | Nomor urut ekstraksi (`E00001` dan seterusnya). Bukan kode resmi dan tidak dijamin tetap antar-sumber |
| `urutan` | integer | Nomor urut kemunculan pada publikasi, 1–3.010. Pakai untuk menampilkan data dalam urutan buku |

### Kolom turunan — untuk pemakaian, bukan untuk sitasi

Seluruh kolom di bawah ini dihitung ulang dan diperiksa setiap kali `validate` dijalankan. Kolom ini mempermudah penggunaan; rujukan resmi tetap `kode`, `nama_resmi`, dan `uraian_resmi`.

| Kolom | Tipe saat impor | Definisi |
|---|---|---|
| `kode_golongan_pokok` | teks | Kode 1 digit dari rantai induk. Untuk entri 1 digit, berisi kodenya sendiri |
| `nama_golongan_pokok` | teks | `nama_resmi` dari entri 1 digit tersebut |
| `kode_subgolongan_pokok` | teks | Kode 2 digit; kosong untuk entri 1 digit |
| `nama_subgolongan_pokok` | teks | `nama_resmi` dari entri 2 digit tersebut |
| `kode_golongan` | teks | Kode 3 digit; kosong untuk entri 1–2 digit |
| `nama_golongan` | teks | `nama_resmi` dari entri 3 digit tersebut |
| `kode_subgolongan` | teks | Kode 4 digit; kosong untuk entri 1–3 digit |
| `nama_subgolongan` | teks | `nama_resmi` dari entri 4 digit tersebut |
| `jalur_kode` | teks | Rantai kode dari golongan pokok sampai entri ini, dipisah ` > `. Contoh `2 > 25 > 252 > 2521 > 2521.01` |
| `jalur_nama` | teks | Rantai `nama_resmi` yang bersesuaian, dipisah ` > ` |
| `jumlah_anak_langsung` | integer | Banyaknya entri yang `kode_induk`-nya adalah kode ini. Bernilai 0 untuk jabatan |
| `jumlah_jabatan_turunan` | integer | Banyaknya jabatan enam digit di bawah entri ini. Bernilai 0 untuk entri jabatan itu sendiri |
| `kelompok_sisa` | teks | `ya` bila kode menandai kelompok sisa/lainnya, `tidak` bila tidak. Lihat bagian 4 |
| `nama_pencarian` | teks | `nama_resmi` dalam huruf kecil, tanda baca diganti spasi, spasi dirapatkan. Untuk pencocokan teks. Kolom resmi tidak ikut berubah |

### Kolom status

| Kolom | Tipe saat impor | Definisi |
|---|---|---|
| `status_validasi` | teks | `lolos_struktur_otomatis_belum_review_manual` bila tidak ada temuan berkategori error atau peringatan yang dikaitkan ke entri ini; `perlu_tinjauan_entri` bila ada |

`status_validasi` menyatakan hasil pemeriksaan struktur, bukan pengesahan substansi. Masalah tingkat dataset — misalnya selisih jumlah subgolongan — tercatat pada ringkasan validasi dan tidak mengubah status setiap entri.

---

## 2. `output/kbji_2026_ringkas.csv`

Daftar kode ringan tanpa `uraian_resmi`, untuk dipakai sebagai tabel referensi aplikasi dan validasi kode. Kolom: `kode`, `kode_normalisasi`, `jumlah_digit`, `tingkat`, `kode_induk`, `nama_resmi`, `kode_golongan_pokok`, `nama_golongan_pokok`, `jalur_kode`, `kelompok_sisa`, `halaman_cetak_mulai`. Definisinya sama dengan tabel di atas.

## 3. Berkas JSON

| Berkas | Bentuk |
|---|---|
| `kbji_2026_hierarki.json` | Larik objek; satu objek per entri dengan kolom yang sama seperti CSV. Seluruh kode bertipe string |
| `kbji_2026_pohon.json` | Struktur bersarang. Setiap simpul memuat `kode`, `nama_resmi`, `tingkat`, `jumlah_digit`, `kelompok_sisa`, `halaman_cetak_mulai`, dan `anak`. Tanpa `uraian_resmi` agar ringan |

---

## 4. Aturan `kelompok_sisa`

Publikasi menjelaskan pada halaman cetak 13 (PDF 45) bahwa angka 9 dipakai untuk kode "lainnya" yang menampung kelompok yang belum disebutkan. Kolom `kelompok_sisa` menerapkannya sebagai aturan **kode**, bukan tafsir judul:

- tingkat 2, 3, dan 4 digit: `ya` bila digit terakhir adalah `9`;
- jabatan 6 digit: `ya` bila akhiran dua digitnya `99`;
- golongan pokok: selalu `tidak`, karena kode 0–9 dipakai penuh untuk sepuluh golongan pokok.

Sebagian entri bernama "… LAINNYA" atau "… YTDL" tetapi kodenya tidak berakhiran 9, dan sebaliknya. Ketidaksesuaian semacam itu berasal dari penamaan sumber, bukan dari perhitungan. Seluruh 23 kasus pada publikasi ini tercatat di `output/validasi/penanda_sisa.csv` sebagai catatan informasi.

Untuk pemetaan otomatis, perlakukan `kelompok_sisa = ya` sebagai pilihan terakhir: pakai hanya bila tidak ada kode spesifik yang cocok.

---

## 5. Berkas referensi

| Berkas | Isi |
|---|---|
| `referensi/daftar_isi.csv` | Transkripsi Daftar Isi (halaman PDF 11–26). Kolom `kode`, `nama_daftar_isi`, `halaman_cetak`, `halaman_pdf_daftar_isi`. 630 baris, tingkat 1–4 digit saja; Daftar Isi tidak memuat jabatan enam digit |
| `referensi/tingkat_keterampilan.csv` | Transkripsi Tabel 1 (halaman PDF 38). Kolom `golongan_pokok`, `nama`, `tingkat_keterampilan`, `catatan_sumber`. Sel tingkat keterampilan untuk golongan pokok 5–8 **kosong pada sumber** dan sengaja tidak diisi; `catatan_sumber` menjelaskannya. Gabungkan dengan data utama melalui `kode_golongan_pokok` bila diperlukan, dan perlakukan nilai kosong sebagai tidak tersedia, bukan sebagai nol |
| `referensi/jumlah_acuan_publikasi.csv` | Angka acuan Tabel 3 dan Tabel 25–34 beserta rujukan halamannya. Kolom `cakupan`, `jumlah_digit`, `tingkat`, `acuan_publikasi`, `rujukan` |

---

## 6. Berkas validasi

Laporan gabungan `semua_temuan.csv` dan setiap berkas per kategori memakai kolom berikut:

| Kolom | Definisi |
|---|---|
| `kategori` | Salah satu dari: duplikat, tanpa_induk, nama_kosong, uraian_kosong, format_kode, pola_tidak_terbaca, hierarki, turunan, urutan, halaman, karakter, metadata, cakupan, kelengkapan_kode, daftar_isi, nama_daftar_isi, halaman_daftar_isi, anak_induk, penomoran, penanda_sisa, jumlah_tidak_sesuai |
| `kelas` | `ekstraksi` = dugaan cacat pada proses ini; `sumber` = ketidaksesuaian di dalam publikasi |
| `keparahan` | `error`, `peringatan`, atau `informasi` |
| `id_entri`, `kode`, `halaman_pdf` | Penunjuk ke entri dan halaman terkait, bila ada |
| `detail` | Penjelasan temuan |

Berkas kategori yang tidak memiliki temuan tetap dibuat berisi header saja, supaya proses hilir tidak gagal karena berkas tidak ada.

`ringkasan.json` memuat `status_ekstraksi`, `status_sumber`, cacah temuan per kelas dan per keparahan, perbandingan jumlah per tingkat, serta seluruh metadata dan profil yang dipakai.

---

## 7. Cara memakai data ini

- Gunakan gabungan `versi_kbji` dan `kode` sebagai kunci, setelah memastikan `validasi/duplikat.csv` kosong. Pada hasil ini berkas tersebut kosong.
- `kbji_2026_jabatan.csv` hanya memuat tingkat enam digit. Entri induk tingkat 1–4 digit ada di CSV hierarki lengkap, sehingga CSV jabatan saja bukan hierarki mandiri. Namun setiap barisnya sudah membawa kode dan nama seluruh leluhurnya, sehingga cukup untuk menampilkan konteks tanpa join.
- Jangan menganggap semua kode yang disebut di dalam `uraian_resmi` sebagai kode anak. Uraian juga merujuk kode lain untuk pengecualian dan pembanding. Relasi induk–anak yang sah hanya `kode_induk`.
- Simpan sinonim, istilah bahasa Inggris, hasil pencocokan, skor, dan koreksi pengguna pada tabel terpisah yang merujuk `kode`. Jangan menambah kolom ke berkas resmi.
- Kolom resmi adalah transkripsi mesin dari sumber, bukan data yang telah disahkan penyusun publikasi.
