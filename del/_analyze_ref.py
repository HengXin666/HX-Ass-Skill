"""Analyze the reference file structure to understand what to extract."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

ref_path = r"reference\music-ass\Charlotte\Lia - Bravely You.ass"
with open(ref_path, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Find key markers
ed_idx = None
events_idx = None
for i, line in enumerate(lines):
    if '=====ED=====' in line:
        ed_idx = i
    if line.strip() == '[Events]':
        events_idx = i

print(f"[Events] at line: {events_idx + 1}")
print(f"ED marker at line: {ed_idx + 1 if ed_idx else 'not found'}")

# Count different line types BEFORE the ED marker
code_lines = []
template_lines = []
karaoke_lines = []
fx_lines = []
dialogue_lines = []

for i in range(events_idx, ed_idx if ed_idx else len(lines)):
    line = lines[i].strip()
    if line.startswith('Comment:') and (',code ' in line.lower() or ',Code ' in line):
        code_lines.append(i)
    elif line.startswith('Comment:') and ',template ' in line.lower():
        template_lines.append(i)
    elif line.startswith('Comment:') and ',karaoke,' in line:
        karaoke_lines.append(i)
    elif line.startswith('Dialogue:') and ',fx,' in line:
        fx_lines.append(i)
    elif line.startswith('Dialogue:'):
        dialogue_lines.append(i)

print(f"\nBefore ED marker:")
print(f"  Code lines: {len(code_lines)}")
print(f"  Template lines: {len(template_lines)}")
print(f"  Karaoke (Comment) lines: {len(karaoke_lines)}")
print(f"  FX (Dialogue) lines: {len(fx_lines)}")
print(f"  Other Dialogue lines: {len(dialogue_lines)}")

# Count AFTER the ED marker
fx_after = 0
for i in range(ed_idx + 1 if ed_idx else len(lines), len(lines)):
    line = lines[i].strip()
    if line.startswith('Dialogue:') and ',fx,' in line:
        fx_after += 1

print(f"\nAfter ED marker:")
print(f"  FX Dialogue lines: {fx_after}")

# Show what the karaoke lines look like (check if they have furigana)
print(f"\n--- Sample karaoke lines (first 5 JP) ---")
jp_kara = [i for i in karaoke_lines if 'OPJP' in lines[i]]
for idx in jp_kara[:5]:
    print(f"  L{idx+1}: {lines[idx].rstrip()[:150]}")

print(f"\n--- Sample karaoke lines (first 5 CN) ---")
cn_kara = [i for i in karaoke_lines if 'OPCN' in lines[i]]
for idx in cn_kara[:5]:
    print(f"  L{idx+1}: {lines[idx].rstrip()[:150]}")

# Check for furigana in karaoke lines
has_furi = sum(1 for i in karaoke_lines if '|<' in lines[i])
print(f"\nKaraoke lines with furigana (|<): {has_furi}")

# Show Code lines (used by Aegisub for style definitions, but in Code style)
print(f"\n--- Code style Dialogue lines (first 5) ---")
code_dial = [i for i in range(events_idx, ed_idx) if lines[i].strip().startswith('Dialogue:') and ',Code,' in lines[i]]
for idx in code_dial[:5]:
    print(f"  L{idx+1}: {lines[idx].rstrip()[:150]}")
print(f"  Total Code Dialogues: {len(code_dial)}")
