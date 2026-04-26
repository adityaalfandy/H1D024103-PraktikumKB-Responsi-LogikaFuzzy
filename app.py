"""
==========================================================
 SISTEM FUZZY MAMDANI - DETEKSI KECURIGAAN TRANSAKSI BANK
==========================================================
 Mata Kuliah : Kecerdasan Buatan
 Metode      : Fuzzy Logic Mamdani
 Deskripsi   : Mendeteksi tingkat kecurigaan transaksi
               rekening bank berpotensi judi online
               berdasarkan pola transaksi.

 Variabel Input:
   1. Frekuensi Transfer per Hari (0 - 20 kali)
   2. Total Nominal Transfer per Hari (0 - 5.000.000 Rp)
   3. Waktu Transaksi (0 - 24 jam)

 Variabel Output:
   - Tingkat Kecurigaan Transaksi (0 - 100)
     Kategori: Rendah | Sedang | Tinggi

 Tahapan:
   1. Fuzzifikasi   → Hitung nilai keanggotaan input
   2. Inferensi     → Evaluasi semua rule (MIN untuk AND)
   3. Agregasi      → Gabungkan hasil rule (MAX)
   4. Defuzzifikasi → Centroid (Center of Gravity)
==========================================================
"""

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# ============================================================
#  FUNGSI KEANGGOTAAN SEGITIGA (Triangular Membership Function)
# ============================================================

def trimf(x, a, b, c):
    """
    Fungsi keanggotaan Segitiga (Triangular / trimf)

    Bentuk:
          1 |      /\\
            |     /  \\
            |    /    \\
          0 |___/______\\___
                a    b    c

    Parameters:
        x (float): Nilai crisp input
        a (float): Titik kiri  → μ = 0 (awal naik)
        b (float): Titik puncak → μ = 1 (nilai tertinggi)
        c (float): Titik kanan → μ = 0 (akhir turun)

    Returns:
        float: Nilai keanggotaan μ ∈ [0, 1]

    Kasus Khusus:
        - Jika a == b (shoulder kiri): fungsi turun dari 1 ke 0
        - Jika b == c (shoulder kanan): fungsi naik dari 0 ke 1
    """
    # Jika x di luar range [a, c], keanggotaan = 0
    if x < a or x > c:
        return 0.0

    # Sisi kiri: dari a menuju puncak b
    if a <= x <= b:
        if b == a:
            return 1.0  # shoulder kiri: langsung puncak
        return (x - a) / (b - a)

    # Sisi kanan: dari puncak b turun ke c
    else:  # b < x <= c
        if c == b:
            return 1.0  # shoulder kanan: langsung puncak
        return (c - x) / (c - b)


# ============================================================
#  TAHAP 1: FUZZIFIKASI INPUT
# ============================================================

def fuzzifikasi_frekuensi(frekuensi):
    """
    Fuzzifikasi variabel: Frekuensi Transfer per Hari

    Range  : 0 – 20 kali/hari
    Fungsi : Triangular (trimf)

    Himpunan Fuzzy:
      ┌─────────┬──────────────────────────────────────────┐
      │ Rendah  │ trimf(x, 0, 0, 5)   → puncak di x = 0   │
      │ Sedang  │ trimf(x, 3, 7.5, 12)→ puncak di x = 7.5 │
      │ Tinggi  │ trimf(x, 10, 20, 20)→ puncak di x = 20  │
      └─────────┴──────────────────────────────────────────┘

    Visualisasi:
    μ
    1|*                      Tinggi→        *
     |  *      Sedang→    *   *           *
     |    *      *      *       *       *
     |      *  *          *       *   *
    0|________________________________________
    0        5    7.5     12    17  20

    Args:
        frekuensi (float): Jumlah transfer per hari

    Returns:
        dict: Nilai keanggotaan {rendah, sedang, tinggi}
    """
    rendah = trimf(frekuensi, 0, 0, 5)
    sedang = trimf(frekuensi, 3, 7.5, 12)
    tinggi = trimf(frekuensi, 10, 20, 20)

    return {
        'rendah': round(rendah, 4),
        'sedang': round(sedang, 4),
        'tinggi': round(tinggi, 4)
    }


