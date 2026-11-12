"""Buat supabase/seed.sql dari konten Python SCARLINE (materi, soal, game, lencana).

Pemakaian:
    python scripts/generate_seed.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scarline.content import (  # noqa: E402
    ACHIEVEMENTS,
    FINAL_BANK,
    LESSON_QUIZZES,
    LESSONS,
    TRAINING_BANK,
    TRAINING_LEVELS,
)
from scarline.games import GAMES  # noqa: E402


def q(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def j(value) -> str:
    return q(json.dumps(value, ensure_ascii=False)) + "::jsonb"


def build() -> str:
    out = ["-- File ini DIBUAT OTOMATIS oleh scripts/generate_seed.py — jangan diedit manual.", "begin;", ""]

    out.append("-- Materi (7 misi)")
    for l in LESSONS:
        out.append(
            "insert into public.lessons (slug, mission_no, region, title, xp_reward) values "
            f"({q(l['slug'])}, {l['no']}, {q(l['region'])}, {q(l['title'])}, {l['xp']}) "
            "on conflict (slug) do update set mission_no = excluded.mission_no, region = excluded.region, title = excluded.title, xp_reward = excluded.xp_reward;"
        )

    quizzes = []
    for l in LESSONS:
        quizzes.append((f"lesson-{l['slug']}", f"Mini quiz Mission {l['no']:02d} — {l['region']}", "lesson", None, l["slug"], LESSON_QUIZZES[l["slug"]]))
    for lvl, info in TRAINING_LEVELS.items():
        quizzes.append((f"training-{lvl}", f"Training Level {lvl} — {info['name']}", "training", lvl, None, TRAINING_BANK[lvl]))
    quizzes.append(("daily", "Tantangan Harian", "daily", None, None, []))
    quizzes.append(("final-challenge", "Final Line Challenge", "final", None, None, FINAL_BANK))

    out += ["", "-- Kuis"]
    for slug, title, kind, level, lesson, _ in quizzes:
        out.append(
            "insert into public.quizzes (slug, title, kind, level, lesson_slug) values "
            f"({q(slug)}, {q(title)}, {q(kind)}, {q(level)}, {q(lesson)}) "
            "on conflict (slug) do update set title = excluded.title, kind = excluded.kind, level = excluded.level, lesson_slug = excluded.lesson_slug;"
        )

    out += ["", "-- Bank soal (kunci jawaban hanya dapat dibaca service role)"]
    for slug, _t, _k, _lv, _ls, questions in quizzes:
        for pos, item in enumerate(questions):
            payload = {k: item[k] for k in ("options", "graph", "range", "items", "hint") if k in item}
            out.append(
                "insert into public.quiz_questions (id, quiz_slug, qtype, topic, prompt, payload, answer, explanation, position) values "
                f"({q(item['id'])}, {q(slug)}, {q(item['type'])}, {q(item['topic'])}, {q(item['prompt'])}, {j(payload)}, {j(item['answer'])}, {q(item.get('explain', ''))}, {pos}) "
                "on conflict (id) do update set quiz_slug = excluded.quiz_slug, qtype = excluded.qtype, topic = excluded.topic, prompt = excluded.prompt, "
                "payload = excluded.payload, answer = excluded.answer, explanation = excluded.explanation, position = excluded.position;"
            )

    out += ["", "-- Game"]
    for g in GAMES:
        out.append(
            "insert into public.games (slug, title, tagline, mechanic, description) values "
            f"({q(g['slug'])}, {q(g['title'])}, {q(g['tagline'])}, {q(g['mechanic'])}, {q(g['goal'])}) "
            "on conflict (slug) do update set title = excluded.title, tagline = excluded.tagline, mechanic = excluded.mechanic, description = excluded.description;"
        )

    out += ["", "-- Lencana"]
    for i, a in enumerate(ACHIEVEMENTS):
        out.append(
            "insert into public.achievements (slug, title, description, icon, xp_bonus, sort_order) values "
            f"({q(a['slug'])}, {q(a['title'])}, {q(a['description'])}, {q(a['icon'])}, {a['xp_bonus']}, {i}) "
            "on conflict (slug) do update set title = excluded.title, description = excluded.description, icon = excluded.icon, xp_bonus = excluded.xp_bonus, sort_order = excluded.sort_order;"
        )

    out += ["", "commit;", ""]
    return "\n".join(out)


if __name__ == "__main__":
    target = ROOT / "supabase" / "seed.sql"
    target.write_text(build(), encoding="utf-8")
    print(f"Seed ditulis ke {target.relative_to(ROOT)}")
