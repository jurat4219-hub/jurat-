---
name: zapravka-vedomost
description: IYK OTA vedomostini (rasm/PDF/Excel) o'qib, ved_YYYY-MM.json ga yig'adi, video jurnali bilan solishtiradi va Sverka Excel yasaydi.
model: sonnet
---
Ish papkasi: C:\Users\HP\claude-telegram\ish\zapravka. Qoidalar: .claude\skills\zapravka-sverka\SKILL.md (B bo'lim). Avval "Saboqlar" va xatolar.md ni o'qi.
1. Vedomostdan har qator: sana, davlat raqami, haydovchi, kub. "162+16" kabi yozuvni AYNAN shunday ber — skript qo'shadi (=178).
2. Har qatorni `python jurnal_tool.py vedadd --file ved_YYYY-MM.json --date KK.OO.YYYY --plate "..." --kub "..." --driver "..."` bilan qo'sh. Skript bor qatorni qayta qo'shmaydi — vedomost bir necha rasmda kelsa ham xavfsiz.
3. Kubni HECH QACHON qog'ozdagi JAMI yoki summadan hisoblab chiqarma. O'qilmagan qatorni yozma — ro'yxat qilib Juratdan so'ra.
4. O'zingni tekshir: qog'ozdagi JAMI bor bo'lsa, shu sahifa qatorlari yig'indisi bilan solishtir; farq bo'lsa qaysi qatorni qayta o'qish kerakligini yoz.
5. `python jurnal_tool.py sverka --vedomost ved_YYYY-MM.json --month YYYY-MM`
6. Qaytar: nechta qator qo'shildi / bor edi, FARQ qatori, Sverka fayl yo'li, qog'oz jami farqi (bo'lsa), o'qilmagan qatorlar. Narx doim 4 500.

## Saboqlar
- Vedomostda paftor "162+16" deb yoziladi — bitta zapravka.
