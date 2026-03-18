# -*- coding: utf-8 -*-
"""
Build KFX Template ASS for ときめきポポロン♪ - チマメ隊
Reads input K-timed file, applies reference template structure, outputs ready-to-apply ASS.
Requires: Aegisub + karaoke templater (+ Yutils for some effects)
"""
import re, glob, os, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)
INPUT_GLOB = os.path.join(WORKSPACE, '*28134937*')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'ときめきポポロン♪_KFX_Template.ass')
TEMPLATE_FILE = os.path.join(SCRIPT_DIR, 'template_blocks.txt')

# Line mapping: orig_index (0-based, starting from actual lyrics after 3 title lines)
# -> (style, actor, inline_fx)
LINE_MAP = {
    # Verse 1
    3:('JP_FX_A','chino',None), 4:('JP_FX_A','chino',None),
    5:('JP_FX_AS','chino',None), 6:('JP_FX_A','megu',None),
    7:('JP_FX_AS','megu',None), 8:('JP_FX_A','maya',None),
    9:('JP_FX_A','maya',None), 10:('JP_FX_AS','maya',None),
    11:('JP_FX_A','all','all'), 12:('JP_FX_A','all',None),
    # Bridge 1 — add inline_fx for character color switching (matching original)
    13:('JP_FX_B','','chino'), 14:('JP_FX_B','','maya'),
    15:('JP_FX_B','','megu'),
    16:('JP_FX_B','',None), 17:('JP_FX_B','',None),
    # Chorus 1
    18:('JP_FX_C','','CA'), 19:('JP_FX_CS','megu',None),
    20:('JP_FX_C','','CA'), 21:('JP_FX_CS','maya',None),
    22:('JP_FX_C','chino','CA'), 23:('JP_FX_C','chino',None),
    24:('JP_FX_C','','CA'), 25:('JP_FX_C','',None),
    26:('JP_FX_C','','CB'), 27:('JP_FX_CS','maya',None),
    28:('JP_FX_C','','CB'), 29:('JP_FX_CS','megu',None),
    # Ending 1
    30:('JP_FX_D','',None), 31:('JP_FX_D','',None),
    32:('JP_FX_D','DP',None), 33:('JP_FX_D','DP',None), 34:('JP_FX_D','',None),
    # Verse 2
    35:('JP_FX_A','maya',None), 36:('JP_FX_AS','maya',None),
    37:('JP_FX_A','chino',None), 38:('JP_FX_AS','chino',None),
    39:('JP_FX_A','megu',None), 40:('JP_FX_A','megu',None),
    41:('JP_FX_AS','megu',None), 42:('JP_FX_A','all',None),
    # Bridge 2 — add inline_fx for character color switching
    43:('JP_FX_B','',None), 44:('JP_FX_B','',None),
    45:('JP_FX_B','',None), 46:('JP_FX_B','',None),
    # Chorus 2
    47:('JP_FX_C','','CA'), 48:('JP_FX_CS','maya',None),
    49:('JP_FX_C','','CA'), 50:('JP_FX_CS','megu',None),
    51:('JP_FX_C','','CA'), 52:('JP_FX_C','',None),
    53:('JP_FX_C','','CA'), 54:('JP_FX_C','',None),
    55:('JP_FX_C','','CB'), 56:('JP_FX_C','','CB'),
    57:('JP_FX_CS','megu',None),
    # Ending 2
    58:('JP_FX_D','',None), 59:('JP_FX_D','',None),
    60:('JP_FX_D','',None), 61:('JP_FX_D','',None),
    # Interlude Bridge
    62:('JP_FX_B','',None), 63:('JP_FX_B','',None),
    # Final Chorus
    64:('JP_FX_C','','CA'), 65:('JP_FX_C','','CA'),
    66:('JP_FX_C','chino','CA'), 67:('JP_FX_C','chino',None),
    68:('JP_FX_C','','CA'), 69:('JP_FX_C','',None),
    70:('JP_FX_C','','CB'), 71:('JP_FX_C','','CB'),
    72:('JP_FX_CS','megu',None),
    # Final Ending
    73:('JP_FX_D','',None), 74:('JP_FX_D','',None),
    75:('JP_FX_D','DP',None), 76:('JP_FX_D','',None),
}

