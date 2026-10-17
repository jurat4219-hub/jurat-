# -*- coding: utf-8 -*-
"""Rasm (JPG/PNG/HEIC) -> sifatli skaner PDF.
Hujjat chetini topadi, qiyshiqni to'g'rilaydi, soya/sariqlikni oladi, A4 ga joylaydi.

Ishlatish:
  python skan_tool.py pdf rasm1.jpg [rasm2.jpg ...] [--rejim skan|rang|asl] [--chiqish nom.pdf] [--kesma yoq]
  rejim: skan = oq-qora skaner ko'rinishi (default, hujjat/TTN/faktura uchun)
         rang = rangli, lekin fon oqartirilgan (muhr/imzo rangli qolsin desa)
         asl  = faqat to'g'rilash va A4, rang o'zgarmaydi (foto uchun)
Bir nechta rasm = bitta ko'p sahifali PDF (berilgan tartibda).
"""
import argparse, os, sys, io, datetime
import numpy as np
import cv2
from PIL import Image, ImageOps

A4 = (2480, 3508)  # 300 dpi


def yukla(path):
    try:
        im = Image.open(path)
    except Exception:
        try:
            import pillow_heif; pillow_heif.register_heif_opener(); im = Image.open(path)
        except Exception:
            raise SystemExit(f"Rasm ochilmadi: {path}")
    im = ImageOps.exif_transpose(im).convert("RGB")
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)


def tartib(p):
    p = p.reshape(4, 2).astype("float32"); s = p.sum(1); d = np.diff(p, axis=1).ravel()
    return np.array([p[np.argmin(s)], p[np.argmin(d)], p[np.argmax(s)], p[np.argmax(d)]], dtype="float32")


def hujjat_kesish(img):
    h, w = img.shape[:2]; k = 1000.0 / max(h, w); sm = cv2.resize(img, (int(w * k), int(h * k)))
    g = cv2.GaussianBlur(cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    best = None
    for lo, hi in ((50, 150), (30, 100), (75, 200)):
        e = cv2.dilate(cv2.Canny(g, lo, hi), np.ones((3, 3), np.uint8), iterations=2)
        cs, _ = cv2.findContours(e, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in sorted(cs, key=cv2.contourArea, reverse=True)[:8]:
            a = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
            if len(a) == 4 and cv2.isContourConvex(a) and cv2.contourArea(a) > 0.25 * sm.shape[0] * sm.shape[1]:
                best = a; break
        if best is not None: break
    if best is None: return img, False
    p = tartib(best) / k
    wA = max(np.linalg.norm(p[2] - p[3]), np.linalg.norm(p[1] - p[0])); hA = max(np.linalg.norm(p[1] - p[2]), np.linalg.norm(p[0] - p[3]))
    # perspektiva bo'yini qisqartiradi: A4 ga yaqin varaqni aniq A4 nisbatga keltiramiz
    r = max(wA, hA) / min(wA, hA)
    if 1.12 < r < 1.7:
        if hA >= wA: hA = wA * 1.4142
        else: wA = hA * 1.4142
    dst = np.array([[0, 0], [wA - 1, 0], [wA - 1, hA - 1], [0, hA - 1]], dtype="float32")
    return cv2.warpPerspective(img, cv2.getPerspectiveTransform(p, dst), (int(wA), int(hA)), flags=cv2.INTER_CUBIC), True


def qiyshiq(img):
    """Matn qatorlari bo'yicha mayda burilishni (±10°) to'g'rilaydi."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    b = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    ls = cv2.HoughLinesP(b, 1, np.pi / 720, 200, minLineLength=img.shape[1] // 4, maxLineGap=20)
    if ls is None: return img
    ang = [np.degrees(np.arctan2(y2 - y1, x2 - x1)) for x1, y1, x2, y2 in np.asarray(ls).reshape(-1, 4)]
    ang = [a for a in ang if abs(a) < 10]
    if len(ang) < 5: return img
    a = float(np.median(ang))
    if abs(a) < 0.15: return img
    h, w = img.shape[:2]; M = cv2.getRotationMatrix2D((w / 2, h / 2), a, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def fon_tekisla(ch):
    """Soya va notekis yorug'likni olib tashlaydi (fon oq bo'ladi)."""
    k = max(31, (min(ch.shape[:2]) // 20) | 1)
    bg = cv2.medianBlur(cv2.dilate(ch, np.ones((9, 9), np.uint8)), k)
    out = cv2.divide(ch, bg, scale=255)
    return out


def keskin(g, sigma=1.4, kuch=1.2):
    """Unsharp mask: harf chetlarini tiniqlashtiradi."""
    bl = cv2.GaussianBlur(g, (0, 0), sigma)
    return cv2.addWeighted(g, 1 + kuch, bl, -kuch, 0)


def kontrast(g, past, yuqori, gamma=1.0):
    x = np.clip((np.arange(256) - past) / float(yuqori - past), 0, 1) ** gamma
    return cv2.LUT(g, (x * 255).astype(np.uint8))


def yaxshila(img, rejim):
    if rejim == "asl":
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB); L, A, B = cv2.split(lab)
        L = keskin(L, 1.2, 0.6)
        return cv2.cvtColor(cv2.merge([L, A, B]), cv2.COLOR_LAB2BGR)
    if rejim == "rang":
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB); L, A, B = cv2.split(lab)
        L = fon_tekisla(L); L = cv2.fastNlMeansDenoising(L, None, 4, 7, 21)
        L = keskin(kontrast(L, 70, 230, 1.35), 1.3, 1.0)
        # rang to'yinganligini oshirish (muhr/imzo yorqinroq), fon oq qolsin
        A = cv2.addWeighted(A, 1.35, np.full_like(A, 128), -0.35, 0)
        B = cv2.addWeighted(B, 1.35, np.full_like(B, 128), -0.35, 0)
        out = cv2.cvtColor(cv2.merge([L, A, B]), cv2.COLOR_LAB2BGR)
        oq = L > 235; out[oq] = 255
        return out
    g = fon_tekisla(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    g = cv2.fastNlMeansDenoising(g, None, 5, 7, 21)
    g = kontrast(g, 80, 225, 1.5)          # matn to'q qora, fon toza oq
    g = keskin(g, 1.4, 1.3)
    g[g > 238] = 255
    return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)


def a4_olcham(img):
    """Hujjatni AVVAL A4 300dpi o'lchamga keltiradi (kichik rasm kattalashtiriladi), keyin yaxshilanadi."""
    h, w = img.shape[:2]
    W, H = (A4[1], A4[0]) if w > h else A4
    m = int(0.03 * W); s = min((W - 2 * m) / w, (H - 2 * m) / h)
    return cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LANCZOS4), (W, H)