def fuzzifikasi_nominal(nominal):
    """
    Fuzzifikasi variabel: Total Nominal Transfer per Hari

    Range  : 0 – 5.000.000 rupiah
    Fungsi : Triangular (trimf)

    Himpunan Fuzzy:
      ┌────────┬────────────────────────────────────────────────────┐
      │ Kecil  │ trimf(x, 0, 0, 1_500_000)    → puncak di x = 0    │
      │ Sedang │ trimf(x, 1_000_000, 2_250_000, 3_500_000)          │
      │ Besar  │ trimf(x, 3_000_000, 5_000_000, 5_000_000)          │
      └────────┴────────────────────────────────────────────────────┘

    Args:
        nominal (float): Total nominal transfer dalam rupiah

    Returns:
        dict: Nilai keanggotaan {kecil, sedang, besar}
    """
    kecil  = trimf(nominal, 0,         0,         1_500_000)
    sedang = trimf(nominal, 1_000_000, 2_250_000, 3_500_000)
    besar  = trimf(nominal, 3_000_000, 5_000_000, 5_000_000)

    return {
        'kecil':  round(kecil,  4),
        'sedang': round(sedang, 4),
        'besar':  round(besar,  4)
    }


def fuzzifikasi_waktu(jam):
    """
    Fuzzifikasi variabel: Waktu Transaksi

    Range  : 0 – 24 jam
    Fungsi : Triangular (trimf) + wrap-around untuk Larut Malam

    Himpunan Fuzzy:
      ┌─────────────┬────────────────────────────────────────────┐
      │ Siang       │ trimf(x,  8, 12.5, 17) → puncak 12.5     │
      │ Malam       │ trimf(x, 17, 19.5, 22) → puncak 19.5     │
      │ Larut Malam │ Jam 22–24: naik (22→24), Jam 00–05: turun │
      └─────────────┴────────────────────────────────────────────┘

    Larut Malam (22–05 melewati tengah malam):
        ┌─────────────────────────────────────────────┐
        │  Jika 22 ≤ jam ≤ 24: μ = (jam - 22) / 2    │
        │  Jika  0 ≤ jam ≤  5: μ = (5 - jam) / 5     │
        │  Selain itu         : μ = 0                  │
        └─────────────────────────────────────────────┘
        → Puncak μ = 1 terjadi di jam 24/00 (tengah malam)

    Args:
        jam (float): Jam transaksi (0–24)

    Returns:
        dict: Nilai keanggotaan {siang, malam, larut_malam}
    """
    siang = trimf(jam, 8.0, 12.5, 17.0)
    malam = trimf(jam, 17.0, 19.5, 22.0)

    # Larut Malam: wrap-around melewati tengah malam
    if 22.0 <= jam <= 24.0:
        # Keanggotaan naik linear dari 22 (μ=0) ke 24 (μ=1)
        larut_malam = (jam - 22.0) / (24.0 - 22.0)
    elif 0.0 <= jam <= 5.0:
        # Keanggotaan turun linear dari 0/24 (μ=1) ke 5 (μ=0)
        larut_malam = (5.0 - jam) / (5.0 - 0.0)
    else:
        larut_malam = 0.0

    return {
        'siang':       round(siang,       4),
        'malam':       round(malam,       4),
        'larut_malam': round(larut_malam, 4)
    }


# ============================================================
#  FUNGSI KEANGGOTAAN OUTPUT
# ============================================================

def mf_output_rendah(x):
    """
    MF Output: Tingkat Kecurigaan RENDAH
    trimf(x, 0, 0, 40) → puncak di x = 0, nol di x = 40
    """
    return trimf(x, 0.0, 0.0, 40.0)


def mf_output_sedang(x):
    """
    MF Output: Tingkat Kecurigaan SEDANG
    trimf(x, 30, 50, 70) → puncak simetris di x = 50
    """
    return trimf(x, 30.0, 50.0, 70.0)


def mf_output_tinggi(x):
    """
    MF Output: Tingkat Kecurigaan TINGGI
    trimf(x, 60, 100, 100) → puncak di x = 100, nol di x = 60
    """
    return trimf(x, 60.0, 100.0, 100.0)


# ============================================================
#  TAHAP 2: EVALUASI RULE (Inferensi Mamdani)
# ============================================================

