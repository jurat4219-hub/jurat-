# -*- coding: utf-8 -*-
"""Ko'p zapravka videosini BIRDANIGA tayyorlash (parallel, LLMsiz):
har video uchun bitta rasm <video>_kadr.jpg = [oxirgi kadr | 1.5 s oldingi kadr] yonma-yon (kolonka displeyi uchun).
Agentlar videoni emas, shu rasmni ochadi -> tez va limit tejaladi.

  python navbat.py kadr video1.mp4 video2.mp4 ...        # yoki papka: python navbat.py kadr ish\\zapravka\\video\\2026-10-21
  python navbat.py kadr --oqim 10 *.mp4                  # bir vaqtda nechta ffmpeg (default 6)
Chiqish: har qatorda  OK|<video>|<kadr.jpg>|<davomiylik s>   yoki   XATO|<video>|<sabab>
"""
import argparse, concurrent.futures as cf, glob, json, os, shutil, subprocess, sys

VID = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".3gp", ".webm"}


def ffbin(nom):
    p = shutil.which(nom)
    if p: return p
    for d in (os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"), r"C:\ffmpeg\bin", r"C:\Program Files\ffmpeg\bin"):
        q = os.path.join(d, nom + (".exe" if os.name == "nt" else ""))
        if os.path.exists(q): return q
    raise SystemExit(f"{nom} topilmadi: winget install Gyan.FFmpeg")


FF, FP = ffbin("ffmpeg"), ffbin("ffprobe")


def davom(v):
    r = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "json", v], capture_output=True, text=True)
    try: return float(json.loads(r.stdout)["format"]["duration"])
    except Exception: return 0.0


def kadr_vaqt(v, t, w=760):
    """v videodan t soniyadagi bitta kadr -> vaqtincha jpg yo'li (yoki None)."""
    out = os.path.splitext(v)[0] + f"_t{int(t*10):04d}.jpg"
    r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{max(0,t):.2f}", "-i", v,
                        "-frames:v", "1", "-vf", f"scale={w}:-2", "-q:v", "3", out], capture_output=True, text=True)
    return out if r.returncode == 0 and os.path.exists(out) else None


def bitta(v):
    if not os.path.exists(v): return f"XATO|{v}|fayl yo'q"
    d = davom(v)
    if d <= 0: return f"XATO|{v}|video o'qilmadi (buzuq yoki rasm emas)"
    out = os.path.splitext(v)[0] + "_kadr.jpg"
    # Zapravkada DAVLAT RAQAMI odatda boshi/o'rtasida (mashina kelganda), KUB oxirida (displey to'xtaganda)
    # ko'rinadi. Shuning uchun bir nechta vaqtdan kadr olib, 2 qatorli montaj qilamiz: raqam ham, kub ham tushsin.
    ts = sorted(set([max(0, d*0.12), max(0, d*0.40), max(0, d*0.68), max(0, d-1.5), max(0, d-0.25)]))
    frames = [f for f in (kadr_vaqt(v, t) for t in ts) if f]
    if not frames:
        r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-sseof", "-0.5", "-i", v,
                            "-frames:v", "1", "-vf", "scale=900:-2", "-q:v", "3", out], capture_output=True, text=True)
        return f"OK|{v}|{out}|{d:.1f}" if r.returncode == 0 else f"XATO|{v}|{r.stderr.strip()[-200:]}"
    ok = montaj(frames, out)
    for f in frames:
        try: os.remove(f)
        except OSError: pass
    if not ok:
        r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-sseof", "-0.5", "-i", v,
                            "-frames:v", "1", "-vf", "scale=900:-2", "-q:v", "3", out], capture_output=True, text=True)
        if r.returncode != 0: return f"XATO|{v}|montaj/kadr xato"
    return f"OK|{v}|{out}|{d:.1f}"


def montaj(frames, out, cols=2):
    """Kadrlarni PIL bilan to'r qilib bitta jpg ga joylaydi (ustunlar teng kenglikda)."""
    try:
        from PIL import Image
    except ImportError:
        return False
    try:
        ims = [Image.open(f).convert("RGB") for f in frames]
    except Exception:
        return False
    if not ims: return False
    cw = max(im.width for im in ims)
    import math
    rows = math.ceil(len(ims) / cols)
    cell = [[None] * cols for _ in range(rows)]
    for i, im in enumerate(ims):
        if im.width != cw: im = im.resize((cw, round(im.height * cw / im.width)))
        cell[i // cols][i % cols] = im
    rowh = [max((im.height for im in r if im), default=0) for r in cell]
    W, H, pad = cw * cols + (cols + 1) * 8, sum(rowh) + (rows + 1) * 8, 8
    canvas = Image.new("RGB", (W, H), (20, 20, 20))
    y = pad
    for ri, r in enumerate(cell):
        x = pad
        for im in r:
            if im: canvas.paste(im, (x, y))
            x += cw + pad
        y += rowh[ri] + pad
    canvas.save(out, "JPEG", quality=85)
    return True


def cmd_kadr(o):
    fl = []
    for x in o.fayllar:
        if os.path.isdir(x): fl += sorted(os.path.join(x, f) for f in os.listdir(x) if os.path.splitext(f)[1].lower() in VID)
        else: fl += sorted(glob.glob(x)) or [x]
    fl = [os.path.abspath(f) for f in dict.fromkeys(fl) if not f.endswith("_kadr.jpg")]
    if not fl: raise SystemExit("Video topilmadi")
    with cf.ThreadPoolExecutor(max_workers=max(1, o.oqim)) as ex:
        nat = list(ex.map(bitta, fl))
    for n in nat: print(n)
    ok = sum(n.startswith("OK") for n in nat)
    print(f"JAMI: {len(fl)} video | tayyor {ok} | xato {len(fl) - ok}")


def main():
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    k = sp.add_parser("kadr"); k.add_argument("fayllar", nargs="+"); k.add_argument("--oqim", type=int, default=6)
    o = ap.parse_args(); cmd_kadr(o)


if __name__ == "__main__":
    main()
