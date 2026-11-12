"""Pengujian mesin matematika, bank soal, dan generator game."""
import random
from fractions import Fraction

import pytest

from scarline import mathcore as mc
from scarline.content import FINAL_BANK, LESSON_QUIZZES, LESSONS, QUESTION_BY_ID, TRAINING_BANK
from scarline.games import GAME_BY_SLUG
from scarline.grading import grade, public_question
from scarline.mathcore import MathInputError


@pytest.mark.parametrize("raw,expected", [
    ("3/4", Fraction(3, 4)), ("-1,5", Fraction(-3, 2)), ("−2", Fraction(-2)), (" 10 ", Fraction(10)),
    (2, Fraction(2)), ("0.25", Fraction(1, 4)), ("-6/-3", Fraction(2)),
])
def test_to_frac(raw, expected):
    assert mc.to_frac(raw) == expected


@pytest.mark.parametrize("raw", ["", "abc", "1/0", "2x", None, "1..2", True])
def test_to_frac_invalid(raw):
    with pytest.raises(MathInputError):
        mc.to_frac(raw)


def test_gradient_cases():
    assert mc.gradient((1, 2), (3, 8)) == 3
    assert mc.gradient((-2, 4), (2, -4)) == -2
    assert mc.gradient((-1, 3), (4, 3)) == 0
    assert mc.gradient((2, 1), (2, 5)) is None
    with pytest.raises(MathInputError):
        mc.gradient((1, 1), (1, 1))


def test_from_two_points():
    r = mc.from_two_points((1, 1), (3, 7))
    assert r["equation"] == "y = 3x − 2" and r["general"] == "3x − y − 2 = 0"
    r = mc.from_two_points((-1, 5), (3, -3))
    assert r["equation"] == "y = −2x + 3"
    v = mc.from_two_points((2, 1), (2, 5))
    assert v["vertical"] and v["equation"] == "x = 2" and v["gradient"] == "tidak terdefinisi"


def test_point_slope_and_others():
    assert mc.from_point_slope(3, (2, 5))["equation"] == "y = 3x − 1"
    assert mc.from_point_slope("-1/2", (4, 1))["equation"] == "y = −(1/2)x + 3"
    assert mc.from_slope_intercept(-2, 4)["equation"] == "y = −2x + 4"
    assert mc.through_origin(2)["equation"] == "y = 2x"
    assert mc.general_form(Fraction(-3, 2), Fraction(3)) == "3x + 2y − 6 = 0"
    assert mc.x_intercept(Fraction(2), Fraction(-6)) == 3


def test_relation():
    assert mc.relation(Fraction(2), Fraction(2), 1, -3) == "sejajar"
    assert mc.relation(Fraction(2), Fraction(2), 3, 3) == "berimpit"
    assert mc.relation(Fraction(2), Fraction(-1, 2)) == "tegak lurus"
    assert mc.relation(Fraction(0), None) == "tegak lurus"
    assert mc.relation(Fraction(1), Fraction(3)) == "berpotongan"


def test_quadrants():
    assert mc.quadrant(3, 4) == "Kuadran I"
    assert mc.quadrant(-3, 4) == "Kuadran II"
    assert mc.quadrant(-3, -4) == "Kuadran III"
    assert mc.quadrant(3, -4) == "Kuadran IV"
    assert mc.quadrant(0, 6) == "sumbu Y"


def all_qs():
    for qs in LESSON_QUIZZES.values():
        yield from qs
    for qs in TRAINING_BANK.values():
        yield from qs
    yield from FINAL_BANK


@pytest.mark.parametrize("q", list(all_qs()), ids=lambda q: q["id"])
def test_every_answer_key_is_correct_and_documented(q):
    assert grade(q, q["answer"])["correct"]
    assert q.get("explain"), "setiap soal wajib memiliki pembahasan"
    pub = public_question(q)
    assert "answer" not in pub and "explain" not in pub


def test_question_ids_unique():
    ids = [q["id"] for q in all_qs()]
    assert len(ids) == len(set(ids)) == len(QUESTION_BY_ID)


