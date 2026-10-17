
## 11. LIMITNI TEJASH (majburiy, §10 dan ustun)
Har bir agent va har bir qayta tekshiruv Juratning Claude limitidan yeydi. Shuning uchun:
- Oddiy savol, salomlashish, holat so'rash, bitta raqam — agentsiz, o'zing qisqa javob ber.
- Tayyor Python buyrug'i bor ishlar (qarz kirim/to'lov/qoldiq, jurnal qo'shish/summary, akt) — buyruqni o'zing bevosita ishga tushir, natijani yubor. Agent ochma.
- Akt: `akt_tool.py akt ...` dan keyin `akt_tool.py tekshir ...` ni o'zing ishga tushir. akt-tekshiruvchi agentini FAQAT tekshir muammo ko'rsatsa yoki Jurat raqami farq qilsa chaqir.
- Tekshiruvchi agent faqat: yangi hujjat (shartnoma, pretenziya), video tahlil, katta sverka. Ko'pi bilan 1 marta qayta tuzatish.
- Fayllarni to'liq o'qima: Excel/PDF dan faqat kerakli qatorlarni Python bilan chiqar. Katta jadvallarni chatga chiqarma.
- Javoblar qisqa: natija + fayl + bitta "✓/⚠" qatori.
