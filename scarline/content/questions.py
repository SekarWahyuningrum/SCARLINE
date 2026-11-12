"""Bank soal SCARLINE: mini quiz misi, Training Zone (3 level), dan Final Line Challenge.

Format jawaban per tipe:
- ``mc``    : indeks opsi (int)
- ``tf``    : bool
- ``num``   : string angka/pecahan, mis. "-1/2"
- ``point`` : [x, y]
- ``line``  : {"m": "2", "c": "-1"}  (persamaan y = mx + c)
- ``match`` : daftar pasangan indeks item, mis. [[0, 3], [1, 4]]

Kunci jawaban TIDAK pernah dikirim ke browser sebelum siswa menjawab.
"""

# --------------------------------------------------------------------------
# Mini quiz untuk setiap misi (3 soal; lulus minimal 2 benar)
# --------------------------------------------------------------------------
LESSON_QUIZZES = {
    "coordinate-city": [
        {
            "id": "M1-1", "type": "mc", "topic": "koordinat",
            "prompt": "Titik (−3, 5) terletak di ...",
            "options": ["Kuadran I", "Kuadran II", "Kuadran III", "Kuadran IV"], "answer": 1,
            "hint": "Lihat tanda x dan y: x negatif, y positif.",
            "explain": "x = −3 (kiri) dan y = 5 (atas). Pola (−, +) adalah Kuadran II.",
        },
        {
            "id": "M1-2", "type": "point", "topic": "koordinat", "range": 6,
            "prompt": "Klik letak titik (4, −2) pada bidang koordinat.", "answer": [4, -2],
            "hint": "Mulai dari O: 4 langkah ke kanan, lalu 2 langkah ke bawah.",
            "explain": "x = 4 berarti ke kanan 4 satuan, y = −2 berarti ke bawah 2 satuan. Titiknya di Kuadran IV.",
        },
        {
            "id": "M1-3", "type": "tf", "topic": "koordinat",
            "prompt": "Titik (0, 6) terletak di Kuadran I.", "answer": False,
            "hint": "Nilai x-nya 0. Di mana letak titik yang x-nya 0?",
            "explain": "Karena x = 0, titik (0, 6) berada tepat di sumbu Y, sehingga tidak termasuk kuadran mana pun.",
        },
    ],
    "point-detective": [
        {
            "id": "M2-1", "type": "tf", "topic": "titik-garis",
            "prompt": "Melalui dua titik yang berbeda hanya dapat dibuat tepat satu garis lurus.", "answer": True,
            "hint": "Coba bayangkan menarik benang lurus di antara dua paku.",
            "explain": "Benar. Dua titik berbeda selalu menentukan tepat satu garis lurus.",
        },
        {
            "id": "M2-2", "type": "mc", "topic": "titik-garis",
            "prompt": "Titik manakah yang terletak pada garis y = 2x + 1?",
            "options": ["(1, 2)", "(2, 5)", "(3, 6)", "(0, 2)"], "answer": 1,
            "hint": "Substitusikan nilai x setiap titik ke 2x + 1, lalu bandingkan dengan y-nya.",
            "explain": "Untuk (2, 5): 2(2) + 1 = 5, sama dengan y. Titik lain tidak memenuhi, misalnya (1, 2): 2(1) + 1 = 3 ≠ 2.",
        },
        {
            "id": "M2-3", "type": "mc", "topic": "titik-garis",
            "prompt": "Garis yang melalui titik (2, 1) dan (2, 5) adalah garis ...",
            "options": ["horizontal", "vertikal", "miring naik", "miring turun"], "answer": 1,
            "hint": "Perhatikan: nilai x kedua titik sama.",
            "explain": "Kedua titik memiliki x = 2, jadi garisnya tegak (vertikal) dengan persamaan x = 2.",
        },
    ],
    "gradient-mountain": [
        {
            "id": "M3-1", "type": "num", "topic": "gradien",
            "prompt": "Gradien garis yang melalui (1, 3) dan (3, 7) adalah ...", "answer": "2",
            "hint": "m = (y₂ − y₁)/(x₂ − x₁).",
            "explain": "m = (7 − 3)/(3 − 1) = 4/2 = 2.",
        },
        {
            "id": "M3-2", "type": "mc", "topic": "gradien",
            "prompt": "Garis yang turun dari kiri ke kanan memiliki gradien ...",
            "options": ["positif", "negatif", "nol", "tidak terdefinisi"], "answer": 1,
            "hint": "Saat x bertambah, y justru berkurang.",
            "explain": "Jika y berkurang saat x bertambah, Δy negatif dan Δx positif, sehingga m negatif.",
        },
        {
            "id": "M3-3", "type": "num", "topic": "gradien",
            "prompt": "Gradien garis yang melalui (−2, 5) dan (4, 2) adalah ... (tulis dalam pecahan, mis. −1/3)", "answer": "-1/2",
            "hint": "Hati-hati dengan x₁ = −2: x₂ − x₁ = 4 − (−2).",
            "explain": "m = (2 − 5)/(4 − (−2)) = −3/6 = −1/2.",
        },
    ],
    "equation-factory": [
        {
            "id": "M4-1", "type": "mc", "topic": "persamaan",
            "prompt": "Gradien dan titik potong sumbu Y dari garis y = −3x + 5 adalah ...",
            "options": ["m = −3 dan (0, 5)", "m = 5 dan (0, −3)", "m = 3 dan (0, 5)", "m = −3 dan (5, 0)"], "answer": 0,
            "hint": "Pada y = mx + c, m adalah koefisien x dan titik potong sumbu Y adalah (0, c).",
            "explain": "Koefisien x adalah −3, jadi m = −3. Konstantanya 5, jadi titik potong sumbu Y adalah (0, 5).",
        },
        {
            "id": "M4-2", "type": "num", "topic": "persamaan",
            "prompt": "Gradien garis 4x + 2y − 6 = 0 adalah ...", "answer": "-2",
            "hint": "Gunakan m = −a/b, atau ubah dulu ke bentuk y = mx + c.",
            "explain": "a = 4, b = 2, sehingga m = −4/2 = −2. Cek: 2y = −4x + 6 → y = −2x + 3.",
        },
        {
            "id": "M4-3", "type": "tf", "topic": "persamaan",
            "prompt": "Grafik y = 2x melalui titik pusat (0, 0).", "answer": True,
            "hint": "Substitusikan x = 0.",
            "explain": "x = 0 → y = 2(0) = 0, jadi (0, 0) terletak pada garis. Persamaan y = mx selalu melalui titik pusat.",
        },
    ],
    "line-constructor": [
        {
            "id": "M5-1", "type": "line", "topic": "menentukan",
            "prompt": "Tentukan persamaan garis bergradien 2 yang melalui titik (1, 4).", "answer": {"m": "2", "c": "2"},
            "hint": "Gunakan y − y₁ = m(x − x₁) lalu sederhanakan.",
            "explain": "y − 4 = 2(x − 1) → y − 4 = 2x − 2 → y = 2x + 2.",
        },
        {
            "id": "M5-2", "type": "line", "topic": "menentukan",
            "prompt": "Tentukan persamaan garis yang melalui (0, −1) dan (2, 5).", "answer": {"m": "3", "c": "-1"},
            "hint": "Hitung gradien dulu. Titik (0, −1) adalah titik potong sumbu Y!",
            "explain": "m = (5 − (−1))/(2 − 0) = 6/2 = 3. Garis memotong sumbu Y di (0, −1), jadi c = −1. y = 3x − 1.",
        },
        {
            "id": "M5-3", "type": "mc", "topic": "menentukan",
            "prompt": "Persamaan garis yang melalui titik pusat dengan gradien −4 adalah ...",
            "options": ["y = −4x", "y = x − 4", "y = −4", "y = 4x"], "answer": 0,
            "hint": "Garis melalui titik pusat berbentuk y = mx.",
            "explain": "Melalui O(0, 0) berarti c = 0, sehingga y = −4x.",
        },
    ],
    "parallel-perpendicular": [
        {
            "id": "M6-1", "type": "mc", "topic": "hubungan",
            "prompt": "Garis yang sejajar dengan y = 3x − 2 adalah ...",
            "options": ["y = 3x + 5", "y = −3x − 2", "y = (1/3)x + 1", "y = −(1/3)x"], "answer": 0,
            "hint": "Garis sejajar memiliki gradien yang sama.",
            "explain": "Gradien y = 3x − 2 adalah 3. Hanya y = 3x + 5 yang gradiennya juga 3.",
        },
        {
            "id": "M6-2", "type": "num", "topic": "hubungan",
            "prompt": "Gradien garis yang tegak lurus dengan garis bergradien 4 adalah ...", "answer": "-1/4",
            "hint": "m₁ × m₂ = −1, jadi m₂ = −1/m₁.",
            "explain": "m₂ = −1/4, karena 4 × (−1/4) = −1.",
            "diagnose": {
                "sign": "Kamu sudah membalik angkanya, tapi lupa tanda negatif. Ingat: NEGATIF kebalikan!",
                "flip": "Tanda negatifnya sudah benar, tapi angkanya juga harus dibalik: −1/m₁.",
                "flip_sign": "Itu gradien garis aslinya! Garis tegak lurus memakai negatif kebalikan, bukan gradien yang sama.",
            },
        },
        {
            "id": "M6-3", "type": "line", "topic": "hubungan",
            "prompt": "Tentukan persamaan garis yang melalui (0, 2) dan tegak lurus dengan y = −x + 7.", "answer": {"m": "1", "c": "2"},
            "hint": "Gradien y = −x + 7 adalah −1. Negatif kebalikannya berapa?",
            "explain": "m₁ = −1 → m₂ = −1/(−1) = 1. Garis memotong sumbu Y di (0, 2), jadi y = x + 2.",
        },
    ],
    "real-life": [
        {
            "id": "M7-1", "type": "num", "topic": "kehidupan",
            "prompt": "Sewa sepeda: Rp5.000 ditambah Rp4.000 per jam. Berapa rupiah biaya sewa selama 3 jam? (tulis angkanya saja)", "answer": "17000",
            "hint": "Model: y = 4.000x + 5.000.",
            "explain": "y = 4.000(3) + 5.000 = 12.000 + 5.000 = 17.000. Jadi biayanya Rp17.000.",
        },
        {
            "id": "M7-2", "type": "mc", "topic": "kehidupan",
            "prompt": "Pada model biaya y = 3.000x + 7.000 (x = banyak barang), angka 3.000 menyatakan ...",
            "options": ["biaya tambahan untuk setiap 1 barang", "biaya awal sebelum membeli", "total biaya", "banyak barang yang dibeli"], "answer": 0,
            "hint": "3.000 adalah gradien, yaitu laju perubahan.",
            "explain": "Gradien 3.000 berarti setiap tambah 1 barang, biaya naik Rp3.000. Angka 7.000 adalah biaya awal.",
        },
        {
            "id": "M7-3", "type": "num", "topic": "kehidupan",
            "prompt": "Tinggi air di bak mula-mula 10 cm dan naik 2 cm setiap menit. Setelah berapa menit tinggi air menjadi 30 cm?", "answer": "10",
            "hint": "Susun y = 2x + 10, lalu cari x saat y = 30.",
            "explain": "30 = 2x + 10 → 2x = 20 → x = 10 menit.",
        },
    ],
}