def evaluasi_rule(mf_frekuensi, mf_nominal, mf_waktu):
    """
    Evaluasi semua rule fuzzy (Base of Rules / Rule Base)

    Metode Inferensi  : Mamdani
    Operator AND      : MIN (ambil nilai minimum dari antecedents)
    Operator Agregasi : MAX (per kategori output)

    ╔════╦═══════════════════════════════════════════════════╦═════════╗
    ║ ID ║ ANTECEDENT (IF)                                   ║ KONSEKUEN║
    ╠════╬═══════════════════════════════════════════════════╬═════════╣
    ║ R1 ║ Frekuensi Tinggi  AND Nominal Besar  AND Larut ★  ║ TINGGI  ║
    ║ R2 ║ Frekuensi Sedang  AND Nominal Sedang AND Malam    ║ SEDANG  ║
    ║ R3 ║ Frekuensi Rendah  AND Nominal Kecil               ║ RENDAH  ║
    ║ R4 ║ Frekuensi Tinggi  AND Nominal Besar               ║ TINGGI  ║
    ║ R5 ║ Frekuensi Tinggi  AND Nominal Sedang              ║ SEDANG  ║
    ║ R6 ║ Frekuensi Sedang  AND Nominal Besar               ║ TINGGI  ║
    ║ R7 ║ Frekuensi Sedang  AND Nominal Kecil               ║ RENDAH  ║
    ║ R8 ║ Frekuensi Rendah  AND Nominal Sedang              ║ RENDAH  ║
    ║ R9 ║ Frekuensi Tinggi  AND Waktu Larut Malam ★         ║ TINGGI  ║
    ║ R10║ Frekuensi Rendah  AND Nominal Besar               ║ SEDANG  ║
    ║ R11║ Frekuensi Tinggi  AND Waktu Malam                 ║ SEDANG  ║
    ║ R12║ Frekuensi Sedang  AND Waktu Larut Malam ★         ║ SEDANG  ║
    ╚════╩═══════════════════════════════════════════════════╩═════════╝
    ★ = rule khusus berkaitan waktu larut malam (indikator kuat judi online)

    Args:
        mf_frekuensi (dict): Output fuzzifikasi_frekuensi()
        mf_nominal   (dict): Output fuzzifikasi_nominal()
        mf_waktu     (dict): Output fuzzifikasi_waktu()

    Returns:
        dict: {rules: [...], alpha: {rendah, sedang, tinggi}}
    """
    f = mf_frekuensi
    n = mf_nominal
    w = mf_waktu

    # ---- Definisi Rule Base ----
    rule_base = [
        # ID, Deskripsi rule, Firing strength, Konsekuen
        {
            'id': 'R1',
            'deskripsi': 'Frekuensi Tinggi AND Nominal Besar AND Waktu Larut Malam',
            'detail':    f"min({f['tinggi']}, {n['besar']}, {w['larut_malam']})",
            'firing':    min(f['tinggi'],  n['besar'],  w['larut_malam']),
            'konsekuen': 'tinggi',
            'label':     'TINGGI'
        },
        {
            'id': 'R2',
            'deskripsi': 'Frekuensi Sedang AND Nominal Sedang AND Waktu Malam',
            'detail':    f"min({f['sedang']}, {n['sedang']}, {w['malam']})",
            'firing':    min(f['sedang'],  n['sedang'], w['malam']),
            'konsekuen': 'sedang',
            'label':     'SEDANG'
        },
        {
            'id': 'R3',
            'deskripsi': 'Frekuensi Rendah AND Nominal Kecil',
            'detail':    f"min({f['rendah']}, {n['kecil']})",
            'firing':    min(f['rendah'],  n['kecil']),
            'konsekuen': 'rendah',
            'label':     'RENDAH'
        },
        {
            'id': 'R4',
            'deskripsi': 'Frekuensi Tinggi AND Nominal Besar',
            'detail':    f"min({f['tinggi']}, {n['besar']})",
            'firing':    min(f['tinggi'],  n['besar']),
            'konsekuen': 'tinggi',
            'label':     'TINGGI'
        },
        {
            'id': 'R5',
            'deskripsi': 'Frekuensi Tinggi AND Nominal Sedang',
            'detail':    f"min({f['tinggi']}, {n['sedang']})",
            'firing':    min(f['tinggi'],  n['sedang']),
            'konsekuen': 'sedang',
            'label':     'SEDANG'
        },
        {
            'id': 'R6',
            'deskripsi': 'Frekuensi Sedang AND Nominal Besar',
            'detail':    f"min({f['sedang']}, {n['besar']})",
            'firing':    min(f['sedang'],  n['besar']),
            'konsekuen': 'tinggi',
            'label':     'TINGGI'
        },
        {
            'id': 'R7',
            'deskripsi': 'Frekuensi Sedang AND Nominal Kecil',
            'detail':    f"min({f['sedang']}, {n['kecil']})",
            'firing':    min(f['sedang'],  n['kecil']),
            'konsekuen': 'rendah',
            'label':     'RENDAH'
        },
        {
            'id': 'R8',
            'deskripsi': 'Frekuensi Rendah AND Nominal Sedang',
            'detail':    f"min({f['rendah']}, {n['sedang']})",
            'firing':    min(f['rendah'],  n['sedang']),
            'konsekuen': 'rendah',
            'label':     'RENDAH'
        },
        {
            'id': 'R9',
            'deskripsi': 'Frekuensi Tinggi AND Waktu Larut Malam',
            'detail':    f"min({f['tinggi']}, {w['larut_malam']})",
            'firing':    min(f['tinggi'],  w['larut_malam']),
            'konsekuen': 'tinggi',
            'label':     'TINGGI'
        },
        {
            'id': 'R10',
            'deskripsi': 'Frekuensi Rendah AND Nominal Besar',
            'detail':    f"min({f['rendah']}, {n['besar']})",
            'firing':    min(f['rendah'],  n['besar']),
            'konsekuen': 'sedang',
            'label':     'SEDANG'
        },
        {
            'id': 'R11',
            'deskripsi': 'Frekuensi Tinggi AND Waktu Malam',
            'detail':    f"min({f['tinggi']}, {w['malam']})",
            'firing':    min(f['tinggi'],  w['malam']),
            'konsekuen': 'sedang',
            'label':     'SEDANG'
        },
        {
            'id': 'R12',
            'deskripsi': 'Frekuensi Sedang AND Waktu Larut Malam',
            'detail':    f"min({f['sedang']}, {w['larut_malam']})",
            'firing':    min(f['sedang'],  w['larut_malam']),
            'konsekuen': 'sedang',
            'label':     'SEDANG'
        },
    ]

    # Bulatkan firing strength
    for r in rule_base:
        r['firing'] = round(r['firing'], 4)

    # ---- Agregasi per Kategori Output (Operator MAX) ----
    # Ambil nilai firing strength tertinggi dari setiap kategori
    alpha_rendah = max(r['firing'] for r in rule_base if r['konsekuen'] == 'rendah')
    alpha_sedang = max(r['firing'] for r in rule_base if r['konsekuen'] == 'sedang')
    alpha_tinggi = max(r['firing'] for r in rule_base if r['konsekuen'] == 'tinggi')

    return {
        'rules': rule_base,
        'alpha': {
            'rendah': round(alpha_rendah, 4),
            'sedang': round(alpha_sedang, 4),
            'tinggi': round(alpha_tinggi, 4)
        }
    }


