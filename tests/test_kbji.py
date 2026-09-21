"""Regresi perilaku penting, tanpa PDF atau koneksi internet."""
import copy
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kbji import (ANCESTOR_COLUMNS, FIELDS, ancestors, check_turunan, exit_code, hitung_status,
                  kelompok_sisa, lengkapi_turunan, nama_pencarian, parent, parse_body, pohon,
                  read_csv, reconcile_children, reconcile_scan, reconcile_toc, validate, write_csv)

PROFILE = dict(
    version="2026", body_start=103, body_end=1108, printed_page_offset=32, code_max_x=85,
    acuan_publikasi=dict(rujukan_total="Tabel 3", jumlah_total={"1": 1, "2": 1, "3": 1, "4": 1, "6": 1}),
    selisih_sumber_terverifikasi=[],
)


def line(text, page=105, x=60, bold=False):
    return dict(text=text, page=page, x=x, y=100, bold=bold, first_bold=bold)


def fixture():
    ls = []
    for code in ["0", "01", "011", "0111", "0111.01"]:
        ls.extend([line(code + " NAMA", bold=True), line('Uraian resmi, dengan "kutipan".', x=134)])
    return lengkapi_turunan(parse_body(ls, PROFILE)[0])


def kategori(problems):
    return {p["kategori"] for p in problems}


class StrukturTests(unittest.TestCase):
    def test_hierarki_kecil_lolos(self):
        self.assertEqual(validate(fixture(), PROFILE), [])

    def test_induk_dan_nol_depan(self):
        self.assertEqual(parent("0111.01"), "0111")
        self.assertEqual(parent("01"), "0")
        self.assertEqual(parent("0"), "")
        self.assertEqual(ancestors("0111.01"), ["0111", "011", "01", "0"])
        self.assertEqual(fixture()[-1]["kode_normalisasi"], "011101")

    def test_judul_multibaris_dan_uraian_lintas_halaman(self):
        ls = [line("0111.01 NAMA", bold=True), line("PANJANG", bold=True, x=134),
              line("Uraian halaman satu.", x=134), line("Lanjutan halaman dua.", page=106, x=117)]
        rows, issues, trace = parse_body(ls, PROFILE)
        self.assertEqual(rows[0]["nama_resmi"], "NAMA PANJANG")
        self.assertEqual(rows[0]["uraian_resmi"], "Uraian halaman satu.\nLanjutan halaman dua.")
        self.assertEqual(rows[0]["halaman_pdf_selesai"], 106)
        self.assertEqual(len(trace), 4)
        self.assertEqual(issues, [])

    def test_kode_dalam_uraian_bukan_judul(self):
        rows, _, _ = parse_body([line("0111.01 NAMA", bold=True),
                                 line("0111 nama dalam daftar, bukan judul.", x=134)], PROFILE)
        self.assertEqual(len(rows), 1)
        self.assertIn("0111 nama", rows[0]["uraian_resmi"])

    def test_pola_judul_salah_tidak_dijadikan_entri(self):
        rows, issues, _ = parse_body([line("0111.001 SALAH", bold=True)], PROFILE)
        self.assertEqual(rows, [])
        self.assertEqual(issues[0]["kategori"], "pola_tidak_terbaca")


