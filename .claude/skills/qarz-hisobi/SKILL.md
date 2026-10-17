---
name: qarz-hisobi
description: Ta'minotchi firmalardan olingan mahsulotlar va ularga o'tkazilgan to'lovlarni yuritib, har firma bo'yicha qolgan qarzni, nima va qachon olinganini ko'rsatish. Kirim, to'lov, faktura, nakladnoy, bank ko'chirmasi yoki "qarz" so'ralganda ishlat.
---
# Ta'minotchilar bilan qarz hisobi

Biz firmalardan mahsulot olamiz (KIRIM — qarzimiz oshadi) va pul o'tkazamiz (TO'LOV — qarz kamayadi).
QOLDIQ = boshlang'ich qoldiq + jami kirim − jami to'lov. Musbat = biz qarzmiz, manfiy = ularga avans berganmiz.
Hamma yozuv FAQAT `ish\qarz\qarz_tool.py` orqali. Takror yozuv avtomatik rad etiladi.

## Qat'iy qoidalar
- Summani taxmin qilma. Miqdor va narx bo'lsa skript summani o'zi hisoblaydi; hujjatda summa boshqacha bo'lsa — --summa bilan hujjatdagini yoz va DIQQATni Juratga ayt.
- QQS bilan jami summa yoziladi (hujjatdagi "Всего с НДС"), alohida ko'rsatilmasa.
- Firma nomini skript mavjud ro'yxatdan topadi. "YANGI FIRMA" chiqsa — Juratga "yangi firma qo'shildi: ..." deb ayt (imlo xatosi bo'lsa del qilib qayta yoz).
- Rad etilgan / bekor qilingan / nol fakturani yozma (Didox: faqat "Подписан").
- Bank ko'chirmasidan faqat SHU firmaga chiqqan to'lovlar (kredit emas, bizdan chiqqan) olinadi.
- Birinchi marta firma qo'shilganda Juratdan so'ra: "Bu firma bilan oldingi qoldiq (boshlang'ich qarz) bormi, qaysi sanadan?" → `boshlangich`.

## Buyruqlar (ish\qarz papkasida)
- `python qarz_tool.py kirim --firma ".." --date KK.OO.YYYY --mahsulot ".." --miqdor N --birlik t --narx N [--summa N] [--hujjat ".."] [--biz TSB]`
- `python qarz_tool.py tolov --firma ".." --date KK.OO.YYYY --summa N [--hujjat "p/p 112"]`
- `python qarz_tool.py boshlangich --firma ".." --date 01.10.2026 --summa N`
- `qarz` | `tarix --firma .. [--dan ..] [--gacha ..]` | `mahsulot --firma ..` | `list` | `del --id N` | `excel [--firma ..]`
- Ko'p qator (faktura, Didox eksport, bank ko'chirmasi): JSON yasab `import --file yozuvlar.json`
  `[{"tur":"kirim","firma":"..","date":"16.10.2026","mahsulot":"..","miqdor":2.5,"birlik":"t","narx":8500000,"summa":21250000,"hujjat":"Faktura 45"},{"tur":"tolov","firma":"..","date":"..","summa":10000000,"hujjat":"p/p 112"}]`

## Hujjat keldi
1. Faktura / nakladnoy rasmi yoki PDF: har mahsulot qatori = bitta kirim (mahsulot, miqdor, birlik, narx, summa, hujjat raqami, sana). Qatorlar yig'indisini hujjatdagi JAMI bilan solishtir.
2. Didox eksport (XLS): kiruvchi, "Подписан", 36-ustun jami → har faktura bitta kirim (mahsulot nomi bo'lsa — qatorlab).
3. Bank ko'chirmasi (Xalq banki HTML, CP1251): bizdan chiqqan to'lovlar → tolov.
4. Import qil → `qarz` natijasini va o'zgargan firmalar qoldig'ini Juratga yubor.

## Juratga javob
Qisqa: nima qo'shildi + firma qoldig'i. "Qarz" so'ralsa — firma bo'yicha ro'yxat, eng katta qarz tepada, JAMI pastda. Excel so'ralsa — `excel` faylini yubor.

## Saboqlar
- (hozircha yo'q)