# DP lines: merge multiple per-character input lines into one line with
# grouped syllables + inline_fx, so syl.i cycles correctly for character images.
# Format: { first_input_idx: [( word_group_text, inline_fx ), ...] }
# The K-values for each group are the SUM of per-character K-values in that group.
# First DP (idx 32+33): 可愛い(megu) + 美味しい(maya) + おそろいの時間(chino)
#   Original: {\\k70\\-megu}可愛い{\\k70\\-maya} 美味しい{\\k301\\-chino} おそろいの時間
DP_MERGE = {
    32: {
        'merge_indices': [32, 33],  # input lines to merge
        'groups': [
            # (chars_to_consume, inline_fx, prefix_text)
            # Group 1: 可愛い = 3 chars from line 32 → \\-megu
            (3, 'megu', ''),
            # Group 2: 美味しい = 4 chars from line 32 → \\-maya (with space prefix)
            (4, 'maya', ' '),
            # Group 3: おそろいの時間 = 7 chars from line 33 → \\-chino (with space prefix)
            (7, 'chino', ' '),
        ]
    },
    # Second DP (idx 75): 大好きな笑顔と
    #   3 groups for 3 images: 大好き(megu) + な笑顔(maya) + と(chino)
    #   Or better: group by meaning: 大好きな(chino) + 笑顔(maya) + と(megu)
    75: {
        'merge_indices': [75],
        'groups': [
            # 大好き = 3 chars → \\-chino
            (3, 'chino', ''),
            # な笑顔 = 3 chars → \\-maya
            (3, 'maya', ''),
            # と = 1 char → \\-megu
            (1, 'megu', ''),
        ]
    },
}

# Lines that should be merged into one (non-DP case)
# Maps first_index -> list of indices to merge, with optional mid-line inline_fx switches
# Based on original reference structure
MERGE_LINES = {
    # Bridge 1: original merges ハートもふもふ + あったかい気持ち into one line
    # with \\-chino on first half, \\-maya on second half
    13: {
        'merge_indices': [13, 14],
        'mid_fx': [
            (None, 'chino'),  # line 13: \\-chino on first syl
            (None, 'maya'),   # line 14: \\-maya on first syl (space prefix)
        ],
        'separator': ' ',
    },
    # Bridge 1: おすそ分けしたい with \\-megu
    # (this is a single line, just needs inline_fx - handled by LINE_MAP)
    # Bridge 1: つまんないないんだよ + あれこれそれもしよっ merged
    16: {
        'merge_indices': [16, 17],
        'mid_fx': [
            (None, None),  # line 16: no inline_fx
            (None, None),  # line 17: no inline_fx (space prefix)
        ],
        'separator': ' ',
    },
}

# Skip indices that are consumed by merges
SKIP_INDICES = set()
for cfg in DP_MERGE.values():
    for idx in cfg['merge_indices'][1:]:  # skip first, it's the trigger
        SKIP_INDICES.add(idx)
for cfg in MERGE_LINES.values():
    for idx in cfg['merge_indices'][1:]:
        SKIP_INDICES.add(idx)

