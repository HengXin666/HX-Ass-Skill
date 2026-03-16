#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例记录工具 — 自动化创建案例经验目录和文件

用法:
    python -X utf8 record_case.py <歌曲名> [--song-file <k帧.ass>] [--kfx-file <成品_KFX.ass>] [--build-script <build_kfx.ps1>]

功能:
    1. 在 reference/案例/{歌曲名}/ 下创建目录
    2. 复制 k帧、成品、构建脚本到案例目录
    3. 生成制作记录模板 (制作记录.md)
    4. 统计 KFX 文件信息

示例:
    python -X utf8 record_case.py "星空のMemories" --song-file "k帧.ass" --kfx-file "output_KFX.ass" --build-script "build_kfx_hoshi.ps1"
"""

import sys
import os
import re
import shutil
import argparse
from pathlib import Path
from datetime import date
from collections import Counter


def find_project_root() -> Path:
    """查找项目根目录（包含 furigana_map.txt 的目录）"""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "furigana_map.txt").exists():
            return current
        if (current / "reference" / "案例").exists():
            return current
        current = current.parent
    # fallback to script's grandparent
    return Path(__file__).resolve().parent.parent


def analyze_ass_file(filepath: Path) -> dict:
    """分析 ASS 文件，提取统计信息"""
    stats = {
        "total_lines": 0,
        "styles": [],
        "comments": 0,
        "dialogues": 0,
        "fx_lines": 0,
        "karaoke_lines": 0,
        "template_lines": 0,
        "has_furigana": False,
        "has_kf": False,
        "playres": "",
        "file_size_kb": 0,
    }

    if not filepath.exists():
        return stats

    stats["file_size_kb"] = filepath.stat().st_size / 1024

    try:
        raw = filepath.read_bytes()
        if raw[:3] == b'\xef\xbb\xbf':
            content = raw[3:].decode('utf-8')
        else:
            content = raw.decode('utf-8', errors='replace')
    except Exception:
        return stats

    lines = content.splitlines()
    stats["total_lines"] = len(lines)

    for line in lines:
        if line.startswith("Style:"):
            name = line.split(",")[0].replace("Style:", "").strip()
            stats["styles"].append(name)
        elif line.startswith("Comment:"):
            stats["comments"] += 1
            parts = line.split(",", 9)
            if len(parts) >= 10:
                effect = parts[3].strip()
                if effect == "karaoke":
                    stats["karaoke_lines"] += 1
                    if "|<" in parts[9]:
                        stats["has_furigana"] = True
                    if r"\kf" in parts[9]:
                        stats["has_kf"] = True
                elif "template" in effect:
                    stats["template_lines"] += 1
        elif line.startswith("Dialogue:"):
            stats["dialogues"] += 1
            parts = line.split(",", 9)
            if len(parts) >= 10 and parts[3].strip() == "fx":
                stats["fx_lines"] += 1
        elif line.startswith("PlayResX:"):
            stats["playres"] = f"{line.split(':',1)[1].strip()}"
        elif line.startswith("PlayResY:"):
            stats["playres"] += f"x{line.split(':',1)[1].strip()}"

    return stats


def generate_record_template(song_name: str, stats_kfx: dict, stats_input: dict) -> str:
    """生成制作记录模板"""
    today = date.today().strftime("%Y-%m-%d")

    template = f"""# {song_name} — KFX 制作案例记录

> **歌曲**: {song_name}
> **歌手**: [TODO: 填写歌手名]
> **来源**: [TODO: 填写番剧名] [OP/ED/Insert Song]
> **制作日期**: {today}
> **参考模板**: [TODO: 填写参考文件路径]
> **构建脚本**: [TODO: 填写脚本文件名]

---

## 设计思路

### 番剧与歌曲分析
- 番剧风格：[TODO]
- 歌曲情感：[TODO]
- OP/ED 画面特征：[TODO]

### 设计流派选择
- 采用的流派：[TODO: STAFF流/LOGO流/歌词含义流/混合...]
- 选择理由：[TODO]

### 参考来源
- [TODO: 列出参考文件及使用的效果]

---

## 制作流程

### 1. 输入文件

"""

    if stats_input["total_lines"] > 0:
        template += f"""- **K帧歌词**: `k帧.ass`
  - 总行数: {stats_input['total_lines']}
  - Karaoke 行: {stats_input['karaoke_lines']}
  - 含注音: {'是' if stats_input['has_furigana'] else '否'}
  - 含 \\kf: {'是 (需转 \\k)' if stats_input['has_kf'] else '否'}

