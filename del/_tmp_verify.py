import re

path = r"C:\Users\Heng_Xin\Documents\Lyrics\Lia - Bravely You (28055813)_KFX.ass"
lines = open(path, 'r', encoding='utf-8-sig').read().splitlines()

def time_to_ms(t):
    m = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', t)
    if m:
        h, mi, s, cs = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        return (h * 3600 + mi * 60 + s) * 1000 + cs * 10
    return 0

# Find OPCN word-by-word lines (the first section: "独自一人 你 听到了 什么")
# These should be around the 23170ms mark
print("=== OPCN Word-by-word section 1 (23170ms) ===")
print("First char of each word's ENTER lines:")
for i, l in enumerate(lines):
    if 'OPCN' not in l or 'fx,' not in l:
        continue
    m = re.match(r'Dialogue:\s*\d+,\s*(\d+:\d+:\d+\.\d+),\s*(\d+:\d+:\d+\.\d+),\s*OPCN\s*,', l)
    if not m:
        continue
    ms = time_to_ms(m[1])
    end_ms = time_to_ms(m[2])
    # Only first word-by-word section
    if 23000 <= ms <= 37000:
        # Get char at end of line
        text_part = l.split('fx,', 1)[-1] if 'fx,' in l else ''
        last_char = text_part[-1] if text_part else '?'
        # Only print first band of each char (check for fscx240 which is enter)
        if 'fscx240' in l and '(-70,20)' in text_part:
            print(f"  [{last_char}] Start={m[1]} ({ms}ms) End={m[2]} ({end_ms}ms)")

# Now let's look at the OPCN_WORD_BY_WORD delays and expected vs actual timing
print()
print("=== Expected timing ===")
print("  Line start: 23170ms")
print("  Word '独自一人': delay=2040 → appear at 25210ms")
print("  Word '你':       delay=5170 → appear at 28340ms")
print("  Word '听到了':   delay=8460 → appear at 31630ms")
print("  Word '什么':     delay=11590 → appear at 34760ms")

# Check the echo line at 23170ms too - what's the echo_delay timing?
print()
print("=== Echo timing check (23170ms) ===")
print("  echo 'キミは': echo_delay=2040, echo_start=23170+2040-500=24710ms")
print("  echo 'ヒトリ': echo_delay=5170, echo_start=23170+5170-500=27840ms")
print("  echo 'ナニも': echo_delay=8460, echo_start=23170+8460-500=31130ms")
print("  echo '聴こえない': echo_delay=11590, echo_start=23170+11590-500=34260ms")

# Verify: For Word '独自一人' with delay=2040:
# word_appear_ms = 23170 + 2040 = 25210ms
# word_enter_start = 25210ms  (current code)
# So the ENTER animation plays from 25210 to 25510ms (300ms)
# But the echo 'キミは' starts at 24710ms (echo_delay 2040 - 500 = 23170+1540)
# WAIT: echo uses echo_delay=2040, so echo starts at 23170+2040-500=24710ms
# And the OPCN word uses delay=2040, so word_appear = 23170+2040 = 25210ms
# The OPCN word appears 500ms AFTER the echo starts! That's the pattern - the CN word follows the echo
# But... the user says the OPCN_WORD_BY_WORD delay timing is wrong.

# Let me look at this differently. The delay values in OPCN_WORD_BY_WORD
# are the SAME as the echo_delay values. 
# For echo: echo_start = line_ms + echo_delay - 500  (500ms early)
# For OPCN: word_appear = line_ms + delay  
# So OPCN word appears at the same time as the MAIN singer starts the word
# (delay = word start offset from line start)

# The user says "以第一个字的出现时间作为这个词的出现时间" - meaning
# the word should appear when its first CHARACTER appears in the main lyric.
# Currently word_appear = ms + delay, and delay matches the karaoke timing.
# This should already be correct...

# Unless the issue is that the ENTER ANIMATION takes 300ms to complete,
# so the character isn't fully visible until word_appear + 300ms.
# Maybe the user wants the animation to be COMPLETED at word_appear_ms,
# not STARTED at word_appear_ms?

print()
print("=== Current behavior vs expected ===")
print("  Current: ENTER animation STARTS at word_appear_ms")
print("  → Character not fully visible until word_appear_ms + 300ms")
print("  Expected: Character should be fully visible AT word_appear_ms")  
print("  → ENTER animation should START at word_appear_ms - 300ms")
print("  → word_enter_start = word_appear_ms - 300")
