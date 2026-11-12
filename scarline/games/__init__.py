"""Registri lima game SCAR's Playground."""
from . import coordinate_hunter, equation_puzzle, gradient_rush, line_builder, line_rescue

MODULES = [coordinate_hunter, gradient_rush, line_builder, equation_puzzle, line_rescue]
GAMES = [m.INFO for m in MODULES]
GAME_BY_SLUG = {m.INFO["slug"]: m for m in MODULES}

DIFFICULTIES = {
    "easy": {"label": "Mudah", "mult": 1.0},
    "medium": {"label": "Sedang", "mult": 1.25},
    "hard": {"label": "Sulit", "mult": 1.5},
}
