# build_kfx_taisetsu.ps1 - KFX Template for 大切がきこえる (天使の3P!)
# Style: Cute / Pop / Gentle-Emotional — matching the anime's pastel loli aesthetic
# Color: Pink-Magenta primary (#F04BAF) + White outline — same as reference OP
# Font: FOT-PopJoy Std B (JP) + 方正少儿_GBK (CN) — cute pop fonts
# Effects: Feathers, flowers, music notes, hearts, rainbow HSV — NOT gears/rain/fragments
# v3: Complete redesign based on actual reference template analysis
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$scriptDir = $PSScriptRoot
$utf8 = New-Object System.Text.UTF8Encoding $false
$utf8Bom = New-Object System.Text.UTF8Encoding $true

# Find input file: 大切がきこえる (88999817)
$inputDir = [System.IO.Path]::Combine("C:\Users\Heng_Xin\Documents", "Lyrics")
$inputAss = Get-ChildItem -LiteralPath $inputDir -Filter "*88999817*.ass" -ErrorAction SilentlyContinue | Where-Object { $_.Name -notmatch "_KFX" } | Select-Object -First 1

$furiFile = Join-Path $scriptDir "furigana_map.txt"

if (-not $inputAss) { Write-Host "ERROR: Input file not found in $inputDir"; exit 1 }

Write-Host "In:  $($inputAss.FullName)"

$outputFile = [System.IO.Path]::Combine($inputAss.DirectoryName, $inputAss.BaseName + "_KFX.ass")
Write-Host "Out: $outputFile"

# Read files
$inputLines = [System.IO.File]::ReadAllLines($inputAss.FullName, $utf8)
$furiMapLines = [System.IO.File]::ReadAllLines($furiFile, $utf8)

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

# === SCRIPT INFO ===
[void]$out.Add("[Script Info]")
[void]$out.Add("; KFX Template for: taisetsu ga kikoeru (大切がきこえる)")
[void]$out.Add("; Anime: 天使の3P! (Angel's 3Piece!)")
[void]$out.Add("; Style: Cute Pop — Pink-Magenta + White, Flowers + Feathers + Music Notes")
[void]$out.Add("; v3: Redesigned to match anime's pastel loli aesthetic")
[void]$out.Add("Title: Default Aegisub file")
[void]$out.Add("ScriptType: v4.00+")
[void]$out.Add("WrapStyle: 0")
[void]$out.Add("PlayResX: 1280")
[void]$out.Add("PlayResY: 720")
[void]$out.Add("ScaledBorderAndShadow: yes")
[void]$out.Add("YCbCr Matrix: TV.709")
[void]$out.Add("")

# === STYLES ===
# Color scheme FROM REFERENCE: Primary &H00AF4BF0 (pink-magenta), Outline &H00FFFFFF (white)
# Font FROM REFERENCE: FOT-PopJoy Std B (JP), 方正少儿_GBK (CN)
# Size FROM REFERENCE: 36 (JP), 32 (CN)
# MarginV FROM REFERENCE: 28-30 (top JP), 4 (bottom CN)
[void]$out.Add("[V4+ Styles]")
[void]$out.Add("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding")
# Furigana styles (must be before main for karaskel)
[void]$out.Add("Style: OPCN-furigana,方正少儿_GBK,16,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,-1,0,0,0,100,100,0,0,1,1.5,1.25,2,0,0,4,1")
[void]$out.Add("Style: OPJP 6-furigana,FOT-PopJoy Std B,18,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,1.5,1.25,8,0,0,28,1")
[void]$out.Add("Style: OPJP 5-furigana,FOT-PopJoy Std B,18,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,1.5,1.25,8,0,0,28,1")
[void]$out.Add("Style: OPJP 4-furigana,FOT-PopJoy Std B,18,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,1.5,1.25,8,0,0,35,1")
[void]$out.Add("Style: OPJP 3-furigana,FOT-PopJoy Std B,18,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,1.5,1.25,8,0,0,28,1")
[void]$out.Add("Style: OPJP 2-furigana,FOT-PopJoy Std B,18,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,1.5,1.25,8,0,0,30,1")
[void]$out.Add("Style: OPJP-furigana,FOT-PopJoy Std B,18,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,1.5,1.25,8,0,0,28,1")
# Main styles — all pink-magenta primary + white outline
[void]$out.Add("Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1")
[void]$out.Add("Style: OPJP,FOT-PopJoy Std B,36,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,3,2.5,8,0,0,28,1")
[void]$out.Add("Style: OPJP 2,FOT-PopJoy Std B,36,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,3,2.5,8,0,0,30,1")
[void]$out.Add("Style: OPJP 3,FOT-PopJoy Std B,36,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,3,2.5,8,0,0,28,1")
[void]$out.Add("Style: OPJP 4,FOT-PopJoy Std B,36,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,3,2.5,8,0,0,35,1")
[void]$out.Add("Style: OPJP 5,FOT-PopJoy Std B,36,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,3,2.5,8,0,0,28,1")
[void]$out.Add("Style: OPJP 6,FOT-PopJoy Std B,36,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,0,0,0,0,100,100,0,0,1,3,2.5,8,0,0,28,1")
[void]$out.Add("Style: OPCN,方正少儿_GBK,32,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,-1,0,0,0,100,100,0,0,1,3,2.5,2,0,0,4,1")
[void]$out.Add("")