# ========================================================================
# Furigana (振假名) annotations for kanji
# Format: kanji -> reading (hiragana)
# In ASS karaoke, furigana uses pipe notation: 漢|かん字|じ
# The karaoke templater auto-creates furigana lines using <Style>-furigana
# ========================================================================
FURIGANA_MAP = {
    '隊': 'たい',
    '詞': 'し', '词': 'し',
    '曲': 'きょく',
    '知': 'し',
    '見': 'み',
    '冒': 'ぼう', '険': 'けん',
    '始': 'はじ',
    '未': 'み', '来': 'らい',
    '地': 'ち', '図': 'ず',
    '作': 'つく',
    '気': 'き', '持': 'も',
    '分': 'わ',
    '飛': 'と', '出': 'だ',
    '明': 'あ', '日': 'した',  # 明日=あした, special reading
    '追': 'お', '越': 'こ',
    '煌': 'きら',
    '音': 'おと',
    '響': 'ひび',
    '尽': 'つ',
    '舞': 'ま', '踊': 'おど',
    '木': 'こ', '洩': 'も', '陽': 'び',  # 木洩れ陽=こもれび
    '手': 'て',
    '靴': 'くつ', '鳴': 'な',
    '可': 'か', '愛': 'わ',     # 可愛い=かわいい (愛=わ, trailing い is kana)
    '美': 'お', '味': 'い',    # 美味しい=おいしい (味=い, trailing しい is kana)
    '時': 'じ', '間': 'かん',
    '一': 'いっ', '緒': 'しょ',
    '想': 'そう', '像': 'ぞう',
    '楽': 'たの',
    '疲': 'つか',
    '休': 'やす',
    '繰': 'く', '返': 'かえ',
    '何': 'なん',
    '話': 'はなし',
    '青': 'あお', '空': 'そら',
    '雲': 'くも',
    '私': 'わたし',
    '弾': 'はじ',
    '期': 'き', '待': 'たい',
    '連': 'つ',
    '行': 'い',
    '恋': 'こい',
    '運': 'うん', '命': 'めい',
    '言': 'い',
    '夢': 'ゆめ',
    '処': 'こ',  # 何処=いずこ (歌詞文脈)
    '道': 'みち',
    '大': 'だい', '好': 'す',
    '場': 'ば', '所': 'しょ',
    '目': 'め', '指': 'ざ',
    '進': 'すす',
    '憧': 'あこが',
    '乗': 'の',
    '会': 'あ',
    '十': 'じゅう', '年': 'ねん', '後': 'ご',
    '決': 'けっ', '定': 'てい',
    '笑': 'え', '顔': 'がお',
}

# Context-dependent furigana overrides
# Some kanji have different readings depending on the word context
# Format: (orig_line_index, char_position_in_stripped_text) -> reading
# Or we handle it by checking adjacent characters in the word
CONTEXT_FURIGANA = {
    # 明日 = あした (not あ+にち)
    # 出 in 飛び出した = だ, but 出 in 連れ出して = だ (same)
    # 何 standalone = なに/なん
    # 何処 = いずこ? No, here it's なんどころ→どこ. Actually 何処=どこ
    # Let's handle 何処 specially: 何|なん処|ど → nah, 何処 here = いずこ/どこ
    # Actually lyrics say ココロは何処へゆく, 何処=いずこ
}

def is_kanji(ch):
    """Check if a character is a CJK kanji."""
    cp = ord(ch)
    return (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or 
            0x20000 <= cp <= 0x2A6DF or 0xF900 <= cp <= 0xFAFF)

def add_furigana_to_char(char):
    """Add furigana annotation to a single character if it's a kanji.
    Uses 字|<読み format (with < for per-char furigana)."""
    if char in FURIGANA_MAP:
        return f'{char}|<{FURIGANA_MAP[char]}'
    return char

def add_furigana_to_syl(syl_text):
    """Add furigana to all kanji in a syllable text, per-char with < prefix.
    e.g., 冒険 → 冒|<ぼう険|<けん
    """
    result = []
    chars = list(syl_text)
    i = 0
    while i < len(chars):
        ch = chars[i]
        if is_kanji(ch):
            next_ch = chars[i+1] if i+1 < len(chars) else ''
            if ch == '何' and next_ch == '処':
                result.append('何|<いず')
                result.append('処|<こ')
                i += 2
                continue
            if ch in FURIGANA_MAP:
                result.append(f'{ch}|<{FURIGANA_MAP[ch]}')
            else:
                result.append(ch)
        else:
            result.append(ch)
        i += 1
    return ''.join(result)

