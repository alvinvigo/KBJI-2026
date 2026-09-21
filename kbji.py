#!/usr/bin/env python3
"""Ekstraksi KBJI 2026 berbasis tata letak PDF; tanpa API, OCR, atau AI.

Python >=3.10. Jalankan `python kbji.py --help`.
Kode, nama, dan uraian sumber ditranskripsi apa adanya; tidak ada koreksi,
penambahan, atau penghapusan entri secara otomatis.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import platform
import re
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
VERSION = "2.0.0"

LEVELS = {1: "Golongan pokok", 2: "Subgolongan pokok", 3: "Golongan", 4: "Subgolongan", 6: "Jabatan"}
DEPTH = {1: 1, 2: 2, 3: 3, 4: 4, 6: 5}
ANCESTOR_COLUMNS = {1: ("kode_golongan_pokok", "nama_golongan_pokok"),
                    2: ("kode_subgolongan_pokok", "nama_subgolongan_pokok"),
                    3: ("kode_golongan", "nama_golongan"),
                    4: ("kode_subgolongan", "nama_subgolongan")}

CODE = re.compile(r"^(?:\d{1,4}|\d{4}\.\d{2})$")
HEAD = re.compile(r"^(\d{4}\.\d{2}|\d{1,4})(?:\s+(.*))?$")
WATERMARK = "https://www.bps.go.id"

FIELDS = [
    "id_entri", "versi_kbji", "kode", "kode_normalisasi", "jumlah_digit", "tingkat", "kedalaman",
    "urutan", "kode_induk", "nama_resmi", "uraian_resmi",
    "kode_golongan_pokok", "nama_golongan_pokok",
    "kode_subgolongan_pokok", "nama_subgolongan_pokok",
    "kode_golongan", "nama_golongan",
    "kode_subgolongan", "nama_subgolongan",
    "jalur_kode", "jalur_nama",
    "jumlah_anak_langsung", "jumlah_jabatan_turunan", "kelompok_sisa", "nama_pencarian",
    "halaman_pdf_mulai", "halaman_pdf_selesai", "halaman_cetak_mulai", "halaman_cetak_selesai",
    "status_validasi",
]
# Kolom yang ditulis oleh parser; sisanya diturunkan oleh lengkapi_turunan().
BASE_FIELDS = ["id_entri", "versi_kbji", "kode", "kode_normalisasi", "jumlah_digit", "tingkat",
               "kode_induk", "nama_resmi", "uraian_resmi", "halaman_pdf_mulai", "halaman_pdf_selesai",
               "status_validasi"]
RINGKAS_FIELDS = ["kode", "kode_normalisasi", "jumlah_digit", "tingkat", "kode_induk", "nama_resmi",
                  "kode_golongan_pokok", "nama_golongan_pokok", "jalur_kode", "kelompok_sisa",
                  "halaman_cetak_mulai"]
ISSUE_FIELDS = ["kategori", "kelas", "keparahan", "id_entri", "kode", "halaman_pdf", "detail"]

# kelas: "ekstraksi" = dugaan cacat pada proses ini; "sumber" = ketidaksesuaian di dalam publikasi.
CATEGORIES = [
    "duplikat", "tanpa_induk", "nama_kosong", "uraian_kosong", "format_kode", "pola_tidak_terbaca",
    "hierarki", "turunan", "urutan", "halaman", "karakter", "metadata", "cakupan",
    "kelengkapan_kode", "daftar_isi", "nama_daftar_isi", "halaman_daftar_isi", "anak_induk",
    "penomoran", "penanda_sisa", "jumlah_tidak_sesuai",
]
SEVERITIES = ("error", "peringatan", "informasi")


# --------------------------------------------------------------------------- util

def write_csv(path, rows, fields):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # UTF-8 BOM memudahkan impor Excel. Kutip semua sel; kode tetap perlu diimpor sebagai Text.
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = set(FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Kolom wajib tidak tersedia: " + ", ".join(sorted(missing)))
        return list(reader)


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parent(code):
    """Induk struktural: 0111.01 -> 0111 -> 011 -> 01 -> 0 -> ''."""
    if "." in code:
        return code.split(".")[0]
    return code[:-1]


def ancestors(code):
    """Seluruh induk dari yang terdekat ke golongan pokok."""
    chain, cur = [], parent(code)
    while cur:
        chain.append(cur)
        cur = parent(cur)
    return chain


def digits_of(code):
    return len(code.replace(".", ""))


def kelompok_sisa(code):
    """Kode sisa/lainnya menurut aturan penomoran pada Tabel 3 dan penjelasannya (PDF 45).

    Angka 9 pada digit terakhir tingkat 2/3/4 digit dan akhiran .99 pada jabatan
    menandai kelompok sisa. Golongan pokok dikecualikan karena kode 0-9 dipakai penuh.
    """
    d = digits_of(code)
    if d in (2, 3, 4):
        return "ya" if code[-1] == "9" else "tidak"
    if d == 6:
        return "ya" if code.endswith(".99") else "tidak"
    return "tidak"


def nama_pencarian(nama):
    """Turunan untuk pencocokan teks. Kolom resmi tidak diubah."""
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-z]+", " ", nama.casefold())).strip()


def issue(category, detail, row=None, severity="error", kelas="ekstraksi"):
    row = row or {}
    return dict(kategori=category, kelas=kelas, keparahan=severity,
                id_entri=row.get("id_entri", ""), kode=row.get("kode", ""),
                halaman_pdf=row.get("halaman_pdf_mulai", row.get("page", "")), detail=detail)


# --------------------------------------------------------------------------- turunan

def lengkapi_turunan(rows):
    """Isi kolom turunan dari relasi struktural. Tidak menambah atau menghapus entri."""
    by_code = {}
    for r in rows:
        by_code.setdefault(r["kode"], r)
    anak = collections.Counter()
    jabatan = collections.Counter()
    for r in rows:
        code = r["kode"]
        p = parent(code)
        if p:
            anak[p] += 1
        if digits_of(code) == 6:
            for a in ancestors(code):
                jabatan[a] += 1
    for i, r in enumerate(rows, start=1):
        code = r["kode"]
        d = digits_of(code)
        r["kode_normalisasi"] = code.replace(".", "")
        r["jumlah_digit"] = d
        r["tingkat"] = LEVELS.get(d, "")
        r["kedalaman"] = DEPTH.get(d, "")
        r["urutan"] = i
        r["kode_induk"] = parent(code)
        for col_code, col_name in ANCESTOR_COLUMNS.values():
            r[col_code] = r[col_name] = ""
        rantai = [code] + ancestors(code)
        for c in rantai:
            cols = ANCESTOR_COLUMNS.get(digits_of(c))
            if cols:
                r[cols[0]] = c
                r[cols[1]] = by_code[c]["nama_resmi"] if c in by_code else ""
        rantai = list(reversed(rantai))
        r["jalur_kode"] = " > ".join(rantai)
        r["jalur_nama"] = " > ".join(by_code[c]["nama_resmi"] if c in by_code else "" for c in rantai)
        r["jumlah_anak_langsung"] = anak[code]
        r["jumlah_jabatan_turunan"] = jabatan[code]
        r["kelompok_sisa"] = kelompok_sisa(code)
        r["nama_pencarian"] = nama_pencarian(r["nama_resmi"])
    return rows


def pohon(rows):
    """Bentuk struktur bersarang untuk penelusuran taksonomi; tanpa uraian agar ringan."""
    node = {r["kode"]: dict(kode=r["kode"], nama_resmi=r["nama_resmi"], tingkat=r["tingkat"],
                            jumlah_digit=r["jumlah_digit"], kelompok_sisa=r["kelompok_sisa"],
                            halaman_cetak_mulai=r["halaman_cetak_mulai"], anak=[]) for r in rows}
    akar = []
    for r in rows:
        p = r["kode_induk"]
        (node[p]["anak"] if p in node else akar).append(node[r["kode"]])
    return akar


# --------------------------------------------------------------------------- pembacaan PDF

def page_lines(page, page_number, profile, removed):
    """Kelompokkan fragmen horizontal pada baseline yang sama; watermark dikenali dari arah teks."""
    lines = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(s["text"] for s in line["spans"]).strip()
            if not text:
                continue
            y = line["bbox"][1]
            reason = None
            if abs(line["dir"][1]) > 0.01:
                reason = "teks_miring_watermark"
            elif y < profile["body_top"] or y > profile["body_bottom"]:
                reason = "margin_kepala_kaki"
            if reason:
                removed.append(dict(halaman_pdf=page_number, alasan=reason, teks=text))
                continue
            spans = [s for s in line["spans"] if s["text"].strip()]
            lines.append(dict(y=y, x=line["bbox"][0], text=text,
                              bold=all("bold" in s["font"].lower() for s in spans)))
    lines.sort(key=lambda z: (round(z["y"]), z["x"]))
    groups = []
    for line in lines:
        if groups and abs(line["y"] - groups[-1][0]["y"]) < 2:
            groups[-1].append(line)
        else:
            groups.append([line])
    result = []
    for g in groups:
        g.sort(key=lambda z: z["x"])
        result.append(dict(page=page_number, y=g[0]["y"], x=g[0]["x"],
                           text=" ".join(l["text"] for l in g),
                           bold=all(l["bold"] for l in g), first_bold=g[0]["bold"]))
    return result


def parse_body(layout_rows, profile):
    """Judul = kode tebal pada kolom kiri. Sisanya uraian milik kode terakhir."""
    entries, problems, trace = [], [], []
    current = None
    title_open = False
    for line in layout_rows:
        match = HEAD.fullmatch(line["text"])
        is_header = bool(match) and line["first_bold"] and line["x"] <= profile["code_max_x"]
        if is_header:
            code, title = match[1], match[2] or ""
            current = dict(id_entri=f"E{len(entries)+1:05d}", versi_kbji=profile["version"],
                           kode=code, kode_normalisasi=code.replace(".", ""),
                           jumlah_digit=digits_of(code), tingkat=LEVELS.get(digits_of(code), ""),
                           kode_induk=parent(code), nama_resmi=title, uraian_resmi="",
                           halaman_pdf_mulai=line["page"], halaman_pdf_selesai=line["page"],
                           status_validasi="lolos_struktur_otomatis_belum_review_manual")
            entries.append(current)
            title_open, role = True, "judul"
        elif current is None:
            problems.append(issue("pola_tidak_terbaca", "Teks sebelum entri pertama: " + line["text"], line))
            role = "tidak_terpetakan"
        elif title_open and line["bold"]:
            current["nama_resmi"] += " " + line["text"]
            role = "lanjutan_judul"
        else:
            title_open = False
            current["uraian_resmi"] += ("\n" if current["uraian_resmi"] else "") + line["text"]
            role = "uraian"
            if line["bold"] or (line["x"] <= profile["code_max_x"] and re.match(r"^\d", line["text"])):
                problems.append(issue("pola_tidak_terbaca",
                                      "Baris menyerupai judul tetapi tidak memenuhi aturan: " + line["text"], current))
        if current:
            current["halaman_pdf_selesai"] = line["page"]
        trace.append(dict(**line, id_entri=current["id_entri"] if current else "", peran=role))
    for r in entries:
        r["halaman_cetak_mulai"] = r["halaman_pdf_mulai"] - profile["printed_page_offset"]
        r["halaman_cetak_selesai"] = r["halaman_pdf_selesai"] - profile["printed_page_offset"]
    return entries, problems, trace


def parse_toc(doc, profile):
    """Transkripsi Daftar Isi: kode, nama, dan nomor halaman cetak untuk tingkat 1-4 digit."""
    entries, current = [], None
    for page_number in range(profile["toc_start"], profile["toc_end"] + 1):
        page = doc[page_number - 1]
        lines = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                text = "".join(s["text"] for s in line["spans"]).strip()
                if not text or abs(line["dir"][1]) > 0.01:
                    continue
                y = line["bbox"][1]
                if y < profile["body_top"] or y > profile["body_bottom"]:
                    continue
                lines.append((round(y, 1), line["bbox"][0], text))
        lines.sort()
        groups = []
        for y, x, text in lines:
            if groups and abs(y - groups[-1][0][0]) < 3:
                groups[-1].append((y, x, text))
            else:
                groups.append([(y, x, text)])
        for g in groups:
            g.sort(key=lambda z: z[1])
            joined = " ".join(t for _, _, t in g)
            match = re.match(r"^(\d{1,4})\s+(.*)$", joined)
            if match and g[0][1] <= profile["toc_code_max_x"]:
                current = [match[1], match[2], page_number]
                entries.append(current)
            elif current is not None and not re.match(r"^(KATA|DAFTAR|PENJELASAN|[IVX]+\.)\b", joined):
                current[1] += " " + joined
    result = []
    for code, text, page_number in entries:
        match = re.match(r"^(.*?)[\s.]*\.{3,}[\s.]*(\d+)\s*$", text)
        nama = re.sub(r"\s+", " ", (match[1] if match else text)).strip()
        result.append(dict(kode=code, nama_daftar_isi=nama,
                           halaman_cetak=int(match[2]) if match else "",
                           halaman_pdf_daftar_isi=page_number))
    return result


def scan_code_column(doc, profile):
    """Pemindaian independen: setiap span yang isinya persis sebuah kode pada kolom kiri isi.

    Dipakai untuk membuktikan tidak ada judul yang terlewat oleh aturan tebal/kolom.
    """
    found = {}
    for i in range(profile["body_start"] - 1, profile["body_end"]):
        page = doc[i]
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                if abs(line["dir"][1]) > 0.01:
                    continue
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not CODE.fullmatch(text):
                        continue
                    x, y = span["bbox"][0], span["bbox"][1]
                    if x > profile["code_max_x"] or y < profile["body_top"] or y > profile["body_bottom"]:
                        continue
                    found.setdefault(text, dict(kode=text, halaman_pdf=i + 1, x=round(x, 1),
                                                font=span["font"], jumlah=0))
                    found[text]["jumlah"] += 1
    return found


def page_profile(doc, profile):
    """Klasifikasi halaman tanpa teks isi berdasarkan bukti objektif, bukan daftar manual."""
    result = {}
    for i in range(profile["body_start"] - 1, profile["body_end"]):
        page = doc[i]
        teks = page.get_text().replace(WATERMARK, "").strip()
        gambar = len(page.get_images(full=True))
        if gambar and len(teks) < profile["divider_max_chars"]:
            result[i + 1] = "pembatas_bab_terdeteksi_gambar_halaman_penuh"
        elif not teks and not gambar:
            result[i + 1] = "halaman_kosong_terdeteksi_tanpa_teks_dan_gambar"
        else:
            result[i + 1] = "berisi_teks"
    return result


# --------------------------------------------------------------------------- pemeriksaan

def validate(rows, profile):
    """Pemeriksaan struktur mandiri; tidak mengubah, menambah, atau menghapus entri."""
    problems = []
    by_code = collections.defaultdict(list)
    for r in rows:
        by_code[r["kode"]].append(r)
    for code, group in by_code.items():
        if len(group) > 1:
            for r in group:
                problems.append(issue("duplikat", f"Kode muncul {len(group)} kali; seluruh entri dipertahankan.", r))

    counts = collections.Counter()
    last_key = None
    for r in rows:
        code = r["kode"]
        if not CODE.fullmatch(code):
            problems.append(issue("format_kode", "Format harus 1/2/3/4 digit atau dddd.dd.", r))
            continue
        digit = digits_of(code)
        counts[digit] += 1
        if (r["kode_normalisasi"] != code.replace(".", "") or str(r["jumlah_digit"]) != str(digit)
                or r["tingkat"] != LEVELS[digit] or str(r["kedalaman"]) != str(DEPTH[digit])):
            problems.append(issue("hierarki", "Kode normalisasi, jumlah digit, tingkat, atau kedalaman tidak konsisten.", r))
        if r["kode_induk"] != parent(code):
            problems.append(issue("hierarki", f"Kode induk seharusnya {parent(code)!r}.", r))
        if parent(code) and parent(code) not in by_code:
            problems.append(issue("tanpa_induk", f"Induk {parent(code)} tidak ditemukan.", r))
        if not r["nama_resmi"].strip():
            problems.append(issue("nama_kosong", "Nama tidak ditemukan.", r))
        if not r["uraian_resmi"].strip():
            problems.append(issue("uraian_kosong", "Uraian tidak ditemukan.", r))
        if r["versi_kbji"] != profile["version"]:
            problems.append(issue("metadata", "Versi tidak sesuai profil.", r))
        if "�" in r["nama_resmi"] + r["uraian_resmi"] or WATERMARK in r["uraian_resmi"]:
            problems.append(issue("karakter", "Karakter pengganti atau watermark tersisa; periksa sumber.", r))
        problems += check_turunan(r, by_code)
        try:
            start, end = int(r["halaman_pdf_mulai"]), int(r["halaman_pdf_selesai"])
            if not profile["body_start"] <= start <= end <= profile["body_end"]:
                raise ValueError()
            if (int(r["halaman_cetak_mulai"]) != start - profile["printed_page_offset"]
                    or int(r["halaman_cetak_selesai"]) != end - profile["printed_page_offset"]):
                raise ValueError()
        except (ValueError, TypeError):
            problems.append(issue("halaman", "Rentang halaman atau nomor cetak tidak valid untuk profil ini.", r))
        key = tuple(code.replace(".", ""))
        if last_key is not None and key < last_key:
            problems.append(issue("urutan", "Kode menurun dibanding entri sebelumnya; periksa PDF.", r, "peringatan"))
        last_key = key

    problems += check_penomoran(rows, by_code)
    problems += check_jumlah(rows, counts, profile)
    return problems


def check_turunan(r, by_code):
    """Kolom turunan harus dapat dihitung ulang dari kode dan nama resmi."""
    problems = []
    code = r["kode"]
    rantai = list(reversed([code] + ancestors(code)))
    expected = {"jalur_kode": " > ".join(rantai),
                "jalur_nama": " > ".join(by_code[c][0]["nama_resmi"] if c in by_code else "" for c in rantai),
                "kelompok_sisa": kelompok_sisa(code),
                "nama_pencarian": nama_pencarian(r["nama_resmi"])}
    for c in rantai:
        cols = ANCESTOR_COLUMNS.get(digits_of(c))
        if cols:
            expected[cols[0]] = c
            expected[cols[1]] = by_code[c][0]["nama_resmi"] if c in by_code else ""
    for cols in ANCESTOR_COLUMNS.values():
        expected.setdefault(cols[0], "")
        expected.setdefault(cols[1], "")
    for key, value in expected.items():
        if r.get(key, "") != value:
            problems.append(issue("turunan", f"Kolom {key} tidak sesuai hasil perhitungan ulang: {r.get(key, '')!r} != {value!r}.", r))
    return problems


def check_penomoran(rows, by_code):
    """Konvensi penomoran KBJI: subgolongan bernomor urut, 9 untuk sisa, X0 bila tunggal."""
    problems = []
    kids = collections.defaultdict(list)
    for r in rows:
        if r["kode_induk"]:
            kids[r["kode_induk"]].append(r["kode"])
    for golongan in sorted(c for c in by_code if digits_of(c) == 3):
        anak = sorted(int(c[3]) for c in kids.get(golongan, []))
        if not anak:
            problems.append(issue("penomoran", "Golongan tanpa subgolongan.", by_code[golongan][0]))
            continue
        if anak == [0]:
            continue
        bukan_sisa = [d for d in anak if d != 9]
        celah = [d for d in range(1, (max(bukan_sisa) if bukan_sisa else 0)) if d not in bukan_sisa]
        if celah:
            problems.append(issue("penomoran",
                                  f"Golongan {golongan} {by_code[golongan][0]['nama_resmi']}: nomor subgolongan tidak "
                                  "berurutan. Kode yang tidak dipakai pada publikasi: "
                                  + ", ".join(golongan + str(d) for d in celah) + ".",
                                  by_code[golongan][0], "informasi", "sumber"))
        if 0 in anak and len(anak) > 1:
            problems.append(issue("penomoran", "Kode berakhiran 0 dipakai bersama subgolongan lain.",
                                  by_code[golongan][0], "peringatan"))
    for r in rows:
        nama_sisa = bool(re.search(r"\b(LAINNYA|YTDL)\b", r["nama_resmi"]))
        if (r["kelompok_sisa"] == "ya") != nama_sisa:
            problems.append(issue("penanda_sisa",
                                  f"Kode {r['kode']} bertanda kelompok sisa={r['kelompok_sisa']} menurut aturan "
                                  f"penomoran, tetapi penamaan sumber berbunyi {r['nama_resmi']!r}. "
                                  "Gunakan kolom kelompok_sisa sebagai penanda kode, bukan sebagai tafsir judul.",
                                  r, "informasi", "sumber"))
    return problems


def check_jumlah(rows, counts, profile):
    """Bandingkan jumlah hasil dengan acuan publikasi; bedakan cacat ekstraksi dari selisih sumber."""
    problems = []
    known = {(str(d["tingkat_digit"]), d.get("golongan_pokok", "")): d for d in profile.get("selisih_sumber_terverifikasi", [])}

    def lapor(digit, major, actual, expected, rujukan):
        if actual == expected:
            return
        key = (str(digit), major)
        fakta = known.get(key)
        cocok = fakta and fakta["hasil_terverifikasi"] == actual and fakta["acuan_publikasi"] == expected
        detail = (f"{LEVELS[int(digit)]} ({digit} digit)"
                  + (f", golongan pokok {major}" if major else "")
                  + f": hasil ekstraksi {actual}; acuan publikasi {expected} ({rujukan}).")
        if cocok:
            problems.append(issue("jumlah_tidak_sesuai",
                                  detail + " Selisih ini sudah diverifikasi berasal dari dokumen sumber: "
                                  + fakta["bukti"] + " Tidak ada entri yang ditambahkan untuk menutup selisih.",
                                  severity="peringatan", kelas="sumber"))
        else:
            problems.append(issue("jumlah_tidak_sesuai",
                                  detail + " Selisih ini BELUM terverifikasi sebagai ciri sumber; periksa ekstraksi.",
                                  severity="error", kelas="ekstraksi"))

    acuan = profile["acuan_publikasi"]
    for digit, expected in acuan["jumlah_total"].items():
        lapor(digit, "", counts[int(digit)], expected, acuan["rujukan_total"])
    for major, targets in acuan.get("jumlah_per_golongan_pokok", {}).items():
        for digit, target in zip([1, 2, 3, 4, 6], targets):
            actual = sum(r["kode"].startswith(major) and str(r["jumlah_digit"]) == str(digit) for r in rows)
            lapor(digit, major, actual, target, acuan["rujukan_per_golongan_pokok"].format(golongan_pokok=major))
    return problems


def check_noncontent_pages(halaman, profile, digest):
    """Halaman tanpa teks isi yang terdeteksi harus sama dengan daftar yang sudah ditinjau pada profil."""
    if digest != profile["source_sha256"]:
        return []
    terdeteksi = {p for p, s in halaman.items() if s != "berisi_teks"}
    ditinjau = {int(p) for p in profile.get("reviewed_noncontent_pages", {})}
    problems = []
    for p in sorted(terdeteksi - ditinjau):
        problems.append(issue("cakupan", f"Halaman {p} tidak berisi teks isi tetapi belum tercatat pada profil "
                                         "halaman yang sudah ditinjau.", {"page": p}))
    for p in sorted(ditinjau - terdeteksi):
        problems.append(issue("cakupan", f"Halaman {p} tercatat pada profil sebagai halaman tanpa isi, "
                                         "tetapi pada berkas ini terbaca berisi teks.", {"page": p}))
    return problems


def reconcile_toc(toc, rows):
    """Bandingkan kode, nama, dan halaman cetak Daftar Isi dengan judul pada bagian uraian."""
    body = {r["kode"]: r for r in rows if int(r["jumlah_digit"]) < 6}
    daftar = {t["kode"]: t for t in toc}
    report, problems = [], []

    def samakan(teks):
        return re.sub(r"\s+", " ", teks).strip().casefold()

    for code in sorted(set(daftar) | set(body)):
        t, b = daftar.get(code), body.get(code)
        nama_sama = bool(t and b) and samakan(t["nama_daftar_isi"]) == samakan(b["nama_resmi"])
        halaman_sama = bool(t and b) and str(t["halaman_cetak"]) == str(b["halaman_cetak_mulai"])
        report.append(dict(kode=code, ada_daftar_isi=bool(t), ada_uraian=bool(b),
                           nama_daftar_isi=t["nama_daftar_isi"] if t else "",
                           nama_uraian=b["nama_resmi"] if b else "",
                           nama_cocok=nama_sama,
                           halaman_cetak_daftar_isi=t["halaman_cetak"] if t else "",
                           halaman_cetak_uraian=b["halaman_cetak_mulai"] if b else "",
                           halaman_cocok=halaman_sama))
        if bool(t) != bool(b):
            problems.append(issue("daftar_isi", f"Kode {code}: daftar isi={bool(t)}, uraian={bool(b)}.", {"kode": code}))
            continue
        if not nama_sama:
            problems.append(issue("nama_daftar_isi",
                                  f"Nama berbeda. Daftar isi: {t['nama_daftar_isi']!r}; uraian: {b['nama_resmi']!r}.", b))
        if not halaman_sama:
            problems.append(issue("halaman_daftar_isi",
                                  f"Halaman cetak berbeda. Daftar isi: {t['halaman_cetak']}; uraian: {b['halaman_cetak_mulai']}.", b))
    return report, problems


def reconcile_children(rows):
    """Kode anak yang disebut di dalam uraian induk harus punya judul sendiri."""
    by_code = {r["kode"]: r for r in rows}
    kids = collections.defaultdict(set)
    for r in rows:
        if r["kode_induk"]:
            kids[r["kode_induk"]].add(r["kode"])
    report, problems = [], []
    for r in rows:
        digit = int(r["jumlah_digit"])
        if digit not in (1, 2, 3, 4):
            continue
        anak_digit = {1: 2, 2: 3, 3: 4, 4: 6}[digit]
        pola = r"^\s*(\d{4}\.\d{2})\b" if anak_digit == 6 else r"^\s*(\d{%d})\b" % anak_digit
        disebut = set()
        for baris in r["uraian_resmi"].split("\n"):
            m = re.match(pola, baris)
            if m and m[1].startswith(r["kode"].split(".")[0] if digit == 4 else r["kode"]):
                disebut.add(m[1])
        if not disebut:
            continue
        hilang = sorted(disebut - kids[r["kode"]])
        report.append(dict(kode_induk=r["kode"], jumlah_disebut_di_uraian=len(disebut),
                           jumlah_judul=len(kids[r["kode"]]),
                           disebut_tanpa_judul=";".join(hilang),
                           judul_tanpa_disebut=";".join(sorted(kids[r["kode"]] - disebut))))
        for code in hilang:
            problems.append(issue("anak_induk",
                                  f"Kode {code} disebut sebagai anak pada uraian {r['kode']} tetapi tidak memiliki judul sendiri.",
                                  by_code[r["kode"]]))
    return report, problems


def reconcile_scan(scan, rows):
    """Pemindaian kolom kode harus menghasilkan himpunan kode yang sama dengan hasil parsing."""
    hasil = {r["kode"] for r in rows}
    report, problems = [], []
    for code in sorted(set(scan) | hasil, key=lambda c: (len(c.replace(".", "")), c)):
        report.append(dict(kode=code, terpindai_kolom_kode=code in scan, terbaca_sebagai_judul=code in hasil,
                           halaman_pdf=scan[code]["halaman_pdf"] if code in scan else "",
                           jumlah_kemunculan=scan[code]["jumlah"] if code in scan else 0))
        if code in scan and code not in hasil:
            problems.append(issue("kelengkapan_kode",
                                  f"Kode {code} muncul pada kolom kode halaman PDF {scan[code]['halaman_pdf']} tetapi tidak terbaca sebagai judul.",
                                  {"kode": code, "page": scan[code]["halaman_pdf"]}))
        if code in hasil and code not in scan:
            problems.append(issue("kelengkapan_kode",
                                  f"Kode {code} terbaca sebagai judul tetapi tidak ditemukan oleh pemindaian kolom kode.",
                                  {"kode": code}))
    return report, problems


# --------------------------------------------------------------------------- pelaporan

def hitung_status(problems):
    berat = [p for p in problems if p["keparahan"] in ("error", "peringatan")]
    ekstraksi = [p for p in berat if p["kelas"] == "ekstraksi"]
    sumber = [p for p in berat if p["kelas"] == "sumber"]
    return dict(
        status_ekstraksi="LENGKAP_DAN_KONSISTEN" if not ekstraksi else "PERLU_TINJAUAN_EKSTRAKSI",
        status_sumber="KONSISTEN" if not sumber else "ADA_INKONSISTENSI_DOKUMEN_SUMBER",
        temuan_ekstraksi=len(ekstraksi), temuan_sumber=len(sumber),
        temuan_informasi=len(problems) - len(berat),
    )


def exit_code(status):
    if status["status_ekstraksi"] != "LENGKAP_DAN_KONSISTEN":
        return 2
    return 3 if status["status_sumber"] != "KONSISTEN" else 0


def reports(rows, problems, profile, folder, metadata=None):
    folder.mkdir(parents=True, exist_ok=True)
    for cat in CATEGORIES:
        write_csv(folder / (cat + ".csv"), [p for p in problems if p["kategori"] == cat], ISSUE_FIELDS)
    write_csv(folder / "semua_temuan.csv", problems, ISSUE_FIELDS)

    acuan = profile["acuan_publikasi"]
    counts = []
    for d, expected in acuan["jumlah_total"].items():
        subset = [r for r in rows if str(r["jumlah_digit"]) == d]
        counts.append(dict(jumlah_digit=d, tingkat=LEVELS[int(d)], acuan_publikasi=expected,
                           hasil_ekstraksi=len(subset), kode_unik=len({r["kode"] for r in subset}),
                           selisih=len(subset) - expected))
    write_csv(folder / "jumlah_per_tingkat.csv", counts,
              ["jumlah_digit", "tingkat", "acuan_publikasi", "hasil_ekstraksi", "kode_unik", "selisih"])

    major = []
    for code, expected in acuan.get("jumlah_per_golongan_pokok", {}).items():
        for d, target in zip([1, 2, 3, 4, 6], expected):
            actual = sum(r["kode"].startswith(code) and str(r["jumlah_digit"]) == str(d) for r in rows)
            major.append(dict(golongan_pokok=code, jumlah_digit=d, tingkat=LEVELS[d],
                              acuan_publikasi=target, hasil_ekstraksi=actual, selisih=actual - target))
    write_csv(folder / "jumlah_per_golongan_pokok.csv", major,
              ["golongan_pokok", "jumlah_digit", "tingkat", "acuan_publikasi", "hasil_ekstraksi", "selisih"])

    status = hitung_status(problems)
    summary = dict(**status, total_entri=len(rows), jumlah_temuan=len(problems),
                   kategori=dict(collections.Counter(p["kategori"] for p in problems)),
                   keparahan=dict(collections.Counter(p["keparahan"] for p in problems)),
                   jumlah_per_tingkat=counts,
                   catatan=("Pemeriksaan otomatis tidak menggantikan pembacaan manual seluruh redaksi. "
                            "Selisih jumlah tidak pernah ditutup dengan menambah, menghapus, atau mengarang kode."),
                   metadata=metadata or {})
    write_json(folder / "ringkasan.json", summary)

    lines = ["# Laporan validasi KBJI 2026", "",
             f"- Status ekstraksi: **{status['status_ekstraksi']}** ({status['temuan_ekstraksi']} temuan)",
             f"- Status dokumen sumber: **{status['status_sumber']}** ({status['temuan_sumber']} temuan)",
             f"- Catatan informasi: {status['temuan_informasi']}",
             "", f"Total entri: {len(rows)}.", "",
             "| Tingkat | Acuan publikasi | Hasil ekstraksi | Selisih |", "|---|---:|---:|---:|"]
    for c in counts:
        lines.append(f"| {c['tingkat']} | {c['acuan_publikasi']} | {c['hasil_ekstraksi']} | {c['selisih']} |")
    lines += ["", summary["catatan"], "",
              "Uraian mempertahankan pergantian baris PDF. Pemisahan kata dengan tanda hubung dan ejaan sumber "
              "tidak diperbaiki otomatis.", ""]
    for kelas, judul in (("ekstraksi", "Temuan proses ekstraksi"), ("sumber", "Temuan pada dokumen sumber")):
        subset = [p for p in problems if p["kelas"] == kelas]
        lines += [f"## {judul}", ""]
        lines += [f"- `{p['kategori']}` ({p['keparahan']}, halaman PDF {p['halaman_pdf'] or '-'}) {p['kode']} {p['detail']}"
                  for p in subset] or ["Tidak ada temuan."]
        lines += [""]
    (folder / "LAPORAN_VALIDASI.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


# --------------------------------------------------------------------------- perintah

def extract(args, profile):
    try:
        import pymupdf as fitz
    except ImportError as exc:
        raise ValueError("PyMuPDF belum tersedia. Jalankan: python -m pip install -r requirements.txt") from exc

    pdf = args.pdf.resolve()
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest != profile["source_sha256"] and not args.allow_different_pdf:
        raise ValueError("Fingerprint PDF berbeda dari sumber yang diuji. Periksa profil; "
                         "gunakan --allow-different-pdf hanya setelah menyesuaikan profil.")
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError("Folder keluaran tidak kosong. Pilih folder baru agar hasil sebelumnya tidak tertimpa.")
    if pdf.is_relative_to(out):
        raise ValueError("Simpan PDF di luar folder keluaran.")

    removed, lines, problems, coverage = [], [], [], []
    with fitz.open(pdf) as doc:
        if doc.needs_pass:
            raise ValueError("PDF membutuhkan kata sandi; gunakan salinan yang dapat dibaca.")
        if len(doc) != profile["pdf_pages"] or profile["body_end"] > len(doc):
            raise ValueError("Jumlah halaman tidak sesuai profil.")

        halaman = page_profile(doc, profile)
        for i in range(profile["body_start"] - 1, profile["body_end"]):
            extracted = page_lines(doc[i], i + 1, profile, removed)
            lines.extend(extracted)
            terdeteksi = halaman[i + 1]
            status = "terbaca" if extracted else terdeteksi
            coverage.append(dict(halaman_pdf=i + 1, halaman_cetak=i + 1 - profile["printed_page_offset"],
                                 jumlah_baris=len(extracted), status=status,
                                 catatan_profil=profile.get("reviewed_noncontent_pages", {}).get(str(i + 1), "")))
            if not extracted and terdeteksi == "berisi_teks":
                problems.append(issue("cakupan", "Halaman memuat teks tetapi tidak menghasilkan baris isi.",
                                      {"page": i + 1}))
            elif not extracted:
                problems.append(issue("cakupan", f"Halaman tanpa teks isi ({terdeteksi}).",
                                      {"page": i + 1}, "informasi", "sumber"))
            if (i + 1) % 200 == 0:
                print(f"Membaca halaman {i+1}/{profile['body_end']}...", flush=True)

        problems += check_noncontent_pages(halaman, profile, digest)

        rows, parse_problems, trace = parse_body(lines, profile)
        if not rows:
            raise ValueError("Tidak ada entri terbaca. Periksa PDF teks, font, dan profil halaman.")
        lengkapi_turunan(rows)
        problems += parse_problems
        problems += validate(rows, profile)

        print("Memeriksa daftar isi, rujukan induk-anak, dan pemindaian kolom kode...", flush=True)
        toc = parse_toc(doc, profile)
        toc_report, toc_problems = reconcile_toc(toc, rows)
        child_report, child_problems = reconcile_children(rows)
        scan_report, scan_problems = reconcile_scan(scan_code_column(doc, profile), rows)
        problems += toc_problems + child_problems + scan_problems
        pymupdf_version = fitz.VersionBind

    meta = dict(script_version=VERSION, python_version=platform.python_version(),
                pymupdf_version=pymupdf_version, source_filename=pdf.name, source_sha256=digest,
                profile_matches_source=digest == profile["source_sha256"],
                generated_utc=datetime.now(timezone.utc).isoformat(), profile=profile)
    if not meta["profile_matches_source"]:
        problems.append(issue("metadata", "Fingerprint sumber berbeda; hasil belum tervalidasi untuk dokumen ini."))

    bad = {p["id_entri"] for p in problems if p["id_entri"] and p["keparahan"] in ("error", "peringatan")}
    for r in rows:
        if r["id_entri"] in bad:
            r["status_validasi"] = "perlu_tinjauan_entri"

    write_csv(out / "kbji_2026_hierarki.csv", rows, FIELDS)
    write_csv(out / "kbji_2026_jabatan.csv", [r for r in rows if r["jumlah_digit"] == 6], FIELDS)
    write_csv(out / "kbji_2026_ringkas.csv", rows, RINGKAS_FIELDS)
    write_json(out / "kbji_2026_hierarki.json", rows)
    write_json(out / "kbji_2026_pohon.json", pohon(rows))

    referensi = out / "referensi"
    write_csv(referensi / "daftar_isi.csv", toc,
              ["kode", "nama_daftar_isi", "halaman_cetak", "halaman_pdf_daftar_isi"])
    write_csv(referensi / "tingkat_keterampilan.csv", profile["tingkat_keterampilan"],
              ["golongan_pokok", "nama", "tingkat_keterampilan", "catatan_sumber"])
    write_csv(referensi / "jumlah_acuan_publikasi.csv", acuan_rows(profile),
              ["cakupan", "jumlah_digit", "tingkat", "acuan_publikasi", "rujukan"])

    audit = out / "audit"
    audit.mkdir(parents=True, exist_ok=True)
    with (audit / "baris_sumber.jsonl").open("w", encoding="utf-8") as f:
        for line in trace:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    write_csv(audit / "elemen_dikeluarkan.csv", removed, ["halaman_pdf", "alasan", "teks"])
    write_csv(audit / "cakupan_halaman.csv", coverage,
              ["halaman_pdf", "halaman_cetak", "jumlah_baris", "status", "catatan_profil"])
    write_csv(audit / "rekonsiliasi_daftar_isi.csv", toc_report,
              ["kode", "ada_daftar_isi", "ada_uraian", "nama_daftar_isi", "nama_uraian", "nama_cocok",
               "halaman_cetak_daftar_isi", "halaman_cetak_uraian", "halaman_cocok"])
    write_csv(audit / "rekonsiliasi_anak_induk.csv", child_report,
              ["kode_induk", "jumlah_disebut_di_uraian", "jumlah_judul", "disebut_tanpa_judul", "judul_tanpa_disebut"])
    write_csv(audit / "pindaian_kolom_kode.csv", scan_report,
              ["kode", "terpindai_kolom_kode", "terbaca_sebagai_judul", "halaman_pdf", "jumlah_kemunculan"])
    write_json(out / "metadata.json", meta)

    summary = reports(rows, problems, profile, out / "validasi", meta)
    ringkas = {k: summary[k] for k in ("status_ekstraksi", "status_sumber", "total_entri",
                                       "temuan_ekstraksi", "temuan_sumber", "temuan_informasi")}
    print(json.dumps(ringkas, ensure_ascii=False, indent=2))
    print("Hasil:", out)
    return exit_code(summary)


def acuan_rows(profile):
    acuan = profile["acuan_publikasi"]
    rows = [dict(cakupan="seluruh KBJI 2026", jumlah_digit=d, tingkat=LEVELS[int(d)],
                 acuan_publikasi=v, rujukan=acuan["rujukan_total"])
            for d, v in acuan["jumlah_total"].items()]
    for major, targets in acuan.get("jumlah_per_golongan_pokok", {}).items():
        for d, target in zip([1, 2, 3, 4, 6], targets):
            rows.append(dict(cakupan=f"golongan pokok {major}", jumlah_digit=d, tingkat=LEVELS[d],
                             acuan_publikasi=target,
                             rujukan=acuan["rujukan_per_golongan_pokok"].format(golongan_pokok=major)))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    e = sub.add_parser("extract", help="Ekstrak PDF berdasarkan profil KBJI 2026.")
    e.add_argument("--pdf", required=True, type=Path)
    e.add_argument("--out", required=True, type=Path)
    e.add_argument("--profile", type=Path, default=ROOT / "config/kbji_2026.json")
    e.add_argument("--allow-different-pdf", action="store_true",
                   help="Izinkan hash berbeda; hasil tetap ditandai perlu tinjauan.")
    v = sub.add_parser("validate", help="Periksa ulang struktur CSV; tidak membaca ulang PDF.")
    v.add_argument("--csv", required=True, type=Path)
    v.add_argument("--out", required=True, type=Path)
    v.add_argument("--profile", type=Path, default=ROOT / "config/kbji_2026.json")
    args = parser.parse_args()
    try:
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
        if args.command == "extract":
            return extract(args, profile)
        if args.out.exists() and any(args.out.iterdir()):
            raise ValueError("Folder laporan harus kosong atau baru.")
        rows = read_csv(args.csv)
        problems = validate(rows, profile)
        summary = reports(rows, problems, profile, args.out,
                          {"cakupan": "struktur_csv_saja", "source_csv": args.csv.name})
        print(summary["status_ekstraksi"], "/", summary["status_sumber"], "-", len(problems), "temuan")
        return exit_code(summary)
    except (OSError, ValueError, KeyError) as exc:
        print("GAGAL:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
