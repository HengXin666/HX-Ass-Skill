"""
Calculate echo timing for 卑怯だったずっと僕は (115920ms)

k-tags: {\\kf52}卑{\\kf258}怯{\\kf39}だ{\\kf39}っ{\\kf238}た{\\kf39}ず{\\kf39}っ{\\kf251}と{\\kf69}僕{\\kf214}は

Word groups:
  卑怯     = kf52 + kf258 = 310cs → 3100ms
  だった   = kf39 + kf39 + kf238 = 316cs → 3160ms  
  ずっと   = kf39 + kf39 + kf251 = 329cs → 3290ms
  僕は     = kf69 + kf214 = 283cs → 2830ms

Cumulative start times (from line start 115920ms):
  卑怯:     0cs        → 115920ms + 0    = 115920ms  → delay = 0ms
  だった:   310cs      → 115920ms + 3100 = 119020ms  → delay = 3100ms
  ずっと:   310+316 = 626cs → 115920ms + 6260 = 122180ms → delay = 6260ms
  僕は:     626+329 = 955cs → 115920ms + 9550 = 125470ms → delay = 9550ms

Total: 955 + 283 = 1238cs → 12380ms (line dur = 128640-115920 = 12720ms, close match)
"""

# Existing echo patterns for reference:
# 23170ms: delays = [2040, 5170, 8460, 11590], echo_duration = 1370
# 35890ms: delays = [2160, 5330, 8550, 11670], echo_duration = 1250
# 128640ms: delays = [2200, 5400, 8600, 11600], echo_duration = 1300

# For reference, let's check the timing pattern of existing echoes
# 23170: きみは(0) ひとり(~3100?) 何を(?) 聴いてた(?)
# Let's verify with the first line's k-tags

print("=== Line 115920ms: 卑怯だったずっと僕は ===")
k_vals = [52, 258, 39, 39, 238, 39, 39, 251, 69, 214]
chars  = ['卑','怯','だ','っ','た','ず','っ','と','僕','は']
words  = ['卑怯', 'だった', 'ずっと', '僕は']
word_k_groups = [[52, 258], [39, 39, 238], [39, 39, 251], [69, 214]]

base_ms = 115920
cumul = 0
for wi, (word, k_group) in enumerate(zip(words, word_k_groups)):
    delay_ms = cumul * 10
    word_dur = sum(k_group) * 10
    print(f"  {word:8s}: delay={delay_ms:>6d}ms  dur={word_dur:>5d}ms  abs_start={base_ms+delay_ms}ms")
    cumul += sum(k_group)

print(f"  Total: {cumul}cs = {cumul*10}ms  (line_dur = {128640-115920}ms)")

# Now calculate echo delays
# The echo typically starts with a delay matching each word's syllable start
# Looking at existing patterns:
# 23170 line: きみはひとり何を聴いてた
# k-tags: {\\kf23}き{\\kf15}み{\\kf166}は{\\kf38}ひ{\\kf18}と{\\kf245}り{\\kf27}何{\\kf200}を{\\kf27}聴{\\kf27}い{\\kf27}て{\\kf183}た
print()
print("=== Verify with 23170ms line (from existing echo) ===")
# Delays are 2040, 5170, 8460, 11590
# These are NOT the word start times, they include the echo delay offset
# echo_delay = word_start_time + ~2000ms (echo lags behind by ~2s)
# Actually looking at the code: echo_start_ms = ms + word_def['echo_delay'] - 500

# Let's compute the first line to understand the pattern
k_vals_1 = [23, 15, 166, 38, 18, 245, 27, 200, 27, 27, 27, 183]
chars_1  = ['き','み','は','ひ','と','り','何','を','聴','い','て','た']
words_1  = ['きみは', 'ひとり', '何を', '聴いてた']
w_k_groups_1 = [[23, 15, 166], [38, 18, 245], [27, 200], [27, 27, 27, 183]]

