#### NAMA : Aditya Alfandy
#### NIM : H1D024103
#### Shift KRS : C
#### Shift Akhir : A

# 🔍 FuzzyGuard — Sistem Deteksi Kecurigaan Transaksi Bank

Sistem Inferensi Fuzzy Mamdani berbasis Web  
> Mendeteksi potensi aktivitas judi online berdasarkan pola transaksi rekening bank.

---
## Link website: https://fandy456.pythonanywhere.com/

## 📋 Daftar Isi

1. [Deskripsi Program](#deskripsi-program)
2. [Struktur File](#struktur-file)
3. [Instalasi & Cara Menjalankan](#instalasi--cara-menjalankan)
4. [Konsep Fuzzy Logic Mamdani](#konsep-fuzzy-logic-mamdani)
5. [Variabel Input & Fungsi Keanggotaan](#variabel-input--fungsi-keanggotaan)
6. [Variabel Output](#variabel-output)
7. [Rule Base (Basis Aturan)](#rule-base-basis-aturan)
8. [Penjelasan Kode](#penjelasan-kode)
9. [Tahapan Proses Fuzzy](#tahapan-proses-fuzzy)
10. [Contoh Input & Output](#contoh-input--output)
11. [Teknologi yang Digunakan](#teknologi-yang-digunakan)

---

## Deskripsi Program

Program ini adalah implementasi **Sistem Inferensi Fuzzy Mamdani** untuk mendeteksi tingkat kecurigaan transaksi rekening bank yang berpotensi terkait aktivitas judi online. Program dibangun dengan Python (Flask) sebagai backend dan HTML/CSS/JavaScript sebagai frontend berbasis web statis.

**Metode:** Fuzzy Logic Mamdani  
**Defuzzifikasi:** Centroid (Center of Gravity)  
**Perhitungan:** Manual — tanpa library fuzzy (tanpa `scikit-fuzzy`)

---

## Struktur File

```
fuzzy_app/
│
├── app.py                  ← Backend Flask + seluruh logika fuzzy
│
└── templates/
    └── index.html          ← Frontend web (UI interaktif)
```

### Penjelasan Singkat

| File | Peran |
|------|-------|
| `app.py` | Server Flask, semua fungsi fuzzy (fuzzifikasi, inferensi, defuzzifikasi), dan endpoint API `/hitung` |
| `templates/index.html` | Antarmuka web: slider input, grafik MF canvas, tabel rule, grafik defuzzifikasi, gauge hasil |

---

## Instalasi & Cara Menjalankan

### Prasyarat

Pastikan Python sudah terinstal di komputer Anda:

```bash
python --version
# Python 3.8 atau lebih baru
```

### Langkah Instalasi

**1. Clone atau unduh proyek ini, lalu masuk ke folder:**

```bash
cd fuzzy_app
```

**2. (Opsional) Buat virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependensi:**

```bash
pip install flask
```

> Program ini hanya membutuhkan **Flask** saja. Tidak ada library fuzzy eksternal.

**4. Jalankan server:**

```bash
python app.py
```

**5. Buka browser dan akses:**

```
http://127.0.0.1:5000
```

### Contoh Output Terminal Saat Dijalankan

```
============================================================
CONTOH PENGGUNAAN SISTEM FUZZY MAMDANI
============================================================

Input:
  Frekuensi : 15.0 kali/hari
  Nominal   : Rp 4,000,000
  Jam       : 23.0:00

STEP 1 - Fuzzifikasi:
  Frekuensi → Rendah:0.0, Sedang:0.0, Tinggi:0.5
  Nominal   → Kecil :0.0, Sedang:0.0, Besar :0.5
  Waktu     → Siang :0.0, Malam :0.0, Larut :0.5

STEP 2 - Evaluasi Rule:
  [R1] Frekuensi Tinggi AND Nominal Besar AND Waktu Larut Malam
       Firing = min(0.5, 0.5, 0.5) = 0.5 → TINGGI
  [R4] Frekuensi Tinggi AND Nominal Besar
       Firing = min(0.5, 0.5) = 0.5 → TINGGI
  [R9] Frekuensi Tinggi AND Waktu Larut Malam
       Firing = min(0.5, 0.5) = 0.5 → TINGGI

STEP 3 - Agregasi Alpha:
  α_rendah = 0.0
  α_sedang = 0.0
  α_tinggi = 0.5

STEP 4 - Defuzzifikasi (Centroid):
  Σ[x·μ(x)] = ...
  Σ[μ(x)]   = ...
  Centroid   = 84.5

============================================================
HASIL AKHIR
  Nilai Kecurigaan : 84.5
  Kategori         : Tinggi
  Pola transaksi sangat mencurigakan!
============================================================

Menjalankan server Flask di http://127.0.0.1:5000
```

---

## Konsep Fuzzy Logic Mamdani

Sistem Mamdani adalah salah satu metode inferensi fuzzy paling populer. Berbeda dengan Sugeno, output Mamdani berupa **himpunan fuzzy** (bukan konstanta), sehingga membutuhkan tahap defuzzifikasi untuk menghasilkan nilai crisp.

```
INPUT CRISP → [FUZZIFIKASI] → [EVALUASI RULE] → [AGREGASI] → [DEFUZZIFIKASI] → OUTPUT CRISP
```

| Tahap | Metode yang Digunakan |
|-------|-----------------------|
| Fuzzifikasi | Fungsi keanggotaan Segitiga (Triangular / trimf) |
| Evaluasi Rule | Operator AND = MIN |
| Agregasi | Operator OR antar rule = MAX |
| Defuzzifikasi | Centroid (Center of Gravity) |

---

## Variabel Input & Fungsi Keanggotaan

### 1. Frekuensi Transfer per Hari

**Range:** 0 – 20 kali/hari  
**Fungsi keanggotaan:** Segitiga (trimf)

| Himpunan | Parameter (a, b, c) | Puncak (μ=1) |
|----------|---------------------|--------------|
| Rendah   | (0, 0, 5)           | x = 0        |
| Sedang   | (3, 7.5, 12)        | x = 7.5      |
| Tinggi   | (10, 20, 20)        | x = 20       |

```
μ
1 |*                              *
  |  *     /\                   *
  |    *  /  \                *
  |     */    \             *
0 |___________\___________*_______
  0    3    5  7.5  10   12    20
      Rendah  Sedang    Tinggi
```

### 2. Nominal Transfer per Hari

**Range:** 0 – 5.000.000 rupiah  
**Fungsi keanggotaan:** Segitiga (trimf)

| Himpunan | Parameter (a, b, c)              | Puncak (μ=1) |
|----------|----------------------------------|--------------|
| Kecil    | (0, 0, 1.500.000)                | x = 0        |
| Sedang   | (1.000.000, 2.250.000, 3.500.000)| x = 2.250.000|
| Besar    | (3.000.000, 5.000.000, 5.000.000)| x = 5.000.000|

### 3. Waktu Transaksi

**Range:** 0 – 24 jam  
**Fungsi keanggotaan:** Segitiga (trimf) + wrap-around tengah malam

| Himpunan    | Rentang Aktif | Puncak (μ=1)   |
|-------------|---------------|----------------|
| Siang       | 08:00 – 17:00 | 12:30          |
| Malam       | 17:00 – 22:00 | 19:30          |
| Larut Malam | 22:00 – 05:00 | 00:00 (tengah malam) |

> **Catatan:** Larut Malam menggunakan logika khusus *wrap-around* karena melewati tengah malam (jam 24/00).  
> - Jika `22 ≤ jam ≤ 24` → `μ = (jam - 22) / 2`  
> - Jika `0 ≤ jam ≤ 5` → `μ = (5 - jam) / 5`

---

## Variabel Output

**Nama:** Tingkat Kecurigaan Transaksi  
**Range:** 0 – 100

| Himpunan | Parameter (a, b, c) | Rentang Dominan |
|----------|---------------------|-----------------|
| Rendah   | (0, 0, 40)          | 0 – 40          |
| Sedang   | (30, 50, 70)        | 30 – 70         |
| Tinggi   | (60, 100, 100)      | 60 – 100        |

**Interpretasi nilai crisp hasil defuzzifikasi:**

| Nilai     | Kategori | Interpretasi                                    |
|-----------|----------|-------------------------------------------------|
| < 40      | Rendah   | Transaksi normal, tidak ada indikasi mencurigakan |
| 40 – 64   | Sedang   | Perlu dipantau, ada beberapa pola tidak wajar   |
| ≥ 65      | Tinggi   | Sangat mencurigakan, indikasi kuat judi online  |

---

## Rule Base (Basis Aturan)

Program menggunakan **12 rule fuzzy** dengan operator AND (MIN):

| ID  | Antecedent (IF)                                             | Konsekuen (THEN) |
|-----|-------------------------------------------------------------|------------------|
| R1  | Frekuensi **Tinggi** AND Nominal **Besar** AND Waktu **Larut Malam** | Kecurigaan **Tinggi**  |
| R2  | Frekuensi **Sedang** AND Nominal **Sedang** AND Waktu **Malam**      | Kecurigaan **Sedang**  |
| R3  | Frekuensi **Rendah** AND Nominal **Kecil**                           | Kecurigaan **Rendah**  |
| R4  | Frekuensi **Tinggi** AND Nominal **Besar**                           | Kecurigaan **Tinggi**  |
| R5  | Frekuensi **Tinggi** AND Nominal **Sedang**                          | Kecurigaan **Sedang**  |
| R6  | Frekuensi **Sedang** AND Nominal **Besar**                           | Kecurigaan **Tinggi**  |
| R7  | Frekuensi **Sedang** AND Nominal **Kecil**                           | Kecurigaan **Rendah**  |
| R8  | Frekuensi **Rendah** AND Nominal **Sedang**                          | Kecurigaan **Rendah**  |
| R9  | Frekuensi **Tinggi** AND Waktu **Larut Malam**                       | Kecurigaan **Tinggi**  |
| R10 | Frekuensi **Rendah** AND Nominal **Besar**                           | Kecurigaan **Sedang**  |
| R11 | Frekuensi **Tinggi** AND Waktu **Malam**                             | Kecurigaan **Sedang**  |
| R12 | Frekuensi **Sedang** AND Waktu **Larut Malam**                       | Kecurigaan **Sedang**  |

---

## Penjelasan Kode

### `app.py` — Fungsi-fungsi Utama

---

#### `trimf(x, a, b, c)`

Fungsi keanggotaan dasar berbentuk segitiga. Semua himpunan fuzzy dalam program ini menggunakan fungsi ini.

```python
def trimf(x, a, b, c):
    if x < a or x > c:
        return 0.0
    if a <= x <= b:
        if b == a: return 1.0
        return (x - a) / (b - a)   # sisi kiri: naik linear
    else:
        if c == b: return 1.0
        return (c - x) / (c - b)   # sisi kanan: turun linear
```

**Parameter:**
- `x` — nilai crisp yang akan difuzzifikasi
- `a` — titik kiri (μ = 0, awal kenaikan)
- `b` — titik puncak (μ = 1)
- `c` — titik kanan (μ = 0, akhir penurunan)

**Kasus khusus shoulder:** Jika `a == b` (puncak di kiri), fungsi langsung bernilai 1 untuk x = a. Jika `b == c` (puncak di kanan), sama.

---

#### `fuzzifikasi_frekuensi(frekuensi)`

Menghitung derajat keanggotaan nilai frekuensi terhadap tiga himpunan (Rendah, Sedang, Tinggi).

```python
def fuzzifikasi_frekuensi(frekuensi):
    rendah = trimf(frekuensi, 0, 0, 5)
    sedang = trimf(frekuensi, 3, 7.5, 12)
    tinggi = trimf(frekuensi, 10, 20, 20)
    return {'rendah': rendah, 'sedang': sedang, 'tinggi': tinggi}
```

**Contoh:** `frekuensi = 15`
- Rendah → `trimf(15, 0, 0, 5)` = **0.0** (di luar range)
- Sedang → `trimf(15, 3, 7.5, 12)` = **0.0** (di luar range)
- Tinggi → `trimf(15, 10, 20, 20)` = **(15-10)/(20-10)** = **0.5**

---

#### `fuzzifikasi_nominal(nominal)`

Menghitung derajat keanggotaan nilai nominal terhadap himpunan Kecil, Sedang, Besar.

```python
def fuzzifikasi_nominal(nominal):
    kecil  = trimf(nominal, 0,         0,         1_500_000)
    sedang = trimf(nominal, 1_000_000, 2_250_000, 3_500_000)
    besar  = trimf(nominal, 3_000_000, 5_000_000, 5_000_000)
    return {'kecil': kecil, 'sedang': sedang, 'besar': besar}
```

---

#### `fuzzifikasi_waktu(jam)`

Menghitung derajat keanggotaan waktu transaksi. Himpunan Larut Malam menggunakan logika khusus wrap-around karena melewati tengah malam.

```python
def fuzzifikasi_waktu(jam):
    siang = trimf(jam, 8.0, 12.5, 17.0)
    malam = trimf(jam, 17.0, 19.5, 22.0)

    if 22.0 <= jam <= 24.0:
        larut_malam = (jam - 22.0) / (24.0 - 22.0)   # naik ke puncak di 24
    elif 0.0 <= jam <= 5.0:
        larut_malam = (5.0 - jam) / (5.0 - 0.0)       # turun dari puncak di 0
    else:
        larut_malam = 0.0

    return {'siang': siang, 'malam': malam, 'larut_malam': larut_malam}
```

---

#### `evaluasi_rule(mf_frekuensi, mf_nominal, mf_waktu)`

Mengevaluasi seluruh 12 rule fuzzy dan mengembalikan *firing strength* tiap rule beserta nilai alpha agregasi per kategori output.

```python
# Contoh satu rule (R1):
firing_R1 = min(f['tinggi'], n['besar'], w['larut_malam'])   # Operator AND = MIN

# Agregasi per kategori (Operator MAX):
alpha_tinggi = max(firing_R1, firing_R4, firing_R6, firing_R9)
```

**Alur:**
1. Hitung `firing strength` setiap rule dengan `min()` (AND = ambil nilai terkecil dari antecedent).
2. Kelompokkan berdasarkan konsekuen (Rendah/Sedang/Tinggi).
3. Ambil `max()` dalam setiap kelompok → menghasilkan `α_rendah`, `α_sedang`, `α_tinggi`.

---

#### `defuzzifikasi(alpha_rendah, alpha_sedang, alpha_tinggi, n_points=500)`

Mengubah output fuzzy menjadi nilai crisp menggunakan metode **Centroid (Center of Gravity)**.

```python
# Rumus Centroid:
#
#         Σ [ x_i × μ_agg(x_i) ]
#  z* =  ─────────────────────────
#              Σ [ μ_agg(x_i) ]

for i in range(n_points + 1):
    x = i * (100 / n_points)

    # Clip: potong MF output dengan alpha (firing strength)
    mu_r = min(alpha_rendah, mf_output_rendah(x))
    mu_s = min(alpha_sedang, mf_output_sedang(x))
    mu_t = min(alpha_tinggi, mf_output_tinggi(x))

    # Agregasi MAX dari semua output
    mu_agg = max(mu_r, mu_s, mu_t)

    numerator   += x * mu_agg
    denominator += mu_agg

centroid = numerator / denominator
```

**Langkah detail:**
1. **Diskretisasi** domain output [0, 100] menjadi 500 titik.
2. Untuk setiap titik `x`, hitung `μ_clipped` = `min(alpha, MF(x))` — ini adalah *implication* Mamdani (memotong MF output sesuai firing strength).
3. **Agregasi MAX** dari ketiga output clipped per titik `x`.
4. Hitung centroid dengan rumus di atas.

---

#### `tampilkan_hasil(nilai_kecurigaan)`

Mengonversi nilai crisp hasil defuzzifikasi menjadi kategori kualitatif beserta deskripsinya.

```python
def tampilkan_hasil(nilai_kecurigaan):
    if nilai_kecurigaan < 40.0:
        return {'kategori': 'Rendah', ...}
    elif nilai_kecurigaan < 65.0:
        return {'kategori': 'Sedang', ...}
    else:
        return {'kategori': 'Tinggi', ...}
```

---

#### Flask Routes

| Route | Method | Fungsi |
|-------|--------|--------|
| `/` | GET | Render halaman utama, kirim data MF untuk grafik |
| `/hitung` | POST (JSON) | Terima input, proses fuzzy, kembalikan hasil lengkap |

**Request `/hitung`:**
```json
{
  "frekuensi": 15,
  "nominal": 4000000,
  "jam": 23
}
```

**Response `/hitung`:**
```json
{
  "input": { "frekuensi": 15, "nominal": 4000000, "jam": 23 },
  "fuzzifikasi": { "frekuensi": {...}, "nominal": {...}, "waktu": {...} },
  "rules": [ {"id": "R1", "firing": 0.5, "konsekuen": "tinggi", ...}, ... ],
  "alpha": { "rendah": 0.0, "sedang": 0.0, "tinggi": 0.5 },
  "defuzzifikasi": { "centroid": 84.5, "numerator": ..., "denominator": ... },
  "hasil": { "nilai": 84.5, "kategori": "Tinggi", "deskripsi": "..." }
}
```

---

### `templates/index.html` — Frontend

Seluruh UI dibangun dengan HTML + CSS + JavaScript vanilla (tanpa framework). Fitur utama:

| Komponen | Keterangan |
|----------|------------|
| **Grafik MF (Canvas)** | Menampilkan fungsi keanggotaan tiap variabel secara real-time. Dirender ulang setiap kali slider bergerak. |
| **Slider + Number Input** | Input tersinkronisasi dua arah antara slider dan kotak angka. |
| **Badges MF Live** | Menampilkan nilai keanggotaan μ langsung saat slider digeser (dihitung ulang di JavaScript). |
| **Tombol Preset** | 3 skenario siap pakai (Rendah / Sedang / Tinggi) untuk memudahkan pengujian. |
| **Tabel Rule** | Menampilkan semua 12 rule, firing strength, bar kekuatan, dan tag konsekuen. |
| **Grafik Defuzzifikasi** | Menggambar area MF output yang di-clip dan garis centroid. |
| **Gauge Meter** | Jarum gauge visual untuk nilai kecurigaan akhir. |

---

## Tahapan Proses Fuzzy

Berikut alur lengkap proses dari input hingga output:

```
┌─────────────────────────────────────────────────────────────┐
│                         INPUT CRISP                         │
│   Frekuensi: 15  |  Nominal: Rp 4.000.000  |  Jam: 23:00   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    TAHAP 1: FUZZIFIKASI                     │
│                                                             │
│  Frekuensi → Rendah: 0.0 | Sedang: 0.0 | Tinggi: 0.5       │
│  Nominal   → Kecil:  0.0 | Sedang: 0.0 | Besar:  0.5       │
│  Waktu     → Siang:  0.0 | Malam:  0.0 | Larut:  0.5       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│             TAHAP 2: EVALUASI RULE (Mamdani)                │
│                                                             │
│  R1: min(0.5, 0.5, 0.5) = 0.5  → TINGGI                    │
│  R4: min(0.5, 0.5)      = 0.5  → TINGGI                    │
│  R9: min(0.5, 0.5)      = 0.5  → TINGGI                    │
│  ... (rule lain firing = 0.0)                               │
│                                                             │
│  α_rendah = MAX(semua rule Rendah) = 0.0                    │
│  α_sedang = MAX(semua rule Sedang) = 0.0                    │
│  α_tinggi = MAX(semua rule Tinggi) = 0.5                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           TAHAP 3: DEFUZZIFIKASI (Centroid)                 │
│                                                             │
│  Clip MF output Tinggi dengan α = 0.5                       │
│  → Area terpotong pada trimf(x, 60, 100, 100)               │
│                                                             │
│        Σ[x · μ(x)]                                         │
│  z* = ────────────  =  84.5                                 │
│          Σ[μ(x)]                                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  TAHAP 4: HASIL AKHIR                       │
│                                                             │
│  Nilai Kecurigaan : 84.5                                    │
│  Kategori         : TINGGI  ⚠                              │
│  Deskripsi        : Pola transaksi sangat mencurigakan!     │
└─────────────────────────────────────────────────────────────┘
```

---

## Contoh Input & Output

### Skenario 1 — Kecurigaan Rendah

| Parameter | Nilai |
|-----------|-------|
| Frekuensi | 2 kali/hari |
| Nominal | Rp 500.000 |
| Jam | 10:00 |

**Hasil:**
```
α Rendah = 0.6 | α Sedang = 0.0 | α Tinggi = 0.0
Centroid = 14.8
Kategori : RENDAH ✔
```

---

### Skenario 2 — Kecurigaan Sedang

| Parameter | Nilai |
|-----------|-------|
| Frekuensi | 7 kali/hari |
| Nominal | Rp 2.000.000 |
| Jam | 19:30 |

**Hasil:**
```
α Rendah = 0.0 | α Sedang = 0.8 | α Tinggi = 0.0
Centroid = 50.0
Kategori : SEDANG ⚠
```

---

### Skenario 3 — Kecurigaan Tinggi

| Parameter | Nilai |
|-----------|-------|
| Frekuensi | 15 kali/hari |
| Nominal | Rp 4.000.000 |
| Jam | 23:00 |

**Hasil:**
```
α Rendah = 0.0 | α Sedang = 0.0 | α Tinggi = 0.5
Centroid = 84.5
Kategori : TINGGI ✘
```

---

## Teknologi yang Digunakan

| Teknologi | Versi | Kegunaan |
|-----------|-------|----------|
| Python | 3.8+ | Bahasa pemrograman utama |
| Flask | 3.x | Web framework (routing, template, API) |
| HTML5 Canvas | — | Render grafik fungsi keanggotaan dan defuzzifikasi |
| JavaScript (Vanilla) | ES6+ | Logika frontend, sync slider, AJAX fetch |
| Google Fonts | — | Tipografi: Orbitron, Rajdhani, Share Tech Mono |

> **Tidak menggunakan:** `scikit-fuzzy`, `numpy`, `matplotlib`, atau library fuzzy lainnya.  
> Seluruh perhitungan fuzzy diimplementasi secara manual dari nol.

---
