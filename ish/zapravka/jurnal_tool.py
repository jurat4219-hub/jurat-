# -*- coding: utf-8 -*-
"""
Zapravka jurnali (IYK OTA, metan) — Jurat uchun.
Narx DOIM 4 500 so'm/kub (zapravka ekranidagi narx va summa hisobga olinmaydi).

Buyruqlar (shu papkada ishga tushiring):
  python jurnal_tool.py add --date 14.10.2026 --plate "01 696 OMA" --kub 186.041 [--time 18:27] [--driver "Doronov F"] [--video v3.mp4] [--note "..."]
  python jurnal_tool.py list [--month 2026-10]
  python jurnal_tool.py del --id 5
  python jurnal_tool.py merge --id 5 --add 16.311          (paftor: kubni oldingi yozuvga qo'shish)
  python jurnal_tool.py summary --month 2026-10 [--day 15.10.2026]
  python jurnal_tool.py history                             (har mashinaning odatiy kub oralig'i)
  python jurnal_tool.py vedadd --file ved_2026-10.json --date 14.10.2026 --plate "01 696 OMA" --kub "162+16" [--driver "..."]
                                                            (vedomost qatorini qo'shadi; bor qatorni qayta qo'shmaydi)
  python jurnal_tool.py check --month 2026-10               (shubhali yozuvlar: "?", izohli, bir kunda 2 marta, paftor ehtimoli)
  python jurnal_tool.py build [--month 2026-10]          -> Zapravka_jurnal_2026-10.xlsx
  python jurnal_tool.py sverka --vedomost ved.json [--month 2026-10]   -> Sverka_2026-10.xlsx
     ved.json = [{"date":"2026-10-14","plate":"01 696 OMA","kub":186.041,"driver":"..."}, ...]
Kerak: pip install openpyxl
"""
import argparse, json, os, re, sys, datetime, collections
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as L

PRICE = 4500  # so'm / kub — IYK OTA bilan kelishilgan narx
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "jurnal_data.json")
FLEET_XLSX = os.path.join(HERE, "IYK_OTA_mashinalar.xlsx")

F = Font(name='Arial', size=10); B = Font(name='Arial', size=10, bold=True)
H = Font(name='Arial', size=10, bold=True, color='FFFFFF')
HF = PatternFill('solid', fgColor='0A6C96'); TF = PatternFill('solid', fgColor='E3F1F8')
WF = PatternFill('solid', fgColor='FFF3D1'); RF = PatternFill('solid', fgColor='FDECEA'); GF = PatternFill('solid', fgColor='E4F4EB')
th = Side(style='thin', color='BFBFBF'); BD = Border(left=th, right=th, top=th, bottom=th)
NUM = '#,##0;-#,##0;-'; NUM3 = '#,##0.###;-#,##0.###;-'
OYLAR = {'01':'Yanvar','02':'Fevral','03':'Mart','04':'Aprel','05':'May','06':'Iyun','07':'Iyul','08':'Avgust','09':'Sentyabr','10':'Oktyabr','11':'Noyabr','12':'Dekabr'}

CYR = {"А":"A","В":"B","Е":"E","К":"K","М":"M","Н":"H","О":"O","Р":"P","С":"C","Т":"T","У":"U","Х":"X","Л":"L","Ф":"F","Қ":"Q","Ў":"O","Г":"G","Д":"D","З":"Z","И":"I"}
def norm_plate(p):
    raw = str(p or "").upper()
    s = "".join(CYR.get(c, c) for c in raw)
    s = re.sub(r"[^0-9A-Z?]", "", s)
    if len(s) == 8 and not re.match(r"^\d{5}[A-Z]{3}$", s):  # OCR chalkashligi: O<->0, I<->1, B<->8, S<->5, Z<->2
        d = s[:5].translate(str.maketrans("OQDIZSB", "0001258")); l = s[5:].translate(str.maketrans("0185", "OIBS"))
        s = d + l
    m = re.match(r"^(\d{2})(\d{3})([A-Z]{3})$", s)
    return f"{m[1]} {m[2]} {m[3]}" if m else (raw.strip() or "?")

