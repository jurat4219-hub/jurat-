# Botni toza qayta yoqish: hamma bot nusxalarini yopadi va BITTASINI ochadi. Boshqa Claude oynalariga tegmaydi.
$dst = "C:\Users\HP\claude-telegram"
Write-Host "Eski bot nusxalari yopilmoqda..."
Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" | Where-Object { $_.CommandLine -match 'Telegram-bot\.bat' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Get-CimInstance Win32_Process -Filter "Name='claude.exe'" | Where-Object { $_.CommandLine -match 'channels' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep 3
Start-Process -FilePath "$dst\Telegram-bot.bat" -WorkingDirectory $dst
Write-Host "Bot ishga tushirildi, 40 soniya tekshiraman..."
Start-Sleep 40
$n = @(Get-CimInstance Win32_Process -Filter "Name='claude.exe'" | Where-Object { $_.CommandLine -match 'channels' }).Count
if ($n -eq 1) { Write-Host "OK: bot BITTA nusxada ishlayapti. Telegram'ga 'Bot ishga tushdi' kelishi kerak." -ForegroundColor Green }
elseif ($n -eq 0) { Write-Host "DIQQAT: bot ishlamayapti. Qora bot oynasini oching - u yerda 'Login expired' yoki xato yozilgan bo'ladi." -ForegroundColor Red }
else { Write-Host "DIQQAT: $n ta nusxa! Shu faylni yana bir marta ishga tushiring." -ForegroundColor Red }
Write-Host "--- bot_log.txt (oxirgi 4 qator) ---"
Get-Content "$dst\bot_log.txt" -Tail 4 -ErrorAction SilentlyContinue
Write-Host "Oynani yopish uchun Enter bosing"; [void](Read-Host)
