"""GAME 5 — SCAR's Line Rescue: petualangan berjalur, setiap jalur berisi tantangan."""
from fractions import Fraction
from random import Random

from ..mathcore import fmt, fmt_paren, fmt_point, gradient, slope_intercept

INFO = {
    "slug": "line-rescue",
    "title": "SCAR's Line Rescue",
    "tagline": "Petualangan Menyelamatkan SCAR",
    "icon": "map",
    "story": "SCAR terjebak di dunia koordinat yang penuh jalur misterius! Setiap jembatan terkunci oleh teka-teki matematika. Selesaikan semuanya untuk membawa SCAR pulang ke markas.",
    "goal": "Menggabungkan seluruh materi: titik koordinat, gradien, persamaan garis, dan hubungan antargaris.",
    "mechanic": "Petualangan peta bertahap",
    "rules": [
        "Setiap pos di peta berisi satu tantangan: titik, gradien, persamaan, atau hubungan garis.",
        "Jawaban benar membuka jalur dan SCAR berjalan ke pos berikutnya.",
        "Kamu punya 3 nyawa (♥). Setiap jawaban salah mengurangi satu nyawa, tetapi SCAR memberi petunjuk.",
        "Benar di percobaan pertama = 100 poin, setelah petunjuk = 50 poin.",
    ],
    "levels": {"easy": "4 pos petualangan", "medium": "6 pos petualangan", "hard": "8 pos dengan angka pecahan"},
    "hearts": 3,
}

PLAN = {
    "easy": ["point", "gradient", "onpoint", "intercept_form"],
    "medium": ["point", "gradient", "onpoint", "two_points", "relation", "x_intercept"],
    "hard": ["point", "gradient_frac", "two_points", "relation", "parallel", "perpendicular", "x_intercept", "onpoint"],
}

NODE_TITLES = {
    "point": "Gerbang Koordinat", "gradient": "Jembatan Miring", "gradient_frac": "Jembatan Pecahan",
    "onpoint": "Batu Loncatan", "intercept_form": "Mesin y = mx + c", "two_points": "Menara Dua Titik",
    "relation": "Persimpangan Garis", "parallel": "Rel Sejajar", "perpendicular": "Perempatan Siku",
    "x_intercept": "Sungai Sumbu X",
}


