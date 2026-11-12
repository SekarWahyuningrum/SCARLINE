"""GAME 1 — Coordinate Hunter: klik lokasi titik koordinat yang tepat."""
from random import Random

from ..mathcore import fmt_point, quadrant

INFO = {
    "slug": "coordinate-hunter",
    "title": "Coordinate Hunter",
    "tagline": "Berburu Titik Koordinat",
    "icon": "target",
    "story": "SCAR kehilangan titik-titik penting di dunia koordinat. Temukan kembali setiap titik agar peta SCARLINE WORLD bisa terbuka!",
    "goal": "Memahami posisi titik (x, y) pada bidang koordinat Kartesius.",
    "mechanic": "Klik titik koordinat",
    "rules": [
        "SCAR memberi target koordinat, misalnya (3, 4).",
        "Klik persimpangan grid yang tepat. Titik akan otomatis menempel ke grid.",
        "Kamu punya 3 kesempatan per titik. Jika salah, SCAR memberi petunjuk.",
        "Benar di percobaan ke-1 = 100 poin, ke-2 = 60 poin, ke-3 = 30 poin.",
    ],
    "levels": {"easy": "6 titik di Kuadran I", "medium": "8 titik di semua kuadran", "hard": "10 titik, termasuk titik di sumbu, bidang lebih luas"},
    "max_tries": 3,
}

CONFIG = {"easy": (6, 6), "medium": (8, 6), "hard": (10, 8)}


def generate(rng: Random, difficulty: str):
    count, limit = CONFIG[difficulty]
    targets = []
    seen = set()
    quads = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    while len(targets) < count:
        i = len(targets)
        if difficulty == "easy":
            x, y = rng.randint(1, 5), rng.randint(1, 5)
        elif difficulty == "medium":
            sx, sy = quads[i % 4]
            x, y = sx * rng.randint(1, 6), sy * rng.randint(1, 6)
        else:
            if i % 4 == 3:  # titik di sumbu
                v = rng.choice([-1, 1]) * rng.randint(1, 7)
                x, y = (0, v) if rng.random() < 0.5 else (v, 0)
            else:
                sx, sy = quads[i % 4]
                x, y = sx * rng.randint(1, 7), sy * rng.randint(1, 7)
        if (x, y) in seen:
            continue
        seen.add((x, y))
        targets.append((x, y))
    rounds = []
    for n, (x, y) in enumerate(targets, start=1):
        rounds.append({
            "public": {"target": [x, y], "label": fmt_point((x, y)), "range": limit, "n": n},
            "q": {
                "type": "point",
                "answer": [x, y],
                "hint": f"Mulai dari O(0, 0): {abs(x)} langkah ke {'kanan' if x > 0 else 'kiri' if x < 0 else '(tetap di sumbu Y)'}, lalu {abs(y)} langkah ke {'atas' if y > 0 else 'bawah' if y < 0 else '(tetap di sumbu X)'}.",
                "explain": f"Titik {fmt_point((x, y))} berada di {quadrant(x, y)}.",
            },
        })
    return rounds
