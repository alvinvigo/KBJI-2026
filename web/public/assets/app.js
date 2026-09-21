/* KBJI 2026 — penelusuran sisi peramban. Tanpa kerangka kerja dan tanpa langkah bangun.
   Data dimuat dari /data/indeks.json dan /data/blok/*.json yang dihasilkan oleh web/bangun_data.py.

   Kode, nama resmi, dan uraian jabatan tidak pernah diterjemahkan maupun diubah di sini;
   yang berpindah bahasa hanya teks antarmuka. */

(() => {
  "use strict";

  const DIGIT = [1, 2, 3, 4, 6];
  const BAWAAN = { bahasa: "id", tema: "sistem", ukuran: "normal",
                   kontras: false, spasi: false, "garis-tautan": false, gerak: false, kaca: true };
  const CONTOH = ["2511", "2320", "3112", "5120", "7112"];

  const el = (id) => document.getElementById(id);
  const daftarEl = el("daftar");
  const rinciEl = el("rinci");
  const jumlahEl = el("jumlah-daftar");
  const judulDaftarEl = el("judul-daftar");
  const kotakCari = el("kotak-cari");

  const state = {
    entri: [], peta: new Map(), anak: new Map(), meta: null,
    terbuka: new Set(), terpilih: null, kueri: "", tingkat: "",
    pref: { ...BAWAAN },
  };
  const blokCache = new Map();

  // ---------------------------------------------------------------- bahasa

  function T(kunci, ganti) {
    const kamus = window.KBJI_TEKS[state.pref.bahasa] || window.KBJI_TEKS.id;
    let teks = kamus[kunci] ?? window.KBJI_TEKS.id[kunci] ?? kunci;
    if (ganti) for (const [k, v] of Object.entries(ganti)) teks = teks.replaceAll(`{${k}}`, v);
    return teks;
  }
  const namaTingkat = (digit) => T(`tingkat.${digit}`);

  function terapkanBahasa() {
    const lang = T("html.lang");
    document.documentElement.lang = lang;
    document.title = T("app.judul");
    el("lencana-bahasa").textContent = lang.toUpperCase();
    for (const n of document.querySelectorAll("[data-i18n]")) n.textContent = T(n.dataset.i18n);
    for (const n of document.querySelectorAll("[data-i18n-attr]")) {
      for (const pasangan of n.dataset.i18nAttr.split(",")) {
        const [atribut, kunci] = pasangan.split(":");
        n.setAttribute(atribut.trim(), T(kunci.trim()));
      }
    }
  }

  // ---------------------------------------------------------------- preferensi

  function terapkanPref() {
    const d = document.documentElement.dataset;
    d.tema = state.pref.tema === "sistem" ? "" : state.pref.tema;
    if (state.pref.tema === "sistem") delete document.documentElement.dataset.tema;
    d.ukuran = state.pref.ukuran;
    d.kontras = state.pref.kontras ? "tinggi" : "normal";
    d.spasi = state.pref.spasi ? "lega" : "normal";
    d.garisTautan = state.pref["garis-tautan"] ? "selalu" : "normal";
    d.gerak = state.pref.gerak ? "minimal" : "normal";
    d.kaca = state.pref.kaca ? "hidup" : "mati";

    for (const grup of document.querySelectorAll("[data-pref]")) {
      for (const b of grup.querySelectorAll(".pilihan-butir")) {
        b.setAttribute("aria-checked", String(b.dataset.nilai === state.pref[grup.dataset.pref]));
      }
    }
    for (const kotak of document.querySelectorAll("[data-pref-saklar]")) {
      kotak.checked = Boolean(state.pref[kotak.dataset.prefSaklar]);
    }
    simpanPref();
  }

  function simpanPref() {
    try { localStorage.setItem("kbji-pref", JSON.stringify(state.pref)); } catch (_) { /* diblokir */ }
  }

  function muatPref() {
    try {
      const simpan = JSON.parse(localStorage.getItem("kbji-pref") || "{}");
      state.pref = { ...BAWAAN, ...simpan };
    } catch (_) {
      state.pref = { ...BAWAAN };
    }
    if (!window.KBJI_TEKS[state.pref.bahasa]) state.pref.bahasa = "id";
  }

  function ubahPref(kunci, nilai) {
    state.pref[kunci] = nilai;
    terapkanPref();
    if (kunci === "bahasa") {
      terapkanBahasa();
      gambarTentang();
      gambarDaftar();
      if (state.terpilih) pilih(state.terpilih, false); else sambutan();
    }
  }

  // ---------------------------------------------------------------- utilitas

  const induk = (kode) => (kode.includes(".") ? kode.split(".")[0] : kode.slice(0, -1));

  function leluhur(kode) {
    const rantai = [];
    let kini = induk(kode);
    while (kini) { rantai.push(kini); kini = induk(kini); }
    return rantai.reverse();
  }

  const namaBlok = (kode) => {
    const inti = kode.replace(".", "");
    return inti.length <= 3 ? "gp" + inti[0] : inti.slice(0, 4);
  };

  const normalisasi = (teks) =>
    teks.toLowerCase().replace(/[^0-9a-z]+/g, " ").trim().replace(/\s+/g, " ");

  const angka = (n) => Number(n).toLocaleString(state.pref.bahasa === "en" ? "en-US" : "id-ID");

  function amanHTML(teks) {
    const d = document.createElement("div");
    d.textContent = teks;
    return d.innerHTML;
  }

  /** Banyaknya keturunan sebuah kode pada satu tingkat. Kode KBJI bersifat awalan. */
  function jumlahTurunan(kode, digit) {
    let n = 0;
    for (const e of state.entri) {
      if (e.digit === digit && e.kode !== kode && e.kode.startsWith(kode)) n += 1;
    }
    return n;
  }

  function sorot(teks, kunci) {
    if (!kunci) return amanHTML(teks);
    const target = normalisasi(teks);
    const mulai = target.indexOf(kunci);
    if (mulai < 0) return amanHTML(teks);
    let n = 0, awal = -1, akhir = teks.length;
    for (let i = 0; i < teks.length; i += 1) {
      const bersih = /[0-9a-z]/.test(teks[i].toLowerCase());
      if (!bersih && n > 0 && target[n - 1] !== " ") n += 1;
      if (bersih) {
        if (n === mulai && awal < 0) awal = i;
        n += 1;
        if (n === mulai + kunci.length) { akhir = i + 1; break; }
      }
    }
    if (awal < 0) return amanHTML(teks);
    return amanHTML(teks.slice(0, awal)) + "<mark>" + amanHTML(teks.slice(awal, akhir)) +
           "</mark>" + amanHTML(teks.slice(akhir));
  }

  // ---------------------------------------------------------------- muat data

  async function muatBlok(kode) {
    const nama = namaBlok(kode);
    if (!blokCache.has(nama)) {
      let res;
      try {
        res = await fetch(`/data/blok/${nama}.json`);
      } catch (_) {
        throw new Error(T("galat.jaringan"));
      }
      if (!res.ok) throw new Error(T("galat.blok", { status: res.status }));
      try {
        blokCache.set(nama, await res.json());
      } catch (_) {
        throw new Error(T("galat.json"));
      }
    }
    return blokCache.get(nama).find((r) => r.kode === kode) || null;
  }

  async function mulai() {
    muatPref();
    terapkanPref();
    terapkanBahasa();
    daftarEl.innerHTML = `<p class="kosong">${amanHTML(T("daftar.memuat"))}</p>`;
    try {
      const [indeks, meta] = await Promise.all([
        fetch("/data/indeks.json").then((r) => r.json()),
        fetch("/data/meta.json").then((r) => r.json()),
      ]);
      state.meta = meta;
      state.entri = indeks.entri.map(([kode, nama, digit, halaman, sisa]) => ({
        kode, nama, digit, halaman, sisa: sisa === 1, induk: induk(kode), cari: normalisasi(nama),
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
      daftarEl.innerHTML = `<p class="kosong">${amanHTML(T("galat.awal"))}<br><small>` +
        amanHTML(String(kesalahan.message || kesalahan)) + "</small></p>";
    }
  }

  // ---------------------------------------------------------------- daftar

  function barisHTML(e, kunci, bertingkat) {
    const punyaAnak = state.anak.has(e.kode);
    const terbuka = state.terbuka.has(e.kode);
    const tanda = bertingkat && punyaAnak ? (terbuka ? "▾" : "▸") : "";
    const inden = bertingkat ? (e.digit === 6 ? 4 : e.digit - 1) : 0;
    const bawah = bertingkat ? "" :
      `<div class="baris-bawah">${amanHTML(namaTingkat(e.digit))} · ${amanHTML(T("rinci.halamanCetak"))} ${e.halaman}</div>`;
    return (
      `<button class="baris${state.terpilih === e.kode ? " terpilih" : ""}" role="treeitem"` +
      ` data-kode="${amanHTML(e.kode)}" data-digit="${e.digit}" data-inden="${inden}"` +
      (punyaAnak && bertingkat ? ` aria-expanded="${terbuka}"` : "") + ">" +
      '<span class="baris-atas">' +
      (bertingkat ? `<span class="buka" aria-hidden="true">${tanda}</span>` : "") +
      `<span class="kode">${amanHTML(e.kode)}</span>` +
      `<span class="baris-nama">${sorot(e.nama, kunci)}</span>` +
      (e.sisa ? `<span class="lencana lencana-sisa">${amanHTML(T("rinci.kelompokSisa"))}</span>` : "") +
      "</span>" + bawah + "</button>"
    );
  }

  function gambarDaftar() {
    if (state.kueri) return gambarHasilCari();
    judulDaftarEl.textContent = T("panel.telusuri");
    const tampil = [];
    const tambah = (e) => {
      tampil.push(e);
      if (!state.terbuka.has(e.kode)) return;
      for (const anak of state.anak.get(e.kode) || []) tambah(anak);
    };
    for (const e of state.entri.filter((x) => x.digit === 1)) tambah(e);
    jumlahEl.textContent = `${angka(state.entri.length)} ${T("panel.entri")}`;
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

    judulDaftarEl.textContent = T("panel.hasil");
    jumlahEl.textContent = `${angka(hasil.length)} ${T("panel.cocok")}`;
    daftarEl.innerHTML = hasil.length
      ? hasil.slice(0, 300).map(({ e }) => barisHTML(e, kunci, false)).join("") +
        (hasil.length > 300
          ? `<p class="kosong">${amanHTML(T("daftar.terbatas", { jumlah: angka(hasil.length) }))}</p>`
          : "")
      : `<p class="kosong">${amanHTML(T("daftar.kosong"))}<br><small>${amanHTML(T("daftar.kosongSaran"))}</small></p>`;
  }

  // ---------------------------------------------------------------- rel posisi

  /** Lima tingkat hierarki sebagai rel yang selalu terlihat: leluhur, posisi kini, dan turunan. */
  function relHTML(e) {
    const rantai = new Map();
    for (const k of [...leluhur(e.kode), e.kode]) rantai.set(k.replace(".", "").length === 6 ? 6 : k.replace(".", "").length, k);

    const butir = DIGIT.map((digit, i) => {
      const nomor = `<span class="rel-nomor" aria-hidden="true">${i + 1}</span>`;
      const tingkat = `<span class="rel-tingkat">${nomor}${amanHTML(T(`tingkat.${digit}.pendek`))}</span>`;
      const kode = rantai.get(digit);

      if (kode) {
        const simpul = state.peta.get(kode);
        const kini = kode === e.kode;
        const isi = `${tingkat}<span class="rel-kode">${amanHTML(kode)}</span>` +
                    `<span class="rel-nama">${amanHTML(simpul ? simpul.nama : "")}</span>`;
        return kini
          ? `<div class="rel-butir kini" aria-current="true" title="${amanHTML(T("posisi.iniDia"))}">${isi}</div>`
          : `<button type="button" class="rel-butir lalu" data-kode="${amanHTML(kode)}">${isi}</button>`;
      }

      const n = jumlahTurunan(e.kode, digit);
      return `<div class="rel-butir nanti"><span class="rel-tingkat">${nomor}${amanHTML(T(`tingkat.${digit}.pendek`))}</span>` +
             `<span class="rel-kode">${n ? `${angka(n)} ${amanHTML(T("posisi.turunan"))}` : amanHTML(T("posisi.takAda"))}</span></div>`;
    }).join("");

    return `<div class="rel"><span class="rel-judul">${amanHTML(T("posisi.judul"))}</span>${butir}</div>`;
  }

  function turunanHTML(e) {
    const anak = state.anak.get(e.kode) || [];
    const ringkas = DIGIT.filter((d) => d > (e.jumlah_digit === 4 ? 4 : e.jumlah_digit))
      .map((d) => ({ d, n: jumlahTurunan(e.kode, d) }))
      .filter((x) => x.n > 0)
      .map((x) => `<span class="turunan-kartu"><b>${angka(x.n)}</b> ${amanHTML(namaTingkat(x.d).toLowerCase())}</span>`)
      .join("");

    if (!anak.length) {
      return `<div class="rinci-bagian"><h3>${amanHTML(T("turunan.judul"))}</h3>` +
             `<p class="kosong">${amanHTML(T("turunan.kosong"))}</p></div>`;
    }
    const daftar = anak.map((a) => {
      const cucu = state.anak.get(a.kode);
      return `<button class="anak-butir" data-kode="${amanHTML(a.kode)}">` +
        `<span class="kode">${amanHTML(a.kode)}</span>` +
        `<span class="anak-nama">${amanHTML(a.nama)}</span>` +
        (a.sisa ? `<span class="lencana lencana-sisa">${amanHTML(T("rinci.kelompokSisa"))}</span>` : "") +
        (cucu ? `<span class="anak-jumlah">${angka(cucu.length)} ›</span>` : "") +
        "</button>";
    }).join("");

    return `<div class="rinci-bagian"><h3>${amanHTML(T("turunan.judul"))}</h3>` +
           (ringkas ? `<div class="turunan-ringkas">${ringkas}</div>` : "") +
           `<div class="anak-daftar">${daftar}</div></div>`;
  }

  // ---------------------------------------------------------------- rincian

  function sambutan() {
    const kartu = ((state.meta && state.meta.jumlah_per_tingkat) || [])
      .map((c, i) => `<div class="kartu"><div class="kartu-angka">${angka(c.hasil_ekstraksi)}</div>` +
                     `<div class="kartu-label">${amanHTML(namaTingkat(DIGIT[i]))}</div></div>`)
      .join("");
    const contoh = CONTOH.filter((k) => state.peta.has(k)).map((k) =>
      `<button class="tombol" data-kode="${k}"><span class="kode">${k}</span> ${amanHTML(state.peta.get(k).nama)}</button>`
    ).join("");
    rinciEl.innerHTML =
      '<div class="rinci-isi">' +
      `<h2 class="sambut-judul">${amanHTML(T("sambut.judul"))}</h2>` +
      `<p class="sambut-teks">${amanHTML(T("sambut.teks"))}</p>` +
      (contoh ? `<h3 class="judul-kecil">${amanHTML(T("sambut.contoh"))}</h3>` : "") +
      (contoh ? `<div class="contoh-baris">${contoh}</div>` : "") +
      `<div class="kartu-baris">${kartu}</div></div>`;
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

    rinciEl.innerHTML = `<div class="rinci-isi"><p class="kosong">${amanHTML(T("daftar.memuat"))}</p></div>`;
    let entri;
    try {
      entri = await muatBlok(kode);
    } catch (kesalahan) {
      rinciEl.innerHTML = `<div class="rinci-isi"><p class="kosong">${amanHTML(String(kesalahan.message))}</p></div>`;
      return;
    }
    if (!entri) {
      rinciEl.innerHTML = `<div class="rinci-isi"><p class="kosong">${amanHTML(T("galat.takAda", { kode }))}</p></div>`;
      return;
    }
    gambarRinci(entri);
    document.title = `${entri.kode} ${entri.nama_resmi} — KBJI 2026`;
    const isi = rinciEl.querySelector(".rinci-isi");
    if (isi) isi.scrollTop = 0;

    // Di layar satu kolom, panel rincian berada di bawah daftar. Bawa ke tampilan
    // supaya pengguna ponsel tidak perlu menggulir sendiri setiap memilih entri.
    if (dorongRiwayat && window.matchMedia("(max-width: 1000px)").matches) {
      const panel = rinciEl.closest(".panel-rinci");
      if (panel) panel.scrollIntoView({ behavior: state.pref.gerak ? "auto" : "smooth", block: "start" });
    }
  }

  function gambarRinci(e) {
    const remah = leluhur(e.kode).map((k) => {
      const n = state.peta.get(k);
      return n ? `<a href="/kode/${k}" data-kode="${k}"><span class="mono">${k}</span> ${amanHTML(n.nama)}</a>` : "";
    }).filter(Boolean).join('<span class="pemisah" aria-hidden="true">›</span>');

    const rentang = (a, b) => (a === b ? String(a) : `${a}–${b}`);
    const lencana = [
      `<span class="lencana lencana-tingkat">${amanHTML(namaTingkat(e.jumlah_digit))}</span>`,
      `<span class="lencana">${amanHTML(T("rinci.halamanCetak"))} ${rentang(e.halaman_cetak_mulai, e.halaman_cetak_selesai)}</span>`,
      `<span class="lencana">${amanHTML(T("rinci.halamanPdf"))} ${rentang(e.halaman_pdf_mulai, e.halaman_pdf_selesai)}</span>`,
      e.jumlah_jabatan_turunan
        ? `<span class="lencana">${angka(e.jumlah_jabatan_turunan)} ${amanHTML(T("rinci.jabatanTurunan"))}</span>` : "",
      e.kelompok_sisa === "ya"
        ? `<span class="lencana lencana-sisa">${amanHTML(T("rinci.kelompokSisa"))}</span>` : "",
    ].filter(Boolean).join("");

    rinciEl.innerHTML =
      '<div class="rinci-isi">' +
      relHTML(e) +
      (remah ? `<nav class="remah" aria-label="${amanHTML(T("rinci.jalur"))}">${remah}</nav>` : "") +
      '<div class="rinci-judul">' +
      `<span class="kode kode-besar">${amanHTML(e.kode)}</span><h2>${amanHTML(e.nama_resmi)}</h2></div>` +
      `<div class="lencana-baris">${lencana}</div>` +
      `<div class="rinci-bagian"><h3>${amanHTML(T("rinci.uraian"))}</h3>` +
      `<div class="uraian">${amanHTML(e.uraian_resmi)}</div></div>` +
      turunanHTML(e) +
      '<div class="aksi-baris">' +
      `<button class="tombol tombol-utama" type="button" data-salin="${amanHTML(e.kode)}">${amanHTML(T("rinci.salin"))}</button>` +
      (e.kode_induk ? `<button class="tombol" type="button" data-kode="${amanHTML(e.kode_induk)}">${amanHTML(T("rinci.induk"))}</button>` : "") +
      `<a class="tombol" href="/api/v1/kode/${encodeURIComponent(e.kode)}">${amanHTML(T("rinci.json"))}</a>` +
      "</div></div>";
  }

  // ---------------------------------------------------------------- tentang

  function gambarTentang() {
    const m = state.meta;
    if (!m) return;
    const selisih = new Map((m.selisih_sumber_terverifikasi || [])
      .filter((s) => !s.golongan_pokok).map((s) => [String(s.tingkat_digit), s]));
    el("ringkas-jumlah").innerHTML = (m.jumlah_per_tingkat || []).map((c) => {
      const beda = selisih.get(String(c.jumlah_digit));
      return '<div class="kartu">' +
        `<div class="kartu-angka">${angka(c.hasil_ekstraksi)}</div>` +
        `<div class="kartu-label">${amanHTML(namaTingkat(c.jumlah_digit))}</div>` +
        (beda ? `<div class="kartu-acuan">Tabel 3: ${angka(beda.acuan_publikasi)}</div>` : "") +
        "</div>";
    }).join("");

    const baris = [
      ["Publikasi", m.publikasi], ["Katalog", `${m.katalog} · ${m.nomor_publikasi}`],
      ["SHA-256", m.sumber_sha256], [state.pref.bahasa === "en" ? "PDF pages" : "Halaman PDF", angka(m.halaman_pdf)],
      [state.pref.bahasa === "en" ? "Transcription status" : "Status transkripsi", m.status_ekstraksi],
      [state.pref.bahasa === "en" ? "Source document status" : "Status dokumen sumber", m.status_sumber],
      [state.pref.bahasa === "en" ? "Tooling" : "Alat", `kbji.py ${m.versi_alat} · PyMuPDF ${m.versi_pymupdf}`],
      [state.pref.bahasa === "en" ? "Processed (UTC)" : "Waktu proses (UTC)", m.diproses_utc],
    ];
    el("meta-daftar").innerHTML = baris.map(([k, v]) =>
      `<dt>${amanHTML(k)}</dt><dd class="${k.startsWith("SHA") ? "mono" : ""}">${amanHTML(String(v))}</dd>`).join("");
    el("kaki-meta").textContent =
      `${m.versi_alat} · SHA-256 ${m.sumber_sha256.slice(0, 12)}… · ${angka(m.total_entri)} ` +
      `${T("panel.entri")} · ${m.diproses_utc.slice(0, 10)}`;
  }

  // ---------------------------------------------------------------- rute

  function terapkanRute() {
    const cocok = location.pathname.match(/^\/kode\/(.+)$/);
    if (cocok) {
      const kode = decodeURIComponent(cocok[1]);
      if (state.peta.has(kode)) { pilih(kode, false); return; }
    }
    state.terpilih = null;
    for (const e of state.entri.filter((x) => x.digit === 1)) state.terbuka.add(e.kode);
    gambarDaftar();
    sambutan();
    document.title = T("app.judul");
  }

  // ---------------------------------------------------------------- peristiwa

  daftarEl.addEventListener("click", (ev) => {
    const baris = ev.target.closest(".baris");
    if (!baris) return;
    const kode = baris.dataset.kode;
    if (ev.target.closest(".buka") && state.anak.has(kode)) {
      state.terbuka.has(kode) ? state.terbuka.delete(kode) : state.terbuka.add(kode);
      gambarDaftar();
      return;
    }
    if (!state.kueri && state.anak.has(kode)) state.terbuka.add(kode);
    pilih(kode);
  });

  rinciEl.addEventListener("click", (ev) => {
    const salin = ev.target.closest("[data-salin]");
    if (salin) {
      navigator.clipboard.writeText(salin.dataset.salin).then(() => {
        const semula = salin.textContent;
        salin.textContent = T("rinci.tersalin");
        setTimeout(() => { salin.textContent = semula; }, 1400);
      }, () => {});
      return;
    }
    const tuju = ev.target.closest("[data-kode]");
    if (tuju) { ev.preventDefault(); pilih(tuju.dataset.kode); }
  });

  let tunda;
  kotakCari.addEventListener("input", () => {
    clearTimeout(tunda);
    tunda = setTimeout(() => { state.kueri = kotakCari.value.trim(); gambarDaftar(); }, 120);
  });

  el("borang-cari").addEventListener("submit", (ev) => {
    ev.preventDefault();
    const pertama = daftarEl.querySelector(".baris");
    if (pertama) pilih(pertama.dataset.kode);
  });

  for (const cip of document.querySelectorAll(".cip")) {
    cip.addEventListener("click", () => {
      for (const c of document.querySelectorAll(".cip")) c.classList.remove("aktif");
      cip.classList.add("aktif");
      state.tingkat = cip.dataset.tingkat;
      if (!state.kueri && state.tingkat) kotakCari.focus();
      gambarDaftar();
    });
  }

  window.addEventListener("popstate", terapkanRute);

  document.addEventListener("keydown", (ev) => {
    if (ev.key === "/" && document.activeElement !== kotakCari && !el("pref").hasAttribute("hidden") === false) {
      if (document.activeElement.tagName === "INPUT") return;
      ev.preventDefault(); kotakCari.focus(); kotakCari.select();
    }
    if (ev.key === "Escape") {
      if (!el("pref").hidden) { tutupPref(); return; }
      if (document.activeElement === kotakCari) {
        kotakCari.value = ""; state.kueri = ""; gambarDaftar(); kotakCari.blur();
      }
    }
  });

  // maklumat dapat disembunyikan, dan pilihannya diingat
  const maklumat = el("maklumat");
  try { if (localStorage.getItem("kbji-maklumat") === "tutup") maklumat.hidden = true; } catch (_) {}
  el("tutup-maklumat").addEventListener("click", () => {
    maklumat.hidden = true;
    try { localStorage.setItem("kbji-maklumat", "tutup"); } catch (_) {}
  });

  // ---------------------------------------------------------------- panel preferensi

  let pemicuPref = null;
  function bukaPref() {
    pemicuPref = document.activeElement;
    el("tirai").hidden = false;
    el("pref").hidden = false;
    el("buka-pref").setAttribute("aria-expanded", "true");
    el("tutup-pref").focus();
  }
  function tutupPref() {
    el("tirai").hidden = true;
    el("pref").hidden = true;
    el("buka-pref").setAttribute("aria-expanded", "false");
    if (pemicuPref) pemicuPref.focus();
  }
  el("buka-pref").addEventListener("click", bukaPref);
  el("tutup-pref").addEventListener("click", tutupPref);
  el("tirai").addEventListener("click", tutupPref);

  for (const grup of document.querySelectorAll("[data-pref]")) {
    grup.addEventListener("click", (ev) => {
      const b = ev.target.closest(".pilihan-butir");
      if (b) ubahPref(grup.dataset.pref, b.dataset.nilai);
    });
  }
  for (const kotak of document.querySelectorAll("[data-pref-saklar]")) {
    kotak.addEventListener("change", () => ubahPref(kotak.dataset.prefSaklar, kotak.checked));
  }
  el("setel-pref").addEventListener("click", () => {
    state.pref = { ...BAWAAN };
    terapkanPref(); terapkanBahasa(); gambarTentang(); gambarDaftar();
    if (state.terpilih) pilih(state.terpilih, false); else sambutan();
  });

  // Jaga fokus tetap di dalam panel selagi terbuka.
  el("pref").addEventListener("keydown", (ev) => {
    if (ev.key !== "Tab") return;
    const fokusable = el("pref").querySelectorAll('button, input, [href], [tabindex]:not([tabindex="-1"])');
    if (!fokusable.length) return;
    const pertama = fokusable[0], terakhir = fokusable[fokusable.length - 1];
    if (ev.shiftKey && document.activeElement === pertama) { ev.preventDefault(); terakhir.focus(); }
    else if (!ev.shiftKey && document.activeElement === terakhir) { ev.preventDefault(); pertama.focus(); }
  });

  mulai();
})();
