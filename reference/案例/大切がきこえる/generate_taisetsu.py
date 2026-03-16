# -*- coding: utf-8 -*-
"""
大切がきこえる - ASS 动态歌词特效生成器
番剧: 天使的3P! (天使の3P!) OP
歌手: 古賀葵/大野柚布子/遠藤ゆりか

设计要点:
  - 日语在上, 中文在下 (双行同时显示)
  - 整句歌词全文显示, 逐字卡拉OK高亮 (适合跟唱)
  - 汉字注音 (furigana) 使用罗马音行数据
  - 丰富的段落差异化特效
  - 合理的字间距, 避免重叠
"""

import re
import os
import math
import random
import copy
from collections import OrderedDict

# ============================================================
# 配置
# ============================================================
INPUT_FILE = r"C:\Users\Heng_Xin\Documents\Lyrics\古賀葵／大野柚布子／遠藤ゆりか - 大切がきこえる (88999817).ass"
OUTPUT_FILE = r"C:\Users\Heng_Xin\Documents\Lyrics\大切がきこえる_FX.ass"

RES_X = 1920
RES_Y = 1080

# 配色方案 - 天使的3P 粉紫暖色系
COLORS = {
    # 主色 (粉紫系)
    "jp_primary":     "&H00AF4BF0&",  # 粉紫色 (文字填充)
    "jp_secondary":   "&H000078FF&",  # 橙金 (卡拉OK高亮后)
    "jp_outline":     "&H00FFFFFF&",  # 白色描边
    "jp_shadow":      "&H96000000&",  # 半透明黑影

    # 高亮色
    "highlight_1":    "&H00FFFF&",    # 青色闪烁
    "highlight_2":    "&H8080FF&",    # 淡紫
    "highlight_3":    "&H00CCFF&",    # 暖金

    # 中文色
    "cn_primary":     "&H00AF4BF0&",
    "cn_outline":     "&H00FFFFFF&",

    # 粒子色
    "particle_1":     "&HEBBEBE&",
    "particle_2":     "&HF0B4AF&",
    "particle_3":     "&HFFFFFF&",

    # 发光色
    "glow_chorus":    "&H00FFFF&",
    "glow_bridge":    "&HFF88CC&",
}

# 字体
FONT_JP       = "FOT-PopJoy Std B"       # 日文主字体 (参考天使3P)
FONT_JP_FALL  = "A-OTF Shin Maru Go Pro M" # 备选
FONT_CN       = "Source Han Sans SC Medium"
FONT_FURIGANA = "FOT-PopJoy Std B"

# 字号
SIZE_JP       = 48
SIZE_CN       = 36
SIZE_FURIGANA = 22
SPACING_JP    = 3  # 字间距 (避免重叠)
SPACING_CN    = 2

# 位置 (1920x1080, 日语在上中文在下)
POS_JP_Y      = 60   # 日语距顶部
POS_CN_Y      = 115  # 中文距顶部 (紧跟日语下方)
POS_BOTTOM_JP = 920  # 底部歌词位置
POS_BOTTOM_CN = 975

# ============================================================
# ASS 解析器 (不依赖 PyonFX, 直接解析 LDDC 格式)
# ============================================================

def parse_time(ts):
    """解析 ASS 时间戳 -> 毫秒"""
    # 支持 H:MM:SS.xx 和 HH:MM:SS.xx
    m = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', ts.strip())
    if not m:
        return 0
    h, mi, s, cs = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return h * 3600000 + mi * 60000 + s * 1000 + cs * 10

def format_time(ms):
    """毫秒 -> ASS 时间戳 H:MM:SS.xx"""
    if ms < 0:
        ms = 0
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    cs = (ms % 1000) // 10
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def parse_kf_tags(text):
    """解析带 \\kf 标签的文本, 返回 [(duration_cs, syllable_text), ...]"""
    syls = []
    parts = re.split(r'\{\\kf(\d+)\}', text)
    # parts: ['', dur1, text1, dur2, text2, ...]
    i = 1
    while i < len(parts):
        dur = int(parts[i])
        txt = parts[i + 1] if i + 1 < len(parts) else ""
        syls.append((dur, txt))
        i += 2
    return syls