# ============================================================
#  TAHAP 3: DEFUZZIFIKASI (Centroid / Center of Gravity)
# ============================================================

def defuzzifikasi(alpha_rendah, alpha_sedang, alpha_tinggi, n_points=500):
    """
    Defuzzifikasi menggunakan Metode Centroid (Center of Gravity / CoG)

    Prinsip:
      Setelah semua rule dievaluasi dan diagregasi, kita memiliki
      sebuah fungsi keanggotaan output gabungan (aggregated MF).
      Centroid menghitung titik berat dari area fungsi tersebut.

    Langkah-langkah:
      1. Diskretisasi domain output [0, 100] menjadi n_points titik
      2. Untuk setiap titik x, hitung μ_clipped untuk tiap kategori:
             μ_rendah_clip(x) = min(alpha_rendah, mf_output_rendah(x))
             μ_sedang_clip(x) = min(alpha_sedang, mf_output_sedang(x))
             μ_tinggi_clip(x) = min(alpha_tinggi, mf_output_tinggi(x))
      3. Agregasi (MAX): μ_agg(x) = max(μ_rendah_clip, μ_sedang_clip, μ_tinggi_clip)
      4. Hitung centroid:
                    Σ [ x_i × μ_agg(x_i) ]
             z* = ─────────────────────────
                       Σ [ μ_agg(x_i) ]

    Args:
        alpha_rendah (float): Firing strength output Rendah
        alpha_sedang (float): Firing strength output Sedang
        alpha_tinggi (float): Firing strength output Tinggi
        n_points     (int)  : Jumlah titik diskretisasi (default 500)

    Returns:
        tuple: (centroid_value, aggregated_points_list)
    """
    step = 100.0 / n_points
    numerator   = 0.0  # Σ [ x_i × μ_agg(x_i) ]
    denominator = 0.0  # Σ [ μ_agg(x_i) ]

    aggregated_points  = []  # Semua titik untuk visualisasi
    clipped_rendah_pts = []
    clipped_sedang_pts = []
    clipped_tinggi_pts = []

    for i in range(n_points + 1):
        x = i * step  # Nilai crisp output (0..100)

        # --- Clip setiap output MF dengan alpha (firing strength) ---
        mu_r = min(alpha_rendah, mf_output_rendah(x))
        mu_s = min(alpha_sedang, mf_output_sedang(x))
        mu_t = min(alpha_tinggi, mf_output_tinggi(x))

        # --- Agregasi MAX ---
        mu_agg = max(mu_r, mu_s, mu_t)

        # Akumulasi untuk rumus centroid
        numerator   += x * mu_agg
        denominator += mu_agg

        # Simpan titik untuk visualisasi (ambil setiap 5 titik saja)
        if i % 5 == 0:
            aggregated_points.append( {'x': round(x, 1), 'y': round(mu_agg, 4)})
            clipped_rendah_pts.append({'x': round(x, 1), 'y': round(mu_r,   4)})
            clipped_sedang_pts.append({'x': round(x, 1), 'y': round(mu_s,   4)})
            clipped_tinggi_pts.append({'x': round(x, 1), 'y': round(mu_t,   4)})

    # Centroid: hindari pembagian nol
    centroid = round(numerator / denominator, 2) if denominator > 0 else 0.0

    return centroid, {
        'aggregated':  aggregated_points,
        'rendah':      clipped_rendah_pts,
        'sedang':      clipped_sedang_pts,
        'tinggi':      clipped_tinggi_pts,
        'numerator':   round(numerator,   4),
        'denominator': round(denominator, 4)
    }


