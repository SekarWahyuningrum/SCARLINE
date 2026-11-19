"""Sertifikat pencapaian SCARLINE dalam format PDF (A4 lanskap).

Ditulis langsung dengan perintah PDF dasar dan font standar (Helvetica) sehingga
tidak memerlukan pustaka tambahan. Nama, nilai, gelar, dan tanggal diambil dari
data yang tersimpan di server — tidak bisa diubah dari browser.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

W, H = 842, 595  # A4 lanskap dalam satuan point
WIB = timezone(timedelta(hours=7))
MONTHS = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

_REG = dict(zip(" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~",
                [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278] + [556] * 10 +
                [278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778, 667,
                 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333, 556, 556, 500, 556, 556, 278, 556,
                 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584]))
_BOLD = dict(_REG)
_BOLD.update(dict(zip("abcdefghijklmnopqrstuvwxyzAJKL", [556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611, 611,
                                                      611, 389, 556, 333, 611, 556, 778, 556, 556, 500, 722, 556, 722, 611])))


def _width(text: str, size: float, bold: bool) -> float:
    table = _BOLD if bold else _REG
    return sum(table.get(ch, 556) for ch in text) * size / 1000


def _esc(text: str) -> str:
    raw = text.encode("cp1252", errors="replace").decode("latin-1")
    return raw.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _fit(text: str, size: float, bold: bool, max_w: float) -> float:
    while size > 10 and _width(text, size, bold) > max_w:
        size -= 1
    return size


def tanggal(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        dt = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    d = dt.astimezone(WIB)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


class _Canvas:
    def __init__(self):
        self.ops: list = []

    def rgb(self, hex_color: str, stroke: bool = False):
        r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
        self.ops.append(f"{r:.3f} {g:.3f} {b:.3f} {'RG' if stroke else 'rg'}")

    def rect(self, x, y, w, h, fill=None, stroke=None, lw=1):
        if fill:
            self.rgb(fill)
        if stroke:
            self.rgb(stroke, stroke=True)
            self.ops.append(f"{lw} w")
        op = "B" if fill and stroke else ("f" if fill else "S")
        self.ops.append(f"{x} {y} {w} {h} re {op}")

    def line(self, x1, y1, x2, y2, color, lw=1, dash=None):
        self.rgb(color, stroke=True)
        self.ops.append(f"{lw} w")
        self.ops.append(f"[{dash}] 0 d" if dash else "[] 0 d")
        self.ops.append(f"{x1} {y1} m {x2} {y2} l S")
        self.ops.append("[] 0 d")

    def circle(self, cx, cy, r, fill=None, stroke=None, lw=1):
        k = 0.5523 * r
        path = (f"{cx + r} {cy} m {cx + r} {cy + k} {cx + k} {cy + r} {cx} {cy + r} c "
                f"{cx - k} {cy + r} {cx - r} {cy + k} {cx - r} {cy} c {cx - r} {cy - k} {cx - k} {cy - r} {cx} {cy - r} c "
                f"{cx + k} {cy - r} {cx + r} {cy - k} {cx + r} {cy} c")
        if fill:
            self.rgb(fill)
        if stroke:
            self.rgb(stroke, stroke=True)
            self.ops.append(f"{lw} w")
        self.ops.append(path + (" B" if fill and stroke else (" f" if fill else " S")))

    def text(self, x, y, text, size, color="#25334A", bold=False, italic=False, align="left"):
        font = "F2" if bold else ("F3" if italic else "F1")
        if align == "center":
            x = x - _width(text, size, bold) / 2
        elif align == "right":
            x = x - _width(text, size, bold)
        self.rgb(color)
        self.ops.append(f"BT /{font} {size} Tf {x:.2f} {y:.2f} Td ({_esc(text)}) Tj ET")


def build_certificate_pdf(name: str, score: int, title: str, issued_iso: str) -> bytes:
    navy, orange, teal, cream, paper, gold = "#25334A", "#C87945", "#648B83", "#F4EBDD", "#E8D8BD", "#E6C878"
    c = _Canvas()
    c.rect(0, 0, W, H, fill=cream)
    # kisi kertas grafik
    for x in range(36, W - 30, 24):
        c.line(x, 30, x, H - 30, "#DCCFB8", 0.4)
    for y in range(30, H - 24, 24):
        c.line(30, y, W - 30, y, "#DCCFB8", 0.4)
    c.rect(22, 22, W - 44, H - 44, stroke=navy, lw=4)
    c.rect(32, 32, W - 64, H - 64, stroke=orange, lw=1.5)
    c.rect(32, H - 112, W - 64, 80, fill=navy)
    c.text(W / 2, H - 70, "SCARLINE", 30, color=cream, bold=True, align="center")
    c.text(W / 2, H - 94, "A Mathematics Learning Experience", 12, color=gold, align="center")
    # dekorasi: garis lurus melalui titik pada kisi
    c.line(60, 70, 230, 200, teal, 2.5)
    for px, py in ((60, 70), (145, 135), (230, 200)):
        c.circle(px, py, 4.5, fill=orange, stroke=navy, lw=1.2)
    c.text(118, 175, "y = mx + c", 11, color=teal, italic=True)
    c.line(612, 200, 782, 70, orange, 2.5, dash="6 4")
    c.text(W / 2, H - 160, "SERTIFIKAT PENCAPAIAN", 24, color=navy, bold=True, align="center")
    c.text(W / 2, H - 190, "Dengan bangga diberikan kepada", 13, color="#55627A", align="center")
    size = _fit(name, 34, True, W - 220)
    c.text(W / 2, H - 238, name, size, color=orange, bold=True, align="center")
    c.line(W / 2 - 230, H - 250, W / 2 + 230, H - 250, navy, 1.2)
    c.text(W / 2, H - 278, "atas keberhasilan menuntaskan petualangan belajar", 13, color=navy, align="center")
    c.text(W / 2, H - 302, "Persamaan Garis Lurus  -  Matematika SMP Kelas VIII", 16, color=navy, bold=True, align="center")
    # kotak nilai & gelar
    c.rect(W / 2 - 250, H - 390, 230, 62, fill=paper, stroke=navy, lw=1.5)
    c.text(W / 2 - 135, H - 350, "NILAI AKHIR (POST-TEST)", 9.5, color="#55627A", bold=True, align="center")
    c.text(W / 2 - 135, H - 378, f"{int(score)} / 100", 22, color=navy, bold=True, align="center")
    c.rect(W / 2 + 20, H - 390, 230, 62, fill=paper, stroke=navy, lw=1.5)
    c.text(W / 2 + 135, H - 350, "GELAR PENCAPAIAN", 9.5, color="#55627A", bold=True, align="center")
    gsize = _fit(title, 17, True, 210)
    c.text(W / 2 + 135, H - 376, title, gsize, color=teal, bold=True, align="center")
    # segel SCAR
    c.circle(W - 130, 118, 46, fill=gold, stroke=navy, lw=3)
    c.circle(W - 130, 118, 36, stroke=orange, lw=1.5)
    c.text(W - 130, 122, "SCAR", 15, color=navy, bold=True, align="center")
    c.text(W - 130, 106, "APPROVED", 7.5, color=navy, bold=True, align="center")
    c.text(150, 92, f"Diterbitkan: {tanggal(issued_iso)}", 11.5, color=navy, align="left")
    c.line(150, 82, 360, 82, navy, 0.8)
    c.text(150, 66, "SCAR - Pemandu Petualangan SCARLINE", 9.5, color="#55627A", italic=True)
    c.text(W / 2, 44, "Discover the Line, Master the Equation!", 9, color="#55627A", italic=True, align="center")
    return _assemble("\n".join(c.ops).encode("latin-1"))


def _assemble(content: bytes) -> bytes:
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {W} {H}] /Contents 4 0 R "
         f"/Resources << /Font << /F1 5 0 R /F2 6 0 R /F3 7 0 R >> >> >>").encode(),
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>",
        b"<< /Title (Sertifikat SCARLINE) /Producer (SCARLINE) >>",
    ]
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R /Info {len(objects)} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)
