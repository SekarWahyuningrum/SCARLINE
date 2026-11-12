"""Periksa sintaks semua file JavaScript SCARLINE (ES2017) dengan parser esprima.

Pemakaian:  python scripts/check_js.py
"""
import sys
from pathlib import Path

import esprima

ROOT = Path(__file__).resolve().parents[1]
failed = 0
files = sorted((ROOT / "scarline" / "static" / "js").rglob("*.js"))
for path in files:
    try:
        esprima.parseScript(path.read_text(encoding="utf-8"))
        print(f"OK   {path.relative_to(ROOT)}")
    except esprima.Error as exc:
        failed += 1
        print(f"FAIL {path.relative_to(ROOT)}: {exc}")
print(f"{len(files) - failed}/{len(files)} file lolos.")
sys.exit(1 if failed else 0)