# ============================================================
#  TAHAP 4: TAMPILKAN HASIL
# ============================================================

def tampilkan_hasil(nilai_kecurigaan):
    """
    Menentukan kategori akhir berdasarkan nilai kecurigaan crisp.

    Batas Kategori:
      ┌─────────┬────────────┬───────────────────────────────┐
      │ Rendah  │   0 – 40   │ Transaksi normal / wajar      │
      │ Sedang  │  30 – 70   │ Perlu dipantau lebih lanjut   │
      │ Tinggi  │  60 – 100  │ Sangat mencurigakan!          │
      └─────────┴────────────┴───────────────────────────────┘

    Catatan: Ambang batas pengambilan keputusan:
      - nilai < 40  → Rendah
      - 40 ≤ nilai < 65 → Sedang
      - nilai ≥ 65  → Tinggi

    Args:
        nilai_kecurigaan (float): Nilai crisp hasil defuzzifikasi

    Returns:
        dict: {nilai, kategori, warna, deskripsi}
    """
    if nilai_kecurigaan < 40.0:
        return {
            'nilai':     nilai_kecurigaan,
            'kategori':  'Rendah',
            'warna':     '#00ff88',
            'ikon':      '✔',
            'deskripsi': 'Pola transaksi tergolong normal. Tidak ada indikasi kuat aktivitas mencurigakan.'
        }
    elif nilai_kecurigaan < 65.0:
        return {
            'nilai':     nilai_kecurigaan,
            'kategori':  'Sedang',
            'warna':     '#ffaa00',
            'ikon':      '⚠',
            'deskripsi': 'Pola transaksi perlu dipantau. Beberapa parameter menunjukkan potensi aktivitas tidak wajar.'
        }
    else:
        return {
            'nilai':     nilai_kecurigaan,
            'kategori':  'Tinggi',
            'warna':     '#ff3131',
            'ikon':      '✘',
            'deskripsi': 'Pola transaksi sangat mencurigakan! Diindikasikan kuat terkait aktivitas judi online.'
        }


# ============================================================
#  HELPER: Data MF untuk Visualisasi Grafik Input
# ============================================================

