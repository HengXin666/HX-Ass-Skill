# ASS 动态歌词特效制作 Skill (Aegisub KFX)

> 在已有 K 帧(`\k` / `\kf` 时间轴)的 ASS 歌词基础上, 使用 **Aegisub Karaoke Templater** 制作高品质动态卡拉 OK 特效。
> 面向日语番剧 OP / ED / 角色曲场景, 兼顾歌曲节奏、高潮段落、番剧氛围。

---

## 适用场景

- 用户已有带 `\k` / `\kf` 标签的 ASS 歌词文件(K 帧已打好, 可由 LDDC 等工具生成)
- 可能包含多轨歌词: 日语 (orig)、中文翻译 (ts)、罗马音 (roma)
- 需要添加动态视觉特效: 淡入淡出、逐字高亮、粒子、装饰、注音等
- 歌曲类型: 日语番剧 OP / ED / 角色曲 / Insert Song
- 需要特效匹配歌曲情绪(安静段、副歌段、过渡段)

---

## 核心原则(必须遵守)

### ⚠️ 只使用 Aegisub, 禁止 Python 生成

**所有特效必须通过 Aegisub Karaoke Templater 实现**。不使用 Python / PyonFX 直接生成 fx 行。

正确的工作方式:
1. 准备好 Aegisub 模板文件(含 `code`/`template` 行 + `karaoke` 源行)
2. 在 Aegisub 中打开文件 → 自动化 → 卡拉OK模板 执行
3. Templater 自动将 `karaoke` 源行展开为数千条 `fx` 行

### ⚠️ 参考文件是核心资产

本项目有两大核心资源:

1. **`reference/music-ass/`** — 完整 KFX 参考作品(天使の3P、Charlotte、点兔等), 包含经过精心调校的模板代码
2. **`reference/Seekladoom-ASS-Effect-master/`** — Seekladoom 特效合集(价值 10.22w 美刀), 包含 86 首 K 值字幕、设计方法论、量产模板、高级特效
3. **`doc/`** — 从 Seekladoom 合集中提炼的**素材库 + 设计方法论 + 技术手册**(见下文「素材库与设计方法论」节)

不要从零开始写模板——优先查阅 `doc/素材库/` 中已分类的模板, 再查 `reference/` 中的完整作品复用 `code once` / `code line` / `code syl` / `template` 行。

---

## 制作流水线 (Pipeline)

### 概述

整个制作分为两步:

```
步骤 1: build_kfx.ps1 → 组装模板 ASS 文件
         (参考文件 + 输入歌词 + 注音 → KFX.ass)

步骤 2: Aegisub Apply → 生成 FX
         (打开 KFX.ass → 自动化 → 卡拉OK模板 → 数千行 fx 输出)
```

### 步骤 1: 组装模板 ASS 文件 (`build_kfx.ps1`)

PowerShell 脚本将以下内容合并为一个 Aegisub 模板文件:

```
[Script Info]        ← 从参考文件取(PlayResX, PlayResY, Title 等)
[V4+ Styles]         ← 从参考文件取(OPJP, OPJP 2, OPJP 3-1/3-2, OPJP 4, OPJP 5, OPCN + 对应 -furigana 变体)
[Events]
  Comment: code once ...     ← 从参考文件取(变量定义、函数、形状)
  Comment: code line ...     ← 从参考文件取
  Comment: code syl ...      ← 从参考文件取
  Comment: template ...      ← 从参考文件取(所有 template 行原样复制)
  Comment: karaoke ...       ← 从输入文件构建(\kf→\k, 分配 Style, 添加注音)
  Dialogue: OPCN ...         ← 从输入文件取中文翻译
```

#### 关键处理:

1. **\kf → \k 转换**: LDDC 生成的 `\kf` 标签需要转为 `\k`, 否则 templater 不识别
2. **Style 分配**: 根据歌曲时间线将每行分配到正确的 Style(见下文"段落映射")
3. **注音添加**: 使用 `|<` 语法为日语汉字添加假名读音(见下文"注音系统")
4. **Comment 行**: 所有 karaoke 源行必须是 `Comment:` 而非 `Dialogue:`, Effect 字段为 `karaoke`

