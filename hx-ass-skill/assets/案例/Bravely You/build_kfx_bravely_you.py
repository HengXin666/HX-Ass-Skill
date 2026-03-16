"""
build_kfx_bravely_you.py
Generates a pre-rendered KFX ASS file for Bravely You (full version).

Faithfully reproduces the Charlotte reference file's effect system:
- Per-syllable star flash + ripple rings triggered at k-frame times
- Echo/回音 (OPJP-B) lines: katakana echo repeating the main singer's words
- Multi-color distribution: different colors for different words within the same line
- 5 layers per syllable: Main text (L2), Star (L4), Ring x2 (L0), Glow (L1)
- Rapid chanting (OPJP-A/C): scale-in fade effect
- Chinese translation with synchronized display

Output: Final pre-rendered ASS file (no Apply Template needed).
"""
import sys, re, os, math

sys.stdout.reconfigure(encoding='utf-8')

# === Paths ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REF_FILE = os.path.join(SCRIPT_DIR, "reference", "music-ass", "Charlotte", "Lia - Bravely You.ass")
INPUT_FILE = r"C:\Users\Heng_Xin\Documents\Lyrics\Lia - Bravely You (28055813).ass"
FURI_FILE = os.path.join(SCRIPT_DIR, "furigana_map.txt")

base = os.path.splitext(INPUT_FILE)[0]
OUTPUT_FILE = base + "_KFX.ass"

print(f"Ref:  {REF_FILE}")
print(f"In:   {INPUT_FILE}")
print(f"Out:  {OUTPUT_FILE}")

# === Read files ===
with open(REF_FILE, 'r', encoding='utf-8-sig') as f:
    ref_lines = f.read().splitlines()

with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
    input_lines = f.read().splitlines()

# === Load furigana map ===
furi_map = {}
if os.path.exists(FURI_FILE):
    with open(FURI_FILE, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if '=' in line:
                kanji, reading = line.split('=', 1)
                furi_map[kanji.strip()] = reading.strip()
    print(f"Furigana map: {len(furi_map)} entries")
else:
    print("WARNING: furigana_map.txt not found!")


def is_kanji(ch):
    """Check if a character is a CJK kanji that needs furigana."""
    code = ord(ch)
    return 0x4E00 <= code <= 0x9FFF


def get_furigana(text):
    """Get furigana reading for a syllable text.
    Returns list of (kanji_char, reading) pairs for kanji chars that have readings.
    Non-kanji chars return empty list.
    """
    result = []
    for ch in text:
        if is_kanji(ch) and ch in furi_map:
            result.append((ch, furi_map[ch]))
    return result


# === Time helpers ===
def time_to_ms(t):
    m = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', t)
    if m:
        h, mi, s, cs = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        return (h * 3600 + mi * 60 + s) * 1000 + cs * 10
    return 0

def ms_to_time(ms):
    if ms < 0:
        ms = 0
    h = ms // 3600000
    ms %= 3600000
    mi = ms // 60000
    ms %= 60000
    s = ms // 1000
    cs = (ms % 1000) // 10
    return f"{h}:{mi:02d}:{s:02d}.{cs:02d}"


# === Shapes ===
STAR_SHAPE = "m 17 0 b 18 16 18 16 34 17 b 18 18 18 18 17 34 b 16 18 16 18 0 17 b 16 16 16 16 17 0"
RING_SHAPE = "m 33 0 b 66 0 66 50 33 50 b 0 50 0 0 33 0 l 33 1 b 1 1 1 49 33 49 b 65 49 65 1 33 1"


# === Colors (from reference) ===
C_BLUE_PURPLE = '&HBA4561&'
C_PURPLE = '&H672791&'
C_GREEN = '&H45C043&'
C_TEAL = '&HA06E31&'
COLORS = [C_BLUE_PURPLE, C_PURPLE, C_GREEN, C_TEAL]


# === Parse input file ===
orig_lines = []
ts_lines = []
for line in input_lines:
    m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+),\s*(orig|ts)\s*,', line)
    if not m:
        continue
    start, end, style = m[1], m[2], m[3]
    parts = line.split(',', 9)
    if len(parts) < 10:
        continue
    text = parts[9]
    ms = time_to_ms(start)
    entry = {'start': start, 'end': end, 'ms': ms, 'end_ms': time_to_ms(end), 'text': text}
    if style == 'orig':
        orig_lines.append(entry)
    elif style == 'ts':
        ts_lines.append(entry)

print(f"Input: {len(orig_lines)} orig, {len(ts_lines)} ts lines")


# === Parse k-tags from text ===
def parse_k_tags(text):
    """Parse {\kf?N}char sequences into syllable list.
    Returns list of (k_value_cs, syllable_text) tuples.
    k_value_cs is in centiseconds (10ms units).
    """
    syllables = []
    pattern = re.finditer(r'\{\\kf?(\d+)\}([^{]*)', text)
    for m in pattern:
        k_val = int(m.group(1))
        syl_text = m.group(2)
        syllables.append((k_val, syl_text))
    return syllables


# === Estimate character width ===
def char_width(ch):
    """Estimate character width in pixels at font size ~40."""
    code = ord(ch)
    if code <= 0x7F:  # ASCII
        if ch == ' ':
            return 16
        return 22
    elif 0xFF01 <= code <= 0xFF5E:  # Fullwidth
        return 40
    elif 0x3000 <= code <= 0x303F:  # CJK symbols
        return 40
    elif 0x3040 <= code <= 0x309F:  # Hiragana
        return 40
    elif 0x30A0 <= code <= 0x30FF:  # Katakana
        return 40
    elif 0x4E00 <= code <= 0x9FFF:  # CJK Unified
        return 40
    else:
        return 40

def text_width(text):
    """Estimate text width in pixels."""
    return sum(char_width(ch) for ch in text)

def syllable_width(syl_text):
    """Width of a syllable's text."""
    return text_width(syl_text)


# === Layout helpers ===
SCREEN_W = 1280
MAIN_Y = 690       # Main text Y position (from reference)
ECHO_Y = 630       # Echo text Y position (raised 20px from 650)
CHANT_Y = 650      # Rapid chanting Y position