def get_mf_chart_data():
    """
    Generate data titik-titik fungsi keanggotaan untuk setiap
    variabel input dan output (digunakan oleh JavaScript chart).
    """
    # Frekuensi (0-20, step 0.2)
    freq_x    = [round(i * 0.2, 1) for i in range(101)]
    freq_r    = [trimf(x, 0,  0,  5  ) if x > 0 else 1.0 for x in freq_x]
    freq_s    = [trimf(x, 3,  7.5,12  ) for x in freq_x]
    freq_t    = [trimf(x, 10, 20, 20  ) for x in freq_x]

    # Nominal (0-5.000.000, step 50.000)
    nom_x     = [round(i * 50000, 0) for i in range(101)]
    nom_k     = [trimf(x, 0,       0,         1500000) if x > 0 else 1.0 for x in nom_x]
    nom_s     = [trimf(x, 1000000, 2250000,   3500000) for x in nom_x]
    nom_b     = [trimf(x, 3000000, 5000000,   5000000) for x in nom_x]

    # Waktu (0-24, step 0.24)
    waktu_x   = [round(i * 0.24, 2) for i in range(101)]
    waktu_si  = [trimf(x, 8,  12.5, 17  ) for x in waktu_x]
    waktu_ma  = [trimf(x, 17, 19.5, 22  ) for x in waktu_x]
    waktu_la  = []
    for x in waktu_x:
        if 22.0 <= x <= 24.0:
            waktu_la.append(round((x - 22.0) / 2.0, 4))
        elif 0.0 <= x <= 5.0:
            waktu_la.append(round((5.0 - x) / 5.0, 4))
        else:
            waktu_la.append(0.0)

    # Output (0-100, step 1)
    out_x     = list(range(101))
    out_r     = [mf_output_rendah(x) for x in out_x]
    out_s     = [mf_output_sedang(x) for x in out_x]
    out_t     = [mf_output_tinggi(x) for x in out_x]

    return {
        'frekuensi': {'x': freq_x,  'rendah': freq_r, 'sedang': freq_s, 'tinggi': freq_t},
        'nominal':   {'x': nom_x,   'kecil':  nom_k,  'sedang': nom_s,  'besar':  nom_b},
        'waktu':     {'x': waktu_x, 'siang':  waktu_si,'malam': waktu_ma,'larut': waktu_la},
        'output':    {'x': out_x,   'rendah': out_r,   'sedang': out_s,  'tinggi': out_t}
    }


# ============================================================
#  FLASK ROUTES
# ============================================================

@app.route('/')
def index():
    """Halaman utama: kirim data MF untuk grafik statis."""
    mf_data = get_mf_chart_data()
    return render_template('index.html', mf_data=mf_data)


@app.route('/hitung', methods=['POST'])
def hitung():
    """
    Endpoint API: terima input JSON, proses fuzzy, kembalikan hasil.

    Request Body (JSON):
        {
          "frekuensi": <float>,   // 0-20
          "nominal":   <float>,   // 0-5000000
          "jam":       <float>    // 0-24
        }

    Response (JSON):
        {
          "input":         {...},
          "fuzzifikasi":   {...},
          "rules":         [...],
          "alpha":         {...},
          "defuzzifikasi": {...},
          "hasil":         {...}
        }
    """
    try:
        data      = request.get_json()
        frekuensi = float(data['frekuensi'])
        nominal   = float(data['nominal'])
        jam       = float(data['jam'])

        # --- Validasi Range Input ---
        if not (0 <= frekuensi <= 20):
            return jsonify({'error': 'Frekuensi harus antara 0 – 20 kali/hari'}), 400
        if not (0 <= nominal <= 5_000_000):
            return jsonify({'error': 'Nominal harus antara Rp0 – Rp5.000.000'}), 400
        if not (0 <= jam <= 24):
            return jsonify({'error': 'Jam harus antara 0 – 24'}), 400

        # ============================
        # STEP 1: FUZZIFIKASI
        # ============================
        mf_frek  = fuzzifikasi_frekuensi(frekuensi)
        mf_nom   = fuzzifikasi_nominal(nominal)
        mf_wkt   = fuzzifikasi_waktu(jam)

        # ============================
        # STEP 2: EVALUASI RULE
        # ============================
        hasil_rule = evaluasi_rule(mf_frek, mf_nom, mf_wkt)

        # ============================
        # STEP 3: DEFUZZIFIKASI
        # ============================
        alpha = hasil_rule['alpha']
        centroid, defu_data = defuzzifikasi(
            alpha['rendah'], alpha['sedang'], alpha['tinggi']
        )

        # ============================
        # STEP 4: TAMPILKAN HASIL
        # ============================
        hasil_akhir = tampilkan_hasil(centroid)

        return jsonify({
            'input': {
                'frekuensi': frekuensi,
                'nominal':   nominal,
                'jam':       jam
            },
            'fuzzifikasi': {
                'frekuensi': mf_frek,
                'nominal':   mf_nom,
                'waktu':     mf_wkt
            },
            'rules':  hasil_rule['rules'],
            'alpha':  hasil_rule['alpha'],
            'defuzzifikasi': {
                'centroid':    centroid,
                'numerator':   defu_data['numerator'],
                'denominator': defu_data['denominator'],
                'points': {
                    'aggregated': defu_data['aggregated'],
                    'rendah':     defu_data['rendah'],
                    'sedang':     defu_data['sedang'],
                    'tinggi':     defu_data['tinggi']
                }
            },
            'hasil': hasil_akhir
        })

    except (KeyError, TypeError, ValueError) as e:
        return jsonify({'error': f'Input tidak valid: {str(e)}'}), 400


