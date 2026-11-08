# Remove 0-byte placeholder PNGs left behind by an interrupted render (Windows PowerShell).
# IMPORTANT: run this ONLY after every Blender worker has stopped. While a render is running,
# in-progress frames are 0-byte placeholders on purpose, and deleting them breaks the lock system.
param([string]$Dir = "C:\Temp_Render")
$empty = Get-ChildItem -Path $Dir -Filter "*.png" | Where-Object { $_.Length -eq 0 }
Write-Host "Found $($empty.Count) zero-byte placeholder file(s) in $Dir"
$empty | Remove-Item
Write-Host "Done. Re-run one worker (e.g. -s 1 -e 4440 -j 1 -a) to fill any gaps."