# === EVENTS ===
[void]$out.Add("[Events]")
[void]$out.Add("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")
[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# === SHARED CODE BLOCKS ===

# Shape definitions — cute/musical shapes (NOT sci-fi gears!)
# glitzerding = feather (from reference), hoa = flower (3 sizes), heart, music note, circle
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,code once,glitzerding = { ""m 26 37 l 38 27 l 45 19 l 52 11 l 57 7 b 66 0 72 9 64 29 l 59 26 l 62 31 b 58 36 52 43 46 47 l 41 44 l 44 48 b 41 52 37 56 33 58 l 28 52 l 30 58 l 27 61 l 24 58 l 24 61 l 21 58 l 17 61 l 17 59 b 11 62 6 64 0 64 l 0 60 b 5 60 12 57 16 54 l 14 51 l 18 51 l 17 47 l 20 50 l 20 42 l 24 38 l 25 45 ""}")

# 3 sizes of flower shapes (from reference hoa)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,code once,hoa = {""m 21 21 b 6 -7 46 -7 29 21 b 49 -2 63 34 30 28 b 63 44 31 65 25 32 b 26 65 -12 45 21 29 b -13 38 0 -5 21 21 m 25 22 b 21 22 21 28 25 28 b 29 28 29 22 25 22 "",""m 13 12 b 4 -4 28 -4 18 12 b 30 -1 38 20 18 17 b 38 26 19 39 15 19 b 16 39 -7 27 13 17 b -8 23 0 -3 13 12 m 15 13 b 13 13 13 17 15 17 b 18 17 18 13 15 13 "",""m 8 7 b 2 -2 17 -2 11 7 b 18 -1 23 11 11 9 b 23 14 11 21 9 10 b 9 21 -4 15 8 9 b -5 13 0 -2 8 7 m 9 7 b 8 7 8 9 9 9 b 11 9 11 7 9 7 ""}")

# Heart shape
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,code once,heart = { ""m 0 -15 b 0 -20 5 -25 10 -25 b 15 -25 20 -20 20 -15 b 20 -5 10 5 0 15 b -10 5 -20 -5 -20 -15 b -20 -20 -15 -25 -10 -25 b -5 -25 0 -20 0 -15"" }")

# Music note shapes (eighth note, double eighth, quarter)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,code once,note = {""m 5 0 l 5 -30 l 15 -35 l 15 -25 l 5 -20 l 5 0 b 5 5 0 8 -3 6 b -6 4 -3 -2 2 -1 l 5 0"",""m 5 0 l 5 -30 l 25 -35 l 25 -25 l 5 -20 l 5 0 b 5 5 0 8 -3 6 b -6 4 -3 -2 2 -1 l 5 0 m 25 -5 l 25 -25 l 25 -5 b 25 0 20 3 17 1 b 14 -1 17 -7 22 -6 l 25 -5"",""m 3 0 l 3 -25 l 3 0 b 3 5 -2 8 -5 6 b -8 4 -5 -2 0 -1 l 3 0""}")

# Star/sparkle shape
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,code once,star = { ""m 0 -10 l 3 -3 l 10 0 l 3 3 l 0 10 l -3 3 l -10 0 l -3 -3 l 0 -10"" }")

# Circle (for light orbs)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,code once,circle = { ""m 5 0 b 5 -3 3 -5 0 -5 b -3 -5 -5 -3 -5 0 b -5 3 -3 5 0 5 b 3 5 5 3 5 0"" }")

# Small feather (simplified)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,code once,feather_s = { ""m 0 9 l -2 9 l -2 1 l -5 -2 l -8 -7 l -8 -12 l -7 -17 l -5 -20 l -1 -24 l 2 -21 l 4 -18 l 5 -13 l 5 -8 l 4 -4 l 3 -1 l 0 1 l 0 4 l 0 7"" }")

# Color palettes — warm pastel pinks/purples/oranges matching the cute loli aesthetic
# 4 HSV-ranged colors for flower variety (from reference mau)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,code once,mau = { ""&H0000FF&"", ""&H00B4FF&"", ""&H00FFFF&"", ""&H8EFFE6&""}")
# Pastel accent colors for particles
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,code once,pastel = { ""&HFFB4E6&"", ""&HFFC8FF&"", ""&HFFE6C8&"", ""&HC8E6FF&"", ""&HC8FFC8&"" }")

# fxgroup conditions
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,code syl all,fxgroup.firstsyl = syl.i == 1")
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,code syl all,fxgroup.lastsyl = (syl.i == line.kara.n)")

[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# ============================================================
# OPJP: Intro (0:01-0:25) — Soft opening
# Scale pulse + feather float + gentle sparkle
# Like the reference OPJP but softer for this gentler song
# ============================================================

# L1: Text highlight — scale pulse on each syl (FROM REFERENCE)
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP,,0,0,0,template syl furi noblank,!retime(""syl"",0,0)!{\an5\pos(`$scenter,`$smiddle)\fscx100\fscy100\t(0,200,\fscx130\fscy130)\t(200,`$dur,\3c&HFFFFFF&\fscx100\fscy100)}")

# L0: Feather float on each syl (FROM REFERENCE glitzerding)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP,,0,0,0,template noblank notext,!retime(""syl"",0,0)!{\an5\blur3\1c&HFFFFFF&\3c&HEBBEBE&\t(0,`$dur,\frx!math.random(-90,90)!\fry!math.random(-90,90)!\frz!math.random(-90,90)!)\move(!`$center+math.random(-80,80)!,!`$middle+math.random(30,80)!,`$center,`$middle)\1c&HFFFFFF&\3c&HEBBEBE&\fad(300,100)\shad0\p2}!glitzerding[1]!")

# L0: Lead-in text: stretch Y then settle (FROM REFERENCE)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP,,0,0,0,template syl furi noblank char,!retime(""start2syl"",-100,0)!{\an5\pos(`$scenter,`$smiddle)\3c&HFFFFFF&\fscy130\t(0,500,\fscy100)\fad(500,0)}")

# L1: Lead-out text: gentle fade
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP,,0,0,0,template syl furi noblank char,!retime(""syl2end"",0,0)!{\an5\pos(`$center,`$middle)\fad(0,200)}")

# L0: Sparkle stars (2 per syl, soft white)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP,,0,0,0,template syl loop 2 noblank notext,!retime(""syl"",-100+j*200,400)!{\an5\pos(!`$center+math.random(-30,30)!,!`$middle+math.random(-20,20)!)\1c&HFFFFFF&\blur1\bord0\fscx!math.random(40,80)!\fscy!math.random(40,80)!\fad(200,300)\frz!math.random(0,360)!\p2}!star[1]!")

[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# ============================================================
# OPJP 2: Verse (0:26-0:50, 1:36-1:48)
# Music note particles + heartbeat shape + text fly-in with rotation
# Narrative — building emotion gently
# ============================================================

# Counter functions for staggered char entry (FROM REFERENCE)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 2,,0,0,0,code syl all,function char_counter(ref) ci[ref] = ci[ref] + 1; return """" end")
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 2,,0,0,0,code line all,ci = { 0 }; cn = _G.unicode.len((orgline.text_stripped:gsub("" "","""")))")

# L1: Text highlight — scale pulse + outline color flash (FROM REFERENCE)
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 2,,0,0,0,template syl furi noblank,!retime(""syl"",0,300)!{\an5\pos(`$scenter,!`$smiddle-10!)\fad(0,100)\t(0,100,\3c&HFFFFFF&\fscx130\fscy130)\t(100,`$dur,\3c!line.styleref.color3!\fscx100\fscy100\bord3\blur3)}")

# L1: Lead-in: staggered char fly-in with X-axis rotation (FROM REFERENCE)
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 2,,0,0,0,template syl furi char noblank,!char_counter(1)!!retime(""start2syl"",-700+(ci[1]-1)*30,0)!{\an5\frx360\move(`$lcenter,!`$lmiddle-70!,`$scenter,!`$smiddle-10!,0,200)\t(0,500,\bord2\frx0)\t(0,200,\fscx100\fscy100)}")

# L2: Music note particles (5 per syl, float upward) — unique to this song's musical theme
[void]$out.Add("Comment: 2,0:00:00.00,0:00:00.00,OPJP 2,,0,0,0,template syl noblank loop 5 notext,!retime(""presyl"",10+(`$dur/maxj)*j,700+(`$dur/maxj)*j)!{\p1\an5\fad(10,100)\move(!`$scenter+math.random(-20,20)!,`$smiddle,!`$scenter+math.random(-20,20)!,!`$middle+math.random(-130,-70)!)\fad(0,250)\blur3\shad0\1c&HFFFFFF&\3c&HEBBEBE&\fscx150\fscy150\p1}!note[math.random(3)]!")

# L0: Small hearts scatter (2 per syl, gentle drift)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 2,,0,0,0,template syl loop 2 noblank notext,!retime(""syl"",-100+j*300,600)!{\an5\move(!`$center+math.random(-40,40)!,!`$middle!,!`$center+math.random(-50,50)!,!`$middle-math.random(40,80)!)\1c!pastel[math.random(5)]!\blur1\bord0\fscx!math.random(30,50)!\fscy!math.random(30,50)!\fad(200,300)\frz!math.random(-30,30)!\p2}!heart[1]!")

[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# ============================================================
# OPJP 3: Pre-chorus / Narration (0:51-0:57, 1:50-2:06, 2:32-3:10)
# Scale pulse + outline color change + star sparkle
# Simple but warm — building anticipation
# Same as reference OPJP 3-1 (scale pulse highlight)
# ============================================================

# L1: Text highlight — scale pulse (FROM REFERENCE)
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 3,,0,0,0,template syl furi noblank,!retime(""syl"",0,0)!{\an5\pos(`$scenter,`$smiddle)\fscx100\fscy100\t(0,200,\fscx130\fscy130)\t(200,`$dur,\3c&HFFFFFF&\fscx100\fscy100)}")

# L0: Lead-in: stretch Y + fade (FROM REFERENCE)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 3,,0,0,0,template syl furi noblank char,!retime(""start2syl"",-100,0)!{\an5\pos(`$scenter,`$smiddle)\3c&HFFFFFF&\fscy130\t(0,500,\fscy100)\fad(500,0)}")

# L1: Lead-out: fade
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 3,,0,0,0,template syl furi noblank char,!retime(""syl2end"",0,0)!{\an5\pos(`$center,`$middle)\fad(0,200)}")

# L0: Star sparkle burst on highlight (3 per syl)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 3,,0,0,0,template syl loop 3 noblank notext,!retime(""syl"",-50+j*100,500)!{\an5\move(!`$center+math.random(-20,20)!,!`$middle+math.random(-15,15)!,!`$center+math.random(-40,40)!,!`$middle+math.random(-30,30)!)\1c&HFFFFFF&\blur1\bord0\fscx!math.random(50,90)!\fscy!math.random(50,90)!\fad(100,400)\frz!math.random(0,180)!\p2}!star[1]!")

# L0: Soft pastel glow on highlight
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 3,,0,0,0,template syl noblank notext,!retime(""syl"",-50,200)!{\an5\pos(`$scenter,`$smiddle)\blur6\bord5\3c!pastel[math.random(5)]!\1a&HFF&\fad(100,200)}")

[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# ============================================================
# OPJP 4: Chorus (0:57-1:25, 2:41-3:04, 3:10-3:25)
# MAXIMUM CUTE — Flowers + HSV rainbow + grass/vine paths + feathers
# This is the emotional climax — pull out all stops
# Directly inspired by reference OPJP 4 (the most elaborate style)
# ============================================================

# Helper functions (FROM REFERENCE)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,code once,temp = {} function set_temp(ref,val) temp[ref] = val return val end")
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,code syl all,fxgroup.firstsyl = syl.i == 1")
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,code line all,font_ratio = line.styleref.fontsize/40")

# Circle shape for color orbs (FROM REFERENCE)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,code once,shape4 = {""m 5 0 b 2 0 0 2 0 5 b 0 8 2 10 5 10 b 8 10 10 8 10 5 b 10 2 8 0 5 0""}")

# L4: Text lead-in: staggered fade from slightly above (FROM REFERENCE)
[void]$out.Add("Comment: 4,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,template syl furi noblank,!retime(""start2syl"",-1000+`$si*50,0)!{\an5\pos(`$center,`$middle)\fad(300,0)}")

# L5: Text highlight: scale pulse + white flash (FROM REFERENCE)
[void]$out.Add("Comment: 5,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,template syl furi noblank,!retime(""syl"",0,0)!{\an5\pos(`$center,`$middle)\t(0,33,\fscx120\fscy120\1c&HFFFFFF&)\t(33,`$dur,\fscx100\fscy100\1c!line.styleref.color1!)}")

# L4: Text lead-out: staggered fade (FROM REFERENCE)
[void]$out.Add("Comment: 4,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,template syl furi noblank,!retime(""syl2end"",0,-800+(`$si/`$syln)*800)!{\an5\pos(`$center,`$middle)\fad(0,300)}")

# L2: Flower explosion on highlight (FROM REFERENCE — hoa/flower with HSV rainbow colors)
[void]$out.Add("Comment: 2,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,template notext noblank loop 3,!retime(""syl2end"",-`$dur-math.random(0,300),500)!{\c!mau[math.random(4)]!\bord0\fscx!20*font_ratio!\fscy!20*font_ratio!\an5\frz!math.random(-100,0)!\move(!`$scenter+20*font_ratio!,`$stop,!`$scenter+(20+math.random(-50,50))*font_ratio!,!`$stop+math.random(-30,30)*font_ratio!)\fad(0,500)\t(0,300,\fscx!70*font_ratio!\fscy!70*font_ratio!)\t(\frz!math.random(50,300)*(math.random(0,1) == 1 and -1 or 1)!)\p1}!hoa[math.random(3)]!")

# L1: Additional flowers on lower layer
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,template notext noblank loop 2,!retime(""syl2end"",-`$dur-math.random(0,300),500)!{\c!mau[math.random(4)]!\bord0\fscx!20*font_ratio!\fscy!20*font_ratio!\an5\frz!math.random(-100,0)!\move(!`$scenter+20*font_ratio!,`$stop,!`$scenter+(20+math.random(-50,50))*font_ratio!,!`$stop+math.random(-30,30)*font_ratio!)\fad(0,500)\t(0,300,\fscx!70*font_ratio!\fscy!70*font_ratio!)\t(\frz!math.random(50,300)*(math.random(0,1) == 1 and -1 or 1)!)\p1}!hoa[math.random(3)]!")

# L0: Feather drift (3 per syl, white, gentle 3D rotation)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,template syl loop 3 noblank notext,!retime(""syl"",-200+j*150,800)!{\an5\1c&HFFFFFF&\3c&HEBBEBE&\bord1\blur2\fscx50\fscy50\frz!math.random(-100,0)!\move(!`$scenter!,`$smiddle,!`$scenter+math.random(-50,50)!,!`$smiddle+math.random(-50,50)!)\fad(230,300)\t(0,1500,\frz!math.random(-700,700)!\fry!math.random(-700,700)!\frx!math.random(-700,700)!)\p3}!glitzerding[1]!")

# L0: Rainbow HSV color orbs floating up (3 per syl)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,template syl loop 3 noblank notext,!retime(""syl"",-100+j*100,500)!{\an5\move(!`$center+math.random(-30,30)!,!`$middle!,!`$center+math.random(-40,40)!,!`$middle-math.random(30,60)!)\1c&H0000FF&\bord0\shad0\blur1\fscx!math.random(30,60)!\fscy!math.random(30,60)!\t(100,200,\alpha&H88&\1c!j == 1 and set_temp(""color"",_G.ass_color(_G.HSV_to_RGB(math.random(56,88)/255*360,0.8,1))) or temp.color!)\fad(0,500)\p1}!shape4[1]!")

# L0: Heart particles at line edges (subtle, firstsyl only)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,template notext loop 3 fxgroup firstsyl,!retime(""line"",j*200,j*300)!{\an5\move(!`$lleft-math.random(10,40)!,!`$middle+math.random(-20,20)!,!`$lleft-math.random(20,50)!,!`$middle-math.random(30,60)!)\1c!pastel[math.random(5)]!\blur1\bord0\fscx!math.random(30,60)!\fscy!math.random(30,60)!\fad(300,400)\frz!math.random(-20,20)!\p2}!heart[1]!")
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 4,,0,0,0,template notext loop 3 fxgroup firstsyl,!retime(""line"",j*200,j*300)!{\an5\move(!`$lright+math.random(10,40)!,!`$middle+math.random(-20,20)!,!`$lright+math.random(20,50)!,!`$middle-math.random(30,60)!)\1c!pastel[math.random(5)]!\blur1\bord0\fscx!math.random(30,60)!\fscy!math.random(30,60)!\fad(300,400)\frz!math.random(-20,20)!\p2}!heart[1]!")

[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# ============================================================
# OPJP 5: Bridge / End section (1:29-1:35, 2:22-2:31, 3:28-3:44)
# Butterfly flutter + feather scatter + angel halo ring
# Ethereal and dreamy — wings and halos for the "angels"
# Inspired by reference OPJP 5 (butterfly wings + angel halo + feather lead-in)
# ============================================================

# Counter functions (FROM REFERENCE)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 5,,0,0,0,code syl all,function char_counter5(ref) ci5[ref] = ci5[ref] + 1; return """" end")
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 5,,0,0,0,code line all,ci5 = { 0 }")

# Butterfly wing shape (FROM REFERENCE — cánh phải/trái)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 5,,0,0,0,code once,wing = { ""m 17 33 b 12 41 6 26 15 24 b 29 25 26 50 15 49 b 9 51 -4 41 2 22 b 11 3 28 -2 45 0 b 58 3 40 24 31 25 b 52 32 39 42 30 36 b 36 47 31 47 25 40 l 25 40 b 26 32 24 22 14 23 b 3 26 11 43 18 35 b 18 33 17 33 17 33 "" }")

# L1: Right butterfly wing (FROM REFERENCE — flutter animation)
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 5,,0,0,0,template noblank notext,!retime(""syl"",-25,500)!{\an1\frz10\fad(0,200)\move(`$sright,`$smiddle,!`$sright-50!,!`$smiddle-50!)\shad1\bord0\blur1\3c&H000000&\4c&H000000&\c&HFFFFFF&\fscx70\fscy70\t(0,200,\fry-80)\t(200,300,\fry0)\t(300,400,\fry-80)\t(400,500,\fry0)\t(500,600,\fry-80)\t(600,700,\fry0)\t(700,800,\fry-80)\t(800,900,\fry0)\t(900,1000,\fry-80)\t(1000,1100,\fry0)\t(1100,1300,\fry-80)\t(1300,1450,\fry0)\t(1450,1600,\fry-80)\t(1600,1700,\fry0)\t(1700,1850,\fry-80)\t(1850,2000,\fry0)\t(2000,2200,\fry-80)\t(2200,2300,\fry0)\t(2300,2400,\fry-80)\t(2400,2700,\fry0)\p1}!wing[1]!")

# L1: Left butterfly wing (mirrored, FROM REFERENCE)
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 5,,0,0,0,template noblank notext,!retime(""syl"",-25,500)!{\an1\frz-10\fry180\fad(0,200)\move(`$sleft,`$smiddle,!`$sleft-50!,!`$smiddle-50!)\shad1\bord0\blur1\3c&H000000&\4c&H000000&\c&HFFFFFF&\fscx70\fscy70\t(0,200,\fry250)\t(200,300,\fry180)\t(300,400,\fry250)\t(400,500,\fry180)\t(500,600,\fry250)\t(600,700,\fry180)\t(700,800,\fry250)\t(800,900,\fry180)\t(900,1000,\fry250)\t(1000,1100,\fry180)\t(1100,1300,\fry250)\t(1300,1450,\fry180)\t(1450,1600,\fry250)\t(1600,1700,\fry180)\t(1700,1850,\fry250)\t(1850,2000,\fry180)\t(2000,2200,\fry250)\t(2200,2300,\fry180)\t(2300,2400,\fry250)\t(2400,2700,\fry180)\p1}!wing[1]!")

# L1: Angel halo ring above syl (FROM REFERENCE — vòng thiên sứ)
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 5,,0,0,0,template noblank notext,!retime(""syl"",-25,500)!{\frz5\fscx100\fscy50\an5\blur2\fad(0,300)\move(`$scenter,!`$smiddle-40!,!`$scenter-50!,!`$smiddle-90!)\bord1\3c&H00FCFF&\c&HC7FEFF&\p1}m 0 25 b 1 10 50 11 50 25 b 51 40 -1 40 0 25 m 2 23 b -5 38 49 39 49 25 b 50 14 6 11 2 23 ")

# L1: Text highlight — bold glow + drift (FROM REFERENCE)
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 5,,0,0,0,template syl furi noblank,!retime(""syl"",-25,500)!{\an5\blur2\fad(0,300)\move(`$scenter,`$smiddle,!`$scenter-50!,!`$smiddle-50!)\t(0,25,\bord10\blur3)\t(25,`$dur,\frz5\3c&HFFFFFF&\fscx100\fscy100\bord5\blur2)}")

# L1: Feather lead-in per char (FROM REFERENCE — staggered feathers before text)
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 5,,0,0,0,template char notext,!char_counter5(1)!!retime(""start2syl"",-900+(ci5[1]-1)*20,500+(ci5[1]-1)*25)!{\fad(0,100)\1c&HFFFFFF&\3c&HEBBEBE&\bord1\blur2\fscx50\fscy50\an5\frz!math.random(-100,0)!\move(`$scenter,`$smiddle,!`$scenter+math.random(-50,50)!,!`$smiddle+math.random(-50,50)!)\fad(230,0)\t(0,!line.duration!,\fscy90\fscx90\frz!math.random(-700,700)!\fry!math.random(-700,700)!\frx!math.random(-700,700)!)\p3}!glitzerding[1]!")

# L0: Music notes floating up (2 per syl)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 5,,0,0,0,template syl loop 2 noblank notext,!retime(""syl"",-50+j*200,600)!{\an5\move(!`$center+math.random(-30,30)!,!`$middle!,!`$center+math.random(-40,40)!,!`$middle-math.random(40,70)!)\1c!pastel[math.random(5)]!\blur1\bord0\fscx!math.random(60,100)!\fscy!math.random(60,100)!\fad(200,300)\frz!math.random(-15,15)!\p2}!note[math.random(3)]!")

[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# ============================================================
# OPJP 6: Outro (3:44+) — Single line, gentle farewell
# Simple fade + tiny flowers + sparkle — minimalist ending
# ============================================================

# L1: Text: gentle fade in/out
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 6,,0,0,0,template syl furi noblank,!retime(""syl"",0,0)!{\an5\pos(`$scenter,`$smiddle)\fscx100\fscy100\t(0,200,\fscx120\fscy120)\t(200,`$dur,\3c&HFFFFFF&\fscx100\fscy100)}")

# L0: Lead-in
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 6,,0,0,0,template syl furi noblank char,!retime(""start2syl"",-100,0)!{\an5\pos(`$scenter,`$smiddle)\3c&HFFFFFF&\fscy130\t(0,500,\fscy100)\fad(500,0)}")

# L1: Lead-out
[void]$out.Add("Comment: 1,0:00:00.00,0:00:00.00,OPJP 6,,0,0,0,template syl furi noblank char,!retime(""syl2end"",0,0)!{\an5\pos(`$center,`$middle)\fad(0,300)}")

# L0: Tiny flowers drifting (2 per syl)
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 6,,0,0,0,template syl loop 2 noblank notext,!retime(""syl"",-100+j*300,800)!{\an5\move(!`$center+math.random(-30,30)!,!`$middle!,!`$center+math.random(-50,50)!,!`$middle-math.random(30,60)!)\c!mau[math.random(4)]!\bord0\fscx!math.random(20,40)!\fscy!math.random(20,40)!\fad(200,400)\frz!math.random(-100,100)!\p1}!hoa[math.random(3)]!")

# L0: Sparkle
[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPJP 6,,0,0,0,template syl loop 2 noblank notext,!retime(""syl"",-50+j*200,400)!{\an5\pos(!`$center+math.random(-25,25)!,!`$middle+math.random(-15,15)!)\1c&HFFFFFF&\blur1\bord0\fscx!math.random(30,60)!\fscy!math.random(30,60)!\fad(150,300)\frz!math.random(0,180)!\p2}!star[1]!")

[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# ============================================================
# OPCN: Chinese translation — simple fade (FROM REFERENCE)
# Bottom-aligned, matching pink style
# ============================================================

[void]$out.Add("Comment: 0,0:00:00.00,0:00:00.00,OPCN,,0,0,0,template line,{\fad(300,300)}")

[void]$out.Add("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")

# === Functions ===
function TimeToMs([string]$t) {
    if ($t -match "(\d+):(\d+):(\d+)\.(\d+)") {
        return ([int]$matches[1]*3600+[int]$matches[2]*60+[int]$matches[3])*1000+[int]$matches[4]*10
    }
    return 0
}

function Assign-Style([int]$ms, [string]$stripped) {
    # === taisetsu ga kikoeru section mapping ===
    # All thresholds in strictly ascending order; each boundary = first ms of NEXT section
    
    # Intro (0:01.27 - 0:25.46): feather + scale pulse
    if ($ms -lt 26000) { return "OPJP" }
    
    # Verse 1 (0:26.38 - 0:50.98): music notes + fly-in
    if ($ms -lt 51000) { return "OPJP 2" }
    
    # Pre-chorus 1 (0:51.39 - 0:57.36): scale pulse + sparkle
    if ($ms -lt 57800) { return "OPJP 3" }
    
    # Chorus 1 (0:57.90 - 1:25.74): flowers + feathers + HSV rainbow
    if ($ms -lt 86000) { return "OPJP 4" }
    
    # Interlude vocal (1:29.86 - 1:35.32): butterfly + halo
    if ($ms -lt 96000) { return "OPJP 5" }
    
    # Verse 2 (1:36.46 - 1:48.67): music notes
    if ($ms -lt 110000) { return "OPJP 2" }
    
    # Pre-chorus 2 (1:50.11 - 2:06.01): scale pulse + sparkle
    if ($ms -lt 126000) { return "OPJP 3" }
    
    # Transition (2:06.46 - 2:12.60): music notes
    if ($ms -lt 142000) { return "OPJP 2" }
    
    # Bridge active (2:22.37 - 2:31.53): butterfly + halo
    if ($ms -lt 152000) { return "OPJP 5" }
    
    # Bridge narration (2:32.22 - 2:41.51): scale pulse
    if ($ms -lt 162000) { return "OPJP 3" }

    # Chorus-like (2:41.92 - 3:04.44): flowers
    if ($ms -lt 185000) { return "OPJP 4" }

    # Buildup (3:04.67 - 3:10.24): scale pulse
    if ($ms -lt 190500) { return "OPJP 3" }
    
    # Final Chorus (3:10.48 - 3:25.94): flowers
    if ($ms -lt 208000) { return "OPJP 4" }
    
    # Coda (3:28.41 - 3:44.54): butterfly
    if ($ms -lt 224760) { return "OPJP 5" }
    
    # Outro (3:44.76+): gentle fade + tiny flowers
    return "OPJP 6"
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
                
                # === Context overrides ===
                
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
                    # かなしい顔 standalone: 顔=かお
                    if (-not $plain.Contains([string][char]0x7B11+[string][char]0x9854)) {
                        $r = [string][char]0x304B+[string][char]0x304A  # かお
                    }
                }
                
                # 明日(あした): 明=あし (default), 日=た
                if ($code -eq 0x65E5) {  # 日
                    if ($plain.Contains([string][char]0x660E+[string][char]0x65E5)) {
                        $r = [string][char]0x305F  # た
                    }
                    # 今日(きょう): 日=う
                    if ($plain.Contains([string][char]0x4ECA+[string][char]0x65E5)) {
                        $r = [string][char]0x3046  # う
                    }
                }
                
                # 今日(きょう): 今=きょ
                if ($code -eq 0x4ECA) {  # 今
                    if ($plain.Contains([string][char]0x4ECA+[string][char]0x65E5)) {
                        $r = [string][char]0x304D+[string][char]0x3087  # きょ
                    }
                }
                
                # 歌声(うたごえ): 声=ごえ (default こえ)
                if ($code -eq 0x58F0) {  # 声
                    if ($plain.Contains([string][char]0x6B4C+[string][char]0x58F0)) {
                        $r = [string][char]0x3054+[string][char]0x3048  # ごえ
                    }
                    # 声枯らして: 声=こえ (default OK)
                }
                
                # 鐘の音(かねのね): 音=ね (default おと)
                if ($code -eq 0x97F3) {  # 音
                    if ($plain.Contains([string][char]0x97F3+[string][char]0x3084)) {  # 音や
                        $r = [string][char]0x306D  # ね
                    }
                }
                
                # 歌=うた in this song
                if ($code -eq 0x6B4C) {  # 歌
                    $r = [string][char]0x3046+[string][char]0x305F  # うた
                }
                
                # 大切(たいせつ): 大=たい
                if ($code -eq 0x5927) {  # 大
                    if ($plain.Contains([string][char]0x5927+[string][char]0x5207)) {
                        $r = [string][char]0x305F+[string][char]0x3044  # たい
                    }
                }
                
                # 寄(よ)りそってる: 寄=よ
                if ($code -eq 0x5BC4) {  # 寄
                    $r = [string][char]0x3088  # よ
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
    
    # Skip artist/info lines (before song starts)
    if ($ms -lt 1200) { continue }
    
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
    
    [void]$out.Add("Dialogue: 0,$start,$end,OPCN,,0,0,0,,$text")
    $cnCount++
}

Write-Host "CN lines: $cnCount"

# Write
[System.IO.File]::WriteAllLines($outputFile, $out.ToArray(), $utf8Bom)
Write-Host ""
Write-Host "SUCCESS! $outputFile"
Write-Host "Total: $($out.Count) lines"
Write-Host ""
Write-Host "=== Effect Summary (v3 - Cute Pop Style) ==="
Write-Host "OPJP  (Intro):   Scale pulse + feather float + sparkle stars    [Gentle opening]"
Write-Host "OPJP 2 (Verse):  Music notes + heart scatter + char fly-in      [Musical narrative]"
Write-Host "OPJP 3 (Pre-ch): Scale pulse + star sparkle + pastel glow       [Warm buildup]"
Write-Host "OPJP 4 (Chorus): Flowers + feathers + HSV rainbow + hearts      [Maximum cute]"
Write-Host "OPJP 5 (Bridge): Butterfly flutter + angel halo + feather lead  [Ethereal angels]"
Write-Host "OPJP 6 (Outro):  Scale pulse + tiny flowers + sparkle           [Gentle farewell]"
Write-Host "OPCN  (Chinese): Simple fade                                     [Clean bottom text]"
Write-Host ""
Write-Host "Color: Pink-Magenta #F04BAF + White outline (matching anime palette)"
Write-Host "Font:  FOT-PopJoy Std B (JP) + FangZheng ShaoEr (CN)"
