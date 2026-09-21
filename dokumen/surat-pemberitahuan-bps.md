# Draf surat pemberitahuan dan permohonan izin kepada BPS

Ganti seluruh teks dalam kurung sudut, lalu kirim sebagai surat resmi berkop instansi atau sebagai surel.
Simpan tanda terima atau balasannya, dan lampirkan ringkasannya pada repositori bila sudah ada.

**Tujuan surat:** memberitahukan keberadaan transkripsi, melaporkan ketidaksesuaian yang ditemukan pada
publikasi, dan meminta kepastian ketentuan penggunaan.

**Alamat tujuan:** Direktorat Metodologi Statistik dan Sains Data, Badan Pusat Statistik — sebagai penyusun
naskah dan penyunting publikasi (halaman PDF 4). Tembusan kepada Kementerian Ketenagakerjaan Republik
Indonesia sebagai penerbit bersama, dan kepada Ketua Tim Penyusun.

---

## Draf

Nomor: `<NOMOR SURAT>`
Lampiran: 1 (satu) berkas
Hal: **Pemberitahuan transkripsi KBJI 2026 dan permohonan konfirmasi ketentuan penggunaan**

Kepada Yth.
Direktur Metodologi Statistik dan Sains Data
Badan Pusat Statistik
Jl. Dr. Sutomo No. 6–8, Jakarta 10710

Dengan hormat,

Bersama surat ini kami menyampaikan bahwa `<NAMA/ORGANISASI>` telah melakukan transkripsi teknis atas
publikasi **Klasifikasi Baku Jabatan Indonesia (KBJI) 2026, Volume 1** (Katalog 1302037, Nomor Publikasi
03100.26011) dari bentuk PDF menjadi berkas data terstruktur (CSV dan JSON). Transkripsi ini dibuat untuk
keperluan `<SEBUTKAN KEPERLUAN, MISALNYA: standardisasi kode jabatan pada sistem informasi pasar kerja>`.

**1. Sifat pekerjaan**

Pekerjaan ini murni transkripsi. Kode, nama jabatan, dan uraian ditulis persis sebagaimana tercetak, tanpa
koreksi ejaan, tanpa penambahan, dan tanpa penghapusan. Setiap entri membawa rujukan nomor halaman cetak
dan halaman PDF sehingga dapat ditelusuri kembali ke publikasi. Hasilnya mencakup 3.010 entri.

**2. Temuan yang perlu kami laporkan**

Dalam proses verifikasi, kami menemukan ketidaksesuaian di dalam publikasi pada jumlah subgolongan
(4 digit):

| Rujukan | Jumlah subgolongan |
|---|---:|
| Narasi halaman cetak 12, Tabel 3 halaman cetak 13, dan Tabel 19 halaman cetak 54 | 449 |
| Daftar Isi (halaman romawi ix–xxiv) | **447** |
| Judul pada bagian uraian (halaman cetak 71–1076) | **447** |

Selisih terletak pada dua golongan pokok:

- **Golongan pokok 2 (Profesional):** Tabel 27 halaman cetak 62 menyebut 94 subgolongan; Daftar Isi dan
  bagian uraian sama-sama memuat 93.
- **Golongan pokok 6 (Pekerja Terampil Pertanian, Kehutanan, dan Perikanan):** Tabel 31 halaman cetak 64
  menyebut 19 subgolongan; Daftar Isi dan bagian uraian sama-sama memuat 18.

Seluruh jumlah pada tingkat lain — 10 golongan pokok, 43 subgolongan pokok, 130 golongan, dan 2.380
jabatan — telah sesuai dengan tabel ringkasan, termasuk rinciannya per golongan pokok. Untuk 630 kode
tingkat 1 sampai 4 digit, kode, nama, dan nomor halaman pada Daftar Isi dan bagian uraian cocok
seluruhnya tanpa satu pun perbedaan.

Kami **tidak menambahkan kode apa pun** untuk menutup selisih tersebut, dan tidak mengubah angka acuan
pada publikasi. Rincian metode dan buktinya kami lampirkan.

Sehubungan dengan hal tersebut, kami mohon arahan Bapak/Ibu mengenai apakah Tabel 3, Tabel 19, Tabel 27,
dan Tabel 31 perlu diralat, atau terdapat dua subgolongan yang seharusnya tercetak namun luput dari
Daftar Isi maupun bagian uraian.

**3. Permohonan konfirmasi ketentuan penggunaan**

Kami memahami halaman hak cipta publikasi menyatakan: *"Dilarang mereproduksi dan/atau menggandakan
sebagian atau seluruh isi buku ini untuk tujuan komersial tanpa izin tertulis dari Badan Pusat Statistik."*

Rencana kami adalah memublikasikan hasil transkripsi beserta alat ekstraksinya secara terbuka
`<SEBUTKAN: pada repositori GitHub dan situs referensi daring>` **untuk keperluan nonkomersial**, dengan
mencantumkan atribusi kepada Badan Pusat Statistik dan Kementerian Ketenagakerjaan Republik Indonesia,
menegaskan bahwa publikasi ini bukan rilis resmi kedua lembaga, serta menyertakan catatan ketidaksesuaian
pada angka 2 di atas.

Kami mohon:

a. konfirmasi bahwa rencana tersebut sesuai dengan ketentuan yang berlaku; atau
b. arahan penyesuaian yang diperlukan; atau
c. `<HAPUS BILA TIDAK RELEVAN>` izin tertulis apabila di kemudian hari data ini dipakai untuk keperluan
   yang bersifat komersial.

Kami siap menghentikan publikasi atau menghapus data sewaktu-waktu apabila Badan Pusat Statistik
berkeberatan.

**4. Lampiran**

1. Catatan pemeriksaan dan bukti verifikasi (`CATATAN_PEMERIKSAAN.md`).
2. Laporan validasi otomatis (`output/validasi/LAPORAN_VALIDASI.md`).
3. Ketentuan penggunaan data yang kami cantumkan (`KETENTUAN_DATA.md`).
4. `<URL REPOSITORI DAN SITUS, BILA SUDAH ADA>`

Demikian kami sampaikan. Atas perhatian dan arahan Bapak/Ibu, kami ucapkan terima kasih.

`<KOTA>`, `<TANGGAL>`

Hormat kami,

`<NAMA>`
`<JABATAN>`
`<ORGANISASI>`
`<SUREL DAN TELEPON>`

Tembusan:
1. Kementerian Ketenagakerjaan Republik Indonesia
2. Ketua Tim Penyusun KBJI 2026
3. Arsip

---

## Catatan pengiriman

- Kanal resmi BPS untuk permintaan dan konsultasi adalah layanan statistik terpadu; lampirkan surat ini
  di sana bila tidak ada kontak langsung ke direktorat penyusun.
- **Jangan melampirkan berkas PDF publikasi** pada surat atau repositori. Cukup rujuk katalog dan nomor
  publikasinya.
- Setelah ada balasan, catat hasilnya pada `KETENTUAN_DATA.md` dan `CHANGELOG.md` agar status izinnya
  terlihat oleh pengguna data.
