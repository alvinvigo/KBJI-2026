/**
 * Worker KBJI 2026: menyajikan situs referensi dan API JSON baca-saja.
 *
 * Data berasal dari berkas statis pada ./public/data yang dihasilkan oleh
 * `python web/bangun_data.py`. Tidak ada basis data dan tidak ada tulis-menulis.
 * Worker ini tidak pernah mengubah isi data; ia hanya menyusun ulang tampilannya.
 */

const VERSI_API = "v1";
const CACHE_API = "public, max-age=3600, stale-while-revalidate=86400";

const TINGKAT = {
  1: "Golongan pokok",
  2: "Subgolongan pokok",
  3: "Golongan",
  4: "Subgolongan",
  6: "Jabatan",
};

/** Cache per-isolate; berkas statis bersifat tetap sampai penyebaran berikutnya. */
let indeksCache = null;
let metaCache = null;
const blokCache = new Map();

function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "GET, HEAD, OPTIONS",
      "cache-control": CACHE_API,
      ...extraHeaders,
    },
  });
}

function galat(status, pesan, tambahan = {}) {
  return json({ galat: pesan, status, ...tambahan }, status, { "cache-control": "no-store" });
}

async function ambilAset(env, request, path) {
  const url = new URL(path, request.url);
  const res = await env.ASSETS.fetch(new Request(url.toString(), { method: "GET" }));
  return res.ok ? res : null;
}

async function muatIndeks(env, request) {
  if (indeksCache) return indeksCache;
  const res = await ambilAset(env, request, "/data/indeks.json");
  if (!res) throw new Error("Berkas indeks tidak tersedia.");
  const mentah = await res.json();
  const entri = mentah.entri.map(([kode, nama, digit, halaman, sisa]) => ({
    kode,
    nama_resmi: nama,
    jumlah_digit: digit,
    tingkat: TINGKAT[digit],
    kode_induk: induk(kode),
    halaman_cetak_mulai: halaman,
    kelompok_sisa: sisa === 1 ? "ya" : "tidak",
    cari: normalisasi(nama),
  }));
  const peta = new Map(entri.map((e) => [e.kode, e]));
  const anak = new Map();
  for (const e of entri) {
    if (!e.kode_induk) continue;
    if (!anak.has(e.kode_induk)) anak.set(e.kode_induk, []);
    anak.get(e.kode_induk).push(e);
  }
  indeksCache = { entri, peta, anak };
  return indeksCache;
}

async function muatMeta(env, request) {
  if (metaCache) return metaCache;
  const res = await ambilAset(env, request, "/data/meta.json");
  if (!res) throw new Error("Berkas metadata tidak tersedia.");
  metaCache = await res.json();
  return metaCache;
}

async function muatBlok(env, request, nama) {
  if (blokCache.has(nama)) return blokCache.get(nama);
  const res = await ambilAset(env, request, `/data/blok/${nama}.json`);
  if (!res) return null;
  const isi = await res.json();
  blokCache.set(nama, isi);
  return isi;
}

/** Induk struktural: 0111.01 -> 0111 -> 011 -> 01 -> 0 -> "" */
function induk(kode) {
  return kode.includes(".") ? kode.split(".")[0] : kode.slice(0, -1);
}

function leluhur(kode) {
  const rantai = [];
  let kini = induk(kode);
  while (kini) {
    rantai.push(kini);
    kini = induk(kini);
  }
  return rantai.reverse();
}

function namaBlok(kode) {
  const inti = kode.replace(".", "");
  return inti.length <= 3 ? "gp" + inti[0] : inti.slice(0, 4);
}

/** Sama dengan kolom turunan `nama_pencarian` pada CSV. */
function normalisasi(teks) {
  return teks
    .toLowerCase()
    .replace(/[^0-9a-z]+/g, " ")
    .trim()
    .replace(/\s+/g, " ");
}

function kodeValid(kode) {
  return /^(?:\d{1,4}|\d{4}\.\d{2})$/.test(kode);
}

