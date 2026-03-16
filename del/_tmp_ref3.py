import re

ref_path = r"d:\command\Github\HX-Ass-Skill\reference\music-ass\Charlotte\Lia - Bravely You.ass"
ref_lines = open(ref_path, 'r', encoding='utf-8-sig').read().splitlines()

def time_to_ms(t):
    m = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', t)
    if m:
        h, mi, s, cs = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        return (h * 3600 + mi * 60 + s) * 1000 + cs * 10
    return 0

# Search for OPCN Comment lines in section 3 (128640-141490ms range)
print("=== Reference: OPCN Comment lines for section 3 (128-142s) ===")
for i, l in enumerate(ref_lines):
    if 'OPCN' not in l:
        continue
    m = re.match(r'(Comment|Dialogue):\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
    if not m:
        continue
    s_ms = time_to_ms(m[2])
    if 128000 <= s_ms <= 142000:
        text_part = l.split(',', 9)[-1] if l.count(',') >= 9 else ''
        kind = m[1][:4]
        print(f"  L{i:4d} {kind} {m[2]}({s_ms}ms) → {m[3]}({time_to_ms(m[3])}ms)  text={text_part[:100]}")

# Also search for OPCN ENTER lines in that range
print()
print("=== Reference: OPCN ENTER times for section 3 (unique chars) ===")
seen = set()
for i, l in enumerate(ref_lines):
    if 'OPCN' not in l or 'fscx240' not in l or not l.startswith('Dialogue'):
        continue
    m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
    if not m:
        continue
    s_ms = time_to_ms(m[1])
    if 128000 <= s_ms <= 142000:
        text_part = l.split('fx,', 1)[-1] if 'fx,' in l else ''
        last_char = text_part[-1] if text_part else '?'
        key = f"{last_char}_{s_ms}"
        if key not in seen:
            seen.add(key)
            print(f"  [{last_char}] enter_start={s_ms}ms  delay_from_128640={s_ms-128640}ms")

# Also search for the 115920ms range - there may or may not be OPCN lines here
print()
print("=== Reference: OPCN in 115-129s range ===")
for i, l in enumerate(ref_lines):
    if 'OPCN' not in l:
        continue
    m = re.match(r'(Comment|Dialogue):\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
    if not m:
        continue
    s_ms = time_to_ms(m[2])
    if 115000 <= s_ms <= 129000:
        text_part = l.split(',', 9)[-1] if l.count(',') >= 9 else ''
        kind = m[1][:4]
        print(f"  L{i:4d} {kind} {m[2]}({s_ms}ms) → {m[3]}({time_to_ms(m[3])}ms)  text={text_part[:100]}")
