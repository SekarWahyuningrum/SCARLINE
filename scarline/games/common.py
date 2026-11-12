"""Utilitas bersama untuk generator game."""
from fractions import Fraction
from random import Random
from typing import List

from ..mathcore import fmt


def lattice_points(m: Fraction, c: Fraction, rng_limit: int) -> List[tuple]:
    """Titik bilangan bulat pada y = mx + c yang muat di bidang [-limit, limit]."""
    pts = []
    for x in range(-rng_limit, rng_limit + 1):
        y = m * x + c
        if y.denominator == 1 and abs(y) <= rng_limit:
            pts.append((x, int(y)))
    return pts


def pick_two_far(points: List[tuple], rng: Random, prefer_axis: bool = False) -> List[tuple]:
    """Pilih dua titik yang cukup berjauhan supaya garis mudah dibaca."""
    if prefer_axis:
        on_axis = [p for p in points if p[0] == 0]
        if on_axis:
            first = on_axis[0]
            others = sorted((p for p in points if p != first), key=lambda p: -abs(p[0] - first[0]))
            if others:
                return [first, others[min(len(others) - 1, rng.randint(0, 1))]]
    pts = sorted(points)
    if len(pts) < 2:
        raise ValueError("Garis butuh minimal dua titik bulat")
    span = max(1, len(pts) // 3)
    a = pts[rng.randint(0, span - 1)]
    b = pts[-1 - rng.randint(0, span - 1)]
    if a == b:
        a, b = pts[0], pts[-1]
    return [a, b]


def shuffled(items, rng: Random):
    items = list(items)
    rng.shuffle(items)
    return items


def frac_options(correct: Fraction, distractors, k: int, rng: Random) -> List[str]:
    """Opsi jawaban berupa string pecahan unik, berisi jawaban benar."""
    seen = {correct}
    picks = [correct]
    for d in distractors:
        d = Fraction(d)
        if d not in seen:
            seen.add(d)
            picks.append(d)
        if len(picks) == k:
            break
    filler = 1
    while len(picks) < k:
        cand = correct + filler
        if cand not in seen:
            seen.add(cand)
            picks.append(cand)
        filler = -filler if filler > 0 else -filler + 1
    return [fmt(v, unicode_minus=False) for v in shuffled(picks, rng)]
