"""Daftar lencana SCARLINE dan level berdasarkan XP."""

ACHIEVEMENTS = [
    {"slug": "first-step", "title": "First Step", "description": "Menyelesaikan misi pertama.", "icon": "flag", "xp_bonus": 30},
    {"slug": "coordinate-hunter", "title": "Coordinate Hunter", "description": "Menguasai koordinat Kartesius: menyelesaikan Coordinate City dan meraih ≥ 70% di game Coordinate Hunter.", "icon": "target", "xp_bonus": 50},
    {"slug": "gradient-master", "title": "Gradient Master", "description": "Menyelesaikan materi gradien (Gradient Mountain).", "icon": "mountain", "xp_bonus": 50},
    {"slug": "line-creator", "title": "Line Creator", "description": "Berhasil menyusun persamaan garis: menyelesaikan Line Constructor.", "icon": "pen", "xp_bonus": 50},
    {"slug": "equation-expert", "title": "Equation Expert", "description": "Menguasai bentuk persamaan: menyelesaikan Equation Factory dan meraih ≥ 80% di Training Level 3.", "icon": "flask", "xp_bonus": 75},
    {"slug": "parallel-detective", "title": "Parallel Detective", "description": "Menyelesaikan tantangan hubungan garis (Parallel & Perpendicular World).", "icon": "parallel", "xp_bonus": 50},
    {"slug": "game-explorer", "title": "Playground Explorer", "description": "Memainkan semua game di SCAR's Playground.", "icon": "gamepad", "xp_bonus": 50},
    {"slug": "daily-spark", "title": "Daily Spark", "description": "Menyelesaikan tantangan harian pertama.", "icon": "spark", "xp_bonus": 20},
    {"slug": "coordinate-explorer", "title": "Coordinate Explorer", "description": "Mengerjakan pre-test dan menyelesaikan Coordinate City.", "icon": "compass", "xp_bonus": 30},
    {"slug": "equation-solver", "title": "Equation Solver", "description": "Menyelesaikan semua Real-Life Mathematics Challenge.", "icon": "calc", "xp_bonus": 60},
    {"slug": "graph-architect", "title": "Graph Architect", "description": "Meraih ≥ 70% di Line Builder dan Gradient Rush.", "icon": "ruler", "xp_bonus": 50},
    {"slug": "line-detective", "title": "Line Detective", "description": "Meraih ≥ 70% di game Line Detective.", "icon": "search", "xp_bonus": 40},
    {"slug": "daily-streak", "title": "Daily Streak", "description": "Belajar 3 hari berturut-turut.", "icon": "flame", "xp_bonus": 40},
    {"slug": "rising-line", "title": "Rising Line", "description": "Nilai post-test lebih tinggi daripada nilai pre-test.", "icon": "growth", "xp_bonus": 60},
    {"slug": "scarline-champion", "title": "SCARLINE Champion", "description": "Menyelesaikan Final Line Challenge dengan nilai minimal 70.", "icon": "trophy", "xp_bonus": 100},
    {"slug": "master-of-straight-lines", "title": "Master of Straight Lines", "description": "Menuntaskan seluruh SCAR's Secret Mission.", "icon": "crown", "xp_bonus": 120},
]

# Lencana yang membutuhkan migrasi 002 (baris katalognya ditambahkan oleh 002_scarline_features.sql).
V2_ACHIEVEMENTS = {"coordinate-explorer", "equation-solver", "graph-architect", "line-detective", "daily-streak", "rising-line",
                   "master-of-straight-lines"}

ACHIEVEMENT_BY_SLUG = {a["slug"]: a for a in ACHIEVEMENTS}

LEVELS = [
    (0, "Line Beginner"),
    (150, "Point Seeker"),
    (350, "Gradient Climber"),
    (600, "Equation Builder"),
    (900, "Line Engineer"),
    (1250, "Equation Master"),
    (1700, "SCARLINE Legend"),
]


def level_for_xp(xp: int) -> dict:
    xp = max(0, int(xp or 0))
    level = 1
    for idx, (threshold, _name) in enumerate(LEVELS):
        if xp >= threshold:
            level = idx + 1
    floor = LEVELS[level - 1][0]
    nxt = LEVELS[level][0] if level < len(LEVELS) else None
    progress = 100 if nxt is None else int((xp - floor) * 100 / (nxt - floor))
    return {
        "level": level,
        "name": LEVELS[level - 1][1],
        "xp": xp,
        "floor": floor,
        "next": nxt,
        "to_next": None if nxt is None else nxt - xp,
        "progress": progress,
        "max_level": len(LEVELS),
    }
