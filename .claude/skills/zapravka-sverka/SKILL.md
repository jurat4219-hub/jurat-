---
name: zapravka-sverka
description: IYK OTA (metan) zapravka videolaridan oylik jurnal yuritish va zapravka vedomosti bilan solishtirib, oy bo'yicha qancha ortiqcha kub yozilganini chiqarish. Video, doira-video, zapravka rasmi yoki vedomost yuborilganda ishlat.
---
# Zapravka sverkasi (IYK OTA, metan)

Maqsad: zapravka bir oyda vedomostga o'zidan qancha kub qo'shayotganini topish.
BARCHA Excel fayllar FAQAT `ish\zapravka\jurnal_tool.py` orqali yasaladi — o'zing boshqa formatda jadval yasama. Format Jurat tasdiqlagan IYK_OTA_mashinalar.xlsx bilan bir xil.

## Qat'iy qoidalar
- NARX DOIM 4 500 so'm/kub. Kolonka ekranidagi narx (5 600 va h.k.) va summa — BIZ UCHUN EMAS, ularni o'qima ham, yozma ham.
- Videodan faqat IKKI narsa kerak: **KUB** (kolonkaning PASTKI qatori, masalan 186.041) va **DAVLAT RAQAMI**. Tepadagi qator (summa) — e'tibor berma.
- Kubni taxmin qilma, summadan hisoblab chiqarma. O'qilmagan xona bo'lsa — o'qilganini yoz va --note bilan "videoni tekshiring" deb belgila.
- Davlat raqami: faqat O'RTADAGI 3 XONA o'qilsa ham yetarli ("540" → 01 540 UMA, "696" → 01 696 OMA). --plate "540" deb ber, skript IYK_OTA_mashinalar.xlsx dan to'lig'ini topadi; harf xato bo'lsa ham 3 xona bo'yicha tuzatadi.
- Raqam ko'rinmasa — --plate "?" bilan yoz va Juratdan so'ra.

## Bir martalik tayyorgarlik
Python yo'q bo'lsa: `winget install Python.Python.3.12`, keyin `python -m pip install openpyxl`.
Eski o'zing yasagan jurnal fayllaridan (jurnal_2026-10.xlsx va h.k.) FOYDALANMA — faqat jurnal_data.json.

## 0. KO'P VIDEO (2 tadan ko'p) — qotib qolmaslik tartibi
1. Darhol Telegram'ga: "N ta video qabul qilindi, ishlayapman" (bitta qisqa xabar). Videolarni o'zing OCHMA.
2. Hammasini yuklab ol (download_attachment) → `ish\zapravka\video\<YYYY-MM-DD>\`. Yuklanmaganini (20 MB dan katta) sanab qo'y.
3. `python navbat.py kadr --oqim 10 "ish\zapravka\video\<YYYY-MM-DD>"` — barcha kadrlar bir necha soniyada tayyor.
4. Har OK qator uchun bitta `zapravka-video` agenti: BITTA xabarda hammasini birdan, `run_in_background: true` bilan (bir vaqtda 10 tagacha; ko'p bo'lsa 10 tadan to'lqin). Har agentga: video yo'li, kadr.jpg yo'li, sana, vaqt, forward nomi.
5. Agentlar ishlayotganda yangi xabarlarga javob berishda davom et (kutib o'tirma).
6. Hammasi tugagach: `python jurnal_tool.py check --month YYYY-MM` + `summary --day KK.OO.YYYY` → Juratga BITTA umumiy javob: nechta yozildi, qaysilari "?"/xato, yuklanmaganlar ro'yxati.

## A. Video/rasm keldi (zapravka-video agenti bajaradi)
1. download_attachment → ish\zapravka\video\<YYYY-MM-DD>_vN.mp4
2. `python kadr.py "<video>"` → 2 rasm; kubni IKKI rasmdan o'qib solishtir.
3. `python jurnal_tool.py add --date KK.OO.YYYY --time SS:DD --plate "01 696 OMA" --kub 186.041 --video <fayl> [--note "..."]`
   Skript o'zi: takrorni rad etadi, raqamni ro'yxatdan tuzatadi, kub odatdan katta/kichik bo'lsa ogohlantiradi, PAFTOR ehtimolini aytadi.
4. PAFTOR (katta + darhol kichik, bir xil mashina, ≤30 daqiqa): `merge --id <katta> --add <kichik>` → `del --id <kichik>`.
5. Juratga QISQA javob (skript qatorlari + ogohlantirish). Excel faqat so'ralsa yoki kun oxirida.

## B. Vedomost keldi (zapravka-vedomost agenti)
1. Har qator: `python jurnal_tool.py vedadd --file ved_YYYY-MM.json --date KK.OO.YYYY --plate "..." --kub "162+16" --driver "..."`
   "162+16" → 178 (paftor). Bor qator qayta qo'shilmaydi — vedomost bo'lib-bo'lib kelsa ham xavfsiz.
2. Kubni qog'oz JAMIdan chiqarma; o'qilmagan qatorni so'ra.
3. `python jurnal_tool.py sverka --vedomost ved_YYYY-MM.json --month YYYY-MM` → Sverka_YYYY-MM.xlsx
   Varaqlar: Xulosa | Farq bor | Faqat vedomostda | Faqat bizda | Mos keldi | Mashina bo'yicha | Kun bo'yicha.
4. Juratga: FARQ qatori (kub va so'm) + fayl. "Faqat vedomostda" ko'p bo'lsa: "bu qatorlarning videosi yo'q — har zapravka videoga olinganmi?"

## Hisobot va tekshiruv buyruqlari
- `summary --day KK.OO.YYYY` / `summary --month YYYY-MM` — matnli jami (mashina bo'yicha).
- `check --month YYYY-MM` — "?" raqamlar, izohlilar, bir kunda 2 marta (paftor ehtimoli). Hisobotdan oldin ALBATTA.
- `history` — har mashinaning odatiy kub oralig'i (min/o'rtacha/max).
- `build --month YYYY-MM` — Zapravka_jurnal_YYYY-MM.xlsx.

## Tuzatish
- Raqamsiz ("?") yoki noto'g'ri raqamli yozuvga raqam qo'yish: `python jurnal_tool.py setplate --id N --plate "540"` (yoki to'liq raqam). Jurat "69-chisi 861" desa ham shunday.
- Noto'g'ri yozuv: `list --month YYYY-MM` → id → `del --id N` → qayta add → build.
- Jurat tuzatsa: xatolar.md ga qator + shu faylning "Saboqlar"iga qoida.

## Saboqlar
- 15.10.2026: Narx doim 4500. Paftor = bitta zapravka. Displeysiz videoni yozma.