# --------------------------------------------------------------------------
# Training Zone
# --------------------------------------------------------------------------
TRAINING_LEVELS = {
    1: {"name": "LINE BEGINNER", "desc": "Mengenal koordinat, letak titik, garis lurus, dan jenis gradien.", "icon": "compass"},
    2: {"name": "GRADIENT EXPLORER", "desc": "Menghitung gradien, titik potong, bentuk y = mx + c, dan membaca grafik.", "icon": "mountain"},
    3: {"name": "EQUATION MASTER", "desc": "Persamaan garis dari dua titik/gradien, hubungan antargaris, dan soal cerita.", "icon": "crown"},
}

TRAINING_BANK = {
    1: [
        {"id": "T1-01", "type": "mc", "topic": "koordinat", "prompt": "Sumbu mendatar pada bidang Kartesius disebut ...",
         "options": ["sumbu X", "sumbu Y", "titik asal", "kuadran"], "answer": 0,
         "hint": "Sumbu ini berisi nilai absis.", "explain": "Sumbu mendatar adalah sumbu X; sumbu tegak adalah sumbu Y."},
        {"id": "T1-02", "type": "point", "topic": "koordinat", "range": 6, "prompt": "Klik letak titik A(−4, 2).", "answer": [-4, 2],
         "hint": "x negatif berarti ke kiri, y positif berarti ke atas.", "explain": "Dari O, 4 langkah ke kiri lalu 2 langkah ke atas. A berada di Kuadran II."},
        {"id": "T1-03", "type": "point", "topic": "koordinat", "range": 6, "prompt": "Klik letak titik B(3, −5).", "answer": [3, -5],
         "hint": "Geser mendatar dulu (x), baru tegak (y).", "explain": "3 langkah ke kanan lalu 5 langkah ke bawah. B berada di Kuadran IV."},
        {"id": "T1-04", "type": "mc", "topic": "koordinat", "prompt": "Titik (−5, −2) terletak di ...",
         "options": ["Kuadran I", "Kuadran II", "Kuadran III", "Kuadran IV"], "answer": 2,
         "hint": "Polanya (−, −).", "explain": "x negatif dan y negatif → Kuadran III."},
        {"id": "T1-05", "type": "tf", "topic": "koordinat", "prompt": "Koordinat (3, 2) dan (2, 3) menunjukkan titik yang sama.", "answer": False,
         "hint": "Apakah urutan dalam pasangan berurutan penting?", "explain": "Salah. (3, 2) berarti 3 ke kanan dan 2 ke atas, sedangkan (2, 3) berarti 2 ke kanan dan 3 ke atas. Urutan sangat penting."},
        {"id": "T1-06", "type": "mc", "topic": "koordinat", "prompt": "Perhatikan grafik. Koordinat titik P adalah ...",
         "graph": {"range": 6, "points": [{"x": -2, "y": 4, "label": "P"}]},
         "options": ["(−2, 4)", "(4, −2)", "(2, 4)", "(−2, −4)"], "answer": 0,
         "hint": "Baca dulu posisi mendatarnya (x), lalu posisi tegaknya (y).", "explain": "P berada 2 satuan di kiri sumbu Y (x = −2) dan 4 satuan di atas sumbu X (y = 4)."},
        {"id": "T1-07", "type": "num", "topic": "koordinat", "prompt": "Ordinat dari titik (7, −3) adalah ...", "answer": "-3",
         "hint": "Ordinat adalah nilai y.", "explain": "Pada (x, y) = (7, −3), absisnya 7 dan ordinatnya −3."},
        {"id": "T1-08", "type": "mc", "topic": "koordinat", "prompt": "Dari O(0, 0), titik Q digeser 5 satuan ke kiri lalu 2 satuan ke bawah. Koordinat Q adalah ...",
         "options": ["(−5, −2)", "(5, −2)", "(−2, −5)", "(−5, 2)"], "answer": 0,
         "hint": "Kiri → x negatif, bawah → y negatif.", "explain": "5 ke kiri → x = −5; 2 ke bawah → y = −2. Q(−5, −2)."},
        {"id": "T1-09", "type": "tf", "topic": "titik-garis", "prompt": "Garis yang melalui (−3, 4) dan (5, 4) adalah garis horizontal.", "answer": True,
         "hint": "Bandingkan nilai y kedua titik.", "explain": "Benar. Kedua titik memiliki y = 4, jadi garisnya mendatar: y = 4."},
        {"id": "T1-10", "type": "mc", "topic": "gradien", "prompt": "Garis yang naik dari kiri ke kanan memiliki gradien ...",
         "options": ["positif", "negatif", "nol", "tidak terdefinisi"], "answer": 0,
         "hint": "Saat x bertambah, y ikut bertambah.", "explain": "Δy dan Δx sama-sama positif, sehingga m positif."},
        {"id": "T1-11", "type": "tf", "topic": "gradien", "prompt": "Garis vertikal memiliki gradien nol.", "answer": False,
         "hint": "Pada garis vertikal, berapa nilai Δx?", "explain": "Salah. Garis vertikal memiliki Δx = 0, dan pembagian dengan nol tidak terdefinisi. Yang gradiennya nol adalah garis horizontal."},
        {"id": "T1-12", "type": "mc", "topic": "koordinat", "prompt": "Jarak titik (−6, 1) ke sumbu Y adalah ...",
         "options": ["6 satuan", "1 satuan", "−6 satuan", "7 satuan"], "answer": 0,
         "hint": "Jarak ke sumbu Y ditentukan oleh nilai x. Jarak selalu positif.", "explain": "Titik berada 6 langkah di kiri sumbu Y, jadi jaraknya |−6| = 6 satuan."},
    ],
    2: [
        {"id": "T2-01", "type": "num", "topic": "gradien", "prompt": "Gradien garis yang melalui A(2, 1) dan B(6, 9) adalah ...", "answer": "2",
         "hint": "m = (y₂ − y₁)/(x₂ − x₁).", "explain": "m = (9 − 1)/(6 − 2) = 8/4 = 2."},
        {"id": "T2-02", "type": "num", "topic": "gradien", "prompt": "Gradien garis yang melalui (−1, 4) dan (3, −4) adalah ...", "answer": "-2",
         "hint": "Perhatikan tanda negatif pada y₂ dan x₁.", "explain": "m = (−4 − 4)/(3 − (−1)) = −8/4 = −2."},
        {"id": "T2-03", "type": "num", "topic": "gradien", "prompt": "Gradien garis yang melalui (−3, 2) dan (3, 5) adalah ... (boleh pecahan)", "answer": "1/2",
         "hint": "Δy = 5 − 2, Δx = 3 − (−3).", "explain": "m = (5 − 2)/(3 − (−3)) = 3/6 = 1/2."},
        {"id": "T2-04", "type": "mc", "topic": "persamaan", "prompt": "Garis y = 5x − 3 memotong sumbu Y di titik ...",
         "options": ["(0, −3)", "(0, 5)", "(−3, 0)", "(3/5, 0)"], "answer": 0,
         "hint": "Titik potong sumbu Y terjadi saat x = 0.", "explain": "x = 0 → y = 5(0) − 3 = −3, jadi titiknya (0, −3). Titik (3/5, 0) adalah titik potong sumbu X."},
        {"id": "T2-05", "type": "num", "topic": "persamaan", "prompt": "Garis y = 2x − 6 memotong sumbu X di titik (a, 0). Nilai a adalah ...", "answer": "3",
         "hint": "Titik potong sumbu X terjadi saat y = 0.", "explain": "0 = 2x − 6 → 2x = 6 → x = 3. Titiknya (3, 0)."},
        {"id": "T2-06", "type": "num", "topic": "gradien", "prompt": "Gradien garis 3x − 6y + 12 = 0 adalah ...", "answer": "1/2",
         "hint": "m = −a/b dengan a = 3 dan b = −6.", "explain": "m = −3/(−6) = 1/2. Cek: 6y = 3x + 12 → y = (1/2)x + 2."},
        {"id": "T2-07", "type": "mc", "topic": "grafik", "prompt": "Perhatikan grafik. Gradien garis tersebut adalah ...",
         "graph": {"range": 6, "lines": [{"m": -1, "c": 2}], "points": [{"x": 0, "y": 2, "label": "(0, 2)"}, {"x": 2, "y": 0, "label": "(2, 0)"}]},
         "options": ["−1", "1", "2", "−2"], "answer": 0,
         "hint": "Gunakan dua titik yang ditandai: (0, 2) dan (2, 0).", "explain": "m = (0 − 2)/(2 − 0) = −2/2 = −1. Garisnya turun, jadi gradiennya negatif."},
        {"id": "T2-08", "type": "mc", "topic": "grafik", "prompt": "Perhatikan grafik. Persamaan garis tersebut adalah ...",
         "graph": {"range": 6, "lines": [{"m": 2, "c": -1}], "points": [{"x": 0, "y": -1, "label": "(0, −1)"}, {"x": 2, "y": 3, "label": "(2, 3)"}]},
         "options": ["y = 2x − 1", "y = x − 1", "y = −2x − 1", "y = 2x + 1"], "answer": 0,
         "hint": "Cari c dari titik potong sumbu Y, lalu hitung m dari dua titik.", "explain": "Titik potong sumbu Y (0, −1) → c = −1. m = (3 − (−1))/(2 − 0) = 4/2 = 2. Jadi y = 2x − 1."},
        {"id": "T2-09", "type": "tf", "topic": "gradien", "prompt": "Garis y = −4 memiliki gradien 0.", "answer": True,
         "hint": "y = −4 bisa ditulis y = 0x − 4.", "explain": "Benar. y = −4 adalah garis horizontal; koefisien x-nya 0."},
        {"id": "T2-10", "type": "num", "topic": "grafik", "prompt": "Perhatikan grafik. Garis memotong sumbu Y di titik (0, c). Nilai c adalah ...",
         "graph": {"range": 6, "lines": [{"m": -2, "c": 3}]}, "answer": "3",
         "hint": "Lihat di mana garis menyentuh sumbu tegak (sumbu Y).", "explain": "Garis memotong sumbu Y di (0, 3), jadi c = 3. Persamaannya y = −2x + 3."},
        {"id": "T2-11", "type": "line", "topic": "persamaan", "prompt": "Lengkapi persamaan garis bergradien −3 yang memotong sumbu Y di (0, 4).", "answer": {"m": "-3", "c": "4"},
         "hint": "Gunakan y = mx + c secara langsung.", "explain": "m = −3 dan c = 4, jadi y = −3x + 4."},
        {"id": "T2-12", "type": "mc", "topic": "gradien", "prompt": "Garis manakah yang paling curam?",
         "options": ["y = x + 1", "y = −4x + 2", "y = 2x", "y = (1/2)x + 5"], "answer": 1,
         "hint": "Bandingkan nilai mutlak gradiennya, bukan tandanya.", "explain": "Nilai mutlak gradiennya: 1, 4, 2, dan 1/2. Yang terbesar adalah |−4| = 4, jadi y = −4x + 2 paling curam (walaupun arahnya turun)."},
    ],
    3: [
        {"id": "T3-01", "type": "line", "topic": "menentukan", "prompt": "Tentukan persamaan garis yang melalui (2, 3) dan (4, 7).", "answer": {"m": "2", "c": "-1"},
         "hint": "Hitung m, lalu gunakan y − y₁ = m(x − x₁).", "explain": "m = (7 − 3)/(4 − 2) = 2. y − 3 = 2(x − 2) → y = 2x − 1."},
        {"id": "T3-02", "type": "line", "topic": "menentukan", "prompt": "Tentukan persamaan garis bergradien −1/2 yang melalui (4, 1).", "answer": {"m": "-1/2", "c": "3"},
         "hint": "y − 1 = −(1/2)(x − 4).", "explain": "y − 1 = −(1/2)(x − 4) → y − 1 = −(1/2)x + 2 → y = −(1/2)x + 3."},
        {"id": "T3-03", "type": "line", "topic": "menentukan", "prompt": "Tentukan persamaan garis yang melalui (−1, 5) dan (3, −3).", "answer": {"m": "-2", "c": "3"},
         "hint": "Δx = 3 − (−1) = 4.", "explain": "m = (−3 − 5)/(3 − (−1)) = −8/4 = −2. y − 5 = −2(x + 1) → y = −2x + 3."},
        {"id": "T3-04", "type": "line", "topic": "hubungan", "prompt": "Tentukan persamaan garis yang sejajar dengan y = 4x − 1 dan melalui (1, 6).", "answer": {"m": "4", "c": "2"},
         "hint": "Sejajar berarti gradiennya sama.", "explain": "m = 4. y − 6 = 4(x − 1) → y = 4x + 2."},
        {"id": "T3-05", "type": "line", "topic": "hubungan", "prompt": "Tentukan persamaan garis yang tegak lurus dengan 2x + 3y − 6 = 0 dan melalui (2, 0).", "answer": {"m": "3/2", "c": "-3"},
         "hint": "Gradien 2x + 3y − 6 = 0 adalah −2/3. Negatif kebalikannya?", "explain": "m₁ = −2/3 → m₂ = 3/2. y − 0 = (3/2)(x − 2) → y = (3/2)x − 3."},
        {"id": "T3-06", "type": "match", "topic": "hubungan", "prompt": "Pasangkan garis-garis yang SEJAJAR (klik dua garis untuk membuat satu pasangan).",
         "items": ["y = 2x + 1", "y = −3x", "y = (1/2)x − 2", "y = 2x − 5", "y = −3x + 4", "y = (1/2)x + 3"],
         "answer": [[0, 3], [1, 4], [2, 5]],
         "hint": "Garis sejajar memiliki gradien (koefisien x) yang sama.", "explain": "Gradien 2: y = 2x + 1 dan y = 2x − 5. Gradien −3: y = −3x dan y = −3x + 4. Gradien 1/2: y = (1/2)x − 2 dan y = (1/2)x + 3."},
        {"id": "T3-07", "type": "mc", "topic": "hubungan", "prompt": "Hubungan garis y = 3x + 2 dan x + 3y − 9 = 0 adalah ...",
         "options": ["tegak lurus", "sejajar", "berimpit", "berpotongan tidak tegak lurus"], "answer": 0,
         "hint": "Cari gradien garis kedua dengan m = −a/b.", "explain": "m₁ = 3 dan m₂ = −1/3. m₁ × m₂ = 3 × (−1/3) = −1, jadi kedua garis tegak lurus."},
        {"id": "T3-08", "type": "num", "topic": "kehidupan", "prompt": "Biaya cetak foto Rp2.000 per lembar ditambah biaya admin Rp5.000. Jika total biaya Rp45.000, berapa lembar foto yang dicetak?", "answer": "20",
         "hint": "45.000 = 2.000x + 5.000.", "explain": "2.000x = 45.000 − 5.000 = 40.000 → x = 20 lembar."},
        {"id": "T3-09", "type": "line", "topic": "kehidupan", "prompt": "Suhu air yang dipanaskan naik secara linear: menit ke-0 suhunya 25°C dan menit ke-4 suhunya 45°C. Tulis persamaan suhu y terhadap waktu x.", "answer": {"m": "5", "c": "25"},
         "hint": "Dua titik: (0, 25) dan (4, 45).", "explain": "m = (45 − 25)/(4 − 0) = 5 °C per menit, c = 25 (suhu awal). y = 5x + 25."},
        {"id": "T3-10", "type": "num", "topic": "kehidupan", "prompt": "Taksi A: Rp7.000 + Rp4.000/km. Taksi B: Rp10.000 + Rp3.500/km. Pada jarak berapa km biaya keduanya sama?", "answer": "6",
         "hint": "Samakan kedua persamaan.", "explain": "7.000 + 4.000x = 10.000 + 3.500x → 500x = 3.000 → x = 6 km."},
        {"id": "T3-11", "type": "tf", "topic": "hubungan", "prompt": "Garis y = 2x + 3 dan 4x − 2y + 6 = 0 adalah dua garis sejajar yang berbeda.", "answer": False,
         "hint": "Ubah persamaan kedua ke bentuk y = mx + c, lalu bandingkan m dan c-nya.", "explain": "Salah. 4x − 2y + 6 = 0 → 2y = 4x + 6 → y = 2x + 3. Gradien dan konstantanya sama, jadi kedua garis BERIMPIT (garis yang sama), bukan sejajar berbeda."},
        {"id": "T3-12", "type": "match", "topic": "hubungan", "prompt": "Pasangkan garis-garis yang saling TEGAK LURUS.",
         "items": ["y = 2x", "y = −3x + 1", "y = x + 4", "y = −(1/2)x + 2", "y = (1/3)x − 1", "y = −x"],
         "answer": [[0, 3], [1, 4], [2, 5]],
         "hint": "Cari pasangan yang hasil kali gradiennya −1.", "explain": "2 × (−1/2) = −1, −3 × (1/3) = −1, dan 1 × (−1) = −1."},
    ],
}

