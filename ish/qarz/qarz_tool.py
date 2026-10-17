# -*- coding: utf-8 -*-
"""
Ta'minotchilar bilan qarz hisobi (biz mahsulot olamiz, pul o'tkazamiz) — Jurat uchun.
Ma'lumot: qarz_data.json (shu papkada). Excel: Qarzlar_<sana>.xlsx

Buyruqlar (shu papkada ishga tushiring):
  python qarz_tool.py kirim  --firma "Baraka Savdo" --date 16.10.2026 --mahsulot "Armatura 12" --miqdor 2.5 --birlik t --narx 8500000 [--summa N] [--hujjat "Faktura 45"] [--biz TSB]
  python qarz_tool.py tolov  --firma "Baraka Savdo" --date 16.10.2026 --summa 10000000 [--hujjat "p/p 112"] [--biz TSB]
  python qarz_tool.py boshlangich --firma "Baraka Savdo" --date 01.10.2026 --summa 5000000   (+ biz qarzdormiz, - ular bizga qarzdor)
  python qarz_tool.py qarz [--biz TSB]                   -> hamma firma: olindi / to'landi / QARZ
  python qarz_tool.py tarix --firma "Baraka" [--dan 01.10.2026] [--gacha 31.10.2026]   -> sana bo'yicha nima olindi, qancha to'landi, qoldiq
  python qarz_tool.py mahsulot --firma "Baraka"          -> qaysi mahsulotdan jami qancha olindi
  python qarz_tool.py import --file yozuvlar.json        -> ko'p qatorni birdan (Didox / bank ko'chirmasidan)
       [{"tur":"kirim","firma":"..","date":"..","mahsulot":"..","miqdor":1,"birlik":"t","narx":1,"summa":1,"hujjat":".."},
        {"tur":"tolov","firma":"..","date":"..","summa":1,"hujjat":".."}]
  python qarz_tool.py list [--firma ".."]   |   python qarz_tool.py del --id 7
  python qarz_tool.py excel [--firma ".."] [--biz TSB]   -> Excel (Qarzlar varag'i + har firma uchun hisob varag'i)
Takror yozuv (firma+sana+tur+summa+hujjat bir xil) qo'shilmaydi. Kerak: pip install openpyxl
"""
import argparse, json, os, re, sys, datetime, difflib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "qarz_data.json")


def money(x):
    return f"{round(x):,}".replace(",", " ")


def to_iso(s):
    s = str(s).strip()
    m = re.match(r"(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})$", s)
    if m:
        d, mo, y = m.groups(); y = ("20" + y) if len(y) == 2 else y
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    if re.match(r"\d{4}-\d{2}-\d{2}$", s): return s
    raise SystemExit(f"Sana noto'g'ri: {s} (KK.OO.YYYY)")


def dmy(iso): return f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}"


def num(x):
    if x in (None, ""): return None
    return float(str(x).replace(" ", "").replace(" ", "").replace(",", "."))


def load():
    if not os.path.exists(DATA): return {"firmalar": [], "yozuvlar": []}
    with open(DATA, encoding="utf-8") as f: return json.load(f)


def save(db):
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=1)
    os.replace(tmp, DATA)


def key(name):
    s = str(name).upper().replace("Ё", "Е")
    s = re.sub(r"[\"'«»“”`]", " ", s)
    s = re.sub(r"\b(MCHJ|MChJ|МЧЖ|OOO|ООО|XK|ХК|QK|YATT|ЯТТ|AJ|АЖ|LLC)\b", " ", s, flags=re.I)
    return re.sub(r"\s+", " ", s).strip()