def compute_positions(syllables, center_x=None):
    """Compute X positions for each syllable, centered on screen.
    Returns list of (center_x, width) for each syllable.
    """
    widths = []
    for k, text in syllables:
        if text.strip():
            widths.append(syllable_width(text))
        else:
            widths.append(syllable_width(text) if text else 0)
    
    total_w = sum(widths)
    if center_x is None:
        center_x = SCREEN_W // 2
    
    start_x = center_x - total_w // 2
    positions = []
    current_x = start_x
    for w in widths:
        cx = current_x + w // 2
        positions.append((cx, w))
        current_x += w
    
    return positions


# =====================================================
# OPCN CHARACTER FX: Horizontal-slice enter + Vertical-slice exit
# Reference: each char gets 4 enter strips + 4 exit strips (8 lines total)
# =====================================================
import random as _rand

def gen_cn_char_fx(ch, ch_x, ch_y, enter_start_ms, enter_end_ms, color, style='OPCN'):
    """
    Generate 8 ASS Dialogue lines for one Chinese character's clip-slice effect.
    
    Enter: 4 horizontal strips, each fscx240 → fscx100 with clip animation (300ms)
    Exit: 4 vertical strips, each fscy240 + scatter (300ms)
    
    ch_x: character center X
    ch_y: character center Y (typically 30 for reference)
    enter_start_ms: when enter animation starts (typically line_start - 300ms)
    enter_end_ms: when this char's enter ends (slightly staggered per char)
    color: \3c color like &H672791&
    """
    lines = []
    
    # ----- ENTER: 4 horizontal bands -----
    # Band definitions: (y1, y2) relative to character
    bands = [(-70, 20), (20, 30), (30, 40), (40, 130)]
    clip_half_w = 100  # clip width = 200px centered on char
    
    for bi, (by1, by2) in enumerate(bands):
        # Random horizontal offset: alternate left/right, magnitude ~15-25
        offset = _rand.randint(15, 25) * ((-1) ** bi)
        
        # Initial clip (offset from final position)
        init_clip_x1 = ch_x - clip_half_w + offset
        init_clip_x2 = ch_x + clip_half_w + offset
        # Final clip (centered on char)
        final_clip_x1 = ch_x - clip_half_w
        final_clip_x2 = ch_x + clip_half_w
        
        init_move_x = ch_x + offset
        
        tags = (f"{{\\an5\\blur3\\fad(140,0)\\3c{color}"
                f"\\fscx240\\clip({init_clip_x1},{by1},{init_clip_x2},{by2})"
                f"\\t(0,300,\\fscx100"
                f"\\clip({final_clip_x1},{by1},{final_clip_x2},{by2})"
                f"\\move({init_move_x},{ch_y},{ch_x},{ch_y},0,300))}}")
        
        lines.append(f"Dialogue: 0,{ms_to_time(enter_start_ms)},{ms_to_time(enter_end_ms)},{style},,0,0,0,fx,{tags}{ch}")
    
    # ----- EXIT: 4 vertical bands -----
    exit_start_ms = enter_end_ms
    exit_end_ms = enter_end_ms + 300
    
    # Vertical band definitions: (x_offset_left, x_offset_right)
    v_bands = [(-clip_half_w, -10), (-10, 0), (0, 10), (10, clip_half_w)]
    
    for vi, (vx1_off, vx2_off) in enumerate(v_bands):
        vx1 = ch_x + vx1_off
        vx2 = ch_x + vx2_off
        
        # Random vertical offset for scatter: alternate up/down, magnitude ~15-20
        v_offset = _rand.randint(15, 22) * ((-1) ** vi)
        
        # Exit clip animation: from full height to shifted
        init_clip = f"{vx1},-70,{vx2},130"
        final_clip = f"{vx1},{-70 - v_offset},{vx2},{130 - v_offset}"
        
        final_y = ch_y - v_offset
        
        tags = (f"{{\\an5\\blur3\\fad(0,140)\\3c{color}"
                f"\\clip({init_clip})"
                f"\\t(0,300,\\fscy240"
                f"\\clip({final_clip})"
                f"\\move({ch_x},{ch_y},{ch_x},{final_y},0,300))}}")
        
        lines.append(f"Dialogue: 0,{ms_to_time(exit_start_ms)},{ms_to_time(exit_end_ms)},{style},,0,0,0,fx,{tags}{ch}")
    
    return lines


# =====================================================
# SONG STRUCTURE & COLOR ASSIGNMENT
# =====================================================

def get_section(ms):
    """Determine song section from timestamp."""
    if ms < 7000:
        return 'info'
    if ms < 48700:
        return 'slow'       # Intro/Verse - OPJP with star/ripple
    if ms < 61390:
        return 'chant1'     # Rapid chanting 1 - OPJP-A/C
    if ms < 99820:
        return 'chorus1'    # Chorus 1 - OPJP with star/ripple
    if ms < 141490:
        return 'verse2'     # Verse 2 - OPJP with star/ripple
    if ms < 154300:
        return 'chant2'     # Rapid chanting 2
    if ms < 186350:
        return 'chorus2'    # Chorus 2
    if ms < 243930:
        return 'bridge'     # Bridge
    if ms < 256630:
        return 'chant3'     # Rapid chanting 3
    return 'final'          # Final chorus


# =====================================================
# Define echo pairs for slow/verse sections
# Reference: main singer sings kanji, echo sings katakana
# =====================================================
# Format: (main_orig_ms_approx, echo_words)
# echo_words: list of (katakana_text, delay_after_word_start_ms)