def _nz(rng, lo, hi):
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def _node(kind: str, rng: Random) -> dict:
    if kind == "point":
        x, y = _nz(rng, -6, 6), _nz(rng, -6, 6)
        return {"prompt": f"Gerbang hanya terbuka jika kamu menandai titik {fmt_point((x, y))}.", "input": "point", "range": 6,
                "q": {"type": "point", "answer": [x, y], "hint": "Geser mendatar sejauh x, lalu tegak sejauh y.", "explain": f"Titik {fmt_point((x, y))}."}}
    if kind in ("gradient", "gradient_frac"):
        while True:
            x1, x2 = rng.randint(-5, 0), rng.randint(1, 6)
            y1, y2 = rng.randint(-6, 6), rng.randint(-6, 6)
            m = gradient((x1, y1), (x2, y2))
            if m is not None and m != 0 and ((m.denominator == 1) == (kind == "gradient")):
                break
        return {"prompt": f"Hitung gradien jembatan dari A{fmt_point((x1, y1))} ke B{fmt_point((x2, y2))}.", "input": "num",
                "graph": {"range": 6, "points": [{"x": x1, "y": y1, "label": "A"}, {"x": x2, "y": y2, "label": "B"}], "lines": [{"p1": [x1, y1], "p2": [x2, y2]}]},
                "q": {"type": "num", "answer": str(m), "hint": "m = (y₂ − y₁) ÷ (x₂ − x₁).",
                      "explain": f"m = ({fmt(y2)} − {fmt_paren(y1)}) ÷ ({fmt(x2)} − {fmt_paren(x1)}) = {fmt(Fraction(y2 - y1))} ÷ {fmt(Fraction(x2 - x1))} = {fmt(m)}."}}
    if kind == "onpoint":
        m, c = _nz(rng, -3, 3), rng.randint(-4, 4)
        xs = rng.sample([-3, -2, -1, 1, 2, 3], 4)
        good = xs[0]
        options = [(good, m * good + c)] + [(x, m * x + c + rng.choice([-2, -1, 1, 2])) for x in xs[1:]]
        order = list(range(4))
        rng.shuffle(order)
        opts = [fmt_point(options[i]) for i in order]
        return {"prompt": f"Hanya satu batu loncatan yang terletak pada garis {slope_intercept(Fraction(m), Fraction(c))}. Pilih yang mana?", "input": "mc", "options": opts,
                "q": {"type": "mc", "options": opts, "answer": order.index(0), "hint": "Substitusikan x setiap titik ke persamaan, lalu bandingkan dengan y-nya.",
                      "explain": f"Untuk x = {fmt(good)}: y = {fmt(m)}·{fmt_paren(good)} + {fmt_paren(c)} = {fmt(m * good + c)}. Jadi titik {fmt_point(options[0])} terletak pada garis."}}
    if kind == "intercept_form":
        m, c = Fraction(_nz(rng, -4, 4)), Fraction(rng.randint(-5, 5))
        return {"prompt": f"Nyalakan mesin! Tulis persamaan garis bergradien {fmt(m)} yang memotong sumbu Y di (0, {fmt(c)}).", "input": "line",
                "q": {"type": "line", "answer": {"m": str(m), "c": str(c)}, "hint": "Pakai y = mx + c secara langsung.", "explain": f"{slope_intercept(m, c)}."}}
    if kind == "two_points":
        while True:
            m = Fraction(_nz(rng, -3, 3))
            c = Fraction(rng.randint(-4, 4))
            x1, x2 = rng.randint(-3, 0), rng.randint(1, 3)
            y1, y2 = m * x1 + c, m * x2 + c
            if abs(y1) <= 8 and abs(y2) <= 8:
                break
        return {"prompt": f"Bangun persamaan garis yang melalui {fmt_point((x1, y1))} dan {fmt_point((x2, y2))}.", "input": "line",
                "q": {"type": "line", "answer": {"m": str(m), "c": str(c)}, "hint": "Hitung m dulu, lalu gunakan y − y₁ = m(x − x₁).",
                      "explain": f"m = {fmt(m)}, lalu y − {fmt_paren(y1)} = {fmt(m)}(x − {fmt_paren(x1)}) → {slope_intercept(m, c)}."}}
    if kind == "relation":
        m1 = Fraction(rng.choice([1, 2, 3, -2, Fraction(1, 2), Fraction(-1, 3)]))
        rel = rng.choice(["sejajar", "tegak lurus", "berpotongan"])
        m2 = m1 if rel == "sejajar" else (-1 / m1 if rel == "tegak lurus" else m1 + 1 if m1 + 1 != -1 / m1 else m1 + 2)
        c1 = Fraction(rng.randint(-4, 4))
        c2 = c1 + rng.choice([-3, -2, 2, 3])
        options = ["sejajar", "tegak lurus", "berpotongan (tidak tegak lurus)"]
        ans = {"sejajar": 0, "tegak lurus": 1, "berpotongan": 2}[rel]
        return {"prompt": f"Dua jalan: g₁ ≡ {slope_intercept(m1, c1)} dan g₂ ≡ {slope_intercept(m2, c2)}. Bagaimana hubungan keduanya?", "input": "mc", "options": options,
                "q": {"type": "mc", "options": options, "answer": ans, "hint": "Bandingkan gradiennya: sama → sejajar, hasil kali −1 → tegak lurus.",
                      "explain": f"m₁ = {fmt(m1)}, m₂ = {fmt(m2)}, m₁ × m₂ = {fmt(m1 * m2)}. Jadi kedua garis {options[ans]}."}}
    if kind == "parallel":
        m = Fraction(rng.choice([2, -3, Fraction(1, 2), Fraction(-2, 3)]))
        x1 = rng.choice([-2, 2, 3]) * m.denominator
        y1 = rng.randint(-4, 4)
        c = y1 - m * x1
        c0 = c + rng.choice([-3, 2, 4])
        return {"prompt": f"Bangun rel yang sejajar dengan {slope_intercept(m, c0)} dan melalui {fmt_point((x1, y1))}.", "input": "line",
                "q": {"type": "line", "answer": {"m": str(m), "c": str(c)}, "hint": "Garis sejajar memiliki gradien yang sama.",
                      "explain": f"m = {fmt(m)}, lalu substitusi titik: {slope_intercept(m, c)}."}}
    if kind == "perpendicular":
        m0 = Fraction(rng.choice([2, -2, 3, Fraction(1, 2), Fraction(-1, 3)]))
        m = -1 / m0
        x1 = rng.choice([-1, 1, 2]) * m.denominator
        y1 = rng.randint(-3, 3)
        c = y1 - m * x1
        return {"prompt": f"Buat jalan yang tegak lurus dengan {slope_intercept(m0, Fraction(1))} dan melalui {fmt_point((x1, y1))}.", "input": "line",
                "q": {"type": "line", "answer": {"m": str(m), "c": str(c)}, "hint": "Gradien tegak lurus = negatif kebalikan: m₂ = −1/m₁.",
                      "explain": f"m₂ = −1/{fmt_paren(m0)} = {fmt(m)}, lalu {slope_intercept(m, c)}."}}
    if kind == "x_intercept":
        m = Fraction(_nz(rng, -4, 4))
        k = _nz(rng, -5, 5)
        c = -m * k
        return {"prompt": f"Di titik mana garis {slope_intercept(m, c)} menyeberangi sungai sumbu X? Tulis nilai x-nya.", "input": "num",
                "q": {"type": "num", "answer": str(k), "hint": "Garis memotong sumbu X saat y = 0.",
                      "explain": f"0 = {slope_intercept(m, c)[4:]} → x = {fmt(k)}. Titiknya ({fmt(k)}, 0)."}}
    raise ValueError(kind)  # pragma: no cover


def generate(rng: Random, difficulty: str):
    rounds = []
    for i, kind in enumerate(PLAN[difficulty]):
        node = _node(kind, rng)
        public = {k: v for k, v in node.items() if k != "q"}
        public["title"] = NODE_TITLES[kind]
        public["n"] = i + 1
        rounds.append({"public": public, "q": node["q"]})
    return rounds
