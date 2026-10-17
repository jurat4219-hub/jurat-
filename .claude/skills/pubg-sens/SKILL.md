---
name: pubg-sens
description: PUBG Mobile o'yin videolarini ko'rib qurol, pritsel (kollimator/2x/3x/4x/6x/8x), zajim (spray), boshga tekkan o'qlar va videoda ko'rsatilgan sensitivity sozlamalarini yig'ish, har qurol va pritsel uchun chust chiqarish. PUBG videosi, "chust", "sens", sozlama skrinshoti yoki kod kelganda ishlat.
---
# PUBG Mobile chust tahlili (video → har qurol × pritsel sozlamasi)

Faqat o'yin ichidagi Sensitivity sozlamalari va layout kodlari. Cheat/hack/makro/ESP/aimbot — HECH QACHON.
Ish papkasi: ish\pubg. Hamma yozuv FAQAT `python pubg_tool.py ...` orqali (baza: pubg_baza.json).
Juratning sozlamasi: mening_sozlamam.md (o'zgarsa yangila).

## 1. Video keldi — to'liq ko'rib chiq
1. Video ID ber (v1, v2, ... — `pubg_tool.py list` dan keyingisi). Caption va forward manbasidan: kod, FPS, giro, rejim.
   `python pubg_tool.py video --id vN --manba ".." [--kod ..] [--fps 120] [--giro ha] [--rejim TDM]`
2. Butun videodan kadr: `ffmpeg -i video -vf fps=2,scale=1000:-1 k_%04d.jpg`. Hammasini ko'zdan kechir (ko'p bo'lsa 4 tadan birlashtirib — `ffmpeg ... -vf "fps=2,scale=500:-1,tile=2x2"`).
3. SOZLAMA EKRANI ko'rinsa (Settings → Sensitivity: Kamera / ADS / Giroskop / Giroskop ADS ro'yxati) — o'sha joyni `fps=6` bilan qayta ajrat va HAR BIR foizni o'qib yoz:
   `python pubg_tool.py sozlama --id vN --bolim ads --qator 3x --qiymat 31 [--qurol M416]`
   bolim (o'yindagi bo'lim): kamera = Чувствительность камеры | ads = Чувствительность прицела | giro = Чувствительность гироскопа | giroads = Чувствительность гироскопа ADS
   qator (o'yindagi qator): 3l = 3-е лицо (без прицела) | 1l = 1-е лицо (без прицела) | p3 = Прицел (3-е лицо) | p1 = Прицел (1-е лицо) | kol = Коллиматорный, голографический, мушка и боковой | 2x | 3x (Win94) | 4x (ВСС) | 6x | 8x
   Ba'zi o'yinchilar har qurol uchun alohida sozlama ko'rsatadi — unda --qurol bilan yoz.
   Raqam aniq o'qilmasa — yozma, Juratga "qaysi soniyada, nima ko'rinmadi" de.
4. OTISH EPIZODLARI: har bir otish joyini top (o'q chiqishi, o'q soni kamayishi). Shu 2-4 soniyani `fps=8` bilan ajrat va aniqla:
   - QUROL — ekranning pastki o'ng qismidagi qurol nomi/rasmi (M416, AKM, Beryl, UMP, Mini14, SKS, M24, Kar98 ...)
   - PRITSEL — PRITSELSIZ (bez pritsel, hip-fire: ekranda faqat to'r/krest, kattalashtirish yo'q) yoki ko'rinishidan: kollimator (qizil nuqta), golografik, 2x, 3x, 4x, 6x, 8x (ramka va kattalashtirish bo'yicha)
   - ZAJIM — tugma bosib turilib ketma-ket otildimi (spray) yoki bir-bir
   - MASOFA — taxminan (nishon kattaligi / xarita)
   - HEADSHOT — boshga tegishi: qizil/sariq hit-marker boshda, nishon boshidan qon, kill-feed'dagi headshot belgisi, "Headshot" yozuvi. Nechta o'q boshga, nechta tanaga.
   - SILJISH — zajimda pritsel markazi: tepaga ketdi | pastga | chap-ung | barqaror
   `python pubg_tool.py otish --id vN --qurol M416 --pritsel 3x --zajim ha --masofa 60 --headshot 4 --tegdi 9 --uq 25 --siljish tepaga --vaqt 0:12`
   PRITSELSIZ otishda: `--pritsel pritselsiz`. Bunda boshga tegishlarni ALOHIDA diqqat bilan sana — bez pritsel boshga otish Kamera va Giroskop (1-lico/3-lico) foizlariga bog'liq; videoda shu bo'limlar sozlamasi ko'rinsa albatta yoz (`--bolim kamera --qator 3l`, `--bolim giro --qator 3l`, `--qator 1l` va h.k.).
   Bu ko'z bilan baho — taxminiy ekanini Juratga ayt.
5. Natija: `python pubg_tool.py hisobot` (shu video qatori) + `python pubg_tool.py chust`.

## 2. Juratga javob — O'YIN EKRANI KO'RINISHIDA
ASOSIY natija — RASM: `python pubg_tool.py chust --qurol M416 --rasm` → chust_*.png ni Telegram'ga FAYL qilib yubor.
Rasm o'yindagi "Продвинутые настройки → Чувствительность" ekrani kabi: o'sha bo'limlar, o'sha ruscha nomlar, o'sha tartib, foiz + slayder. O'zgargan qatorda "было X%" va +/− farq.
Matnda ham FAQAT o'yindagi ruscha nomlarni ishlat (masalan "Чувствительность прицела → Прицел 3×, Win94: 31% → 35%"), o'zbekcha tushuntirish qisqa.
Juratning o'z sozlamasi rasmi: `python pubg_tool.py rasm --qurol M416 --meniki`.

1. KOD (bo'lsa) — alohida qatorda.
2. Videoda nima ko'rindi (PRITSELSIZ otish va undagi headshotlar alohida qatorda): qaysi qurollar, qaysi pritsellar, nechta zajim, nechta headshot (qaysi soniyada), sozlama ekrani bormi.
3. HAR QUROL × PRITSEL jadvali (chust buyrug'i natijasi): tavsiya foiz + sizdagi qiymat + farq.
4. Ma'lumot yo'q pritsellar ro'yxati — "shu pritsel bilan otilgan yoki sozlamasi ko'ringan video yuboring".
5. Sinov mashqi: Trenirovka → shu qurol + pritsel → 50 m nishonga zajim → pritsel tepaga ketsa ADS +5%, pastga tushsa −5%.
6. Qo'yish: Settings → Sensitivity → Share/Cloud → Use layout code → Apply (oldin o'zingiznikini kodga saqlang).
Excel so'ralsa: `python pubg_tool.py excel` → PUBG_chust.xlsx yubor.

## 3. Buyruqlar (Telegram)
- "chust" / "chust M416" → `chust [--qurol M416]`
- "pubg hisobot" → `hisobot`;  "pubg excel" → `excel`
- "mening chustim" → `rasm --qurol M416 --meniki` rasmini yubor.
- Jurat o'z sozlama skrinshotlarini yuborsa → har qiymatni `python pubg_tool.py meniki --bolim .. --qator .. --qiymat ..` bilan yangila va mening_sozlamam.md ni ham yangila.
- Jurat yangi sozlamani qo'ysa yoki foizlarni aytsa — xuddi shunday meniki bilan yangila.

## Saboqlar
- (hozircha yo'q)
