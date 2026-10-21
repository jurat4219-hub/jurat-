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


def bitta(v):
    if not os.path.exists(v): return f"XATO|{v}|fayl yo'q"
    d = davom(v)
    if d <= 0: return f"XATO|{v}|video o'qilmadi (buzuq yoki rasm emas)"
    out = os.path.splitext(v)[0] + "_kadr.jpg"
    t1, t2 = max(0, d - 0.3), max(0, d - 1.8)          # yakuniy qiymat + biroz oldin (displey to'xtaganini solishtirish uchun)
    fc = "[0:v]scale=900:-2,setsar=1[a];[1:v]scale=900:-2,setsar=1[b];[a][b]hstack=inputs=2"
    r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t1:.2f}", "-i", v, "-ss", f"{t2:.2f}", "-i", v,
                        "-filter_complex", fc, "-frames:v", "1", "-q:v", "3", out], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-sseof", "-0.5", "-i", v, "-frames:v", "1",
                            "-vf", "scale=900:-2", "-q:v", "3", out], capture_output=True, text=True)   # qisqa video: faqat oxirgi kadr
        if r.returncode != 0: return f"XATO|{v}|{r.stderr.strip()[-200:]}"
    return f"OK|{v}|{out}|{d:.1f}"


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