ECHO_DEFINITIONS = {
    # Section 1: きみは...聴いてた (23170ms)
    23170: {
        'words': [
            {'main_text': 'きみは', 'echo_text': 'キミは', 'echo_delay': 2040},
            {'main_text': 'ひとり', 'echo_text': 'ヒトリ', 'echo_delay': 5170},
            {'main_text': '何を', 'echo_text': 'ナニも', 'echo_delay': 8460},
            {'main_text': '聴いてた', 'echo_text': '聴こえない', 'echo_delay': 11590},
        ],
        'echo_duration': 1370,
    },
    # Section 2: 僕は...見てた (35890ms)
    35890: {
        'words': [
            {'main_text': '僕は', 'echo_text': 'ボクは', 'echo_delay': 2160},
            {'main_text': '遠い', 'echo_text': 'とおい', 'echo_delay': 5330},
            {'main_text': '夢を', 'echo_text': 'ユメを', 'echo_delay': 8550},
            {'main_text': '見てた', 'echo_text': '見えない', 'echo_delay': 11670},
        ],
        'echo_duration': 1250,
    },
    # Section 3: 卑怯だったずっと僕は (115920ms) - Verse 2 echo part 1
    # JP word starts: 卑怯@0, だった@3100, ずっと@6260, 僕は@9550
    # echo_delay ≈ word_start + 2100ms (consistent lag from reference pattern)
    # Echo text: katakana equivalent / contrasting echo
    115920: {
        'words': [
            {'main_text': '卑怯', 'echo_text': 'ヒキョウ', 'echo_delay': 2100},
            {'main_text': 'だった', 'echo_text': 'ダッタ', 'echo_delay': 5200},
            {'main_text': 'ずっと', 'echo_text': 'ズット', 'echo_delay': 8360},
            {'main_text': '僕は', 'echo_text': 'ボクは', 'echo_delay': 11650},
        ],
        'echo_duration': 1300,
    },
    # Section 4: きみはいつも向こう見ずだった (128640ms) - Verse 2 echo part 2
    128640: {
        'words': [
            {'main_text': 'きみは', 'echo_text': 'キミは', 'echo_delay': 2200},
            {'main_text': 'いつも', 'echo_text': 'イツモ', 'echo_delay': 5400},
            {'main_text': '向こう見ず', 'echo_text': 'ムコウミズ', 'echo_delay': 8600},
            {'main_text': 'だった', 'echo_text': 'ダッタ', 'echo_delay': 11600},
        ],
        'echo_duration': 1300,
    },
}


# =====================================================
# OPCN WORD-BY-WORD DEFINITIONS for "slow" stacked sections
# Reference: words appear one by one within a fixed grid, each with different color
# Grid: 13 slots, 40px each, centered on screen
# =====================================================
OPCN_WORD_BY_WORD = {
    # ts line: "你独自一人 世间万物皆入你耳" (23170ms-35890ms)
    # Reference Comment start times: 孤獨的@23540 → 你@26710 → 聽到了@29960 → 什麼@33170
    # delay = Comment_start - line_start (verified from reference ENTER = delay - 300)
    23170: {
        'section_end_ms': 35890,  # All words exit together at section end
        'words': [
            {'text': '独自一人', 'color': C_GREEN,        'delay': 370,   'grid_slots': [0, 1, 2, 3]},
            {'text': '你',       'color': C_TEAL,         'delay': 3540,  'grid_slots': [5]},
            {'text': '听到了',   'color': C_TEAL,         'delay': 6790,  'grid_slots': [7, 8, 9]},
            {'text': '什么',     'color': C_TEAL,         'delay': 10000, 'grid_slots': [11, 12]},
        ],
    },
    # ts line: "而我一直凝望着遥远的梦" (35890ms-48700ms)
    # Reference Comment start times: 我@36340 → 看到了@39510 → 遙遠的@42770 → 幻夢@45940
    35890: {
        'section_end_ms': 48700,
        'words': [
            {'text': '我',       'color': C_TEAL,         'delay': 450,   'grid_slots': [0]},
            {'text': '看到了',   'color': C_TEAL,         'delay': 3620,  'grid_slots': [3, 4, 5]},
            {'text': '遥远的',   'color': C_BLUE_PURPLE,  'delay': 6880,  'grid_slots': [7, 8, 9]},
            {'text': '幻梦',     'color': C_BLUE_PURPLE,  'delay': 10050, 'grid_slots': [11, 12]},
        ],
    },
    # Verse 2 echo section 1: "裹足不前的我不过是个懦夫" (115920ms-128640ms)
    # JP word starts: 卑怯@0, だった@3100, ずっと@6260, 僕は@9550
    # CN delay ≈ word_start + 370ms (following reference pattern)
    # 12 chars in 4 groups: 4+2+4+2, fits in 13-slot grid with 1 gap
    115920: {
        'section_end_ms': 128640,
        'words': [
            {'text': '裹足不前', 'color': C_GREEN,        'delay': 370,   'grid_slots': [0, 1, 2, 3]},
            {'text': '的我',     'color': C_TEAL,         'delay': 3470,  'grid_slots': [5, 6]},
            {'text': '不过是个', 'color': C_PURPLE,        'delay': 6630,  'grid_slots': [7, 8, 9, 10]},
            {'text': '懦夫',     'color': C_BLUE_PURPLE,  'delay': 9920,  'grid_slots': [11, 12]},
        ],
    },
    # Verse 2 echo section 2: "而你却总是顾前不顾后" (128640ms-141490ms)
    # JP word starts: きみは@0, いつも@3230, 向こう見ず@6220, だった@9510
    # CN delay ≈ word_start + 370ms (following reference pattern)
    128640: {
        'section_end_ms': 141490,
        'words': [
            {'text': '而你',     'color': C_TEAL,         'delay': 370,   'grid_slots': [0, 1]},
            {'text': '却总是',   'color': C_PURPLE,        'delay': 3600,  'grid_slots': [3, 4, 5]},
            {'text': '顾前不顾后', 'color': C_BLUE_PURPLE, 'delay': 6590, 'grid_slots': [7, 8, 9, 10, 11]},
        ],
    },
}

