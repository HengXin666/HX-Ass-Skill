import re

ref_path = r"d:\command\Github\HX-Ass-Skill\reference\music-ass\Charlotte\Lia - Bravely You.ass"
ref_lines = open(ref_path, 'r', encoding='utf-8-sig').read().splitlines()

def time_to_ms(t):
    m = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', t)
    if m:
        h, mi, s, cs = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        return (h * 3600 + mi * 60 + s) * 1000 + cs * 10
    return 0

# Reference word-by-word OPCN: 孤獨的 → 你 → 聽到了 → 什麼
# Find the ENTER lines for each word's first character
target_chars = {'孤': 'word1_孤獨的', '你': 'word2_你', '聽': 'word3_聽到了', '什': 'word4_什麼',
                '我': 'word1_我', '看': 'word2_看到了', '遙': 'word3_遙遠的', '幻': 'word4_幻夢'}

print("=== Reference: Word-by-word OPCN ENTER times (first band only) ===")
print("Section 1 (23170ms line): 孤獨的 → 你 → 聽到了 → 什麼")
print()
seen = set()
for i, l in enumerate(ref_lines):
    if 'OPCN' not in l or 'fscx240' not in l:
        continue
    m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
    if not m:
        continue
    s_ms = time_to_ms(m[1])
    text_part = l.split('fx,', 1)[-1] if 'fx,' in l else ''
    last_char = text_part[-1] if text_part else '?'
    
    # Only first band per char
    if '(-70,20)' not in text_part and '(-70,' not in text_part:
        continue
    
    key = f"{last_char}_{s_ms}"
    if key in seen:
        continue
    seen.add(key)
    
    if 23000 <= s_ms <= 50000 and last_char in target_chars:
        label = target_chars.get(last_char, last_char)
        print(f"  [{last_char}] {label:20s} ENTER start={m[1]}({s_ms}ms)")

# Let's also check the Comment lines for the exact timing
print()
print("=== Reference: Comment lines for word-by-word sections ===")
for i, l in enumerate(ref_lines):
    if 'OPCN' not in l or not l.startswith('Comment'):
        continue
    m = re.match(r'Comment:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
    if not m:
        continue
    s_ms = time_to_ms(m[1])
    if 23000 <= s_ms <= 50000:
        text_part = l.split(',', 9)[-1] if l.count(',') >= 9 else ''
        print(f"  {m[1]}({s_ms}ms) → {m[2]}({time_to_ms(m[2])}ms)  text={text_part[:100]}")

# Extract exact ENTER start times for all chars in the word-by-word sections
print()
print("=== Reference: ALL unique ENTER start times for OPCN chars (23-50s) ===")
enter_times = {}
for i, l in enumerate(ref_lines):
    if 'OPCN' not in l or 'fscx240' not in l or not l.startswith('Dialogue'):
        continue
    m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
    if not m:
        continue
    s_ms = time_to_ms(m[1])
    text_part = l.split('fx,', 1)[-1] if 'fx,' in l else ''
    last_char = text_part[-1] if text_part else '?'
    
    if 23000 <= s_ms <= 50000:
        if last_char not in enter_times:
            enter_times[last_char] = s_ms
        elif enter_times[last_char] != s_ms:
            # Different enter time for same char - this shouldn't happen in word-by-word mode
            pass

# Sort by time
for ch, ms_val in sorted(enter_times.items(), key=lambda x: x[1]):
    line_base = 23170 if ms_val < 36000 else 35890
    delay_from_base = ms_val - line_base
    print(f"  [{ch}] enter_start={ms_val}ms  delay_from_line={delay_from_base}ms")