#### 运行方式:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File build_kfx.ps1
```

脚本自动检测参考文件和输入文件位置, 输出 `_KFX.ass` 后缀的模板文件。

### 步骤 2: Aegisub 执行模板

1. 在 Aegisub 中打开 `*_KFX.ass` 文件
2. 加载对应的视频/音频(如有)
3. 菜单: **自动化 → 卡拉OK模板** (Apply karaoke template)
4. 等待处理完成(高品质模板可能生成 5000~10000+ 行 fx)
5. 保存并预览

---

## 素材库与设计方法论 (Material Library)

> **制作 KFX 时必须首先查阅本节引用的素材库**, 按情绪和段落选择合适的效果模板。

### 总索引

`doc/README.md` — 素材库总索引, 包含按效果类型的快速查找表

### 设计方法论

`doc/设计思想/OPED歌词特效设计思路.md` — 核心方法论文档, 包含:
- **5 大设计流派**: STAFF 流、LOGO 流、道具流、人物流、歌词含义流、题材流、创意风格流、技术流
- **情绪-特效对照表**: 歌曲情绪 → 推荐特效组合（安静→clip帘幕+羽毛, 热血→碎片+齿轮, 梦幻→雪花+渐变, 感伤→雨滴+淡出）
- **段落-特效策略**: Intro/Verse/Pre-chorus/Chorus/Ending 各段应如何差异化
- **生产流程**: 分析→选型→实现→调参 的标准工作流

### 分类素材库 (`doc/素材库/`)

AI 在选择特效时, 应按以下分类查阅对应的 `.ass` 模板文件:

| 分类 | 目录 | 包含模板 | 适用情绪 |
|------|------|---------|---------|
| 基础模板 | `doc/素材库/01-基础模板/` | 量产三段式、简单淡入淡出 | 万能 |
| 卡拉 OK 换色 | `doc/素材库/02-卡拉OK换色/` | K 值换色、主边色切换 | 万能 |
| 粒子特效 | `doc/素材库/03-粒子特效/` | 雨滴、羽毛、雪花数字、glitter 闪光 | 感伤/梦幻/热血 |
| 运动特效 | `doc/素材库/04-运动特效/` | 碎片组装、齿轮旋转 | 科技/命运/燃 |
| clip 遮罩 | `doc/素材库/05-clip遮罩/` | 帘幕展开、字体分割 | 优雅/创意 |
| 颜色渐变 | `doc/素材库/06-颜色渐变/` | 逐字渐变 (`ass_color`) | 彩虹/温暖 |
| 综合大作 | `doc/素材库/07-综合大作/` | 命运石之门、天气之子等完整 KFX 索引 | 学习参考 |
| 绘图代码 | `doc/素材库/08-绘图代码/` | shape 素材库 (矩形/圆/三角/羽毛/雨滴/齿轮/棍棒) | 所有装饰 |

### 技术手册

`doc/技术手册/ASS特效标签速查.md` — 完整的 ASS 标签参考 + Karaoke Templater 语法 + retime 模式图 + K 值文件索引

### 🔄 新歌 KFX 选型流程

制作新歌 KFX 时, 按以下步骤选择特效:

1. **听歌 + 分析情绪**: 判断歌曲整体氛围和各段落情绪
2. **查阅设计方法论**: 读 `doc/设计思想/OPED歌词特效设计思路.md`, 确定设计流派
3. **查阅情绪-特效对照表**: 根据情绪找到推荐的特效组合
4. **从素材库选取模板**: 在 `doc/素材库/` 中找到对应的 `.ass` 文件, 复制模板代码
5. **参考综合大作**: 如需更复杂的效果, 查阅 `doc/素材库/07-综合大作/README.md` 中的完整作品
6. **混搭组合**: 不同段落可以混用不同素材（如 Intro 用帘幕展开, Verse 用羽毛飘散, Chorus 用碎片组装）

---

## 歌曲段落映射 (Section Mapping)

### 设计思路

一首完整的歌曲被分成多个段落, 每个段落使用不同的 Style, 从而获得不同的视觉效果:

| Style | 段落类型 | 视觉效果 | 典型效果描述 |
|-------|---------|----------|-------------|
| **OPJP** | 前奏/Intro | 清新简洁 | 羽毛粒子 + 缩放高亮 + 淡入淡出 |
| **OPJP 2** | 主歌/Verse | 音乐感强 | 音符粒子(×5) + 心跳波形 + 3D翻转lead-in |
| **OPJP 3-1** | 过渡/Pre-chorus | 双行显示(上) | MarginV=5, 高亮+lead-in+lead-out |
| **OPJP 3-2** | 过渡/Pre-chorus | 双行显示(下) | MarginV=40, 同上但位置不同 |
| **OPJP 4** | 副歌/Chorus | 最华丽 | 贝塞尔藤蔓+花朵+草+文字lead-in/highlight/lead-out |
| **OPJP 5** | 终段/Ending | 梦幻感 | 蝴蝶翅膀扇动+天使光环+羽毛3D翻滚+描边爆发 |

### 歌曲结构示例(羽ばたきのバースデイ full ver ~4:10)

```
时间范围          | Style      | 段落
0:01  - 0:24    | OPJP       | Intro
0:24  - 0:41    | OPJP 2     | Verse 1
0:41  - 1:01    | OPJP 3-1   | Pre-chorus 1 (with 3-2 for dual lines)
1:01  - 1:17    | OPJP 4     | Chorus 1
1:17  - 1:26    | OPJP 5     | End Chorus 1
1:36  - 1:58    | OPJP 2     | Verse 2
1:58  - 2:13    | OPJP 3-1   | Pre-chorus 2 (with 3-2 for dual lines)
2:13  - 2:29    | OPJP 4     | Chorus 2
2:29  - 2:38    | OPJP 5     | End Chorus 2
2:58  - 3:36    | OPJP 2     | Bridge / Verse 3
3:36  - 3:46    | OPJP 3-1   | Build-up
3:46  - 4:02    | OPJP 4     | Final Chorus
4:02  - 4:10    | OPJP 5     | Ending
```

### 双行显示(Multi-singer / 同时歌唱)

当多人同时唱不同歌词时(如 Pre-chorus 段落), 使用 **OPJP 3-1**(MarginV=5, 上方)和 **OPJP 3-2**(MarginV=40, 下方)在不同垂直位置同时显示两行歌词。

检测方式: 在 `Assign-Style` 函数中, 对特定时间段内的特定歌词内容进行字符匹配(如包含「響」或「平」的行分配给 3-2)。

```
主旋律行 → OPJP 3-1 (MarginV=5)
和声/副歌词 → OPJP 3-2 (MarginV=40)
```

---

## 注音系统 (Furigana)

### Aegisub 原生注音语法

Aegisub karaskel 支持 `|<` 语法在 karaoke 源行中内嵌注音:

```
{\k20}合|<あ{\k19}図|<い{\k23}は
```

这表示「合」的读音是「あ」, 「図」的读音是「い」。Templater 处理时会自动生成 `-furigana` 后缀的样式行来显示注音。

### 注音映射文件 (`furigana_map.txt`)

为避免 PowerShell 的编码问题(GBK/UTF-8 冲突), 注音映射存储在独立的 UTF-8 文本文件中:

```
始=はじ
合=あ
図=い
歌=う
飛=と
先=さき
見=み
...
```

格式: `漢字=ひらがな読み`, 每行一个映射。

### 上下文相关的注音

**同一个汉字在不同词语中可能有不同读音**。在 `Add-Furigana` 函数中通过检查前后文字进行覆盖:

| 汉字 | 默认读音 | 上下文 | 实际读音 | 判断条件 |
|------|---------|--------|---------|---------|
| 一 | いっ (一歩) | 一人 | ひと | 后接「人」|
| 出 | だ (踏み出す) | 出来る/出会う | で | 后接「来」或「会」|
| 来 | らい (未来) | 出来る | き | 前接「出」|
| 音 | おと (音/音が) | 音色 | ね | 后接「色」|
| 分 | わ (分かんない) | 多分 | ぶん | 前接「多」|

实现方式: 在 PowerShell 中通过 Unicode 码点比较(避免编码问题):

```powershell
if ($code -eq 0x4E00 -and $plain.Contains([string][char]0x4E00+[string][char]0x4EBA)) {
    $r = [string][char]0x3072+[string][char]0x3068  # 一人 → ひと
}
```

### 注音规则

1. 只对 CJK 汉字 (U+4E00~U+9FFF) 添加注音
2. 纯假名(ひらがな/カタカナ)不需要注音
3. **注音必须是假名(ひらがな), 绝对不能是罗马音**
4. 注音文字会继承主文字的动画效果(通过 `syl furi` 组合修饰符实现)

### ⭐ 注音特效同步(`syl furi` 组合修饰符)

**核心原则**: 注音必须和主文字的卡拉OK特效(lead-in、highlight、lead-out)完全同步。

#### ❌ 错误做法: 独立 `template furi`

```ass
template noblank multi,{...高光效果...}     ← 只处理主文字
template furi,{...静态显示...}               ← 注音只是呆呆地显示, 无同步
```

注音在整行时间内静态显示, 和主文字的逐字高亮完全不同步。

#### ✅ 正确做法: `template syl furi` 组合

```ass
template syl furi noblank multi,{...高光效果...}  ← 同时处理主文字和注音!
```

`syl furi` 组合让 kara-templater 从**同一个模板**生成两个版本:
- 一个给主文字(syl), 位置用 `$scenter`/`$smiddle`
- 一个给注音(furi), `$scenter`/`$smiddle` 自动调整为注音位置

#### 修改原则

| 模板类型 | 是否加 `furi` | 原因 |
|---------|:---:|------|
| 文字高光 (`template noblank multi`) | ✅ → `syl furi noblank multi` | 注音需要同步高亮 |
| 文字 lead-in (`template char`) | ✅ → `syl furi char` | 注音需要同步入场 |
| 文字 lead-out (`template noblank char`) | ✅ → `syl furi noblank char` | 注音需要同步退场 |
| 粒子/装饰 (`template notext`) | ❌ 不加 | 装饰效果不需要给注音也生成 |
| 矢量绘图 (`\p1`/`\p2`/`\p3`) | ❌ 不加 | 绘图模式的装饰不适用于注音 |

#### ⚠️ 注意事项

1. 如果只写 `furi`(不写 `syl`), 模板变成 **furi-only 类**, 不再处理主文字!
2. `syl furi` 是唯一允许的组合——不能写 `char furi`(应写 `syl furi char`)
3. `code syl all` 行通常不需要改为 `code syl furi all`(函数定义是全局的)

### 注音分配原则

多汉字词的注音必须按**自然音节**分割到每个汉字上:

| 词 | ✅ 正确 | ❌ 错误 |
|---|---|---|
| 世界(せかい) | 世=せ, 界=かい | 世=せか, 界=い |
| 必死(ひっし) | 必=ひっ, 死=し | 必=ひ, 死=っし |
| 一人(ひとり) | 一=ひと, 人=り | 一=ひと, 人=无注音 |

原则:
- 促音「っ」属于前字(如 必死 → 必=ひっ)
- 每个汉字都应有对应注音, 不要遗漏
- 1 个汉字可以对应多个假名(如 先=さき), 这在 Aegisub furigana 中是正常的

---

## Aegisub Karaoke Templater 系统

### 核心概念

ASS 文件的 `[Events]` 区域中, `Comment:` 行的 `Effect` 字段控制 Templater 行为:

| Effect 值 | 类型 | 作用 |
|-----------|------|------|
| `code once` | 初始化代码 | 脚本开始时执行一次, 定义全局变量/函数/形状 |
| `code line [all]` | 行级代码 | 每行执行一次, 设置行级变量 |
| `code syl [all]` | 音节级代码 | 每个音节执行一次, 设置条件判定 |
| `template noblank multi` | 音节模板 | 多高亮模式的主文字模板 |
| `template noblank` | 音节模板 | 标准音节模板 |
| `template noblank notext` | 音节装饰 | 只输出标签(粒子/装饰), 不输出文字 |
| `template char noblank` | 字符模板 | 逐字符处理(lead-in/out 效果) |
| `template syl noblank loop N` | 循环模板 | 每音节循环 N 次(粒子效果) |
| `template notext noblank fxgroup X` | 条件装饰 | 仅在 fxgroup 条件满足时执行 |
| `karaoke` | 源数据 | karaoke 源行, 被 Templater 读取并处理 |

### 修饰符说明

| 修饰符 | 作用 |
|--------|------|
| `noblank` | 跳过空白音节 |
| `notext` | 不输出文本, 仅标签(用于形状/粒子/装饰) |
| `multi` | 多高亮模式: 重复匹配行中所有样式 |
| `char` | 逐字符处理(不是逐音节) |
| `loop N` | 循环 N 次 |
| `all` | 匹配所有 style 的源行(默认只匹配同名 style) |
| `fxgroup X` | 条件执行: 仅当 `fxgroup.X` 为 true 时生效 |
| `keeptags` | 保留源行中的非 `\k` 标签 |

### 内联变量

在模板 Text 中可用 `$varname` 引用内置变量:

| 变量 | 说明 |
|------|------|
| `$center`, `$middle` | 字符中心坐标 |
| `$scenter`, `$smiddle` | 音节中心坐标 |
| `$lcenter`, `$lmiddle` | 行中心坐标 |
| `$lleft`, `$lright` | 行左右边界 |
| `$ltop`, `$lbottom` | 行上下边界 |
| `$sstart`, `$send`, `$sdur` | 音节起止时间(ms, 相对行起始) |
| `$lstart`, `$lend`, `$ldur` | 行起止时间 |
| `$si`, `$syln` | 音节索引 / 音节总数 |
| `$j`, `$maxj` | 循环索引 / 循环总数 |
| `$dur` | 字符持续时间 |
| `$swidth`, `$lwidth` | 音节/行宽度 |

### Lua 内联代码

用 `!expr!` 在模板中嵌入 Lua 表达式:

```
!retime("syl", 0, 0)!           -- 重置时间为音节范围
!math.random(-20, 20)!           -- 随机数
!syl.i * 50!                     -- 音节索引计算
!line.styleref.margin_v!         -- 访问样式属性
```

### 关键内置函数

| 函数 | 说明 |
|------|------|
| `retime(mode, start, end)` | 重设行时间 |
| `relayer(n)` | 设置图层 |
| `restyle(name)` | 切换样式 |
| `maxloop(n)` | 动态设置循环次数 |
| `fxgroup.name = bool` | 设置 fxgroup 条件 |

#### `retime()` 模式速查

| 模式 | 效果 |
|------|------|
| `"syl", 0, 0` | 精确的音节时间范围 |
| `"start2syl", -N, 0` | 从行开始到音节开始(lead-in) |
| `"syl2end", 0, 0` | 从音节开始到行结束(sustain) |
| `"presyl", N, M` | 音节前 N ms 到音节前 M ms |
| `"line", N, M` | 行开始+N 到行结束+M |
| `"set", abs_start, abs_end` | 绝对时间 |

---

## 参考文件模板详解

### 天使の3P「羽ばたきのバースデイ」— 黄金标准

参考文件位于 `reference/music-ass/天使の3P/` (9858行)。

#### Styles (14个)

```
OPJP, OPJP 2, OPJP 3-1, OPJP 3-2, OPJP 4, OPJP 5, OPCN
+ 对应的 7 个 -furigana 变体 (由 karaskel 自动生成使用)
```

关键样式参数:
- 字体: `FOT-PopJoy Std B`
- 主色: `&H00AF4BF0&` (粉紫)
- 边框色: `&H00FFFFFF&` (白)
- 阴影: `&H96000000&` (半透明黑)
- OPJP 3-1: MarginV=5 (上行)
- OPJP 3-2: MarginV=40 (下行)

#### 代码块结构 (lines 43-122)

**`code once`** — 全局初始化:
- `glitzerding`: 羽毛矢量形状
- `shape`: 3种音符形状 + 心跳波形
- `set`: 花朵(3尺寸)、树叶、圆形、草(4种)、蝴蝶翅膀、天使光环、装饰藤蔓(6路径)
- `hoa`/`la`/`grass1`/`grass2`/`mau`: 颜色数组
- `Vector_Move`, `Bezier`, `bernstein`, `factk`: 贝塞尔曲线运动函数

**`code line all`** — 行级计算:
- `ci = { 0 }`: 字符计数器
- `font_ratio`, `sc_ratio`: 缩放比例

**`code syl all`** — 音节级条件:
- `fxgroup.firstsyl`: 判断是否为行首音节
- `char_counter`: 字符索引递增器

#### 6 组 Style 对应的模板

**OPJP (Intro)** — 4行/音节:
1. Highlight: `\fscx130\fscy130` → `\fscx100\fscy100` + `\3c` 颜色过渡
2. Feather particle: 3D旋转 `\frx\fry\frz` + `\move` + `\p2` 形状
3. Lead-in: `\fscy130` 压缩 → 正常 + `\fad`
4. Lead-out: `\fad(0,200)` 淡出

**OPJP 2 (Verse)** — ~8行/音节:
1. Note particles (×5 loop): 3种音符形状随机选取, 向上浮动 + 缩放 + 旋转
2. Heartbeat waveform: `\clip` + `\move` 实现滚动波形
3. Highlight: `\fscx130` + `\blur`/`\bord` 变化
4. Lead-in: `\frx360` 3D翻转 + `\move` + `char_counter` 错开
5. Lead-out (per char): `\fscx100\fscy100` → 缩小消失

**OPJP 3-1/3-2 (Pre-chorus)** — 3行/音节 (×2行):
1. Highlight: 缩放 + 颜色变化
2. Lead-in: 提前出现 + 淡入
3. Lead-out: 淡出消失
- 3-1 和 3-2 使用相同模板但不同 MarginV

**OPJP 4 (Chorus)** — 最复杂:
1. Vector_Move Bezier 装饰藤蔓 (fxgroup.firstsyl): 6条曲线 × 多个控制点
2. 花朵 (hoa): `maxloop()` 动态数量, HSV 随机色
3. 草地 (grass): 4种形态, 底部生长
4. Text lead-in: 缩放 + 移动 + 颜色
5. Text highlight: 主高亮效果
6. Text lead-out: 淡出

**OPJP 5 (Ending)** — 6行/音节:
1. Butterfly right wing: `\fry` + 20段 `\t()` 交替扇动
2. Butterfly left wing: `\fry180` 镜像 + 同步扇动
3. Angel halo: 椭圆环 `\fscy50` 压扁 + 上下浮动
4. Feather 3D tumble: `\frz\fry\frx` 随机 -700~700 旋转
5. Text highlight: `\bord10` 描边爆发 + 颜色过渡
6. Text lead-in: `\move` + 颜色变化

---

## 其他参考文件经验

### Charlotte「Bravely You」(1366行)
- 多位置 JP/CN 并行显示
- 多 singer 使用不同 Style 在不同屏幕位置

### ヨスガノソラ「ツナグキズナ」(1315行)
- `\clip` 扫光效果: 底层白色 + 上层彩色, `\t(\clip(...))` 渐进显示
- 通过 `|<` 语法实现 furigana 注音
- K1/K2 多位置同时显示

### 点兔「ときめきポポロン♪」(22580行)
- 顶级 KFX: 自定义 AutoTags 函数、多重贝塞尔曲线
- 钟表/兔子/茶杯主题形状
- 角色特定颜色 (line.actor)
- multiloop 大量粒子
- 代表了最高品质水平

### Made In Abyss OP (11000+行)
- `\clip` 四象限拼合效果: 每字符分4块分别移入
- 数字故障效果

### 命运石之门「ファティマ」
- 齿轮装饰矢量
- 四象限 clip 拼装
- 数字干扰效果

---

## 共通经验法则

1. **多 Layer 叠加**是创造视觉深度的关键(发光 + 文字 + 粒子 + 装饰 = 4~8层/音节)
2. **自定义矢量形状** (`\p` 绘图模式) 大幅提升丰富度, 每首歌应有 10+ 种形状
3. **段落完全差异化**: 不同段落用不同 Style、不同层数、不同装饰、不同颜色方案
4. **fxgroup 条件判定**是段落差异的核心(在 `code syl` 中设条件)
5. **双行 = 两句连续歌词同时可见**(3-1 和 3-2), 不是日语+中文上下排列
6. **假名注音必须用ひらがな**, 通过 `|<` 语法嵌入 karaoke 源行
7. 高品质 KFX 通常 **5000~10000+** 行 fx 输出
8. 蝴蝶翅膀扇动: 20+ 段 `\t()` 交替 `\fry` 值
9. 副歌装饰物(花/草/藤蔓)要**大量堆叠**
10. **复用参考文件的模板代码**, 不要从零写模板

---

## PowerShell 编码注意事项

Windows PowerShell 处理日语文件时的关键问题和解决方案:

### 1. 日语字符串不要写在 .ps1 中

PowerShell 脚本文件经过 GBK/UTF-8 编码转换后, 日语字符会被损坏(garbled)。

**解决方案**: 将所有日语映射存储在独立的 UTF-8 文本文件中, 运行时用 `[System.IO.File]::ReadAllLines($path, $utf8)` 读取。

### 2. 文件路径中含日语

`$path = "C:\...\天使の3P\羽ばたき..."` 这类路径字符串也会被 GBK 损坏。

**解决方案**: 使用 `Get-ChildItem` + `Where-Object` 通过模糊匹配找到文件:
```powershell
$allAss = Get-ChildItem -LiteralPath $dir -Filter "*.ass" -Recurse
$refFile = $allAss | Where-Object { $_.DirectoryName -match "3P" } | Select-Object -First 1
```

### 3. Unicode 字符比较

不要直接在脚本中写日语字符做比较, 使用 `[char]0xXXXX` 码点:
```powershell
$h97FF = [char]0x97FF  # 響
if ($stripped.Contains($h97FF)) { ... }
```

### 4. BOM 编码输出

ASS 文件需要 UTF-8 BOM 编码, 使用:
```powershell
$utf8Bom = New-Object System.Text.UTF8Encoding $true
[System.IO.File]::WriteAllLines($outputFile, $lines, $utf8Bom)
```

### 5. Join-Path 版本兼容

PowerShell v5 的 `Join-Path` 只支持 2 个参数, 不能写 `Join-Path $a $b $c`:
```powershell
# 错误 (v5):
$path = Join-Path $scriptDir "reference" "music-ass"
# 正确:
$path = Join-Path (Join-Path $scriptDir "reference") "music-ass"
```

---

## ASS 特效标签速查

### 文本样式

| 标签 | 说明 | 示例 |
|------|------|------|
| `\fn<name>` | 字体 | `{\fnFOT-PopJoy Std B}` |
| `\fs<size>` | 字号 | `{\fs48}` |
| `\fsp<px>` | 字间距 | `{\fsp5}` |
| `\fscx<n>` / `\fscy<n>` | 水平/垂直缩放% | `{\fscx120\fscy80}` |

### 颜色 (格式: `&HBBGGRR&`)

| 标签 | 说明 |
|------|------|
| `\1c` | 主色(文字填充) |
| `\2c` | 次要色(卡拉OK) |
| `\3c` | 边框色 |
| `\4c` | 阴影色 |
| `\alpha` / `\1a~\4a` | 透明度 (00=不透明, FF=全透明) |

### 边框/阴影/模糊

| 标签 | 说明 |
|------|------|
| `\bord<n>` | 边框大小 |
| `\shad<n>` | 阴影距离 |
| `\blur<n>` | 高斯模糊 |

### 位置/移动

| 标签 | 说明 |
|------|------|
| `\an<1-9>` | 对齐 (5=正中, 2=中下) |
| `\pos(x,y)` | 固定位置 |
| `\move(x1,y1,x2,y2[,t1,t2])` | 移动动画 |
| `\org(x,y)` | 旋转原点 |

### 旋转/变形

| 标签 | 说明 |
|------|------|
| `\frz<deg>` | Z轴旋转 |
| `\frx<deg>` | X轴旋转(前后翻转) |
| `\fry<deg>` | Y轴旋转(左右翻转) |

### 动画

| 标签 | 说明 |
|------|------|
| `\fad(in, out)` | 淡入淡出 |
| `\t(tags)` | 标签动画 |
| `\t(t1, t2, tags)` | 定时动画 |
| `\t(t1, t2, accel, tags)` | 加速动画 |
| `\clip(x1,y1,x2,y2)` | 矩形裁剪 |
| `\k<n>` / `\kf<n>` | 卡拉OK标签 |
| `\p<n>` | 绘图模式 |

### `\t()` 可动画标签

`\fs` `\fsp` `\fscx` `\fscy` `\1c` `\2c` `\3c` `\4c` `\alpha` `\1a~\4a` `\bord` `\shad` `\blur` `\frz` `\frx` `\fry` `\clip()`

---

## 自定义矢量形状库

### 羽毛 (glitzerding)
```
m 26 37 l 38 27 l 45 19 l 52 11 l 57 7 b 66 0 72 9 64 29 l 59 26 l 62 31
b 58 36 52 43 46 47 l 41 44 l 44 48 b 41 52 37 56 33 58 l 28 52 l 30 58
l 27 61 l 24 58 l 24 61 l 21 58 l 17 61 l 17 59 b 11 62 6 64 0 64 l 0 60
b 5 60 12 57 16 54 l 14 51 l 18 51 l 17 47 l 20 50 l 20 42 l 24 38 l 25 45
```

### 音符 (3种)
```
# 双八分音符
m 0 0 l 0 7 b 0 7 0 6 -1 7 b -1 7 -3 8 -2 9 b -2 9 -1 10 0 9 b 0 9 1 8 1 8
b 1 8 1 7 1 7 l 1 1 l 7 0 l 7 6 b 7 6 6 5 5 6 b 5 6 3 7 4 8 b 4 8 5 9 6 8
b 6 8 8 8 8 7 b 8 6 8 6 8 6 l 8 -1