async function cariEntri(env, request, url) {
  const q = (url.searchParams.get("q") || "").trim();
  const tingkat = url.searchParams.get("tingkat");
  const limit = Math.min(Math.max(parseInt(url.searchParams.get("limit") || "25", 10) || 25, 1), 200);
  const offset = Math.max(parseInt(url.searchParams.get("offset") || "0", 10) || 0, 0);
  if (!q) return galat(400, "Parameter q wajib diisi.");

  const { entri } = await muatIndeks(env, request);
  const kunci = normalisasi(q);
  const potongan = kunci.split(" ").filter(Boolean);
  const kodeQ = q.replace(/\s+/g, "");
  const saring = tingkat ? entri.filter((e) => String(e.jumlah_digit) === String(tingkat)) : entri;

  const hasil = [];
  for (const e of saring) {
    let skor = 0;
    if (e.kode === kodeQ) skor = 100;
    else if (kodeValid(kodeQ) && e.kode.startsWith(kodeQ)) skor = 90;
    else if (e.cari === kunci) skor = 80;
    else if (e.cari.startsWith(kunci)) skor = 70;
    else if (e.cari.includes(kunci)) skor = 60;
    else if (potongan.length > 1 && potongan.every((t) => e.cari.includes(t))) skor = 40;
    if (skor) hasil.push({ skor, entri: e });
  }
  hasil.sort((a, b) => b.skor - a.skor || a.entri.kode.localeCompare(b.entri.kode));

  return json({
    kueri: q,
    tingkat: tingkat || null,
    jumlah_cocok: hasil.length,
    limit,
    offset,
    catatan:
      "Pencocokan teks sederhana atas nama resmi. Hasil ini alat bantu penelusuran, bukan penetapan kode. " +
      "Periksa uraian_resmi sebelum memakai sebuah kode.",
    hasil: hasil.slice(offset, offset + limit).map(({ skor, entri: e }) => ({
      kode: e.kode,
      nama_resmi: e.nama_resmi,
      jumlah_digit: e.jumlah_digit,
      tingkat: e.tingkat,
      kode_induk: e.kode_induk,
      halaman_cetak_mulai: e.halaman_cetak_mulai,
      kelompok_sisa: e.kelompok_sisa,
      skor_kecocokan: skor,
    })),
  });
}

async function ambilKode(env, request, kode) {
  if (!kodeValid(kode)) {
    return galat(400, "Format kode tidak sah. Gunakan 1-4 digit atau pola dddd.dd, contoh 2521.01.");
  }
  const blok = await muatBlok(env, request, namaBlok(kode));
  const entri = blok && blok.find((r) => r.kode === kode);
  if (!entri) return galat(404, `Kode ${kode} tidak terdapat pada KBJI 2026.`);

  const { peta, anak } = await muatIndeks(env, request);
  return json({
    entri,
    leluhur: leluhur(kode).map((k) => ringkas(peta.get(k))).filter(Boolean),
    anak_langsung: (anak.get(kode) || []).map(ringkas),
  });
}

function ringkas(e) {
  if (!e) return null;
  return {
    kode: e.kode,
    nama_resmi: e.nama_resmi,
    jumlah_digit: e.jumlah_digit,
    tingkat: e.tingkat,
    halaman_cetak_mulai: e.halaman_cetak_mulai,
    kelompok_sisa: e.kelompok_sisa,
  };
}

async function ambilAnak(env, request, kode) {
  if (kode && !kodeValid(kode)) return galat(400, "Format kode tidak sah.");
  const { peta, anak } = await muatIndeks(env, request);
  if (kode && !peta.has(kode)) return galat(404, `Kode ${kode} tidak terdapat pada KBJI 2026.`);
  const daftar = kode
    ? anak.get(kode) || []
    : (await muatIndeks(env, request)).entri.filter((e) => e.jumlah_digit === 1);
  return json({ kode_induk: kode || null, jumlah: daftar.length, anak: daftar.map(ringkas) });
}

