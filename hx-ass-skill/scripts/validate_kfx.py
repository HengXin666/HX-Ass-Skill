#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KFX 验证工具 — 检查 ASS 文件的 KFX 模板/输出正确性

用法:
    python -X utf8 validate_kfx.py <ass_file> [--mode template|fx]

模式:
    template  — 验证 Aegisub Templater 模板文件（执行前状态）
    fx        — 验证最终 fx 输出文件

检查项:
    1. 文件编码（UTF-8 BOM）
    2. Script Info 完整性
    3. Styles 定义（包含 -furigana 变体、Default 样式）
    4. Events 结构
    5. \\kf → \\k 转换检查
    6. 注音 |< 语法检查
    7. syl furi 修饰符检查
    8. 时间戳格式
    9. 行数统计
"""

import sys
import re
import os
from pathlib import Path
from collections import Counter


class KFXValidator:
    def __init__(self, filepath: str, mode: str = "auto"):
        self.filepath = Path(filepath)
        self.mode = mode
        self.lines: list[str] = []
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []
        self.stats: dict = {}

    def error(self, msg: str):
        self.errors.append(f"❌ {msg}")

    def warn(self, msg: str):
        self.warnings.append(f"⚠️ {msg}")

    def ok(self, msg: str):
        self.info.append(f"✅ {msg}")

    def load(self) -> bool:
        """加载文件并检查编码"""
        if not self.filepath.exists():
            self.error(f"文件不存在: {self.filepath}")
            return False

        # 检查 BOM
        raw = self.filepath.read_bytes()
        if raw[:3] == b'\xef\xbb\xbf':
            self.ok("UTF-8 BOM 编码 ✓")
            content = raw[3:].decode('utf-8')
        elif raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
            self.warn("文件是 UTF-16 编码，建议转为 UTF-8 BOM")
            content = raw.decode('utf-16')
        else:
            self.warn("文件无 BOM 标记（ASS 推荐 UTF-8 BOM）")
            content = raw.decode('utf-8', errors='replace')

        self.lines = content.splitlines()
        self.info.append(f"📄 文件: {self.filepath.name} ({len(self.lines)} 行, {len(raw)/1024:.1f} KB)")

        # 自动检测模式
        if self.mode == "auto":
            has_karaoke = any("karaoke" in line for line in self.lines if line.startswith("Comment:"))
            has_template = any("template" in line for line in self.lines if line.startswith("Comment:"))
            has_fx = any(",fx," in line for line in self.lines if line.startswith("Dialogue:"))

            if has_template and has_karaoke:
                self.mode = "template"
                self.ok("自动检测模式: template（含 code/template/karaoke 行）")
            elif has_fx:
                self.mode = "fx"
                self.ok("自动检测模式: fx（含 fx Dialogue 行）")
            else:
                self.mode = "template"
                self.warn("无法自动检测模式，默认为 template")

        return True

    def check_script_info(self):
        """检查 Script Info 区域"""
        in_section = False
        has_playresx = False
        has_playresy = False
        has_title = False

        for line in self.lines:
            if line.strip() == "[Script Info]":
                in_section = True
                continue
            if in_section and line.startswith("["):
                break
            if in_section:
                if line.startswith("PlayResX:"):
                    has_playresx = True
                    val = line.split(":", 1)[1].strip()
                    self.info.append(f"   PlayResX: {val}")
                elif line.startswith("PlayResY:"):
                    has_playresy = True
                    val = line.split(":", 1)[1].strip()
                    self.info.append(f"   PlayResY: {val}")
                elif line.startswith("Title:"):
                    has_title = True

        if has_playresx and has_playresy:
            self.ok("Script Info: PlayResX/Y 已定义")
        else:
            self.error("Script Info: 缺少 PlayResX 或 PlayResY")

    def check_styles(self):
        """检查样式定义"""
        styles = []
        for line in self.lines:
            if line.startswith("Style:"):
                name = line.split(",")[0].replace("Style:", "").strip()
                styles.append(name)

        self.stats["styles"] = len(styles)
        self.info.append(f"🎨 样式数量: {len(styles)}")

        # 检查 Default 样式
        if "Default" in styles:
            self.ok("Default 样式已定义")
        else:
            # 检查是否有引用 Default 的行
            has_default_ref = any(",Default," in line for line in self.lines
                                 if line.startswith("Dialogue:") or line.startswith("Comment:"))
            if has_default_ref:
                self.warn("有行引用 Default 样式，但样式表中未定义（可能导致警告）")

        # 检查 furigana 变体
        base_styles = [s for s in styles if not s.endswith("-furigana")]
        furi_styles = [s for s in styles if s.endswith("-furigana")]
        jp_styles = [s for s in base_styles if "JP" in s.upper() or "OP" in s.upper()]

        if furi_styles:
            self.ok(f"Furigana 样式变体: {len(furi_styles)} 个")
        elif jp_styles:
            self.warn("日语样式存在但无 -furigana 变体（注音可能不显示）")

        # 列出所有样式
        if styles:
            self.info.append(f"   样式列表: {', '.join(styles[:20])}" +
                           (f" ... (+{len(styles)-20})" if len(styles) > 20 else ""))

    def check_events(self):
        """检查 Events 区域"""
        comments = []
        dialogues = []

        for line in self.lines:
            if line.startswith("Comment:"):
                comments.append(line)
            elif line.startswith("Dialogue:"):
                dialogues.append(line)

        self.stats["comments"] = len(comments)
        self.stats["dialogues"] = len(dialogues)

        # 统计 Effect 字段类型
        effect_counter = Counter()
        for line in comments:
            parts = line.split(",", 9)
            if len(parts) >= 10:
                effect = parts[3].strip()
                effect_counter[effect] += 1

        for line in dialogues:
            parts = line.split(",", 9)
            if len(parts) >= 10:
                effect = parts[3].strip()
                if effect:
                    effect_counter[effect] += 1

        self.info.append(f"📊 Comment 行: {len(comments)}, Dialogue 行: {len(dialogues)}")
        if effect_counter:
            self.info.append("   Effect 分布:")
            for effect, count in sorted(effect_counter.items(), key=lambda x: -x[1]):
                self.info.append(f"     {effect}: {count}")

        if self.mode == "template":
            self._check_template_events(comments, dialogues, effect_counter)
        else:
            self._check_fx_events(comments, dialogues, effect_counter)

    def _check_template_events(self, comments, dialogues, effect_counter):
        """模板模式的事件检查"""
        # 必须有 karaoke 源行
        karaoke_count = effect_counter.get("karaoke", 0)
        if karaoke_count > 0:
            self.ok(f"Karaoke 源行: {karaoke_count} 行")
        else:
            self.error("没有找到 karaoke 源行（Effect=karaoke 的 Comment 行）")

        # 必须有 template 行
        template_count = sum(v for k, v in effect_counter.items() if "template" in k)
        if template_count > 0:
            self.ok(f"Template 行: {template_count} 行")
        else:
            self.error("没有找到 template 行")

        # code once 检查
        code_once = sum(v for k, v in effect_counter.items() if "code once" in k)
        if code_once > 0:
            self.ok(f"Code once 行: {code_once} 行")
        else:
            self.warn("没有 code once 行（全局变量/函数可能缺失）")

        # 检查 \kf 残留
        kf_lines = []
        for line in comments:
            parts = line.split(",", 9)
            if len(parts) >= 10 and parts[3].strip() == "karaoke":
                text = parts[9]
                if r"\kf" in text:
                    kf_lines.append(text[:50])

        if kf_lines:
            self.error(f"发现 {len(kf_lines)} 行 karaoke 源行仍包含 \\kf 标签（应转为 \\k）")
            for sample in kf_lines[:3]:
                self.info.append(f"   示例: {sample}...")
        else:
            self.ok("所有 karaoke 源行使用 \\k 标签 ✓")

        # 检查注音 |<
        furi_lines = 0
        for line in comments:
            parts = line.split(",", 9)
            if len(parts) >= 10 and parts[3].strip() == "karaoke":
                if "|<" in parts[9]:
                    furi_lines += 1

        if furi_lines > 0:
            self.ok(f"含注音的 karaoke 行: {furi_lines} / {karaoke_count}")
        else:
            self.warn("没有找到注音标记 |<（日语歌词可能缺少假名注音）")

        # 检查 syl furi 修饰符
        self._check_syl_furi(comments)

    def _check_fx_events(self, comments, dialogues, effect_counter):
        """fx 输出模式的事件检查"""
        fx_count = effect_counter.get("fx", 0)
        if fx_count > 0:
            self.ok(f"FX 行: {fx_count} 行")
        else:
            self.warn("没有找到 fx 行（Effect=fx 的 Dialogue 行）")

        # 检查层级分布
        layer_counter = Counter()
        for line in dialogues:
            parts = line.split(",", 9)
            if len(parts) >= 10:
                try:
                    layer = int(parts[0].replace("Dialogue:", "").strip())
                    layer_counter[layer] += 1
                except ValueError:
                    pass

        if layer_counter:
            self.info.append("   Layer 分布:")
            for layer, count in sorted(layer_counter.items()):
                self.info.append(f"     Layer {layer}: {count} 行")

        # 检查 Style 分布
        style_counter = Counter()
        for line in dialogues:
            parts = line.split(",", 9)
            if len(parts) >= 10:
                style_counter[parts[3].strip()] += 1

        if style_counter:
            self.info.append("   Style 分布 (fx):")
            for style, count in sorted(style_counter.items(), key=lambda x: -x[1])[:15]:
                self.info.append(f"     {style}: {count} 行")

    def _check_syl_furi(self, comments):
        """检查 syl furi 修饰符使用"""
        template_lines = []
        for line in comments:
            parts = line.split(",", 9)
            if len(parts) >= 10:
                effect = parts[3].strip()
                if effect.startswith("template"):
                    template_lines.append(effect)

        # 分类
        text_templates = [e for e in template_lines if "notext" not in e]
        has_syl_furi = any("syl furi" in e or "syl  furi" in e for e in text_templates)
        has_standalone_furi = any(
            e.startswith("template furi") or e.startswith("template  furi")
            for e in template_lines
        )

        if has_syl_furi:
            self.ok("使用 syl furi 组合修饰符（注音特效同步 ✓）")
        elif has_standalone_furi:
            self.warn("使用独立 template furi（注音不会同步主文字特效！建议改为 syl furi）")
        elif text_templates:
            self.info.append("   ℹ️ 文字模板未包含 furi 修饰符（注音将不显示）")

    def check_timestamps(self):
        """检查时间戳格式"""
        ts_pattern = re.compile(r'\d+:\d{2}:\d{2}\.\d{2}')
        bad_ts = []

        for i, line in enumerate(self.lines):
            if line.startswith("Comment:") or line.startswith("Dialogue:"):
                parts = line.split(",", 9)
                if len(parts) >= 3:
                    start = parts[1].strip()
                    end = parts[2].strip()
                    if not ts_pattern.match(start):
                        bad_ts.append((i+1, "start", start))
                    if not ts_pattern.match(end):
                        bad_ts.append((i+1, "end", end))

        if bad_ts:
            self.warn(f"发现 {len(bad_ts)} 个格式异常的时间戳")
            for ln, field, val in bad_ts[:5]:
                self.info.append(f"   行{ln} {field}: '{val}'")
        else:
            self.ok("所有时间戳格式正确 (H:MM:SS.cc)")

    def validate(self):
        """执行所有验证"""
        if not self.load():
            return

        self.check_script_info()
        self.check_styles()
        self.check_events()
        self.check_timestamps()

    def report(self) -> str:
        """生成验证报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("KFX 验证报告")
        lines.append("=" * 60)

        # 基本信息
        for item in self.info:
            lines.append(item)

        lines.append("")

        # 错误
        if self.errors:
            lines.append(f"--- 错误 ({len(self.errors)}) ---")
            for e in self.errors:
                lines.append(e)
            lines.append("")

        # 警告
        if self.warnings:
            lines.append(f"--- 警告 ({len(self.warnings)}) ---")
            for w in self.warnings:
                lines.append(w)
            lines.append("")

        # 总结
        lines.append("=" * 60)
        if not self.errors:
            lines.append("🎉 验证通过！" + (f"（{len(self.warnings)} 个警告）" if self.warnings else ""))
        else:
            lines.append(f"💥 发现 {len(self.errors)} 个错误，{len(self.warnings)} 个警告")
        lines.append("=" * 60)

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python -X utf8 validate_kfx.py <ass_file> [--mode template|fx]")
        print()
        print("示例:")
        print("  python -X utf8 validate_kfx.py my_song_KFX.ass")
        print("  python -X utf8 validate_kfx.py output.ass --mode fx")
        sys.exit(1)

    filepath = sys.argv[1]
    mode = "auto"

    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]

    validator = KFXValidator(filepath, mode)
    validator.validate()
    print(validator.report())

    # 返回码: 0=通过, 1=有错误
    sys.exit(1 if validator.errors else 0)


if __name__ == "__main__":
    main()
