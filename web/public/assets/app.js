/* KBJI 2026 — penelusuran sisi peramban. Tanpa kerangka kerja dan tanpa langkah bangun.
   Data dimuat dari /data/indeks.json dan /data/blok/*.json yang dihasilkan oleh web/bangun_data.py. */

(() => {
  "use strict";

  const TINGKAT = {
    1: "Golongan pokok",
    2: "Subgolongan pokok",
    3: "Golongan",
    4: "Subgolongan",
    6: "Jabatan",
  };

  const el = (id) => document.getElementById(id);
  const daftarEl = el("daftar");
  const rinciEl = el("rinci");
  const jumlahEl = el("jumlah-daftar");
  const judulDaftarEl = el("judul-daftar");
  const kotakCari = el("kotak-cari");

  const state = {
    entri: [],
    peta: new Map(),
    anak: new Map(),
    meta: null,
    terbuka: new Set(),
    terpilih: null,
    kueri: "",
    tingkat: "",
  };
  const blokCache = new Map();

  // ---------------------------------------------------------------- utilitas

  const induk = (kode) => (kode.includes(".") ? kode.split(".")[0] : kode.slice(0, -1));

  function leluhur(kode) {
    const rantai = [];
    let kini = induk(kode);
    while (kini) {
      rantai.push(kini);
      kini = induk(kini);
    }
    return rantai.reverse();
  }

  const namaBlok = (kode) => {
    const inti = kode.replace(".", "");
    return inti.length <= 3 ? "gp" + inti[0] : inti.slice(0, 4);
  };

  const normalisasi = (teks) =>
    teks.toLowerCase().replace(/[^0-9a-z]+/g, " ").trim().replace(/\s+/g, " ");

  const angka = (n) => Number(n).toLocaleString("id-ID");

  function amanHTML(teks) {
    const d = document.createElement("div");
    d.textContent = teks;
    return d.innerHTML;
  }

  function sorot(teks, kunci) {
    if (!kunci) return amanHTML(teks);
    const target = normalisasi(teks);
    const mulai = target.indexOf(kunci);
    if (mulai < 0) return amanHTML(teks);
    // Peta posisi teks ternormalisasi kembali ke teks asli.
    let n = 0, awal = -1, akhir = teks.length;
    for (let i = 0; i < teks.length; i += 1) {
      const c = teks[i].toLowerCase();
      const bersih = /[0-9a-z]/.test(c);
      if (!bersih && n > 0 && target[n - 1] !== " ") n += 1;
      if (bersih) {
        if (n === mulai && awal < 0) awal = i;
        n += 1;
        if (n === mulai + kunci.length) { akhir = i + 1; break; }
      }
    }
    if (awal < 0) return amanHTML(teks);
    return (
      amanHTML(teks.slice(0, awal)) +
      "<mark>" + amanHTML(teks.slice(awal, akhir)) + "</mark>" +
      amanHTML(teks.slice(akhir))
    );
  }

  // ---------------------------------------------------------------- muat data

  async function muatBlok(kode) {
    const nama = namaBlok(kode);
    if (!blokCache.has(nama)) {
      let res;
      try {
        res = await fetch(`/data/blok/${nama}.json`);
      } catch (_) {
        throw new Error("Koneksi terputus saat memuat rincian. Periksa jaringan, lalu coba lagi.");
      }
      if (!res.ok) {
        throw new Error(
          `Rincian untuk blok ${nama} tidak dapat dimuat (HTTP ${res.status}). ` +
          "Bila situs baru saja diperbarui, muat ulang halaman dengan Ctrl+F5."
        );
      }
      try {
        blokCache.set(nama, await res.json());
      } catch (_) {
        throw new Error(`Berkas blok ${nama} tidak berbentuk JSON yang sah. Muat ulang dengan Ctrl+F5.`);
      }
    }
    return blokCache.get(nama).find((r) => r.kode === kode) || null;
  }

  async function mulai() {
    daftarEl.innerHTML = '<p class="kosong">Memuat data…</p>';
    try {
      const [indeks, meta] = await Promise.all([
        fetch("/data/indeks.json").then((r) => r.json()),
        fetch("/data/meta.json").then((r) => r.json()),
      ]);
      state.meta = meta;
      state.entri = indeks.entri.map(([kode, nama, digit, halaman, sisa]) => ({
        kode,
        nama,
        digit,
        halaman,
        sisa: sisa === 1,
        induk: induk(kode),
        cari: normalisasi(nama),
      }));
      for (const e of state.entri) {
        state.peta.set(e.kode, e);
        if (!e.induk) continue;
        if (!state.anak.has(e.induk)) state.anak.set(e.induk, []);
        state.anak.get(e.induk).push(e);
      }
      gambarTentang();
      terapkanRute();
    } catch (kesalahan) {
      daftarEl.innerHTML =
        '<p class="kosong">Data gagal dimuat. Muat ulang dengan Ctrl+F5, atau periksa koneksi.<br><small>' +
        amanHTML(String(kesalahan.message || kesalahan)) + "</small></p>";
    }
  }

  // ---------------------------------------------------------------- daftar

  function barisHTML(e, kunci, bertingkat) {
    const punyaAnak = state.anak.has(e.kode);
    const terbuka = state.terbuka.has(e.kode);
    const tanda = bertingkat && punyaAnak ? (terbuka ? "▾" : "▸") : "";
    const inden = bertingkat ? (e.digit === 6 ? 4 : e.digit - 1) : 0;
    const jalur = bertingkat ? "" :
      `<div class="baris-bawah">${amanHTML(TINGKAT[e.digit])} · halaman cetak ${e.halaman}</div>`;
    return (
      `<button class="baris${state.terpilih === e.kode ? " terpilih" : ""}" role="treeitem"` +
      ` data-kode="${amanHTML(e.kode)}" data-digit="${e.digit}" data-inden="${inden}"` +
      (punyaAnak && bertingkat ? ` aria-expanded="${terbuka}"` : "") + ">" +
      '<span class="baris-atas">' +
      (bertingkat ? `<span class="buka" aria-hidden="true">${tanda}</span>` : "") +
      `<span class="kode">${amanHTML(e.kode)}</span>` +
      `<span class="baris-nama">${sorot(e.nama, kunci)}</span>` +
      (e.sisa ? '<span class="lencana lencana-sisa">sisa</span>' : "") +
      "</span>" + jalur + "</button>"
    );
  }

  function gambarDaftar() {
    if (state.kueri) return gambarHasilCari();

    judulDaftarEl.textContent = "Telusuri hierarki";
    const tampil = [];
    const tambah = (e) => {
      tampil.push(e);
      if (!state.terbuka.has(e.kode)) return;
      for (const anak of state.anak.get(e.kode) || []) tambah(anak);
    };
    for (const e of state.entri.filter((x) => x.digit === 1)) tambah(e);

    jumlahEl.textContent = `${angka(state.entri.length)} entri`;
    daftarEl.innerHTML = tampil.map((e) => barisHTML(e, "", true)).join("");
  }

  function cocokkan(e, kunci, potongan, kodeQ) {
    if (e.kode === kodeQ) return 100;
    if (/^\d/.test(kodeQ) && e.kode.startsWith(kodeQ)) return 90;
    if (e.cari === kunci) return 80;
    if (e.cari.startsWith(kunci)) return 70;
    if (e.cari.includes(kunci)) return 60;
    if (potongan.length > 1 && potongan.every((t) => e.cari.includes(t))) return 40;
    return 0;
  }

  function gambarHasilCari() {
    const kunci = normalisasi(state.kueri);
    const potongan = kunci.split(" ").filter(Boolean);
    const kodeQ = state.kueri.replace(/\s+/g, "");
    const sumber = state.tingkat
      ? state.entri.filter((e) => String(e.digit) === state.tingkat)
      : state.entri;

    const hasil = [];
    for (const e of sumber) {
      const skor = cocokkan(e, kunci, potongan, kodeQ);
      if (skor) hasil.push({ skor, e });
    }
    hasil.sort((a, b) => b.skor - a.skor || a.e.kode.localeCompare(b.e.kode));

    judulDaftarEl.textContent = "Hasil pencarian";
    jumlahEl.textContent = `${angka(hasil.length)} cocok`;
    daftarEl.innerHTML = hasil.length
      ? hasil.slice(0, 300).map(({ e }) => barisHTML(e, kunci, false)).join("") +
        (hasil.length > 300
          ? `<p class="kosong">Menampilkan 300 teratas dari ${angka(hasil.length)}. Persempit kata kuncinya.</p>`
          : "")
      : '<p class="kosong">Tidak ada entri yang cocok.<br><small>Coba kata kunci lain, atau cari dengan kodenya.</small></p>';
  }

  // ---------------------------------------------------------------- rincian

  function sambutan() {
    const jumlah = (state.meta && state.meta.jumlah_per_tingkat) || [];
    const kartu = jumlah
      .map((c) => `<div class="kartu"><div class="kartu-angka">${angka(c.hasil_ekstraksi)}</div>` +
                  `<div class="kartu-label">${amanHTML(c.tingkat)}</div></div>`)
      .join("");
    rinciEl.innerHTML =
      '<div class="rinci-isi">' +
      '<h2 class="sambut-judul">Pilih sebuah kode</h2>' +
      '<p class="sambut-teks">' +
      "Telusuri hierarki di sebelah kiri, atau cari nama jabatan dan kode pada kotak pencarian. " +
      "Setiap entri menampilkan uraian resmi lengkap beserta rujukan halaman publikasi.</p>" +
      `<div class="kartu-baris">${kartu}</div>` +
      "</div>";
  }

  async function pilih(kode, dorongRiwayat = true) {
    state.terpilih = kode;
    for (const k of leluhur(kode)) state.terbuka.add(k);
    gambarDaftar();
    const aktif = daftarEl.querySelector(".baris.terpilih");
    if (aktif) aktif.scrollIntoView({ block: "nearest" });

    if (dorongRiwayat) {
      const jalur = `/kode/${kode}`;
      if (location.pathname !== jalur) history.pushState({ kode }, "", jalur);
    }

    rinciEl.innerHTML = '<div class="rinci-isi"><p class="kosong">Memuat…</p></div>';
    let entri;
    try {
      entri = await muatBlok(kode);
    } catch (kesalahan) {
      rinciEl.innerHTML = `<div class="rinci-isi"><p class="kosong">${amanHTML(String(kesalahan.message))}</p></div>`;
      return;
    }
    if (!entri) {
      rinciEl.innerHTML = `<div class="rinci-isi"><p class="kosong">Kode ${amanHTML(kode)} tidak ada pada KBJI 2026.</p></div>`;
      return;
    }
    gambarRinci(entri);
    document.title = `${entri.kode} ${entri.nama_resmi} — KBJI 2026`;
  }

  function gambarRinci(e) {
    const remah = leluhur(e.kode)
      .map((k) => {
        const n = state.peta.get(k);
        return n ? `<a href="/kode/${k}" data-kode="${k}"><span class="mono">${k}</span> ${amanHTML(n.nama)}</a>` : "";
      })
      .filter(Boolean)
      .join('<span class="pemisah" aria-hidden="true">›</span>');

    const anak = state.anak.get(e.kode) || [];
    const daftarAnak = anak.length
      ? '<div class="rinci-bagian"><h3>' +
        `${anak.length === 1 ? "1 entri" : angka(anak.length) + " entri"} di bawahnya</h3>` +
        '<div class="anak-daftar">' +
        anak
          .map(
            (a) =>
              `<button class="anak-butir" data-kode="${amanHTML(a.kode)}">` +
              `<span class="kode">${amanHTML(a.kode)}</span>` +
              `<span>${amanHTML(a.nama)}</span>` +
              (a.sisa ? '<span class="lencana lencana-sisa">sisa</span>' : "") +
              "</button>"
          )
          .join("") +
        "</div></div>"
      : "";

    const lencana = [
      `<span class="lencana">${amanHTML(e.tingkat)}</span>`,
      `<span class="lencana">Halaman cetak ${e.halaman_cetak_mulai}${
        e.halaman_cetak_selesai !== e.halaman_cetak_mulai ? "–" + e.halaman_cetak_selesai : ""
      }</span>`,
      `<span class="lencana">Halaman PDF ${e.halaman_pdf_mulai}${
        e.halaman_pdf_selesai !== e.halaman_pdf_mulai ? "–" + e.halaman_pdf_selesai : ""
      }</span>`,
      e.jumlah_jabatan_turunan
        ? `<span class="lencana">${angka(e.jumlah_jabatan_turunan)} jabatan turunan</span>`
        : "",
      e.kelompok_sisa === "ya" ? '<span class="lencana lencana-sisa">kelompok sisa</span>' : "",
    ]
      .filter(Boolean)
      .join("");

    rinciEl.innerHTML =
      '<div class="rinci-isi">' +
      (remah ? `<nav class="remah" aria-label="Jalur hierarki">${remah}</nav>` : "") +
      '<div class="rinci-judul">' +
      `<span class="kode kode-besar">${amanHTML(e.kode)}</span>` +
      `<h2>${amanHTML(e.nama_resmi)}</h2>` +
      "</div>" +
      `<div class="lencana-baris">${lencana}</div>` +
      `<div class="uraian">${amanHTML(e.uraian_resmi)}</div>` +
      daftarAnak +
      '<div class="aksi-baris">' +
      `<button class="tombol" type="button" data-salin="${amanHTML(e.kode)}">Salin kode</button>` +
      `<a class="tombol" href="/api/v1/kode/${encodeURIComponent(e.kode)}">Lihat JSON</a>` +
      "</div></div>";
  }

  // ---------------------------------------------------------------- tentang

  function gambarTentang() {
    const m = state.meta;
    if (!m) return;
    const selisih = new Map(
      (m.selisih_sumber_terverifikasi || [])
        .filter((s) => !s.golongan_pokok)
        .map((s) => [String(s.tingkat_digit), s])
    );
    el("ringkas-jumlah").innerHTML = (m.jumlah_per_tingkat || [])
      .map((c) => {
        const beda = selisih.get(String(c.jumlah_digit));
        return (
          '<div class="kartu">' +
          `<div class="kartu-angka">${angka(c.hasil_ekstraksi)}</div>` +
          `<div class="kartu-label">${amanHTML(c.tingkat)}</div>` +
          (beda ? `<div class="kartu-acuan">Tabel 3 menyebut ${angka(beda.acuan_publikasi)}</div>` : "") +
          "</div>"
        );
      })
      .join("");

    const baris = [
      ["Publikasi", m.publikasi],
      ["Penerbit", m.penerbit],
      ["Katalog", `${m.katalog} · nomor publikasi ${m.nomor_publikasi}`],
      ["SHA-256 berkas sumber", m.sumber_sha256],
      ["Jumlah halaman PDF", angka(m.halaman_pdf)],
      ["Status transkripsi", m.status_ekstraksi],
      ["Status dokumen sumber", m.status_sumber],
      ["Alat", `kbji.py ${m.versi_alat} · PyMuPDF ${m.versi_pymupdf}`],
      ["Waktu proses (UTC)", m.diproses_utc],
    ];
    el("meta-daftar").innerHTML = baris
      .map(([k, v]) => `<dt>${amanHTML(k)}</dt><dd class="${k.startsWith("SHA") ? "mono" : ""}">${amanHTML(String(v))}</dd>`)
      .join("");
    el("kaki-meta").textContent =
      `Transkripsi ${m.versi_alat} atas berkas ber-SHA-256 ${m.sumber_sha256.slice(0, 12)}… · ` +
      `${angka(m.total_entri)} entri · diproses ${m.diproses_utc.slice(0, 10)}.`;
  }

  // ---------------------------------------------------------------- rute & peristiwa

  function terapkanRute() {
    const cocok = location.pathname.match(/^\/kode\/(.+)$/);
    if (cocok) {
      const kode = decodeURIComponent(cocok[1]);
      if (state.peta.has(kode)) {
        pilih(kode, false);
        return;
      }
    }
    state.terpilih = null;
    for (const e of state.entri.filter((x) => x.digit === 1)) state.terbuka.add(e.kode);
    gambarDaftar();
    sambutan();
    document.title = "KBJI 2026 — Klasifikasi Baku Jabatan Indonesia";
  }

  daftarEl.addEventListener("click", (ev) => {
    const baris = ev.target.closest(".baris");
    if (!baris) return;
    const kode = baris.dataset.kode;
    const tandaBuka = ev.target.closest(".buka");
    if (tandaBuka && state.anak.has(kode)) {
      if (state.terbuka.has(kode)) state.terbuka.delete(kode);
      else state.terbuka.add(kode);
      gambarDaftar();
      return;
    }
    if (!state.kueri && state.anak.has(kode)) state.terbuka.add(kode);
    pilih(kode);
  });

  rinciEl.addEventListener("click", (ev) => {
    const salin = ev.target.closest("[data-salin]");
    if (salin) {
      navigator.clipboard.writeText(salin.dataset.salin).then(
        () => {
          const semula = salin.textContent;
          salin.textContent = "Tersalin";
          setTimeout(() => { salin.textContent = semula; }, 1400);
        },
        () => {}
      );
      return;
    }
    const tuju = ev.target.closest("[data-kode]");
    if (tuju) {
      ev.preventDefault();
      pilih(tuju.dataset.kode);
    }
  });

  let tunda;
  kotakCari.addEventListener("input", () => {
    clearTimeout(tunda);
    tunda = setTimeout(() => {
      state.kueri = kotakCari.value.trim();
      gambarDaftar();
    }, 120);
  });

  el("borang-cari").addEventListener("submit", (ev) => {
    ev.preventDefault();
    const pertama = daftarEl.querySelector(".baris");
    if (pertama) pilih(pertama.dataset.kode);
  });

  document.querySelectorAll(".cip").forEach((cip) => {
    cip.addEventListener("click", () => {
      document.querySelectorAll(".cip").forEach((c) => c.classList.remove("aktif"));
      cip.classList.add("aktif");
      state.tingkat = cip.dataset.tingkat;
      if (!state.kueri && state.tingkat) {
        kotakCari.focus();
      }
      gambarDaftar();
    });
  });

  window.addEventListener("popstate", terapkanRute);

  document.addEventListener("keydown", (ev) => {
    if (ev.key === "/" && document.activeElement !== kotakCari) {
      ev.preventDefault();
      kotakCari.focus();
      kotakCari.select();
    }
    if (ev.key === "Escape" && document.activeElement === kotakCari) {
      kotakCari.value = "";
      state.kueri = "";
      gambarDaftar();
      kotakCari.blur();
    }
  });

  // Tema: ikuti sistem, dapat ditimpa dan diingat per peramban.
  const tombolTema = el("tombol-tema");
  try {
    const simpan = localStorage.getItem("kbji-tema");
    if (simpan) document.documentElement.dataset.tema = simpan;
  } catch (_) { /* penyimpanan lokal dapat diblokir; abaikan */ }
  tombolTema.addEventListener("click", () => {
    const gelapSekarang =
      document.documentElement.dataset.tema === "gelap" ||
      (!document.documentElement.dataset.tema &&
        window.matchMedia("(prefers-color-scheme: dark)").matches);
    const baru = gelapSekarang ? "terang" : "gelap";
    document.documentElement.dataset.tema = baru;
    try { localStorage.setItem("kbji-tema", baru); } catch (_) { /* abaikan */ }
  });

  mulai();
})();
