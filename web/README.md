# Situs referensi dan API KBJI 2026 — Cloudflare Workers

Worker baca-saja yang menyajikan dua hal dari berkas statis: antarmuka penelusuran dan API JSON terbuka.
Tanpa basis data, tanpa kerangka kerja, tanpa langkah bangun. Muat di paket gratis Cloudflare.

```
web/
├─ wrangler.jsonc        konfigurasi Worker dan Static Assets
├─ package.json          hanya wrangler sebagai devDependency
├─ bangun_data.py        membangun public/data/ dari ../output
├─ src/index.js          Worker: API, peta situs, dan cadangan tautan dalam
└─ public/               berkas statis yang disajikan apa adanya
   ├─ index.html
   ├─ robots.txt
   ├─ _headers           kebijakan tembolok dan header keamanan
   ├─ assets/app.css
   ├─ assets/app.js
   └─ data/              dihasilkan: indeks.json, meta.json, blok/*.json
```

## Antarmuka

- Penelusuran hierarki lima tingkat, pencarian instan atas 3.010 entri, dan tautan dalam per kode.
- **Rel posisi**: kelima tingkat hierarki selalu terlihat pada panel rincian. Leluhur dapat diklik;
  tingkat di bawah posisi kini menampilkan jumlah turunannya.
- **Preferensi & Aksesibilitas**: bahasa Indonesia/Inggris, tema, tiga ukuran teks, kontras tinggi,
  spasi baca lega, garis bawah tautan, dan kurangi animasi. Disimpan di `localStorage`.
- Setiap baris pohon punya tombol panah tersendiri untuk membuka cabang, lengkap dengan jumlah anak
  dan navigasi papan ketik (atas/bawah/kanan/kiri).
- **Material kaca**: permukaan tembus pandang dengan buram latar. Hanya 4 permukaan yang benar-benar
  diburamkan — kepala, kotak pencarian, panel preferensi, dan tirainya — agar beban gulir tetap ringan. Dapat dimatikan dari panel
  preferensi, dan mati sendiri pada kontras tinggi, `prefers-reduced-transparency`, serta peramban
  tanpa `backdrop-filter`.
- Seluruh jarak dan ukuran huruf memakai skala token di `app.css`; sasaran sentuh minimum 2,75 rem.
- Dua bahasa hanya menyentuh teks antarmuka. Kode, nama resmi, dan uraian jabatan tetap dalam
  bahasa Indonesia karena menerjemahkannya akan mengubah isi resmi.

## Bentuk data

`bangun_data.py` memecah `output/kbji_2026_hierarki.csv` menjadi berkas kecil agar dapat disajikan
sebagai aset statis:

| Berkas | Isi | Ukuran |
|---|---|---:|
| `data/indeks.json` | Seluruh 3.010 entri dalam bentuk larik ringkas: kode, nama, jumlah digit, halaman cetak, penanda kelompok sisa. Dipakai untuk pencarian dan penelusuran di peramban. | ±152 KB |
| `data/meta.json` | Metadata sumber, status validasi, jumlah per tingkat, selisih sumber terverifikasi, dan transkripsi Tabel 1. | ±4 KB |
| `data/blok/gp{0-9}.json` | Rincian lengkap entri tingkat 1–3 per golongan pokok. | 10 berkas |
| `data/blok/{kode4}.json` | Rincian lengkap satu subgolongan beserta seluruh jabatannya. | 447 berkas |

Total 457 berkas, sekitar 5 MB. Batas Static Assets adalah 20.000 berkas dan 25 MiB per berkas,
jadi masih sangat longgar.

Peramban memuat `indeks.json` satu kali, lalu mengambil satu berkas blok saat sebuah entri dibuka.
Worker memakai jalur yang sama melalui pengikatan `ASSETS`, sehingga API dan antarmuka membaca sumber
yang persis sama.

## Titik akhir API

Seluruhnya `GET`, tanpa autentikasi, `Access-Control-Allow-Origin: *`.

| Titik akhir | Keterangan |
|---|---|
| `/api/v1` | Dokumentasi ringkas dalam JSON |
| `/api/v1/meta` | Metadata sumber, status, dan jumlah per tingkat |
| `/api/v1/kode/{kode}` | Satu entri lengkap beserta leluhur dan anak langsung. Contoh: `/api/v1/kode/2521.01` |
| `/api/v1/anak/{kode}` | Anak langsung sebuah kode. Tanpa `{kode}` mengembalikan 10 golongan pokok |
| `/api/v1/cari?q=` | Pencarian nama atau kode. Parameter: `q`, `tingkat` (1\|2\|3\|4\|6), `limit` (1–200), `offset` |
| `/api/v1/tingkat/{digit}` | Seluruh entri pada satu tingkat, bentuk ringkas |
| `/sitemap.xml` | Peta situs untuk 3.010 entri, dibuat dari indeks |

Kode status: `400` parameter tidak sah, `404` kode atau titik akhir tidak ada, `405` metode selain
GET/HEAD, `500` kegagalan membaca aset.

Pencarian memakai pencocokan teks sederhana atas nama resmi dan berskala 40–100. **Hasilnya alat bantu
penelusuran, bukan penetapan kode.** Periksa `uraian_resmi` sebelum memakai sebuah kode.

## Menjalankan secara lokal

```bash
cd web
npm install
python bangun_data.py          # membangun ulang public/data dari ../output
npm run dev                    # http://127.0.0.1:8787
```

Situs produksi: <https://kbji-2026.sipk-paskerid.workers.dev>

Untuk mencoba titik akhir, cara paling mudah adalah menempelkan alamatnya di peramban. Bila memakai
terminal Windows PowerShell, tulis `curl.exe`, bukan `curl` — `curl` di PowerShell adalah alias
`Invoke-WebRequest` dengan sintaks berbeda. Di Command Prompt, `curl` berjalan apa adanya.

`npm install` dapat memblokir skrip pemasangan `esbuild` dan `workerd` pada npm versi baru. Bila
`wrangler dev` gagal menyalakan runtime, jalankan:

```bash
npm install-scripts approve esbuild workerd && npm rebuild esbuild workerd
```

## Menyebarkan

```bash
npx wrangler login
npx wrangler deploy
```

Langkah lengkapnya, termasuk penyebaran otomatis dari GitHub dan pemasangan domain sendiri, ada pada
[Panduan_KBJI_2026.md](../Panduan_KBJI_2026.md) bagian 13.

## Bila data diperbarui

Setelah `kbji.py extract` dijalankan ulang:

```bash
python web/bangun_data.py --out output --data web/public/data
cd web && npx wrangler deploy
```

Komit ulang `web/public/data/` agar penyebaran dari GitHub tetap berjalan tanpa Python. CI akan
memeriksa bahwa isi folder itu sama dengan hasil pembangunan ulang.

## Ketentuan

Kode Worker dan antarmuka: lisensi MIT, lihat [LICENSE](../LICENSE).
Data KBJI 2026: hak cipta Badan Pusat Statistik, lihat [KETENTUAN_DATA.md](../KETENTUAN_DATA.md).
Proyek sumber terbuka. Bukan penerbitan resmi KBJI 2026 dan tidak mewakili lembaga mana pun.