def to_iso(s):
    s = str(s).strip()
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m: return f"{int(m[1]):04d}-{int(m[2]):02d}-{int(m[3]):02d}"
    m = re.match(r"^(\d{1,2})[.\/-](\d{1,2})[.\/-](\d{2,4})$", s)
    if m:
        y = int(m[3]); y = y + 2000 if y < 100 else y
        return f"{y:04d}-{int(m[2]):02d}-{int(m[1]):02d}"
    raise SystemExit(f"Sana tushunilmadi: {s}")

def load():
    if not os.path.exists(DATA): return []
    with open(DATA, encoding='utf-8') as f: return json.load(f)
def save(rows):
    with open(DATA, 'w', encoding='utf-8', newline='\n') as f: json.dump(rows, f, ensure_ascii=False, indent=1)

def fleet():
    """Mashinalar ro'yxati (IYK_OTA_mashinalar.xlsx 'Mashinalar' varag'i)."""
    out = collections.OrderedDict()
    if not os.path.exists(FLEET_XLSX): return out
    from openpyxl import load_workbook
    ws = load_workbook(FLEET_XLSX, read_only=True)['Mashinalar']
    for r in ws.iter_rows(min_row=5, values_only=True):
        if r[1] and re.match(r"^\d{2} \d{3} [A-Z]{3}$", str(r[1])): out[r[1]] = r[2] or ""
    return out

def match_plate(p):
    """(raqam, izoh). 1 belgi farq -> ro'yxatdagisi."""
    f = fleet(); p = norm_plate(p)
    if "?" in p or not p.strip(): return "?", "raqam noma'lum — Juratdan so'rash kerak"
    if not f or p in f: return p, ""
    if re.match(r"^\d{2} \d{3} [A-Z]{3}$", p):
        near = [k for k in f if sum(a != b for a, b in zip(k, p)) == 1]
        if len(near) == 1: return near[0], f"ro'yxatdan tuzatildi (o'qilgan: {p})"
    return p, "YANGI MASHINA? ro'yxatda yo'q"


