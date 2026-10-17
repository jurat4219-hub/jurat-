# Bot allaqachon ishlayaptimi? (claude.exe --channels) -> exit 1 = ha, exit 0 = yo'q
$p = Get-CimInstance Win32_Process -Filter "Name='claude.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'channels' }
if ($p) { exit 1 } else { exit 0 }
