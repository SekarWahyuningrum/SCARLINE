"""GAME 2 — Gradient Rush: atur kemiringan jembatan / pilih garis bergradien tepat."""
from fractions import Fraction
from random import Random

from ..mathcore import MathInputError, fmt
from .common import shuffled

INFO = {
    "slug": "gradient-rush",
    "title": "Gradient Rush",
    "tagline": "Tantangan Kemiringan Garis",
    "icon": "bridge",
    "story": "SCAR harus membangun jembatan dengan kemiringan yang pas agar bisa menyeberang ke wilayah berikutnya. Cepat dan tepat!",
    "goal": "Memahami bahwa gradien menunjukkan tingkat kemiringan garis (Δy ÷ Δx).",
    "mechanic": "Atur slider kemiringan",
    "rules": [
        "Mode JEMBATAN: geser slider naik/turun (Δy) dan mendatar (Δx) sampai gradien jembatan sama dengan target.",
        "Mode PILIH: klik satu dari empat garis yang gradiennya sesuai target.",
        "Poin = ketepatan (100/60/30) + bonus kecepatan sampai 50 poin jika benar di percobaan pertama.",
        "Waktu dihitung oleh server, jadi tidak bisa dicurangi!",
    ],
    "levels": {"easy": "6 jembatan, gradien bilangan bulat", "medium": "8 tantangan, ada pecahan & mode pilih", "hard": "10 tantangan cepat dengan pecahan sulit"},
    "max_tries": 3,
    "speed_bonus": 50,
}

POOLS = {
    "easy": ["1", "2", "3", "-1", "-2", "-3", "0", "4"],
    "medium": ["1/2", "-1/2", "2", "-3", "1/3", "-2/3", "3/2", "0", "-1", "3"],
    "hard": ["3/4", "-4/3", "5/2", "-2/5", "2/3", "-3/2", "-5/3", "1/4", "-6/5", "0", "4/3", "-3/4"],
}
COUNTS = {"easy": 6, "medium": 8, "hard": 10}


def _line_through(m: Fraction, rng: Random):
    p, q = m.numerator, m.denominator
    if q > 6 or abs(p) > 9:  # pragma: no cover - pool dibatasi
        raise ValueError("slope too large")
    x0 = rng.randint(-5, 5 - q)
    lo, hi = max(-5, -5 - p), min(5, 5 - p)
    y0 = rng.randint(lo, hi)
    return [[x0, y0], [x0 + q, y0 + p]]


def generate(rng: Random, difficulty: str):
    pool = shuffled(POOLS[difficulty], rng)
    count = COUNTS[difficulty]
    targets = [Fraction(pool[i % len(pool)]) for i in range(count)]
    rounds = []
    for i, m in enumerate(targets):
        mode = "set" if difficulty == "easy" or i % 2 == 0 else "pick"
        if mode == "set":
            public = {"mode": "set", "target": fmt(m), "target_value": float(m), "rise": [-6, 6], "run": [1, 6]}
            rounds.append({"public": public, "kind": "set", "m": str(m), "solution": f"Δy = {fmt(m.numerator)}, Δx = {m.denominator} (atau kelipatannya)"})
        else:
            distract = []
            for d in (-m, (1 / m) if m != 0 else Fraction(1), (-1 / m) if m != 0 else Fraction(-1), m + 1, m * 2, m - 1):
                if d != m and d not in distract and abs(d.numerator) <= 6 and d.denominator <= 6:
                    distract.append(d)
            slopes = shuffled([m] + distract[:3], rng)
            options = [_line_through(s, rng) for s in slopes]
            public = {"mode": "pick", "target": fmt(m), "target_value": float(m), "options": options}
            rounds.append({"public": public, "kind": "pick", "m": str(m), "answer": slopes.index(m), "solution": f"Garis {'ABCD'[slopes.index(m)]}"})
    return rounds


def check(rnd: dict, answer) -> dict:
    m = Fraction(rnd["m"])
    if rnd["kind"] == "pick":
        try:
            idx = int(answer)
        except (TypeError, ValueError):
            raise MathInputError("Pilih salah satu garis.")
        if not 0 <= idx < 4:
            raise MathInputError("Pilihan garis tidak valid.")
        if idx == rnd["answer"]:
            return {"correct": True, "feedback": ""}
        return {"correct": False, "feedback": f"Belum tepat. Untuk tiap garis, hitung Δy ÷ Δx dari dua titik ujungnya. Target gradien {fmt(m)} berarti {'naik' if m > 0 else 'turun' if m < 0 else 'mendatar'}."}

    if not isinstance(answer, dict):
        raise MathInputError("Atur slider jembatan terlebih dahulu.")
    try:
        rise, run = int(answer.get("rise")), int(answer.get("run"))
    except (TypeError, ValueError):
        raise MathInputError("Nilai slider tidak valid.")
    if not (-6 <= rise <= 6 and 1 <= run <= 6):
        raise MathInputError("Nilai slider di luar batas.")
    user = Fraction(rise, run)
    if user == m:
        return {"correct": True, "feedback": ""}
    if m != 0 and user == -m:
        fb = "Arah jembatanmu terbalik! Gradien positif naik ke kanan, gradien negatif turun ke kanan."
    elif m == 0:
        fb = "Target gradien 0 berarti jembatan harus mendatar: Δy = 0."
    elif abs(user) > abs(m):
        fb = f"Jembatanmu terlalu curam (gradienmu {fmt(user)}). Kurangi Δy atau tambah Δx."
    else:
        fb = f"Jembatanmu terlalu landai (gradienmu {fmt(user)}). Tambah Δy atau kurangi Δx."
    return {"correct": False, "feedback": fb}