def history():
    """Har mashina bo'yicha IYK OTA vedomostidagi kub tarixi: {plate: (min, median, max, n)}."""
    out = {}
    if not os.path.exists(FLEET_XLSX): return out
    from openpyxl import load_workbook
    try:
        ws = load_workbook(FLEET_XLSX, read_only=True)['Barcha qatorlar']
    except KeyError:
        return out
    tmp = collections.defaultdict(list)
    for r in ws.iter_rows(min_row=5, values_only=True):
        if r and r[3] and isinstance(r[5], (int, float)): tmp[r[3]].append(float(r[5]))
    for p, v in tmp.items():
        v.sort(); out[p] = (v[0], v[len(v) // 2], v[-1], len(v))
    return out

def kub_warning(plate, kub):
    h = history().get(plate)
    if kub > 300: return "KUB JUDA KATTA (>300) — displeyni qayta tekshiring"
    if h and kub > h[2] * 1.15: return f"bu mashina uchun odatdan katta (tarixda max {h[2]:.0f}) — tekshiring"
    if kub < 60: return "kichik kub — paftor bo'lsa merge qiling"
    return ""

def summary(month, day=None):
    rows = [r for r in month_rows(load(), month) if not day or r['date'] == day]
    if not rows: return "Yozuv yo'q."
    tot = sum(float(r['kub']) for r in rows)
    by = collections.defaultdict(lambda: [0, 0.0])
    for r in rows: by[r['plate']][0] += 1; by[r['plate']][1] += float(r['kub'])
    lines = [f"{'Kun ' + day if day else 'Oy ' + month}: {len(rows)} ta, {tot:.3f} kub, {round(tot * PRICE):,} so'm".replace(',', ' ')]
    for p, (n, k) in sorted(by.items(), key=lambda kv: -kv[1][1]):
        lines.append(f"  {p}: {n} marta, {k:.3f} kub")
    unk = [r for r in rows if r['plate'] == '?' or r.get('note')]
    if unk: lines.append(f"Diqqat: {len(unk)} ta yozuvda izoh/noma'lum raqam bor (list bilan ko'ring)")
    return "\n".join(lines)

# ---------- helpers for sheets ----------
def hdr(ws, r, cols):
    for i, c in enumerate(cols, 1):
        x = ws.cell(r, i, c); x.font = H; x.fill = HF; x.border = BD
        x.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
def title(ws, t, sub):
    ws['A1'] = t; ws['A1'].font = Font(name='Arial', size=13, bold=True)
    ws['A2'] = sub; ws['A2'].font = Font(name='Arial', size=9, italic=True, color='5A6B78')
def cell(ws, r, c, v, fmt=None, font=F, fill=None):
    x = ws.cell(r, c, v); x.font = font; x.border = BD
    if fmt: x.number_format = fmt
    if fill: x.fill = fill
    return x
def total_row(ws, r, ncol):
    for j in range(1, ncol + 1):
        x = ws.cell(r, j); x.fill = TF; x.font = B; x.border = BD
def widths(ws, ws_w):
    for j, w in enumerate(ws_w, 1): ws.column_dimensions[L(j)].width = w
def finish(wb):
    for ws in wb:
        ws.sheet_view.showGridLines = False
        ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1

def month_rows(rows, month):
    return [r for r in rows if not month or r['date'].startswith(month)]

# ---------- build jurnal ----------
def build(month):
    rows = sorted(month_rows(load(), month), key=lambda r: (r['date'], r.get('time') or '', r['id']))
    if not rows: raise SystemExit("Bu oy uchun yozuv yo'q.")
    d0, d1 = rows[0]['date'], rows[-1]['date']
    dmy = lambda iso: f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}"
    period = f"{dmy(d0)} – {dmy(d1)}"
    wb = Workbook()
    # Barcha qatorlar
    R = wb.active; R.title = 'Barcha qatorlar'
    title(R, "Zapravka jurnali (videolar bo'yicha) — barcha qatorlar", f"IYK OTA · metan · {period} · narx {PRICE:,} so'm/kub (doimiy)".replace(',', ' '))
    hdr(R, 4, ['№', 'Sana', 'Vaqt', 'Davlat raqami', 'Haydovchi', 'Kub', 'Narx', 'Summa', 'Video', 'Izoh'])
    for i, x in enumerate(rows, 1):
        r = 4 + i; warn = bool(x.get('note'))
        fill = WF if warn else None
        cell(R, r, 1, i, fill=fill)
        cell(R, r, 2, datetime.date.fromisoformat(x['date']), 'DD.MM.YYYY', fill=fill)
        cell(R, r, 3, x.get('time') or '', fill=fill)
        cell(R, r, 4, x['plate'], fill=fill)
        cell(R, r, 5, x.get('driver') or '', fill=fill)
        cell(R, r, 6, float(x['kub']), NUM3, fill=fill)
        cell(R, r, 7, PRICE, NUM, fill=fill)
        cell(R, r, 8, f"=F{r}*G{r}", NUM, fill=fill)
        cell(R, r, 9, x.get('video') or '', fill=fill)
        cell(R, r, 10, x.get('note') or '', fill=fill)
    last = 4 + len(rows); t = last + 1
    R.cell(t, 1, 'Jami'); R.cell(t, 6, f"=SUM(F5:F{last})").number_format = NUM3; R.cell(t, 8, f"=SUM(H5:H{last})").number_format = NUM
    total_row(R, t, 10); widths(R, [6, 12, 8, 15, 18, 11, 9, 14, 18, 45])
    R.freeze_panes = 'A5'; R.auto_filter.ref = f"A4:J{last}"
    RG = lambda col: f"'Barcha qatorlar'!${col}$5:${col}${last}"
    # Mashinalar
    M = wb.create_sheet('Mashinalar', 0)
    title(M, "Zapravka jurnali — mashinalar bo'yicha", f"{period} · 'Barcha qatorlar' varag'idan formulalar bilan")
    hdr(M, 4, ['№', 'Davlat raqami', 'Haydovchi(lar)', 'Necha marta', 'Jami kub', "Summa, so'm", 'Birinchi sana', 'Oxirgi sana'])
    agg = collections.OrderedDict()
    for x in rows:
        a = agg.setdefault(x['plate'], {'k': 0, 'dr': []}); a['k'] += float(x['kub'])
        if x.get('driver') and x['driver'] not in a['dr']: a['dr'].append(x['driver'])
    fl = fleet()
    order = sorted(agg, key=lambda p: -agg[p]['k'])
    for i, p in enumerate(order, 1):
        r = 4 + i
        cell(M, r, 1, i); cell(M, r, 2, p)
        cell(M, r, 3, ', '.join(agg[p]['dr']) or fl.get(p, ''))
        cell(M, r, 4, f"=COUNTIFS({RG('D')},B{r})")
        cell(M, r, 5, f"=SUMIFS({RG('F')},{RG('D')},B{r})", NUM3)
        cell(M, r, 6, f"=SUMIFS({RG('H')},{RG('D')},B{r})", NUM)
        cell(M, r, 7, f"=_xlfn.MINIFS({RG('B')},{RG('D')},B{r})", 'DD.MM.YYYY')
        cell(M, r, 8, f"=_xlfn.MAXIFS({RG('B')},{RG('D')},B{r})", 'DD.MM.YYYY')
    ml = 4 + len(order); t = ml + 1
    M.cell(t, 2, f"Jami: {len(order)} ta mashina")
    M.cell(t, 4, f"=SUM(D5:D{ml})"); M.cell(t, 5, f"=SUM(E5:E{ml})").number_format = NUM3; M.cell(t, 6, f"=SUM(F5:F{ml})").number_format = NUM
    total_row(M, t, 8); widths(M, [5, 15, 32, 12, 12, 16, 13, 13]); M.freeze_panes = 'A5'
    # Kunlar bo'yicha
    K = wb.create_sheet("Kunlar bo'yicha", 1)
    days = sorted({x['date'] for x in rows})
    title(K, "Zapravka jurnali — kunlar bo'yicha", period)
    hdr(K, 4, ['Sana', 'Necha marta', 'Jami kub', "Summa, so'm"])
    for i, d in enumerate(days, 1):
        r = 4 + i
        cell(K, r, 1, datetime.date.fromisoformat(d), 'DD.MM.YYYY')
        cell(K, r, 2, f"=COUNTIFS({RG('B')},A{r})")
        cell(K, r, 3, f"=SUMIFS({RG('F')},{RG('B')},A{r})", NUM3)
        cell(K, r, 4, f"=SUMIFS({RG('H')},{RG('B')},A{r})", NUM)
    kl = 4 + len(days); t = kl + 1
    K.cell(t, 1, 'Jami'); K.cell(t, 2, f"=SUM(B5:B{kl})"); K.cell(t, 3, f"=SUM(C5:C{kl})").number_format = NUM3; K.cell(t, 4, f"=SUM(D5:D{kl})").number_format = NUM
    total_row(K, t, 4); widths(K, [13, 12, 12, 16])
    finish(wb)
    out = os.path.join(HERE, f"Zapravka_jurnal_{month or 'hammasi'}.xlsx"); wb.save(out)
    return out

# ---------- sverka ----------
def sverka(ved_path, month):
    ours = month_rows(load(), month)
    with open(ved_path, encoding='utf-8') as f: ved = json.load(f)
    ved = [{'date': to_iso(v['date']), 'plate': norm_plate(v['plate']), 'kub': float(v['kub']), 'driver': v.get('driver', '')} for v in ved]
    ved = [v for v in ved if not month or v['date'].startswith(month)]
    # juftlash: sana + raqam, kub bo'yicha eng yaqini
    pool = collections.defaultdict(list)
    for i, o in enumerate(ours): pool[(o['date'], o['plate'])].append(i)
    used = set(); pairs = []; only_v = []
    for v in sorted(ved, key=lambda x: (x['date'], x['plate'])):
        cand = [i for i in pool[(v['date'], v['plate'])] if i not in used]
        if cand:
            i = min(cand, key=lambda i: abs(float(ours[i]['kub']) - v['kub'])); used.add(i); pairs.append((v, ours[i]))
        else: only_v.append(v)
    only_o = [o for i, o in enumerate(ours) if i not in used]
    dmy = lambda iso: f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}"
    wb = Workbook()
    X = wb.active; X.title = 'Xulosa'
    title(X, f"IYK OTA sverkasi — {OYLAR.get((month or '0000-00')[5:7], '')} {(month or '')[:4]}", f"Vedomost vs videolar jurnali · narx {PRICE} so'm/kub")
    vk = sum(v['kub'] for v in ved); ok = sum(float(o['kub']) for o in ours)
    lines = [("Vedomost bo'yicha", len(ved), vk), ("Videolar (bizning jurnal) bo'yicha", len(ours), ok)]
    hdr(X, 4, ['Ko\'rsatkich', 'Necha marta', 'Kub', "Summa, so'm"])
    for i, (n, c, k) in enumerate(lines, 5):
        cell(X, i, 1, n); cell(X, i, 2, c); cell(X, i, 3, round(k, 3), NUM3); cell(X, i, 4, f"=C{i}*{PRICE}", NUM)
    cell(X, 7, 1, "FARQ (vedomost − bizda)", font=B, fill=RF); cell(X, 7, 2, "=B5-B6", font=B, fill=RF)
    cell(X, 7, 3, "=C5-C6", NUM3, B, RF); cell(X, 7, 4, "=D5-D6", NUM, B, RF)
    cell(X, 8, 1, "Farq, %", font=B); cell(X, 8, 3, "=IF(C6=0,0,(C5-C6)/C6)", '0.0%', B)
    X['A10'] = "Juftlangan: %d · Farq bor: %d · Faqat vedomostda: %d · Faqat bizda: %d" % (
        len(pairs), sum(1 for v, o in pairs if abs(v['kub'] - float(o['kub'])) > 0.001), len(only_v), len(only_o)); X['A10'].font = F
    X['A11'] = "Eslatma: 'Faqat vedomostda' — videosi yo'q yozuvlar. Har bir zapravka videoga olinmagan bo'lsa, bu ortiqcha degani emas."; X['A11'].font = Font(name='Arial', size=9, italic=True, color='5A6B78')
    widths(X, [38, 14, 14, 18])
    def table(name, cols, data, w):
        ws = wb.create_sheet(name); title(ws, name, f"{len(data)} ta qator"); hdr(ws, 4, cols)
        for i, row in enumerate(data, 1):
            for j, (v, f, fill) in enumerate(row, 1): cell(ws, 4 + i, j, v, f, fill=fill)
        widths(ws, w); ws.freeze_panes = 'A5'
    D = lambda iso: datetime.date.fromisoformat(iso)
    farq = [(v, o) for v, o in pairs if abs(v['kub'] - float(o['kub'])) > 0.001]
    table('Farq bor', ['Sana', 'Davlat raqami', 'Vedomost kub', 'Bizda kub', 'Farq kub', "Farq so'm", 'Video'],
          [[(D(v['date']), 'DD.MM.YYYY', None), (v['plate'], None, None), (v['kub'], NUM3, None), (float(o['kub']), NUM3, None),
            (round(v['kub'] - float(o['kub']), 3), NUM3, RF if v['kub'] > float(o['kub']) else GF), (round((v['kub'] - float(o['kub'])) * PRICE), NUM, None), (o.get('video', ''), None, None)] for v, o in farq],
          [12, 15, 14, 12, 12, 14, 18])
    table('Faqat vedomostda', ['Sana', 'Davlat raqami', 'Haydovchi', 'Kub', "Summa, so'm"],
          [[(D(v['date']), 'DD.MM.YYYY', None), (v['plate'], None, None), (v['driver'], None, None), (v['kub'], NUM3, RF), (round(v['kub'] * PRICE), NUM, None)] for v in only_v],
          [12, 15, 18, 12, 14])
    table('Faqat bizda', ['Sana', 'Davlat raqami', 'Kub', 'Video', 'Izoh'],
          [[(D(o['date']), 'DD.MM.YYYY', None), (o['plate'], None, None), (float(o['kub']), NUM3, None), (o.get('video', ''), None, None), (o.get('note', ''), None, None)] for o in only_o],
          [12, 15, 12, 18, 40])
    table('Mos keldi', ['Sana', 'Davlat raqami', 'Kub', 'Video'],
          [[(D(v['date']), 'DD.MM.YYYY', None), (v['plate'], None, None), (v['kub'], NUM3, GF), (o.get('video', ''), None, None)] for v, o in pairs if abs(v['kub'] - float(o['kub'])) <= 0.001],
          [12, 15, 12, 18])
    # mashina bo'yicha
    mm = collections.defaultdict(lambda: [0.0, 0.0])
    for v in ved: mm[v['plate']][0] += v['kub']
    for o in ours: mm[o['plate']][1] += float(o['kub'])
    table("Mashina bo'yicha", ['Davlat raqami', 'Vedomost kub', 'Bizda kub', 'Farq kub', "Farq so'm"],
          [[(p, None, None), (round(a, 3), NUM3, None), (round(b, 3), NUM3, None), (round(a - b, 3), NUM3, RF if a - b > 0.001 else None), (round((a - b) * PRICE), NUM, None)]
           for p, (a, b) in sorted(mm.items(), key=lambda kv: -(kv[1][0] - kv[1][1]))], [15, 14, 12, 12, 14])
    dd = collections.defaultdict(lambda: [0.0, 0.0])
    for v in ved: dd[v['date']][0] += v['kub']
    for o in ours: dd[o['date']][1] += float(o['kub'])
    table("Kun bo'yicha", ['Sana', 'Vedomost kub', 'Bizda kub', 'Farq kub', "Farq so'm"],
          [[(D(d), 'DD.MM.YYYY', None), (round(a, 3), NUM3, None), (round(b, 3), NUM3, None), (round(a - b, 3), NUM3, RF if a - b > 0.001 else None), (round((a - b) * PRICE), NUM, None)]
           for d, (a, b) in sorted(dd.items())], [12, 14, 12, 12, 14])
    finish(wb)
    out = os.path.join(HERE, f"Sverka_{month or 'hammasi'}.xlsx"); wb.save(out)
    print(f"Vedomost: {len(ved)} ta, {vk:.3f} kub | Bizda: {len(ours)} ta, {ok:.3f} kub | FARQ: {vk-ok:.3f} kub = {round((vk-ok)*PRICE):,} so'm".replace(',', ' '))
    return out

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    a = sp.add_parser('add'); a.add_argument('--date', required=True); a.add_argument('--plate', required=True); a.add_argument('--kub', required=True, type=float)
    a.add_argument('--time', default=''); a.add_argument('--driver', default=''); a.add_argument('--video', default=''); a.add_argument('--note', default='')
    l = sp.add_parser('list'); l.add_argument('--month', default='')
    d = sp.add_parser('del'); d.add_argument('--id', type=int, required=True)
    b = sp.add_parser('build'); b.add_argument('--month', default='')
    s = sp.add_parser('sverka'); s.add_argument('--vedomost', required=True); s.add_argument('--month', default='')
    m = sp.add_parser('merge'); m.add_argument('--id', type=int, required=True); m.add_argument('--add', type=float, required=True); m.add_argument('--note', default='paftor')
    u = sp.add_parser('summary'); u.add_argument('--month', default=''); u.add_argument('--day', default='')
    sp.add_parser('history')
    v = sp.add_parser('vedadd'); v.add_argument('--file', required=True); v.add_argument('--date', required=True); v.add_argument('--plate', required=True)
    v.add_argument('--kub', required=True); v.add_argument('--driver', default='')
    c = sp.add_parser('check'); c.add_argument('--month', default='')
    o = ap.parse_args()
    if o.cmd == 'add':
        with Lock():
            add(o)
        return
    elif o.cmd == 'list':
        for r in month_rows(load(), o.month): print(r)
    elif o.cmd == 'del':
        with Lock():
            rows = load(); n = len(rows); rows = [r for r in rows if r['id'] != o.id]; save(rows); print("o'chirildi" if len(rows) < n else "topilmadi")
    elif o.cmd == 'build': print(build(o.month))
    elif o.cmd == 'sverka': print(sverka(o.vedomost, o.month))
    elif o.cmd == 'merge':
        with Lock():
            rows = load(); r = next((x for x in rows if x['id'] == o.id), None)
            if not r: print("topilmadi"); return
            old_k = float(r['kub']); r['kub'] = round(old_k + o.add, 3)
            r['note'] = "; ".join(x for x in [r.get('note', ''), f"{old_k} + {o.add} {o.note}"] if x)
            save(rows); print(f"Qo'shildi (paftor) #{o.id}: {r['plate']} | {old_k} + {o.add} = {r['kub']} kub | {round(r['kub']*PRICE):,} so'm".replace(',', ' '))
    elif o.cmd == 'summary': print(summary(o.month, to_iso(o.day) if o.day else None))
    elif o.cmd == 'history':
        for p, (a, med, b, n) in sorted(history().items()): print(f"{p}: {n} ta, min {a:.0f}, o'rtacha {med:.0f}, max {b:.0f}")
    elif o.cmd == 'vedadd':
        with Lock():
            vedadd(o)
    elif o.cmd == 'check': print(check(o.month))

