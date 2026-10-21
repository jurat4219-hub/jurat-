# Jurat bot: GitHub'dan yangilash (ASCII). Ma'lumotlarga (baza, json, excel) tegmaydi.
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$dst  = "C:\Users\HP\claude-telegram"
Set-Location $repo
git pull --ff-only
python -m pip install --quiet --disable-pip-version-check -r "$repo\requirements.txt"
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue) -and -not (Test-Path "$env:LOCALAPPDATA\Microsoft\WinGet\Links\ffmpeg.exe")) {
  Write-Host "ffmpeg o'rnatilmoqda (video montaj uchun)..."; winget install --id Gyan.FFmpeg -e --source winget --accept-package-agreements --accept-source-agreements
}
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Videos\montaj" | Out-Null
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Videos\montaj\fon_musiqa" | Out-Null
$bk = "$dst\zaxira\$(Get-Date -Format yyyyMMdd_HHmm)"
New-Item -ItemType Directory -Force -Path $bk | Out-Null
foreach ($d in @(".claude\agents", ".claude\skills", "ish\akt", "ish\qarz", "ish\pubg", "ish\zapravka", "ish\skan", "ish\video", "ish\guruh", "ish\musiqa")) {
  if (Test-Path "$dst\$d") { Copy-Item "$dst\$d" "$bk\$d" -Recurse -Force -ErrorAction SilentlyContinue }
  New-Item -ItemType Directory -Force -Path "$dst\$d" | Out-Null
  Copy-Item "$repo\$d\*" "$dst\$d\" -Recurse -Force
}
foreach ($f in @("Telegram-bot.bat", "bot_tekshir.ps1", "awake.ps1", "bot_qayta.ps1")) { Copy-Item "$repo\bot\$f" "$dst\$f" -Force }
$cm = "$dst\CLAUDE.md"
if (Test-Path $cm) {
  $cur = [IO.File]::ReadAllText($cm, [Text.Encoding]::UTF8)
  foreach ($q in Get-ChildItem "$repo\docs\claude_qoshimcha_*.md" | Sort-Object Name) {
    $add = [IO.File]::ReadAllText($q.FullName, [Text.Encoding]::UTF8)
    $first = ($add -split "`n" | Where-Object { $_ -match '^## ' } | Select-Object -First 1)
    if ($first -and -not $cur.Contains($first.Trim())) {
      Copy-Item $cm "$bk\CLAUDE.md" -Force
      [IO.File]::AppendAllText($cm, "`n" + $add, (New-Object Text.UTF8Encoding($false))); $cur += $add
      Write-Host "CLAUDE.md ga qo'shildi: $($first.Trim())"
    }
  }
}
Write-Host "Oxirgi o'zgarish: $(git log -1 --format='%cd | %s' --date=format:'%d.%m.%Y %H:%M')"
# Ish stolida "Botni qayta yoqish" tugmasi va Windows yonganda avto-start
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) "Botni qayta yoqish.lnk"))
$lnk.TargetPath = "powershell.exe"; $lnk.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$dst\bot_qayta.ps1`""
$lnk.WorkingDirectory = $dst; $lnk.IconLocation = "shell32.dll,238"; $lnk.Save()
$st = $ws.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Telegram-bot.lnk")
$st.TargetPath = "$dst\Telegram-bot.bat"; $st.WorkingDirectory = $dst; $st.Save()
Write-Host "TAYYOR. Zaxira: $bk. Bot qayta yoqilmoqda (yangi sozlamalar bilan)..." -ForegroundColor Green
& powershell -NoProfile -ExecutionPolicy Bypass -File "$dst\bot_qayta.ps1"
