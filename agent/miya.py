# -*- coding: utf-8 -*-
"""Miya — ekrandan o'qilgan matn va foydalanuvchi so'rovini Claude'ga berib,
tushuntirish/maslahat/qadamlar rejasini oladi.

LLM manbai: foydalanuvchining Claude Pro obunasi orqali Claude Code CLI (`claude -p`).
Qo'shimcha API kalit, to'lov kerak emas. Matn asosida ishlaydi (ekran OCR matni),
shuning uchun rasm API shart emas.
"""
import os, shutil, subprocess, textwrap

TIZIM = (
    "Sen Juratning Windows kompyuteridagi ish yordamchisisan. "
    "U qurilish korxonalarini (TASHKENT STROY BUILD, TOSHKENT LOGISTIK TRANS, TEMUR TEXNIK TRANS, RAYXONA SHIRINA SERVIS) "
    "boshqaradi: buxgalteriya, akt sverka, Didox, bank, Excel reys jadvallari, 1C 8.3, shartnomalar. "
    "Senga ekrandan OCR orqali o'qilgan matn va uning so'rovi beriladi. "
    "QOIDALAR: javob O'ZBEK LOTIN yozuvida, qisqa va amaliy. "
    "Agar xato ko'rsang — aniq qaysi joyda va qanday tuzatishni ayt. "
    "Ishni osonlashtirish bo'yicha aniq taklif ber. "
    "Hech qachon parol, EIMZO yoki maxfiy ma'lumotни so'rama va takrorlama. "
    "Bironta amal (tugma bosish, yozish) kerak bo'lsa — uni bosqichlar ro'yxati qilib taklif qil, "
    "lekin O'ZING bajarma; bajarishdan oldin Jurat tasdiqlaydi."
)


def _claude_exe():
    for c in ("claude", os.path.expandvars(r"%USERPROFILE%\.local\bin\claude.exe"),
              os.path.expandvars(r"%LOCALAPPDATA%\Programs\claude\claude.exe")):
        p = shutil.which(c) if os.path.sep not in c else (c if os.path.exists(c) else None)
        if p:
            return p
    return "claude"


def sora(ocr_matn, sorov, oyna="", kontekst=""):
    """Claude'dan javob oladi. Xato bo'lsa tushunarli matn qaytaradi."""
    prompt = textwrap.dedent(f"""\
        {TIZIM}

        {kontekst}

        Faol oyna: {oyna or "noma'lum"}

        Ekrandan o'qilgan matn (OCR, xatolar bo'lishi mumkin):
        <<<
        {(ocr_matn or '').strip()[:6000]}
        >>>

        Jurat so'rovi: {sorov.strip() or "Ekrandagi ishni ko'rib, xato bor-yo'qligini va qanday osonlashtirishni ayt."}

        Javobni o'zbek lotin yozuvida, qisqa punktlar bilan ber.
    """)
    exe = _claude_exe()
    try:
        r = subprocess.run(
            [exe, "-p", prompt, "--model", "sonnet"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    except FileNotFoundError:
        return "[Claude topilmadi. Claude Code CLI o'rnatilganini tekshiring (claude --version).]"
    except subprocess.TimeoutExpired:
        return "[Claude javob bermadi (vaqt tugadi). Qayta urinib ko'ring.]"
    out = (r.stdout or "").strip()
    if not out and r.returncode != 0:
        return f"[Claude xato: {(r.stderr or '').strip()[-400:]}]"
    return out or "[Bo'sh javob]"


if __name__ == "__main__":
    print(sora("A1 Sana B1 Summa\n01.13.2026 1500000", "xato bormi"))
