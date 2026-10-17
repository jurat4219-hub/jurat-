---
name: bot-qollanma
description: Jurat "nima qila olasan", "qanday ishlatаман", "yordam", "buyruqlar", "/yordam" desa — botning barcha imkoniyatlari va har biri qanday ishga tushirilishini qisqa ro'yxat qilib beradi.
---
# Bot qo'llanmasi (agentsiz, qisqa javob)

Jurat yordam so'rasa — quyidagi jadvalni Telegram'ga yubor (o'zgartirmasdan, faqat so'ralgan bo'limni ham berish mumkin):

| Ish | Nima yuborasiz / yozasiz | Natija |
|---|---|---|
| Akt sverka | `Shafoat bilan akt` (davr aytmasa — to'liq tarix) | PDF + Excel, shartnomalar bo'yicha saldo |
| Bank / faktura yuklash | Bank ko'chirmasi yoki Didox Excel faylini yuboring | Bazaga qo'shiladi |
| Qarz hisobi | `Rustam firmadan 5 tonna sement oldik 12 mln`, `qarz qancha` | Qoldiq, tarix, Excel |
| Zapravka | Zapravka videosi/rasmi; `oylik hisobot`, `sverka` | Jurnal, IYK OTA sverkasi |
| Rasm → PDF | Hujjat rasm(lar)i + `pdf qil` (`rangli`, `oq-qora`) | Skaner sifatidagi PDF |
| Texpasport / ID | Ikki tomon rasmi + `bitta pdf qil` | Ikkala tomon bitta A4 betda |
| Video montaj | Video + `montaj qil` / `reels qil subtitr bilan` | Pauzasiz video, 9:16, subtitr |
| PUBG chust | O'yin videosi + `chust` | Har qurol/pritsel uchun sozlama rasmi |
| Guruh kuzatuvi | `IYK OTA guruhida bugun nima bo'ldi`, `guruh fayllari` | Qisqa xulosa, guruhga kelgan fayllar |
| Musiqa | `Sherali Jo'rayev Bahor top`; `trenddagi qo'shiqlar`; audio/video + `bu qanaqa qo'shiq`; `kompyuterimdagi ... qo'shig'ini yubor`; video + `fon musiqa qo'y` | Havolalar, qo'shiq nomi, audio fayl, musiqali video |
| Shartnoma / hujjat | `... bilan shartnoma tuz`, `pretenziya yoz` | Word + PDF |

Eslatmalar (kerak bo'lsa qo'sh):
- 20 MB dan katta video/fayl Telegram'dan kelmaydi — `C:\Users\HP\Videos\montaj` papkasiga tashlab, nomini yozing.
- Bot kompyuterda ishlaydi: kompyuter o'chsa yoki uxlasa — bot javob bermaydi.
- Yangilash: PowerShell'da `powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\jurat-\yangilash.ps1"`, keyin bot oynasida `/exit`.
