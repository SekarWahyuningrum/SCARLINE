"""GAME 4 — Equation Puzzle: seret potongan rumus ke slot yang benar."""
from fractions import Fraction
from random import Random

from ..mathcore import MathInputError, MINUS, coef_term, fmt, signed, x_minus
from .common import shuffled

INFO = {
    "slug": "equation-puzzle",
    "title": "Equation Puzzle",
    "tagline": "Menyusun Potongan Persamaan",
    "icon": "puzzle",
    "story": "Oh tidak! Buku rumus SCAR jatuh dan persamaannya terpecah menjadi potongan-potongan. Bantu SCAR menyusunnya kembali!",
    "goal": "Mengenali dan memahami struktur rumus gradien dan persamaan garis lurus.",
    "mechanic": "Drag & drop potongan rumus",
    "rules": [
        "Seret (drag) potongan ke slot kosong. Di ponsel kamu juga bisa mengetuk potongan lalu mengetuk slot.",
        "Ada potongan pengecoh yang tidak dipakai — hati-hati!",
        "Tekan PERIKSA SUSUNAN. SCAR memberi tahu berapa potongan yang sudah benar.",
        "3 kesempatan per teka-teki. Poin 100/60/30.",
    ],
    "levels": {"easy": "4 rumus dasar", "medium": "6 teka-teki dengan angka", "hard": "8 teka-teki, termasuk bentuk umum ax + by + c = 0"},
    "max_tries": 3,
}


def _m_text(m: Fraction) -> str:
    return fmt(m) if m.denominator == 1 else f"({fmt(m)})"


def _term_x(m: Fraction) -> str:
    return ("" if m > 0 else MINUS) + coef_term(m, "x")