def add_furigana_to_k_text(text):
    """Add furigana to all kanji within K-timed text, preserving K tags.
    
    Uses context-aware processing: first extracts all syllable chars in order
    to detect cross-syllable word boundaries (e.g., 何+処 in adjacent syls),
    then applies the correct readings.
    """
    # Step 1: Parse all {tags}text segments
    segments = []  # [(full_match, tag_part, text_part), ...]
    pos = 0
    for m in re.finditer(r'(\{[^}]*\\kf?\d+[^}]*\})([^{]*)', text):
        # Include any text before this match (shouldn't normally happen)
        if m.start() > pos:
            segments.append(('', '', text[pos:m.start()]))
        segments.append((m.group(0), m.group(1), m.group(2)))
        pos = m.end()
    if pos < len(text):
        segments.append(('', '', text[pos:]))
    
    # Step 2: Build a flat character list with segment references for context detection
    flat_chars = []  # [(char, seg_idx, char_idx_in_seg), ...]
    for seg_idx, (_, _, txt) in enumerate(segments):
        for ci, ch in enumerate(txt):
            flat_chars.append((ch, seg_idx, ci))
    
    # Step 3: Mark context-dependent overrides
    overrides = {}  # (seg_idx, char_idx) -> reading
    for fi in range(len(flat_chars) - 1):
        ch1, si1, ci1 = flat_chars[fi]
        ch2, si2, ci2 = flat_chars[fi + 1]
        if ch1 == '何' and ch2 == '処':
            overrides[(si1, ci1)] = 'いず'
            overrides[(si2, ci2)] = 'こ'
    
    # Step 4: Rebuild text with furigana using 字|<読み format
    result_parts = []
    for seg_idx, (_, tag, txt) in enumerate(segments):
        result_parts.append(tag)
        for ci, ch in enumerate(txt):
            key = (seg_idx, ci)
            if key in overrides:
                result_parts.append(f'{ch}|<{overrides[key]}')
            elif is_kanji(ch) and ch in FURIGANA_MAP:
                result_parts.append(f'{ch}|<{FURIGANA_MAP[ch]}')
            else:
                result_parts.append(ch)
    
    return ''.join(result_parts)

def normalize_ts(ts):
    """00:00:06.67 -> 0:00:06.67"""
    if ts.startswith('00:'): return ts[1:]
    return ts

def ts_to_ms(ts):
    """Convert ASS timestamp (H:MM:SS.cc) to milliseconds.
    e.g. '0:01:05.25' -> 65250"""
    parts = ts.split(':')
    h = int(parts[0])
    m = int(parts[1])
    sec_parts = parts[2].split('.')
    s = int(sec_parts[0])
    cs = int(sec_parts[1])
    return (h * 3600 + m * 60 + s) * 1000 + cs * 10

def ms_to_ts(ms):
    """Convert milliseconds to ASS timestamp (H:MM:SS.cc).
    e.g. 65250 -> '0:01:05.25'"""
    total_cs = ms // 10
    cs = total_cs % 100
    total_s = total_cs // 100
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f'{h}:{m:02d}:{s:02d}.{cs:02d}'

