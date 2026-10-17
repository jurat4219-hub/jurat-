---
name: skan-pdf
description: Telegram'da kelgan JPG/PNG rasm(lar)ni sifatli skaner PDF ga aylantirish (hujjat, TTN, faktura, shartnoma, pasport). "pdf qil", "skan qil", "pdf ga aylantir" deganda.
---
# Rasm → sifatli PDF (agentsiz, limit tejaladi)

Ish papkasi: `C:\Users\HP\claude-telegram\ish\skan`

1. Kelgan rasm(lar)ning to'liq yo'lini ol (Telegram inbox). Bir nechta rasm bo'lsa — kelgan tartibda bitta PDF. Bitta rasmni ikki marta berma (dastur takrorni o'zi tashlaydi, lekin baribir).
2. Rejimni tanla (odatda `--rejim` BERMA — default `avto`: ko'k/qizil muhr yoki imzo bo'lsa rangli, bo'lmasa oq-qora):
   - `skan` — Jurat "oq-qora" desa;
   - `rang` — Jurat "rangli", "muhr ko'k qolsin", "imzo rangli" desa;
   - `asl` — foto yoki rasmning o'zi kerak bo'lsa (rang o'zgarmaydi, faqat to'g'rilanadi).
3. Ishga tushir:
   `python skan_tool.py pdf "<rasm1>" "<rasm2>" --chiqish "C:\Users\HP\claude-telegram\ish\skan\<Nom>.pdf"`
   Nom: hujjat turidan (masalan `TTN_17102026.pdf`); bilmasang default nom qoladi.
4. PDF faylni Telegram'ga yubor. Javob bir qator: "PDF tayyor: N bet, <rejim>".
5. Chiqishda "chet topilmadi" bo'lsa — PDF baribir yasaladi; faqat qo'shimcha: "Varaq chetlari ko'rinmadi — keyingi safar varaqni to'q fonda, to'liq suratga oling."

Qoidalar: rasmni o'zing ko'rib chizma, matnni qayta terma — faqat dastur. Agent ochma (oddiy ish). Asl rasmlarni o'chirma.

## Karta rejimi (texpasport, ID karta, guvohnoma, prava)
Jurat karta suratlarini (odatda old + orqa) yuborib "bitta pdf", "ketma-ket", "ikkovi bitta betda", "texpasport pdf" desa, yoki rasmlarda kichik karta bo'lsa:
`python skan_tool.py karta "<old>" "<orqa>" --chiqish "C:\Users\HP\claude-telegram\ish\skan\Texpasport_<raqam yoki sana>.pdf"`
- Ikkala tomon BITTA A4 betda: birinchi berilgan tepada. Old tomon (gerb, "GUVOHNOMA", davlat raqami) birinchi bo'lsin — kelgan tartib teskari bo'lsa almashtir.
- "haqiqiy o'lchamda", "asl o'lcham" → `--olcham asl` (86 mm). Default katta (o'qish oson).
- 4 ta rasm = 2 bet (har betda 2 tadan).
