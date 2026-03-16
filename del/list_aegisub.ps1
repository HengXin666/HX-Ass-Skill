$base = "D:\command\Aegisub\aegisub-portable"
Get-ChildItem $base -Recurse -Depth 3 | ForEach-Object {
    $rel = $_.FullName.Substring($base.Length)
    Write-Host $rel
}
