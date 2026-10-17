# Bot ishlab turganda kompyuterni avtomatik uxlashdan saqlaydi. Ekran baribir o'chadi va qulflanadi.
Add-Type @"
using System; using System.Runtime.InteropServices;
public static class Awake { [DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f); }
"@
while ($true) { [Awake]::SetThreadExecutionState([uint32]"0x80000001") | Out-Null; Start-Sleep -Seconds 30 }