def parse_dialogue_line(line_str):
    """解析 Dialogue/Comment 行"""
    m = re.match(r'(Dialogue|Comment):\s*(\d+),([^,]+),([^,]+),([^,]*),([^,]*),(\d+),(\d+),(\d+),([^,]*),(.*)', line_str)
    if not m:
        return None
    return {
        "type": m.group(1),
        "layer": int(m.group(2)),
        "start": m.group(3).strip(),
        "end": m.group(4).strip(),
        "style": m.group(5).strip(),
        "name": m.group(6).strip(),
        "marginL": int(m.group(7)),
        "marginR": int(m.group(8)),
        "marginV": int(m.group(9)),
        "effect": m.group(10).strip(),
        "text": m.group(11),
        "start_ms": parse_time(m.group(3)),
        "end_ms": parse_time(m.group(4)),
    }

def parse_ass_file(filepath):
    """解析完整 ASS 文件"""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()

    lines_orig = []  # 日语 (orig)
    lines_ts = []    # 中文 (ts)
    lines_roma = []  # 罗马音 (roma)

    for raw_line in content.split('\n'):
        raw_line = raw_line.rstrip('\r\n')
        if not raw_line.startswith('Dialogue:'):
            continue
        parsed = parse_dialogue_line(raw_line)
        if not parsed:
            continue

        if parsed["style"] == "orig":
            parsed["syls"] = parse_kf_tags(parsed["text"])
            lines_orig.append(parsed)
        elif parsed["style"] == "ts":
            lines_ts.append(parsed)
        elif parsed["style"] == "roma":
            parsed["syls"] = parse_kf_tags(parsed["text"])
            lines_roma.append(parsed)

    return lines_orig, lines_ts, lines_roma


# ============================================================
# 段落分析
# ============================================================

# 手动标注段落 (根据歌词内容和时间)
# 前3行是 歌手信息/作词/作曲 -> info
# 然后根据时间和内容分段

def classify_sections(lines_orig):
    """为每行标注段落类型"""
    sections = []
    for line in lines_orig:
        t = line["start_ms"]
        # 歌手/作词/作曲 信息行 (0~1.27s)
        if t < 1270:
            sections.append("info")
        # A1段 (1.27 ~ 51s) 安静叙事
        elif t < 51000:
            sections.append("verse_A")
        # 副歌1 (51 ~ 86s)
        elif t < 86000:
            sections.append("chorus_1")
        # 间奏 + A2段 (86 ~ 135s)
        elif t < 135000:
            # 间奏过后有 キラキラ (29.86s) 然后进入A2
            if t < 96000:
                sections.append("interlude")
            else:
                sections.append("verse_B")
        # B段过渡 (135 ~ 162s)
        elif t < 162000:
            sections.append("bridge")
        # 副歌2 + 间奏2 (162 ~ 222s)
        elif t < 222000:
            sections.append("chorus_2")
        # C段 (222 ~ 260s)
        elif t < 260000:
            sections.append("verse_C")
        # 终章副歌 (260 ~ 末尾)
        else:
            sections.append("final_chorus")

    return sections


# ============================================================
# 汉字注音提取
# ============================================================

# 日语汉字范围 (CJK)
def is_kanji(ch):
    cp = ord(ch)
    return (0x4E00 <= cp <= 0x9FFF or
            0x3400 <= cp <= 0x4DBF or
            0xF900 <= cp <= 0xFAFF or
            0x20000 <= cp <= 0x2A6DF)

def extract_furigana_pairs(orig_syls, roma_syls):
    """
    尝试对齐日语音节和罗马音, 为汉字生成注音
    返回: [(kanji_text, reading), ...] 或 None
    """
    # 简单策略: 如果音节数一致且时间对齐, 直接配对
    if len(orig_syls) != len(roma_syls):
        return None

    pairs = []
    for (dur_o, text_o), (dur_r, text_r) in zip(orig_syls, roma_syls):
        text_o = text_o.strip()
        text_r = text_r.strip()
        if text_o and any(is_kanji(ch) for ch in text_o):
            pairs.append((text_o, text_r))
    return pairs if pairs else None


# ============================================================
# 特效字形定义
# ============================================================

