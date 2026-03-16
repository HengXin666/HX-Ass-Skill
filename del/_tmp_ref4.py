import re

ref_path = r"d:\command\Github\HX-Ass-Skill\reference\music-ass\Charlotte\Lia - Bravely You.ass"
ref_lines = open(ref_path, 'r', encoding='utf-8-sig').read().splitlines()

def time_to_ms(t):
    m = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', t)
    if m:
        h, mi, s, cs = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        return (h * 3600 + mi * 60 + s) * 1000 + cs * 10
    return 0

# All lines in 115-142s
print("=== Reference: ALL styles in 115-142s ===")
styles_found = set()
for i, l in enumerate(ref_lines):
    m = re.match(r'(Comment|Dialogue):\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+),\s*(\S+)\s*,', l)
    if not m:
        continue
    s_ms = time_to_ms(m[2])
    if 115000 <= s_ms <= 142000:
        style = m[4]
        styles_found.add(style)

print(f"Styles found: {styles_found}")

# Check if this section has OPCN at all in reference
print()
print("=== Reference: Comment lines with OPCN style (all) ===")
for i, l in enumerate(ref_lines):
    if not l.startswith('Comment') or 'OPCN' not in l:
        continue
    m = re.match(r'Comment:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+),\s*(\S+)', l)
    if m:
        s_ms = time_to_ms(m[1])
        text_part = l.split(',', 9)[-1] if l.count(',') >= 9 else ''
        print(f"  {m[1]}({s_ms:>8d}ms) {m[3]:10s} text={text_part[:80]}")
