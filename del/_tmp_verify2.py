import re

path = r"C:\Users\Heng_Xin\Documents\Lyrics\Lia - Bravely You (28055813)_KFX.ass"
lines = open(path, 'r', encoding='utf-8-sig').read().splitlines()

def time_to_ms(t):
    m = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', t)
    if m:
        h, mi, s, cs = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        return (h * 3600 + mi * 60 + s) * 1000 + cs * 10
    return 0

# Search for 独 character in OPCN fx lines
print("=== Search for '独' in OPCN fx lines ===")
for i, l in enumerate(lines):
    if l.endswith('独') and 'OPCN' in l and 'fx,' in l:
        m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
        if m:
            s_ms = time_to_ms(m[1])
            e_ms = time_to_ms(m[2])
            is_enter = 'fscx240' in l
            is_exit = 'fscy240' in l
            kind = 'ENTER' if is_enter else ('EXIT' if is_exit else 'OTHER')
            print(f"  Line {i}: {kind} {m[1]}({s_ms}ms) → {m[2]}({e_ms}ms)")

print()
# Search for 自 character  
print("=== Search for '自' in OPCN fx lines ===")
for i, l in enumerate(lines):
    if l.endswith('自') and 'OPCN' in l and 'fx,' in l:
        m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
        if m:
            s_ms = time_to_ms(m[1])
            e_ms = time_to_ms(m[2])
            is_enter = 'fscx240' in l
            is_exit = 'fscy240' in l
            kind = 'ENTER' if is_enter else ('EXIT' if is_exit else 'OTHER')
            print(f"  Line {i}: {kind} {m[1]}({s_ms}ms) → {m[2]}({e_ms}ms)")

print()
# Search for 你 character (word 2 in first section)
print("=== Search for '你' in OPCN fx lines (first section only) ===")
for i, l in enumerate(lines):
    if l.endswith('你') and 'OPCN' in l and 'fx,' in l:
        m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
        if m:
            s_ms = time_to_ms(m[1])
            e_ms = time_to_ms(m[2])
            if s_ms > 40000:
                continue
            is_enter = 'fscx240' in l
            is_exit = 'fscy240' in l
            kind = 'ENTER' if is_enter else ('EXIT' if is_exit else 'OTHER')
            print(f"  Line {i}: {kind} {m[1]}({s_ms}ms) → {m[2]}({e_ms}ms)")

print()
# Also check the reference file for OPCN timing patterns
print("=== Reference OPCN timing (first word-by-word section) ===")
ref_path = r"d:\command\Github\HX-Ass-Skill\reference\music-ass\Charlotte\Lia - Bravely You.ass"
ref_lines = open(ref_path, 'r', encoding='utf-8-sig').read().splitlines()

# Search for OPCN fx lines with 孤 or 獨 (reference uses traditional)
for i, l in enumerate(ref_lines):
    if 'OPCN' in l and 'fx,' in l:
        m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
        if not m:
            continue
        s_ms = time_to_ms(m[1])
        if 23000 <= s_ms <= 37000:
            text_part = l.split('fx,', 1)[-1] if 'fx,' in l else ''
            last_char = text_part[-1] if text_part else '?'
            if last_char in '孤獨的你聽到了什麼':
                is_enter = 'fscx240' in l
                if is_enter and '(-70,20' in text_part:
                    print(f"  [{last_char}] Start={m[1]}({s_ms}ms) End={m[2]}({time_to_ms(m[2])}ms)")
