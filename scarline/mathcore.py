"""Mesin matematika SCARLINE: persamaan garis lurus dengan pecahan eksak.

Semua perhitungan memakai ``fractions.Fraction`` agar hasil seperti 1/3 tidak
berubah menjadi 0.333... Modul ini dipakai oleh kalkulator Laboratory,
penilaian soal, dan generator game.
"""
from __future__ import annotations

import re
from fractions import Fraction
from math import gcd
from typing import Iterable, Optional, Tuple, Union

Number = Union[int, float, str, Fraction]
Point = Tuple[Fraction, Fraction]

MINUS = "−"  # tanda minus tipografis "−"

_NUM_RE = re.compile(r"^[+-]?(\d+(\.\d+)?|\.\d+)(\s*/\s*[+-]?\d+(\.\d+)?)?$")


class MathInputError(ValueError):
    """Input angka tidak valid (pesan dalam bahasa Indonesia)."""


def to_frac(value: Number) -> Fraction:
    """Ubah input (``"3/4"``, ``"-1,5"``, ``2``) menjadi Fraction eksak."""
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise MathInputError("Masukkan angka, bukan nilai benar/salah.")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise MathInputError("Angka tidak valid.")
        return Fraction(str(value))
    if value is None:
        raise MathInputError("Kolom angka masih kosong.")
    text = str(value).strip().replace(MINUS, "-").replace("–", "-").replace(",", ".")
    text = text.replace(" ", "")
    if not text:
        raise MathInputError("Kolom angka masih kosong.")
    if len(text) > 24 or not _NUM_RE.match(text):
        raise MathInputError(f"'{value}' bukan angka. Contoh yang benar: 2, -3, 1/2, atau 0.75.")
    if "/" in text:
        num, den = text.split("/")
        den_f = Fraction(den)
        if den_f == 0:
            raise MathInputError("Penyebut pecahan tidak boleh nol.")
        return Fraction(num) / den_f
    return Fraction(text)


def is_decimal_text(value: Number) -> bool:
    return isinstance(value, float) or (isinstance(value, str) and ("." in value or "," in value))


def fmt(value: Fraction, *, unicode_minus: bool = True) -> str:
    """Format pecahan: 2, -3, 1/2, -3/4."""
    value = Fraction(value)
    sign = "-" if value < 0 else ""
    a = abs(value)
    body = str(a.numerator) if a.denominator == 1 else f"{a.numerator}/{a.denominator}"
    out = sign + body
    return out.replace("-", MINUS) if unicode_minus else out


def fmt_paren(value: Fraction) -> str:
    """Bungkus bilangan negatif atau pecahan dengan kurung: (−2), (1/2)."""
    value = Fraction(value)
    text = fmt(value)
    if value < 0 or value.denominator != 1:
        return f"({text})"
    return text


def fmt_point(p: Iterable[Number]) -> str:
    x, y = (to_frac(v) for v in p)
    return f"({fmt(x)}, {fmt(y)})"


def coef_term(coef: Fraction, var: str) -> str:
    """Suku dengan koefisien, tanpa tanda depan: 2x, x, (1/2)x."""
    a = abs(Fraction(coef))
    if a == 1:
        return var
    if a.denominator != 1:
        return f"({a.numerator}/{a.denominator}){var}"
    return f"{a.numerator}{var}"


def signed(value: Fraction, *, first: bool = False) -> str:
    """Tulis konstanta sebagai suku: '+ 3', '− 2' (atau '3', '−2' jika di depan)."""
    value = Fraction(value)
    if first:
        return fmt(value)
    return f"{'+' if value >= 0 else MINUS} {fmt(abs(value))}"


def slope_intercept(m: Fraction, c: Fraction) -> str:
    """y = mx + c dalam bentuk paling rapi."""
    m, c = Fraction(m), Fraction(c)
    if m == 0:
        return f"y = {fmt(c)}"
    head = ("" if m > 0 else MINUS) + coef_term(m, "x")
    if c == 0:
        return f"y = {head}"
    return f"y = {head} {signed(c)}"


def x_minus(value: Fraction, var: str = "x") -> str:
    """(x − x₁) yang sudah disederhanakan: x − 3, x + 2, x."""
    value = Fraction(value)
    if value == 0:
        return var
    if value > 0:
        return f"{var} {MINUS} {fmt(value)}"
    return f"{var} + {fmt(-value)}"


def _lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)


def general_form(m: Optional[Fraction], c: Optional[Fraction], x_vertical: Optional[Fraction] = None) -> str:
    """Bentuk umum ax + by + c = 0 dengan koefisien bulat (a ≥ 0)."""
    if m is None:
        k = Fraction(x_vertical)
        a, cc = k.denominator, -k.numerator
        return _join_general(a, 0, cc)
    m, c = Fraction(m), Fraction(c)
    # y = mx + c  ->  mx - y + c = 0
    den = _lcm(m.denominator, c.denominator)
    a = int(m * den)
    b = -den
    cc = int(c * den)
    g = gcd(gcd(abs(a), abs(b)), abs(cc)) or 1
    a, b, cc = a // g, b // g, cc // g
    if a < 0 or (a == 0 and b < 0):
        a, b, cc = -a, -b, -cc
    return _join_general(a, b, cc)