# ============================================================
#  CONTOH PENGGUNAAN (dijalankan langsung tanpa Flask)
# ============================================================

def contoh_penggunaan():
    """
    Contoh perhitungan manual sistem fuzzy.

    Contoh Input:
        Frekuensi : 15 kali/hari   (tinggi)
        Nominal   : 4.000.000 Rp  (besar)
        Jam       : 23.00          (larut malam)

    Expected Output:
        Kecurigaan: Tinggi (nilai sekitar 75-90)
    """
    print("=" * 60)
    print("CONTOH PENGGUNAAN SISTEM FUZZY MAMDANI")
    print("=" * 60)

    freq, nom, jam = 15.0, 4_000_000.0, 23.0
    print(f"\nInput:")
    print(f"  Frekuensi : {freq} kali/hari")
    print(f"  Nominal   : Rp {nom:,.0f}")
    print(f"  Jam       : {jam}:00\n")

    mf_f = fuzzifikasi_frekuensi(freq)
    mf_n = fuzzifikasi_nominal(nom)
    mf_w = fuzzifikasi_waktu(jam)

    print("STEP 1 - Fuzzifikasi:")
    print(f"  Frekuensi → Rendah:{mf_f['rendah']}, Sedang:{mf_f['sedang']}, Tinggi:{mf_f['tinggi']}")
    print(f"  Nominal   → Kecil :{mf_n['kecil']},  Sedang:{mf_n['sedang']}, Besar :{mf_n['besar']}")
    print(f"  Waktu     → Siang :{mf_w['siang']},  Malam :{mf_w['malam']},  Larut :{mf_w['larut_malam']}")

    hasil_r = evaluasi_rule(mf_f, mf_n, mf_w)
    print("\nSTEP 2 - Evaluasi Rule:")
    for r in hasil_r['rules']:
        if r['firing'] > 0:
            print(f"  [{r['id']}] {r['deskripsi']}")
            print(f"       Firing = {r['detail']} = {r['firing']} → {r['label']}")

    print(f"\nSTEP 3 - Agregasi Alpha:")
    alpha = hasil_r['alpha']
    print(f"  α_rendah = {alpha['rendah']}")
    print(f"  α_sedang = {alpha['sedang']}")
    print(f"  α_tinggi = {alpha['tinggi']}")

    centroid, dd = defuzzifikasi(alpha['rendah'], alpha['sedang'], alpha['tinggi'])
    print(f"\nSTEP 4 - Defuzzifikasi (Centroid):")
    print(f"  Σ[x·μ(x)] = {dd['numerator']}")
    print(f"  Σ[μ(x)]   = {dd['denominator']}")
    print(f"  Centroid  = {centroid}")

    hasil = tampilkan_hasil(centroid)
    print(f"\n{'='*60}")
    print(f"HASIL AKHIR")
    print(f"  Nilai Kecurigaan : {hasil['nilai']}")
    print(f"  Kategori         : {hasil['kategori']}")
    print(f"  {hasil['deskripsi']}")
    print("=" * 60)


if __name__ == "__main__":
    app.run(debug=True)