# 四分音符
m 0 0 l 0 9 b 0 9 -1 8 -3 9 b -3 9 -5 10 -4 12 b -4 12 -3 13 -1 12
b -1 12 1 11 1 10 b 1 10 1 9 1 9 l 1 -1

# 附点音符
m 0 0 l 0 9 b 0 9 -1 8 -3 9 b -3 9 -5 10 -4 12 b -4 12 -3 13 -1 12
b -1 12 1 11 1 10 b 1 10 1 9 1 9 l 1 1 b 2 2 3 2 2 6 b 5 2 2 1 1 0
```

### 花朵 (3尺寸)
```
# 大
m 21 21 b 6 -7 46 -7 29 21 b 49 -2 63 34 30 28 b 63 44 31 65 25 32
b 26 65 -12 45 21 29 b -13 38 0 -5 21 21 m 25 22 b 21 22 21 28 25 28
b 29 28 29 22 25 22

# 中
m 13 12 b 4 -4 28 -4 18 12 b 30 -1 38 20 18 17 b 38 26 19 39 15 19
b 16 39 -7 27 13 17 b -8 23 0 -3 13 12 m 15 13 b 13 13 13 17 15 17
b 18 17 18 13 15 13

# 小
m 8 7 b 2 -2 17 -2 11 7 b 18 -1 23 11 11 9 b 23 14 11 21 9 10
b 9 21 -4 15 8 9 b -5 13 0 -2 8 7 m 9 7 b 8 7 8 9 9 9 b 11 9 11 7 9 7
```

### 蝴蝶翅膀 + 天使光环
```
# 蝴蝶翅膀 (右翼, 左翼用 \fry180 镜像)
m 17 33 b 12 41 6 26 15 24 b 29 25 26 50 15 49 b 9 51 -4 41 2 22
b 11 3 28 -2 45 0 b 58 3 40 24 31 25 b 52 32 39 42 30 36 b 36 47 31 47 25 40
l 25 40 b 26 32 24 22 14 23 b 3 26 11 43 18 35

