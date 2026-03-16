import re

path = r"C:\Users\Heng_Xin\Documents\Lyrics\Lia - Bravely You (28055813)_KFX.ass"
lines = open(path, 'r', encoding='utf-8-sig').read().splitlines()

def time_to_ms(t):
    m = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', t)
    if m:
        h, mi, s, cs = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        return (h * 3600 + mi * 60 + s) * 1000 + cs * 10
    return 0

ref_path = r"d:\command\Github\HX-Ass-Skill\reference\music-ass\Charlotte\Lia - Bravely You.ass"
ref_lines = open(ref_path, 'r', encoding='utf-8-sig').read().splitlines()

# ==== CHECK 1: Word-by-word OPCN timing (section 1) ====
print("=" * 60)
print("CHECK 1: OPCN word-by-word timing (section 1: 23170ms)")
print("=" * 60)

# Reference ENTER times:
# 孤: 23240ms, 你: 26410ms, 聽: 29660ms, 什: 32870ms
ref_enter = {'孤': 23240, '你': 26410, '聽': 29660, '什': 32870}
my_chars = {'独': '独(→孤)', '你': '你', '听': '听(→聽)', '什': '什'}

for char, label in my_chars.items():
    for l in lines:
        if l.endswith(char) and 'OPCN' in l and 'fscx240' in l:
            m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+)', l)
            if m:
                s_ms = time_to_ms(m[1])
                if 23000 <= s_ms <= 35000:
                    # Find reference equivalent
                    ref_char = '孤' if char == '独' else ('聽' if char == '听' else char)
                    ref_ms = ref_enter.get(ref_char, '?')
                    match = "✓" if isinstance(ref_ms, int) and abs(s_ms - ref_ms) < 50 else "✗"
                    print(f"  [{label:8s}] my_enter={s_ms}ms  ref_enter={ref_ms}ms  {match}")
                    break

# ==== CHECK 2: Word-by-word OPCN timing (section 2) ====
print()
print("=" * 60)
print("CHECK 2: OPCN word-by-word timing (section 2: 35890ms)")
print("=" * 60)

ref_enter2 = {'我': 36040, '看': 39210, '遙': 42470, '幻': 45640}
my_chars2 = {'我': '我', '看': '看(→看)', '遥': '遥(→遙)', '幻': '幻'}

for char, label in my_chars2.items():
    for l in lines:
        if l.endswith(char) and 'OPCN' in l and 'fscx240' in l:
            m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+)', l)
            if m:
                s_ms = time_to_ms(m[1])
                if 35000 <= s_ms <= 48000:
                    ref_char = '遙' if char == '遥' else char
                    ref_ms = ref_enter2.get(ref_char, ref_enter2.get(char, '?'))
                    match = "✓" if isinstance(ref_ms, int) and abs(s_ms - ref_ms) < 50 else "✗"
                    print(f"  [{label:8s}] my_enter={s_ms}ms  ref_enter={ref_ms}ms  {match}")
                    break

# ==== CHECK 3: New 115920ms echo ====
print()
print("=" * 60)
print("CHECK 3: New echo at 115920ms (卑怯だったずっと僕は)")
print("=" * 60)

echo_chars = list('ヒキョウダッタズットボクは')
for l in lines:
    if 'OPJP-B' in l and 'fx,' in l:
        m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+)', l)
        if m:
            s_ms = time_to_ms(m[1])
            if 115000 <= s_ms <= 130000:
                text_part = l.split('fx,', 1)[-1]
                last_char = text_part[-1] if text_part else '?'
                print(f"  [{last_char}] start={m[1]}({s_ms}ms) end={m[2]}")

# ==== CHECK 4: 115920ms word-by-word CN ====
print()
print("=" * 60)
print("CHECK 4: New OPCN word-by-word at 115920ms")
print("=" * 60)

for char in '裹足不前的我过是个懦夫':
    for l in lines:
        if l.endswith(char) and 'OPCN' in l and 'fscx240' in l:
            m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+)', l)
            if m:
                s_ms = time_to_ms(m[1])
                if 115000 <= s_ms <= 130000:
                    print(f"  [{char}] enter_start={s_ms}ms")
                    break

# ==== CHECK 5: Original echo timing unchanged ====
print()
print("=" * 60)
print("CHECK 5: Original echoes still correct (23170ms section)")
print("=" * 60)

for l in lines:
    if 'OPJP-B' in l and 'fx,' in l:
        m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+)', l)
        if m:
            s_ms = time_to_ms(m[1])
            if 24000 <= s_ms <= 36000:
                text_part = l.split('fx,', 1)[-1]
                last_char = text_part[-1] if text_part else '?'
                if last_char in 'キヒナ聴':
                    print(f"  [{last_char}] start={m[1]}({s_ms}ms)")