def resolve(db, name, create=False):
    """Firma nomini mavjud ro'yxatdan topadi (qisman / imlo xatosi bilan ham)."""
    k = key(name)
    names = db["firmalar"]
    for n in names:
        if key(n) == k: return n, ""
    part = [n for n in names if k and (k in key(n) or key(n) in k)]
    if len(part) == 1: return part[0], f"(firma: {part[0]})"
    close = difflib.get_close_matches(k, [key(n) for n in names], n=1, cutoff=0.85)
    if close:
        n = next(n for n in names if key(n) == close[0]); return n, f"(firma: {n})"
    if len(part) > 1 and not create:
        raise SystemExit("Bir nechta firma mos keldi: " + "; ".join(part) + " — aniqroq yozing")
    if not create:
        raise SystemExit(f"Firma topilmadi: {name}. Mavjud: " + "; ".join(names[:30]))
    names.append(str(name).strip()); return names[-1], "YANGI FIRMA qo'shildi"


def add_row(db, r):
    for x in db["yozuvlar"]:
        if (x["firma"], x["date"], x["tur"], round(x["summa"], 2), x.get("hujjat", ""), x.get("mahsulot", "")) == \
           (r["firma"], r["date"], r["tur"], round(r["summa"], 2), r.get("hujjat", ""), r.get("mahsulot", "")):
            return None, x["id"]
    r["id"] = max([x["id"] for x in db["yozuvlar"]] or [0]) + 1
    db["yozuvlar"].append(r); return r, None


def balance(db, firma, biz=None):
    rows = [x for x in db["yozuvlar"] if x["firma"] == firma and (not biz or x.get("biz", "") == biz)]
    k = sum(x["summa"] for x in rows if x["tur"] in ("kirim", "boshlangich"))
    t = sum(x["summa"] for x in rows if x["tur"] == "tolov")
    return k, t, k - t, rows


def ledger(rows):
    out, q = [], 0.0
    for x in sorted(rows, key=lambda x: (x["date"], 0 if x["tur"] == "boshlangich" else 1, x["id"])):
        q += x["summa"] if x["tur"] != "tolov" else -x["summa"]
        out.append((x, q))
    return out


def holat(q):
    if abs(q) < 0.5: return "hisob-kitob yopiq (qarz yo'q)"
    return f"BIZ QARZMIZ: {money(q)} so'm" if q > 0 else f"ULAR BIZGA QARZ (avans): {money(-q)} so'm"


# ---------------- commands ----------------
def cmd_kirim(o, db):
    firma, note = resolve(db, o.firma, create=True)
    miq, narx, summa = num(o.miqdor), num(o.narx), num(o.summa)
    if summa is None:
        if miq is None or narx is None: raise SystemExit("summa yoki (miqdor va narx) kerak")
        summa = round(miq * narx, 2)
    elif miq is not None and narx is not None and abs(miq * narx - summa) > max(1, summa * 0.001):
        note += f" | DIQQAT: miqdor×narx = {money(miq*narx)}, summa = {money(summa)} — tekshiring"
    r, dup = add_row(db, {"tur": "kirim", "firma": firma, "date": to_iso(o.date), "mahsulot": o.mahsulot or "",
                          "miqdor": miq, "birlik": o.birlik or "", "narx": narx, "summa": summa,
                          "hujjat": o.hujjat or "", "biz": o.biz or "", "izoh": o.izoh or ""})
    if dup: print(f"TAKROR — qo'shilmadi (id {dup})"); return
    save(db); k, t, q, _ = balance(db, firma, o.biz or None)
    mq = "" if miq is None else f" {miq:g} {r['birlik']}"
    print(f"Kirim #{r['id']}: {dmy(r['date'])} | {firma} | {r['mahsulot']}{mq} | {money(summa)} so'm {note}".rstrip())
    print(f"{firma}: olindi {money(k)}, to'landi {money(t)} → {holat(q)}")


def cmd_tolov(o, db):
    firma, note = resolve(db, o.firma, create=False)
    r, dup = add_row(db, {"tur": "tolov", "firma": firma, "date": to_iso(o.date), "summa": num(o.summa),
                          "hujjat": o.hujjat or "", "biz": o.biz or "", "izoh": o.izoh or ""})
    if dup: print(f"TAKROR — qo'shilmadi (id {dup})"); return
    save(db); k, t, q, _ = balance(db, firma, o.biz or None)
    print(f"To'lov #{r['id']}: {dmy(r['date'])} | {firma} | {money(r['summa'])} so'm {note}".rstrip())
    print(f"{firma}: olindi {money(k)}, to'landi {money(t)} → {holat(q)}")