class Lock:
    """Bir nechta agent bir vaqtda yozsa, jurnal buzilmasligi uchun."""
    path = os.path.join(HERE, "jurnal_data.lock")
    def __enter__(self):
        import time
        for _ in range(300):
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY); return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.path) > 60: os.remove(self.path)
                except OSError: pass
                time.sleep(0.2)
        raise SystemExit("jurnal band — keyinroq urinib ko'ring")
    def __exit__(self, *a):
        os.close(self.fd)
        try: os.remove(self.path)
        except OSError: pass

def kub_expr(x):
    """'162+16' yoki '162.410+16.311' -> yig'indi (vedomostda paftor shunday yoziladi)."""
    parts = re.split(r"\s*\+\s*", str(x).replace(',', '.').strip())
    return round(sum(float(t) for t in parts if t), 3)

def vedadd(o):
    path = o.file if os.path.isabs(o.file) else os.path.join(HERE, o.file)
    ved = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else []
    iso = to_iso(o.date); plate, auto = match_plate(o.plate); k = kub_expr(o.kub)
    for v in ved:
        if to_iso(v['date']) == iso and norm_plate(v['plate']) == plate and abs(float(v['kub']) - k) < 0.0005:
            print(f"BOR — qo'shilmadi: {iso} {plate} {k}"); return
    ved.append({'date': iso, 'plate': plate, 'kub': k, 'driver': o.driver, 'raw': str(o.kub)})
    json.dump(ved, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    mon = [v for v in ved if to_iso(v['date'])[:7] == iso[:7]]
    print(f"Vedomostga qo'shildi: {iso} | {plate} | {o.kub} = {k} kub{(' | ' + auto) if auto else ''}")
    print(f"Vedomost oy bo'yicha: {len(mon)} ta, {sum(float(v['kub']) for v in mon):.3f} kub")

def check(month):
    rows = month_rows(load(), month); out = []
    by = collections.defaultdict(list)
    for r in rows: by[(r['date'], r['plate'])].append(r)
    for r in rows:
        if r['plate'] == '?': out.append(f"#{r['id']} {r['date']} raqam NOMA'LUM, {r['kub']} kub")
        elif r.get('note'): out.append(f"#{r['id']} {r['date']} {r['plate']} {r['kub']} — {r['note']}")
    for (d, p), lst in by.items():
        if p != '?' and len(lst) > 1:
            small = [x for x in lst if float(x['kub']) < 60]
            ids = ", ".join(f"#{x['id']}={x['kub']}" for x in lst)
            out.append(f"{d} {p} bir kunda {len(lst)} marta: {ids}" + (" — PAFTOR bo'lishi mumkin, merge qiling" if small else ""))
    return "Shubhali yozuv yo'q ✓" if not out else "Tekshirish kerak:\n" + "\n".join(out)

def add(o):
        rows = load(); iso = to_iso(o.date); plate, auto = match_plate(o.plate)
        for r in rows:
            if r['date'] == iso and r['plate'] == plate and abs(float(r['kub']) - o.kub) < 0.0005:
                print(f"TAKROR — qo'shilmadi (id {r['id']})"); return
        nid = max([r['id'] for r in rows] or [0]) + 1
        note = "; ".join(x for x in [o.note, auto, kub_warning(plate, o.kub)] if x)
        rows.append({'id': nid, 'date': iso, 'time': o.time, 'plate': plate, 'driver': o.driver, 'kub': o.kub, 'video': o.video, 'note': note})
        save(rows)
        m = [r for r in rows if r['date'][:7] == iso[:7]]
        print(f"Qo'shildi #{nid}: {iso} | {plate} | {o.kub} kub | {round(o.kub*PRICE):,} so'm{(' | '+note) if note else ''}".replace(',', ' '))
        same = [r for r in rows if r['date'] == iso and r['plate'] == plate and r['id'] != nid and plate != '?']
        if same and (o.kub < 60 or any(float(r['kub']) < 60 for r in same)):
            print(f"PAFTOR ehtimoli: shu kuni {plate} yana bor (id {', '.join(str(r['id']) for r in same)}). Bitta zapravka bo'lsa: merge --id <katta> --add <kichik>, keyin del kichigini")
        print(f"Oy bo'yicha: {len(m)} ta, {sum(float(r['kub']) for r in m):.3f} kub")

if __name__ == '__main__':
    main()
