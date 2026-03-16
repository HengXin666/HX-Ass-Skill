import re

path = r"C:\Users\Heng_Xin\Documents\Lyrics\Lia - Bravely You (28055813).ass"
lines = open(path, 'r', encoding='utf-8-sig').read().splitlines()

# Print all orig/ts lines with timestamps
for l in lines:
    m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+),\s*(orig|ts)\s*,', l)
    if not m:
        continue
    start = m[1]
    # Check if in verse2 range (1:39 to 2:21)
    if '1:55' in start or '1:56' in start or '2:08' in start or '2:09' in start:
        print(l)

print("\n--- ALL orig lines from verse2 section ---")
def time_to_ms(t):
    m2 = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', t)
    if m2:
        h, mi, s, cs = int(m2[1]), int(m2[2]), int(m2[3]), int(m2[4])
        return (h * 3600 + mi * 60 + s) * 1000 + cs * 10
    return 0

for l in lines:
    m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+),\s*(orig|ts)\s*,', l)
    if not m:
        continue
    ms = time_to_ms(m[1])
    if 99000 <= ms <= 142000:
        parts = l.split(',', 9)
        text = parts[9] if len(parts) >= 10 else ''
        print(f"  {m[3]:4s} {m[1]} -> {m[2]}  ms={ms:>8d}  text={text[:60]}")
