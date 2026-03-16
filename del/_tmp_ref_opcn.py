import re

ref_path = r"d:\command\Github\HX-Ass-Skill\reference\music-ass\Charlotte\Lia - Bravely You.ass"
ref_lines = open(ref_path, 'r', encoding='utf-8-sig').read().splitlines()

def time_to_ms(t):
    m = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', t)
    if m:
        h, mi, s, cs = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        return (h * 3600 + mi * 60 + s) * 1000 + cs * 10
    return 0

# Find all OPCN lines in reference
print("=== ALL OPCN lines in reference (23-37s range) ===")
for i, l in enumerate(ref_lines):
    if 'OPCN' not in l:
        continue
    m = re.match(r'(Dialogue|Comment):\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
    if not m:
        continue
    s_ms = time_to_ms(m[2])
    if 22000 <= s_ms <= 37000:
        text_part = l.split(',', 9)[-1] if l.count(',') >= 9 else ''
        last_char = text_part[-1] if text_part else '?'
        typ = m[1][:4]
        is_enter = 'fscx240' in l
        is_exit = 'fscy240' in l
        kind = 'ENT' if is_enter else ('EXT' if is_exit else '---')
        print(f"  L{i:4d} {typ} [{last_char}] {kind} {m[2]}({s_ms}ms) → {m[3]}({time_to_ms(m[3])}ms)  {text_part[:80]}")

# Also search broader
print()
print("=== First 5 OPCN Dialogue lines in reference ===")
count = 0
for i, l in enumerate(ref_lines):
    if 'OPCN' in l and l.startswith('Dialogue'):
        m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
        if m:
            s_ms = time_to_ms(m[1])
            text_part = l.split('fx,', 1)[-1] if 'fx,' in l else l.split(',', 9)[-1]
            print(f"  L{i:4d} {m[1]} → {m[2]}  text[-30:]={text_part[-30:]}")
            count += 1
            if count >= 15:
                break