def cmd_bosh(o, db):
    firma, note = resolve(db, o.firma, create=True)
    r, dup = add_row(db, {"tur": "boshlangich", "firma": firma, "date": to_iso(o.date), "summa": num(o.summa),
                          "hujjat": "boshlang'ich qoldiq", "biz": o.biz or "", "izoh": ""})
    if dup: print(f"TAKROR (id {dup})"); return
    save(db); print(f"Boshlang'ich qoldiq #{r['id']}: {firma} {money(r['summa'])} ({dmy(r['date'])}) {note}")


def cmd_qarz(o, db):
    tot = 0; lines = []
    for f in sorted(db["firmalar"]):
        k, t, q, rows = balance(db, f, o.biz or None)
        if not rows: continue
        last = max(x["date"] for x in rows if x["tur"] != "tolov") if any(x["tur"] != "tolov" for x in rows) else ""
        lines.append((q, f"{f}: olindi {money(k)} | to'landi {money(t)} | {holat(q)}" + (f" | oxirgi kirim {dmy(last)}" if last else "")))
        tot += q
    if not lines: print("Yozuv yo'q."); return
    for _, l in sorted(lines, key=lambda x: -x[0]): print(l)
    print(f"JAMI: {holat(tot)}")


def flt(rows, o):
    if getattr(o, "dan", ""): rows = [x for x in rows if x["date"] >= to_iso(o.dan)]
    if getattr(o, "gacha", ""): rows = [x for x in rows if x["date"] <= to_iso(o.gacha)]
    return rows


def cmd_tarix(o, db):
    firma, _ = resolve(db, o.firma)
    k, t, q, rows = balance(db, firma, o.biz or None)
    print(f"{firma} — hisob tarixi")
    for x, run in ledger(rows):
        if (o.dan and x["date"] < to_iso(o.dan)) or (o.gacha and x["date"] > to_iso(o.gacha)): continue
        if x["tur"] == "kirim":
            mq = "" if x.get("miqdor") is None else f" {x['miqdor']:g} {x.get('birlik','')}"
            print(f"{dmy(x['date'])}  OLINDI  {x.get('mahsulot','')}{mq}  +{money(x['summa'])}  {x.get('hujjat','')}  → qoldiq {money(run)}")
        elif x["tur"] == "tolov":
            print(f"{dmy(x['date'])}  TO'LANDI  −{money(x['summa'])}  {x.get('hujjat','')}  → qoldiq {money(run)}")
        else:
            print(f"{dmy(x['date'])}  BOSHLANG'ICH QOLDIQ  {money(x['summa'])}")
    print(f"Jami olindi {money(k)} | to'landi {money(t)} | {holat(q)}")


def cmd_mahsulot(o, db):
    firma, _ = resolve(db, o.firma)
    agg = collections.OrderedDict()
    for x in sorted(db["yozuvlar"], key=lambda x: x["date"]):
        if x["firma"] != firma or x["tur"] != "kirim": continue
        a = agg.setdefault((x.get("mahsulot", ""), x.get("birlik", "")), [0.0, 0.0, 0, x["date"], x["date"]])
        a[0] += x.get("miqdor") or 0; a[1] += x["summa"]; a[2] += 1; a[4] = x["date"]
    print(f"{firma} — olingan mahsulotlar")
    for (m, b), (mq, s, n, d1, d2) in agg.items():
        print(f"{m or '(nomsiz)'}: {mq:g} {b} | {money(s)} so'm | {n} marta | {dmy(d1)}–{dmy(d2)}")


