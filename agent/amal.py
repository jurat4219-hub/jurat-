# -*- coding: utf-8 -*-
"""Amal — sichqoncha va klaviatura bilan ish bajarish.
XAVFSIZLIK: har bir amal faqat Jurat TASDIQLAGANDAN keyin bajariladi.
MVP'da bu modul O'CHIQ turadi (YOQILGAN=False). 2-bosqichda yoqamiz.
"""
YOQILGAN = False  # MVP: amal bajarilmaydi, faqat taklif qilinadi


def mavjudmi():
    try:
        import pyautogui  # noqa
        return True
    except Exception:
        return False


def bajar(amal, tasdiq_fn):
    """amal = {'tur':'yoz'|'bos'|'kop','matn':..,'x':..,'y':..}. tasdiq_fn(matn)->bool.
    YOQILGAN=False bo'lsa — hech narsa qilmaydi, faqat 'o'chiq' deb qaytaradi."""
    if not YOQILGAN:
        return "O'CHIQ: amal bajarilmadi (xavfsizlik uchun MVP'da amal bajarish o'chirilgan)."
    if not mavjudmi():
        return "pyautogui yo'q — amal bajarib bo'lmaydi."
    tavsif = _tavsif(amal)
    if not tasdiq_fn(tavsif):
        return f"Bekor qilindi: {tavsif}"
    import pyautogui
    pyautogui.FAILSAFE = True  # sichqonchani burchakka olib borish = to'xtatadi
    t = amal.get("tur")
    if t == "yoz":
        pyautogui.typewrite(amal.get("matn", ""), interval=0.02)
    elif t == "bos":
        pyautogui.click(amal.get("x"), amal.get("y"))
    elif t == "klavish":
        pyautogui.press(amal.get("matn", "enter"))
    else:
        return f"Noma'lum amal: {t}"
    return f"Bajarildi: {tavsif}"


def _tavsif(amal):
    t = amal.get("tur")
    if t == "yoz":
        return f"Matn yozish: «{amal.get('matn','')[:60]}»"
    if t == "bos":
        return f"Sichqoncha bosish: ({amal.get('x')},{amal.get('y')})"
    if t == "klavish":
        return f"Klavish: {amal.get('matn')}"
    return str(amal)
