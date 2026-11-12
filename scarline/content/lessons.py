"""Materi tujuh misi SCARLINE — Persamaan Garis Lurus (SMP kelas VIII).

Setiap misi memiliki struktur halaman materi yang sama:
nama wilayah, nomor misi, judul, tujuan, konsep, rumus, diagram, contoh
kehidupan sehari-hari, contoh soal + penyelesaian bertahap, fakta menarik,
aktivitas interaktif, mini quiz (lihat ``questions.py``), dan rangkuman.

Teks memakai tanda minus "−" dan indeks bawah (x₁, y₂) agar mudah dibaca.
"""

LESSONS = [
    # ------------------------------------------------------------------ 01
    {
        "slug": "coordinate-city",
        "no": 1,
        "region": "Coordinate City",
        "title": "Mengenal Koordinat Kartesius",
        "icon": "city",
        "xp": 100,
        "scar_intro": "Hai, Line Explorer! Selamat datang di Coordinate City. Di kota ini, setiap rumah punya alamat berupa dua angka. Yuk, kita pelajari cara membacanya!",
        "objectives": [
            "Menjelaskan pengertian bidang koordinat Kartesius.",
            "Mengenal sumbu X, sumbu Y, dan titik asal O(0, 0).",
            "Menentukan letak titik dari pasangan koordinat (x, y).",
            "Menentukan kuadran tempat suatu titik berada.",
        ],
        "concepts": [
            {
                "heading": "Bidang Kartesius",
                "body": "Bidang Kartesius dibentuk oleh dua garis bilangan yang <b>saling tegak lurus</b>. Garis mendatar disebut <b>sumbu X</b> dan garis tegak disebut <b>sumbu Y</b>. Keduanya berpotongan di <b>titik asal O(0, 0)</b>.",
            },
            {
                "heading": "Pasangan berurutan (x, y)",
                "body": "Setiap titik ditulis sebagai pasangan berurutan <span class='math'>(x, y)</span>. Nilai <b>x</b> disebut <b>absis</b> (langkah mendatar), nilai <b>y</b> disebut <b>ordinat</b> (langkah tegak). Urutannya penting: titik (2, 5) berbeda dengan titik (5, 2)!",
            },
            {
                "heading": "Cara menentukan posisi titik",
                "body": "Mulai dari titik O. Geser sejauh <b>x</b> langkah: ke kanan jika x positif, ke kiri jika x negatif. Lalu geser sejauh <b>y</b> langkah: ke atas jika y positif, ke bawah jika y negatif.",
            },
            {
                "heading": "Empat kuadran",
                "body": "Sumbu X dan Y membagi bidang menjadi empat daerah yang disebut kuadran, diberi nomor berlawanan arah jarum jam.",
                "bullets": [
                    "Kuadran I: x positif, y positif → (+, +)",
                    "Kuadran II: x negatif, y positif → (−, +)",
                    "Kuadran III: x negatif, y negatif → (−, −)",
                    "Kuadran IV: x positif, y negatif → (+, −)",
                    "Titik yang tepat berada di sumbu X atau sumbu Y tidak termasuk kuadran mana pun.",
                ],
            },
        ],
        "formulas": [
            {
                "expr": "P(x, y)",
                "label": "Penulisan titik koordinat",
                "symbols": [
                    ["P", "nama titik (huruf kapital)"],
                    ["x", "absis: jarak mendatar dari sumbu Y"],
                    ["y", "ordinat: jarak tegak dari sumbu X"],
                ],
            }
        ],
        "diagram": {
            "caption": "Empat titik di empat kuadran berbeda. Perhatikan tanda x dan y-nya!",
            "plane": {
                "range": 6,
                "quadrants": True,
                "points": [
                    {"x": 3, "y": 4, "label": "A(3, 4)"},
                    {"x": -4, "y": 2, "label": "B(−4, 2)"},
                    {"x": -2, "y": -3, "label": "C(−2, −3)"},
                    {"x": 4, "y": -2, "label": "D(4, −2)"},
                ],
            },
        },
        "daily": {
            "title": "Kursi bioskop dan peta",
            "body": "Tiket bioskop bertuliskan “Baris F, Kursi 7” — dua informasi untuk menunjuk satu tempat, mirip pasangan (x, y). Aplikasi peta di ponsel juga memakai dua angka (garis bujur dan lintang) untuk menunjukkan lokasimu.",
        },
        "examples": [
            {
                "title": "Menentukan kuadran",
                "question": "Tentukan letak titik A(3, 4), B(−2, 5), C(−4, −1), D(2, −3), dan E(0, −2).",
                "steps": [
                    "Periksa tanda x dan y setiap titik.",
                    "A(3, 4): x positif, y positif → Kuadran I.",
                    "B(−2, 5): x negatif, y positif → Kuadran II.",
                    "C(−4, −1): x negatif, y negatif → Kuadran III.",
                    "D(2, −3): x positif, y negatif → Kuadran IV.",
                    "E(0, −2): x = 0, jadi titik E berada tepat di sumbu Y (tidak di kuadran mana pun).",
                ],
                "answer": "A di Kuadran I, B di Kuadran II, C di Kuadran III, D di Kuadran IV, E di sumbu Y.",
            },
            {
                "title": "Membaca pergeseran",
                "question": "Dari titik O, sebuah titik P digeser 4 satuan ke kiri lalu 3 satuan ke atas. Tentukan koordinat P.",
                "steps": [
                    "4 satuan ke kiri → x = −4 (ke kiri berarti negatif).",
                    "3 satuan ke atas → y = 3 (ke atas berarti positif).",
                    "Tulis sebagai pasangan berurutan (x, y).",
                ],
                "answer": "P(−4, 3), terletak di Kuadran II.",
            },
        ],
        "fact": "Nama “Kartesius” berasal dari René Descartes (1596–1650), matematikawan Prancis. Konon idenya muncul saat ia berbaring dan memperhatikan seekor lalat di langit-langit kamar — ia ingin menyatakan posisi lalat itu dengan dua angka!",
        "activity": {
            "type": "place-points",
            "title": "Misi: Pasang Lampu Kota",
            "instructions": "Klik bidang koordinat untuk menempatkan setiap titik sesuai koordinat yang diminta. Titik yang benar akan menyala!",
            "range": 6,
            "targets": [[2, 3], [-3, 1], [-2, -4], [4, -2], [0, 3]],
        },
        "summary": [
            "Bidang Kartesius terdiri dari sumbu X (mendatar) dan sumbu Y (tegak) yang berpotongan di O(0, 0).",
            "Titik ditulis (x, y): x = absis, y = ordinat. Urutan tidak boleh tertukar.",
            "Kanan/atas bernilai positif, kiri/bawah bernilai negatif.",
            "Kuadran I (+, +), II (−, +), III (−, −), IV (+, −).",
        ],
    },
    # ------------------------------------------------------------------ 02
    {
        "slug": "point-detective",
        "no": 2,
        "region": "Point Detective",
        "title": "Memahami Titik dan Garis",
        "icon": "search",
        "xp": 100,
        "scar_intro": "Detektif Garis, siap bertugas? Di wilayah ini kita akan menyelidiki hubungan rahasia antara titik-titik dan garis lurus!",
        "objectives": [
            "Menjelaskan pengertian titik dan garis lurus.",
            "Memahami bahwa dua titik berbeda menentukan tepat satu garis lurus.",
            "Memeriksa apakah suatu titik terletak pada sebuah garis.",
            "Menentukan apakah beberapa titik segaris.",
        ],
        "concepts": [
            {
                "heading": "Titik",
                "body": "<b>Titik</b> menunjukkan sebuah <b>posisi</b>. Titik tidak memiliki panjang maupun lebar, dan diberi nama dengan huruf kapital, misalnya A(2, 3).",
            },
            {
                "heading": "Garis lurus",
                "body": "<b>Garis lurus</b> adalah kumpulan titik yang jumlahnya tak terhingga dan tersusun lurus, memanjang tanpa ujung ke dua arah. Di bidang koordinat kita menggambarnya dengan tanda panah di kedua ujung.",
            },
            {
                "heading": "Dua titik, satu garis",
                "body": "Melalui <b>dua titik yang berbeda</b> hanya dapat dibuat <b>tepat satu</b> garis lurus. Karena itu, untuk menggambar garis kita cukup mengetahui dua titik yang dilaluinya.",
            },
            {
                "heading": "Titik pada garis",
                "body": "Sebuah titik terletak pada garis jika koordinatnya <b>memenuhi persamaan garis</b>. Contoh: titik (2, 7) terletak pada garis y = 3x + 1 karena 3 × 2 + 1 = 7.",
            },
            {
                "heading": "Garis istimewa",
                "body": "Jika semua titik memiliki nilai y yang sama, garisnya <b>mendatar (horizontal)</b>, misalnya y = 4. Jika semua titik memiliki nilai x yang sama, garisnya <b>tegak (vertikal)</b>, misalnya x = −2.",
            },
        ],
        "formulas": [
            {
                "expr": "y₁ = m·x₁ + c  →  titik (x₁, y₁) terletak pada garis",
                "label": "Uji titik pada garis",
                "symbols": [
                    ["(x₁, y₁)", "titik yang diperiksa"],
                    ["m, c", "angka pada persamaan garis y = mx + c"],
                ],
            }
        ],
        "diagram": {
            "caption": "Titik A, B, dan C segaris: setiap bergeser 1 ke kanan, garis naik 2.",
            "plane": {
                "range": 6,
                "points": [
                    {"x": 0, "y": 1, "label": "A(0, 1)"},
                    {"x": 1, "y": 3, "label": "B(1, 3)"},
                    {"x": 2, "y": 5, "label": "C(2, 5)"},
                ],
                "lines": [{"m": 2, "c": 1, "label": "y = 2x + 1"}],
            },
        },
        "daily": {
            "title": "Tali jemuran dan laser",
            "body": "Saat tali jemuran ditarik kencang di antara dua tiang, tali membentuk garis lurus. Dua tiang = dua titik, dan hanya ada satu cara tali itu lurus! Sinar laser penunjuk juga merambat lurus.",
        },
        "examples": [
            {
                "title": "Apakah titik-titiknya segaris?",
                "question": "Periksa apakah titik A(1, 3), B(2, 5), dan C(4, 9) terletak pada satu garis lurus.",
                "steps": [
                    "Dari A ke B: x bertambah 1, y bertambah 2. Perbandingan 2 : 1 = 2.",
                    "Dari B ke C: x bertambah 2, y bertambah 4. Perbandingan 4 : 2 = 2.",
                    "Perbandingannya sama (sama-sama 2), jadi arah garisnya tidak berubah.",
                ],
                "answer": "A, B, dan C segaris.",
            },
            {
                "title": "Titik pada garis",
                "question": "Apakah titik P(3, 10) dan Q(2, 6) terletak pada garis y = 3x + 1?",
                "steps": [
                    "Substitusi P: x = 3 → y = 3 × 3 + 1 = 10. Hasilnya sama dengan ordinat P (10). ✓",
                    "Substitusi Q: x = 2 → y = 3 × 2 + 1 = 7. Ordinat Q adalah 6, tidak sama. ✗",
                ],
                "answer": "P terletak pada garis, Q tidak terletak pada garis.",
            },
        ],
        "fact": "Euclid, matematikawan Yunani kuno, mendefinisikan titik sebagai “sesuatu yang tidak memiliki bagian”. Bukunya, Elements, dipakai sebagai buku pelajaran geometri selama lebih dari 2.000 tahun!",
        "activity": {
            "type": "two-points",
            "title": "Misi: Hubungkan Dua Petunjuk",
            "instructions": "Klik dua titik berbeda pada bidang koordinat. SCAR akan menggambar garis yang melalui keduanya dan menjelaskan garis apa yang terbentuk.",
            "range": 6,
        },
        "summary": [
            "Titik menunjukkan posisi; garis lurus adalah kumpulan titik tak terhingga yang tersusun lurus.",
            "Dua titik berbeda menentukan tepat satu garis lurus.",
            "Titik terletak pada garis jika koordinatnya memenuhi persamaan garis.",
            "y = k adalah garis horizontal, x = k adalah garis vertikal.",
        ],
    },
    # ------------------------------------------------------------------ 03
    {
        "slug": "gradient-mountain",
        "no": 3,
        "region": "Gradient Mountain",
        "title": "Memahami Gradien",
        "icon": "mountain",
        "xp": 120,
        "scar_intro": "Siap mendaki Gradient Mountain? Ada lereng yang landai, ada yang curam, ada juga yang turun. Angka yang mengukur kemiringan itu disebut gradien!",
        "objectives": [
            "Menjelaskan gradien sebagai ukuran kemiringan garis.",
            "Membedakan gradien positif, negatif, nol, dan tidak terdefinisi.",
            "Menghitung gradien dari dua titik.",
            "Menentukan gradien dari persamaan garis.",
        ],
        "concepts": [
            {
                "heading": "Apa itu gradien?",
                "body": "<b>Gradien</b> (dilambangkan <b>m</b>) adalah tingkat kemiringan garis, yaitu perbandingan <b>perubahan tegak (Δy)</b> terhadap <b>perubahan mendatar (Δx)</b>. Bayangkan: “setiap melangkah 1 ke kanan, garis naik atau turun berapa?”",
            },
            {
                "heading": "Empat jenis gradien",
                "body": "Arah garis dibaca dari kiri ke kanan:",
                "bullets": [
                    "Gradien positif (m > 0): garis naik.",
                    "Gradien negatif (m < 0): garis turun.",
                    "Gradien nol (m = 0): garis mendatar/horizontal, karena Δy = 0.",
                    "Tidak terdefinisi: garis tegak/vertikal, karena Δx = 0 dan pembagian dengan nol tidak terdefinisi.",
                ],
            },
            {
                "heading": "Curam atau landai?",
                "body": "Semakin besar nilai mutlak gradien, semakin curam garisnya. Garis dengan m = 4 lebih curam daripada m = 1, dan garis dengan m = −4 juga lebih curam daripada m = −1 (hanya arahnya turun).",
            },
            {
                "heading": "Gradien dari persamaan",
                "body": "Pada <span class='math'>y = mx + c</span>, gradiennya adalah koefisien x, yaitu <b>m</b>. Pada bentuk <span class='math'>ax + by + c = 0</span>, gradiennya <span class='math'>m = −a/b</span>.",
            },
        ],
        "formulas": [
            {
                "expr": "m = Δy / Δx = (y₂ − y₁) / (x₂ − x₁)",
                "label": "Gradien dari dua titik",
                "symbols": [
                    ["m", "gradien (kemiringan garis)"],
                    ["(x₁, y₁)", "titik pertama"],
                    ["(x₂, y₂)", "titik kedua"],
                    ["Δy = y₂ − y₁", "perubahan tegak"],
                    ["Δx = x₂ − x₁", "perubahan mendatar (tidak boleh 0)"],
                ],
            },
            {
                "expr": "ax + by + c = 0  →  m = −a / b",
                "label": "Gradien dari bentuk umum",
                "symbols": [["a", "koefisien x"], ["b", "koefisien y (b ≠ 0)"]],
            },
        ],
        "diagram": {
            "caption": "Segitiga kemiringan: dari A ke B, Δx = 2 dan Δy = 6, sehingga m = 6/2 = 3.",
            "plane": {
                "range": 8,
                "points": [{"x": 1, "y": 2, "label": "A(1, 2)"}, {"x": 3, "y": 8, "label": "B(3, 8)"}],
                "lines": [{"m": 3, "c": -1, "label": "m = 3"}],
                "triangles": [{"from": [1, 2], "to": [3, 8]}],
            },
        },
        "daily": {
            "title": "Tanjakan dan ramp kursi roda",
            "body": "Rambu jalan “tanjakan 10%” berarti jalan naik 10 meter setiap 100 meter mendatar — gradiennya 10/100 = 0,1. Ramp kursi roda dibuat landai (sekitar 1 : 12) agar aman dinaiki.",
        },
        "examples": [
            {
                "title": "Gradien positif",
                "question": "Tentukan gradien garis yang melalui A(1, 2) dan B(3, 8).",
                "steps": [
                    "m = (y₂ − y₁) / (x₂ − x₁)",
                    "m = (8 − 2) / (3 − 1) = 6 / 2 = 3",
                    "m positif, jadi garis naik dari kiri ke kanan.",
                ],
                "answer": "m = 3",
            },
            {
                "title": "Gradien negatif",
                "question": "Tentukan gradien garis yang melalui P(−2, 4) dan Q(2, −4).",
                "steps": [
                    "m = (−4 − 4) / (2 − (−2))",
                    "m = −8 / 4 = −2",
                    "m negatif, jadi garis turun dari kiri ke kanan.",
                ],
                "answer": "m = −2",
            },
            {
                "title": "Gradien nol dan tidak terdefinisi",
                "question": "Tentukan gradien garis melalui (−1, 3) dan (4, 3), lalu garis melalui (2, 1) dan (2, 5).",
                "steps": [
                    "Garis pertama: m = (3 − 3) / (4 − (−1)) = 0 / 5 = 0 → garis horizontal.",
                    "Garis kedua: m = (5 − 1) / (2 − 2) = 4 / 0.",
                    "Pembagian dengan nol tidak terdefinisi → garis vertikal, gradien tidak terdefinisi.",
                ],
                "answer": "Garis pertama m = 0; garis kedua gradiennya tidak terdefinisi.",
            },
            {
                "title": "Gradien dari bentuk umum",
                "question": "Tentukan gradien garis 2x + 4y − 8 = 0.",
                "steps": [
                    "a = 2 dan b = 4.",
                    "m = −a / b = −2 / 4 = −1/2.",
                    "Cek dengan mengubah bentuk: 4y = −2x + 8 → y = −(1/2)x + 2. Koefisien x adalah −1/2. ✓",
                ],
                "answer": "m = −1/2",
            },
        ],
        "fact": "Kata “gradien” berasal dari bahasa Latin gradi yang berarti “melangkah”. Jalan raya terjal di dunia, Baldwin Street di Selandia Baru, memiliki kemiringan sekitar 35% — gradien kira-kira 0,35!",
        "activity": {
            "type": "gradient-lines",
            "title": "Misi: Ukur Lereng Gunung",
            "instructions": "Klik setiap garis untuk melihat segitiga kemiringannya, lalu tuliskan gradiennya. Gunakan Δy ÷ Δx!",
            "range": 6,
            "lines": [
                {"name": "Lereng A", "p1": [-2, -3], "p2": [1, 3]},
                {"name": "Lereng B", "p1": [-3, 2], "p2": [3, -1]},
                {"name": "Lereng C", "p1": [-4, 4], "p2": [3, 4]},
                {"name": "Lereng D", "p1": [0, -4], "p2": [3, 5]},
            ],
        },
        "summary": [
            "Gradien m = Δy / Δx = (y₂ − y₁)/(x₂ − x₁) menyatakan kemiringan garis.",
            "m > 0 naik, m < 0 turun, m = 0 horizontal, garis vertikal tidak memiliki gradien (tidak terdefinisi).",
            "Semakin besar nilai mutlak m, semakin curam garisnya.",
            "Pada y = mx + c gradiennya m; pada ax + by + c = 0 gradiennya −a/b.",
        ],
    },
    # ------------------------------------------------------------------ 04
    {
        "slug": "equation-factory",
        "no": 4,
        "region": "Equation Factory",
        "title": "Bentuk Persamaan Garis Lurus",
        "icon": "factory",
        "xp": 120,
        "scar_intro": "Selamat datang di pabrik persamaan! Di sini angka m dan c diolah menjadi garis lurus. Ubah angkanya, dan lihat garisnya ikut berubah!",
        "objectives": [
            "Menjelaskan pengertian persamaan garis lurus.",
            "Memahami arti x, y, m, dan c pada y = mx + c.",
            "Mengubah bentuk ax + by + c = 0 menjadi y = mx + c.",
            "Menggambar grafik dari persamaan garis lurus.",
        ],
        "concepts": [
            {
                "heading": "Persamaan garis lurus",
                "body": "Persamaan garis lurus adalah persamaan yang jika digambar pada bidang Kartesius membentuk garis lurus. Variabel <b>x</b> dan <b>y</b>-nya berpangkat satu. Setiap titik (x, y) pada garis pasti memenuhi persamaannya.",
            },
            {
                "heading": "Bentuk y = mx + c",
                "body": "Ini disebut bentuk <b>eksplisit</b> (y sendirian di ruas kiri).",
                "bullets": [
                    "x dan y: variabel, yaitu koordinat setiap titik pada garis.",
                    "m: gradien, menentukan kemiringan garis.",
                    "c: konstanta, menentukan titik potong garis dengan sumbu Y, yaitu (0, c).",
                ],
            },
            {
                "heading": "Bentuk ax + by + c = 0",
                "body": "Ini disebut bentuk <b>umum</b> atau implisit, dengan a, b, c bilangan real (a dan b tidak keduanya nol). Gradiennya <span class='math'>m = −a/b</span>. Untuk mengubahnya ke bentuk y = mx + c, “sendirikan” y di satu ruas. Hati-hati: huruf c di dua bentuk ini <b>tidak selalu bernilai sama</b>.",
            },
            {
                "heading": "Menggambar grafik",
                "body": "Cukup cari <b>dua titik</b> lalu hubungkan. Cara paling mudah: titik potong sumbu Y (substitusi x = 0) dan titik potong sumbu X (substitusi y = 0). Bisa juga membuat tabel nilai x dan y.",
            },
        ],
        "formulas": [
            {
                "expr": "y = mx + c",
                "label": "Bentuk eksplisit",
                "symbols": [["m", "gradien"], ["c", "titik potong sumbu Y di (0, c)"], ["x, y", "koordinat titik pada garis"]],
            },
            {
                "expr": "ax + by + c = 0",
                "label": "Bentuk umum",
                "symbols": [["a, b, c", "bilangan real, a dan b tidak keduanya nol"], ["m = −a/b", "gradien (jika b ≠ 0)"]],
            },
        ],
        "diagram": {
            "caption": "Grafik y = 2x − 4 memotong sumbu Y di (0, −4) dan sumbu X di (2, 0).",
            "plane": {
                "range": 6,
                "points": [{"x": 0, "y": -4, "label": "(0, −4)"}, {"x": 2, "y": 0, "label": "(2, 0)"}, {"x": 3, "y": 2, "label": "(3, 2)"}],
                "lines": [{"m": 2, "c": -4, "label": "y = 2x − 4"}],
            },
        },
        "daily": {
            "title": "Argo taksi",
            "body": "Sebuah taksi memasang tarif buka pintu Rp10.000 dan Rp5.000 per km. Biaya y untuk jarak x km adalah y = 5.000x + 10.000. Di sini m = 5.000 (tambahan biaya per km) dan c = 10.000 (biaya awal saat jarak masih 0).",
        },
        "examples": [
            {
                "title": "Menggambar y = 2x − 4",
                "question": "Gambarlah grafik y = 2x − 4.",
                "steps": [
                    "Titik potong sumbu Y: x = 0 → y = 2(0) − 4 = −4 → (0, −4).",
                    "Titik potong sumbu X: y = 0 → 0 = 2x − 4 → x = 2 → (2, 0).",
                    "Titik cek: x = 3 → y = 2(3) − 4 = 2 → (3, 2).",
                    "Hubungkan titik-titik tersebut menjadi garis lurus.",
                ],
                "answer": "Garis melalui (0, −4), (2, 0), dan (3, 2), dengan gradien 2.",
            },
            {
                "title": "Mengubah bentuk umum",
                "question": "Ubah 3x + 2y − 6 = 0 ke bentuk y = mx + c, lalu tentukan gradien dan titik potong sumbu Y.",
                "steps": [
                    "Pindahkan 3x dan −6 ke ruas kanan: 2y = −3x + 6.",
                    "Bagi kedua ruas dengan 2: y = −(3/2)x + 3.",
                    "Gradien m = −3/2 (cek: −a/b = −3/2 ✓). Titik potong sumbu Y: (0, 3).",
                ],
                "answer": "y = −(3/2)x + 3, m = −3/2, memotong sumbu Y di (0, 3).",
            },
        ],
        "fact": "Di Amerika Serikat, persamaan garis biasa ditulis y = mx + b, sedangkan di Inggris sering ditulis y = mx + c. Bentuknya sama, hanya hurufnya berbeda!",
        "activity": {
            "type": "equation-sliders",
            "title": "Misi: Nyalakan Mesin Garis",
            "instructions": "Geser slider m dan c. Perhatikan: m mengubah kemiringan, c menggeser garis naik-turun. Coba buat garis yang melewati titik target!",
            "range": 8,
            "target": {"m": -1, "c": 3},
        },
        "summary": [
            "Persamaan garis lurus jika digambar membentuk garis lurus; setiap titik pada garis memenuhi persamaannya.",
            "Pada y = mx + c: m = gradien, c = titik potong sumbu Y (0, c).",
            "Bentuk umum ax + by + c = 0 memiliki gradien m = −a/b.",
            "Untuk menggambar grafik cukup cari dua titik, misalnya titik potong sumbu X dan sumbu Y.",
        ],
    },
    # ------------------------------------------------------------------ 05
    {
        "slug": "line-constructor",
        "no": 5,
        "region": "Line Constructor",
        "title": "Menentukan Persamaan Garis Lurus",
        "icon": "crane",
        "xp": 150,
        "scar_intro": "Waktunya jadi arsitek garis! Dengan sedikit informasi — gradien, satu titik, atau dua titik — kamu bisa membangun persamaan garis yang utuh.",
        "objectives": [
            "Menentukan persamaan garis jika diketahui gradien dan satu titik.",
            "Menentukan persamaan garis jika diketahui dua titik.",
            "Menentukan persamaan garis jika diketahui gradien dan titik potong sumbu Y.",
            "Menentukan persamaan garis yang melalui titik pusat O(0, 0).",
        ],
        "concepts": [
            {
                "heading": "1. Gradien dan satu titik",
                "body": "Jika diketahui gradien <b>m</b> dan titik <b>(x₁, y₁)</b>, gunakan <span class='math'>y − y₁ = m(x − x₁)</span>, lalu sederhanakan menjadi y = mx + c.",
            },
            {
                "heading": "2. Dua titik",
                "body": "Jika diketahui dua titik, hitung dulu gradiennya dengan <span class='math'>m = (y₂ − y₁)/(x₂ − x₁)</span>. Setelah itu gunakan salah satu titik pada rumus y − y₁ = m(x − x₁). Titik mana pun yang dipakai, hasil akhirnya sama.",
            },
            {
                "heading": "3. Gradien dan titik potong sumbu Y",
                "body": "Jika garis memotong sumbu Y di <b>(0, c)</b> dan gradiennya <b>m</b>, persamaannya langsung <span class='math'>y = mx + c</span>.",
            },
            {
                "heading": "4. Melalui titik pusat",
                "body": "Garis yang melalui O(0, 0) memiliki c = 0, sehingga persamaannya <span class='math'>y = mx</span>.",
            },
        ],
        "formulas": [
            {
                "expr": "y − y₁ = m(x − x₁)",
                "label": "Gradien + satu titik",
                "symbols": [["m", "gradien"], ["(x₁, y₁)", "titik yang dilalui garis"]],
            },
            {
                "expr": "m = (y₂ − y₁)/(x₂ − x₁), lalu y − y₁ = m(x − x₁)",
                "label": "Dua titik",
                "symbols": [["(x₁, y₁), (x₂, y₂)", "dua titik yang dilalui garis (x₁ ≠ x₂)"]],
            },
            {
                "expr": "y = mx + c",
                "label": "Gradien + titik potong sumbu Y",
                "symbols": [["c", "ordinat titik potong sumbu Y (0, c)"]],
            },
            {
                "expr": "y = mx",
                "label": "Melalui titik pusat O(0, 0)",
                "symbols": [["m", "gradien; konstanta c = 0"]],
            },
        ],
        "diagram": {
            "caption": "Garis y = 3x − 2 dibangun dari dua titik (1, 1) dan (3, 7).",
            "plane": {
                "range": 8,
                "points": [{"x": 1, "y": 1, "label": "(1, 1)"}, {"x": 3, "y": 7, "label": "(3, 7)"}],
                "lines": [{"m": 3, "c": -2, "label": "y = 3x − 2"}],
                "triangles": [{"from": [1, 1], "to": [3, 7]}],
            },
        },
        "daily": {
            "title": "Paket kuota internet",
            "body": "Sebuah provider menjual kuota: setiap tambah 1 GB harganya naik Rp10.000, dan paket 3 GB seharga Rp50.000. Gradien m = 10.000 dan titik (3, 50.000) → y − 50.000 = 10.000(x − 3) → y = 10.000x + 20.000.",
        },
        "examples": [
            {
                "title": "Gradien dan satu titik",
                "question": "Tentukan persamaan garis bergradien 3 yang melalui titik (2, 5).",
                "steps": [
                    "y − y₁ = m(x − x₁)",
                    "y − 5 = 3(x − 2)",
                    "y − 5 = 3x − 6",
                    "y = 3x − 6 + 5 = 3x − 1",
                    "Cek: x = 2 → y = 3(2) − 1 = 5 ✓",
                ],
                "answer": "y = 3x − 1",
            },
            {
                "title": "Dua titik",
                "question": "Tentukan persamaan garis yang melalui (1, 1) dan (3, 7).",
                "steps": [
                    "m = (7 − 1)/(3 − 1) = 6/2 = 3",
                    "Gunakan titik (1, 1): y − 1 = 3(x − 1)",
                    "y − 1 = 3x − 3",
                    "y = 3x − 2",
                    "Cek titik (3, 7): 3(3) − 2 = 7 ✓",
                ],
                "answer": "y = 3x − 2",
            },
            {
                "title": "Gradien dan titik potong sumbu Y",
                "question": "Sebuah garis bergradien −2 memotong sumbu Y di (0, 4). Tentukan persamaannya.",
                "steps": ["m = −2 dan c = 4.", "y = mx + c → y = −2x + 4"],
                "answer": "y = −2x + 4",
            },
            {
                "title": "Melalui titik pusat",
                "question": "Tentukan persamaan garis yang melalui O(0, 0) dan (3, 6).",
                "steps": ["m = (6 − 0)/(3 − 0) = 2", "Garis melalui O, jadi c = 0.", "y = 2x"],
                "answer": "y = 2x",
            },
        ],
        "fact": "Dua titik cukup untuk menentukan garis. Itulah sebabnya tukang bangunan cukup memasang dua patok lalu menarik benang di antaranya untuk membuat garis lurus saat memasang batu bata!",
        "activity": {
            "type": "construct",
            "title": "Misi: Bangun Garis dari Petunjuk",
            "instructions": "Baca petunjuknya, hitung nilai m dan c, lalu tekan Bangun. Garismu akan digambar dan dibandingkan dengan garis rahasia!",
            "range": 8,
            "challenges": [
                {"clue": "Gradien 2 dan melalui titik (1, 5).", "m": "2", "c": "3", "show": [[1, 5]]},
                {"clue": "Melalui dua titik (−2, 6) dan (2, −2).", "m": "-2", "c": "2", "show": [[-2, 6], [2, -2]]},
                {"clue": "Gradien 1/2 dan memotong sumbu Y di (0, −3).", "m": "1/2", "c": "-3", "show": [[0, -3]]},
                {"clue": "Melalui titik pusat dan titik (2, −6).", "m": "-3", "c": "0", "show": [[0, 0], [2, -6]]},
            ],
        },
        "summary": [
            "Gradien + satu titik: y − y₁ = m(x − x₁).",
            "Dua titik: hitung m dulu, lalu pakai y − y₁ = m(x − x₁).",
            "Gradien + titik potong sumbu Y (0, c): y = mx + c.",
            "Melalui titik pusat: y = mx.",
            "Selalu cek jawaban dengan mensubstitusi titik yang diketahui.",
        ],
    },
    # ------------------------------------------------------------------ 06
    {
        "slug": "parallel-perpendicular",
        "no": 6,
        "region": "Parallel & Perpendicular World",
        "title": "Hubungan Antargaris",
        "icon": "parallel",
        "xp": 150,
        "scar_intro": "Di dunia ini ada garis yang berjalan berdampingan selamanya, ada juga yang bertemu membentuk sudut siku-siku. Rahasianya ada pada gradien!",
        "objectives": [
            "Membedakan garis sejajar, berpotongan, dan tegak lurus.",
            "Menggunakan hubungan gradien garis sejajar (m₁ = m₂).",
            "Menggunakan hubungan gradien garis tegak lurus (m₁ × m₂ = −1).",
            "Menentukan persamaan garis yang sejajar atau tegak lurus garis lain.",
        ],
        "concepts": [
            {
                "heading": "Garis sejajar (∥)",
                "body": "Dua garis sejajar <b>tidak pernah berpotongan</b> karena kemiringannya sama. Syaratnya <span class='math'>m₁ = m₂</span> dengan titik potong sumbu Y berbeda. Jika gradien dan c-nya sama, kedua garis <b>berimpit</b> (sebenarnya garis yang sama).",
            },
            {
                "heading": "Garis berpotongan",
                "body": "Dua garis dengan gradien <b>berbeda</b> pasti berpotongan di tepat satu titik.",
            },
            {
                "heading": "Garis tegak lurus (⊥)",
                "body": "Garis tegak lurus adalah garis berpotongan yang membentuk sudut <b>90°</b>. Untuk garis yang gradiennya terdefinisi berlaku <span class='math'>m₁ × m₂ = −1</span>, atau <span class='math'>m₂ = −1/m₁</span> (“negatif kebalikan”).",
            },
            {
                "heading": "Kasus khusus",
                "body": "Garis horizontal (m = 0) tegak lurus dengan garis vertikal (gradien tidak terdefinisi). Rumus m₁ × m₂ = −1 tidak dapat dipakai di sini karena salah satu gradiennya tidak terdefinisi.",
            },
        ],
        "formulas": [
            {"expr": "m₁ = m₂", "label": "Garis sejajar", "symbols": [["m₁", "gradien garis pertama"], ["m₂", "gradien garis kedua"]]},
            {
                "expr": "m₁ × m₂ = −1  ⟺  m₂ = −1/m₁",
                "label": "Garis tegak lurus (gradien terdefinisi)",
                "symbols": [["−1/m₁", "negatif kebalikan dari m₁"]],
            },
        ],
        "diagram": {
            "caption": "y = 2x + 1 sejajar y = 2x − 3, dan keduanya tegak lurus y = −(1/2)x + 4.",
            "plane": {
                "range": 6,
                "lines": [
                    {"m": 2, "c": 1, "label": "y = 2x + 1"},
                    {"m": 2, "c": -3, "label": "y = 2x − 3"},
                    {"m": -0.5, "c": 4, "label": "y = −½x + 4", "color": "teal"},
                ],
            },
        },
        "daily": {
            "title": "Rel kereta dan perempatan",
            "body": "Dua rel kereta api dibuat sejajar agar roda kereta tetap berjalan — jaraknya selalu sama. Jalan di perempatan sering dibuat saling tegak lurus, membentuk sudut siku-siku seperti tanda “+”.",
        },
        "examples": [
            {
                "title": "Memeriksa hubungan garis",
                "question": "Tentukan hubungan garis y = 2x + 1 dengan (a) y = 2x − 3 dan (b) y = −(1/2)x + 4.",
                "steps": [
                    "(a) m₁ = 2 dan m₂ = 2. Gradien sama, c berbeda → sejajar.",
                    "(b) m₁ = 2 dan m₂ = −1/2. m₁ × m₂ = 2 × (−1/2) = −1 → tegak lurus.",
                ],
                "answer": "(a) sejajar, (b) tegak lurus.",
            },
            {
                "title": "Garis sejajar melalui sebuah titik",
                "question": "Tentukan persamaan garis yang melalui (1, 2) dan sejajar dengan y = 3x − 5.",
                "steps": [
                    "Sejajar → gradiennya sama: m = 3.",
                    "y − 2 = 3(x − 1)",
                    "y − 2 = 3x − 3",
                    "y = 3x − 1",
                ],
                "answer": "y = 3x − 1",
            },
            {
                "title": "Garis tegak lurus melalui sebuah titik",
                "question": "Tentukan persamaan garis yang melalui (2, 3) dan tegak lurus dengan y = 2x + 1.",
                "steps": [
                    "m₁ = 2, maka m₂ = −1/2 (karena 2 × (−1/2) = −1).",
                    "y − 3 = −(1/2)(x − 2)",
                    "y − 3 = −(1/2)x + 1",
                    "y = −(1/2)x + 4",
                    "Cek: x = 2 → y = −1 + 4 = 3 ✓",
                ],
                "answer": "y = −(1/2)x + 4",
            },
        ],
        "fact": "Simbol ∥ (sejajar) dan ⊥ (tegak lurus) sudah dipakai matematikawan sejak abad ke-17. Simbol ⊥ diperkenalkan oleh Pierre Hérigone pada tahun 1634!",
        "activity": {
            "type": "pair-lines",
            "title": "Misi: Cari Pasangan Garis",
            "instructions": "Klik dua garis (dari daftar atau grafik) lalu tekan Periksa. Temukan satu pasangan garis SEJAJAR dan satu pasangan garis TEGAK LURUS!",
            "range": 6,
            "lines": [
                {"id": "L1", "m": "1", "c": "2"},
                {"id": "L2", "m": "1", "c": "-3"},
                {"id": "L3", "m": "2", "c": "-1"},
                {"id": "L4", "m": "-1/2", "c": "3"},
                {"id": "L5", "m": "-3", "c": "1"},
                {"id": "L6", "m": "0", "c": "-4"},
            ],
            "parallel": ["L1", "L2"],
            "perpendicular": ["L3", "L4"],
        },
        "summary": [
            "Sejajar: m₁ = m₂ (dan c berbeda). Jika c juga sama, garisnya berimpit.",
            "Berpotongan: gradien berbeda.",
            "Tegak lurus: m₁ × m₂ = −1, atau m₂ = −1/m₁.",
            "Garis horizontal tegak lurus dengan garis vertikal.",
        ],
    },
    # ------------------------------------------------------------------ 07
    {
        "slug": "real-life",
        "no": 7,
        "region": "Real Life Line Adventure",
        "title": "Persamaan Garis dalam Kehidupan Sehari-hari",
        "icon": "house",
        "xp": 150,
        "scar_intro": "Persamaan garis lurus bukan cuma di buku! Tarif ojek, tagihan air, sampai tinggi tanaman bisa dihitung dengannya. Ayo, jelajahi dunia nyata bersamaku!",
        "objectives": [
            "Membuat model persamaan garis dari situasi sehari-hari.",
            "Mengartikan gradien sebagai laju perubahan dan c sebagai nilai awal.",
            "Menyelesaikan soal cerita dengan persamaan garis lurus.",
            "Membandingkan dua pola perubahan linear.",
        ],
        "concepts": [
            {
                "heading": "Model linear",
                "body": "Situasi dengan <b>perubahan yang tetap</b> dapat dimodelkan dengan y = mx + c.",
                "bullets": [
                    "m = laju perubahan (misalnya rupiah per km, cm per hari).",
                    "c = nilai awal (nilai y ketika x = 0).",
                    "x = variabel bebas (jarak, waktu, banyak barang).",
                    "y = hasil (biaya, posisi, tinggi).",
                ],
            },
            {
                "heading": "Langkah menyelesaikan soal cerita",
                "body": "1) Tulis yang diketahui. 2) Tentukan m dan c. 3) Tulis persamaannya. 4) Substitusi nilai yang ditanyakan. 5) Tafsirkan hasilnya dalam kalimat.",
            },
        ],
        "formulas": [
            {
                "expr": "y = mx + c",
                "label": "Model situasi linear",
                "symbols": [["m", "laju perubahan per satuan x"], ["c", "nilai awal (saat x = 0)"]],
            }
        ],
        "diagram": {
            "caption": "Tinggi tanaman y = 2x + 4: mulai 4 cm, tumbuh 2 cm per hari.",
            "plane": {
                "range": 10,
                "first_quadrant": True,
                "points": [{"x": 0, "y": 4, "label": "hari 0: 4 cm"}, {"x": 3, "y": 10, "label": "hari 3: 10 cm"}],
                "lines": [{"m": 2, "c": 4, "label": "y = 2x + 4"}],
            },
        },
        "daily": {
            "title": "Di mana-mana ada garis lurus",
            "body": "Tarif ojek online, biaya parkir per jam, tagihan air PDAM, jarak tempuh kendaraan dengan kecepatan tetap — semuanya bisa digambar sebagai garis lurus jika perubahannya tetap.",
        },
        "examples": [],
        "fact": "Ahli ekonomi, dokter, dan ilmuwan iklim sering memakai “regresi linear”, yaitu mencari garis lurus yang paling cocok untuk sekumpulan data. Itu adalah pengembangan dari persamaan y = mx + c yang kamu pelajari!",
        "activity": {"type": "real-life", "title": "Misi: Selesaikan Kasus Kota", "instructions": "Baca setiap kasus, tulis jawabanmu, lalu tekan Periksa. Setelah itu, buka langkah penyelesaian lengkapnya."},
        "cases": [
            {
                "icon": "bike",
                "title": "Biaya perjalanan ojek online",
                "known": ["Tarif dasar Rp8.000.", "Biaya tambahan Rp2.500 per km."],
                "question": "Berapa biaya perjalanan sejauh 6 km?",
                "formula": "y = mx + c, dengan m = 2.500 dan c = 8.000",
                "steps": ["Model: y = 2.500x + 8.000", "Substitusi x = 6: y = 2.500(6) + 8.000", "y = 15.000 + 8.000 = 23.000"],
                "answer": "23000",
                "answer_text": "Rp23.000",
                "interpretation": "Setiap 1 km menambah Rp2.500 (gradien). Rp8.000 tetap dibayar walaupun baru berangkat (konstanta).",
                "unit": "rupiah",
            },
            {
                "icon": "drop",
                "title": "Tagihan air berdasarkan pemakaian",
                "known": ["Biaya abonemen Rp15.000 per bulan.", "Biaya pemakaian Rp3.000 per m³.", "Tagihan bulan ini Rp60.000."],
                "question": "Berapa m³ air yang dipakai bulan ini?",
                "formula": "y = 3.000x + 15.000",
                "steps": ["60.000 = 3.000x + 15.000", "3.000x = 60.000 − 15.000 = 45.000", "x = 45.000 ÷ 3.000 = 15"],
                "answer": "15",
                "answer_text": "15 m³",
                "interpretation": "Dari tagihan Rp60.000, sebanyak Rp15.000 adalah abonemen; sisanya Rp45.000 untuk 15 m³ air.",
                "unit": "m³",
            },
            {
                "icon": "car",
                "title": "Waktu dan jarak",
                "known": ["Mobil melaju dengan kecepatan tetap 60 km/jam.", "Saat mulai diamati, mobil sudah berada 20 km dari kota A."],
                "question": "Berapa jarak mobil dari kota A setelah 3 jam?",
                "formula": "s = 60t + 20",
                "steps": ["Model: s = 60t + 20 (s dalam km, t dalam jam)", "t = 3: s = 60(3) + 20", "s = 180 + 20 = 200"],
                "answer": "200",
                "answer_text": "200 km",
                "interpretation": "Gradien 60 adalah kecepatan: setiap 1 jam jarak bertambah 60 km.",
                "unit": "km",
            },
            {
                "icon": "book",
                "title": "Jumlah barang dan harga",
                "known": ["Harga 3 buku tulis Rp15.000.", "Harga 7 buku tulis Rp35.000.", "Harga berubah secara linear."],
                "question": "Berapa harga 10 buku tulis?",
                "formula": "m = (y₂ − y₁)/(x₂ − x₁), lalu y = mx + c",
                "steps": [
                    "Titik (3, 15.000) dan (7, 35.000).",
                    "m = (35.000 − 15.000)/(7 − 3) = 20.000/4 = 5.000",
                    "y − 15.000 = 5.000(x − 3) → y = 5.000x",
                    "x = 10: y = 5.000 × 10 = 50.000",
                ],
                "answer": "50000",
                "answer_text": "Rp50.000",
                "interpretation": "Harga satu buku Rp5.000. Karena c = 0, garisnya melalui titik pusat: 0 buku harganya Rp0.",
                "unit": "rupiah",
            },
            {
                "icon": "plant",
                "title": "Membaca grafik pertumbuhan",
                "known": ["Grafik tinggi tanaman berupa garis lurus.", "Hari ke-0 tingginya 4 cm.", "Hari ke-5 tingginya 14 cm."],
                "question": "Berapa tinggi tanaman pada hari ke-12?",
                "formula": "y = mx + c",
                "steps": ["m = (14 − 4)/(5 − 0) = 10/5 = 2 cm per hari", "c = 4 (tinggi awal)", "y = 2x + 4", "x = 12: y = 2(12) + 4 = 28"],
                "answer": "28",
                "answer_text": "28 cm",
                "interpretation": "Tanaman tumbuh 2 cm setiap hari. Model ini hanya berlaku selama pertumbuhannya tetap.",
                "unit": "cm",
                "plane": {"range": 16, "first_quadrant": True, "lines": [{"m": 2, "c": 4}], "points": [{"x": 0, "y": 4, "label": "(0, 4)"}, {"x": 5, "y": 14, "label": "(5, 14)"}]},
            },
            {
                "icon": "road",
                "title": "Kemiringan jalan",
                "known": ["Sebuah jalan naik setinggi 15 m.", "Jarak mendatarnya 300 m."],
                "question": "Berapa persen kemiringan jalan tersebut?",
                "formula": "m = Δy / Δx, persen = m × 100%",
                "steps": ["m = 15 / 300 = 1/20 = 0,05", "Persen kemiringan = 0,05 × 100% = 5%"],
                "answer": "5",
                "answer_text": "5%",
                "interpretation": "Jalan naik 5 m untuk setiap 100 m mendatar — tanjakan yang cukup landai.",
                "unit": "%",
            },
            {
                "icon": "compare",
                "title": "Membandingkan dua pola perubahan",
                "known": ["Rental sepeda A: Rp10.000 + Rp5.000 per jam.", "Rental sepeda B: Rp20.000 + Rp3.000 per jam."],
                "question": "Setelah berapa jam biaya kedua rental sama?",
                "formula": "y_A = 5.000x + 10.000 dan y_B = 3.000x + 20.000",
                "steps": ["Samakan: 5.000x + 10.000 = 3.000x + 20.000", "5.000x − 3.000x = 20.000 − 10.000", "2.000x = 10.000 → x = 5"],
                "answer": "5",
                "answer_text": "5 jam",
                "interpretation": "Pada 5 jam biayanya sama (Rp35.000). Kurang dari 5 jam, A lebih murah; lebih dari 5 jam, B lebih murah karena gradiennya lebih kecil.",
                "unit": "jam",
                "plane": {"range": 10, "first_quadrant": True, "lines": [{"m": 0.5, "c": 1, "label": "A (×Rp10rb)"}, {"m": 0.3, "c": 2, "label": "B (×Rp10rb)", "color": "teal"}], "points": [{"x": 5, "y": 3.5, "label": "(5 jam, Rp35rb)"}]},
            },
        ],
        "summary": [
            "Situasi dengan perubahan tetap dapat dimodelkan y = mx + c.",
            "Gradien = laju perubahan; konstanta c = nilai awal.",
            "Soal cerita: tulis diketahui → tentukan m dan c → susun persamaan → substitusi → tafsirkan.",
            "Dua model linear dapat dibandingkan dengan mencari titik potongnya.",
        ],
    },
]

LESSON_BY_SLUG = {lesson["slug"]: lesson for lesson in LESSONS}
LESSON_ORDER = [lesson["slug"] for lesson in LESSONS]


def next_lesson(slug):
    idx = LESSON_ORDER.index(slug)
    return LESSONS[idx + 1] if idx + 1 < len(LESSONS) else None


def prev_lesson(slug):
    idx = LESSON_ORDER.index(slug)
    return LESSONS[idx - 1] if idx > 0 else None
