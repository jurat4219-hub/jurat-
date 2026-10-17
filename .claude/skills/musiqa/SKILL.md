---
name: musiqa
description: Jurat qo'shiq so'rasa ("... qo'shig'ini top", "havola ber"), audio/video yuborib "bu qanaqa qo'shiq", "qo'shiqni aniqla" desa, "kompyuterimdagi ... qo'shig'ini yubor" desa yoki videoga "fon musiqa qo'y" desa ishlaydi. Faqat qonuniy yo'llar.
---
# Musiqa (agentsiz, qisqa javob)

Dastur: `C:\Users\HP\claude-telegram\ish\musiqa\musiqa_tool.py` (quyida `M`).

## 1. Havola — "Sherali Jo'rayev Bahor top", "... havola ber"
`python M havola "<ijrochi va nom>"` → chiqqan havolalarni Telegram'ga yubor (YouTube Music birinchi).
Aniqroq kerak bo'lsa WebSearch bilan bitta aniq trek havolasini top. MP3 yuklab berma.

## 2. Aniqlash (Shazam kabi) — audio/ovozli xabar/video + "bu qanaqa qo'shiq"
`python M aniqla "<fayl yo'li>"` (o'zi 0, 30, 60-soniyadan sinaydi; Jurat "1 daqiqadan keyin" desa `--dan 60`).
Natijani (ijrochi — nom, albom, havolalar) yubor. "AUDD_TOKEN yo'q" chiqsa — Juratga 3-bo'limdagi sozlashni qisqa ayt.

## 3. O'z kutubxonasidan — "kompyuterimdagi Yulduz Usmonova qo'shig'ini yubor"
1. Birinchi marta yoki "musiqani yangila" desa: `python M kutubxona` (Music va Downloads). Boshqa papka aytsa: `--papka "D:\Musiqa"`.
2. `python M qidir "<so'zlar>"` → eng mos 1-faylni Telegram'ga AUDIO fayl qilib yubor. Bir nechta mos bo'lsa — ro'yxatni 5 tagacha ko'rsatib, raqam so'ra.
3. 50 MB dan katta fayl Telegram'ga sig'maydi — shuni ayt.
Faqat Juratning shaxsiy foydalanishi uchun; guruhlarga yoki boshqalarga tarqatma.

## 4. Fon musiqasi — video + "fon musiqa qo'y" (yoki "montaj qil musiqa bilan")
Montaj ham so'ralsa avval video-montaj skilini bajar, keyin natijaga:
`python M fon "<video>" [--musiqa "<fayl>"|avto] [--baland 0.18]` ("musiqa balandroq" → 0.3, "pastroq" → 0.1).
Treklar `C:\Users\HP\Videos\montaj\fon_musiqa` dan olinadi (mualliflik huquqisiz). Papka bo'sh bo'lsa — Juratga
YouTube Audio Library yoki Pixabay Music'dan yuklab, shu papkaga tashlashni ayt.

## Bir martalik sozlash (aniqlash uchun)
1. Brauzerda https://dashboard.audd.io → ro'yxatdan o'tish → "API Token" ni nusxalash.
2. Bloknotda yozing: `AUDD_TOKEN=<token>` → «Сохранить как» → «Имя файла»: `C:\Users\HP\claude-telegram\ish\musiqa\.env`, «Тип файла»: «Все файлы».
Tokenni hech qachon Telegram chatga yozdirma va omborga qo'yma.

## Qilma
VK, Telegram musiqa kanallari yoki pirat saytlardan qo'shiq yuklab berma — so'rasa, havola (1-bo'lim) taklif qil.
