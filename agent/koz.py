# -*- coding: utf-8 -*-
"""Ko'z — ekranni suratga olish va OCR bilan matnga aylantirish.
Faqat foydalanuvchi so'raganda ishlaydi (doimiy kuzatuv YO'Q).

- surat(): butun ekran yoki faol oynaning suratini oladi -> PIL.Image
- matn(img): OCR orqali matn chiqaradi (Tesseract)
- faol_oyna_nomi(): hozirgi faol oyna sarlavhasi (qaysi dastur ochiq)
"""
import os, io, time

HERE = os.path.dirname(os.path.abspath(__file__))
SURATLAR = os.path.join(HERE, "suratlar")
os.makedirs(SURATLAR, exist_ok=True)


def _mss():
    import mss
    return mss.mss()


def surat(faqat_faol=False):
    """Ekran suratini oladi. faqat_faol=True bo'lsa faqat faol oynani qirqadi (Windows)."""
    from PIL import Image
    with _mss() as sct:
        mon = sct.monitors[1]
        if faqat_faol:
            r = faol_oyna_rect()
            if r:
                mon = {"left": r[0], "top": r[1], "width": r[2] - r[0], "height": r[3] - r[1]}
        raw = sct.grab(mon)
        img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
    return img


def saqla(img, nom=None):
    nom = nom or time.strftime("ekran_%Y%m%d_%H%M%S.png")
    p = os.path.join(SURATLAR, nom)
    img.save(p)
    return p


def matn(img):
    """OCR -> matn. Tesseract o'rnatilmagan bo'lsa tushunarli xato qaytaradi."""
    try:
        import pytesseract
    except ImportError:
        return "[OCR yo'q: pip install pytesseract]"
    exe = os.environ.get("TESSERACT_EXE") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(exe):
        pytesseract.pytesseract.tesseract_cmd = exe
    try:
        # rus + ingliz: 1C, Didox, Excel ko'pincha rus/lotin aralash
        return pytesseract.image_to_string(img, lang="rus+eng")
    except Exception as e:
        try:
            return pytesseract.image_to_string(img)
        except Exception as e2:
            return f"[OCR xato: {e2}]"


def faol_oyna_nomi():
    """Windows: faol oyna sarlavhasi. Boshqa OS yoki xato: bo'sh."""
    try:
        import ctypes
        u = ctypes.windll.user32
        h = u.GetForegroundWindow()
        n = u.GetWindowTextLengthW(h)
        buf = ctypes.create_unicode_buffer(n + 1)
        u.GetWindowTextW(h, buf, n + 1)
        return buf.value
    except Exception:
        return ""


def faol_oyna_rect():
    try:
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32
        h = u.GetForegroundWindow()
        r = wintypes.RECT()
        u.GetWindowRect(h, ctypes.byref(r))
        return (r.left, r.top, r.right, r.bottom)
    except Exception:
        return None


if __name__ == "__main__":
    img = surat()
    print("Surat:", img.size, "faol oyna:", faol_oyna_nomi())
    print(matn(img)[:300])