def _join_general(a: int, b: int, c: int) -> str:
    parts = []
    for coef, var in ((a, "x"), (b, "y")):
        if coef == 0:
            continue
        term = coef_term(Fraction(coef), var)
        if not parts:
            parts.append(("" if coef > 0 else MINUS) + term)
        else:
            parts.append(f"{'+' if coef > 0 else MINUS} {term}")
    if c != 0:
        parts.append(signed(Fraction(c), first=not parts))
    return " ".join(parts) + " = 0"


def gradient(p1: Iterable[Number], p2: Iterable[Number]) -> Optional[Fraction]:
    """Gradien dua titik; None jika garis vertikal."""
    x1, y1 = (to_frac(v) for v in p1)
    x2, y2 = (to_frac(v) for v in p2)
    if x1 == x2 and y1 == y2:
        raise MathInputError("Kedua titik sama. Butuh dua titik yang berbeda untuk membentuk garis.")
    if x1 == x2:
        return None
    return (y2 - y1) / (x2 - x1)


def x_intercept(m: Fraction, c: Fraction) -> Optional[Fraction]:
    m, c = Fraction(m), Fraction(c)
    if m == 0:
        return None
    return -c / m


def quadrant(x: Number, y: Number) -> str:
    x, y = to_frac(x), to_frac(y)
    if x == 0 and y == 0:
        return "titik asal O(0, 0)"
    if x == 0:
        return "sumbu Y"
    if y == 0:
        return "sumbu X"
    if x > 0 and y > 0:
        return "Kuadran I"
    if x < 0 < y:
        return "Kuadran II"
    if x < 0 and y < 0:
        return "Kuadran III"
    return "Kuadran IV"


def slope_direction(m: Optional[Fraction]) -> str:
    if m is None:
        return "tegak (vertikal) — gradien tidak terdefinisi"
    if m > 0:
        return "naik dari kiri ke kanan (gradien positif)"
    if m < 0:
        return "turun dari kiri ke kanan (gradien negatif)"
    return "mendatar (horizontal) — gradien nol"


def relation(m1: Optional[Fraction], m2: Optional[Fraction], c1=None, c2=None, x1=None, x2=None) -> str:
    """Hubungan dua garis: 'berimpit', 'sejajar', 'tegak lurus', 'berpotongan'."""
    if m1 is None and m2 is None:
        return "berimpit" if x1 is not None and x1 == x2 else "sejajar"
    if m1 is None or m2 is None:
        other = m2 if m1 is None else m1
        return "tegak lurus" if other == 0 else "berpotongan"
    if m1 == m2:
        if c1 is not None and c1 == c2:
            return "berimpit"
        return "sejajar"
    if m1 * m2 == -1:
        return "tegak lurus"
    return "berpotongan"


def _line_result(m: Optional[Fraction], c: Optional[Fraction], x_vertical=None) -> dict:
    if m is None:
        k = Fraction(x_vertical)
        return {
            "vertical": True,
            "x": fmt(k),
            "x_value": float(k),
            "gradient": "tidak terdefinisi",
            "equation": f"x = {fmt(k)}",
            "general": general_form(None, None, k),
            "y_intercept": "tidak ada" if k != 0 else "seluruh sumbu Y",
            "x_intercept": fmt_point((k, 0)),
            "direction": slope_direction(None),
            "sample_points": [fmt_point((k, j)) for j in (-2, 0, 2)],
        }
    xi = x_intercept(m, c)
    return {
        "vertical": False,
        "m": fmt(m),
        "c": fmt(c),
        "m_value": float(m),
        "c_value": float(c),
        "gradient": fmt(m),
        "equation": slope_intercept(m, c),
        "general": general_form(m, c),
        "y_intercept": fmt_point((0, c)),
        "x_intercept": fmt_point((xi, 0)) if xi is not None else ("tidak ada (garis sejajar sumbu X)" if c != 0 else "seluruh sumbu X"),
        "direction": slope_direction(m),
        "sample_points": [fmt_point((x, m * x + c)) for x in (Fraction(-1), Fraction(0), Fraction(1), Fraction(2))],
    }


def from_two_points(p1: Iterable[Number], p2: Iterable[Number]) -> dict:
    """Persamaan garis dari dua titik lengkap dengan langkah penyelesaian."""
    x1, y1 = (to_frac(v) for v in p1)
    x2, y2 = (to_frac(v) for v in p2)
    m = gradient((x1, y1), (x2, y2))
    steps = [
        f"Diketahui titik A{fmt_point((x1, y1))} dan B{fmt_point((x2, y2))}.",
        "Rumus gradien: m = (y₂ − y₁) / (x₂ − x₁).",
    ]
    if m is None:
        steps += [
            f"x₂ − x₁ = {fmt(x2)} − {fmt_paren(x1)} = 0, sehingga penyebutnya nol.",
            "Pembagian dengan nol tidak terdefinisi, jadi gradiennya TIDAK TERDEFINISI.",
            f"Kedua titik memiliki x yang sama, sehingga garisnya vertikal: x = {fmt(x1)}.",
        ]
        result = _line_result(None, None, x1)
    else:
        dy, dx = y2 - y1, x2 - x1
        steps.append(
            f"m = ({fmt(y2)} − {fmt_paren(y1)}) / ({fmt(x2)} − {fmt_paren(x1)}) = {fmt(dy)} / {fmt(dx)} = {fmt(m)}."
        )
        steps += _point_slope_steps(m, x1, y1)
        result = _line_result(m, y1 - m * x1)
    result["steps"] = steps
    result["points"] = [[float(x1), float(y1)], [float(x2), float(y2)]]
    return result


