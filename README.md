# SCARLINE — Discover the Line, Master the Equation!

**SCARLINE** adalah platform pembelajaran matematika interaktif untuk siswa **SMP kelas VIII** dengan materi utama **Persamaan Garis Lurus**. Siswa menjelajahi *SCARLINE WORLD* bersama maskot **SCAR**: membuka 7 wilayah misi, bereksperimen di Coordinate Laboratory, berlatih di Training Zone, bermain 5 game edukatif, lalu menuntaskan Final Line Challenge.

Tema visual: **Vintage Mathematics Laboratory** — kertas grafik, buku catatan, papan tulis, dan stempel retro.

| Lapisan | Teknologi |
|---|---|
| Backend | **Python 3.11+**, Flask 3, requests |
| Frontend | **JavaScript** (ES2017, tanpa framework), SVG, CSS |
| Autentikasi & database | Supabase Auth, PostgreSQL, Row Level Security |
| Pengujian | pytest (175 test), esprima (cek sintaks JS) |
| Deployment | Vercel (runtime Python) |

> Repo ini sengaja memakai **Python + JavaScript**. File `.gitattributes` mengecualikan HTML/CSS/SQL dari statistik bahasa GitHub, sehingga bilah bahasa repo menampilkan **Python** dan **JavaScript**.

---