def cmd_import(o, db):
    with open(o.file, encoding="utf-8") as f: items = json.load(f)
    add = dup = 0; new_f = set()
    for it in items:
        tur = it.get("tur", "kirim")
        firma, note = resolve(db, it["firma"], create=True)
        if "YANGI" in note: new_f.add(firma)
        miq, narx, summa = num(it.get("miqdor")), num(it.get("narx")), num(it.get("summa"))
        if summa is None and miq is not None and narx is not None: summa = round(miq * narx, 2)
        r, d = add_row(db, {"tur": tur, "firma": firma, "date": to_iso(it["date"]), "mahsulot": it.get("mahsulot", ""),
                            "miqdor": miq, "birlik": it.get("birlik", ""), "narx": narx, "summa": summa,
                            "hujjat": it.get("hujjat", ""), "biz": it.get("biz", ""), "izoh": it.get("izoh", "")})
        add += bool(r); dup += bool(d)
    save(db)
    print(f"Import: {add} ta qo'shildi, {dup} ta takror (o'tkazib yuborildi)" + (f", yangi firmalar: {', '.join(sorted(new_f))}" if new_f else ""))


def cmd_list(o, db):
    firma = resolve(db, o.firma)[0] if o.firma else None
    for x in sorted(db["yozuvlar"], key=lambda x: (x["date"], x["id"])):
        if not firma or x["firma"] == firma: print(x)


def cmd_del(o, db):
    n = len(db["yozuvlar"]); db["yozuvlar"] = [x for x in db["yozuvlar"] if x["id"] != o.id]
    save(db); print("o'chirildi" if len(db["yozuvlar"]) < n else "topilmadi")


