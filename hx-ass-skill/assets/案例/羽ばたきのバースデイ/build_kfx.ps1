## build_kfx.ps1 - Assembles Aegisub KFX template file
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$scriptDir = $PSScriptRoot
$utf8 = New-Object System.Text.UTF8Encoding $false
$utf8Bom = New-Object System.Text.UTF8Encoding $true

# Find files using wildcards to avoid encoding issues
$refDir = Join-Path (Join-Path $scriptDir "reference") "music-ass"
$allAss = Get-ChildItem -LiteralPath $refDir -Filter "*.ass" -Recurse -ErrorAction SilentlyContinue
$refFile = $allAss | Where-Object { $_.DirectoryName -match "3P" } | Select-Object -First 1

$inputDir = [System.IO.Path]::Combine("C:\Users\Heng_Xin\Documents", "Lyrics")
$inputAss = Get-ChildItem -LiteralPath $inputDir -Filter "*67973169*.ass" -ErrorAction SilentlyContinue | Where-Object { $_.Name -notmatch "_KFX" } | Select-Object -First 1

$furiFile = Join-Path $scriptDir "furigana_map.txt"

if (-not $refFile) { Write-Host "ERROR: Reference file not found in $refDir"; exit 1 }
if (-not $inputAss) { Write-Host "ERROR: Input file not found in $inputDir"; exit 1 }

Write-Host "Ref: $($refFile.FullName)"
Write-Host "In:  $($inputAss.FullName)"

$outputFile = [System.IO.Path]::Combine($inputAss.DirectoryName, $inputAss.BaseName + "_KFX.ass")
Write-Host "Out: $outputFile"

# Read files
$refLines = [System.IO.File]::ReadAllLines($refFile.FullName, $utf8)
$inputLines = [System.IO.File]::ReadAllLines($inputAss.FullName, $utf8)
$furiMapLines = [System.IO.File]::ReadAllLines($furiFile, $utf8)

Write-Host "Ref lines: $($refLines.Count)"
Write-Host "Input lines: $($inputLines.Count)"

# Build furigana map
$furiMap = @{}
foreach ($fl in $furiMapLines) {
    $fl = $fl.Trim()
    if ($fl -and $fl.Contains("=")) {
        $idx = $fl.IndexOf("=")
        $furiMap[$fl.Substring(0, $idx)] = $fl.Substring($idx + 1)
    }
}
Write-Host "Furigana entries: $($furiMap.Count)"

$out = [System.Collections.ArrayList]::new()

# --- Script Info + Styles from reference (lines 0-41) ---
for ($i = 0; $i -le 41; $i++) {
    [void]$out.Add($refLines[$i])
}
[void]$out.Add("")