"""
    else:
        template += "- **K帧歌词**: [TODO: 填写输入文件信息]\n\n"

    template += """### 2. 构建脚本

**流水线**: [TODO: Aegisub Template 流 / Python 预渲染流]

[TODO: 描述输出文件结构]

### 3. 歌曲段落映射

| 时间范围 | Style | 段落 | 效果 | 歌词概要 |
|---------|-------|------|------|---------|
| [TODO] | [TODO] | Intro | [TODO] | [TODO] |
| [TODO] | [TODO] | Verse | [TODO] | [TODO] |
| [TODO] | [TODO] | Chorus | [TODO] | [TODO] |
| [TODO] | [TODO] | ... | [TODO] | [TODO] |

### 4. 最终输出

"""

    if stats_kfx["total_lines"] > 0:
        template += f"""{stats_kfx['total_lines']} 行, {stats_kfx['file_size_kb']:.1f} KB
- Dialogue 行: {stats_kfx['dialogues']}
- FX 行: {stats_kfx['fx_lines']}
- 样式数: {len(stats_kfx['styles'])}
- 分辨率: {stats_kfx['playres'] or '[未知]'}

"""
    else:
        template += "[TODO: 填写输出统计]\n\n"

    template += """---

## 遇到的问题与解决方案

### 问题 1: [TODO]

**现象**: [TODO]

**根因**: [TODO]

**修复方案**: [TODO]

---

## 注音统计

- 总映射: [TODO] 个
- 新增映射: [TODO] 个
- 上下文覆盖: [TODO] 组

---

## 文件清单

| 文件 | 说明 |
|------|------|
| [TODO] | 构建脚本 |
| `k帧.ass` | 输入 K 帧歌词 |
| `成品_KFX.ass` | 最终输出成品 |

---

## 经验教训

### ⭐ 可迁移的通用经验
1. [TODO]
2. [TODO]

### 本歌曲特有的注意事项
1. [TODO]
"""

    return template


def main():
    parser = argparse.ArgumentParser(description="案例记录工具 — 创建 KFX 制作案例目录")
    parser.add_argument("song_name", help="歌曲名（作为目录名）")
    parser.add_argument("--song-file", help="K帧歌词文件路径（将复制到案例目录）")
    parser.add_argument("--kfx-file", help="成品 KFX 文件路径（将复制到案例目录）")
    parser.add_argument("--build-script", help="构建脚本路径（将复制到案例目录）")
    parser.add_argument("--project-root", help="项目根目录（默认自动检测）")

    args = parser.parse_args()

    # 确定项目根目录
    if args.project_root:
        root = Path(args.project_root)
    else:
        root = find_project_root()

    case_dir = root / "reference" / "案例" / args.song_name
    case_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 案例目录: {case_dir}")

    # 复制文件
    stats_input = {"total_lines": 0, "karaoke_lines": 0, "has_furigana": False, "has_kf": False}
    stats_kfx = {"total_lines": 0, "dialogues": 0, "fx_lines": 0, "styles": [], "file_size_kb": 0, "playres": ""}

    if args.song_file:
        src = Path(args.song_file)
        if src.exists():
            dst = case_dir / "k帧.ass"
            shutil.copy2(src, dst)
            print(f"   ✅ 复制 K帧歌词 → {dst.name}")
            stats_input = analyze_ass_file(dst)
        else:
            print(f"   ⚠️ K帧文件不存在: {src}")

    if args.kfx_file:
        src = Path(args.kfx_file)
        if src.exists():
            dst = case_dir / "成品_KFX.ass"
            shutil.copy2(src, dst)
            print(f"   ✅ 复制成品 KFX → {dst.name}")
            stats_kfx = analyze_ass_file(dst)
        else:
            print(f"   ⚠️ KFX 文件不存在: {src}")

    if args.build_script:
        src = Path(args.build_script)
        if src.exists():
            dst = case_dir / src.name
            shutil.copy2(src, dst)
            print(f"   ✅ 复制构建脚本 → {dst.name}")
        else:
            print(f"   ⚠️ 构建脚本不存在: {src}")

    # 生成制作记录模板
    record_path = case_dir / "制作记录.md"
    if record_path.exists():
        print(f"   ℹ️ 制作记录已存在，跳过生成: {record_path.name}")
    else:
        content = generate_record_template(args.song_name, stats_kfx, stats_input)
        record_path.write_text(content, encoding="utf-8")
        print(f"   ✅ 生成制作记录模板 → {record_path.name}")

    print()
    print(f"🎉 案例目录创建完成!")
    print(f"   请编辑 {record_path} 填写 [TODO] 部分")


if __name__ == "__main__":
    main()