def cmd_excel(o, db):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter as L
    F = Font(name="Arial", size=10); B = Font(name="Arial", size=10, bold=True)
    H = Font(name="Arial", size=10, bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor="0A6C96")
    TF = PatternFill("solid", fgColor="E3F1F8"); RF = PatternFill("solid", fgColor="FDECEA")
    th = Side(style="thin", color="BFBFBF"); BD = Border(left=th, right=th, top=th, bottom=th)
    NUM = '#,##0;-#,##0;-'; NUM3 = '#,##0.###;-#,##0.###;-'

    def hdr(ws, r, cols):
        for i, c in enumerate(cols, 1):
            x = ws.cell(r, i, c); x.font = H; x.fill = HF; x.border = BD
            x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def cell(ws, r, c, v, fmt=None, font=F, fill=None):
        x = ws.cell(r, c, v); x.font = font; x.border = BD
        if fmt: x.number_format = fmt
        if fill: x.fill = fill
        return x

    firms = [resolve(db, o.firma)[0]] if o.firma else sorted({x["firma"] for x in db["yozuvlar"]})
    wb = Workbook(); S = wb.active; S.title = "Qarzlar"
    S["A1"] = "Ta'minotchilar bilan hisob-kitob" + (f" ({o.biz})" if o.biz else ""); S["A1"].font = Font(name="Arial", size=13, bold=True)
    S["A2"] = f"Holat: {datetime.date.today():%d.%m.%Y} · musbat qoldiq = biz qarzmiz, manfiy = avans"; S["A2"].font = Font(name="Arial", size=9, italic=True)
    hdr(S, 4, ["№", "Firma", "Olindi (mahsulot), so'm", "To'landi, so'm", "QOLDIQ QARZ, so'm", "Oxirgi kirim", "Oxirgi to'lov"])
    r = 5
    for i, f in enumerate(firms, 1):
        k, t, q, rows = balance(db, f, o.biz or None)
        if not rows: continue
        lk = max([x["date"] for x in rows if x["tur"] == "kirim"] or [""]); lt = max([x["date"] for x in rows if x["tur"] == "tolov"] or [""])
        cell(S, r, 1, i); cell(S, r, 2, f); cell(S, r, 3, round(k, 2), NUM); cell(S, r, 4, round(t, 2), NUM)
        cell(S, r, 5, f"=C{r}-D{r}", NUM, B, RF if q > 0.5 else None)
        cell(S, r, 6, dmy(lk) if lk else ""); cell(S, r, 7, dmy(lt) if lt else ""); r += 1
    cell(S, r, 2, "JAMI", font=B, fill=TF)
    for c in (3, 4, 5): cell(S, r, c, f"=SUM({L(c)}5:{L(c)}{r-1})", NUM, B, TF)
    for c, w in zip("ABCDEFG", [5, 34, 22, 20, 22, 13, 13]): S.column_dimensions[c].width = w
    S.freeze_panes = "A5"

    for f in firms:
        k, t, q, rows = balance(db, f, o.biz or None)
        if not rows: continue
        ws = wb.create_sheet(re.sub(r"[\[\]\*\?/\\:]", "", f)[:31])
        ws["A1"] = f"{f} — hisob-kitob"; ws["A1"].font = Font(name="Arial", size=12, bold=True)
        hdr(ws, 3, ["Sana", "Hujjat", "Mahsulot", "Miqdor", "Birlik", "Narx", "Olindi, so'm", "To'landi, so'm", "Qoldiq qarz, so'm"])
        rr = 4
        for x, _ in ledger(rows):
            cell(ws, rr, 1, dmy(x["date"])); cell(ws, rr, 2, x.get("hujjat", ""))
            cell(ws, rr, 3, x.get("mahsulot", "") if x["tur"] == "kirim" else ("To'lov" if x["tur"] == "tolov" else "Boshlang'ich qoldiq"))
            cell(ws, rr, 4, x.get("miqdor"), NUM3); cell(ws, rr, 5, x.get("birlik", "")); cell(ws, rr, 6, x.get("narx"), NUM)
            cell(ws, rr, 7, x["summa"] if x["tur"] != "tolov" else None, NUM)
            cell(ws, rr, 8, x["summa"] if x["tur"] == "tolov" else None, NUM)
            cell(ws, rr, 9, f"=G{rr}-H{rr}" if rr == 4 else f"=I{rr-1}+G{rr}-H{rr}", NUM, B)
            rr += 1
        cell(ws, rr, 3, "JAMI", font=B, fill=TF)
        for c in (7, 8): cell(ws, rr, c, f"=SUM({L(c)}4:{L(c)}{rr-1})", NUM, B, TF)
        cell(ws, rr, 9, f"=G{rr}-H{rr}", NUM, B, RF)
        for c, w in zip("ABCDEFGHI", [12, 18, 30, 10, 8, 14, 18, 18, 20]): ws.column_dimensions[c].width = w
        ws.freeze_panes = "A4"
    name = f"Qarzlar_{datetime.date.today():%Y-%m-%d}" + (f"_{key(o.firma).replace(' ', '_')}" if o.firma else "") + ".xlsx"
    path = os.path.join(HERE, name); wb.save(path); print(path)


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("kirim")
    for n in ("--firma", "--date"): a.add_argument(n, required=True)
    for n in ("--mahsulot", "--miqdor", "--birlik", "--narx", "--summa", "--hujjat", "--biz", "--izoh"): a.add_argument(n, default="")
    t = sp.add_parser("tolov")
    for n in ("--firma", "--date", "--summa"): t.add_argument(n, required=True)
    for n in ("--hujjat", "--biz", "--izoh"): t.add_argument(n, default="")
    b = sp.add_parser("boshlangich")
    for n in ("--firma", "--date", "--summa"): b.add_argument(n, required=True)
    b.add_argument("--biz", default="")
    q = sp.add_parser("qarz"); q.add_argument("--biz", default="")
    h = sp.add_parser("tarix"); h.add_argument("--firma", required=True)
    for n in ("--dan", "--gacha", "--biz"): h.add_argument(n, default="")
    m = sp.add_parser("mahsulot"); m.add_argument("--firma", required=True)
    i = sp.add_parser("import"); i.add_argument("--file", required=True)
    l = sp.add_parser("list"); l.add_argument("--firma", default="")
    d = sp.add_parser("del"); d.add_argument("--id", type=int, required=True)
    e = sp.add_parser("excel"); e.add_argument("--firma", default=""); e.add_argument("--biz", default="")
    o = ap.parse_args(); db = load()
    {"kirim": cmd_kirim, "tolov": cmd_tolov, "boshlangich": cmd_bosh, "qarz": cmd_qarz, "tarix": cmd_tarix,
     "mahsulot": cmd_mahsulot, "import": cmd_import, "list": cmd_list, "del": cmd_del, "excel": cmd_excel}[o.cmd](o, db)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    main()
