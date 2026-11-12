"""Kalimat SCAR, maskot SCARLINE. Bahasa santai untuk siswa SMP."""
import random

LINES = {
    "welcome": [
        "Halo, Line Explorer! SCAR siap mengajakmu menjelajahi dunia persamaan garis lurus!",
        "Yuk, kita pecahkan misteri koordinat berikutnya!",
        "Hai, Line Explorer! Hari ini kita akan mempelajari rahasia garis lurus!",
    ],
    "correct": [
        "YEAY! Tepat sekali! Kamu berhasil menemukan garis yang benar!",
        "Hebat! Jawabanmu benar!",
        "Mantap! Otak matematikamu sedang panas-panasnya!",
        "Keren! Garis lurus pun tunduk padamu!",
    ],
    "wrong": [
        "Ups! Sepertinya ada sedikit kesalahan. Yuk, kita periksa lagi!",
        "Wah, hampir benar! Coba perhatikan kembali langkahnya.",
        "Tidak apa-apa salah, itu bagian dari belajar. Ayo lihat penjelasanku!",
    ],
    "encourage": [
        "Jangan menyerah! Ingat, gradien menunjukkan seberapa miring suatu garis.",
        "Pelan-pelan saja. Tulis dulu yang diketahui, lalu pilih rumusnya.",
        "Setiap penjelajah hebat pernah tersesat. Ayo coba lagi!",
    ],
    "mission_done": [
        "LUAR BIASA! Kamu berhasil membuka wilayah koordinat baru!",
    ],
    "celebrate": [
        "Selamat! Kamu luar biasa, Line Explorer!",
        "Pesta garis lurus! Kamu berhasil!",
    ],
}


def say(kind: str, rng: random.Random = None) -> str:
    options = LINES.get(kind) or LINES["welcome"]
    return (rng or random).choice(options)
