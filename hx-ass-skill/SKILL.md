---
name: hx-ass-skill
description: This skill should be used when the user wants to create anime-themed ASS karaoke effects (KFX) from K-timed lyrics. It covers the full workflow from analyzing K-framed ASS files (Japanese + Chinese + optional romaji) to producing high-quality, themed ASS lyric files with furigana annotations and visual effects matching the anime's OP/ED style. The output is in pre-template state (before Aegisub's "Apply Karaoke Template"). This skill should also be used when recording case study experience after a successful KFX production.
---

# HX ASS Skill — 番剧主题 ASS 卡拉OK特效制作

## Overview

Transform K-framed ASS lyrics (Japanese + Chinese translation + optional romaji) into high-quality, anime-themed ASS karaoke effect files with furigana annotations. Output is in pre-template state — ready for Aegisub's "Apply Karaoke Template" execution. The production process may require web searches for anime information.

## Workflow

### Step 1: Analyze Input

Parse the K-framed ASS file: identify tracks (orig/ts/roma), count lines and duration, extract timestamps, convert `\kf` → `\k` tags.

Search anime info on [萌娘百科](https://zh.moegirl.org.cn/) and [bgm.tv](https://bgm.tv/) — gather genre, visual style, character colors, confirm OP/ED/Insert position.

Read through lyrics (Japanese + Chinese) to determine emotional tone per section.

→ Design methodology: `references/设计思想/OPED歌词特效设计思路.md`

### Step 2: Design & Plan

Select design school(s) and effect combinations based on anime theme and song emotion. Divide the song into segments (Intro/Verse/Chorus/Bridge/Coda), assign a Style to each line, build a time-threshold table.

Choose reference templates from the asset library. Determine color scheme in `&HBBGGRR&` (BGR) format.

→ **Past case studies (most important)**: `assets/案例/` — 4 complete productions with build scripts, 制作记录, and output files. Always review relevant cases first.
→ KFX reference works: `assets/music-ass/`
→ Seekladoom collection: `assets/Seekladoom-ASS-Effect-master/`
→ Material templates: `assets/素材库/` (8 categories, see `references/素材库索引.md`)

### Step 3: Build Furigana

Load `furigana_map.txt` (project root, shared across songs, 218+ entries). Scan Japanese lines for CJK kanji, apply context-dependent overrides (e.g. 一人→ひと, 笑顔→えがお), embed using `|<` syntax.

For new kanji not in the map, look up the correct reading and append to `furigana_map.txt`.

→ Full furigana guide: `references/知识库/日语注音(Furigana)编写与特效同步教程.md`

### Step 4: Assemble Template

Two pipelines exist — prefer Aegisub Template pipeline unless the reference is purely hand-crafted:

**Aegisub Template pipeline**: Create `build_kfx_{song}.ps1`. Merge Script Info + Styles + code/template Comment lines + karaoke source lines + Chinese translation lines into one ASS file.

**Python pre-render pipeline**: Create `build_kfx_{song}.py`. Generate all fx Dialogue lines directly. Run with `python -X utf8`.

Critical rules:
- Use `syl furi` combined modifier for furigana sync (never standalone `template furi`)
- Convert `\kf` → `\k` (Aegisub Templater only recognizes `\k`)
- Chinese lines: `\fad(300,300)` for standard, `\pos(x,600)` for chorus sections

→ ASS tag reference: `references/技术手册/ASS特效标签速查.md`
→ Full ASS knowledge base: `references/知识库/ASS-Effect-Knowledge-Base.md`

### Step 5: Validate & Debug

Check output line count (Template: 150~300, Python: 3000~10000+). Search specific kanji in output fx lines and compare with reference files.

Common issues: `unicode.len` needs wrapping parentheses, missing Default style, furigana not syncing, animation overlap between adjacent lines.

→ Automated validator: `scripts/validate_kfx.py`

### Step 6: Fine-tune

Adjust colors, timing, positions, particle parameters on actual video preview. Ensure smooth transitions between sections.

### Step 7: Record Case Experience (ref)

**Execute after every satisfactory production.** Create directory `assets/案例/{song_name}/` containing: 制作记录.md + build script + k帧.ass + 成品_KFX.ass.

→ Automated case recorder: `scripts/record_case.py`
→ Existing cases for reference: `assets/案例/`

## Resources

### scripts/

| Script | Purpose |
|--------|---------|
| `validate_kfx.py` | Validate KFX output: line count, styles, furigana presence, timing |
| `record_case.py` | Create case study directory structure and template for Step 7 |

### references/

Reference documentation loaded into context as needed:

| File | Content |
|------|---------|
| `设计思想/OPED歌词特效设计思路.md` | 5 design schools + emotion-effect mapping table |
| `技术手册/ASS特效标签速查.md` | ASS override tags: color, position, animation, clip, drawing |
| `知识库/ASS-Effect-Knowledge-Base.md` | Complete ASS effect knowledge base (Seekladoom) |
| `知识库/日语注音(Furigana)编写与特效同步教程.md` | Furigana writing + `syl furi` sync tutorial |
| `素材库索引.md` | Index of material library categories |

### assets/

Files used in output — template .ass files, reference works, and case archives:

| Directory | Content |
|-----------|---------|
| `案例/` | **4 complete production case studies** — each contains 制作记录.md (design decisions, problems solved, lessons learned), build script, K-framed input, and output KFX. **Always consult before starting a new production.** |
| `music-ass/` | Complete KFX reference works (天使の3P, Charlotte, 点兔, MIA, 命运石之门, ヨスガノソラ) |
| `Seekladoom-ASS-Effect-master/` | 86 K-timed subtitle files + effect templates + drawing code |
| `素材库/` | 8 categories of reusable .ass templates (01-基础模板 through 08-绘图代码) |
