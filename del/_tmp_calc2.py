"""
Reference file analysis: OPCN word-by-word Comment start times
(These are the ACTUAL word appearance times from the reference)

Section 1 (line_start=23170ms, line_end=35890ms):
  孤獨的: Comment start=23540ms → delay = 23540 - 23170 = 370ms
  你:     Comment start=26710ms → delay = 26710 - 23170 = 3540ms
  聽到了: Comment start=29960ms → delay = 29960 - 23170 = 6790ms
  什麼:   Comment start=33170ms → delay = 33170 - 23170 = 10000ms

  ENTER start = Comment start - 300ms (animation completes at word appear time)
  孤獨的: ENTER 23240ms (= 23540-300) ✓ matches reference 23240ms
  你:     ENTER 26410ms (= 26710-300) ✓ matches reference 26410ms
  聽到了: ENTER 29660ms (= 29960-300) ✓ matches reference 29660ms
  什麼:   ENTER 32870ms (= 33170-300) ✓ matches reference 32870ms

Section 2 (line_start=35890ms, line_end=48700ms):
  我:     Comment start=36340ms → delay = 36340 - 35890 = 450ms
  看到了: Comment start=39510ms → delay = 39510 - 35890 = 3620ms
  遙遠的: Comment start=42770ms → delay = 42770 - 35890 = 6880ms
  幻夢:   Comment start=45940ms → delay = 45940 - 35890 = 10050ms

  ENTER start verification:
  我:     36040ms (= 36340-300) ✓ matches reference
  看到了: 39210ms (= 39510-300) ✓ matches reference
  遙遠的: 42470ms (= 42770-300) ✓ matches reference
  幻夢:   45640ms (= 45940-300) ✓ matches reference

Current code delays (WRONG - these match echo delays, not word appear times):
  Section 1: [2040, 5170, 8460, 11590]
  Section 2: [2160, 5330, 8550, 11670]
  Section 3 (128640): [2200, 5400, 8600] (no 4th word)

CORRECT delays should be:
  Section 1: [370, 3540, 6790, 10000]
  Section 2: [450, 3620, 6880, 10050]
"""

print("=== CORRECT delay values from reference ===")
print("Section 1 (23170ms):")
print("  孤獨的/独自一人: delay=370ms  (was 2040)")
print("  你:             delay=3540ms (was 5170)")
print("  聽到了/听到了:   delay=6790ms (was 8460)")
print("  什麼/什么:       delay=10000ms (was 11590)")

print()
print("Section 2 (35890ms):")
print("  我:             delay=450ms  (was 2160)")
print("  看到了:          delay=3620ms (was 5330)")
print("  遙遠的/遥远的:   delay=6880ms (was 8550)")
print("  幻夢/幻梦:       delay=10050ms (was 11670)")

# Now calculate Section 3 (128640ms)
# Using the same pattern: words spaced ~3200ms apart
# Line duration: 141490 - 128640 = 12850ms
# Similar spacing ratio as section 1&2
# Ref Comment times for section 3 are not available, so estimate:
# The pattern is: first word at ~370-450ms, then ~3200ms apart
print()
print("=== Calculate Section 3 (128640ms - 141490ms) ===")
print("Line: きみはいつも向こう見ずだった")
print("CN: 而你 → 却总是 → 顾前不顾后")

# From k-tags: {\\kf55}き{\\kf18}み{\\kf250}は{\\kf52}い{\\kf17}つ{\\kf230}も{\\kf19}向{\\kf26}こ{\\kf26}う{\\kf19}見{\\kf239}ず{\\kf45}だ{\\kf45}っ{\\kf198}た
# Word groups:
# きみは: 55+18+250 = 323cs → 3230ms
# いつも: 52+17+230 = 299cs → 2990ms  
# 向こう見ず: 19+26+26+19+239 = 329cs → 3290ms
# だった: 45+45+198 = 288cs → 2880ms
# Cumulative: 0, 3230, 6220, 9510

# Following the reference pattern where word appear = ~line_start + small_offset + word_position
# The CN words should appear slightly after the JP words start
# For sections 1&2, delay ≈ word_start_offset + 370~450ms

# For echo_delay 2200 → actual word start ≈ 0ms → CN delay ≈ 370ms (but line is different)
# Actually let's look at the reference Comment for section 3
print()
print("Need to check reference for section 3 Comment times...")

# For the NEW section at 115920ms:
print()
print("=== Calculate NEW Section (115920ms - 128640ms) ===")
print("Line: 卑怯だったずっと僕は")
print("CN: 裹足不前的我不过是个懦夫")
# k-tags: {\\kf52}卑{\\kf258}怯{\\kf39}だ{\\kf39}っ{\\kf238}た{\\kf39}ず{\\kf39}っ{\\kf251}と{\\kf69}僕{\\kf214}は
# Word groups:
# 卑怯: 52+258 = 310cs → 3100ms
# だった: 39+39+238 = 316cs → 3160ms
# ずっと: 39+39+251 = 329cs → 3290ms  
# 僕は: 69+214 = 283cs → 2830ms
# Cumulative start: 0, 3100, 6260, 9550

# Echo timing: these are the JP singing times for each word
# Echo delay = cumul + ~2100ms lag
# CN word appear = cumul + ~370ms offset (following ref pattern)
print("JP word starts from line: 0, 3100, 6260, 9550")
print("Proposed CN delays (word_start + 370ms): 370, 3470, 6630, 9920")
print("Proposed echo delays (word_start + 2100ms): 2100, 5200, 8360, 11650")
