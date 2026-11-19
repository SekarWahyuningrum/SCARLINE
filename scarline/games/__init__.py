"""Registri game SCAR's Playground."""
from . import (
    coordinate_hunter,
    equation_puzzle,
    gradient_rush,
    line_builder,
    line_detective,
    line_rescue,
    parallel_perpendicular,
)

MODULES = [coordinate_hunter, gradient_rush, line_builder, equation_puzzle, line_detective, parallel_perpendicular, line_rescue]
GAMES = [m.INFO for m in MODULES]
GAME_BY_SLUG = {m.INFO["slug"]: m for m in MODULES}

# Game yang baris katalognya ditambahkan oleh migrasi 002_scarline_features.sql.
V2_GAMES = {"line-detective", "parallel-perpendicular"}

DIFFICULTIES = {
    "easy": {"label": "Mudah", "mult": 1.0},
    "medium": {"label": "Sedang", "mult": 1.25},
    "hard": {"label": "Sulit", "mult": 1.5},
}
