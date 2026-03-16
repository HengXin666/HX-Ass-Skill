## build_kfx_innocent_blue.ps1 - Assembles KFX template for INNOCENT BLUE
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$scriptDir = $PSScriptRoot
$utf8 = New-Object System.Text.UTF8Encoding $false
$utf8Bom = New-Object System.Text.UTF8Encoding $true

# Find reference file (same anime: 天使の3P)
$refDir = Join-Path (Join-Path $scriptDir "reference") "music-ass"
$allAss = Get-ChildItem -LiteralPath $refDir -Filter "*.ass" -Recurse -ErrorAction SilentlyContinue
$refFile = $allAss | Where-Object { $_.DirectoryName -match "3P" } | Select-Object -First 1

# Find input file: INNOCENT BLUE (88999812)
$inputDir = [System.IO.Path]::Combine("C:\Users\Heng_Xin\Documents", "Lyrics")
$inputAss = Get-ChildItem -LiteralPath $inputDir -Filter "*88999812*.ass" -ErrorAction SilentlyContinue | Where-Object { $_.Name -notmatch "_KFX" } | Select-Object -First 1

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
    # === INNOCENT BLUE section mapping ===
    
    # == Intro (0:11 - 0:27) ==
    if ($ms -lt 27200) { return "OPJP" }
    
    # == Verse 1 (0:27 - 0:41) ==
    if ($ms -lt 41500) { return "OPJP 2" }
    
    # == Pre-chorus 1 (0:41 - 1:01) ==
    if ($ms -lt 61500) { return "OPJP 3-1" }
    
    # == Chorus 1 (1:01 - 1:17) ==
    if ($ms -lt 77000) { return "OPJP 4" }
    
    # == (Interlude 1:17 - 1:27, no lyrics) ==
    
    # == Verse 2 (1:27 - 1:47) ==
    if ($ms -lt 106600) { return "OPJP 2" }
    
    # == Pre-chorus 2 / Bridge (1:47 - 1:57) ==
    if ($ms -lt 116800) { return "OPJP 3-1" }
    
    # == Chorus 2 (1:57 - 2:17) ==
    if ($ms -lt 137000) { return "OPJP 4" }
    
    # == End chorus 2 / Outro section (2:17 - 2:33) ==
    if ($ms -lt 153000) { return "OPJP 5" }
    
    # == (Interlude 2:33 - 2:52, no lyrics) ==
    
    # == Bridge (2:52 - 3:02) ==
    if ($ms -lt 182000) { return "OPJP 2" }
    
    # == Final Chorus (3:02 - 3:22) ==
    if ($ms -lt 202200) { return "OPJP 4" }
    
    # == Ending (3:22+) ==
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
                
                # === Context overrides (Unicode code points to avoid encoding issues) ===
                
                # 笑顔(えがお): 笑=え (default わら), 顔=がお (default お)
                if ($code -eq 0x7B11) {  # 笑
                    if ($plain.Contains([string][char]0x7B11+[string][char]0x9854)) {
                        $r = [string][char]0x3048  # え
                    }
                }
                if ($code -eq 0x9854) {  # 顔
                    if ($plain.Contains([string][char]0x7B11+[string][char]0x9854)) {
                        $r = [string][char]0x304C+[string][char]0x304A  # がお
                    }
                }
                
                # 何回(なんかい): 何=なん (default なに), 回=かい (default まわ)
                if ($code -eq 0x4F55) {  # 何
                    if ($plain.Contains([string][char]0x4F55+[string][char]0x56DE)) {
                        $r = [string][char]0x306A+[string][char]0x3093  # なん
                    }
                }
                if ($code -eq 0x56DE) {  # 回
                    if ($plain.Contains([string][char]0x4F55+[string][char]0x56DE)) {
                        $r = [string][char]0x304B+[string][char]0x3044  # かい
                    }
                }
                
                # 出口(でぐち)/出来(でき)/出会(であ): 出=で (default だ)
                if ($code -eq 0x51FA) {  # 出
                    if ($plain.Contains([string][char]0x51FA+[string][char]0x53E3) -or $plain.Contains([string][char]0x51FA+[string][char]0x6765) -or $plain.Contains([string][char]0x51FA+[string][char]0x4F1A)) {
                        $r = [string][char]0x3067  # で
                    }
                    # 逃げ出す: 出=だ (default, no change)
                }
                
                # 見上(みあ)げる: 見=み (default OK), 上=あ (default OK)
                
                # 自分(じぶん): 分=ぶん (default わ)
                if ($code -eq 0x5206) {  # 分
                    if ($plain.Contains([string][char]0x81EA+[string][char]0x5206)) {
                        $r = [string][char]0x3076+[string][char]0x3093  # ぶん
                    }
                    # 多分(たぶん) → ぶん (same)
                    if ($plain.Contains([string][char]0x591A+[string][char]0x5206)) {
                        $r = [string][char]0x3076+[string][char]0x3093  # ぶん
                    }
                }
                
                # 風(ふう) in どんな風に: 風=ふう (default かぜ)
                if ($code -eq 0x98A8) {  # 風
                    if ($plain.Contains([string][char]0x98A8+[string][char]0x306B)) {  # 風に
                        $r = [string][char]0x3075+[string][char]0x3046  # ふう
                    }
                }
                
                # 今日(きょう): 今=きょ (default いま), 日=う
                if ($code -eq 0x4ECA) {  # 今
                    if ($plain.Contains([string][char]0x4ECA+[string][char]0x65E5)) {
                        $r = [string][char]0x304D+[string][char]0x3087  # きょ
                    }
                }
                if ($code -eq 0x65E5) {  # 日
                    if ($plain.Contains([string][char]0x4ECA+[string][char]0x65E5)) {
                        $r = [string][char]0x3046  # う
                    }
                    # 日常(にちじょう): 日=にち
                    if ($plain.Contains([string][char]0x65E5+[string][char]0x5E38)) {
                        $r = [string][char]0x306B+[string][char]0x3061  # にち
                    }
                    # 泣いた日(ひ)も: 日=ひ
                    if ($plain.Contains([string][char]0x65E5+[string][char]0x3082)) {
                        $r = [string][char]0x3072  # ひ
                    }
                }
                
                # 大切(たいせつ): 大=たい (default だい)
                if ($code -eq 0x5927) {  # 大
                    if ($plain.Contains([string][char]0x5927+[string][char]0x5207)) {
                        $r = [string][char]0x305F+[string][char]0x3044  # たい
                    }
                }
                # 切(せつ)なくなる - standalone 切 = せつ (default OK)
                
                # 蹲(うずくま)った - special: 1 kanji = 4 kana
                # Already in map: 蹲=うずくま
                
                # 音色(ねいろ): 音=ね (default おと) - keep from previous song
                if ($code -eq 0x97F3 -and $plain.Contains([string][char]0x97F3+[string][char]0x8272)) {
                    $r = [string][char]0x306D  # ね
                }
                
                # 一人(ひとり): keep from previous song
                if ($code -eq 0x4E00 -and $plain.Contains([string][char]0x4E00+[string][char]0x4EBA)) {
                    $r = [string][char]0x3072+[string][char]0x3068  # ひと
                }
                
                # 来 in 出来 → き: keep from previous song
                if ($code -eq 0x6765) {  # 来
                    if ($plain.Contains([string][char]0x51FA+[string][char]0x6765)) {
                        $r = [string][char]0x304D  # き
                    }
                }
                
                # 日常(にちじょう): 常=じょう (default OK from map)
                
                # 窮屈(きゅうくつ): 窮=きゅう, 屈=くつ (both in map OK)
                
                # 感情(かんじょう): 感=かん, 情=じょう (both in map OK)
                
                # 無意識(むいしき): 無=む, 意=い, 識=しき (all in map OK)
                
                # 否定(ひてい): 否=ひ, 定=てい (both in map OK)
                
                # 圧倒的(あっとうてき): 圧=あっ, 倒=とう, 的=てき (all in map OK)
                
                # 色褪(いろあ)せない: 色=いろ (default OK), 褪=あ (in map OK)
                
                # 蒼穹(そうきゅう): 蒼=そう, 穹=きゅう (both in map OK)
                
                # 孤独(こどく): 孤=こ, 独=どく (both in map OK)
                
                # 希望(きぼう): 希=き, 望=ぼう (both in map OK)
                # Wait - 希=き conflicts with 気=き... 希 is a different kanji (0x5E0C)
                # 気=き is 0x6C17, 希=き is 0x5E0C - different characters, no conflict
                
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
    
    # Skip artist/info lines (before song starts at ~0:11)
    if ($ms -lt 11000) { continue }
    
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
    # Chorus sections: Chorus 1 (1:01-1:17), Chorus 2 (1:57-2:17), Final Chorus (3:02-3:22)
    $isChorus = (($ms -ge 61500 -and $ms -lt 77000) -or ($ms -ge 116800 -and $ms -lt 137000) -or ($ms -ge 182000 -and $ms -lt 202200))
    if ($isChorus -and $text -notmatch "\\pos") {
        $layer = 6
        $pt = $text -replace "\{[^}]+\}", ""
        $px = [math]::Max(30, [math]::Round($pt.Length * 16))
        $ct = $text -replace "\{\\fad\([^)]+\)\}", ""
        $text = "{\fad(300,300)\pos($px,600)}$ct"
    }
    
    # End chorus / Ending sections: move CN up to avoid furigana overlap
    $isEnding = (($ms -ge 137000 -and $ms -lt 153000) -or ($ms -ge 202200 -and $ms -lt 220000))
    if ($isEnding -and $text -notmatch "\\pos") {
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
