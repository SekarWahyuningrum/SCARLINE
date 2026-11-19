"""Penilaian jawaban di server.

Browser hanya mengirim jawaban; kunci dan pembahasan dikirim balik SETELAH
jawaban dinilai. Setiap jawaban salah mendapat umpan balik spesifik dari SCAR
(misalnya “tanda gradien terbalik” atau “x dan y tertukar”).
"""
from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

from .mathcore import MathInputError, fmt, fmt_point, is_decimal_text, slope_intercept, to_frac

PUBLIC_KEYS = ("id", "type", "topic", "prompt", "options", "graph", "range", "items", "money", "level")

GENERIC_DIAGNOSE = {
    "sign": "Tanda jawabanmu terbalik (positif ↔ negatif). Periksa urutan pengurangan: (y₂ − y₁) dan (x₂ − x₁) harus dimulai dari titik yang sama.",
    "flip": "Sepertinya pembilang dan penyebutnya tertukar. Gradien = Δy ÷ Δx (perubahan tegak dibagi perubahan mendatar).",
    "flip_sign": "Angkanya terbalik DAN tandanya juga terbalik. Ulangi pelan-pelan: m = (y₂ − y₁)/(x₂ − x₁).",
}


_MONEY_RE = re.compile(r"^\d{1,3}(\.\d{3})+(,\d+)?$")


def normalize_money(raw: Any) -> Any:
    """Terima penulisan rupiah: "Rp25.000", "25.000", "25 000" → "25000"."""
    if not isinstance(raw, str):
        return raw
    s = raw.strip().lower().replace("rp", "").replace(" ", "").replace(" ", "")
    if _MONEY_RE.match(s):
        s = s.replace(".", "")
    return s


def rupiah(value: Fraction) -> str:
    whole = int(value) if value.denominator == 1 else float(value)
    return "Rp" + f"{whole:,}".replace(",", ".")


def public_question(q: dict) -> dict:
    """Data soal yang aman dikirim ke browser (tanpa kunci jawaban)."""
    return {k: q[k] for k in PUBLIC_KEYS if k in q}


def answer_display(q: dict) -> str:
    t, a = q["type"], q["answer"]
    if t == "mc":
        return q["options"][a]
    if t == "tf":
        return "Benar" if a else "Salah"
    if t == "num":
        return rupiah(to_frac(a)) if q.get("money") else fmt(to_frac(a))
    if t == "point":
        return fmt_point(a)
    if t == "line":
        return slope_intercept(to_frac(a["m"]), to_frac(a["c"]))
    if t == "match":
        items = q["items"]
        return "; ".join(f"{items[i]} ↔ {items[j]}" for i, j in a)
    return str(a)


def _num_equal(user_raw: Any, user: Fraction, expected: Fraction) -> bool:
    if user == expected:
        return True
    # Toleransi untuk desimal berulang, mis. 0.33 untuk 1/3.
    return is_decimal_text(user_raw) and expected.denominator != 1 and abs(user - expected) <= Fraction(1, 200)


def _diagnose_num(q: dict, user: Fraction, expected: Fraction) -> str:
    table = dict(GENERIC_DIAGNOSE)
    table.update(q.get("diagnose") or {})
    if expected != 0 and user == -expected:
        return table["sign"]
    if expected != 0 and user != 0:
        if user == 1 / expected:
            return table["flip"]
        if user == -1 / expected:
            return table["flip_sign"]
    if user > expected:
        return "Jawabanmu terlalu besar. " + q.get("hint", "")
    return "Jawabanmu terlalu kecil. " + q.get("hint", "")


def _parse_point(answer: Any):
    if not isinstance(answer, (list, tuple)) or len(answer) != 2:
        raise MathInputError("Pilih satu titik pada bidang koordinat.")
    return to_frac(answer[0]), to_frac(answer[1])


def _parse_line(answer: Any):
    if not isinstance(answer, dict):
        raise MathInputError("Isi nilai m dan c terlebih dahulu.")
    return to_frac(answer.get("m")), to_frac(answer.get("c"))


