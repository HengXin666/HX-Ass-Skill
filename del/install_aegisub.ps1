$ErrorActionPreference = "Stop"
$url = "https://github.com/TypesettingTools/Aegisub/releases/download/v3.4.2/Aegisub-3.4.2-portable.zip"
$zipPath = "D:\command\Aegisub-3.4.2-portable.zip"
$extractPath = "D:\command\Aegisub"

Write-Host "Downloading Aegisub 3.4.2 portable..."
if (-not (Test-Path $zipPath)) {
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
    Write-Host "Downloaded: $zipPath"
} else {
    Write-Host "Already downloaded: $zipPath"
}

Write-Host "Extracting to $extractPath..."
if (Test-Path $extractPath) {
    Remove-Item -Path $extractPath -Recurse -Force
}
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
Write-Host "Extracted!"

# Find aegisub executable
$exe = Get-ChildItem -Path $extractPath -Filter "aegisub*.exe" -Recurse | Select-Object -First 1
if ($exe) {
    Write-Host "Aegisub found at: $($exe.FullName)"
} else {
    Write-Host "Looking for exe..."
    Get-ChildItem -Path $extractPath -Filter "*.exe" -Recurse | ForEach-Object { Write-Host $_.FullName }
}