cumul = 0
print("  Word starts:")
for wi, (word, k_group) in enumerate(zip(words_1, w_k_groups_1)):
    abs_start = 23170 + cumul * 10
    print(f"    {word:8s}: cumul={cumul:>4d}cs → abs={abs_start}ms  existing_delay={[2040,5170,8460,11590][wi]}ms")
    cumul += sum(k_group)

# Pattern analysis: 
# きみは: word_start=0cs→0ms, echo_delay=2040ms → offset=+2040ms from word start
# ひとり: word_start=204cs→2040ms, echo_delay=5170ms → offset=5170-2040=+3130ms from word start? 
# No wait - echo_delay is relative to line start, not word start
# きみは: word_start_from_line=0ms, echo_delay=2040ms → echo is at +2040 from word start
# ひとり: word_start_from_line=2040ms, echo_delay=5170ms → echo is at +3130 from word start
# 何を: word_start_from_line=5050ms, echo_delay=8460ms → echo is at +3410 from word start
# 聴いてた: word_start_from_line=7320ms, echo_delay=11590ms → echo is at +4270 from word start

# Actually the delays ARE the absolute times from line start
# The pattern seems like: echo_delay ≈ word_start + ~2000ms consistent lag
print()
print("=== Echo delay analysis ===")
word_starts_1 = [0, 2040, 5050, 7320]  # ms from line start
echo_delays_1 = [2040, 5170, 8460, 11590]
for ws, ed in zip(word_starts_1, echo_delays_1):
    print(f"  word_start={ws:>5d}ms  echo_delay={ed:>5d}ms  diff={ed-ws:>5d}ms")

# So echo_delay = word_start + lag, where lag varies: 2040, 3130, 3410, 4270
# Actually these ARE the echo_delay values in the config - they're offsets from line start

# For the NEW echo (115920ms), we need to add similar lag to word start times:
# The delay values in the config ARE the echo timing relative to line start
# For existing 128640: delays = [2200, 5400, 8600, 11600] with words starting at 0, 3230, 6490, 9530
# Let's verify:
print()
print("=== Verify 128640ms echoes ===")
k_vals_3 = [55, 18, 250, 52, 17, 230, 19, 26, 26, 19, 239, 45, 45, 198]
chars_3  = ['き','み','は','い','つ','も','向','こ','う','見','ず','だ','っ','た']
words_3  = ['きみは', 'いつも', '向こう見ず', 'だった']
w_k_groups_3 = [[55, 18, 250], [52, 17, 230], [19, 26, 26, 19, 239], [45, 45, 198]]

cumul = 0
word_starts_3 = []
for wi, (word, k_group) in enumerate(zip(words_3, w_k_groups_3)):
    word_starts_3.append(cumul * 10)
    cumul += sum(k_group)

echo_delays_3 = [2200, 5400, 8600, 11600]
for ws, ed in zip(word_starts_3, echo_delays_3):
    print(f"  word_start={ws:>5d}ms  echo_delay={ed:>5d}ms  diff={ed-ws:>5d}ms")

# The diff is the actual delay between when the singer starts the word and when the echo appears
# For 128640: diffs = 2200, 2410, 2310, 2330 → pretty consistent ~2200-2400ms lag

# Now for 115920ms line:
# Word starts: 卑怯=0ms, だった=3100ms, ずっと=6260ms, 僕は=9550ms
# Use similar lag: ~2100-2200ms (average of existing patterns)
# echo_delay ≈ word_start + 2100ms (slightly less than 128640's since it's the earlier line)

print()
print("=== Proposed echo for 115920ms ===")
word_starts_new = [0, 3100, 6260, 9550]
# Use ~2100ms lag (matching the pattern of the first echo which has 2040 base lag)
lag = 2100
for ws in word_starts_new:
    ed = ws + lag
    print(f"  word_start={ws:>5d}ms  proposed_delay={ed:>5d}ms")

# Echo text mappings for 卑怯だったずっと僕は:
# 卑怯 → ヒキョウ (cowardly)
# だった → ダッタ
# ずっと → ズット
# 僕は → ボクは
# Echo duration: about 1200-1400ms
