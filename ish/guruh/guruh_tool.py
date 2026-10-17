# -*- coding: utf-8 -*-
"""Telegram guruh xabarlarini jurnalga yozish va qisqa ko'rinishda chiqarish (limit tejash uchun).

  python guruh_tool.py yoz --guruh "<nom yoki id>" --kim "<ism>" --matn "<matn>" [--fayl "<yo'l>"] [--vaqt "2026-10-17 19:50"]
  python guruh_tool.py oxirgi --guruh "<nom>" [--soat 24] [--qidir "so'z"] [--max 200]
  python guruh_tool.py royxat                 # qaysi guruhlar, nechta xabar, oxirgi vaqt
  python guruh_tool.py fayllar --guruh "<nom>" [--soat 72]
Jurnal: guruh_jurnal/<guruh>.jsonl (shu papkada). Fayllar: guruh_fayllar/<guruh>/
"""
import argparse, datetime, json, os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
JUR = os.path.join(HERE, "guruh_jurnal"); FAY = os.path.join(HERE, "guruh_fayllar")


def slug(s): return re.sub(r"[^\w\-]+", "_", s.strip())[:60] or "guruh"
def now(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def cmd_yoz(o):
    os.makedirs(JUR, exist_ok=True)
    rec = {"vaqt": o.vaqt or now(), "kim": o.kim, "matn": o.matn or ""}
    if o.fayl and os.path.exists(o.fayl):
        d = os.path.join(FAY, slug(o.guruh)); os.makedirs(d, exist_ok=True)
        dst = os.path.join(d, datetime.datetime.now().strftime("%Y%m%d_%H%M%S_") + os.path.basename(o.fayl))
        shutil.copy2(o.fayl, dst); rec["fayl"] = dst
    with open(os.path.join(JUR, slug(o.guruh) + ".jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("ok")


def oqi(guruh):
    p = os.path.join(JUR, slug(guruh) + ".jsonl")
    if not os.path.exists(p):
        raise SystemExit(f"'{guruh}' bo'yicha jurnal yo'q. Mavjudlari: python guruh_tool.py royxat")
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def chegara(soat): return (datetime.datetime.now() - datetime.timedelta(hours=soat)).strftime("%Y-%m-%d %H:%M")


def cmd_oxirgi(o):
    rs = [r for r in oqi(o.guruh) if r["vaqt"] >= chegara(o.soat)]
    if o.qidir: rs = [r for r in rs if o.qidir.lower() in (r["matn"] + " " + r["kim"]).lower()]
    rs = rs[-o.max:]
    print(f"{o.guruh}: oxirgi {o.soat} soat, {len(rs)} xabar")
    for r in rs:
        m = r["matn"].replace("\n", " ")
        print(f"{r['vaqt'][5:]} {r['kim']}: {m[:300]}" + (f" [fayl: {os.path.basename(r['fayl'])}]" if r.get("fayl") else ""))


def cmd_royxat(o):
    if not os.path.isdir(JUR): print("Hali guruh xabarlari yo'q"); return
    for fn in sorted(os.listdir(JUR)):
        with open(os.path.join(JUR, fn), encoding="utf-8") as f: ls = f.readlines()
        last = json.loads(ls[-1])["vaqt"] if ls else "-"
        print(f"{fn[:-6]}: {len(ls)} xabar, oxirgisi {last}")


def cmd_fayllar(o):
    rs = [r for r in oqi(o.guruh) if r.get("fayl") and r["vaqt"] >= chegara(o.soat)]
    for r in rs: print(f"{r['vaqt']} {r['kim']}: {r['fayl']}")
    print(f"Jami: {len(rs)} fayl")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    y = sp.add_parser("yoz"); y.add_argument("--guruh", required=True); y.add_argument("--kim", required=True)
    y.add_argument("--matn", default=""); y.add_argument("--fayl"); y.add_argument("--vaqt")
    x = sp.add_parser("oxirgi"); x.add_argument("--guruh", required=True); x.add_argument("--soat", type=float, default=24)
    x.add_argument("--qidir"); x.add_argument("--max", type=int, default=200)
    sp.add_parser("royxat")
    fl = sp.add_parser("fayllar"); fl.add_argument("--guruh", required=True); fl.add_argument("--soat", type=float, default=72)
    o = ap.parse_args()
    {"yoz": cmd_yoz, "oxirgi": cmd_oxirgi, "royxat": cmd_royxat, "fayllar": cmd_fayllar}[o.cmd](o)


if __name__ == "__main__":
    main()
