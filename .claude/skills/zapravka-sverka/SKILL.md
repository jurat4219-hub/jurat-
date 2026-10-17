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
- Davlat raqamini ish\zapravka\IYK_OTA_mashinalar.xlsx ro'yxatidan tanla (skript o'zi 1 belgi farqni tuzatadi, O/0 chalkashligini to'g'rilaydi).
- Raqam ko'rinmasa — --plate "?" bilan yoz va Juratdan so'ra.

## Bir martalik tayyorgarlik
Python yo'q bo'lsa: `winget install Python.Python.3.12`, keyin `python -m pip install openpyxl`.
Eski o'zing yasagan jurnal fayllaridan (jurnal_2026-10.xlsx va h.k.) FOYDALANMA — faqat jurnal_data.json.

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
- Noto'g'ri yozuv: `list --month YYYY-MM` → id → `del --id N` → qayta add → build.
- Jurat tuzatsa: xatolar.md ga qator + shu faylning "Saboqlar"iga qoida.

## Saboqlar
- 15.10.2026: Narx doim 4500. Paftor = bitta zapravka. Displeysiz videoni yozma.
