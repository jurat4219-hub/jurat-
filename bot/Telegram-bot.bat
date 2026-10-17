@echo off
title Telegram bot - Claude (YOPMANG!)
cd /d C:\Users\HP\claude-telegram
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\HP\claude-telegram\bot_tekshir.ps1"
if errorlevel 1 (
  echo Bot allaqachon ishlayapti. Ikkinchi nusxa kerak emas - bu oyna 5 soniyada yopiladi.
  timeout /t 5 /nobreak >nul
  exit
)
start "" /min powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\Users\HP\claude-telegram\awake.ps1"
:loop
echo [%date% %time%] Bot ishga tushmoqda >> bot_log.txt
claude "Telegram chat 7993263197 ga bitta qisqa xabar yubor: Bot ishga tushdi. Bot o'chiq paytda yuborilgan xabarlar kelmagan bo'lishi mumkin - kerak bo'lsa qayta yuboring. Keyin odatdagidek xabarlarni kut." --model sonnet --channels plugin:telegram@claude-plugins-official
echo [%date% %time%] Bot to'xtadi >> bot_log.txt
echo Bot to'xtadi. 15 soniyadan keyin qayta ishga tushadi. Butunlay to'xtatish uchun oynani yoping.
timeout /t 15 /nobreak
goto loop
