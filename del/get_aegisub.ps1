$ErrorActionPreference = "Stop"
$rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/TypesettingTools/Aegisub/releases/latest' -UseBasicParsing
foreach ($a in $rel.assets) {
    Write-Host "$($a.name) --- $($a.browser_download_url)"
}