def a4_sahifa(img, WH):
    W, H = WH; nh, nw = img.shape[:2]
    page = np.full((H, W, 3), 255, np.uint8); y, x = (H - nh) // 2, (W - nw) // 2
    page[y:y + nh, x:x + nw] = img
    return page


def cmd_pdf(o):
    import img2pdf
    sahifalar = []; hisob = []
    for p in o.rasmlar:
        img = yukla(p); kesildi = False
        if o.kesma != "yoq": img, kesildi = hujjat_kesish(img)
        img = qiyshiq(img)
        img, WH = a4_olcham(img)
        img = a4_sahifa(yaxshila(img, o.rejim), WH)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb).convert("L") if o.rejim == "skan" else Image.fromarray(rgb)
        buf = io.BytesIO(); pil.save(buf, "JPEG", quality=93, dpi=(300, 300), optimize=True)
        sahifalar.append(buf.getvalue()); hisob.append(f"{os.path.basename(p)}: {'chet topildi, kesildi' if kesildi else 'chet topilmadi, butun rasm'}")
    out = o.chiqish or os.path.join(os.path.dirname(os.path.abspath(o.rasmlar[0])),
                                    f"Skan_{datetime.datetime.now():%Y%m%d_%H%M%S}.pdf")
    with open(out, "wb") as f:
        f.write(img2pdf.convert(sahifalar, layout_fun=img2pdf.get_fixed_dpi_layout_fun((300, 300))))
    print(out)
    print(f"Sahifalar: {len(sahifalar)} | rejim: {o.rejim} | hajm: {os.path.getsize(out) / 1024:.0f} KB")
    for h in hisob: print("  " + h)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("pdf"); p.add_argument("rasmlar", nargs="+")
    p.add_argument("--rejim", choices=["skan", "rang", "asl"], default="skan")
    p.add_argument("--chiqish"); p.add_argument("--kesma", choices=["ha", "yoq"], default="ha")
    o = ap.parse_args()
    if o.cmd == "pdf": cmd_pdf(o)


if __name__ == "__main__":
    main()
