# -*- coding: utf-8 -*-
"""Video avto-montaj: pauza/sukutlarni kesadi, ovozni -14 LUFS ga keltiradi, Reels (9:16) qiladi, subtitr qo'yadi.

Ishlatish:
  python video_tool.py montaj video.mp4 [--format asl|reels] [--subtitr ha|yoq] [--til uz|ru|auto]
                                  [--sukut 0.40] [--porog -35] [--chiqish nom.mp4]
  python video_tool.py tekshir video.mp4      # davomiylik, o'lcham, fps, LUFS

  --sukut  : shundan uzun jimlik kesiladi (soniya, default 0.40)
  --porog  : jimlik chegarasi dB (default -35; shovqinli joyda -30)
  --format : reels = 1080x1920 vertikal (Instagram/TikTok/Shorts), asl = o'lcham o'zgarmaydi
  --subtitr: ha = nutqni matnga aylantirib (faster-whisper) videoga yozadi
Natija: <nom>_montaj.mp4 + <nom>_montaj.srt (subtitr bo'lsa) + qisqa hisobot.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile


def ffbin(nom):
    p = shutil.which(nom)
    if p: return p
    for d in (os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"), r"C:\ffmpeg\bin", r"C:\Program Files\ffmpeg\bin"):
        q = os.path.join(d, nom + (".exe" if os.name == "nt" else ""))
        if os.path.exists(q): return q
    raise SystemExit(f"{nom} topilmadi. O'rnatish: winget install Gyan.FFmpeg  (keyin PowerShell'ni qayta oching)")


FF, FP = None, None


def run(args, cwd=None):
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)
    if r.returncode != 0: raise SystemExit("ffmpeg xato:\n" + r.stderr[-1500:])
    return r


def info(path):
    r = run([FP, "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate", "-of", "json", path])
    j = json.loads(r.stdout); v = next((s for s in j["streams"] if s["codec_type"] == "video"), {})
    a = any(s["codec_type"] == "audio" for s in j["streams"])
    fps = v.get("r_frame_rate", "30/1"); n, d = fps.split("/"); fps = round(float(n) / float(d or 1), 2)
    return float(j["format"]["duration"]), v.get("width"), v.get("height"), fps, a


def lufs(path):
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    s = r.stderr[r.stderr.rfind("Summary"):]
    I = re.search(r"I:\s+(-?[\d.]+) LUFS", s); P = re.search(r"Peak:\s+(-?[\d.]+) dBFS", s)
    return (float(I.group(1)) if I else None), (float(P.group(1)) if P else None)


def nutq_qismlari(path, dur, porog, sukut, pad=0.12, minseg=0.25):
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", path, "-af", f"silencedetect=noise={porog}dB:d={sukut}", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", r.stderr)]
    if len(en) < len(st): en.append(dur)
    seg, cur = [], 0.0
    for s, e in zip(st, en):
        a, b = cur, min(dur, s + pad)
        if b - a >= minseg: seg.append([max(0, a), b])
        cur = max(0, e - pad)
    if dur - cur >= minseg: seg.append([cur, dur])
    # bir-biriga tegib turganlarini birlashtirish
    out = []
    for a, b in seg:
        if out and a <= out[-1][1] + 0.05: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out


def kesish(src, dst, seg, reels, w, h):
    sel = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in seg)
    vf = f"select='{sel}',setpts=N/FRAME_RATE/TB"
    if reels:
        vf += ",crop='min(iw,ih*9/16)':'min(ih,iw*16/9)',scale=1080:1920:flags=lanczos,setsar=1"
    af = f"aselect='{sel}',asetpts=N/SR/TB"
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(f"[0:v]{vf}[v];[0:a]{af}[a]"); fs = f.name
    try:
        run([FF, "-y", "-hide_banner", "-i", src, "-filter_complex_script", fs, "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", dst])
    finally:
        os.unlink(fs)


def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def subtitr_yasa(video, srt, til, reels):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise SystemExit("Subtitr uchun: python -m pip install faster-whisper  (birinchi ishlatishda model ~1.5 GB yuklanadi)")
    model = WhisperModel(os.environ.get("WHISPER_MODEL", "medium"), device="auto", compute_type="int8")
    segs, inf = model.transcribe(video, language=None if til == "auto" else til, word_timestamps=True, vad_filter=True)
    words = [w for s in segs for w in (s.words or [])]
    n = 3 if reels else 7
    lines, i = [], 0
    while i < len(words):
        grp = words[i:i + n]; i += n
        txt = "".join(w.word for w in grp).strip()
        if txt: lines.append((grp[0].start, grp[-1].end, txt))
    with open(srt, "w", encoding="utf-8") as f:
        for k, (a, b, t) in enumerate(lines, 1):
            f.write(f"{k}\n{ts(a)} --> {ts(max(b, a + 0.3))}\n{t}\n\n")
    return len(lines), inf.language


def cmd_montaj(o):
    src = os.path.abspath(o.video); dur, w, h, fps, has_a = info(src)
    if not has_a: raise SystemExit("Videoda ovoz yo'q — pauzalarni ovoz bo'yicha topib bo'lmaydi.")
    base = os.path.splitext(src)[0]
    out = os.path.abspath(o.chiqish) if o.chiqish else base + ("_reels" if o.format == "reels" else "") + "_montaj.mp4"
    seg = nutq_qismlari(src, dur, o.porog, o.sukut)
    if not seg: raise SystemExit("Nutq topilmadi (porog juda past?). --porog -30 bilan urinib ko'ring.")
    tmp = out + ".kesilgan.mp4"
    kesish(src, tmp, seg, o.format == "reels", w, h)
    srt_info = ""
    vf = []
    if o.subtitr == "ha":
        srt = os.path.splitext(out)[0] + ".srt"
        n, lang = subtitr_yasa(tmp, srt, o.til, o.format == "reels")
        st = ("FontName=Arial,FontSize=13,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=0,Alignment=2,MarginV=70"
              if o.format == "reels" else
              "FontName=Arial,FontSize=20,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=30")
        vf = ["-vf", f"subtitles={os.path.basename(srt)}:force_style='{st}'"]
        srt_info = f" | subtitr: {n} qator ({lang}) -> {os.path.basename(srt)}"
    run([FF, "-y", "-hide_banner", "-i", os.path.basename(tmp)] + vf +
        (["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"] if vf else ["-c:v", "copy"]) +
        ["-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", os.path.basename(out)], cwd=os.path.dirname(out))
    os.unlink(tmp)
    d2, w2, h2, f2, _ = info(out); I, P = lufs(out)
    print(out)
    print(f"Asl: {dur:.1f} s -> montaj: {d2:.1f} s (kesildi {dur - d2:.1f} s, {len(seg)} bo'lak) | {w2}x{h2} @ {f2} fps | "
          f"ovoz: {I} LUFS, pik {P} dBFS{srt_info}")


def cmd_tekshir(o):
    d, w, h, f, a = info(o.video); I, P = lufs(o.video) if a else (None, None)
    print(f"{os.path.basename(o.video)}: {d:.1f} s | {w}x{h} @ {f} fps | ovoz: {'bor' if a else 'yoq'} | {I} LUFS, pik {P} dBFS")


def main():
    global FF, FP
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("montaj"); m.add_argument("video")
    m.add_argument("--format", choices=["asl", "reels"], default="asl")
    m.add_argument("--subtitr", choices=["ha", "yoq"], default="yoq")
    m.add_argument("--til", default="auto"); m.add_argument("--sukut", type=float, default=0.40)
    m.add_argument("--porog", type=float, default=-35); m.add_argument("--chiqish")
    t = sp.add_parser("tekshir"); t.add_argument("video")
    o = ap.parse_args(); FF, FP = ffbin("ffmpeg"), ffbin("ffprobe")
    {"montaj": cmd_montaj, "tekshir": cmd_tekshir}[o.cmd](o)


if __name__ == "__main__":
    main()
