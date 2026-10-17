# -*- coding: utf-8 -*-
"""Musiqa yordamchisi (faqat qonuniy yo'llar):

  python musiqa_tool.py havola "Sherali Jo'rayev Bahor"      # YouTube Music / Spotify / Yandex / Apple qidiruv havolalari
  python musiqa_tool.py aniqla audio_yoki_video.mp4 [--dan 0]  # qo'shiq nomini aniqlash (AudD rasmiy API, token kerak)
  python musiqa_tool.py kutubxona [--papka "D:\\Musiqa"]      # kompyuterdagi musiqa papkasini indekslash
  python musiqa_tool.py qidir "jo'rayev bahor" [--max 10]      # o'z kutubxonangizdan fayl topish
  python musiqa_tool.py trend [--mamlakat uz] [--max 20]      # hozir ommabop qo'shiqlar (Apple Music / Deezer rasmiy chartlari)
  python musiqa_tool.py fon video.mp4 [--musiqa fayl.mp3|avto] [--baland 0.18] [--chiqish nom.mp4]
                                                               # videoga fon musiqasi (nutq paytida ovozi pasayadi)

Token: https://dashboard.audd.io dan olingan tokenni ish\\musiqa\\.env fayliga  AUDD_TOKEN=...  qilib yozing
(.env omborga tushmaydi). Fon musiqasi uchun mualliflik huquqisiz treklarni
%USERPROFILE%\\Videos\\montaj\\fon_musiqa papkasiga tashlang (YouTube Audio Library, Pixabay Music).
"""
import argparse, json, os, random, re, shutil, subprocess, sys, tempfile, urllib.parse, urllib.request, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
BAZA = os.path.join(HERE, "musiqa_baza.json")
HOME = os.path.expanduser("~")
FON_PAPKA = os.path.join(HOME, "Videos", "montaj", "fon_musiqa")
AUDIO_EXT = {".mp3", ".m4a", ".flac", ".wav", ".ogg", ".opus", ".aac", ".wma"}


# ---------------- umumiy ----------------
def ffbin(nom):
    p = shutil.which(nom)
    if p: return p
    for d in (os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"), r"C:\ffmpeg\bin", r"C:\Program Files\ffmpeg\bin"):
        q = os.path.join(d, nom + (".exe" if os.name == "nt" else ""))
        if os.path.exists(q): return q
    raise SystemExit(f"{nom} topilmadi. O'rnatish: winget install Gyan.FFmpeg  (keyin PowerShell'ni qayta oching)")


def run(args, cwd=None):
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)
    if r.returncode != 0: raise SystemExit("ffmpeg xato:\n" + r.stderr[-1500:])
    return r


def env_token(nom):
    if os.environ.get(nom): return os.environ[nom].strip()
    p = os.path.join(HERE, ".env")
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8-sig"):
            k, _, v = ln.partition("=")
            if k.strip() == nom and v.strip(): return v.strip().strip('"').strip("'")
    return ""


CYR = dict(zip("абвгдеёжзийклмнопрстуфхцчшъыьэюяўқғҳ",
               ["a", "b", "v", "g", "d", "e", "yo", "j", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "x",
                "ts", "ch", "sh", "", "i", "", "e", "yu", "ya", "o", "q", "g", "h"]))


def norm(t):
    t = (t or "").lower()
    t = "".join(CYR.get(ch, ch) for ch in t)
    t = re.sub(r"[ʻʼ'`‘’ʹ]", "", t)                  # o' / o‘ / o` -> o
    t = t.replace("ye", "e").replace("yo", "o")           # Jo'rayev ~ Жўраев, Yo'ldosh ~ Йўлдош
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


# ---------------- 1) havola ----------------
def cmd_havola(o):
    q = o.nom.strip(); u = urllib.parse.quote(q)
    print(f"«{q}» bo'yicha qidiruv havolalari:")
    print(f"YouTube Music: https://music.youtube.com/search?q={u}")
    print(f"YouTube:       https://www.youtube.com/results?search_query={u}")
    print(f"Spotify:       https://open.spotify.com/search/{u}")
    print(f"Yandex Musiqa: https://music.yandex.ru/search?text={u}")
    print(f"Apple Music:   https://music.apple.com/search?term={u}")


# ---------------- 2) aniqlash (AudD) ----------------
def kesib_ol(src, dan, uzun=15):
    out = os.path.join(tempfile.gettempdir(), f"aniqla_{uuid.uuid4().hex[:8]}.mp3")
    run([ffbin("ffmpeg"), "-y", "-hide_banner", "-ss", str(dan), "-t", str(uzun), "-i", src, "-vn", "-ac", "1", "-ar", "44100", "-b:a", "128k", out])
    return out


def audd_sorov(path, token):
    b = "----jurat" + uuid.uuid4().hex
    parts = []
    for k, v in (("api_token", token), ("return", "spotify,apple_music,deezer")):
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode()
                 + open(path, "rb").read() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request("https://api.audd.io/", data=b"".join(parts), headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read().decode("utf-8"))


