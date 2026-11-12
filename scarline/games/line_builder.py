"""GAME 3 — Line Builder: pilih m dan c agar mesin menggambar garis target."""
from fractions import Fraction
from random import Random

from ..mathcore import fmt, slope_intercept
from .common import frac_options, lattice_points, pick_two_far

INFO = {
    "slug": "line-builder",
    "title": "Line Builder",
    "tagline": "Membangun Persamaan Garis",
    "icon": "gear",
    "story": "SCAR menemukan mesin pembuat garis yang rusak! Masukkan gradien (m) dan konstanta (c) yang tepat agar mesin menggambar garis yang sama persis dengan garis target.",
    "goal": "Memahami hubungan persamaan y = mx + c dengan grafiknya.",
    "mechanic": "Rakit persamaan dengan tuas m dan c",
    "rules": [
        "Garis target (putus-putus) digambar dengan dua titik bantu.",
        "Pilih tuas nilai m dan c. Mesin langsung menggambar garismu.",
        "Tekan UJI MESIN. Jika garismu berimpit dengan target, tantangan selesai!",
        "3 kesempatan per garis. Poin 100/60/30.",
    ],
    "levels": {"easy": "5 garis, gradien bulat", "medium": "6 garis, ada gradien 0 dan 1/2", "hard": "7 garis, gradien pecahan & lebih banyak pilihan"},
    "max_tries": 3,
}

M_POOLS = {
    "easy": ["1", "2", "3", "-1", "-2", "-3"],
    "medium": ["1", "-1", "2", "-2", "0", "1/2", "-1/2", "3"],
    "hard": ["1/2", "-1/2", "1/3", "-2/3", "3/2", "-3/2", "2", "-3", "2/3"],
}
COUNTS = {"easy": 5, "medium": 6, "hard": 7}


def generate(rng: Random, difficulty: str):
    limit = 6 if difficulty != "hard" else 8
    k = 4 if difficulty != "hard" else 5
    pool = M_POOLS[difficulty][:]
    rng.shuffle(pool)
    rounds = []
    used = set()
    i = 0
    while len(rounds) < COUNTS[difficulty]:
        m = Fraction(pool[i % len(pool)])
        i += 1
        c = Fraction(rng.randint(-4, 4) if difficulty != "hard" else rng.randint(-5, 5))
        if (m, c) in used:
            continue
        pts = lattice_points(m, c, limit - 1)
        if len(pts) < 2:
            continue
        used.add((m, c))
        two = pick_two_far(pts, rng, prefer_axis=(difficulty == "easy"))
        m_opts = frac_options(m, [-m, m + 1, m - 1, 2 * m, 1 / m if m else Fraction(1)], k, rng)
        c_opts = frac_options(c, [-c, c + 1, c - 2, c + 2, c - 1], k, rng)
        rounds.append({
            "public": {"points": [list(p) for p in two], "range": limit, "m_options": m_opts, "c_options": c_opts},
            "q": {
                "type": "line",
                "answer": {"m": str(m), "c": str(c)},
                "hint": "Cari c dari titik potong dengan sumbu Y, lalu hitung m = Δy ÷ Δx dari dua titik bantu.",
                "explain": f"Garis target adalah {slope_intercept(m, c)}: gradien {fmt(m)} dan memotong sumbu Y di (0, {fmt(c)}).",
            },
        })
    return rounds