def _nz(rng: Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def t_gradient_formula(rng):
    return ("Susun rumus gradien garis yang melalui (x₁, y₁) dan (x₂, y₂).",
            ["m =", "(y₂ − y₁)", "÷", "(x₂ − x₁)"],
            ["(x₁ − x₂)", "(y₂ + y₁)", "×", "(x₂ − y₁)"],
            "Gradien = perubahan y dibagi perubahan x, dengan urutan titik yang sama.")


def t_point_slope_formula(rng):
    return ("Susun rumus persamaan garis yang bergradien m dan melalui titik (x₁, y₁).",
            ["y − y₁", "=", "m", "(x − x₁)"],
            ["(x + x₁)", "y + y₁", "c", "(y − x₁)"],
            "Rumusnya y − y₁ = m(x − x₁).")


def t_perpendicular(rng):
    return ("Susun syarat dua garis saling tegak lurus.",
            ["m₁", "×", "m₂", "= −1"],
            ["= 1", "+", "= 0", "÷"],
            "Dua garis tegak lurus jika hasil kali gradiennya −1.")


def t_slope_intercept(rng):
    m = Fraction(_nz(rng, -4, 4))
    c = Fraction(_nz(rng, -6, 6))
    return (f"Susun persamaan garis bergradien {fmt(m)} yang memotong sumbu Y di (0, {fmt(c)}).",
            ["y", "=", _term_x(m), signed(c)],
            [_term_x(-m), signed(-c), _term_x(m + 1) if m + 1 != 0 else _term_x(m - 1), signed(c + 1)],
            "Bentuk y = mx + c: koefisien x adalah gradien, konstanta adalah titik potong sumbu Y.")


def t_point_slope_numeric(rng):
    m = Fraction(_nz(rng, -3, 4))
    x1, y1 = _nz(rng, -5, 5), _nz(rng, -5, 5)
    return (f"Susun persamaan garis bergradien {fmt(m)} yang melalui titik ({fmt(x1)}, {fmt(y1)}) dalam bentuk y − y₁ = m(x − x₁).",
            [x_minus(Fraction(y1), "y"), "=", _m_text(m), f"({x_minus(Fraction(x1))})"],
            [x_minus(Fraction(-y1), "y"), f"({x_minus(Fraction(-x1))})", _m_text(-m), f"({x_minus(Fraction(y1))})" if x1 != y1 else "c"],
            "Substitusikan m, x₁, dan y₁ ke rumus y − y₁ = m(x − x₁). Hati-hati dengan tanda negatif!")


def t_gradient_numeric(rng):
    x1, x2 = rng.randint(-4, 1), rng.randint(2, 5)
    y1, y2 = rng.randint(-5, 5), rng.randint(-5, 5)
    while y2 == y1:
        y2 = rng.randint(-5, 5)
    p = lambda v: f"({fmt(v)})" if v < 0 else fmt(v)  # noqa: E731
    return (f"Susun perhitungan gradien garis yang melalui A({fmt(x1)}, {fmt(y1)}) dan B({fmt(x2)}, {fmt(y2)}).",
            ["m =", f"({fmt(y2)} − {p(y1)})", "÷", f"({fmt(x2)} − {p(x1)})"],
            [f"({fmt(x1)} − {p(x2)})", f"({fmt(y2)} − {p(x1)})", "×", f"({fmt(x2)} − {p(y1)})"],
            "m = (y₂ − y₁) ÷ (x₂ − x₁). Pembilang memakai nilai y, penyebut memakai nilai x.")


def t_general_form(rng):
    m = _nz(rng, -4, 4)
    c = _nz(rng, -6, 6)
    # y = mx + c  ->  mx − y + c = 0 ; buat a positif
    a, b, k = m, -1, c
    if a < 0:
        a, b, k = -a, 1, -c
    a_txt = coef_term(Fraction(a), "x")
    y_txt = f"{'+' if b > 0 else MINUS} y"
    k_txt = signed(Fraction(k))
    wrong_y = f"{'+' if b < 0 else MINUS} y"
    return (f"Susun bentuk umum ax + by + c = 0 dari persamaan y = {_term_x(Fraction(m))} {signed(Fraction(c))}.",
            [a_txt, y_txt, k_txt, "= 0"],
            [wrong_y, signed(Fraction(-k)), coef_term(Fraction(a + 1), "x"), "= 1"],
            "Pindahkan semua suku ke ruas kiri sehingga ruas kanan bernilai 0, lalu buat koefisien x positif.")


def join_tokens(tokens) -> str:
    out = ""
    for tok in tokens:
        glue = out and tok.startswith("(") and not out.endswith(("=", "÷", "×"))
        out += tok if glue or not out else " " + tok
    return out


TEMPLATES = {
    "easy": [t_gradient_formula, t_point_slope_formula, t_slope_intercept, t_perpendicular],
    "medium": [t_gradient_formula, t_point_slope_formula, t_slope_intercept, t_point_slope_numeric, t_gradient_numeric, t_perpendicular],
    "hard": [t_gradient_numeric, t_point_slope_numeric, t_slope_intercept, t_general_form, t_point_slope_numeric, t_gradient_numeric, t_general_form, t_perpendicular],
}
DISTRACTORS = {"easy": 2, "medium": 3, "hard": 4}


def generate(rng: Random, difficulty: str):
    rounds = []
    for tpl in shuffled(TEMPLATES[difficulty], rng):
        prompt, solution, distractors, hint = tpl(rng)
        extra = [d for d in distractors if d not in solution][: DISTRACTORS[difficulty]]
        tiles_txt = shuffled(solution + extra, rng)
        tiles = [{"id": f"t{i}", "text": t} for i, t in enumerate(tiles_txt)]
        rounds.append({
            "public": {"prompt": prompt, "slots": len(solution), "tiles": tiles},
            "kind": "order",
            "solution_tokens": solution,
            "tiles": {t["id"]: t["text"] for t in tiles},
            "hint": hint,
            "solution": join_tokens(solution),
        })
    return rounds


def check(rnd: dict, answer) -> dict:
    if not isinstance(answer, list) or len(answer) != len(rnd["solution_tokens"]):
        raise MathInputError("Isi semua slot terlebih dahulu.")
    try:
        texts = [rnd["tiles"][str(tid)] for tid in answer]
    except KeyError:
        raise MathInputError("Potongan tidak dikenal.")
    hits = sum(1 for a, b in zip(texts, rnd["solution_tokens"]) if a == b)
    if hits == len(texts):
        return {"correct": True, "feedback": ""}
    return {"correct": False, "feedback": f"{hits} dari {len(texts)} potongan sudah di tempat yang benar. {rnd['hint']}"}