# 星星 (来自参考: 天使の3P)
SHAPE_STAR = "m 26 37 l 38 27 l 45 19 l 52 11 l 57 7 b 66 0 72 9 64 29 l 59 26 l 62 31 b 58 36 52 43 46 47 l 41 44 l 44 48 b 41 52 37 56 33 58 l 28 52 l 30 58 l 27 61 l 24 58 l 24 61 l 21 58 l 17 61 l 17 59 b 11 62 6 64 0 64 l 0 60 b 5 60 12 57 16 54 l 14 51 l 18 51 l 17 47 l 20 50 l 20 42 l 24 38 l 25 45"

# 音符
SHAPE_NOTE = "m 5 0 b 2 0 0 2 0 5 b 0 8 2 10 5 10 b 8 10 10 8 10 5 b 10 2 8 0 5 0"

# 心形
SHAPE_HEART = "m 21 21 b 6 -7 46 -7 29 21 b 49 -2 63 34 30 28 b 63 44 31 65 25 32 b 26 65 -12 45 21 29 b -13 38 0 -5 21 21 m 25 22 b 21 22 21 28 25 28 b 29 28 29 22 25 22"

# 花瓣 (简化版)
SHAPE_PETAL = "m 0 0 b 8 -10 15 -4 21 -3 b 34 -2 32 -9 30 -11 b 25 -14 20 -6 27 -7"

PARTICLES = [SHAPE_STAR, SHAPE_NOTE, SHAPE_HEART]


# ============================================================
# 核心特效生成
# ============================================================

def estimate_char_width(fontsize, text):
    """估算文字像素宽度 (简化版, 日文约0.8~1.0倍字号)"""
    w = 0
    for ch in text:
        if ord(ch) > 0x7F:  # CJK / 假名
            w += fontsize * 0.95
        elif ch == ' ':
            w += fontsize * 0.35
        else:
            w += fontsize * 0.55
    return w

def compute_syl_positions(syls, fontsize, spacing, center_x):
    """计算每个音节的 x 位置 (居中排列)"""
    widths = []
    for dur, txt in syls:
        w = estimate_char_width(fontsize, txt) + spacing
        widths.append(w)

    total_w = sum(widths)
    start_x = center_x - total_w / 2

    positions = []
    x = start_x
    for i, w in enumerate(widths):
        cx = x + w / 2
        positions.append(cx)
        x += w
    return positions, total_w