# Color assignment for slow/verse sections - per word/group
# Maps (line_ms, word_index) to color
# This creates the multi-color effect within a single line
COLOR_MAP_BY_LINE = {
    # Line: 崩れて終わる世界
    7100: [C_BLUE_PURPLE],
    # Line: 無慈悲に告げる
    13430: [C_PURPLE],
    # Line: きみはひとり何を聴いてた (stacked - each word different color!)
    # Input uses hiragana きみは not kanji 君は
    23170: {
        'き': C_PURPLE, 'み': C_PURPLE, 'は': C_PURPLE,
        'ひ': C_GREEN, 'と': C_GREEN, 'り': C_GREEN,
        '何': C_BLUE_PURPLE, 'を': C_BLUE_PURPLE,
        '聴': C_GREEN, 'い': C_GREEN, 'て': C_GREEN, 'た': C_GREEN,
    },
    # Line: 僕は遠い夢を見てた (stacked)
    35890: {
        '僕': C_TEAL, 'は': C_TEAL,
        '遠': C_PURPLE, 'い': C_PURPLE,
        '夢': C_BLUE_PURPLE, 'を': C_BLUE_PURPLE,
        '見': C_PURPLE, 'て': C_PURPLE, 'た': C_PURPLE,
    },
    # Chorus 1
    61390: [C_PURPLE],   # ひとりきりじゃなかった
    64480: [C_PURPLE],   # ずっとそばに居たんだ
    68800: [C_PURPLE],   # この手を伸ばす
    81600: [C_GREEN],    # 恐いものなんかない
    84800: [C_PURPLE],   # 例え化け物になろうとも
    88800: [C_PURPLE],   # 成し遂げる
    # Verse 2
    99820: [C_BLUE_PURPLE],  # あの日を最後にして
    105700: [C_PURPLE],      # 強くなれたか
    115920: {
        '卑': C_GREEN, '怯': C_GREEN,
        'だ': C_PURPLE, 'っ': C_PURPLE, 'た': C_PURPLE,
        'ず': C_BLUE_PURPLE, 'と': C_BLUE_PURPLE,
        '僕': C_TEAL, 'は': C_TEAL,
    },
    128640: {
        'き': C_TEAL, 'み': C_TEAL,
        'い': C_PURPLE, 'つ': C_PURPLE, 'も': C_PURPLE,
        '向': C_BLUE_PURPLE, 'こ': C_BLUE_PURPLE, 'う': C_BLUE_PURPLE, '見': C_BLUE_PURPLE, 'ず': C_BLUE_PURPLE,
        'だ': C_GREEN, 'っ': C_GREEN, 'た': C_GREEN,
    },
    # Chorus 2
    154300: [C_PURPLE],
    157280: [C_BLUE_PURPLE],
    166970: [C_GREEN],
    170130: [C_PURPLE],
    # Bridge
    186350: [C_BLUE_PURPLE],
    189460: [C_PURPLE],
    192680: [C_GREEN],
    195840: [C_TEAL],
    199070: [C_BLUE_PURPLE],
    202230: [C_PURPLE],
    205440: [C_GREEN],
    208660: [C_PURPLE],
    # Final chorus
    256630: [C_PURPLE],
    259680: [C_BLUE_PURPLE],
    269340: [C_GREEN],
    272490: [C_PURPLE],
    274110: [C_BLUE_PURPLE],
    282120: [C_PURPLE],
    285230: [C_GREEN],
    294880: [C_TEAL],
    298040: [C_PURPLE],
}

# Default color cycling for lines without specific mapping
DEFAULT_COLOR_CYCLE = [C_BLUE_PURPLE, C_PURPLE, C_GREEN, C_TEAL]


