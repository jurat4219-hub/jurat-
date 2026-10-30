# Jurat Yordamchi — Windows Desktop AI Agent (MVP, 1-bosqich)

Siz ishga tushirganingizda ekranni ko'rib, OCR + Claude bilan tushunadigan, xato va
maslahat beradigan yordamchi. **Doimiy fon kuzatuvi YO'Q** — faqat «Ekranni ko'r» bosganda qaraydi.

## 1-bosqich (hozir)
- Ekranni suratga olish (butun ekran yoki faqat faol oyna)
- OCR (Tesseract, rus+eng) — Excel, Word, PDF, 1C matnini o'qiydi
- Claude Pro (Claude Code CLI, `claude -p`) orqali tahlil — qo'shimcha to'lov yo'q
- Xato topish, maslahat, qadamlar rejasi (o'zbek lotin)
- Xotira va jurnal (SQLite: agent_xotira.db)
- Ko'rinadigan holat indikatori, Pauza, Stop

## Sichqoncha/klaviatura bilan amal bajarish
`amal.py` da, hozircha **O'CHIQ** (YOQILGAN=False). 2-bosqichda, har amal uchun
tasdiq oynasi bilan yoqamiz.

## O'rnatish (bir marta)
1. Python 3.12+ bo'lishi kerak: `python --version`. Yo'q bo'lsa: `winget install Python.Python.3.12`
2. Tesseract OCR: `winget install UB-Mannheim.TesseractOCR`
   (rus tili uchun o'rnatishda "Russian" ni belgilang; yoki keyin til paketini qo'shing)
   O'rnatilgach odatda: C:\Program Files\Tesseract-OCR\tesseract.exe
3. Claude Code CLI o'rnatilgan va Pro bilan kirgan bo'lishi kerak (`claude --version`).

## Ishga tushirish
`agent` papkasidagi **boshla.bat** ni ikki marta bosing. Birinchi marta kutubxonalarni o'rnatadi.

## EXE qilish (ixtiyoriy)
```
python -m pip install pyinstaller
pyinstaller --noconsole --onefile --name "JuratYordamchi" yordamchi.py
```
Natija: dist\JuratYordamchi.exe. (Tesseract va Claude CLI baribir alohida o'rnatilgan bo'lishi kerak.)

## Xavfsizlik
- Parol/EIMZO terilayotganda ishlatmang — yordamchini faqat ish (Excel/1C/hujjat) paytida chaqiring.
- Suratlar `suratlar\` papkasida saqlanadi; kerakmas bo'lsa o'chirib turing.
- Amal bajarish o'chiq; yoqilганда ham har amal tasdiq so'raydi.
