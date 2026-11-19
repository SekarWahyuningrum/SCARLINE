"""GAME 6 — Line Detective: baca petunjuk persamaan, lalu tunjuk garis pelakunya di grafik.

Mekanisme: beberapa garis "tersangka" tergambar. Petunjuk ditulis dalam bentuk
yang berbeda-beda (y = mx + c, bentuk umum, titik + gradien, dua titik, sejajar/
tegak lurus). Siswa mengeklik garis langsung di bidang koordinat. Tuduhan yang
salah membuka identitas tersangka itu sebagai petunjuk tambahan.
"""
from fractions import Fraction
from random import Random

from ..mathcore import MathInputError, fmt, fmt_point, general_form, slope_intercept
from .common import lattice_points

INFO = {
    "slug": "line-detective",
    "title": "Line Detective",
    "tagline": "Menyelidiki Garis Tersangka",
    "icon": "search",
    "story": "Sebuah garis misterius mencoret peta harta karun SCAR! Beberapa garis tersangka sudah ditangkap. Baca berkas petunjuknya, lalu tunjuk garis pelakunya langsung di peta.",
    "goal": "Menghubungkan berbagai bentuk persamaan garis dengan grafiknya.",
    "mechanic": "Klik garis tersangka di grafik",
    "rules": [
        "Setiap kasus memiliki beberapa garis tersangka dan satu berkas petunjuk.",
        "Klik garis yang cocok dengan petunjuk langsung pada grafik.",
        "Tuduhan salah? Identitas garis itu terungkap sebagai petunjuk tambahan.",
        "2 kesempatan per kasus. Poin 100 (sekali tebak) atau 60.",
    ],
    "levels": {"easy": "5 kasus, 3 tersangka, petunjuk y = mx + c", "medium": "6 kasus, 4 tersangka, bentuk umum & titik-gradien",
               "hard": "7 kasus, 5 tersangka, dua titik & sejajar/tegak lurus"},
    "max_tries": 2,
}

COUNTS = {"easy": 5, "medium": 6, "hard": 7}
SUSPECTS = {"easy": 3, "medium": 4, "hard": 5}
M_POOL = [Fraction(v) for v in ("1", "2", "3", "-1", "-2", "-3", "1/2", "-1/2", "0")]
CLUE_STYLES = {"easy": ["si"], "medium": ["si", "general", "point"], "hard": ["general", "point", "two", "parallel", "perp"]}


def _clue(style: str, m: Fraction, c: Fraction, rng: Random) -> str:
    pts = lattice_points(m, c, 6)
    if style == "general":
        return f"Pelaku memenuhi persamaan {general_form(m, c)}."
    if style == "point" and pts:
        p = rng.choice(pts)
        return f"Pelaku melalui titik {fmt_point(p)} dan memiliki gradien {fmt(m)}."
    if style == "two" and len(pts) >= 2:
        a, b = pts[0], pts[-1]
        return f"Pelaku melalui titik {fmt_point(a)} dan {fmt_point(b)}."
    if style == "parallel":
        k = c + rng.choice([-3, -2, 2, 3])
        return f"Pelaku sejajar dengan garis {slope_intercept(m, k)} dan memotong sumbu Y di (0, {fmt(c)})."
    if style == "perp" and m != 0:
        k = rng.randint(-3, 3)
        return f"Pelaku tegak lurus dengan garis {slope_intercept(-1 / m, Fraction(k))} dan memotong sumbu Y di (0, {fmt(c)})."
    return f"Pelaku adalah garis {slope_intercept(m, c)}."


def generate(rng: Random, difficulty: str):
    rounds = []
    for _ in range(COUNTS[difficulty]):
        n = SUSPECTS[difficulty]
        while True:
            m = rng.choice(M_POOL)
            c = Fraction(rng.randint(-4, 4))
            if len(lattice_points(m, c, 6)) >= 2:
                break
        # tersangka pengecoh: gradien sama c beda, c sama gradien beda, gradien berlawanan, dll.
        cands = [(m, c + d) for d in (-3, -2, 2, 3)] + [(mm, c) for mm in M_POOL if mm != m] + [(-m, c + 1), (-m, c - 1)]
        rng.shuffle(cands)
        lines = [(m, c)]
        for cand in cands:
            if len(lines) == n:
                break
            if cand not in lines and abs(cand[1]) <= 5 and len(lattice_points(cand[0], cand[1], 6)) >= 2:
                lines.append(cand)
        order = list(range(len(lines)))
        rng.shuffle(order)
        shuffled = [lines[i] for i in order]
        target = order.index(0)
        style = rng.choice(CLUE_STYLES[difficulty])
        if style == "perp" and m == 0:
            style = "general"
        rounds.append({
            "public": {"range": 6, "clue": _clue(style, m, c, rng),
                       "lines": [{"m": str(lm), "c": str(lc)} for lm, lc in shuffled]},
            "answer": target, "m": str(m), "c": str(c),
            "labels": [slope_intercept(lm, lc) for lm, lc in shuffled],
            "solution": slope_intercept(m, c),
            "hint": "Ubah petunjuk menjadi bentuk y = mx + c. Nilai c menunjukkan titik potong sumbu Y, nilai m menunjukkan kemiringan.",
        })
    return rounds


def check(rnd: dict, answer) -> dict:
    try:
        idx = int(answer)
    except (TypeError, ValueError):
        raise MathInputError("Klik salah satu garis tersangka.")
    if not 0 <= idx < len(rnd["labels"]):
        raise MathInputError("Garis tersangka tidak valid.")
    if idx == rnd["answer"]:
        return {"correct": True, "feedback": "", "explain": f"Pelakunya {rnd['solution']}."}
    return {"correct": False, "feedback": f"Bukan dia! Garis itu adalah {rnd['labels'][idx]}. Bandingkan lagi dengan berkas petunjuk.",
            "reveal": {"index": idx, "label": rnd["labels"][idx]}}
