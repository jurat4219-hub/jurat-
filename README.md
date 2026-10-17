# Jurat Assistant bot (@jurat_ish_2026_bot)

Bot fayllari: agentlar, skill'lar va Python dasturlari (akt, qarz, zapravka, pubg).
Ma'lumotlar (bank/faktura bazasi, jurnal, Excel/PDF) va bot tokeni bu yerda SAQLANMAYDI, ular faqat kompyuterda turadi.

## Yangilash (Windows PowerShell)
```
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\jurat-\yangilash.ps1"
```
Keyin bot oynasida `/exit` yozing.

| Papka | Kompyuterdagi joyi |
|---|---|
| `.claude/agents`, `.claude/skills` | `C:\Users\HP\claude-telegram\.claude\...` |
| `ish/akt`, `ish/qarz`, `ish/pubg`, `ish/zapravka`, `ish/skan`, `ish/video` | `C:\Users\HP\claude-telegram\ish\...` |
| `bot/` | `C:\Users\HP\claude-telegram\` |
| `docs/claude_qoshimcha_*.md` | `CLAUDE.md` oxiriga qo'shiladi (bir marta) |

## Chrome yangi varaq (o't animatsiyasi)
`chrome://extensions` → «Режим разработчика» → «Загрузить распакованное» → `C:\Users\HP\jurat-\chrome\yangi-varaq`.
Saytlar ro'yxati: `chrome/yangi-varaq/app.js` (LINKS). Yangilangandan keyin kengaytma kartasidagi ↻ ni bosing.

## Ish stoli foni (jonli o't) va ekran blokirovkasi
- Jonli fon: Microsoft Store → **Lively Wallpaper** (bepul) → «+» → `C:\Users\HP\jurat-\chrome\lively-fon\index.html`.
- Ekran blokirovkasi: Параметры → Персонализация → Экран блокировки → Фото → `chrome\lively-fon\ekran_blokirovka.jpg`.