def grade(q: dict, answer: Any) -> dict:
    """Nilai satu jawaban. Raise MathInputError jika format input tidak valid."""
    t = q["type"]
    correct = False
    feedback = ""

    if t == "mc":
        try:
            idx = int(answer)
        except (TypeError, ValueError):
            raise MathInputError("Pilih salah satu jawaban.")
        if not 0 <= idx < len(q["options"]):
            raise MathInputError("Pilihan jawaban tidak valid.")
        correct = idx == q["answer"]
        if not correct:
            feedback = q.get("hint", "Coba baca kembali soalnya dengan teliti.")

    elif t == "tf":
        if answer not in (True, False, "true", "false"):
            raise MathInputError("Pilih Benar atau Salah.")
        user = answer if isinstance(answer, bool) else answer == "true"
        correct = user == q["answer"]
        if not correct:
            feedback = q.get("hint", "Periksa kembali pernyataannya.")

    elif t == "num":
        if q.get("money"):
            answer = normalize_money(answer)
        user = to_frac(answer)
        expected = to_frac(q["answer"])
        correct = _num_equal(answer, user, expected)
        if not correct:
            feedback = _diagnose_num(q, user, expected)

    elif t == "point":
        ux, uy = _parse_point(answer)
        ex, ey = (to_frac(v) for v in q["answer"])
        correct = (ux, uy) == (ex, ey)
        if not correct:
            if (ux, uy) == (ey, ex):
                feedback = "x dan y tertukar! Ingat urutannya (x, y): geser mendatar dulu, baru tegak."
            elif ux == ex:
                feedback = f"Posisi mendatarmu (x) sudah tepat. Sekarang periksa y: kamu memilih y = {fmt(uy)}, seharusnya bergeser ke {'atas' if ey > 0 else 'bawah' if ey < 0 else 'sumbu X'}."
            elif uy == ey:
                feedback = f"Posisi tegakmu (y) sudah tepat. Periksa x: kamu memilih x = {fmt(ux)}, seharusnya bergeser ke {'kanan' if ex > 0 else 'kiri' if ex < 0 else 'sumbu Y'}."
            elif ux == -ex and uy == -ey:
                feedback = "Tanda x dan y terbalik. Positif berarti kanan/atas, negatif berarti kiri/bawah."
            else:
                feedback = q.get("hint", "Mulai dari titik O(0, 0), geser x langkah mendatar lalu y langkah tegak.")

    elif t == "line":
        um, uc = _parse_line(answer)
        em, ec = (to_frac(q["answer"]["m"]), to_frac(q["answer"]["c"]))
        correct = um == em and uc == ec
        if not correct:
            if um == em:
                feedback = "Gradienmu (m) sudah tepat! Tinggal nilai c: substitusikan satu titik yang diketahui untuk mencarinya."
            elif uc == ec:
                if um == -em:
                    feedback = "Nilai c sudah benar, tapi tanda gradiennya terbalik. Garisnya naik atau turun?"
                else:
                    feedback = "Nilai c sudah benar. Hitung ulang gradiennya: m = Δy ÷ Δx."
            elif um == -em:
                feedback = "Tanda gradienmu terbalik, sehingga c ikut salah. " + q.get("hint", "")
            else:
                feedback = "Gradien dan konstanta belum tepat. " + q.get("hint", "")

    elif t == "match":
        if not isinstance(answer, list) or not answer:
            raise MathInputError("Buat pasangan garis terlebih dahulu.")
        try:
            user_pairs = {tuple(sorted((int(a), int(b)))) for a, b in answer}
        except (TypeError, ValueError):
            raise MathInputError("Format pasangan tidak valid.")
        expected_pairs = {tuple(sorted(p)) for p in q["answer"]}
        hits = len(user_pairs & expected_pairs)
        correct = user_pairs == expected_pairs
        if not correct:
            feedback = f"{hits} dari {len(expected_pairs)} pasangan sudah benar. {q.get('hint', '')}"

    else:  # pragma: no cover - tipe baru wajib ditangani
        raise MathInputError("Tipe soal tidak dikenal.")

    return {
        "correct": bool(correct),
        "feedback": feedback.strip(),
        "explain": q.get("explain", ""),
        "answer_display": answer_display(q),
    }