def audd_natija(j):
    """AudD javobini o'qiladigan matnga aylantiradi (None = topilmadi)."""
    if j.get("status") != "success":
        e = j.get("error") or {}
        raise SystemExit(f"AudD xato: {e.get('error_message', j)} (kod {e.get('error_code', '?')})")
    r = j.get("result")
    if not r: return None
    qat = [f"🎵 {r.get('artist', '?')} — {r.get('title', '?')}"]
    if r.get("album"): qat.append(f"Albom: {r['album']}" + (f" ({r['release_date'][:4]})" if r.get("release_date") else ""))
    sp = ((r.get("spotify") or {}).get("external_urls") or {}).get("spotify")
    am = (r.get("apple_music") or {}).get("url")
    dz = (r.get("deezer") or {}).get("link")
    for nom, url in (("Spotify", sp), ("Apple Music", am), ("Deezer", dz), ("Boshqa", r.get("song_link"))):
        if url: qat.append(f"{nom}: {url}")
    u = urllib.parse.quote(f"{r.get('artist', '')} {r.get('title', '')}".strip())
    qat.append(f"Yandex Musiqa: https://music.yandex.ru/search?text={u}")
    qat.append(f"YouTube Music: https://music.youtube.com/search?q={u}")
    return "\n".join(qat)


def cmd_aniqla(o):
    token = env_token("AUDD_TOKEN")
    if not token:
        raise SystemExit("AUDD_TOKEN yo'q. https://dashboard.audd.io dan token oling va ish\\musiqa\\.env fayliga  AUDD_TOKEN=...  deb yozing.")
    src = os.path.abspath(o.fayl)
    if not os.path.exists(src): raise SystemExit(f"Fayl topilmadi: {src}")
    for dan in ([o.dan] if o.dan is not None else [0, 30, 60]):     # boshida jimlik/gap bo'lsa — keyingi bo'lakni sinaymiz
        try: clip = kesib_ol(src, dan)
        except SystemExit:
            continue
        try: txt = audd_natija(audd_sorov(clip, token))
        finally: os.unlink(clip)
        if txt:
            print(txt); return
    print("Topilmadi. Qo'shiq aniq eshitiladigan joyni yuboring yoki --dan <soniya> bilan boshqa joydan sinang.")


# ---------------- 3) kutubxona ----------------
def teglar(p):
    try:
        from mutagen import File
        m = File(p, easy=True)
        if m and m.tags:
            g = lambda k: (m.tags.get(k) or [""])[0]
            return g("artist"), g("title"), g("album")
    except Exception:
        pass
    return "", "", ""