## Daftar isi
1. [Fitur](#fitur)
2. [Struktur folder](#struktur-folder)
3. [Instalasi & menjalankan lokal](#instalasi--menjalankan-lokal)
4. [Membuat & mengonfigurasi Supabase](#membuat--mengonfigurasi-supabase)
5. [Migrasi database & seed](#migrasi-database--seed)
6. [Pengujian](#pengujian)
7. [Deployment ke Vercel](#deployment-ke-vercel)
8. [Arsitektur & keamanan](#arsitektur--keamanan)
9. [Aturan XP, level, dan lencana](#aturan-xp-level-dan-lencana)
10. [Pemecahan masalah](#pemecahan-masalah)

---

## Fitur

**Autentikasi (Supabase Auth, bukan login palsu)**
- Registrasi: nama lengkap, username (unik), email, kelas, password + konfirmasi; validasi lengkap & pesan kesalahan ramah.
- Login dengan tombol tampil/sembunyikan password, lupa password (email pemulihan), reset password, logout.
- Semua halaman belajar bersifat privat; pengunjung tanpa login diarahkan ke halaman masuk.

**Pembelajaran**
- **Landing page**: hero, About, What Will You Learn, Featured Features, How to Play.
- **Dashboard “SCAR’s Mathematics Headquarters”**: sapaan, level (dial), XP, progres, misi, game, lencana, aktivitas terakhir, rekomendasi, perjalanan SCARLINE WORLD, tantangan harian, 6 tombol aksi.
- **Straight Line Adventure Map**: 7 wilayah + Final Mission; misi berikutnya terbuka setelah misi sebelumnya selesai; misi terbuka bisa diulang.
- **7 misi** dengan format lengkap: wilayah, nomor, judul, tujuan, konsep, rumus + arti simbol, diagram, contoh sehari-hari, contoh soal bertahap (tampil langkah demi langkah), fakta menarik, **aktivitas interaktif**, mini quiz (lulus ≥ 2/3), rangkuman, tombol selesai & lanjut.

| Misi | Wilayah | Aktivitas interaktif |
|---|---|---|
| 01 | Coordinate City | Klik bidang untuk memasang titik (umpan balik x/y tertukar, arah salah) |
| 02 | Point Detective | Pilih dua titik → garis tergambar + penjelasan |
| 03 | Gradient Mountain | Ukur gradien 4 lereng dengan segitiga Δx/Δy |
| 04 | Equation Factory | Slider m & c, capai garis target |
| 05 | Line Constructor | Susun m & c dari petunjuk, garis dibandingkan |
| 06 | Parallel & Perpendicular World | Temukan pasangan sejajar & tegak lurus |
| 07 | Real Life Line Adventure | 7 kasus nyata (ilustrasi, diketahui, ditanya, rumus, langkah, jawaban, interpretasi) + simulasi dua rental |

**Coordinate Laboratory** — bidang Kartesius interaktif (tambah/geser/hapus/hubungkan titik, zoom, snap 0,5, info kuadran), **Gradient Simulator** (positif/negatif/nol/tidak terdefinisi), **Equation to Graph** (titik potong X & Y, tabel titik, bentuk umum, penjelasan perubahan), **Two Points to Line** (validasi garis vertikal), **Equation Calculator** (5 metode, langkah penyelesaian dihitung di server Python dengan pecahan eksak).

**Training Zone** — 3 level (Line Beginner, Gradient Explorer, Equation Master), 36 soal dengan 10 tipe: pilihan ganda, benar/salah, isian angka, menentukan koordinat (klik), mengidentifikasi gradien, melengkapi persamaan, menentukan persamaan, membaca grafik, memasangkan garis, soal cerita. Jawaban salah → SCAR menjelaskan letak kesalahan (mis. “tanda gradien terbalik”, “Δx dan Δy tertukar”, “x dan y tertukar”).

**SCAR’s Playground — 5 game dengan mekanisme berbeda** (masing-masing punya petunjuk, aturan, 3 tingkat kesulitan, skor, umpan balik, hasil akhir, main lagi, dan riwayat tersimpan):

| Game | Mekanisme |
|---|---|
| Coordinate Hunter | Klik titik koordinat di bidang |
| Gradient Rush | Atur slider Δy/Δx jembatan + pilih garis; bonus kecepatan dihitung server |
| Line Builder | Tuas m & c, mesin menggambar garis vs target |
| Equation Puzzle | Drag & drop (atau ketuk) potongan rumus ke slot |
| SCAR’s Line Rescue | Peta petualangan bertahap, 3 nyawa, tantangan campuran |

**Final Line Challenge** — 10/15/20/25 soal dipilih berimbang dari 8 topik, timer opsional, navigasi nomor soal, tandai ragu-ragu, tinjau sebelum kirim, kunci tidak dikirim selama evaluasi, pembahasan setelah selesai, riwayat tersimpan.

**Gamifikasi** — XP, 7 level, 9 lencana (notifikasi toast), bintang 1–3, progres misi, tantangan harian. **Profil** (data akun, statistik, edit nama/kelas) dan **Riwayat** (log aktivitas dengan filter, nilai latihan/evaluasi, hasil game).

---

## Struktur folder

```
.
├── app.py                      # Titik masuk Flask (lokal & Vercel)
├── requirements.txt            # Dependensi produksi
├── requirements-dev.txt        # + pytest, esprima
├── .env.example                # Contoh konfigurasi
├── vercel.json                 # Konfigurasi deploy Vercel
├── scarline/                   # Paket aplikasi (Python)
│   ├── __init__.py             # create_app(), filter & macro global Jinja
│   ├── config.py               # Konfigurasi dari environment
│   ├── supabase_client.py      # Klien Supabase Auth + PostgREST
│   ├── security.py             # Sesi login, login_required, CSRF, header keamanan
│   ├── auth.py                 # Registrasi, login, lupa/reset password, logout
│   ├── views.py                # Halaman (dashboard, peta, misi, lab, dll.)
│   ├── api.py                  # API JSON: sesi aktivitas, misi selesai, kalkulator
│   ├── runs.py                 # Sesi kuis/game: soal dibuat server, dinilai server
│   ├── grading.py              # Penilaian + diagnosis kesalahan
│   ├── services.py             # Progres, XP, level, lencana, riwayat
│   ├── mathcore.py             # Mesin matematika (Fraction eksak) + langkah penyelesaian
│   ├── content/                # Materi 7 misi, bank soal, lencana, kalimat SCAR
│   ├── games/                  # Generator ronde 5 game (Python)
│   ├── templates/              # Template Jinja (HTML)
│   └── static/
│       ├── css/scarline.css    # Sistem desain Vintage Mathematics Laboratory
│       ├── img/favicon.svg
│       └── js/                 # core, plane (SVG Kartesius), quiz, lesson, lab, final, games/*
├── supabase/
│   ├── migrations/001_scarline_schema.sql   # Tabel, trigger, RLS
│   └── seed.sql                              # Data materi/soal/game/lencana (dibuat otomatis)
├── scripts/
│   ├── generate_seed.py        # Membuat supabase/seed.sql dari konten Python
│   └── check_js.py             # Cek sintaks semua file JavaScript
└── tests/                      # pytest + Supabase tiruan khusus pengujian
```

---

## Instalasi & menjalankan lokal

Prasyarat: **Python 3.11+** dan akun **Supabase** (gratis). Node.js tidak diperlukan.

```bash
# 1. Buat virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. Pasang dependensi
pip install -r requirements-dev.txt

# 3. Konfigurasi
cp .env.example .env        # Windows: copy .env.example .env
#   lalu isi SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, FLASK_SECRET_KEY

# 4. Jalankan
python app.py
```

Buka **http://localhost:5000**. Tanpa kredensial Supabase, halaman publik tetap tampil dan halaman login/registrasi menampilkan pemberitahuan konfigurasi — aplikasi **tidak** membuat login palsu.

---

## Membuat & mengonfigurasi Supabase

1. Masuk ke <https://supabase.com> → **New project**. Catat password database.
2. **Project Settings → API**, salin ke `.env`:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` → `SUPABASE_ANON_KEY`
   - `service_role` (rahasia) → `SUPABASE_SERVICE_ROLE_KEY` — **hanya** untuk server, jangan pernah ditaruh di JavaScript/browser.
3. **Authentication → URL Configuration**
   - *Site URL*: `http://localhost:5000` (atau domain Vercel Anda).
   - *Redirect URLs*: tambahkan `http://localhost:5000/login`, `http://localhost:5000/reset-password`, dan versi domain produksinya.
4. **Authentication → Providers → Email**: aktif. Secara default SCARLINE membuat akun lewat Admin API di server (`REQUIRE_EMAIL_CONFIRMATION=0`), jadi siswa langsung bisa masuk tanpa email konfirmasi dan tidak terkena batas kirim email bawaan Supabase (±2 email/jam). Set `REQUIRE_EMAIL_CONFIRMATION=1` bila ingin mewajibkan konfirmasi email (sebaiknya dengan SMTP sendiri).
5. (Opsional) **Authentication → Email Templates**: sesuaikan bahasa email.

## Migrasi database & seed

1. Buka **SQL Editor** di dashboard Supabase.
2. Jalankan isi `supabase/migrations/001_scarline_schema.sql` (membuat 13 tabel, trigger profil otomatis, dan seluruh kebijakan RLS).
3. Jalankan isi `supabase/seed.sql` (7 misi, 12 kuis, 82 soal, 5 game, 9 lencana).

Jika Anda mengubah materi/soal di `scarline/content/`, buat ulang seed:

```bash
python scripts/generate_seed.py
```

Dengan Supabase CLI (opsional): `supabase db push` lalu `psql "$DATABASE_URL" -f supabase/seed.sql`.

**Tabel:** `profiles`, `lessons`, `lesson_progress`, `quizzes`, `quiz_questions`, `quiz_attempts`, `games`, `game_attempts`, `user_stats`, `achievements`, `user_achievements`, `activity_logs`, `daily_claims`. Semua memakai UUID dari Supabase Auth, foreign key, dan timestamp.

---

## Pengujian

```bash
python -m pytest -q            # 175 test: matematika, bank soal, game, auth, alur belajar, XP, RLS
python scripts/check_js.py     # cek sintaks seluruh JavaScript
```

Cakupan test otomatis:
- **Matematika**: parser pecahan, gradien (positif/negatif/nol/tidak terdefinisi), persamaan dari titik-gradien/dua titik/titik potong/titik pusat, bentuk umum, hubungan garis, kuadran.
- **Bank soal**: setiap kunci jawaban dinilai benar, setiap soal punya pembahasan, kunci tidak ikut data publik, diagnosis kesalahan spesifik.
- **Game**: 5 game × 3 tingkat × 120 seed — setiap ronde dapat diselesaikan dan deterministik dari seed.
- **Autentikasi**: registrasi & validasi, username unik, password salah, kolom kosong, open redirect, CSRF, lupa password, logout, perlindungan seluruh halaman privat.
- **Alur belajar**: mini quiz → selesai misi, misi terkunci, XP tidak bertambah saat diulang/refresh, tantangan harian sekali sehari, kelima game dimainkan & tersimpan, skor dari browser diabaikan, nyawa Line Rescue, Final terkunci → terbuka, perjalanan lengkap sampai lencana SCARLINE Champion, siswa lain tidak bisa melihat riwayat.
- **Lab**: kelima metode kalkulator + input tidak valid.

Test memakai `tests/fakes.py` (Supabase tiruan **khusus pengujian**). Selain itu, seluruh halaman dan kelima game telah diuji di browser Edge headless (klik, jawab, selesaikan) tanpa error JavaScript, termasuk lebar layar 390 px.

**Uji manual dengan Supabase asli** (checklist): daftar akun baru → cek baris `profiles` & `user_stats` terbuat → login/logout → lupa password (cek email) → selesaikan Mission 01 → pastikan XP naik sekali → mainkan satu game → buka Riwayat.

---

## Deployment ke Vercel

1. Push repo ke GitHub (file `.env` sudah diabaikan oleh `.gitignore`).
2. Di <https://vercel.com> → **Add New Project** → impor repo. Vercel membaca `vercel.json` dan memakai runtime Python untuk `app.py`.
3. **Settings → Environment Variables**: isi `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `FLASK_SECRET_KEY` (wajib — sesi disimpan di cookie bertanda tangan), `SITE_URL=https://nama-proyek.vercel.app`, dan (opsional) `REQUIRE_EMAIL_CONFIRMATION=0`.
4. Deploy, lalu tambahkan domain Vercel ke *Site URL* dan *Redirect URLs* di Supabase.

Alternatif hosting Python lain (Render, Railway, PythonAnywhere): jalankan `gunicorn app:app` dengan environment variable yang sama.

---

## Arsitektur & keamanan

- **Password** tidak pernah disimpan oleh aplikasi; seluruhnya ditangani Supabase Auth.
- **Sesi**: token Supabase disimpan di cookie Flask yang ditandatangani, `HttpOnly`, `SameSite=Lax` (dan `Secure` di HTTPS); token diperbarui otomatis.
- **CSRF**: semua formulir & panggilan API POST memakai token CSRF.
- **RLS**: siswa hanya dapat **membaca** baris miliknya sendiri. Tabel hasil belajar tidak dapat ditulis dari browser; `quiz_questions` (berisi kunci) tidak dapat dibaca siswa sama sekali.
- **Anti manipulasi skor**: soal & ronde game dibuat server dari *seed* acak; browser hanya menerima data publik tanpa kunci; setiap jawaban dinilai server; skor, waktu (bonus kecepatan), XP, dan lencana dihitung server lalu disimpan dengan service role. Nilai skor yang dikirim browser diabaikan.
- **Validasi input**: angka/pecahan diparse dengan aman (mis. `3/4`, `-1,5`), pembagian nol & garis vertikal ditangani, pesan kesalahan berbahasa Indonesia.
- **Open redirect** diblokir; header `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` dipasang.

## Aturan XP, level, dan lencana

| Aktivitas | XP |
|---|---|
| Menyelesaikan misi (pertama kali) | 100–150 per misi |
| Training Zone | 10 × (jumlah benar − rekor terbaik di level itu) |
| Game | kenaikan dari rekor terbaik (persen × pengali kesulitan 1 / 1,25 / 1,5), maks. 150 |
| Final Line Challenge | 2 × kenaikan nilai terbaik |
| Tantangan harian | 10 per jawaban benar, sekali per hari |
| Lencana | bonus 20–100 XP sekali |

Level: Line Beginner (0) → Point Seeker (150) → Gradient Climber (350) → Equation Builder (600) → Line Engineer (900) → Equation Master (1250) → SCARLINE Legend (1700).

Lencana: First Step, Coordinate Hunter, Gradient Master, Line Creator, Equation Expert, Parallel Detective, Playground Explorer, Daily Spark, SCARLINE Champion.

## Pemecahan masalah

| Gejala | Solusi |
|---|---|
| “Supabase belum dikonfigurasi” | Isi `SUPABASE_URL` dan `SUPABASE_ANON_KEY` di `.env`, lalu restart. |
| Progres tidak tersimpan / pemberitahuan service role | Isi `SUPABASE_SERVICE_ROLE_KEY` di `.env` (server saja). |
| “Batas pengiriman email tercapai” | Pastikan `SUPABASE_SERVICE_ROLE_KEY` terisi dan `REQUIRE_EMAIL_CONFIRMATION=0`, atau pasang SMTP sendiri di Supabase. |
| “Email belum dikonfirmasi” | Klik tautan di email, atau matikan *Confirm email* di Supabase untuk uji coba. |
| Selalu logout setelah restart | Isi `FLASK_SECRET_KEY` dengan nilai tetap. |
| Tautan reset tidak bekerja | Tambahkan `.../reset-password` ke *Redirect URLs* Supabase dan pastikan `SITE_URL` benar. |
| Error “relation does not exist” | Jalankan migrasi lalu seed di SQL Editor. |

---

**SCARLINE — DISCOVER THE LINE, MASTER THE EQUATION!** SCAR is ready. Are you ready to explore?