function dokumentasi(url) {
  const basis = `${url.origin}/api/${VERSI_API}`;
  return json({
    nama: "API KBJI 2026",
    versi: VERSI_API,
    sifat: "baca-saja, tanpa autentikasi",
    sumber_data:
      "Klasifikasi Baku Jabatan Indonesia (KBJI) 2026, Volume 1 - Kementerian Ketenagakerjaan dan " +
      "Badan Pusat Statistik. Katalog 1302037, nomor publikasi 03100.26011.",
    sifat_repositori:
      "Proyek sumber terbuka. Bukan penerbitan resmi KBJI 2026 dan tidak mewakili lembaga mana pun; " +
      "penerbitan resminya adalah publikasi Badan Pusat Statistik.",
    kode_sumber: "https://github.com/alvinvigo/KBJI-2026",
    ketentuan:
      "Isi KBJI 2026 adalah hak cipta Badan Pusat Statistik. Dilarang mereproduksi dan/atau " +
      "menggandakan sebagian atau seluruh isi untuk tujuan komersial tanpa izin tertulis BPS.",
    titik_akhir: {
      [`${basis}/meta`]: "Metadata sumber, status validasi, dan jumlah per tingkat.",
      [`${basis}/kode/{kode}`]: "Satu entri lengkap beserta leluhur dan anak langsungnya. Contoh: /kode/2521.01",
      [`${basis}/anak/{kode}`]: "Anak langsung sebuah kode. Tanpa {kode} mengembalikan 10 golongan pokok.",
      [`${basis}/cari?q=`]: "Pencarian nama atau kode. Parameter: q, tingkat (1|2|3|4|6), limit (1-200), offset.",
      [`${basis}/tingkat/{digit}`]: "Seluruh entri pada satu tingkat, bentuk ringkas. digit: 1, 2, 3, 4, atau 6.",
    },
    catatan_penting:
      "Publikasi menyebut 449 subgolongan pada Tabel 3, sedangkan Daftar Isi dan bagian uraian " +
      "sama-sama memuat 447. Selisih ini berasal dari dokumen sumber dan tidak ditutup dengan " +
      "menambahkan kode. Lihat /api/" + VERSI_API + "/meta.",
  });
}

async function rute(request, env, url) {
  const bagian = url.pathname.split("/").filter(Boolean); // ["api", "v1", ...]
  if (bagian[1] !== VERSI_API) {
    return galat(404, `Versi API tidak dikenal. Gunakan /api/${VERSI_API}.`);
  }
  const sumber = bagian[2];
  const argumen = bagian.slice(3).map(decodeURIComponent).join("/");

  if (!sumber) return dokumentasi(url);
  if (sumber === "meta") return json(await muatMeta(env, request));
  if (sumber === "kode") {
    if (!argumen) return galat(400, "Sertakan kode, contoh /api/v1/kode/2521.01");
    return ambilKode(env, request, argumen);
  }
  if (sumber === "anak") return ambilAnak(env, request, argumen);
  if (sumber === "cari") return cariEntri(env, request, url);
  if (sumber === "tingkat") {
    if (!["1", "2", "3", "4", "6"].includes(argumen)) {
      return galat(400, "Tingkat harus 1, 2, 3, 4, atau 6.");
    }
    const { entri } = await muatIndeks(env, request);
    const daftar = entri.filter((e) => String(e.jumlah_digit) === argumen);
    return json({ jumlah_digit: Number(argumen), tingkat: TINGKAT[argumen], jumlah: daftar.length, entri: daftar.map(ringkas) });
  }
  return galat(404, `Titik akhir tidak dikenal: /${bagian.join("/")}`);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-methods": "GET, HEAD, OPTIONS",
          "access-control-max-age": "86400",
        },
      });
    }
    if (request.method !== "GET" && request.method !== "HEAD") {
      return galat(405, "Hanya GET dan HEAD yang didukung. API ini baca-saja.");
    }

    if (url.pathname === "/api" || url.pathname.startsWith("/api/")) {
      try {
        return await rute(request, env, url);
      } catch (kesalahan) {
        return galat(500, "Kesalahan internal saat membaca data.", { pesan: String(kesalahan && kesalahan.message) });
      }
    }

    if (url.pathname === "/sitemap.xml") {
      try {
        const { entri } = await muatIndeks(env, request);
        const baris = entri
          .map((e) => `  <url><loc>${url.origin}/kode/${encodeURIComponent(e.kode)}</loc></url>`)
          .join("\n");
        return new Response(
          '<?xml version="1.0" encoding="UTF-8"?>\n' +
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
            `  <url><loc>${url.origin}/</loc></url>\n${baris}\n</urlset>\n`,
          { headers: { "content-type": "application/xml; charset=utf-8", "cache-control": CACHE_API } }
        );
      } catch (kesalahan) {
        return galat(500, "Peta situs tidak dapat dibuat.");
      }
    }

    // Berkas statis; jalur yang tidak cocok dikembalikan ke halaman utama agar
    // tautan dalam seperti /kode/2521.01 dapat dibuka langsung.
    const aset = await env.ASSETS.fetch(request);
    if (aset.status !== 404) return aset;
    const beranda = await ambilAset(env, request, "/index.html");
    return beranda
      ? new Response(beranda.body, { status: 200, headers: beranda.headers })
      : galat(404, "Halaman tidak ditemukan.");
  },
};