def get_syllable_color(line_ms, syl_text, syl_index, total_syls, all_syllables=None):
    """Get color for a syllable based on line and position.
    
    For stacked sections (dict mapping), uses syllable index to determine
    which word-group a syllable belongs to, then assigns color accordingly.
    """
    # Check specific color map
    if line_ms in COLOR_MAP_BY_LINE:
        mapping = COLOR_MAP_BY_LINE[line_ms]
        if isinstance(mapping, list):
            return mapping[0]
        elif isinstance(mapping, dict):
            # Per-character mapping - use first char of this syllable's text
            first_char = syl_text[0] if syl_text else ''
            if first_char in mapping:
                return mapping[first_char]
            # Fallback: check if any char in syl_text matches
            for ch in syl_text:
                if ch in mapping:
                    return mapping[ch]
    
    # Default: cycle through colors based on line index
    idx = (line_ms // 1000) % len(DEFAULT_COLOR_CYCLE)
    return DEFAULT_COLOR_CYCLE[idx]


# =====================================================
# FX GENERATION FUNCTIONS
# =====================================================

def gen_main_text(start_ms, end_ms, syl_start_ms, x, y, color, text, line_dur_ms):
    """Layer 2: Main text - appears early with fad, stays until line end.
    Reference: \an5\blur2\fad(200,200)\3c&HCOLOR&\fscx0\fscy0
               \t(0,200,\fscx100\fscy100\blur8)\pos(X,Y)
               \t(line_dur-400,line_dur,\fscx150\fscy150)
    """
    # Main text appears slightly before syllable starts (staggered offset)
    fade_start = start_ms - 400
    if fade_start < 0:
        fade_start = 0
    
    # End expand timing
    expand_start = max(0, line_dur_ms - 400)
    
    tags = (f"{{\\an5\\blur2\\fad(200,200)\\3c{color}"
            f"\\fscx0\\fscy0\\t(0,200,\\fscx100\\fscy100\\blur8)"
            f"\\pos({x},{y})"
            f"\\t({expand_start},{line_dur_ms},\\fscx150\\fscy150)}}")
    
    # End time = fade_start + line_dur_ms (no extra extension — matches reference)
    char_end = fade_start + line_dur_ms
    return f"Dialogue: 2,{ms_to_time(fade_start)},{ms_to_time(char_end)},OPJP,,0,0,0,fx,{tags}{text}"


def gen_star(syl_start_ms, syl_dur_ms, x, y, color):
    """Layer 4: Star diamond flash at syllable start.
    Reference: \an5\p1\alpha&H20&\3c&HCOLOR&\fscx0\fscy0
               \t(0,dur/2,\fscx{sz}\fscy{sz})\t(dur/2,dur,\fscx0\fscy0)
               \blur6\pos(X,Y)
    Position: random offset around the syllable center for natural feel.
    """
    # Star size based on duration, capped
    sz = min(int(syl_dur_ms / 3 + 120), 170)
    half_dur = int(syl_dur_ms / 2)
    full_dur = syl_dur_ms
    
    # Star appears slightly before syllable, lasts about 400-500ms
    star_dur = min(max(full_dur, 400), 600)
    half = star_dur // 2
    
    # Random position offset: ±20px X, ±25px Y (biased downward) around syllable center
    rx = _rand.randint(-20, 20)
    ry = _rand.randint(-10, 25)
    
    tags = (f"{{\\an5\\p1\\alpha&H20&\\3c{color}"
            f"\\fscx0\\fscy0\\t(0,{half},\\fscx{sz}\\fscy{sz})"
            f"\\t({half},{star_dur},\\fscx0\\fscy0)"
            f"\\blur6\\pos({x + rx},{y - 14 + ry})}}")
    
    start_t = syl_start_ms - 200
    end_t = syl_start_ms + star_dur - 200
    
    return f"Dialogue: 4,{ms_to_time(max(0, start_t))},{ms_to_time(end_t)},OPJP,,0,0,0,fx,{tags}{STAR_SHAPE}"


def gen_ring(syl_start_ms, syl_dur_ms, x, y, color, offset_ms=0, start_scale=0):
    """Layer 0: Ripple ring that expands and fades.
    Reference: \an5\p1\blur8\alpha&H20&\3c&HCOLOR&
               \fscx{start}\fscy{start}\t(0,dur*1.1,\fscx{max}\fscy{max})
               \t(dur*0.5,dur*1.1,\blur12\alpha&HFF&)
    Position: random offset around the syllable center for natural feel.
    """
    # Ring max size, capped at 280
    max_sz = min(int(syl_dur_ms * 0.18 + 180), 280)
    expand_dur = int(syl_dur_ms * 1.1) + 300
    fade_start = expand_dur // 2
    
    # Random position offset: ±20px X, ±25px Y (biased downward)
    rx = _rand.randint(-20, 20)
    ry = _rand.randint(-10, 25)
    
    tags = (f"{{\\an5\\p1\\blur8\\alpha&H20&\\3c{color}"
            f"\\fscx{start_scale}\\fscy{start_scale}"
            f"\\t(0,{expand_dur},\\fscx{max_sz}\\fscy{max_sz})"
            f"\\t({fade_start},{expand_dur},\\blur12\\alpha&HFF&)"
            f"\\pos({x + rx},{y - 14 + ry})}}")
    
    start_t = syl_start_ms - 200 + offset_ms
    end_t = syl_start_ms + expand_dur - 200 + offset_ms
    
    return f"Dialogue: 0,{ms_to_time(max(0, start_t))},{ms_to_time(end_t)},OPJP,,0,0,0,fx,{tags}{RING_SHAPE}"


def gen_glow(syl_start_ms, syl_dur_ms, x, y, color, text):
    """Layer 1: Glow text - highlight flash on syllable.
    Reference: \an5\fscx20\fscy20\blur1\fad(100,0)\1a&HFF&\3c&HCOLOR&
               \pos(X,Y)\t(0,200,\fscx120\fscy120\blur4)
               \t(200,dur*0.8,\fscx128\fscy128\blur8)
               \t(dur*0.8,dur*1.6,\blur3\alpha&HFF&)
    """
    phase1 = 200
    phase2 = max(int(syl_dur_ms * 0.8), 250)
    phase3 = max(int(syl_dur_ms * 1.6), 500)
    
    tags = (f"{{\\an5\\fscx20\\fscy20\\blur1\\fad(100,0)\\1a&HFF&\\3c{color}"
            f"\\pos({x},{y})"
            f"\\t(0,{phase1},\\fscx120\\fscy120\\blur4)"
            f"\\t({phase1},{phase2},\\fscx128\\fscy128\\blur8)"
            f"\\t({phase2},{phase3},\\blur3\\alpha&HFF&)}}")
    
    start_t = syl_start_ms - 200
    end_t = syl_start_ms + phase3 - 200
    
    return f"Dialogue: 1,{ms_to_time(max(0, start_t))},{ms_to_time(end_t)},OPJP,,0,0,0,fx,{tags}{text}"


def gen_furigana(start_ms, end_ms, syl_start_ms, x, y, color, kanji_text, reading, syl_w, line_dur_ms):
    """Generate furigana (ruby annotation) lines above the main kanji text.
    
    Uses OPJP-furigana style (font size 20, half of main 40).
    Position: centered above the kanji, offset up by ~30px (1.5 * furigana font height).
    
    Each reading character is placed individually, distributed evenly across
    the width of the main kanji character(s).
    
    Returns list of Dialogue lines for the furigana characters.
    """
    FURI_FONT_SIZE = 20
    FURI_Y_OFFSET = 30  # 1.5 * font_size
    furi_y = y - FURI_Y_OFFSET
    
    # Width of each furigana character (half of main char width since font is half size)
    furi_char_w = 20  # Approximate width of a furigana char at size 20
    
    reading_chars = list(reading)
    n_chars = len(reading_chars)
    
    if n_chars == 0:
        return []
    
    # Center the furigana reading over the kanji
    # Total furigana width
    total_furi_w = n_chars * furi_char_w
    # Start X so that furigana is centered over the kanji character(s)
    furi_start_x = x - total_furi_w // 2
    
    lines = []
    
    # Timing: furigana appears with main text, same stagger
    fade_start = start_ms - 400
    if fade_start < 0:
        fade_start = 0
    expand_start = max(0, line_dur_ms - 400)
    
    for ci, ch in enumerate(reading_chars):
        ch_x = furi_start_x + ci * furi_char_w + furi_char_w // 2
        
        # Furigana uses same animation as main text but with OPJP-furigana style
        tags = (f"{{\\an5\\blur1\\fad(200,200)\\3c{color}"
                f"\\fscx0\\fscy0\\t(0,200,\\fscx100\\fscy100\\blur4)"
                f"\\pos({ch_x},{furi_y})"
                f"\\t({expand_start},{line_dur_ms},\\fscx150\\fscy150)}}")
        
        furi_end = fade_start + line_dur_ms
        line = f"Dialogue: 3,{ms_to_time(fade_start)},{ms_to_time(furi_end)},OPJP-furigana,,0,0,0,fx,{tags}{ch}"
        lines.append(line)
    
    return lines


def gen_echo_syllable(start_ms, end_ms, syl_start_ms, syl_dur_ms, x, y, text, line_end_ms):
    """OPJP-B echo effect: scale in from 200%, fade to white, disappear.
    Reference: \an5\blur4\fad(100,200)\pos(X,650)
               \fscx200\fscy200\t(0,200,\fscx100\fscy100)
               \t(remain-700,remain,\3c&HFFFFFF&)
               \t(remain-300,remain,\blur10\alpha&HFF&)
    """
    remain = line_end_ms - syl_start_ms
    white_start = max(0, remain - 700)
    fade_start = max(0, remain - 300)
    
    tags = (f"{{\\an5\\blur4\\fad(100,200)\\pos({x},{y})"
            f"\\fscx200\\fscy200\\t(0,200,\\fscx100\\fscy100)"
            f"\\t({white_start},{remain},\\3c&HFFFFFF&)"
            f"\\t({fade_start},{remain},\\blur10\\alpha&HFF&)}}")
    
    return f"Dialogue: 0,{ms_to_time(syl_start_ms)},{ms_to_time(line_end_ms)},OPJP-B,,0,0,0,fx,{tags}{text}"


def gen_chant_syllable(syl_start_ms, line_end_ms, x, y, text, style):
    """OPJP-A/C rapid chanting: scale in, fade to white.
    Reference: \an5\blur4\fad(100,200)\pos(X,650)
               \fscx200\fscy200\t(0,200,\fscx100\fscy100)
               \t(remain-700,remain,\3c&HFFFFFF&)
               \t(remain-300,remain,\blur10\alpha&HFF&)
    """
    remain = line_end_ms - syl_start_ms
    white_start = max(0, remain - 700)
    fade_start = max(0, remain - 300)
    
    tags = (f"{{\\an5\\blur4\\fad(100,200)\\pos({x},{y})"
            f"\\fscx200\\fscy200\\t(0,200,\\fscx100\\fscy100)"
            f"\\t({white_start},{remain},\\3c&HFFFFFF&)"
            f"\\t({fade_start},{remain},\\blur10\\alpha&HFF&)}}")
    
    return f"Dialogue: 0,{ms_to_time(syl_start_ms)},{ms_to_time(line_end_ms)},{style},,0,0,0,fx,{tags}{text}"


# =====================================================
# EXTRACT HEADER FROM REFERENCE
# =====================================================
ref_header = []
for i, line in enumerate(ref_lines):
    if line.strip() == '[Events]':
        break
    ref_header.append(line)

print(f"Header lines: {len(ref_header)}")


# =====================================================
# MAIN GENERATION
# =====================================================
out = []

# Part 1: Script Info + Styles
for line in ref_header:
    out.append(line)

# Part 2: Events header
out.append('')
out.append('[Events]')
out.append('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')

# Counters
fx_count = 0
echo_count = 0
chant_count = 0
cn_count = 0
furi_count = 0
color_cycle_idx = 0
chant_idx = 0

# Process each orig line
for ol_idx, ol in enumerate(orig_lines):
    text = ol['text']
    ms = ol['ms']
    end_ms = ol['end_ms']
    
    # Skip info lines
    if ms < 7000:
        continue
    
    section = get_section(ms)
    syllables = parse_k_tags(text)
    
    if not syllables:
        continue
    
    stripped = ''.join(s[1] for s in syllables)
    line_dur_ms = end_ms - ms
    
    # ===== RAPID CHANTING SECTIONS =====
    if section in ('chant1', 'chant2', 'chant3'):
        is_left_jp = (chant_idx % 2 == 0)
        style = 'OPJP-A' if is_left_jp else 'OPJP-C'
        chant_idx += 1
        
        positions = compute_positions(syllables)
        
        # Adjust X offset for A (left) vs C (right) alignment
        if style == 'OPJP-A':
            x_offset = -180  # Shift left
        else:
            x_offset = 180   # Shift right
        
        # Paired disappearing: calculate shared end time
        # A(left) extends to C(right)'s end + 600ms
        # C(right) extends to its own end + 600ms
        if is_left_jp:
            # Look ahead to find the C partner in orig_lines
            jp_pair_end = end_ms + 600  # default
            if ol_idx + 1 < len(orig_lines):
                next_ol = orig_lines[ol_idx + 1]
                next_ol_section = get_section(next_ol['ms'])
                if next_ol_section in ('chant1', 'chant2', 'chant3'):
                    jp_pair_end = next_ol['end_ms'] + 600
            fx_end_jp = jp_pair_end
        else:
            fx_end_jp = end_ms + 600
        
        cumulative_cs = 0
        for si, (k_val, syl_text) in enumerate(syllables):
            if not syl_text.strip():
                cumulative_cs += k_val
                continue
            
            syl_start = ms + cumulative_cs * 10
            x = positions[si][0] + x_offset
            
            fx_line = gen_chant_syllable(syl_start, fx_end_jp, x, CHANT_Y, syl_text, style)
            out.append(fx_line)
            chant_count += 1
            cumulative_cs += k_val
        
        continue
    
    # ===== SLOW / VERSE / CHORUS SECTIONS (OPJP with star+ripple) =====
    positions = compute_positions(syllables)
    
    # Determine color for this line/section
    # Use per-syllable color if available, otherwise cycle
    line_color = DEFAULT_COLOR_CYCLE[color_cycle_idx % len(DEFAULT_COLOR_CYCLE)]
    color_cycle_idx += 1
    
    # Generate spacer line (empty {\p1} line matching reference pattern)
    out.append(f"Dialogue: 2,{ol['start']},{ol['end']},OPJP,,0,0,0,fx," + 
               "{\\p1}" * max(1, len([s for s in syllables if s[1].strip()])))
    
    # Generate per-syllable effects
    cumulative_cs = 0
    for si, (k_val, syl_text) in enumerate(syllables):
        syl_text_stripped = syl_text.strip()
        if not syl_text_stripped:
            cumulative_cs += k_val
            continue
        
        syl_start_ms = ms + cumulative_cs * 10
        syl_dur_ms = k_val * 10
        x = positions[si][0]
        y = MAIN_Y
        
        # Get color for this syllable
        color = get_syllable_color(ms, syl_text_stripped, si, len(syllables))
        
        # Layer 2: Main text (fade in early, stay until line end)
        # Stagger appearance: each syllable appears ~30ms after the previous
        stagger_offset = si * 30
        main_start = ms + stagger_offset
        out.append(gen_main_text(main_start, end_ms, syl_start_ms, x, y, color, syl_text_stripped, line_dur_ms))
        
        # Layer 4: Star flash (at k-frame time)
        out.append(gen_star(syl_start_ms, syl_dur_ms, x, y, color))
        
        # Layer 0: Ripple ring 1 (at k-frame time, from scale 0)
        out.append(gen_ring(syl_start_ms, syl_dur_ms, x, y, color, offset_ms=0, start_scale=0))
        
        # Layer 0: Ripple ring 2 (offset 100ms, from scale 60)
        out.append(gen_ring(syl_start_ms, syl_dur_ms, x, y, color, offset_ms=100, start_scale=60))
        
        # Layer 1: Glow text (at k-frame time)
        out.append(gen_glow(syl_start_ms, syl_dur_ms, x, y, color, syl_text_stripped))
        
        # Layer 3: Furigana (ruby annotations for kanji characters)
        furi_pairs = get_furigana(syl_text_stripped)
        if furi_pairs:
            # Build combined reading for the whole syllable
            combined_reading = ''.join(r for _, r in furi_pairs)
            syl_w = positions[si][1]
            furi_lines = gen_furigana(
                ms + si * 30,  # stagger like main text
                end_ms, syl_start_ms,
                x, y, color, syl_text_stripped, combined_reading,
                syl_w, line_dur_ms
            )
            out.extend(furi_lines)
            furi_count += len(furi_lines)
        
        fx_count += 5
        cumulative_cs += k_val
    
    # ===== ECHO GENERATION (OPJP-B) =====
    if ms in ECHO_DEFINITIONS:
        echo_def = ECHO_DEFINITIONS[ms]
        for word_def in echo_def['words']:
            echo_text = word_def['echo_text']
            echo_start_ms = ms + word_def['echo_delay'] - 500  # Show echo 0.5s earlier
            echo_dur = echo_def['echo_duration']
            echo_end_ms = echo_start_ms + echo_dur
            
            # Parse echo text into individual characters
            echo_chars = list(echo_text)
            total_echo_width = sum(char_width(ch) for ch in echo_chars)
            echo_center_x = SCREEN_W // 2
            echo_start_x = echo_center_x - total_echo_width // 2
            
            # Distribute k-timing evenly across echo characters
            per_char_dur = echo_dur // max(len(echo_chars), 1)
            
            echo_cumul = 0
            current_echo_x = echo_start_x
            for ci, ch in enumerate(echo_chars):
                cw = char_width(ch)
                ch_x = current_echo_x + cw // 2
                ch_start = echo_start_ms + echo_cumul
                
                fx_line = gen_echo_syllable(
                    echo_start_ms, echo_end_ms,
                    ch_start, per_char_dur,
                    ch_x, ECHO_Y, ch, echo_end_ms
                )
                out.append(fx_line)
                echo_count += 1
                
                # Furigana for echo kanji characters
                furi_pairs = get_furigana(ch)
                if furi_pairs:
                    reading = furi_pairs[0][1]
                    echo_line_dur = echo_end_ms - echo_start_ms
                    furi_lines = gen_furigana(
                        echo_start_ms, echo_end_ms, ch_start,
                        ch_x, ECHO_Y, C_BLUE_PURPLE,
                        ch, reading, cw, echo_line_dur
                    )
                    out.extend(furi_lines)
                    furi_count += len(furi_lines)
                
                current_echo_x += cw
                echo_cumul += per_char_dur


# Part: Chinese translation lines
out.append(f"Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,")
out.append('; === CHINESE TRANSLATION ===')

chant_cn_idx = 0
cn_color_cycle_idx = 0
for tl_idx, tl in enumerate(ts_lines):
    ms = tl['ms']
    text = tl['text'].strip()
    if not text:
        continue
    
    section = get_section(ms)
    
    # Determine CN line color: find closest orig line and use its color
    cn_color = DEFAULT_COLOR_CYCLE[cn_color_cycle_idx % len(DEFAULT_COLOR_CYCLE)]
    # Find matching orig line by timestamp
    best_orig_ms = None
    for ol in orig_lines:
        if ol['ms'] <= ms < ol['end_ms'] or abs(ol['ms'] - ms) < 2000:
            best_orig_ms = ol['ms']
            break
    if best_orig_ms is not None and best_orig_ms in COLOR_MAP_BY_LINE:
        mapping = COLOR_MAP_BY_LINE[best_orig_ms]
        if isinstance(mapping, list):
            cn_color = mapping[0]
        elif isinstance(mapping, dict):
            # Use first color in the dict
            cn_color = list(mapping.values())[0]
    elif best_orig_ms is not None:
        # Use cycle color based on line position
        cn_color = DEFAULT_COLOR_CYCLE[(best_orig_ms // 1000) % len(DEFAULT_COLOR_CYCLE)]
    cn_color_cycle_idx += 1
    
    if section in ('chant1', 'chant2', 'chant3'):
        # Rapid chanting CN: PAIRED left-right display
        # Pattern: A(left) appears → C(right) appears → BOTH fade out together → next pair
        # We collect pairs: even index = A(left), odd index = C(right)
        cn_stripped = re.sub(r'\{[^}]+\}', '', text)
        dur_ms = tl['end_ms'] - ms
        
        if not cn_stripped:
            chant_cn_idx += 1
            cn_count += 1
            continue
        
        is_left = (chant_cn_idx % 2 == 0)
        cn_style = 'OPCN-A' if is_left else 'OPCN-C'
        
        # Generate Comment karaoke line
        per_char_cs = max(1, dur_ms // (len(cn_stripped) * 10))
        k_text = ''.join(f'{{\\k{per_char_cs}}}{ch}' for ch in cn_stripped)
        out.append(f"Comment: 0,{tl['start']},{tl['end']},{cn_style},,0,0,0,karaoke,{k_text}")
        
        cn_chars = list(cn_stripped)
        
        # Reference positioning: OPCN-A X ~315-529 (left), OPCN-C X ~751-965 (right), Y=72
        CN_CHANT_Y = 72
        total_cn_w = sum(char_width(ch) for ch in cn_chars)
        if is_left:
            cn_center_x = 422
        else:
            cn_center_x = 858
        cn_start_x = cn_center_x - total_cn_w // 2
        
        # For paired disappearing: find the partner's end time
        # A(left) uses C(right)'s end time as shared end; C uses its own end + 600ms
        # Look ahead to find the partner's timing
        pair_idx = chant_cn_idx
        if is_left:
            # Left line: look ahead for the right partner
            partner_end_ms = tl['end_ms'] + 600  # default
            # Find next ts_line that would be OPCN-C (use tl_idx from enumerate)
            if tl_idx + 1 < len(ts_lines):
                next_tl = ts_lines[tl_idx + 1]
                next_section = get_section(next_tl['ms'])
                if next_section in ('chant1', 'chant2', 'chant3'):
                    # Shared end = right partner's end + 600ms
                    partner_end_ms = next_tl['end_ms'] + 600
            fx_end_ms = partner_end_ms
        else:
            # Right line: its own end + 600ms is the shared end
            fx_end_ms = tl['end_ms'] + 600
        
        fx_start_ms = ms - 200
        per_char_dur_ms = dur_ms // max(len(cn_chars), 1)
        cn_cumul = 0
        current_cn_x = cn_start_x
        
        for ci, ch in enumerate(cn_chars):
            cw = char_width(ch)
            ch_x = current_cn_x + cw // 2
            ch_start = fx_start_ms + 200 + cn_cumul
            
            remain = fx_end_ms - ch_start
            white_start = max(0, remain - 700)
            fade_start_t = max(0, remain - 300)
            
            tags = (f"{{\\an5\\blur4\\fad(100,200)\\pos({ch_x},{CN_CHANT_Y})"
                    f"\\fscx10\\fscy10\\t(0,100,\\fscx140\\fscy140)\\t(100,200,\\fscx100\\fscy100)"
                    f"\\t({white_start},{remain},\\1c&HFFFFFF&)"
                    f"\\t({fade_start_t},{remain},\\blur10\\alpha&HFF&)}}")
            
            out.append(f"Dialogue: 0,{ms_to_time(ch_start)},{ms_to_time(fx_end_ms)},{cn_style},,0,0,0,fx,{tags}{ch}")
            cn_count += 1
            
            current_cn_x += cw
            cn_cumul += per_char_dur_ms
        
        chant_cn_idx += 1
    else:
        # Normal sections: check if this is a word-by-word grid section
        chant_cn_idx = 0
        cn_stripped = re.sub(r'\{[^}]+\}', '', text)
        
        if not cn_stripped:
            cn_count += 1
            continue
        
        CN_FX_Y = 30    # Character center Y (reference uses Y=30 for top area)
        GRID_SLOT_W = 40  # Each grid slot is 40px wide
        GRID_SLOTS = 13   # 13 slots in the grid
        
        if ms in OPCN_WORD_BY_WORD:
            # ===== WORD-BY-WORD GRID MODE =====
            # Words appear one by one at fixed grid positions, each with different color
            # All words stay visible until section end, then exit together
            wbw = OPCN_WORD_BY_WORD[ms]
            section_end = wbw['section_end_ms']
            
            # Calculate grid base X (centered on screen)
            total_grid_w = GRID_SLOTS * GRID_SLOT_W
            grid_base_x = (SCREEN_W - total_grid_w) // 2
            
            for word_def in wbw['words']:
                word_text = word_def['text']
                word_color = word_def['color']
                word_delay = word_def['delay']
                grid_slots = word_def['grid_slots']
                
                # Word appear time: the first char is fully visible at ms + delay
                # Enter animation takes 300ms, so start 300ms before appear time
                # (Reference: ENTER start = Comment start - 300ms)
                word_appear_ms = ms + word_delay
                word_enter_start = word_appear_ms - 300
                
                # Each character in the word maps to a grid slot
                for ci, ch in enumerate(word_text):
                    if ci >= len(grid_slots):
                        break
                    slot_idx = grid_slots[ci]
                    ch_x = grid_base_x + slot_idx * GRID_SLOT_W + GRID_SLOT_W // 2
                    
                    # Stagger exit slightly per char
                    # Exit animation is 300ms, so enter_end = section_end - 300
                    # to finish exit exactly at section_end
                    stagger = _rand.randint(-60, 60)
                    char_enter_end = section_end - 300 + stagger
                    
                    char_fx = gen_cn_char_fx(
                        ch, ch_x, CN_FX_Y,
                        word_enter_start, char_enter_end,
                        word_color, 'OPCN'
                    )
                    out.extend(char_fx)
                    cn_count += 1
            
            # Generate Comment karaoke lines (grid pattern with fullwidth spaces)
            # One Comment per word, showing grid positions
            for word_def in wbw['words']:
                word_delay = word_def['delay']
                word_start = ms + word_delay
                word_text = word_def['text']
                grid_slots = word_def['grid_slots']
                
                # Build grid line with fullwidth spaces for empty slots
                grid_chars = ['\u3000'] * GRID_SLOTS
                for ci, ch in enumerate(word_text):
                    if ci < len(grid_slots):
                        grid_chars[grid_slots[ci]] = ch
                
                # Replace spaces between CJK with half-width space for readability
                per_slot_cs = max(1, (section_end - word_start) // (GRID_SLOTS * 10))
                k_text = ''.join(f'{{\\k{per_slot_cs}}}{ch}' for ch in grid_chars)
                out.append(f"Comment: 0,{ms_to_time(word_start)},{ms_to_time(section_end)},OPCN,,0,0,0,karaoke,{k_text}")
        
        else:
            # ===== NORMAL PER-CHAR CLIP-SLICE MODE =====
            dur_ms = tl['end_ms'] - ms
            
            # Generate Comment karaoke line for reference
            per_char_cs = max(1, dur_ms // (len(cn_stripped) * 10))
            k_text = ''.join(f'{{\\k{per_char_cs}}}{ch}' for ch in cn_stripped)
            out.append(f"Comment: 0,{tl['start']},{tl['end']},OPCN,,0,0,0,karaoke,{k_text}")
            
            # Calculate character positions using actual char widths, centered on screen
            char_widths = [char_width(ch) for ch in cn_stripped]
            total_w = sum(char_widths)
            block_start_x = (SCREEN_W - total_w) // 2
            
            cn_positions = []
            cur_x = block_start_x
            for cw in char_widths:
                cn_positions.append(cur_x + cw // 2)
                cur_x += cw
            
            # Enter starts at line start (no early offset to avoid overlap with prev line)
            enter_start = ms
            
            # Generate per-character fx with staggered exit times
            # Exit animation is 300ms, so enter_end = end_ms - 300 to finish exit at end_ms
            for ci, ch in enumerate(cn_stripped):
                if ch in (' ', '\u3000'):
                    continue
                
                ch_x = cn_positions[ci]
                stagger = _rand.randint(-60, 60)
                char_enter_end = tl['end_ms'] - 300 + stagger
                
                char_fx = gen_cn_char_fx(
                    ch, ch_x, CN_FX_Y,
                    enter_start, char_enter_end,
                    cn_color, 'OPCN'
                )
                out.extend(char_fx)
                cn_count += 1


# === Write output ===
with open(OUTPUT_FILE, 'w', encoding='utf-8-sig', newline='\r\n') as f:
    f.write('\n'.join(out))

print(f"\nSUCCESS! {OUTPUT_FILE}")
print(f"Total: {len(out)} lines")
print(f"  FX effects: {fx_count}")
print(f"  Furigana: {furi_count}")
print(f"  Echo (OPJP-B): {echo_count}")
print(f"  Chanting: {chant_count}")
print(f"  CN translation: {cn_count}")
