---
name: akt-sverka
description: Ikki kompaniya o'rtasida akt sverka (АКТ СВЕРКИ ВЗАИМНЫХ РАСЧЕТОВ) tuzish — bank ko'chirmasi va fakturalardan, faqat ish\akt\akt_tool.py orqali. "akt sverka", "sverka", "solishtirma", bank ko'chirmasi yoki Didox eksporti kelganda ishlat.
---
# Akt sverka (faqat akt_tool.py)

Akt sverka Excel'ini O'ZING YASAMA — faqat `ish\akt\akt_tool.py`. Format doim bir xil: Times New Roman, A4 albom,
ikki tomonlama (bizning va kontragent ma'lumotlari) Дебет/Кредит, Сальдо начальное / Обороты / Сальдо конечное SUM formulalari,
summa so'z bilan, ikki tomon imzo bloklari. Baza: akt_baza.json (bank va fakturalar to'planib boradi).

## 0. TOKEN TEJASH — muhim
Bank ko'chirmasi va faktura fayllarini O'ZING OCHMA va O'QIMA (Read, openpyxl bilan ko'rish, rasmga aylantirish — yo'q).
Faylni yuklab ol va darhol skriptga ber: skript o'zi faqat kerakli qatorlarni (faktura sarlavha qatori: СТАТУС, raqam, sana,
INN, jami) oladi, tovar qatorlarini o'qimaydi. Juratga faqat skript chiqargan 2-3 qatorni yubor.

## 1. Ma'lumot yuklash (fayl kelganda)
- Bank ko'chirmasi (Xalq banki HTML/CP1251, xlsx, csv): `python akt_tool.py bank --biz TSB --file "<fayl>"`
  Qaysi kompaniyaniki (TSB/TLT/RAYXONA) — fayldagi hisob raqami/STIRdan aniqla, aniq bo'lmasa so'ra.
- Didox / Soliq servis eksporti: `python akt_tool.py faktura --biz TSB --file "<fayl>"`
  Skript o'zi: faqat "Подписан"; Отказ/Отменен/Ожидает, nol summa, twin "Не настоящий", tuzatuvchi bilan almashtirilganlar tashlanadi;
  "Tekshiruv: fayldagi N = qo'shildi + takror + tashlandi ✓" qatorini Juratga ko'rsat. ✗ bo'lsa — to'xta, sababini top.
  "SUMMA YOZILMAGAN" bor bo'lsa (eski fakturalarda eksportda summa bo'lmaydi) — Juratga ayt; akt so'ralganda shu kontragent
  bo'yicha bunday faktura bo'lsa, ro'yxatini (`tashlangan --stir ..`) ko'rsatib summalarini so'ra va `qator --tur oldik|sotdik` bilan qo'sh.
  "Без оплаты" fakturalar aktga kirmaydi.
- Takrorlar avtomatik o'tkaziladi — bir xil faylni qayta yuklash xavfsiz. Har oy yangi ko'chirmalarni yuklab boring.
- Qo'lda qator (masalan avvalgi yildan qolgan hujjat): `qator --biz TSB --stir .. --date .. --tur sotdik|oldik|toladik|toladi --summa .. --hujjat ..`

## 2. Akt yasash — akt-sverka AGENTI bajaradi (dispetcher darhol agentga beradi, o'zi savol bermaydi)
Standart: davr aytilmasa — to'liq tarix (birinchi operatsiyadan bugungacha, `akt --biz .. --stir ..` davrsiz).
Natijada doim: umumiy saldo (hamma to'lov va fakturalar) + shartnomalar bo'yicha jadval. Shartnoma raqami aytilsa — `--shartnoma`.
Quyidagi qadamlar agent uchun ma'lumot:
1. Kontragent STIRini top: `python akt_tool.py kontragentlar --biz TSB --qidir "bo'ston"`.
2. Kerak: davr (dan–gacha), boshlang'ich saldo (bilmasang — so'ra; bazada oldingi davr bo'lsa skript o'zi hisoblaydi), shartnoma raqami (bo'lsa).
3. `python akt_tool.py akt --biz TSB --stir 301234567 --dan 01.01.2026 --gacha 30.09.2026 [--saldo 0] [--shartnoma 22-ГБ-2026] [--nom "ООО \"...\""]`
4. Skript Excel va PDF yasaydi. Juratga PDF FAYLni (asosiy) va Excel faylni birga yubor + Saldo/Debet/Kredit va Natija qatorlarini.
   "PDF yasalmadi" desa — faqat Excel yubor va sababini ayt.
   "Diqqat: N ta faktura tashlangan" bo'lsa — `tashlangan --stir ..` ro'yxatini ham ko'rsat.
5. Katta summa yoki yangi kontragent bo'lsa — yuborishdan oldin tekshiruvchi agentiga ber (manba fayllar + akt).

## Qoidalar
- Bizning tomondan: sotdik (bizning faktura) va to'ladik (biz o'tkazdik) = Дебет; oldik (ularning fakturasi) va to'ladi (ular o'tkazdi) = Кредит.
  Kontragent tomoni — oynadek (skript o'zi qiladi). Saldo + = kontragent bizga qarz, − = biz qarzmiz.
- TSB va TEMUR TEXNIK TRANS — bitta korxona (STIR 307669546). Kompaniyalarni hech qachon aralashtirma.
- Bizning rekvizitlar, direktor, bosh buxgalter: ish\akt\firmalar.json (Jurat aytsa yangila).

## Telegram buyruqlari
- "akt TSB bo'stonliq 01.01.2026-30.09.2026" → yuqoridagi 2-bo'lim
- "akt baza" / "akt holat" → `holat` (qaysi kompaniya bo'yicha qaysi oylar yuklangan)
- "kontragentlar TSB" → `kontragentlar --biz TSB`

## Saboqlar
- (hozircha yo'q)
