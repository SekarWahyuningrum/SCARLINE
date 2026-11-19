"""SCAR AI Tutor.

- Jika ``ANTHROPIC_API_KEY`` diatur di server, SCAR menjawab memakai Claude
  (SDK resmi ``anthropic``). Kunci API TIDAK pernah dikirim ke browser.
- Jika belum diatur (atau layanan AI sedang gangguan), SCAR memakai tutor dasar
  lokal yang tetap berguna: menghitung gradien/persamaan dari angka yang diketik
  siswa (dengan langkah lengkap dari ``mathcore``), menjelaskan konsep kunci,
  memberi latihan, dan motivasi.
"""
from __future__ import annotations

import random
import re
from fractions import Fraction
from typing import List, Optional

from . import mathcore
from .content import TRAINING_BANK
from .mathcore import MathInputError, fmt

MODES = {
    "tanya": "Siswa bertanya atau minta penjelasan konsep.",
    "petunjuk": "Siswa minta PETUNJUK saja. Beri satu langkah awal atau pertanyaan pancingan; jangan berikan jawaban akhir.",
    "koreksi": "Siswa ingin jawabannya dikoreksi. Periksa setiap langkah, sebutkan bagian yang benar, tunjukkan letak kesalahan dan alasannya, lalu beri langkah perbaikan.",
    "latihan": "Siswa minta latihan tambahan. Beri 1–2 soal baru setingkat SMP kelas VIII sesuai topik yang diminta. Jangan sertakan jawaban; ajak siswa mengirim jawabannya untuk dikoreksi.",
    "ulang": "Siswa ingin mengulang materi. Beri ringkasan singkat: konsep, rumus, satu contoh singkat.",
    "motivasi": "Siswa butuh semangat. Beri motivasi singkat yang tulus dan satu tips belajar yang konkret.",
}

SYSTEM_PROMPT = """Kamu adalah SCAR, maskot dan tutor matematika di SCARLINE — platform petualangan belajar Persamaan Garis Lurus untuk siswa SMP kelas VIII di Indonesia.

Peranmu adalah TUTOR, bukan sekadar mesin jawaban:
- Gunakan bahasa Indonesia yang sederhana, hangat, dan menyemangati, cocok untuk siswa usia 13–14 tahun.
- Jelaskan langkah demi langkah. Sebutkan rumus yang dipakai dan arti setiap simbolnya.
- Utamakan pemahaman: bila wajar, ajukan satu pertanyaan pancingan agar siswa berpikir sendiri.
- Saat mengoreksi, sebutkan dulu bagian yang sudah benar, lalu tunjukkan letak kesalahan dengan lembut.
- Perhitungan harus akurat. Periksa ulang aritmetika (terutama tanda negatif dan pecahan) sebelum menjawab.
- Materi yang kamu kuasai: koordinat Kartesius, titik dan garis, gradien (positif, negatif, nol, tidak terdefinisi), bentuk y = mx + c dan ax + by + c = 0, menentukan persamaan garis (gradien + titik, dua titik), grafik dan titik potong sumbu, garis sejajar (m₁ = m₂), garis tegak lurus (m₁ × m₂ = −1), dan penerapannya dalam kehidupan sehari-hari.
- Jika siswa bertanya di luar matematika sekolah, jawab singkat dengan ramah lalu ajak kembali belajar. Jangan membahas hal yang tidak pantas untuk anak.
- Jangan meminta atau menyimpan data pribadi siswa.

Format jawaban:
- Singkat dan jelas: biasanya 60–180 kata. Gunakan daftar bernomor untuk langkah.
- Teks biasa (tanpa LaTeX). Tulis rumus seperti: m = (y₂ − y₁) / (x₂ − x₁), y = 2x − 3, m₁ × m₂ = −1.
- Boleh menutup dengan satu kalimat semangat singkat dari SCAR."""

MAX_HISTORY = 8
MAX_CHARS = 1500


def clean_history(raw) -> List[dict]:
    """Validasi riwayat percakapan dari browser: hanya role user/assistant, teks dipotong, urutan dimulai dari user."""
    out: List[dict] = []
    for item in (raw or [])[-MAX_HISTORY:]:
        if not isinstance(item, dict):
            continue
        role, text = item.get("role"), item.get("content")
        if role not in ("user", "assistant") or not isinstance(text, str) or not text.strip():
            continue
        text = text.strip()[:MAX_CHARS]
        if out and out[-1]["role"] == role:
            out[-1]["content"] += "\n" + text
        else:
            out.append({"role": role, "content": text})
    while out and out[0]["role"] != "user":
        out.pop(0)
    return out