def build_ass_header():
    """构建 ASS 文件头"""
    header = f"""[Script Info]
; Generated by HX-Ass-Skill FX Generator
; Anime: 天使の3P! (天使の3P!)
; Song: 大切がきこえる (OP)
Title: 大切がきこえる FX
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {RES_X}
PlayResY: {RES_Y}
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: JP_base,{FONT_JP},48,{COLORS["jp_primary"]},{COLORS["jp_secondary"]},{COLORS["jp_outline"]},{COLORS["jp_shadow"]},0,0,0,0,100,100,{SPACING_JP},0,1,3,2,8,30,30,{POS_JP_Y},1
Style: JP_highlight,{FONT_JP},48,&H00FFFFFF&,{COLORS["jp_secondary"]},{COLORS["jp_primary"]},{COLORS["jp_shadow"]},0,0,0,0,100,100,{SPACING_JP},0,1,3,2,8,30,30,{POS_JP_Y},1
Style: JP_glow,{FONT_JP},48,{COLORS["jp_primary"]},&H000000FF&,{COLORS["glow_chorus"]},&H00000000&,0,0,0,0,100,100,{SPACING_JP},0,1,5,0,8,30,30,{POS_JP_Y},1
Style: CN,{FONT_CN},36,{COLORS["cn_primary"]},&H000000FF&,{COLORS["cn_outline"]},{COLORS["jp_shadow"]},0,0,0,0,100,100,{SPACING_CN},0,1,2.5,1.5,2,30,30,{POS_CN_Y},1
Style: Furigana,{FONT_FURIGANA},22,{COLORS["jp_primary"]},&H000000FF&,{COLORS["jp_outline"]},{COLORS["jp_shadow"]},0,0,0,0,100,100,0,0,1,1.5,1,8,30,30,0,1
Style: Particle,{FONT_JP},30,&H00FFFFFF&,&H000000FF&,&H00000000&,&H00000000&,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Info,{FONT_CN},28,&H00FFFFFF&,&H000000FF&,&H64000000&,&H00000000&,0,0,0,0,100,100,0,0,1,2,1,8,30,30,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    return header


def generate_fx_lines(lines_orig, lines_ts, lines_roma):
    """生成所有特效行"""
    fx_lines = []
    sections = classify_sections(lines_orig)

    # 对齐日语/中文/罗马音 (通过时间匹配)
    ts_map = {}  # start_ms -> ts_line
    for ts in lines_ts:
        ts_map[ts["start_ms"]] = ts

    roma_map = {}  # start_ms -> roma_line
    for roma in lines_roma:
        roma_map[roma["start_ms"]] = roma

    center_x = RES_X / 2

    for idx, orig in enumerate(lines_orig):
        section = sections[idx] if idx < len(sections) else "verse_A"
        start_ms = orig["start_ms"]
        end_ms = orig["end_ms"]
        syls = orig["syls"]

        if not syls:
            continue

        # 跳过 duration=0 的纯信息行
        if all(dur == 0 for dur, _ in syls):
            # 信息行: 歌手名/词曲信息
            plain_text = "".join(t for _, t in syls)
            fx_lines.append(
                f"Dialogue: 5,{format_time(start_ms)},{format_time(end_ms)},Info,,0,0,0,,"
                f"{{\\an8\\pos({center_x},30)\\fad(500,500)\\blur0.5}}{plain_text}"
            )
            continue

        # 获取对应中文翻译
        ts_line = ts_map.get(start_ms)
        # 获取罗马音
        roma_line = roma_map.get(start_ms)

        # --- 计算日语音节位置 ---
        syl_positions, total_w = compute_syl_positions(syls, SIZE_JP, SPACING_JP, center_x)

        # --- 决定布局位置 (上方 or 下方, 基于段落) ---
        jp_y = POS_JP_Y
        cn_y = POS_CN_Y
        if section in ("chorus_1", "chorus_2", "final_chorus"):
            jp_y = POS_JP_Y  # 副歌保持顶部
            cn_y = POS_CN_Y
        elif section == "bridge":
            jp_y = POS_JP_Y + 5  # 微调
            cn_y = POS_CN_Y + 5

        # 提前/延后显示时间 (让字幕提前出现, 便于跟唱)
        pre_time = 400  # ms, 提前显示
        post_time = 300  # ms, 延后消失

        display_start = max(0, start_ms - pre_time)
        display_end = end_ms + post_time

        # ============================================================
        # Layer 0: 底层发光 (副歌段)
        # ============================================================
        if section in ("chorus_1", "chorus_2", "final_chorus"):
            for si, (dur_cs, syl_text) in enumerate(syls):
                if not syl_text.strip():
                    continue
                syl_start_ms = start_ms + sum(d * 10 for d, _ in syls[:si])
                syl_dur_ms = dur_cs * 10
                sx = syl_positions[si]

                intensity = 1.3 if section == "final_chorus" else 1.0
                blur_val = 6 * intensity
                bord_val = 4 * intensity

                glow_color = COLORS["glow_chorus"]
                if section == "final_chorus":
                    glow_color = "&H00CCFF&"

                fx_lines.append(
                    f"Dialogue: 0,{format_time(display_start)},{format_time(display_end)},JP_glow,,0,0,0,,"
                    f"{{\\an5\\pos({sx:.0f},{jp_y})"
                    f"\\1a&HFF&\\3a&H60&\\3c{glow_color}\\bord{bord_val:.1f}\\blur{blur_val:.1f}"
                    f"\\t({syl_start_ms - start_ms},{syl_start_ms - start_ms + syl_dur_ms},"
                    f"\\3a&H20&\\bord{bord_val + 3:.1f}\\blur{blur_val + 4:.1f})"
                    f"\\t({syl_start_ms - start_ms + syl_dur_ms},{end_ms - start_ms},"
                    f"\\3a&HCC&\\bord{bord_val:.1f}\\blur{blur_val:.1f})"
                    f"\\fad({pre_time},300)}}{syl_text}"
                )

        # ============================================================
        # Layer 1: 日语底层 (全文显示, 未高亮状态, \an5\pos 逐字)
        # ============================================================
        for si, (dur_cs, syl_text) in enumerate(syls):
            if not syl_text.strip():
                continue
            sx = syl_positions[si]
            syl_start_ms = start_ms + sum(d * 10 for d, _ in syls[:si])
            syl_dur_ms = dur_cs * 10

            # 选择进场效果
            if section == "info":
                continue  # 已经处理过
            elif section == "verse_A":
                # A段: 柔和淡入, 字符依次出现 (打字机风格)
                char_delay = min(si * 35, 400)
                fx_lines.append(
                    f"Dialogue: 1,{format_time(display_start + char_delay)},{format_time(display_end)},JP_base,,0,0,0,,"
                    f"{{\\an5\\pos({sx:.0f},{jp_y})"
                    f"\\fad(250,300)\\blur0.5"
                    f"\\t({syl_start_ms - start_ms},{syl_start_ms - start_ms + int(syl_dur_ms * 0.4)},"
                    f"\\1c&H00FFFF&\\fscx110\\fscy110)"
                    f"\\t({syl_start_ms - start_ms + int(syl_dur_ms * 0.4)},{syl_start_ms - start_ms + syl_dur_ms},"
                    f"\\1c{COLORS['jp_secondary']}\\fscx100\\fscy100)"
                    f"}}{syl_text}"
                )
            elif section in ("verse_B", "verse_C"):
                # B/C段: 从下方微滑入
                offset_y = 8
                fx_lines.append(
                    f"Dialogue: 1,{format_time(display_start)},{format_time(display_end)},JP_base,,0,0,0,,"
                    f"{{\\an5\\move({sx:.0f},{jp_y + offset_y},{sx:.0f},{jp_y},0,300)"
                    f"\\fad(300,300)\\blur0.3"
                    f"\\t({syl_start_ms - start_ms},{syl_start_ms - start_ms + int(syl_dur_ms * 0.3)},"
                    f"\\1c&H00DDFF&\\fscx108\\fscy108\\blur0)"
                    f"\\t({syl_start_ms - start_ms + int(syl_dur_ms * 0.3)},{syl_start_ms - start_ms + syl_dur_ms},"
                    f"\\1c{COLORS['jp_secondary']}\\fscx100\\fscy100\\blur0.3)"
                    f"}}{syl_text}"
                )
            elif section == "interlude":
                # 间奏: 特殊处理 キラキラ 等
                fx_lines.append(
                    f"Dialogue: 1,{format_time(display_start)},{format_time(display_end)},JP_base,,0,0,0,,"
                    f"{{\\an5\\pos({sx:.0f},{jp_y})"
                    f"\\fad(500,500)\\blur1"
                    f"\\t({syl_start_ms - start_ms},{syl_start_ms - start_ms + syl_dur_ms},"
                    f"\\1c&H00FFFF&\\blur0\\fscx115\\fscy115)"
                    f"\\t({syl_start_ms - start_ms + syl_dur_ms},{end_ms - start_ms},"
                    f"\\1c{COLORS['jp_secondary']}\\fscx100\\fscy100\\blur0.5)"
                    f"}}{syl_text}"
                )
            elif section == "bridge":
                # 过渡段: 旋转微动 + 色彩过渡
                rot = random.uniform(-3, 3)
                fx_lines.append(
                    f"Dialogue: 1,{format_time(display_start)},{format_time(display_end)},JP_base,,0,0,0,,"
                    f"{{\\an5\\pos({sx:.0f},{jp_y})"
                    f"\\frz{rot:.1f}\\fad(300,400)\\blur0.5"
                    f"\\t({syl_start_ms - start_ms},{syl_start_ms - start_ms + int(syl_dur_ms * 0.3)},"
                    f"\\frz0\\1c&HFF88CC&\\fscx112\\fscy112\\blur0)"
                    f"\\t({syl_start_ms - start_ms + int(syl_dur_ms * 0.3)},{syl_start_ms - start_ms + syl_dur_ms},"
                    f"\\1c{COLORS['jp_secondary']}\\fscx100\\fscy100\\blur0.3)"
                    f"}}{syl_text}"
                )
            elif section in ("chorus_1", "chorus_2", "final_chorus"):
                # 副歌: 缩放冲击 + 颜色爆发
                scale_peak = 125 if section == "final_chorus" else 118
                fx_lines.append(
                    f"Dialogue: 2,{format_time(display_start)},{format_time(display_end)},JP_base,,0,0,0,,"
                    f"{{\\an5\\pos({sx:.0f},{jp_y})"
                    f"\\fad({pre_time},300)\\blur0.3"
                    f"\\t({syl_start_ms - start_ms},{syl_start_ms - start_ms + int(syl_dur_ms * 0.2)},"
                    f"\\fscx{scale_peak}\\fscy{scale_peak}\\1c&H00FFFF&\\blur0)"
                    f"\\t({syl_start_ms - start_ms + int(syl_dur_ms * 0.2)},{syl_start_ms - start_ms + int(syl_dur_ms * 0.6)},"
                    f"\\fscx100\\fscy100\\1c{COLORS['jp_secondary']})"
                    f"\\t({syl_start_ms - start_ms + int(syl_dur_ms * 0.6)},{syl_start_ms - start_ms + syl_dur_ms},"
                    f"\\1c{COLORS['jp_primary']}\\blur0.3)"
                    f"}}{syl_text}"
                )

        # ============================================================
        # Layer 3: 粒子效果 (副歌 + 终章)
        # ============================================================
        if section in ("chorus_1", "chorus_2", "final_chorus"):
            particle_count = 3 if section == "final_chorus" else 2
            for si, (dur_cs, syl_text) in enumerate(syls):
                if not syl_text.strip() or dur_cs < 5:
                    continue
                syl_start_ms = start_ms + sum(d * 10 for d, _ in syls[:si])
                syl_dur_ms = dur_cs * 10
                sx = syl_positions[si]

                for p in range(particle_count):
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.randint(25, 65)
                    dx = math.cos(angle) * dist
                    dy = math.sin(angle) * dist
                    shape = random.choice(PARTICLES)
                    p_color = random.choice([COLORS["particle_1"], COLORS["particle_2"], COLORS["particle_3"]])
                    scale = random.randint(30, 55)
                    fade_out = random.randint(300, 600)

                    p_start = syl_start_ms
                    p_end = syl_start_ms + syl_dur_ms + fade_out

                    fx_lines.append(
                        f"Dialogue: 0,{format_time(p_start)},{format_time(p_end)},Particle,,0,0,0,,"
                        f"{{\\an5\\move({sx:.0f},{jp_y},{sx + dx:.0f},{jp_y + dy:.0f})"
                        f"\\fad(100,{fade_out})\\blur{2 + p}\\bord0"
                        f"\\fscx{scale}\\fscy{scale}"
                        f"\\1c{p_color}\\1a&H{p * 30:02X}&"
                        f"\\frz{random.randint(-180, 180)}"
                        f"\\t(0,{syl_dur_ms},\\fscx{scale - 15}\\fscy{scale - 15}\\frz{random.randint(-360, 360)})"
                        f"\\p2}}{shape}"
                    )

        # ============================================================
        # Layer 3: 星星装饰 (B段/过渡段)
        # ============================================================
        if section in ("bridge", "verse_B", "verse_C") and len(syls) > 3:
            # 在行首和行尾各放一个星星
            for pos_x, delay in [(syl_positions[0] - 40, 0), (syl_positions[-1] + 40, 200)]:
                star_scale = random.randint(40, 60)
                rot_speed = random.randint(60, 180)
                fx_lines.append(
                    f"Dialogue: 0,{format_time(display_start + delay)},{format_time(display_end)},Particle,,0,0,0,,"
                    f"{{\\an5\\pos({pos_x:.0f},{jp_y})"
                    f"\\fad(400,400)\\blur2\\bord0.5"
                    f"\\fscx{star_scale}\\fscy{star_scale}"
                    f"\\1c&HFFFFFF&\\3c{COLORS['glow_bridge']}"
                    f"\\frz0\\t(0,{end_ms - start_ms},\\frz{rot_speed})"
                    f"\\p2}}{SHAPE_STAR}"
                )

        # ============================================================
        # Layer 4: 中文翻译 (同时显示, 淡入淡出, 简洁)
        # ============================================================
        if ts_line:
            cn_text = ts_line["text"]
            # 去除可能的标签
            cn_clean = re.sub(r'\{[^}]*\}', '', cn_text).strip()

            if section in ("chorus_1", "chorus_2", "final_chorus"):
                # 副歌中文: 略微大一点, 带描边
                fx_lines.append(
                    f"Dialogue: 3,{format_time(display_start)},{format_time(display_end)},CN,,0,0,0,,"
                    f"{{\\an8\\pos({center_x},{cn_y})"
                    f"\\fad({pre_time},300)\\blur0.3"
                    f"\\bord2.5\\3c&HFFFFFF&"
                    f"}}{cn_clean}"
                )
            elif section in ("bridge",):
                fx_lines.append(
                    f"Dialogue: 3,{format_time(display_start)},{format_time(display_end)},CN,,0,0,0,,"
                    f"{{\\an8\\pos({center_x},{cn_y})"
                    f"\\fad(400,400)\\blur0.5"
                    f"}}{cn_clean}"
                )
            else:
                # 普通段中文
                fx_lines.append(
                    f"Dialogue: 3,{format_time(display_start)},{format_time(display_end)},CN,,0,0,0,,"
                    f"{{\\an8\\pos({center_x},{cn_y})"
                    f"\\fad(300,300)\\blur0.3"
                    f"}}{cn_clean}"
                )

        # ============================================================
        # Layer 5: 罗马音注音 (显示在日语上方, 较小)
        # ============================================================
        if roma_line and roma_line["syls"]:
            roma_syls = roma_line["syls"]
            # 尝试对齐
            if len(roma_syls) == len(syls):
                for si, ((dur_o, text_o), (dur_r, text_r)) in enumerate(zip(syls, roma_syls)):
                    text_o = text_o.strip()
                    text_r = text_r.strip()
                    # 只为包含汉字的音节显示注音
                    if text_o and text_r and any(is_kanji(ch) for ch in text_o):
                        sx = syl_positions[si]
                        furigana_y = jp_y - 28  # 在日语上方

                        syl_start_ms_r = start_ms + sum(d * 10 for d, _ in syls[:si])

                        fx_lines.append(
                            f"Dialogue: 5,{format_time(display_start)},{format_time(display_end)},Furigana,,0,0,0,,"
                            f"{{\\an5\\pos({sx:.0f},{furigana_y})"
                            f"\\fad(300,300)\\blur0.3"
                            f"\\t({syl_start_ms_r - start_ms},{syl_start_ms_r - start_ms + dur_o * 10},"
                            f"\\1c&H00FFFF&)"
                            f"\\t({syl_start_ms_r - start_ms + dur_o * 10},{end_ms - start_ms},"
                            f"\\1c{COLORS['jp_primary']})"
                            f"}}{text_r}"
                        )

    return fx_lines


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("  大切がきこえる - ASS FX Generator")
    print("  天使の3P! OP")
    print("=" * 60)

    # 解析输入文件
    lines_orig, lines_ts, lines_roma = parse_ass_file(INPUT_FILE)
    print(f"  Parsed: {len(lines_orig)} orig, {len(lines_ts)} ts, {len(lines_roma)} roma")

    # 生成特效行
    fx_lines = generate_fx_lines(lines_orig, lines_ts, lines_roma)
    print(f"  Generated: {len(fx_lines)} FX lines")

    # 构建完整 ASS
    header = build_ass_header()

    # 写入原始行作为注释
    comments = []
    comments.append("; === Original lines (commented out) ===")
    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.rstrip('\r\n')
            if line.startswith("Dialogue:"):
                comments.append(f"Comment: {line[len('Dialogue: '):]}")

    # 合并输出
    output = header
    for c in comments:
        output += c + "\n"
    output += "; === FX lines ===\n"
    for fx in fx_lines:
        output += fx + "\n"

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8-sig") as f:
        f.write(output)

    print()
    print("=" * 60)
    print(f"  [DONE] FX generated!")
    print(f"  Output: {OUTPUT_FILE}")
    print(f"  Total FX events: {len(fx_lines)}")
    print(f"  Resolution: {RES_X}x{RES_Y}")
    print("=" * 60)


if __name__ == "__main__":
    random.seed(42)  # 可重现的随机效果
    main()