# --------------------------------------------------------------------------
# Final Line Challenge (25 soal, dipilih acak berimbang per topik)
# --------------------------------------------------------------------------
FINAL_BANK = [
    {"id": "F01", "type": "mc", "topic": "koordinat", "prompt": "Titik (4, −7) terletak di ...",
     "options": ["Kuadran I", "Kuadran II", "Kuadran III", "Kuadran IV"], "answer": 3,
     "explain": "x positif dan y negatif → (+, −) → Kuadran IV."},
    {"id": "F02", "type": "point", "topic": "koordinat", "range": 6, "prompt": "Tentukan letak titik (−3, −4) pada bidang koordinat.", "answer": [-3, -4],
     "explain": "3 langkah ke kiri dan 4 langkah ke bawah dari O. Titiknya di Kuadran III."},
    {"id": "F03", "type": "mc", "topic": "koordinat", "prompt": "Titik pada sumbu Y yang berjarak 5 satuan di bawah titik asal adalah ...",
     "options": ["(0, −5)", "(−5, 0)", "(5, 0)", "(0, 5)"], "answer": 0,
     "explain": "Pada sumbu Y, x = 0. Di bawah titik asal berarti y negatif: (0, −5)."},
    {"id": "F04", "type": "tf", "topic": "titik-garis", "prompt": "Titik (−1, −1) terletak pada garis y = 3x + 2.", "answer": True,
     "explain": "3(−1) + 2 = −1, sama dengan y-nya. Jadi titik tersebut terletak pada garis."},
    {"id": "F05", "type": "mc", "topic": "titik-garis", "prompt": "Garis melalui (0, 1) dan (1, 3). Titik berikut terletak pada garis tersebut, KECUALI ...",
     "options": ["(2, 5)", "(3, 7)", "(−1, −1)", "(4, 8)"], "answer": 3,
     "explain": "Garisnya y = 2x + 1. Untuk x = 4: y = 9, bukan 8. Titik lain memenuhi persamaan."},
    {"id": "F06", "type": "num", "topic": "gradien", "prompt": "Gradien garis yang melalui (−4, −1) dan (2, 2) adalah ...", "answer": "1/2",
     "explain": "m = (2 − (−1))/(2 − (−4)) = 3/6 = 1/2."},
    {"id": "F07", "type": "num", "topic": "gradien", "prompt": "Gradien garis yang melalui (5, −2) dan (1, 6) adalah ...", "answer": "-2",
     "explain": "m = (6 − (−2))/(1 − 5) = 8/(−4) = −2."},
    {"id": "F08", "type": "mc", "topic": "gradien", "prompt": "Gradien garis yang melalui (3, −1) dan (3, 4) adalah ...",
     "options": ["tidak terdefinisi", "0", "5", "1/5"], "answer": 0,
     "explain": "x₂ − x₁ = 3 − 3 = 0. Pembagian dengan nol tidak terdefinisi; garisnya vertikal x = 3."},
    {"id": "F09", "type": "num", "topic": "gradien", "prompt": "Gradien garis 5x + 2y − 10 = 0 adalah ...", "answer": "-5/2",
     "explain": "m = −a/b = −5/2."},
    {"id": "F10", "type": "mc", "topic": "grafik", "prompt": "Perhatikan grafik. Gradien garis tersebut adalah ...",
     "graph": {"range": 6, "lines": [{"m": 0.5, "c": -2}], "points": [{"x": 0, "y": -2, "label": "(0, −2)"}, {"x": 4, "y": 0, "label": "(4, 0)"}]},
     "options": ["1/2", "2", "−1/2", "−2"], "answer": 0,
     "explain": "m = (0 − (−2))/(4 − 0) = 2/4 = 1/2."},
    {"id": "F11", "type": "mc", "topic": "persamaan", "prompt": "Persamaan garis bergradien 3 yang memotong sumbu Y di (0, −2) adalah ...",
     "options": ["y = 3x − 2", "y = −2x + 3", "y = 3x + 2", "y = −3x − 2"], "answer": 0,
     "explain": "y = mx + c dengan m = 3 dan c = −2 → y = 3x − 2."},
    {"id": "F12", "type": "mc", "topic": "persamaan", "prompt": "Bentuk umum dari y = 2x − 5 adalah ...",
     "options": ["2x − y − 5 = 0", "2x + y − 5 = 0", "x − 2y − 5 = 0", "2x − y + 5 = 0"], "answer": 0,
     "explain": "Pindahkan y ke ruas kanan: 0 = 2x − y − 5, atau 2x − y − 5 = 0."},
    {"id": "F13", "type": "mc", "topic": "grafik", "prompt": "Perhatikan grafik. Persamaan garis tersebut adalah ...",
     "graph": {"range": 6, "lines": [{"m": -2, "c": 4}], "points": [{"x": 0, "y": 4, "label": "(0, 4)"}, {"x": 2, "y": 0, "label": "(2, 0)"}]},
     "options": ["y = −2x + 4", "y = 2x + 4", "y = −2x + 2", "y = −(1/2)x + 4"], "answer": 0,
     "explain": "c = 4 (titik potong sumbu Y). m = (0 − 4)/(2 − 0) = −2. Jadi y = −2x + 4."},
    {"id": "F14", "type": "num", "topic": "persamaan", "prompt": "Garis y = −3x + 9 memotong sumbu X di titik (a, 0). Nilai a adalah ...", "answer": "3",
     "explain": "0 = −3x + 9 → 3x = 9 → x = 3."},
    {"id": "F15", "type": "line", "topic": "menentukan", "prompt": "Tentukan persamaan garis bergradien 4 yang melalui (1, −2).", "answer": {"m": "4", "c": "-6"},
     "explain": "y − (−2) = 4(x − 1) → y + 2 = 4x − 4 → y = 4x − 6."},
    {"id": "F16", "type": "line", "topic": "menentukan", "prompt": "Tentukan persamaan garis yang melalui (−2, 1) dan (2, 9).", "answer": {"m": "2", "c": "5"},
     "explain": "m = (9 − 1)/(2 − (−2)) = 8/4 = 2. y − 1 = 2(x + 2) → y = 2x + 5."},
    {"id": "F17", "type": "line", "topic": "menentukan", "prompt": "Tentukan persamaan garis yang melalui titik pusat dan titik (4, −2).", "answer": {"m": "-1/2", "c": "0"},
     "explain": "m = (−2 − 0)/(4 − 0) = −1/2. Melalui titik pusat → c = 0. y = −(1/2)x."},
    {"id": "F18", "type": "line", "topic": "menentukan", "prompt": "Tentukan persamaan garis yang melalui (6, 0) dan (0, 3).", "answer": {"m": "-1/2", "c": "3"},
     "explain": "m = (3 − 0)/(0 − 6) = −1/2. Titik (0, 3) → c = 3. y = −(1/2)x + 3."},
    {"id": "F19", "type": "mc", "topic": "hubungan", "prompt": "Persamaan garis yang melalui (2, 5) dan sejajar dengan y = −x + 1 adalah ...",
     "options": ["y = −x + 7", "y = x + 3", "y = −x + 3", "y = −x + 5"], "answer": 0,
     "explain": "Sejajar → m = −1. y − 5 = −(x − 2) → y = −x + 7. (y = x + 3 memang melalui (2, 5), tetapi gradiennya 1, tidak sejajar.)"},
    {"id": "F20", "type": "num", "topic": "hubungan", "prompt": "Garis g tegak lurus dengan garis 3x − y + 2 = 0. Gradien garis g adalah ...", "answer": "-1/3",
     "explain": "Gradien 3x − y + 2 = 0 adalah −3/(−1) = 3. Garis tegak lurusnya bergradien −1/3."},
    {"id": "F21", "type": "line", "topic": "hubungan", "prompt": "Tentukan persamaan garis yang melalui (3, 1) dan tegak lurus dengan y = 3x − 4.", "answer": {"m": "-1/3", "c": "2"},
     "explain": "m = −1/3. y − 1 = −(1/3)(x − 3) → y − 1 = −(1/3)x + 1 → y = −(1/3)x + 2."},
    {"id": "F22", "type": "num", "topic": "hubungan", "prompt": "Garis y = ax + 2 sejajar dengan garis y = 4x − 1. Nilai a adalah ...", "answer": "4",
     "explain": "Sejajar → gradiennya sama, sehingga a = 4."},
    {"id": "F23", "type": "num", "topic": "kehidupan", "prompt": "Sebuah tangki berisi 200 liter air dan bocor 8 liter setiap jam. Setelah berapa jam tangki kosong?", "answer": "25",
     "explain": "Model y = −8x + 200. Tangki kosong saat y = 0: 8x = 200 → x = 25 jam. Gradien negatif berarti air berkurang."},
    {"id": "F24", "type": "num", "topic": "kehidupan", "prompt": "Harga 4 kg beras Rp56.000 dan 10 kg Rp140.000 (hubungan linear). Berapa rupiah harga 7 kg beras? (angka saja)", "answer": "98000",
     "explain": "m = (140.000 − 56.000)/(10 − 4) = 84.000/6 = 14.000 per kg, y = 14.000x. Untuk 7 kg: 98.000."},
    {"id": "F25", "type": "mc", "topic": "kehidupan", "prompt": "Andi punya tabungan awal Rp50.000 dan menabung Rp20.000 setiap minggu. Model tabungan y setelah x minggu adalah ...",
     "options": ["y = 20.000x + 50.000", "y = 50.000x + 20.000", "y = 70.000x", "y = 20.000x − 50.000"], "answer": 0,
     "explain": "Laju perubahan (gradien) Rp20.000 per minggu, nilai awal Rp50.000: y = 20.000x + 50.000."},
]

FINAL_TOPICS = ["koordinat", "titik-garis", "gradien", "persamaan", "grafik", "menentukan", "hubungan", "kehidupan"]

TOPIC_LABELS = {
    "koordinat": "Koordinat Kartesius",
    "titik-garis": "Titik dan Garis",
    "gradien": "Gradien",
    "persamaan": "Persamaan Garis",
    "grafik": "Membaca Grafik",
    "menentukan": "Menentukan Persamaan",
    "hubungan": "Garis Sejajar & Tegak Lurus",
    "kehidupan": "Penerapan Sehari-hari",
}


def all_questions():
    for qs in LESSON_QUIZZES.values():
        yield from qs
    for qs in TRAINING_BANK.values():
        yield from qs
    yield from FINAL_BANK


QUESTION_BY_ID = {q["id"]: q for q in all_questions()}