class TurunanTests(unittest.TestCase):
    def test_kolom_leluhur_dan_jalur(self):
        row = fixture()[-1]
        self.assertEqual(row["kode_golongan_pokok"], "0")
        self.assertEqual(row["kode_subgolongan_pokok"], "01")
        self.assertEqual(row["kode_golongan"], "011")
        self.assertEqual(row["kode_subgolongan"], "0111")
        self.assertEqual(row["jalur_kode"], "0 > 01 > 011 > 0111 > 0111.01")
        self.assertEqual(row["jalur_nama"], "NAMA > NAMA > NAMA > NAMA > NAMA")
        self.assertEqual(row["kedalaman"], 5)
        self.assertEqual(row["urutan"], 5)

    def test_leluhur_kosong_untuk_tingkat_atas(self):
        row = fixture()[0]
        self.assertEqual(row["kode_golongan_pokok"], "0")
        for cols in list(ANCESTOR_COLUMNS.values())[1:]:
            self.assertEqual(row[cols[0]], "")
            self.assertEqual(row[cols[1]], "")

    def test_hitungan_anak_dan_jabatan(self):
        rows = {r["kode"]: r for r in fixture()}
        self.assertEqual(rows["0111"]["jumlah_anak_langsung"], 1)
        self.assertEqual(rows["0"]["jumlah_jabatan_turunan"], 1)
        self.assertEqual(rows["0111.01"]["jumlah_jabatan_turunan"], 0)

    def test_aturan_kelompok_sisa(self):
        self.assertEqual(kelompok_sisa("2119"), "ya")
        self.assertEqual(kelompok_sisa("219"), "ya")
        self.assertEqual(kelompok_sisa("2111.99"), "ya")
        self.assertEqual(kelompok_sisa("2111.09"), "tidak")
        self.assertEqual(kelompok_sisa("5120"), "tidak")
        self.assertEqual(kelompok_sisa("9"), "tidak")

    def test_nama_pencarian_tidak_mengubah_kolom_resmi(self):
        self.assertEqual(nama_pencarian("AHLI TEKNIK LAINNYA YTDL"), "ahli teknik lainnya ytdl")
        self.assertEqual(nama_pencarian("ARSITEK PERTAMANAN/LANSKAP"), "arsitek pertamanan lanskap")
        rows = fixture()
        self.assertEqual(rows[-1]["nama_resmi"], "NAMA")

    def test_kolom_turunan_yang_diubah_terdeteksi(self):
        rows = fixture()
        rows[-1]["jalur_kode"] = "salah"
        self.assertIn("turunan", kategori(validate(rows, PROFILE)))

    def test_pohon_bersarang(self):
        akar = pohon(fixture())
        self.assertEqual(len(akar), 1)
        node = akar[0]
        for _ in range(4):
            self.assertEqual(len(node["anak"]), 1)
            node = node["anak"][0]
        self.assertEqual(node["kode"], "0111.01")


class ValidasiTests(unittest.TestCase):
    def test_duplikat_dipertahankan(self):
        rows = fixture()
        rows.append(copy.deepcopy(rows[-1]))
        issues = validate(rows, PROFILE)
        self.assertEqual(len([i for i in issues if i["kategori"] == "duplikat"]), 2)
        self.assertEqual(len(rows), 6)

    def test_induk_hilang(self):
        self.assertIn("tanpa_induk", kategori(validate(lengkapi_turunan(fixture()[1:]), PROFILE)))

    def test_nama_kosong(self):
        rows = fixture()
        rows[-1]["nama_resmi"] = ""
        self.assertIn("nama_kosong", kategori(validate(rows, PROFILE)))

    def test_uraian_kosong(self):
        rows = fixture()
        rows[-1]["uraian_resmi"] = ""
        self.assertIn("uraian_kosong", kategori(validate(rows, PROFILE)))

    def test_kode_dan_halaman_tidak_valid(self):
        rows = fixture()
        rows[-1]["halaman_pdf_selesai"] = 99
        self.assertIn("halaman", kategori(validate(rows, PROFILE)))
        rows[-1]["kode"] = "01110"
        self.assertIn("format_kode", kategori(validate(rows, PROFILE)))

    def test_selisih_jumlah_tidak_diisi_buatan(self):
        rows = fixture()
        profile = copy.deepcopy(PROFILE)
        profile["acuan_publikasi"]["jumlah_total"]["6"] = 2
        issues = [i for i in validate(rows, profile) if i["kategori"] == "jumlah_tidak_sesuai"]
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["kelas"], "ekstraksi")
        self.assertEqual(issues[0]["keparahan"], "error")
        self.assertEqual(len(rows), 5)

    def test_selisih_terverifikasi_ditandai_sebagai_temuan_sumber(self):
        rows = fixture()
        profile = copy.deepcopy(PROFILE)
        profile["acuan_publikasi"]["jumlah_total"]["6"] = 2
        profile["selisih_sumber_terverifikasi"] = [dict(tingkat_digit=6, golongan_pokok="",
                                                        acuan_publikasi=2, hasil_terverifikasi=1,
                                                        bukti="Bukti uji.")]
        issues = [i for i in validate(rows, profile) if i["kategori"] == "jumlah_tidak_sesuai"]
        self.assertEqual(issues[0]["kelas"], "sumber")
        self.assertEqual(issues[0]["keparahan"], "peringatan")
        status = hitung_status(issues)
        self.assertEqual(status["status_ekstraksi"], "LENGKAP_DAN_KONSISTEN")
        self.assertEqual(exit_code(status), 3)

    def test_kode_status_keluaran(self):
        self.assertEqual(exit_code(hitung_status([])), 0)
        cacat = [dict(kategori="hierarki", kelas="ekstraksi", keparahan="error")]
        self.assertEqual(exit_code(hitung_status(cacat)), 2)