def _point_slope_steps(m: Fraction, x1: Fraction, y1: Fraction) -> list:
    c = y1 - m * x1
    m_txt = fmt(m) if m.denominator == 1 else f"({fmt(m)})"
    steps = [
        "Substitusi ke rumus y − y₁ = m(x − x₁).",
        f"{x_minus(y1, 'y')} = {m_txt}({x_minus(x1)})",
    ]
    if x1 == 0:
        rhs = coef_term_signed(m) if m != 0 else "0"
    else:
        rhs = (coef_term_signed(m) + " " + signed(-m * x1)) if m != 0 else "0"
    steps.append(f"{x_minus(y1, 'y')} = {rhs}")
    if y1 != 0:
        how = f"kedua ruas ditambah {fmt(y1)}" if y1 > 0 else f"kedua ruas dikurangi {fmt(-y1)}"
        steps.append(f"y = {rhs} {signed(y1)}  ({how})")
    steps.append(f"Hasil akhir: {slope_intercept(m, c)}.")
    return steps


def coef_term_signed(m: Fraction) -> str:
    m = Fraction(m)
    if m == 0:
        return "0"
    return ("" if m > 0 else MINUS) + coef_term(m, "x")


def from_point_slope(m: Number, p: Iterable[Number]) -> dict:
    m = to_frac(m)
    x1, y1 = (to_frac(v) for v in p)
    steps = [
        f"Diketahui gradien m = {fmt(m)} dan titik {fmt_point((x1, y1))}.",
    ]
    steps += _point_slope_steps(m, x1, y1)
    result = _line_result(m, y1 - m * x1)
    result["steps"] = steps
    result["points"] = [[float(x1), float(y1)]]
    return result


def from_slope_intercept(m: Number, c: Number) -> dict:
    m, c = to_frac(m), to_frac(c)
    steps = [
        f"Diketahui gradien m = {fmt(m)} dan garis memotong sumbu Y di (0, {fmt(c)}), jadi c = {fmt(c)}.",
        "Gunakan bentuk y = mx + c.",
        f"y = {fmt_paren(m)}x + {fmt_paren(c)}",
        f"Hasil akhir: {slope_intercept(m, c)}.",
    ]
    if c == 0:
        steps.insert(3, "Karena c = 0, garis melalui titik pusat O(0, 0).")
    result = _line_result(m, c)
    result["steps"] = steps
    result["points"] = [[0.0, float(c)]]
    return result


def gradient_steps(p1: Iterable[Number], p2: Iterable[Number]) -> dict:
    x1, y1 = (to_frac(v) for v in p1)
    x2, y2 = (to_frac(v) for v in p2)
    m = gradient((x1, y1), (x2, y2))
    steps = [
        f"Diketahui A{fmt_point((x1, y1))} dan B{fmt_point((x2, y2))}.",
        "m = Δy / Δx = (y₂ − y₁) / (x₂ − x₁).",
        f"Δy = {fmt(y2)} − {fmt_paren(y1)} = {fmt(y2 - y1)}.",
        f"Δx = {fmt(x2)} − {fmt_paren(x1)} = {fmt(x2 - x1)}.",
    ]
    if m is None:
        steps.append("Δx = 0, pembagian dengan nol tidak terdefinisi → gradien TIDAK TERDEFINISI (garis vertikal).")
        line = _line_result(None, None, x1)
    else:
        steps.append(f"m = {fmt(y2 - y1)} / {fmt(x2 - x1)} = {fmt(m)}.")
        steps.append(f"Artinya garis {slope_direction(m)}.")
        line = _line_result(m, y1 - m * x1)
    line["steps"] = steps
    line["points"] = [[float(x1), float(y1)], [float(x2), float(y2)]]
    return line


def through_origin(m: Number) -> dict:
    m = to_frac(m)
    res = from_slope_intercept(m, 0)
    res["steps"] = [
        f"Garis melalui titik pusat O(0, 0) dengan gradien m = {fmt(m)}.",
        "Substitusi O(0, 0) ke y = mx + c: 0 = m·0 + c, jadi c = 0.",
        "Bentuk persamaannya y = mx.",
        f"Hasil akhir: {slope_intercept(m, 0)}.",
    ]
    return res


def on_line(point: Iterable[Number], m: Number, c: Number) -> bool:
    x, y = (to_frac(v) for v in point)
    return y == to_frac(m) * x + to_frac(c)


def to_float_pair(p) -> list:
    return [float(to_frac(p[0])), float(to_frac(p[1]))]