def read_input():
    files = glob.glob(INPUT_GLOB)
    if not files:
        print(f"ERROR: No input file matching {INPUT_GLOB}"); sys.exit(1)
    with open(files[0], 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    orig, ts = [], []
    for line in lines:
        line = line.rstrip('\r\n')
        if line.startswith('Dialogue:'):
            if ',orig,' in line: orig.append(line)
            elif ',ts,' in line: ts.append(line)
    return orig, ts

def parse_dialogue(line):
    m = re.match(r'(Dialogue|Comment): (\d+),(\d{1,2}:\d{2}:\d{2}\.\d{2}),(\d{1,2}:\d{2}:\d{2}\.\d{2}),([^,]*),([^,]*),(\d+),(\d+),(\d+),([^,]*),(.*)', line)
    if m:
        return {'type':m[1],'layer':m[2],'start':m[3],'end':m[4],
                'style':m[5],'name':m[6],'ml':m[7],'mr':m[8],'mv':m[9],
                'effect':m[10],'text':m[11]}
    return None

def kf_to_k(text):
    return text.replace('\\kf', '\\k')

def apply_inline_fx(text, fx):
    """Add \\-fx to the FIRST \\k tag in text."""
    if fx:
        text = re.sub(r'(\\k\d+)', r'\1\\-' + fx, text, count=1)
    return text

def extract_k_chars(text):
    """Extract list of (k_value, char) from K-timed text like {\\k20}ま{\\k16}だ..."""
    result = []
    # Match each {\\k<val>}<char> pair
    for m in re.finditer(r'\{[^}]*\\k(\d+)[^}]*\}([^{]*)', text):
        k_val = int(m.group(1))
        char = m.group(2)
        result.append((k_val, char))
    return result

def build_dp_line(orig_lines, first_idx, dp_cfg):
    """Build a single merged DP karaoke line with per-GROUP \\k tags.
    
    Matches original format: {\\k70\\-megu}可愛い{\\k70\\-maya} 美味しい{\\k301\\-chino} おそろいの時間
    Each GROUP gets ONE \\k tag with the SUM of per-char K-values.
    This gives exactly 3 syls so math.fmod(syl.i-1,3)+1 cycles 1→2→3 for images.
    
    NOTE: No per-char furigana in DP lines — multiple kanji in one \\k tag
    cannot use pipe notation safely (karaskel only supports one | per \\k).
    """
    all_chars = []
    starts = []
    ends = []
    for idx in dp_cfg['merge_indices']:
        p = parse_dialogue(orig_lines[idx])
        if not p:
            continue
        text = kf_to_k(p['text'])
        chars = extract_k_chars(text)
        all_chars.extend(chars)
        starts.append(p['start'])
        ends.append(p['end'])

    start = normalize_ts(min(starts))
    end = normalize_ts(max(ends))
    pos = 0
    parts = []
    for char_count, fx, prefix in dp_cfg['groups']:
        # Sum K-values for the entire group
        group_k = sum(all_chars[pos + i][0] for i in range(char_count))
        # Concatenate all chars in the group
        group_text = ''.join(all_chars[pos + i][1] for i in range(char_count))
        # Build the tag: {\\k<sum>\\-<fx>}<prefix><text>
        tag = f'\\k{group_k}'
        if fx:
            tag += f'\\-{fx}'
        parts.append(f'{prefix}{{{tag}}}{group_text}')
        pos += char_count

    style, actor, _ = LINE_MAP[first_idx]
    text = ''.join(parts)
    return f"Comment: 0,{start},{end},{style},{actor},0,0,0,karaoke,{text}"

def build_merged_line(orig_lines, first_idx, merge_cfg):
    """Build a merged karaoke line from multiple input lines."""
    all_parts = []
    starts = []
    ends = []
    for i, idx in enumerate(merge_cfg['merge_indices']):
        p = parse_dialogue(orig_lines[idx])
        if not p:
            continue
        text = kf_to_k(p['text'])
        text = add_furigana_to_k_text(text)  # Add furigana
        starts.append(p['start'])
        ends.append(p['end'])

        # Apply mid-line inline_fx if specified
        _, mid_fx = merge_cfg['mid_fx'][i]
        if mid_fx:
            text = apply_inline_fx(text, mid_fx)

        # Add separator between merged parts
        if i > 0:
            sep = merge_cfg.get('separator', '')
            if sep:
                # Insert space as a 0-duration k tag before the line's content
                text = f'{{\\k0}}{sep}' + text

        all_parts.append(text)

    start = normalize_ts(min(starts))
    end = normalize_ts(max(ends))
    style, actor, fx = LINE_MAP[first_idx]
    merged_text = ''.join(all_parts)
    # Apply the LINE_MAP inline_fx to the first syl if not already applied by mid_fx
    first_mid_fx = merge_cfg['mid_fx'][0][1] if merge_cfg['mid_fx'] else None
    if fx and not first_mid_fx:
        merged_text = apply_inline_fx(merged_text, fx)
    return f"Comment: 0,{start},{end},{style},{actor},0,0,0,karaoke,{merged_text}"

# Lines with embedded parentheses that need to be split
# The parenthesized content becomes a separate JP_FX_CS line
# Format: orig_idx -> actor for the new CS line
EMBEDDED_PAREN = {
    55: 'megu',   # 夢ふるこの道を(この道を) → CS: この道を
    70: 'maya',   # キラキラ舞い踊る(舞い踊る) → CS: 舞い踊る
}

def build_karaoke_lines(orig_lines):
    out = []
    for idx in range(3, len(orig_lines)):
        if idx not in LINE_MAP:
            continue
        if idx in SKIP_INDICES:
            continue  # consumed by a merge

        # Check if this is a DP merge
        if idx in DP_MERGE:
            out.append(build_dp_line(orig_lines, idx, DP_MERGE[idx]))
            continue

        # Check if this is a regular merge
        if idx in MERGE_LINES:
            out.append(build_merged_line(orig_lines, idx, MERGE_LINES[idx]))
            continue

        # Normal single line
        p = parse_dialogue(orig_lines[idx])
        if not p:
            continue
        style, actor, fx = LINE_MAP[idx]
        text = kf_to_k(p['text'])
        start, end = normalize_ts(p['start']), normalize_ts(p['end'])

        # Strip parentheses from CS (top-positioned) lines — they are already separate
        if style == 'JP_FX_CS':
            text = text.replace('(', '').replace(')', '')
            text = add_furigana_to_k_text(text)
            text = apply_inline_fx(text, fx)
            out.append(f"Comment: 0,{start},{end},{style},{actor},0,0,0,karaoke,{text}")
            continue

        # Check for embedded parentheses that need to be split into a CS line
        if idx in EMBEDDED_PAREN:
            cs_actor = EMBEDDED_PAREN[idx]
            # Split K-tagged text into main (before paren) and CS (inside paren)
            main_segs = []
            cs_segs = []
            in_paren = False
            pre_paren_k_sum = 0  # Sum of K-values before the parenthesized content (in centiseconds)
            for m in re.finditer(r'(\{[^}]*\\k(\d+)[^}]*\})([^{]*)', text):
                tag = m.group(1)
                k_val = int(m.group(2))
                txt = m.group(3)
                if not in_paren:
                    if '(' in txt:
                        before_paren = txt[:txt.index('(')]
                        after_paren = txt[txt.index('(')+1:]
                        if before_paren:
                            main_segs.append(tag + before_paren)
                        pre_paren_k_sum += k_val  # Include this syl's K in pre-paren sum
                        if after_paren:
                            cs_segs.append(tag + after_paren)
                        in_paren = True
                    else:
                        main_segs.append(tag + txt)
                        pre_paren_k_sum += k_val
                else:
                    if ')' in txt:
                        before_close = txt[:txt.index(')')]
                        if before_close:
                            cs_segs.append(tag + before_close)
                        in_paren = False
                    else:
                        cs_segs.append(tag + txt)
            
            # Build main line (before parenthesis)
            main_text = ''.join(main_segs)
            main_text = add_furigana_to_k_text(main_text)
            main_text = apply_inline_fx(main_text, fx)
            out.append(f"Comment: 0,{start},{end},{style},{actor},0,0,0,karaoke,{main_text}")
            
            # Build CS line (parenthesized content) with INDEPENDENT timing
            # CS start = main line start + pre_paren_k_sum (converted from centiseconds to timestamp)
            # CS end = main line end (same as original)
            if cs_segs:
                cs_text = ''.join(cs_segs)
                cs_text = add_furigana_to_k_text(cs_text)
                # Calculate CS start time: line_start_ms + pre_paren_k_sum * 10
                start_ms = ts_to_ms(start)
                cs_start_ms = start_ms + pre_paren_k_sum * 10
                cs_start = ms_to_ts(cs_start_ms)
                out.append(f"Comment: 0,{cs_start},{end},JP_FX_CS,{cs_actor},0,0,0,karaoke,{cs_text}")
            continue

        # Regular line (no parentheses issue)
        text = add_furigana_to_k_text(text)
        text = apply_inline_fx(text, fx)
        out.append(f"Comment: 0,{start},{end},{style},{actor},0,0,0,karaoke,{text}")
    
    # Post-process: ensure consecutive JP_FX_B lines have no time gaps
    # (the tipi.png sliding effect uses retime("line",-100,150) which only adds
    # 250ms overlap — if input lines have gaps > 250ms, Tippy will break)
    # Fix: extend each JP_FX_B line's end to overlap with the next JP_FX_B line's start
    _fix_consecutive_gaps(out, 'JP_FX_B')
    
    return out


def _fix_consecutive_gaps(lines, target_style):
    """Ensure consecutive lines of target_style have overlapping times.
    
    For each pair of adjacent lines with the target style, if there's a small gap
    (< MAX_GAP_MS) between line N's end and line N+1's start, extend line N's end
    time to cover the gap. Gaps larger than MAX_GAP_MS indicate different sections
    and are left alone.
    """
    OVERLAP_MS = 300  # ms of overlap to ensure smooth transition
    MAX_GAP_MS = 5000  # only fix gaps smaller than 5 seconds (same section)
    
    # Find indices of target style lines
    style_indices = []
    for i, line in enumerate(lines):
        p = parse_dialogue(line)
        if p and p['style'] == target_style:
            style_indices.append(i)
    
    # Fix gaps between consecutive lines
    for k in range(len(style_indices) - 1):
        i1 = style_indices[k]
        i2 = style_indices[k + 1]
        p1 = parse_dialogue(lines[i1])
        p2 = parse_dialogue(lines[i2])
        if not p1 or not p2:
            continue
        
        end1_ms = ts_to_ms(p1['end'])
        start2_ms = ts_to_ms(p2['start'])
        gap = start2_ms - end1_ms
        
        # Only fix small gaps within the same section
        if 0 < gap < MAX_GAP_MS:
            new_end_ms = start2_ms + OVERLAP_MS
            new_end = ms_to_ts(new_end_ms)
            # Rebuild line with new end time
            lines[i1] = (f"Comment: {p1['layer']},{p1['start']},{new_end},"
                         f"{p1['style']},{p1['name']},{p1['ml']},{p1['mr']},"
                         f"{p1['mv']},{p1['effect']},{p1['text']}")

def build_cn_lines(ts_lines):
    """Chinese translation lines - REMOVED per user request."""
    return []

def main():
    print("Reading input file...")
    orig_lines, ts_lines = read_input()
    print(f"  Found {len(orig_lines)} orig lines, {len(ts_lines)} ts lines")
    
    print("Building karaoke lines (with furigana)...")
    karaoke = build_karaoke_lines(orig_lines)
    print(f"  Generated {len(karaoke)} karaoke lines")
    
    # CN translation lines removed per user request
    
    print("Reading template blocks...")
    if not os.path.exists(TEMPLATE_FILE):
        print(f"ERROR: {TEMPLATE_FILE} not found. Run extract_templates.py first.")
        sys.exit(1)
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_lines = [l.rstrip('\r\n') for l in f.readlines() if l.strip()]
    print(f"  Loaded {len(template_lines)} template lines")
    
    # Assemble output
    print("Assembling output file...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8-sig') as f:
        # Script Info
        f.write("[Script Info]\n")
        f.write("; KFX Template for ときめきポポロン♪ - チマメ隊\n")
        f.write("; Generated by build_kfx.py\n")
        f.write("; Apply with Aegisub karaoke templater\n")
        f.write("Title: ときめきポポロン♪ (心动泡芙♪) - チマメ隊 KFX\n")
        f.write("ScriptType: v4.00+\n")
        f.write(f"PlayResX: 1920\n")
        f.write(f"PlayResY: 1080\n")
        f.write("WrapStyle: 0\n")
        f.write("ScaledBorderAndShadow: yes\n")
        f.write("Timer: 100.0000\n")
        f.write("\n")
        
        # Styles (main + furigana pairs)
        f.write("[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        # Default
        f.write("Style: Default,Meiryo,60,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n")
        f.write("Style: Default-furigana,Meiryo,30,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1\n")
        # JP_FX_A  
        f.write("Style: JP_FX_A,FOT-ニューロダン Pro M,70,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,5,0,1,3,0,2,10,10,50,1\n")
        f.write("Style: JP_FX_A-furigana,FOT-ニューロダン Pro M,35,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,5,0,1,1.5,0,2,10,10,50,1\n")
        # JP_FX_AS (MarginV=150: 比其它行多100px, 使带杯子的上方歌词更高, 避免与下行重叠)
        f.write("Style: JP_FX_AS,FOT-ニューロダン Pro M,70,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,2,10,10,150,1\n")
        f.write("Style: JP_FX_AS-furigana,FOT-ニューロダン Pro M,35,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,5,0,1,1.5,0,2,10,10,150,1\n")
        # JP_FX_B
        f.write("Style: JP_FX_B,FOT-ニューロダン Pro M,70,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,5,0,1,3,0,2,10,10,50,1\n")
        f.write("Style: JP_FX_B-furigana,FOT-ニューロダン Pro M,35,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,5,0,1,1.5,0,2,10,10,50,1\n")
        # JP_FX_C
        f.write("Style: JP_FX_C,FOT-ニューロダン Pro M,70,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,5,0,1,3,0,2,10,10,50,1\n")
        f.write("Style: JP_FX_C-furigana,FOT-ニューロダン Pro M,35,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,5,0,1,1.5,0,2,10,10,50,1\n")
        # JP_FX_CS
        f.write("Style: JP_FX_CS,FOT-ニューロダン Pro M,70,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,8,10,10,50,1\n")
        f.write("Style: JP_FX_CS-furigana,FOT-ニューロダン Pro M,35,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,5,0,1,1.5,0,2,10,10,50,1\n")
        # JP_FX_D
        f.write("Style: JP_FX_D,FOT-ニューロダン Pro M,70,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,5,0,1,3,0,2,10,10,50,1\n")
        f.write("Style: JP_FX_D-furigana,FOT-ニューロダン Pro M,35,&H00FFFFFF,&H000000FF,&H00223D83,&H00000000,-1,0,0,0,100,100,5,0,1,1.5,0,2,10,10,50,1\n")
        f.write("\n")
        
        # Events
        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        
        # Template code/template blocks
        for line in template_lines:
            f.write(line + "\n")
        
        # Separator
        f.write("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,,\n")
        f.write("Comment: 0,0:00:00.00,0:00:00.00,Default,=== 卡拉OK源行 (含振假名) ===,0,0,0,,\n")
        f.write("Comment: 0,0:00:00.00,0:00:00.00,Default,,0,0,0,,\n")
        
        # Karaoke source lines (with furigana)
        for line in karaoke:
            f.write(line + "\n")
    
    print(f"\nOutput written to: {OUTPUT_FILE}")
    print(f"Total lines: {len(template_lines) + len(karaoke) + 18} (approx)")
    print("\nNext steps:")
    print("  1. Open the output file in Aegisub")
    print("  2. Load the video/audio")
    print("  3. Run: Automation -> Apply karaoke template")
    print("  4. The fx lines will be generated (with furigana)")
    print("\nNote: CN translation lines removed per user request.")

if __name__ == '__main__':
    main()