class RekonsiliasiTests(unittest.TestCase):
    def test_daftar_isi_nama_dan_halaman(self):
        rows = fixture()
        toc = [dict(kode=r["kode"], nama_daftar_isi=r["nama_resmi"],
                    halaman_cetak=r["halaman_cetak_mulai"], halaman_pdf_daftar_isi=11)
               for r in rows if r["jumlah_digit"] < 6]
        self.assertEqual(reconcile_toc(toc, rows)[1], [])
        toc[3]["nama_daftar_isi"] = "NAMA LAIN"
        toc[2]["halaman_cetak"] = 999
        cats = kategori(reconcile_toc(toc, rows)[1])
        self.assertEqual(cats, {"nama_daftar_isi", "halaman_daftar_isi"})

    def test_daftar_isi_kode_hilang(self):
        rows = fixture()
        self.assertIn("daftar_isi", kategori(reconcile_toc([], rows)[1]))

    def test_pindaian_kolom_kode_menemukan_judul_terlewat(self):
        rows = fixture()
        scan = {r["kode"]: dict(kode=r["kode"], halaman_pdf=105, jumlah=1) for r in rows}
        self.assertEqual(reconcile_scan(scan, rows)[1], [])
        scan["0112"] = dict(kode="0112", halaman_pdf=120, jumlah=1)
        problems = reconcile_scan(scan, rows)[1]
        self.assertEqual(kategori(problems), {"kelengkapan_kode"})
        self.assertIn("0112", problems[0]["detail"])

    def test_anak_disebut_tanpa_judul(self):
        rows = fixture()
        by = {r["kode"]: r for r in rows}
        by["011"]["uraian_resmi"] += "\n0111 Nama anak\n0112 Anak yang hilang"
        report, problems = reconcile_children(rows)
        self.assertEqual(kategori(problems), {"anak_induk"})
        self.assertIn("0112", problems[0]["detail"])
        self.assertTrue(any(r["kode_induk"] == "011" for r in report))


class BerkasTests(unittest.TestCase):
    def test_csv_roundtrip_nol_depan_kutipan_newline(self):
        rows = fixture()
        rows[-1]["uraian_resmi"] += "\nBaris kedua."
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "uji.csv"
            write_csv(path, rows, FIELDS)
            loaded = read_csv(path)
        self.assertEqual(loaded[-1]["kode"], "0111.01")
        self.assertEqual(loaded[-1]["kode_normalisasi"], "011101")
        self.assertEqual(loaded[-1]["uraian_resmi"], rows[-1]["uraian_resmi"])
        self.assertEqual(loaded[-1]["jalur_kode"], "0 > 01 > 011 > 0111 > 0111.01")
        self.assertEqual(validate(loaded, PROFILE), [])

    def test_kolom_wajib_diperiksa(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "kurang.csv"
            write_csv(path, fixture(), [f for f in FIELDS if f != "jalur_kode"])
            with self.assertRaises(ValueError):
                read_csv(path)


if __name__ == "__main__":
    unittest.main()
