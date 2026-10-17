---
name: video-montaj
description: Telegram'da kelgan videoni avto-montaj qilish — pauza/jimlik va bo'sh joylarni kesish, ovozni -14 LUFS ga keltirish, Reels/TikTok uchun 9:16, subtitr. "montaj qil", "pauzalarni kes", "reels qil", "subtitr qo'y" deganda.
---
# Video avto-montaj (agentsiz)

Ish papkasi: `C:\Users\HP\claude-telegram\ish\video`

1. Video yo'lini ol (Telegram inbox). Telegram botlar 20 MB dan katta faylni yuklay olmaydi — video kelmasa:
   "Video 20 MB dan katta. Uni kompyuterdagi `Videolar\montaj` papkasiga tashlang va nomini yozing" de; keyin `C:\Users\HP\Videos\montaj\<nom>` dan ol.
2. Buyruq (Jurat so'ziga qarab parametr):
   `python video_tool.py montaj "<video>" [--format reels] [--subtitr ha] [--til uz|ru]`
   - "reels", "tiktok", "shorts", "vertikal" → `--format reels`
   - "subtitr", "yozuv" → `--subtitr ha` (til aytilmasa auto; o'zbekcha bo'lsa `--til uz`)
   - "ko'proq kes" → `--sukut 0.25`; "kamroq kes", "tabiiy" → `--sukut 0.7`; shovqinli joy → `--porog -30`
3. Chiqishdagi hisobot qatorini Juratga yubor (asl → montaj soniya, nechta bo'lak, LUFS) va videoni yubor.
   Fayl 49 MB dan katta bo'lsa — Telegram bot yubora olmaydi: faylning to'liq yo'lini ayt.
4. Subtitr bo'lsa .srt faylni ham yubor (Jurat xatosini tuzatib qayta yuborishi mumkin: "subtitrni shu .srt bilan qo'y" → ffmpeg subtitles bilan qayta yoz).

Qoidalar: asl videoni o'chirma va ustidan yozma. Videoni o'zing "ko'rib" kadrma-kadr tahlil qilma — limit ketadi; faqat dastur.
