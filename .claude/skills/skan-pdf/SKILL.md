---
name: skan-pdf
description: Telegram'da kelgan JPG/PNG rasm(lar)ni sifatli skaner PDF ga aylantirish (hujjat, TTN, faktura, shartnoma, pasport). "pdf qil", "skan qil", "pdf ga aylantir" deganda.
---
# Rasm → sifatli PDF (agentsiz, limit tejaladi)

Ish papkasi: `C:\Users\HP\claude-telegram\ish\skan`

1. Kelgan rasm(lar)ning to'liq yo'lini ol (Telegram inbox). Bir nechta rasm bo'lsa — kelgan tartibda bitta PDF.
2. Rejimni tanla:
   - default `skan` — oq-qora skaner (hujjat, TTN, faktura, akt);
   - `rang` — Jurat "rangli", "muhr ko'k qolsin", "imzo rangli" desa;
   - `asl` — foto yoki rasmning o'zi kerak bo'lsa (rang o'zgarmaydi, faqat to'g'rilanadi).
3. Ishga tushir:
   `python skan_tool.py pdf "<rasm1>" "<rasm2>" --rejim skan --chiqish "C:\Users\HP\claude-telegram\ish\skan\<Nom>.pdf"`
   Nom: hujjat turidan (masalan `TTN_17102026.pdf`); bilmasang default nom qoladi.
4. PDF faylni Telegram'ga yubor. Javob bir qator: "PDF tayyor: N bet, <rejim>".
5. Chiqishda "chet topilmadi" bo'lsa — PDF baribir yasaladi; faqat qo'shimcha: "Varaq chetlari ko'rinmadi — keyingi safar varaqni to'q fonda, to'liq suratga oling."

Qoidalar: rasmni o'zing ko'rib chizma, matnni qayta terma — faqat dastur. Agent ochma (oddiy ish). Asl rasmlarni o'chirma.