# 天使光环 (椭圆环, \fscy50 压扁)
m 0 25 b 1 10 50 11 50 25 b 51 40 -1 40 0 25 m 2 23 b -5 38 49 39 49 25
b 50 14 6 11 2 23
```

### 草地 (4种)
```
m 0 0 b 8 -10 15 -4 21 -3 b 34 -2 32 -9 30 -11 b 25 -14 20 -6 27 -7
m 0 0 b 8 -10 15 -4 21 -2 b 24 0 28 5 31 5 b 36 7 40 6 43 5 ...
```

使用方式: `{\p1}` / `{\p2}` / `{\p3}` + 形状字符串, 配合 `\fscx` `\fscy` `\frz` `\move`。

---

## 参考资源

- **素材库总索引**: `doc/README.md`
- **设计方法论**: `doc/设计思想/OPED歌词特效设计思路.md`
- **分类模板**: `doc/素材库/` (8 大分类, 15+ 个 .ass 模板)
- **技术手册**: `doc/技术手册/ASS特效标签速查.md`
- **Seekladoom 原始合集**: `reference/Seekladoom-ASS-Effect-master/` (314 文件, 86 首 K 值字幕)
- **Aegisub Karaoke Templater**: https://aegisub.org/docs/latest/automation/karaoke_templater/
- **ASS 标签参考**: https://www.nikse.dk/subtitleedit/formats/assa-override-tags
- **481 特效模板合集**: https://github.com/Seekladoom/Aegisub-Karaoke-Effect-481-Templates
- **ASS 标签笔记**: https://note.tonycrane.cc/others/subs/ass/
- **Aegisub 自动化笔记**: https://note.tonycrane.cc/others/subs/aegisub/automation/
