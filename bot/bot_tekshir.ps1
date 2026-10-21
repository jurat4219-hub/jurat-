# Bot allaqachon ishlayaptimi? exit 1 = ha (bu nusxa yopilsin), exit 0 = yo'q (ishga tushsin)
# 1) claude.exe --channels ishlayapti  2) bizdan OLDIN ochilgan boshqa Telegram-bot.bat oynasi bor
$meId = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$me   = Get-CimInstance Win32_Process -Filter "ProcessId=$meId"
$cl = Get-CimInstance Win32_Process -Filter "Name='claude.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'channels' }
$old = Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" -ErrorAction SilentlyContinue |
  Where-Object { $_.CommandLine -match 'Telegram-bot\.bat' -and $_.ProcessId -ne $meId -and $me -and $_.CreationDate -lt $me.CreationDate }
if ($cl -or $old) { exit 1 } else { exit 0 }