def ask_claude(api_key: str, model: str, message: str, history: List[dict], mode: str, context: str) -> str:
    import anthropic  # impor di sini agar aplikasi tetap jalan walau paket belum terpasang

    client = anthropic.Anthropic(api_key=api_key, timeout=45.0, max_retries=1)
    turn = f"[Mode: {MODES.get(mode, MODES['tanya'])}]"
    if context:
        turn += f"\n[Siswa sedang membuka: {context[:200]}]"
    turn += "\n\n" + message[:MAX_CHARS]
    messages = history + [{"role": "user", "content": turn}]
    response = client.beta.messages.create(
        model=model,
        max_tokens=2048,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=messages,
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        return "Maaf, SCAR tidak bisa membantu pertanyaan itu. Yuk, kita kembali ke petualangan persamaan garis lurus! Kamu boleh bertanya tentang gradien, persamaan garis, atau grafik."
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    return text or "SCAR sedang berpikir keras tapi belum menemukan jawabannya. Coba tulis pertanyaanmu dengan cara lain, ya!"


# ---------------------------------------------------------------- tutor dasar (tanpa AI)
NUM = r"[-−–]?\d+(?:[.,]\d+)?(?:/\d+)?"
POINT_RE = re.compile(rf"\(\s*({NUM})\s*[,;]\s*({NUM})\s*\)")
SLOPE_RE = re.compile(rf"(?:gradien|m)\s*(?:=|adalah|nya)?\s*({NUM})", re.I)
SI_RE = re.compile(rf"y\s*=\s*({NUM})?\s*(-?)\s*x\s*(?:([+\-−–])\s*({NUM}))?", re.I)

CONCEPTS = [
    (("tegak lurus", "⊥", "tegaklurus"), "Dua garis TEGAK LURUS jika hasil kali gradiennya −1: m₁ × m₂ = −1. Jadi m₂ = −1/m₁ (dibalik lalu diberi tanda berlawanan). Contoh: garis y = 2x + 1 tegak lurus dengan garis bergradien −1/2."),
    (("sejajar", "∥", "paralel"), "Dua garis SEJAJAR jika gradiennya sama: m₁ = m₂, tetapi nilai c-nya berbeda. Contoh: y = 3x + 1 sejajar dengan y = 3x − 4. Jika m dan c-nya sama, kedua garis berimpit (garis yang sama)."),
    (("tidak terdefinisi", "vertikal", "tegak"), "Garis VERTIKAL (tegak) seperti x = 3 memiliki gradien TIDAK TERDEFINISI, karena Δx = 0 dan pembagian dengan nol tidak bisa dihitung."),
    (("nol", "horizontal", "mendatar"), "Garis HORIZONTAL (mendatar) seperti y = 4 memiliki gradien NOL, karena nilai y tidak berubah (Δy = 0), sehingga m = 0 ÷ Δx = 0."),
    (("bentuk umum", "ax + by", "ax+by"), "Bentuk umum persamaan garis: ax + by + c = 0. Gradiennya m = −a/b. Contoh: 2x − y + 3 = 0 → m = −2/(−1) = 2. Kamu juga bisa mengubahnya ke bentuk y = mx + c: y = 2x + 3."),
    (("titik potong", "memotong sumbu", "sumbu y", "sumbu x"), "Titik potong sumbu Y: ganti x = 0 (pada y = mx + c hasilnya (0, c)). Titik potong sumbu X: ganti y = 0 lalu selesaikan x. Contoh y = 2x − 4: sumbu Y di (0, −4), sumbu X di (2, 0)."),
    (("kuadran",), "Bidang Kartesius dibagi empat kuadran: I (+, +) kanan atas, II (−, +) kiri atas, III (−, −) kiri bawah, IV (+, −) kanan bawah. Titik yang tepat di sumbu tidak termasuk kuadran mana pun."),
    (("koordinat", "absis", "ordinat"), "Titik ditulis (x, y). x disebut absis (langkah mendatar dari O), y disebut ordinat (langkah tegak). Kanan/atas positif, kiri/bawah negatif. Urutannya tidak boleh tertukar!"),
    (("gradien", "kemiringan", "slope"), "Gradien (m) menyatakan kemiringan garis: m = Δy/Δx = (y₂ − y₁)/(x₂ − x₁). m positif → garis naik, m negatif → turun, m = 0 → mendatar, garis vertikal → tidak terdefinisi. Semakin besar |m|, semakin curam garisnya."),
    (("persamaan garis", "y = mx", "rumus"), "Rumus penting persamaan garis:\n1. Bentuk y = mx + c (m = gradien, c = titik potong sumbu Y).\n2. Melalui titik (x₁, y₁) dengan gradien m: y − y₁ = m(x − x₁).\n3. Melalui dua titik: hitung m = (y₂ − y₁)/(x₂ − x₁), lalu pakai rumus nomor 2.\n4. Melalui titik asal: y = mx."),
]

MOTIVATION = [
    "Setiap ahli matematika pernah salah berkali-kali. Yang membedakan: mereka tidak berhenti mencoba! Tips SCAR: kerjakan satu soal pelan-pelan, tulis setiap langkah, lalu cek dengan mensubstitusi titiknya.",
    "Kamu sudah sejauh ini — itu luar biasa! Tips SCAR: kalau bingung, gambar dulu grafiknya. Garis yang terlihat jauh lebih mudah dipahami.",
    "Otakmu seperti otot: makin sering dilatih, makin kuat. Tips SCAR: coba 3 soal Training Zone setiap hari, sedikit tapi rutin.",
]


def _num(raw: str) -> Fraction:
    return mathcore.to_frac(raw.replace("−", "-").replace("–", "-"))


def _steps(res: dict) -> str:
    steps = res.get("steps") or []
    return "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))


def local_reply(message: str, mode: str) -> dict:
    text = message.strip()
    low = text.lower()
    if mode == "motivasi" or any(w in low for w in ("semangat", "menyerah", "susah banget", "malas", "capek")):
        return {"reply": random.choice(MOTIVATION)}
    if mode == "latihan" or "latihan" in low or "soal baru" in low:
        q = random.choice(TRAINING_BANK[random.choice([1, 2, 3])])
        from .grading import answer_display

        reply = f"Ini latihan dari SCAR:\n\n{q['prompt']}"
        if q.get("options"):
            reply += "\n" + "\n".join(f"{chr(65 + i)}. {o}" for i, o in enumerate(q["options"]))
        return {"reply": reply + "\n\nKerjakan dulu di kertas, lalu buka pembahasannya di bawah.",
                "practice": {"answer": answer_display(q), "explain": q.get("explain", ""), "hint": q.get("hint", "")}}

    points = POINT_RE.findall(text)
    try:
        if len(points) >= 2:
            p1 = (_num(points[0][0]), _num(points[0][1]))
            p2 = (_num(points[1][0]), _num(points[1][1]))
            res = mathcore.from_two_points(p1, p2)
            if mode == "petunjuk":
                return {"reply": "Petunjuk: hitung dulu gradiennya dengan m = (y₂ − y₁)/(x₂ − x₁). Setelah dapat m, gunakan y − y₁ = m(x − x₁) dengan salah satu titik. Coba hitung, lalu kirim jawabanmu untuk dikoreksi!"}
            return {"reply": f"Garis yang melalui kedua titik itu:\n\n{_steps(res)}\n\nHasil: {res['equation']} (bentuk umum: {res['general']})."}
        slope = SLOPE_RE.search(text)
        if len(points) == 1 and slope:
            m = _num(slope.group(1))
            res = mathcore.from_point_slope(m, (_num(points[0][0]), _num(points[0][1])))
            if mode == "petunjuk":
                return {"reply": "Petunjuk: gunakan rumus y − y₁ = m(x − x₁). Masukkan nilai m dan titik (x₁, y₁), lalu jabarkan sampai berbentuk y = mx + c."}
            return {"reply": f"{_steps(res)}\n\nHasil: {res['equation']}."}
        si = SI_RE.search(text.replace("−", "-").replace("–", "-"))
        if si and "x" in low:
            coef = si.group(1)
            m = _num(coef) if coef else Fraction(1)
            if si.group(2) == "-":
                m = -m
            c = Fraction(0)
            if si.group(4):
                c = _num(si.group(4)) * (-1 if si.group(3) in "-−–" else 1)
            res = mathcore.from_slope_intercept(m, c)
            return {"reply": (f"Untuk garis {res['equation']}:\n1. Gradien m = {res['gradient']} → garis {res['direction']}.\n"
                              f"2. Titik potong sumbu Y: {res['y_intercept']}.\n3. Titik potong sumbu X: {res['x_intercept']}.\n"
                              f"4. Bentuk umum: {res['general']}.\n5. Gradien garis sejajar: {res['gradient']}; gradien garis tegak lurus: "
                              f"{fmt(-1 / m) if m != 0 else 'tidak terdefinisi (garis vertikal)'}.")}
    except (MathInputError, ZeroDivisionError, ValueError):
        pass

    for keys, answer in CONCEPTS:
        if any(k in low for k in keys):
            return {"reply": answer + ("\n\nIngin latihan? Tekan tombol “Latihan” di bawah." if mode != "petunjuk" else "")}
    return {"reply": ("SCAR siap membantu! Kamu bisa:\n1. Menanyakan konsep, misalnya “apa itu gradien?” atau “syarat garis tegak lurus”.\n"
                      "2. Mengetik soal, misalnya “persamaan garis melalui (1, 2) dan (3, 6)” atau “gradien 2 melalui (1, 5)”.\n"
                      "3. Mengetik persamaan, misalnya “y = 2x − 4”, untuk melihat gradien dan titik potongnya.\n"
                      "4. Menekan tombol Latihan atau Motivasi.")}


def answer(message: str, history, mode: str, context: str, api_key: Optional[str], model: str) -> dict:
    mode = mode if mode in MODES else "tanya"
    if api_key:
        try:
            import anthropic
        except ImportError:
            anthropic = None
        if anthropic is not None:
            try:
                return {"reply": ask_claude(api_key, model, message, clean_history(history), mode, context), "engine": "ai"}
            except anthropic.APIError as exc:  # jaringan, kuota, kunci salah: tetap bantu siswa dengan tutor dasar
                out = local_reply(message, mode)
                out.update(engine="basic", error_type=type(exc).__name__,
                           notice="Layanan AI sedang tidak tersedia, jadi SCAR menjawab dengan mode tutor dasar.")
                return out
    out = local_reply(message, mode)
    out["engine"] = "basic"
    return out