def cmd_kutubxona(o):
    papkalar = o.papka or [os.path.join(HOME, "Music"), os.path.join(HOME, "Downloads")]
    old = json.load(open(BAZA, encoding="utf-8")) if os.path.exists(BAZA) else {"papkalar": [], "fayllar": []}
    papkalar = list(dict.fromkeys([os.path.abspath(p) for p in old.get("papkalar", []) + papkalar if os.path.isdir(p)]))
    fl = []
    for root in papkalar:
        for d, _, fs in os.walk(root):
            for f in fs:
                if os.path.splitext(f)[1].lower() in AUDIO_EXT:
                    p = os.path.join(d, f); a, t, al = teglar(p)
                    fl.append({"yol": p, "artist": a, "title": t, "album": al, "mb": round(os.path.getsize(p) / 1048576, 1)})
    json.dump({"papkalar": papkalar, "fayllar": fl}, open(BAZA, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"Kutubxona: {len(fl)} ta qo'shiq | papkalar: {'; '.join(papkalar) or 'YOQ'}")


def cmd_qidir(o):
    if not os.path.exists(BAZA): raise SystemExit("Avval: python musiqa_tool.py kutubxona")
    fl = json.load(open(BAZA, encoding="utf-8"))["fayllar"]
    sozlar = norm(o.soz).split()
    if not sozlar: raise SystemExit("Qidiruv so'zi bo'sh")
    nat = []
    for x in fl:
        matn = norm(" ".join([x["artist"], x["title"], x["album"], os.path.splitext(os.path.basename(x["yol"]))[0]]))
        tok = set(matn.split())
        bal = sum(2 if s in tok else (1 if s in matn else 0) for s in sozlar)
        if all(s in matn for s in sozlar): bal += 5
        if bal: nat.append((bal, x))
    nat.sort(key=lambda z: (-z[0], z[1]["yol"]))
    if not nat:
        print("Kutubxonada topilmadi."); return
    for bal, x in nat[:o.max]:
        nom = f"{x['artist']} — {x['title']}" if x["title"] else os.path.basename(x["yol"])
        print(f"{x['yol']} | {nom} | {x['mb']} MB" + (" | 50 MB dan katta — Telegram'ga sig'maydi" if x["mb"] > 49 else ""))


# ---------------- 4) fon musiqasi ----------------
def davomiylik(p, fp):
    r = run([fp, "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", p])
    j = json.loads(r.stdout)
    return float(j["format"]["duration"]), any(s["codec_type"] == "audio" for s in j["streams"])


def cmd_fon(o):
    ff, fp = ffbin("ffmpeg"), ffbin("ffprobe")
    src = os.path.abspath(o.video)
    if o.musiqa in (None, "avto"):
        tr = [os.path.join(FON_PAPKA, f) for f in (os.listdir(FON_PAPKA) if os.path.isdir(FON_PAPKA) else [])
              if os.path.splitext(f)[1].lower() in AUDIO_EXT]
        if not tr: raise SystemExit(f"Fon musiqasi yo'q. Mualliflik huquqisiz treklarni shu papkaga tashlang: {FON_PAPKA}")
        mus = random.choice(tr)
    else:
        mus = os.path.abspath(o.musiqa)
    dur, ovoz = davomiylik(src, fp)
    out = os.path.abspath(o.chiqish) if o.chiqish else os.path.splitext(src)[0] + "_fon.mp4"
    fade = min(1.5, dur / 4)
    m = (f"[1:a]aloop=loop=-1:size=2e9,atrim=0:{dur:.3f},asetpts=N/SR/TB,volume={o.baland},"
         f"afade=t=in:d={fade:.2f},afade=t=out:st={max(0, dur - fade):.3f}:d={fade:.2f}[m]")
    if ovoz:   # nutq bor: nutq paytida musiqa pasayadi (sidechain), keyin aralashtiriladi
        fc = (m + ";[0:a]asplit=2[v][sc];[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];"
              "[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.0:LRA=11[a]")
    else:      # videoda ovoz yo'q: faqat musiqa
        fc = m.replace(f"volume={o.baland}", "volume=1.0") + ";[m]loudnorm=I=-14:TP=-1.0:LRA=11[a]"
    run([ff, "-y", "-hide_banner", "-i", src, "-i", mus, "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out])
    print(out)
    print(f"Fon: {os.path.basename(mus)} | video {dur:.1f} s | {'nutq ustiga past ovozda' if ovoz else 'videoda ovoz yoq — faqat musiqa'}")


# ---------------- 5) trend (rasmiy ochiq chartlar, kalitsiz) ----------------
def json_ol(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read().decode("utf-8"))


def apple_chart(cc, n):
    j = json_ol(f"https://rss.applemarketingtools.com/api/v2/{cc}/music/most-played/{n}/songs.json")
    return [(x.get("artistName", "?"), x.get("name", "?"), x.get("url", "")) for x in (j.get("feed") or {}).get("results", [])]


def deezer_chart(n):
    j = json_ol(f"https://api.deezer.com/chart/0/tracks?limit={n}")
    return [((x.get("artist") or {}).get("name", "?"), x.get("title", "?"), x.get("link", "")) for x in j.get("data", [])]


def cmd_trend(o):
    MN = {"uz": "O'zbekiston", "ru": "Rossiya", "kz": "Qozog'iston", "tr": "Turkiya", "us": "AQSh"}
    royxat, manba = [], ""
    for cc in dict.fromkeys([o.mamlakat.lower(), "ru", "us"]):
        try:
            royxat = apple_chart(cc, o.max)
            if royxat: manba = f"Apple Music — {MN.get(cc, cc.upper())} top {len(royxat)}"; break
        except Exception:
            continue
    if o.dunyo or not royxat:
        try:
            d = deezer_chart(o.max)
            if d and not royxat: royxat, manba = d, f"Deezer — dunyo top {len(d)}"
            elif d: royxat += [None] + d; manba += f" + Deezer dunyo top {len(d)}"
        except Exception:
            pass
    if not royxat: raise SystemExit("Chartlarni olib bo'lmadi (internet?). Keyinroq urinib ko'ring.")
    print(f"🔥 {manba}:")
    k = 0
    for x in royxat:
        if x is None:
            print("— Deezer (dunyo) —"); k = 0; continue
        k += 1; a, t, url = x
        yt = "https://music.youtube.com/search?q=" + urllib.parse.quote(f"{a} {t}")
        print(f"{k}. {a} — {t}\n   {url or yt}" + (f"\n   YouTube Music: {yt}" if url else ""))


def main():
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("havola"); a.add_argument("nom")
    a = sp.add_parser("aniqla"); a.add_argument("fayl"); a.add_argument("--dan", type=float)
    a = sp.add_parser("kutubxona"); a.add_argument("--papka", action="append")
    a = sp.add_parser("qidir"); a.add_argument("soz"); a.add_argument("--max", type=int, default=10)
    a = sp.add_parser("trend"); a.add_argument("--mamlakat", default="uz"); a.add_argument("--max", type=int, default=20)
    a.add_argument("--dunyo", action="store_true")
    a = sp.add_parser("fon"); a.add_argument("video"); a.add_argument("--musiqa"); a.add_argument("--baland", type=float, default=0.18)
    a.add_argument("--chiqish")
    o = ap.parse_args()
    {"havola": cmd_havola, "aniqla": cmd_aniqla, "kutubxona": cmd_kutubxona, "qidir": cmd_qidir, "trend": cmd_trend, "fon": cmd_fon}[o.cmd](o)


if __name__ == "__main__":
    main()