def test_wrong_answers_get_specific_feedback():
    q = QUESTION_BY_ID["T2-02"]  # m = -2
    assert "terbalik" in grade(q, "2")["feedback"]
    assert "tertukar" in grade(q, "-1/2")["feedback"]
    p = QUESTION_BY_ID["T1-02"]  # (-4, 2)
    assert "tertukar" in grade(p, [2, -4])["feedback"]
    l = QUESTION_BY_ID["T3-01"]  # y = 2x - 1
    assert "Gradienmu (m) sudah tepat" in grade(l, {"m": "2", "c": "3"})["feedback"]
    m = QUESTION_BY_ID["T3-06"]
    assert not grade(m, [[0, 3], [1, 2]])["correct"]
    assert grade(QUESTION_BY_ID["M6-2"], "1/4")["feedback"].startswith("Kamu sudah membalik")


def test_decimal_tolerance_for_repeating():
    q = QUESTION_BY_ID["F20"]  # -1/3
    assert grade(q, "-0.33")["correct"]
    assert not grade(q, "-0.3")["correct"]


def test_mathematical_facts_in_question_bank():
    """Cek ulang beberapa kunci dengan mesin matematika (bukan sekadar menyalin kunci)."""
    assert mc.gradient((2, 3), (4, 7)) == 2 and mc.from_two_points((2, 3), (4, 7))["c"] == "−1"
    assert mc.from_point_slope("-1/2", (4, 1))["c"] == "3"
    assert mc.from_two_points((-2, 1), (2, 9))["equation"] == "y = 2x + 5"
    assert mc.from_two_points((6, 0), (0, 3))["equation"] == "y = −(1/2)x + 3"
    assert mc.from_point_slope(Fraction(-1, 3), (3, 1))["equation"] == "y = −(1/3)x + 2"
    assert mc.from_point_slope(Fraction(3, 2), (2, 0))["equation"] == "y = (3/2)x − 3"


def test_lessons_have_full_structure():
    assert len(LESSONS) == 7
    for l in LESSONS:
        for key in ("region", "no", "title", "objectives", "concepts", "formulas", "diagram", "daily", "fact", "activity", "summary"):
            assert l.get(key), (l["slug"], key)
        assert l["examples"] or l.get("cases")
        assert len(LESSON_QUIZZES[l["slug"]]) == 3
        for f in l["formulas"]:
            assert f["symbols"], "rumus wajib disertai arti simbol"


def test_activity_answers_consistent():
    act = next(l for l in LESSONS if l["slug"] == "line-constructor")["activity"]
    for ch in act["challenges"]:
        m, c = mc.to_frac(ch["m"]), mc.to_frac(ch["c"])
        for p in ch["show"]:
            assert mc.on_line(p, m, c), ch
    pp = next(l for l in LESSONS if l["slug"] == "parallel-perpendicular")["activity"]
    lines = {l["id"]: mc.to_frac(l["m"]) for l in pp["lines"]}
    a, b = pp["parallel"]
    assert lines[a] == lines[b]
    a, b = pp["perpendicular"]
    assert lines[a] * lines[b] == -1
    # pasangan sejajar/tegak lurus harus unik
    ids = list(lines)
    par = [(x, y) for i, x in enumerate(ids) for y in ids[i + 1:] if lines[x] == lines[y]]
    perp = [(x, y) for i, x in enumerate(ids) for y in ids[i + 1:] if lines[x] * lines[y] == -1]
    assert par == [tuple(pp["parallel"])] and perp == [tuple(pp["perpendicular"])]
    for case in next(l for l in LESSONS if l["slug"] == "real-life")["cases"]:
        assert mc.to_frac(case["answer"]) is not None


@pytest.mark.parametrize("slug", list(GAME_BY_SLUG))
@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_game_generators_are_solvable(slug, difficulty):
    mod = GAME_BY_SLUG[slug]
    for seed in range(120):
        rounds = mod.generate(random.Random(seed), difficulty)
        assert rounds
        again = mod.generate(random.Random(seed), difficulty)
        assert [r["public"] for r in rounds] == [r["public"] for r in again], "ronde harus deterministik dari seed"
        for r in rounds:
            if r.get("q"):
                assert grade(r["q"], r["q"]["answer"])["correct"]
                assert "answer" not in r["public"] or slug == "coordinate-hunter"
            elif r["kind"] == "set":
                m = Fraction(r["m"])
                assert mod.check(r, {"rise": m.numerator, "run": m.denominator})["correct"]
            elif r["kind"] == "pick":
                assert mod.check(r, r["answer"])["correct"]
            else:
                inv = {v: k for k, v in r["tiles"].items()}
                assert mod.check(r, [inv[t] for t in r["solution_tokens"]])["correct"]
