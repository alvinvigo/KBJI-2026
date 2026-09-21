#!/usr/bin/env python3
"""Ubah keluaran `kbji.py extract` menjadi berkas statis untuk Cloudflare Workers.

Tidak mengubah isi apa pun. Hanya memecah data agar dapat disajikan sebagai
berkas statis kecil tanpa basis data.

    python web/bangun_data.py --out ../output --data web/public/data
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
# Kolom yang dikirim ke peramban pada berkas rincian.
DETAIL_FIELDS = [
    "kode", "kode_normalisasi", "jumlah_digit", "tingkat", "kedalaman", "urutan", "kode_induk",
    "nama_resmi", "uraian_resmi", "jalur_kode", "jalur_nama",
    "kode_golongan_pokok", "nama_golongan_pokok", "kode_subgolongan_pokok", "nama_subgolongan_pokok",
    "kode_golongan", "nama_golongan", "kode_subgolongan", "nama_subgolongan",
    "jumlah_anak_langsung", "jumlah_jabatan_turunan", "kelompok_sisa",
    "halaman_pdf_mulai", "halaman_pdf_selesai", "halaman_cetak_mulai", "halaman_cetak_selesai",
    "status_validasi",
]
INT_FIELDS = {"jumlah_digit", "kedalaman", "urutan", "jumlah_anak_langsung", "jumlah_jabatan_turunan",
              "halaman_pdf_mulai", "halaman_pdf_selesai", "halaman_cetak_mulai", "halaman_cetak_selesai"}


def baca_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def tulis(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path.stat().st_size


def blok_untuk(kode):
    """Nama berkas blok yang memuat rincian sebuah kode."""
    inti = kode.replace(".", "")
    if len(inti) <= 3:
        return "gp" + inti[0]
    return inti[:4]


def rincian(row):
    out = {}
    for f in DETAIL_FIELDS:
        nilai = row[f]
        out[f] = int(nilai) if f in INT_FIELDS and str(nilai).strip() else nilai
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=ROOT.parent / "output", help="Folder hasil ekstraksi.")
    p.add_argument("--data", type=Path, default=ROOT / "public/data", help="Folder tujuan berkas statis.")
    args = p.parse_args()

    sumber, tujuan = args.out.resolve(), args.data.resolve()
    rows = baca_csv(sumber / "kbji_2026_hierarki.csv")
    meta = json.loads((sumber / "metadata.json").read_text(encoding="utf-8"))
    ringkasan = json.loads((sumber / "validasi" / "ringkasan.json").read_text(encoding="utf-8"))
    profil = meta["profile"]

    if tujuan.exists():
        shutil.rmtree(tujuan)
    tujuan.mkdir(parents=True)

    # Indeks ringkas: satu larik per entri, dipakai untuk pencarian dan penelusuran di peramban.
    # Urutan kolom: kode, nama, jumlah_digit, halaman_cetak_mulai, kelompok_sisa(0/1)
    indeks = [[r["kode"], r["nama_resmi"], int(r["jumlah_digit"]), int(r["halaman_cetak_mulai"]),
               1 if r["kelompok_sisa"] == "ya" else 0] for r in rows]
    ukuran_indeks = tulis(tujuan / "indeks.json",
                          {"kolom": ["kode", "nama", "jumlah_digit", "halaman_cetak", "kelompok_sisa"],
                           "entri": indeks})

    # Blok rincian. Tingkat 1-3 dikelompokkan per golongan pokok; tingkat 4 dan 6 per subgolongan.
    blok = {}
    for r in rows:
        blok.setdefault(blok_untuk(r["kode"]), []).append(rincian(r))
    total_blok = 0
    for nama, isi in blok.items():
        total_blok += tulis(tujuan / "blok" / f"{nama}.json", isi)

    selisih = {(str(d["tingkat_digit"]), d.get("golongan_pokok", "")): d
               for d in profil.get("selisih_sumber_terverifikasi", [])}
    meta_web = {
        "publikasi": profil["publikasi"],
        "penerbit": profil["penerbit"],
        "katalog": profil["katalog"],
        "nomor_publikasi": profil["nomor_publikasi"],
        "versi_kbji": profil["version"],
        "sumber_sha256": meta["source_sha256"],
        "halaman_pdf": profil["pdf_pages"],
        "versi_alat": meta["script_version"],
        "versi_pymupdf": meta["pymupdf_version"],
        "diproses_utc": meta["generated_utc"],
        "status_ekstraksi": ringkasan["status_ekstraksi"],
        "status_sumber": ringkasan["status_sumber"],
        "total_entri": ringkasan["total_entri"],
        "jumlah_per_tingkat": ringkasan["jumlah_per_tingkat"],
        "selisih_sumber_terverifikasi": list(selisih.values()),
        "tingkat_keterampilan": profil["tingkat_keterampilan"],
        "rujukan_tingkat_keterampilan": profil["rujukan_tingkat_keterampilan"],
    }
    ukuran_meta = tulis(tujuan / "meta.json", meta_web)

    print(f"indeks.json   {ukuran_indeks/1024:8.1f} KB  ({len(indeks)} entri)")
    print(f"meta.json     {ukuran_meta/1024:8.1f} KB")
    print(f"blok/*.json   {total_blok/1024:8.1f} KB  ({len(blok)} berkas)")
    print(f"total         {(ukuran_indeks+ukuran_meta+total_blok)/1024/1024:8.2f} MB")
    print("tujuan:", tujuan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
