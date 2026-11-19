from .achievements import ACHIEVEMENTS, ACHIEVEMENT_BY_SLUG, LEVELS, V2_ACHIEVEMENTS, level_for_xp  # noqa: F401
from .assessments import ASSESSMENT_TITLES, ASSESSMENTS, POSTTEST, PRETEST, TOPIC_LESSON  # noqa: F401
from .challenges import (  # noqa: F401
    REAL_BY_SLUG,
    REAL_CASES,
    SECRET_BY_SLUG,
    SECRET_MISSIONS,
    SECRET_ORDER,
    SECRET_PASS,
)
from .lessons import LESSONS, LESSON_BY_SLUG, LESSON_ORDER, next_lesson, prev_lesson  # noqa: F401
from .questions import (  # noqa: F401
    FINAL_BANK,
    FINAL_TOPICS,
    LESSON_QUIZZES,
    QUESTION_BY_ID,
    TOPIC_LABELS,
    TRAINING_BANK,
    TRAINING_LEVELS,
)

# Semua soal (termasuk pre/post-test, misi rahasia, kehidupan nyata) untuk Mistake Notebook.
for _q in PRETEST + POSTTEST + [q for m in SECRET_MISSIONS for q in m["questions"]] + [q for c in REAL_CASES for q in c["questions"]]:
    QUESTION_BY_ID.setdefault(_q["id"], _q)
