"""GAME 7 — Parallel or Perpendicular?: seret kartu pasangan garis ke portal yang benar.

Mekanisme: kartu berisi dua persamaan garis datang satu per satu. Siswa menyeret
kartu ke portal SEJAJAR, TEGAK LURUS, atau BERPOTONGAN (tingkat sulit menambah
portal BERIMPIT). Menjawab cepat memberi bonus. Setelah menjawab, kedua garis
digambar sehingga siswa melihat hubungannya.
"""
from fractions import Fraction
from random import Random

from ..mathcore import MathInputError, fmt, general_form, slope_intercept

INFO = {
    "slug": "parallel-perpendicular",
    "title": "Parallel or Perpendicular?",
    "tagline": "Memilah Pasangan Garis",
    "icon": "parallel",
    "story": "Gerbang dimensi di Parallel World kacau! Pasangan garis tersesat di portal yang salah. Bantu SCAR memilah setiap pasangan ke portal yang tepat sebelum gerbangnya menutup.",
    "goal": "Menentukan hubungan dua garis dari gradiennya: sejajar (m₁ = m₂), tegak lurus (m₁ × m₂ = −1), atau berpotongan.",
    "mechanic": "Seret kartu ke portal hubungan garis",
    "rules": [
        "Seret kartu pasangan garis ke salah satu portal (atau klik portalnya).",
        "Sejajar: gradien sama. Tegak lurus: hasil kali gradien −1. Selain itu: berpotongan.",
        "Tingkat Sulit menambah portal BERIMPIT (garis yang sama, ditulis berbeda).",
        "Satu kesempatan per kartu: 100 poin + bonus kecepatan hingga 30.",
    ],
    "levels": {"easy": "6 kartu, bentuk y = mx + c", "medium": "8 kartu, ada bentuk umum ax + by + c = 0",
               "hard": "10 kartu, gradien pecahan + portal berimpit"},
    "max_tries": 1,
    "speed_bonus": 30,
}

COUNTS = {"easy": 6, "medium": 8, "hard": 10}
PORTALS = {
    "sejajar": "Sejajar ∥",
    "tegak": "Tegak lurus ⊥",
    "potong": "Berpotongan ✕",
    "berimpit": "Berimpit ≡",
}
M_EASY = [Fraction(v) for v in (1, 2, 3, -1, -2, -3)]
M_HARD = M_EASY + [Fraction(1, 2), Fraction(-1, 2), Fraction(2, 3), Fraction(-3, 2), Fraction(1, 3)]


def _show(m: Fraction, c: Fraction, general: bool) -> str:
    return general_form(m, c) if general else slope_intercept(m, c)


def generate(rng: Random, difficulty: str):
    cats = ["sejajar", "tegak", "potong"] + (["berimpit"] if difficulty == "hard" else [])
    count = COUNTS[difficulty]
    plan = [cats[i % len(cats)] for i in range(count)]
    rng.shuffle(plan)
    pool = M_HARD if difficulty == "hard" else M_EASY
    rounds = []
    for cat in plan:
        m1 = rng.choice(pool)
        c1 = Fraction(rng.randint(-4, 4))
        if cat == "sejajar":
            m2, c2 = m1, c1 + rng.choice([-3, -2, 2, 3])
        elif cat == "tegak":
            m2, c2 = -1 / m1, Fraction(rng.randint(-4, 4))
        elif cat == "berimpit":
            m2, c2 = m1, c1
        else:
            while True:
                m2 = rng.choice(pool)
                if m2 != m1 and m1 * m2 != -1:
                    break
            c2 = Fraction(rng.randint(-4, 4))
        g1 = difficulty == "hard" and rng.random() < 0.5
        g2 = difficulty != "easy" and (cat == "berimpit" or rng.random() < 0.6)
        if cat == "berimpit":
            g1 = False
        rounds.append({
            "public": {"eq1": _show(m1, c1, g1), "eq2": _show(m2, c2, g2), "portals": [{"key": k, "label": PORTALS[k]} for k in cats],
                       "lines": [{"m": str(m1), "c": str(c1)}, {"m": str(m2), "c": str(c2)}], "range": 6},
            "answer": cat, "m1": str(m1), "m2": str(m2),
            "solution": PORTALS[cat],
            "hint": "Ubah kedua persamaan ke bentuk y = mx + c, lalu bandingkan gradiennya.",
        })
    return rounds


def check(rnd: dict, answer) -> dict:
    if answer not in PORTALS:
        raise MathInputError("Seret kartu ke salah satu portal.")
    m1, m2 = Fraction(rnd["m1"]), Fraction(rnd["m2"])
    why = f"m₁ = {fmt(m1)} dan m₂ = {fmt(m2)}"
    if rnd["answer"] == "sejajar":
        why += " → gradien sama, c berbeda: SEJAJAR."
    elif rnd["answer"] == "tegak":
        why += f" → m₁ × m₂ = {fmt(m1 * m2)}: TEGAK LURUS."
    elif rnd["answer"] == "berimpit":
        why += " → gradien dan c sama: kedua persamaan adalah garis yang SAMA (berimpit)."
    else:
        why += f" → gradien berbeda dan m₁ × m₂ = {fmt(m1 * m2)} ≠ −1: BERPOTONGAN (tidak tegak lurus)."
    if answer == rnd["answer"]:
        return {"correct": True, "feedback": "", "explain": why}
    return {"correct": False, "feedback": f"Portal yang tepat: {PORTALS[rnd['answer']]}.", "explain": why}