# --- Events ---
[void]$out.Add("[Events]")
[void]$out.Add("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")
[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# --- Template blocks from reference (lines 44-123) ---
for ($i = 44; $i -le 123; $i++) {
    [void]$out.Add($refLines[$i])
}
[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# --- Functions ---
function TimeToMs([string]$t) {
    if ($t -match "(\d+):(\d+):(\d+)\.(\d+)") {
        return ([int]$matches[1]*3600+[int]$matches[2]*60+[int]$matches[3])*1000+[int]$matches[4]*10
    }
    return 0
}

function Assign-Style([int]$ms, [string]$stripped) {
    # Characters for dual-line detection
    $h97FF = [char]0x97FF  # 響
    $h5E73 = [char]0x5E73  # 平
    
    # == Intro (0:01-0:24) ==
    if ($ms -lt 24000) { return "OPJP" }
    
    # == Verse 1 (0:24-0:41) ==
    if ($ms -lt 41000) { return "OPJP 2" }
    
    # == Pre-chorus 1 (0:41-1:01) ==
    # 分かんない at ~0:55 -> OPJP 3-2
    if ($ms -ge 41000 -and $ms -lt 55500) { return "OPJP 3-1" }
    if ($ms -ge 55500 -and $ms -lt 56600) { return "OPJP 3-2" }
    if ($ms -ge 56500 -and $ms -lt 61500) {
        if ($stripped.Contains($h97FF)) { return "OPJP 3-2" }  # 響くから at ~0:59
        return "OPJP 3-1"
    }
    
    # == Chorus 1 (1:01-1:17) ==
    if ($ms -ge 61000 -and $ms -lt 77000) { return "OPJP 4" }
    
    # == End chorus 1 (1:17-1:36) ==
    if ($ms -ge 77000 -and $ms -lt 96000) { return "OPJP 5" }
    
    # == Verse 2 (1:36-1:58) ==
    if ($ms -ge 96000 -and $ms -lt 118000) { return "OPJP 2" }
    
    # == Pre-chorus 2 (1:58-2:13) ==
    # 平気 at ~2:07 (127000ms) -> OPJP 3-2
    # 響くなら at ~2:12 (132000ms) -> OPJP 3-2
    if ($ms -ge 118000 -and $ms -lt 127000) { return "OPJP 3-1" }
    if ($ms -ge 127000 -and $ms -lt 128000) {
        if ($stripped.Contains($h5E73)) { return "OPJP 3-2" }
        return "OPJP 3-1"
    }
    if ($ms -ge 128000 -and $ms -lt 132000) { return "OPJP 3-1" }
    if ($ms -ge 132000 -and $ms -lt 133000) {
        if ($stripped.Contains($h97FF)) { return "OPJP 3-2" }
        return "OPJP 3-1"
    }
    
    # == Chorus 2 (2:13-2:29) ==
    if ($ms -ge 133000 -and $ms -lt 149000) { return "OPJP 4" }
    
    # == End chorus 2 (2:29-2:58) ==
    if ($ms -ge 149000 -and $ms -lt 178000) { return "OPJP 5" }
    
    # == Bridge / Verse 3 (2:58-3:36) ==
    if ($ms -ge 178000 -and $ms -lt 216000) { return "OPJP 2" }
    
    # == Build-up (3:36-3:46) ==
    if ($ms -ge 216000 -and $ms -lt 226000) { return "OPJP 3-1" }
    
    # == Final chorus (3:46-4:02) ==
    if ($ms -ge 226000 -and $ms -lt 242000) { return "OPJP 4" }
    
    # == Ending (4:02+) ==
    return "OPJP 5"
}

function Add-Furigana([string]$text, [hashtable]$map) {
    $sb = New-Object System.Text.StringBuilder
    $i = 0
    $plain = $text -replace "\{[^}]+\}", ""
    
    while ($i -lt $text.Length) {
        if ($text[$i] -eq [char]'{') {
            $end = $text.IndexOf('}', $i)
            if ($end -ge 0) {
                [void]$sb.Append($text.Substring($i, $end - $i + 1))
                $i = $end + 1
            } else {
                [void]$sb.Append($text[$i]); $i++
            }
        } else {
            $ch = [string]$text[$i]
            $code = [int]$text[$i]
            $isK = ($code -ge 0x4E00 -and $code -le 0x9FFF)
            
            if ($isK -and $map.ContainsKey($ch)) {
                $r = $map[$ch]
                
                # Context overrides using char codes
                if ($code -eq 0x4E00 -and $plain.Contains([string][char]0x4E00+[string][char]0x4EBA)) {
                    $r = [string][char]0x3072+[string][char]0x3068  # 一人 → ひと
                }
                if ($code -eq 0x51FA) {
                    if ($plain.Contains([string][char]0x51FA+[string][char]0x6765) -or $plain.Contains([string][char]0x51FA+[string][char]0x4F1A)) {
                        $r = [string][char]0x3067  # 出来/出会 → で
                    }
                }
                if ($code -eq 0x6765) {  # 来
                    if ($plain.Contains([string][char]0x51FA+[string][char]0x6765)) {
                        $r = [string][char]0x304D  # 出来 → き
                    }
                    # 未来 → らい (default, no change needed)
                }
                if ($code -eq 0x97F3 -and $plain.Contains([string][char]0x97F3+[string][char]0x8272)) {
                    $r = [string][char]0x306D  # 音色 → ね
                }
                if ($code -eq 0x5206) {  # 分
                    if ($plain.Contains([string][char]0x591A+[string][char]0x5206)) {
                        $r = [string][char]0x3076+[string][char]0x3093  # 多分 → ぶん
                    }
                    # 分かんない → わ (default, no change needed)
                }
                
                [void]$sb.Append($ch + "|<" + $r)
            } else {
                [void]$sb.Append($ch)
            }
            $i++
        }
    }
    return $sb.ToString()
}

# --- Karaoke lines ---
[void]$out.Add("; === KARAOKE SOURCE LINES ===")
$kCount = 0

foreach ($line in $inputLines) {
    if ($line -notmatch "^Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+),\s*orig\s*,") { continue }
    
    $start = $matches[1]; $end = $matches[2]
    $ms = TimeToMs $start
    $parts = $line -split ",", 10
    if ($parts.Count -lt 10) { continue }
    $text = $parts[9]
    
    # Skip artist/info (before song starts)
    if ($ms -lt 1370) { continue }
    
    $stripped = $text -replace "\{[^}]+\}", ""
    
    if ($text -notmatch "\\kf") {
        if ($stripped.Trim().Length -gt 0) {
            $st = Assign-Style $ms $stripped
            $dur = (TimeToMs $end) - $ms
            $kv = [math]::Floor($dur / 10)
            $ft = Add-Furigana $stripped.Trim() $furiMap
            [void]$out.Add("Comment: 0,$start,$end,$st,,0,0,0,karaoke,{\k$kv}$ft")
            $kCount++
        }
        continue
    }
    
    $text = $text -replace "\\kf", "\k"
    $st = Assign-Style $ms $stripped
    $ft = Add-Furigana $text $furiMap
    [void]$out.Add("Comment: 0,$start,$end,$st,,0,0,0,karaoke,$ft")
    $kCount++
}

Write-Host "Karaoke lines: $kCount"
[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# --- CN translation ---
[void]$out.Add("; === CHINESE TRANSLATION ===")
$cnCount = 0

foreach ($line in $inputLines) {
    if ($line -notmatch "^Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+),\s*ts\s*,") { continue }
    
    $start = $matches[1]; $end = $matches[2]
    $ms = TimeToMs $start
    $parts = $line -split ",", 10
    $text = $parts[9]
    
    if ($text -notmatch "\\fad") { $text = "{\fad(300,300)}" + $text }
    
    $layer = 0
    $isChorus = (($ms -ge 61000 -and $ms -lt 77000) -or ($ms -ge 133000 -and $ms -lt 149000) -or ($ms -ge 226000 -and $ms -lt 242000))
    if ($isChorus -and $text -notmatch "\\pos") {
        $layer = 6
        $pt = $text -replace "\{[^}]+\}", ""
        $px = [math]::Max(30, [math]::Round($pt.Length * 16))
        $ct = $text -replace "\{\\fad\([^)]+\)\}", ""
        $text = "{\fad(300,300)\pos($px,600)}$ct"
    }
    
    [void]$out.Add("Dialogue: $layer,$start,$end,OPCN,,0,0,0,,$text")
    $cnCount++
}

Write-Host "CN lines: $cnCount"

# Write
[System.IO.File]::WriteAllLines($outputFile, $out.ToArray(), $utf8Bom)
Write-Host "`nSUCCESS! $outputFile"
Write-Host "Total: $($out.Count) lines"
