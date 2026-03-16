# 日语注音 (Furigana) 编写与特效同步教程

> 本教程基于「羽ばたきのバースデイ」KFX 制作中的实战经验, 详细讲解如何在 Aegisub Karaoke Templater 中正确实现日语注音, 并让注音和主文字的卡拉OK特效完全同步。

---

## 目录

1. [什么是 Furigana? ](#1-什么是-furigana)
2. [Aegisub 的 Furigana 语法](#2-aegisub-的-furigana-语法)
3. [Furigana 样式系统](#3-furigana-样式系统)
4. [注音映射文件的编写](#4-注音映射文件的编写)
5. [上下文相关注音](#5-上下文相关注音)
6. [⭐ 注音与主文字特效同步](#6-注音与主文字特效同步)
7. [常见错误与排查](#7-常见错误与排查)
8. [完整示例](#8-完整示例)

---

## 1. 什么是 Furigana?

Furigana(振り仮名)是日语中显示在汉字上方的小假名字符, 用于标注汉字的读音。在字幕/卡拉OK中, furigana 帮助观众正确朗读日语歌词中的汉字。

```
  さき
  先      ← 汉字「先」上方显示假名「さき」
```

在 Aegisub 的卡拉OK系统中, furigana 由 `karaskel.lua` 自动处理布局和定位。

---

## 2. Aegisub 的 Furigana 语法

### 基本语法

在 karaoke 源行中, 使用 `|<` 语法将注音附加到汉字后面:

```ass
Comment: 0,0:00:01.00,0:00:05.00,OPJP,,0,0,0,karaoke,{\k18}合|<あ{\k16}図|<い{\k27}は
```

解析结果:
- `合` 的注音 → `あ`
- `図` 的注音 → `い`
- `は` → 纯假名, 无注音

### 多假名注音

一个汉字可以对应多个假名:

```ass
{\k36}先|<さき      ← 「先」的注音是2个假名「さき」
{\k54}心|<こころ    ← 「心」的注音是3个假名「こころ」
```

### 连续汉字

连续的汉字各自独立标注注音:

```ass
{\k26}革|<かく{\k91}命|<めい    ← 「革命」= かくめい
{\k23}世|<せ{\k19}界|<かい      ← 「世界」= せかい
```

---

## 3. Furigana 样式系统

### 自动生成的 -furigana 样式

Aegisub 的 `karaskel.lua` 会自动查找带 `-furigana` 后缀的样式来渲染注音。例如:

| 主样式 | 注音样式 |
|-------|---------|
| `OPJP` | `OPJP-furigana` |
| `OPJP 2` | `OPJP 2-furigana` |
| `OPJP 4` | `OPJP 4-furigana` |
| `OPCN` | `OPCN-furigana` |

### 注音样式的关键参数

注音样式通常与主样式使用相同字体, 但字号更小:

```
主样式:   FOT-PopJoy Std B, 字号 36, 边框 3, 阴影 2.5
注音样式: FOT-PopJoy Std B, 字号 18, 边框 1.5, 阴影 1.25
```

注音样式的 `Alignment` (对齐方式) 和颜色通常与主样式保持一致。

### ⚠️ 必须预先定义注音样式

如果 ASS 文件中没有定义 `-furigana` 后缀的样式, karaskel 会回退使用主样式渲染注音, 导致注音字号和位置不正确。务必在 `[V4+ Styles]` 中为每个需要注音的样式定义对应的 `-furigana` 变体。

---

## 4. 注音映射文件的编写

### 为什么用外部文件?

在 Windows PowerShell 中直接在 `.ps1` 脚本里写日语字符串会因 GBK/UTF-8 编码冲突而损坏。因此将注音映射存储在独立的 UTF-8 文本文件中。

### 映射文件格式

`furigana_map.txt` — 每行一个映射, 格式 `漢字=ひらがな読み`:

```
合=あ
図=い
飛=と
先=さき
見=み
流=なが
音=おと
鼓=こ
動=どう
革=かく
命=めい
```

### 注音分配原则

**核心原则: 按自然音节分割到每个汉字上**

| 词 | 读音 | ✅ 正确分配 | ❌ 错误分配 |
|---|---|---|---|
| 世界 | せかい | 世=せ, 界=かい | 世=せか, 界=い |
| 必死 | ひっし | 必=ひっ, 死=し | 必=ひ, 死=っし |
| 一人 | ひとり | 一=ひと, 人=り | 一=ひとり, 人=无 |
| 出会 | であ | 出=で, 会=あ | 出=であ, 会=无 |
| 革命 | かくめい | 革=かく, 命=めい | ✓ (这个天然是对的) |

**分割规则**:

1. **促音「っ」属于前字**: 必死 → 必=ひっ, 死=し(不是 必=ひ, 死=っし)
2. **每个汉字都必须有注音**: 不要遗漏任何一个字
3. **训读词特殊处理**: 如「一人」(ひとり) 是训读, 音节分割要按习惯而非字面
4. **一字多假名完全正常**: `先=さき`, `心=こころ` 都是合理的

### 什么字需要注音?

| 字符类型 | 是否需要注音 | 示例 |
|---------|:---:|------|
| CJK 汉字 (U+4E00~U+9FFF) | ✅ | 歌、先、革、命 |
| ひらがな | ❌ | は、の、を |
| カタカナ | ❌ | キ、ミ、バ |
| 英字/数字 | ❌ | fly, high, 3 |
| 标点符号 | ❌ | ＆、?  |

---

## 5. 上下文相关注音

### 同字不同音

日语中同一个汉字在不同词语中可能有不同读音:

| 汉字 | 默认读音 | 上下文词语 | 实际读音 |
|------|---------|-----------|---------|
| 一 | いっ (一歩) | 一人 | ひと |
| 出 | だ (踏み出す) | 出来る / 出会う | で |
| 来 | らい (未来) | 出来る | き |
| 音 | おと (音が) | 音色 | ね |
| 分 | わ (分かんない) | 多分 | ぶん |

### PowerShell 中的上下文覆盖

由于编码问题, 不能直接写日语字符串比较。使用 Unicode 码点:

```powershell
# 检测「一人」→ 「一」读「ひと」
if ($code -eq 0x4E00 -and $plain.Contains([string][char]0x4E00+[string][char]0x4EBA)) {
    $r = [string][char]0x3072+[string][char]0x3068  # ひと
}

# 检测「出来」/「出会」→ 「出」读「で」
if ($code -eq 0x51FA) {
    if ($plain.Contains([string][char]0x51FA+[string][char]0x6765) -or
        $plain.Contains([string][char]0x51FA+[string][char]0x4F1A)) {
        $r = [string][char]0x3067  # で
    }
}

# 检测「音色」→ 「音」读「ね」
if ($code -eq 0x97F3 -and $plain.Contains([string][char]0x97F3+[string][char]0x8272)) {
    $r = [string][char]0x306D  # ね
}
```

---

## 6. ⭐ 注音与主文字特效同步

**这是最关键的部分。**

### 问题: 独立 `template furi` 导致不同步

如果你为注音写了一个独立的模板行:

```ass
Comment: 0,...,OPJP,,0,0,0,template furi,!retime("line")!{\an5\pos($scenter,$smiddle)}
```

注音会在**整行时间**内静态显示——没有 lead-in 淡入、没有高光效果、没有 lead-out 淡出。主文字在逐字高亮, 而注音只是呆呆地待着。**这是错误的! **

### 解决方案: `template syl furi` 组合修饰符

在**每个显示文字的模板行**上加上 `syl furi`:

```ass
# 高光模板: 主文字和注音共享同一套缩放+颜色变化效果
Comment: 1,...,OPJP,,0,0,0,template syl furi noblank multi,
    !retime("syl",0,0)!{\an5\pos($scenter,$smiddle)\fscx100\fscy100
    \t(0,200,\fscx130\fscy130)\t(200,$dur,\3c&HFFFFFF&\fscx100\fscy100)}

# Lead-in 模板: 注音和主文字同步入场
Comment: 0,...,OPJP,,0,0,0,template syl furi noblank char,
    !retime("start2syl",-100,0)!{\an5\pos($scenter,$smiddle)
    \3c&HFFFFFF&\fscy130\t(0,500,\fscy100)\fad(500,0)}

# Lead-out 模板: 注音和主文字同步退场
Comment: 1,...,OPJP,,0,0,0,template syl furi noblank char,
    !retime("syl2end",0,0)!{\an5\pos($center,$middle)\fad(0,200)}
```

### `syl furi` 的工作原理

`syl furi` 组合让 kara-templater **从同一个模板生成两个独立的输出**:

```
同一个 template syl furi noblank multi
    │
    ├── 为每个 syl (主文字音节) 执行一次 → 生成主文字 fx 行
    │   $scenter/$smiddle = 主文字的位置
    │   使用主样式 (OPJP)
    │
    └── 为每个 furi (注音音节) 执行一次 → 生成注音 fx 行
        $scenter/$smiddle = 注音的位置 (自动偏移到汉字上方)
        使用注音样式 (OPJP-furigana)
```

### 哪些模板该加 `furi`, 哪些不该?

| 模板用途 | 是否加 `furi` | 说明 |
|---------|:---:|------|
| 文字高光 (highlight) | ✅ | 注音需要同步高亮 |
| 文字入场 (lead-in) | ✅ | 注音需要同步淡入 |
| 文字退场 (lead-out) | ✅ | 注音需要同步淡出 |
| 粒子效果 (notext) | ❌ | 装饰不应给注音也生成 |
| 矢量绘图 (\p1/\p2) | ❌ | 绘图装饰不适用注音 |
| 蝴蝶翅膀/光环 | ❌ | 这些是视觉装饰 |
| 贝塞尔曲线藤蔓 | ❌ | 这些是 fxgroup 装饰 |

### ⚠️ 关键注意事项

1. **必须显式写 `syl furi`**:
   - `template noblank multi` 是隐式 syl 类
   - `template furi noblank multi` 是 **furi-only 类**(不处理主文字! )
   - `template syl furi noblank multi` 才是正确的组合

2. **`code syl all` 通常不需要改**: 函数定义是全局的, furi 模板执行时也能调用

3. **`$scenter`/`$smiddle` 自动适配**: 当模板为 furi 执行时, 这些内联变量自动使用注音的位置

4. **参考 ツナグキズナ 的实现**:
   ```ass
   # ツナグキズナ 使用 syl.isfuri 在同一模板中微调注音位置
   template syl furi fxgroup base all,!retime("line")!{
       \pos(...,!syl.isfuri and math.floor(y-syl.height*3/2) or y!)...}
   ```
   通过 `syl.isfuri` 可以在模板内部区分是处理主文字还是注音。

---

## 7. 常见错误与排查

### 错误 1: 注音不显示

**症状**: 执行模板后 fx 输出中没有注音行

**可能原因**:
- 所有 template 行都用了 `noblank`, 跳过了 furigana 音节
- 没有定义 `-furigana` 后缀样式

**解决**: 在文字模板上加 `syl furi` 组合

### 错误 2: 注音显示但不同步

**症状**: 注音在整行时间内静态显示, 不跟随逐字高亮

**原因**: 使用了独立的 `template furi` + `retime("line")`

**解决**: 删除独立 furi 模板, 改用 `syl furi` 组合

### 错误 3: 注音位置偏移

**症状**: 注音没有出现在对应汉字上方

**可能原因**:
- `-furigana` 样式的 Alignment 设置不一致
- 使用了不支持 furigana 的定位方式

**解决**: 确保注音样式和主样式的 Alignment 一致

### 错误 4: 加了 `furi` 后主文字消失

**症状**: 改了模板后主文字不显示, 只有注音

**原因**: 写成了 `template furi ...`(furi-only 类), 而不是 `template syl furi ...`

**解决**: 必须同时写 `syl` 和 `furi`

### 错误 5: 中文翻译遮挡注音

**症状**: 底部中文翻译和日语注音在垂直方向重叠

**原因**: 中文行的 Y 坐标没有考虑 furigana 的额外高度

**解决**: 将中文行的 Y 坐标上移 30~40px(如从 Y=640 调整到 Y=600)

---

## 8. 完整示例

### 8.1 ASS 样式定义

```ass
[V4+ Styles]
Style: OPJP,FOT-PopJoy Std B,36,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,...
Style: OPJP-furigana,FOT-PopJoy Std B,18,&H00AF4BF0,&H000000FF,&H00FFFFFF,&H96000000,...
```

### 8.2 Karaoke 源行(含注音)

```ass
Comment: 0,...,OPJP,,0,0,0,karaoke,{\k18}は{\k15}じ{\k15}ま{\k15}り{\k15}の{\k18}合|<あ{\k16}図|<い{\k27}は
Comment: 0,...,OPJP 2,,0,0,0,karaoke,{\k23}世|<せ{\k19}界|<かい{\k33}中|<じゅう{\k190}を
```

### 8.3 模板行(syl furi 组合)

```ass
; 高光效果 — 主文字和注音共享
Comment: 1,...,OPJP,,0,0,0,template syl furi noblank multi,
    !retime("syl",0,0)!{\an5\pos($scenter,$smiddle)
    \fscx100\fscy100\t(0,200,\fscx130\fscy130)
    \t(200,$dur,\3c&HFFFFFF&\fscx100\fscy100)}

; Lead-in — 主文字和注音同步入场
Comment: 0,...,OPJP,,0,0,0,template syl furi noblank char,
    !retime("start2syl",-100,0)!{\an5\pos($scenter,$smiddle)
    \3c&HFFFFFF&\fscy130\t(0,500,\fscy100)\fad(500,0)}

; Lead-out — 主文字和注音同步退场
Comment: 1,...,OPJP,,0,0,0,template syl furi noblank char,
    !retime("syl2end",0,0)!{\an5\pos($center,$middle)\fad(0,200)}

; 粒子效果 — 不加 furi(装饰不给注音生成)
Comment: 0,...,OPJP,,0,0,0,template noblank,
    !retime("syl",0,0)!{\an5\blur3\1c&HFFFFFF&...粒子效果...}
```

### 8.4 注音映射文件

```
# furigana_map.txt (UTF-8)
合=あ
図=い
世=せ
界=かい
必=ひっ
死=し
先=さき
心=こころ
```

---

## 参考资源

- **Aegisub Furigana 文档**: https://aegisub.org/docs/latest/furigana_karaoke/
- **Template 修饰符文档**: https://aegisub.org/docs/latest/automation/karaoke_templater/template_modifiers/
- **karaskel.lua 文档**: https://aegi.vmoe.info/docs/3.0/Automation/Lua/Modules/karaskel.lua/
- **模范参考**: `reference/music-ass/ヨスガノソラ/Team.ねこかん[猫] - ツナグキズナ.ass`(使用 `syl furi` + `syl.isfuri` 的完整实现)
