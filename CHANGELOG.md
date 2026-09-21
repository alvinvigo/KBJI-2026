# Riwayat perubahan

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/1.1.0/).

## [2.1.0] — 2026-09-21

### Ditambahkan
- **Dua bahasa, Indonesia dan Inggris.** Hanya teks antarmuka yang berpindah bahasa; kode, nama
  resmi, dan uraian tetap dalam bahasa Indonesia sesuai publikasi. Nama tingkat dalam bahasa
  Inggris memakai padanan ISCO-08 (major/sub-major/minor/unit group), bukan terjemahan resmi KBJI.
- **Panel Preferensi & Aksesibilitas**: bahasa, tema (sistem/terang/gelap), ukuran teks tiga
  tingkat, kontras tinggi, spasi baca lega untuk pembaca disleksia, garis bawah tautan, dan
  kurangi animasi. Tersimpan di peramban, dengan jebakan fokus dan tutup lewat Esc.
- **Rel posisi hierarki** pada panel rincian: kelima tingkat selalu terlihat. Leluhur dapat diklik,
  posisi kini ditandai, dan tingkat di bawahnya menampilkan jumlah turunan.
- **Bagian "Rincian di bawahnya"**: ringkasan jumlah per tingkat dan daftar entri langsung beserta
  jumlah anaknya masing-masing.

### Diubah
- Palet dan tipografi disesuaikan bernuansa Karirhub — Kementerian Ketenagakerjaan.
- Seluruh ukuran memakai satuan `rem` agar preferensi ukuran teks pengguna bekerja.
- Berkas data dan aset yang hilang membalas 404 apa adanya, tidak lagi dikembalikan ke halaman utama.
- Dokumentasi dirampingkan dari 11.376 menjadi 7.485 kata; draf surat internal dikeluarkan dari repositori.

## [2.0.0] — 2026-09-21

### Ditambahkan
- Rekonsiliasi Daftar Isi yang membandingkan kode, nama, **dan** nomor halaman cetak untuk
  630 entri tingkat 1–4 digit.
- Pemindaian kolom kode secara independen sebagai bukti kelengkapan: 3.010 kode, identik dengan
  hasil parsing.
- Rekonsiliasi rujukan induk–anak: 173 entri induk, 584 rujukan kode anak, nol yang tidak diuraikan.
- Pemeriksaan konvensi penomoran dan konsistensi kolom turunan.
- Deteksi otomatis halaman tanpa teks isi, dicocokkan dengan daftar pada profil.
- 16 kolom turunan pada CSV: kode dan nama seluruh leluhur, `jalur_kode`, `jalur_nama`, `kedalaman`,
  `urutan`, `jumlah_anak_langsung`, `jumlah_jabatan_turunan`, `kelompok_sisa`, `nama_pencarian`.
- Berkas keluaran baru: `kbji_2026_ringkas.csv`, `kbji_2026_pohon.json`, serta folder `referensi/`
  berisi `daftar_isi.csv`, `tingkat_keterampilan.csv`, dan `jumlah_acuan_publikasi.csv`.
- Situs referensi dan API JSON untuk Cloudflare Workers pada folder `web/`.
- Berkas tata kelola: `LICENSE`, `KETENTUAN_DATA.md`, `CITATION.cff`, `CONTRIBUTING.md`,
  `SECURITY.md`, dan alur kerja CI.

### Diubah
- Folder keluaran `hasil/` menjadi `output/`.
- Temuan validasi dipisah menjadi kelas `ekstraksi` dan `sumber`, dengan `status_ekstraksi` dan
  `status_sumber` terpisah. Kode keluar `3` ditambahkan untuk "ekstraksi lengkap, sumber tidak konsisten".
- Rentang Daftar Isi pada profil diperbaiki dari halaman PDF 9–27 menjadi 11–26. Rentang lama ikut
  mencakup Kata Pengantar dan Daftar Tabel.
- Acuan jumlah pada profil kini menyertakan rujukan tabel dan halaman sumbernya.
- Pengujian regresi diperluas dari 12 menjadi 26.
- `README.md` tidak lagi duplikat dari `Panduan_KBJI_2026.md`.

### Catatan
- Isi kolom resmi (`kode`, `nama_resmi`, `uraian_resmi`, dan seluruh nomor halaman) **identik**
  dengan hasil versi sebelumnya. Diverifikasi bidang demi bidang untuk seluruh 3.010 entri.
- Selisih 447 berbanding 449 subgolongan tetap dilaporkan apa adanya sebagai ketidaksesuaian pada
  dokumen sumber. Tidak ada kode yang ditambahkan.

## [1.0.0] — 2026-09-21

- Rilis awal: ekstraksi berbasis tata letak, validasi struktur, dan 12 pengujian regresi.
