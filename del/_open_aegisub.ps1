$aegisub = "D:\command\Aegisub\aegisub-portable\aegisub.exe"
$dir = "C:\Users\Heng_Xin\Documents\Lyrics"
$kfx = Get-ChildItem -LiteralPath $dir -Filter "*67973169*_KFX.ass" -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $kfx) {
    Write-Host "ERROR: KFX file not found!"
    exit 1
}

Write-Host "Opening in Aegisub: $($kfx.FullName)"
Start-Process -FilePath $aegisub -ArgumentList "`"$($kfx.FullName)`""
Write-Host "Aegisub launched!"
