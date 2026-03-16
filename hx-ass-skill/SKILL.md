# HX ASS Skill — 番剧主题 ASS 卡拉OK特效制作

> 将 K 帧 ASS 歌词(日语 + 中文翻译 + 可选罗马音)转化为 **符合番剧主题的、高质量的、带日语注音的 ASS 卡拉OK特效歌词**。
> 输出为 Aegisub「应用卡拉OK模板」**执行前**的模板文件状态(含 code/template/karaoke 行)。

---

## 适用场景

- 用户已有带 `\k` / `\kf` 标签的 ASS 歌词文件(K 帧已打好, 可由 LDDC 等工具生成)
- 歌词可能包含多轨: 日语原文(orig)、中文翻译(ts)、罗马音(roma)
- 歌曲来源: 日语番剧 OP / ED / 角色曲 / Insert Song
- 需要添加动态视觉特效并匹配番剧风格和歌曲情绪
- 输出可被 Aegisub Karaoke Templater 直接执行生成数千行 fx

---

## 核心原则

### 1. 两条制作流水线

根据参考文件的性质选择制作方式:

| 流水线 | 适用场景 | 工具 | 输出状态 |
|--------|---------|------|---------|
| **Aegisub Template 流** | 参考文件含 code/template 行(可复用模板) | PowerShell + Aegisub | code + template + karaoke Comment 行 |
| **Python 预渲染流** | 参考文件是纯手工 fx(无可复用模板) | Python 脚本 | 直接输出所有 fx Dialogue 行 |

**优先使用 Aegisub Template 流**, 除非参考文件完全是手工制作的(如 Charlotte Bravely You)。

### 2. 参考文件是核心资产

本项目包含丰富的参考资源, **不要从零写模板**:

| 资源 | 位置 | 说明 |
|------|------|------|
| 完整 KFX 参考作品 | `reference/music-ass/` | 天使の3P、Charlotte、点兔、Made in Abyss、命运石之门、ヨスガノソラ 等 |
| Seekladoom 特效合集 | `reference/Seekladoom-ASS-Effect-master/` | 86 首 K 值字幕 + 效果模板 |
| 分类素材库 | `doc/素材库/` | 8大分类的可复用 .ass 模板(见 `references/素材库索引.md`) |
| 设计方法论 | `doc/设计思想/` | 5大设计流派 + 情感-特效对照 |
| 技术手册 | `doc/技术手册/` | ASS 标签速查 + Templater 语法 |
| 制作案例 | `reference/案例/` | 4个完整案例的制作记录(见下文「案例经验库」) |

### 3. 番剧主题决定特效风格

特效设计必须与番剧的风格、场景、情绪一致。不是随便堆砌效果, 而是**用特效讲述番剧的故事**。

### 4. 注音(Furigana)是必选项

所有日语歌词中的汉字必须添加假名注音, 使用 `|<` 语法嵌入 karaoke 源行。

---

## 制作流程(7 步)

### Step 1: 分析输入 — 了解歌曲与番剧

**输入**: 用户提供的 K 帧 ASS 歌词文件 + 番剧/歌曲信息

**操作**:

1. **解析 K 帧文件**
   - 识别歌词轨道: orig(日语)、ts(中文翻译)、roma(罗马音)
   - 统计行数、时长、K 帧标签类型(`\k` 或 `\kf`)
   - 提取每行的精确时间戳(`H:MM:SS.cc` → 毫秒)

2. **收集番剧信息**(需要网络搜索)
   - 在 **萌娘百科** 搜索番剧名 → 获取: 题材、风格、关键视觉元素、角色配色
   - 在 **https://bgm.tv/** 搜索 → 获取: 评分、标签、Staff 信息
   - 确认歌曲在番剧中的位置: OP / ED / Insert Song / 角色曲
   - 观察 OP/ED 动画画面(如有): STAFF 字幕风格、LOGO 设计、标志性道具

3. **分析歌曲情绪**
   - 通读歌词(日语 + 中文翻译)
   - 判断整体情感基调: 温暖治愈 / 热血激燃 / 抒情感伤 / 欢快可爱 / 科幻悬疑 / 庄严史诗 / 神秘诡异
   - 标注各段落的情绪变化

**输出**: 番剧信息摘要 + 歌曲情绪分析 + K 帧统计

---

### Step 2: 设计规划 — 选择特效风格

**输入**: Step 1 的分析结果

**操作**:

1. **选择设计流派**(参考 `references/设计方法论.md`)
   - 从 OPED 画面能直接观察到的: STAFF 流、LOGO 流、道具流、人物流
   - 需要挖掘的: 歌词含义流、题材流、创意风格流、技术流
   - 可混合使用多个流派

2. **确定情感-特效组合**

   | 情感 | 推荐主效果 | 推荐辅助效果 | 素材库来源 |
   |------|-----------|-------------|-----------|
   | 温暖治愈 | clip 帘幕展开 | 羽毛飘散 | 05-clip遮罩 + 03-粒子特效 |
   | 热血激燃 | glitter 闪光 | 三角碎片爆发 | 03-粒子特效 |
   | 抒情感伤 | 雨滴下落 | 光晕圆点 | 03-粒子特效 |
   | 欢快可爱 | 逐字弹跳 | 星星/音符/爱心 | 01-基础模板 + 03-粒子特效 |
   | 科幻悬疑 | 碎片组装 | 齿轮旋转 | 04-运动特效 |
   | 庄严史诗 | clip 横向扫描 | 数字雪花 | 05-clip遮罩 + 03-粒子特效 |
   | 神秘诡异 | iclip 字体分割 | 随机抖动 | 05-clip遮罩 |

3. **划分歌曲段落** — 为每行分配 Style

   ```
   Intro (前奏/引入)  → 最简单、安静 → 建立基调
   Verse (主歌)       → 中等复杂度 → 推进叙事
   Pre-chorus (副歌前) → 开始升温 → 蓄势待发
   Chorus (副歌)      → 最复杂、华丽 → 情感高潮
   Bridge (桥段)      → 变化 → 打破重复
   Coda (尾奏)        → 回归平静 → 余韵悠长
   ```

   **具体操作**: 提取源文件每行的毫秒时间戳 → 根据歌词内容和情绪划分段落 → 建立 `Assign-Style` 时间阈值表

   ⚠️ **时间戳必须从源文件提取**, 不要手动心算 `分:秒` → 毫秒转换(案例经验: 曾因心算错误经历 3 轮修正)

4. **选择参考模板**

   从 `reference/music-ass/` 和 `doc/素材库/` 中选择最匹配的参考文件:
   - **同一动画**: 优先复用(如天使の3P 两首歌复用同一模板)
   - **同情绪**: 在不同动画的参考中找风格匹配的(如抒情 → Made in Abyss clip 效果)
   - **混合来源**: 可从多个参考中各取所长(案例: 大切がきこえる = MIA clip + S;G 碎片)

5. **确定颜色方案**

   - 颜色格式: `&HBBGGRR&`(ASS 使用 **BGR** 顺序, 不是 RGB! )
   - 来源优先级: 角色应援色 > LOGO 配色 > OPED 画面提取 > 情绪通用色
   - 每个段落可以有不同的颜色变化
   - 参考 `references/色彩预设.md` 中的预设方案

**输出**: 完整的设计规划文档(流派 + 特效组合 + 段落映射 + 颜色方案 + 参考来源)

---

### Step 3: 构建注音 — 日语汉字假名标注

**输入**: K 帧歌词的日语行

**操作**:

1. **加载注音映射** — 读取 `furigana_map.txt`(项目根目录, 全歌共享)
   - 格式: `漢字=ひらがな読み`, 每行一个映射
   - 当前 218+ 条映射

2. **扫描日语行**中的 CJK 汉字(U+4E00 ~ U+9FFF)

3. **应用上下文覆盖** — 同一汉字在不同词语中可能有不同读音

   常见覆盖规则(已积累):

   | 汉字 | 默认 | 上下文 | 覆盖后 | 判断 |
   |------|------|--------|--------|------|
   | 一 | いっ | 一人 | ひと | 后接「人」 |
   | 出 | だ | 出来/出会/出口 | で | 后接「来」「会」「口」 |
   | 分 | わ | 自分/多分 | ぶん | 前接「自」「多」 |
   | 笑 | わら | 笑顔 | え | 后接「顔」 |
   | 日 | ひ | 今日 → う / 日常 → にち / 明日 → た | 多义 | 根据前后文 |
   | 音 | おと | 鐘の音 → ね / 音色 → ね | ね | 后接特定字 |

4. **添加 `|<` 语法**: 将 `{\k20}合` 转为 `{\k20}合|<あ`

5. **注音分配原则**
   - 多汉字词按**自然音节**分割到每个汉字上
   - 促音「っ」属于前字(如 必死 → 必=ひっ, 死=し)
   - 每个汉字都必须有对应注音, 不要遗漏
   - 1 个汉字可对应多个假名(如 蹲=うずくま)
   - ⚠️ **注音必须是假名(ひらがな), 绝对不能是罗马音**

6. **如遇到新汉字**(不在 furigana_map.txt 中)
   - 查询该汉字在歌词上下文中的正确读音
   - 添加到 `furigana_map.txt`
   - 检查是否需要上下文覆盖规则

**输出**: 所有日语行均已嵌入 `|<` 注音标记

---

### Step 4: 组装模板文件 — 构建 KFX

根据 Step 2 选择的流水线, 执行对应的组装流程:

#### 方式 A: Aegisub Template 流(推荐)

创建 `build_kfx_{song}.ps1` 脚本, 将以下内容合并为一个 ASS 文件:

```
[Script Info]        ← 从参考文件取(PlayResX, PlayResY, Title 等)
[V4+ Styles]         ← 从参考文件取 + 补充 Default 样式 + -furigana 变体
[Events]
  Comment: code once ...     ← 参考文件(变量、函数、矢量形状定义)
  Comment: code line ...     ← 参考文件(行级计算)
  Comment: code syl ...      ← 参考文件(音节级条件判定)
  Comment: template ...      ← 参考文件(所有效果模板行)
  Comment: karaoke ...       ← 从输入歌词构建(\kf→\k, 分配 Style, 嵌入注音)
  Dialogue: OPCN ...         ← 中文翻译行(\fad(300,300) 淡入淡出)
```

**关键处理**:

| 处理项 | 说明 |
|--------|------|
| `\kf` → `\k` | LDDC 生成的 `\kf` 标签必须转为 `\k`, Aegisub Templater 只认 `\k` |
| Style 分配 | 根据 Step 2 的时间阈值表, 将每行分配到正确的 Style |
| 注音嵌入 | Step 3 的结果, `漢|<かん` 格式 |
| Comment 行 | 所有 karaoke 源行必须是 `Comment:` + `Effect=karaoke` |
| Default 样式 | 如果有任何行引用 Default 样式, 必须在样式表中定义 |

**⭐ 注音特效同步 — `syl furi` 组合修饰符**:

这是最重要的注音处理规则。注音必须和主文字的卡拉OK特效(lead-in、highlight、lead-out)**完全同步**。

```ass
# ❌ 错误做法(注音不同步, 呆呆地显示):
template noblank multi,{...高光效果...}     ← 只处理主文字
template furi,{...静态显示...}               ← 独立处理注音, 无特效

# ✅ 正确做法(注音和主文字共享同一套特效):
template syl furi noblank multi,{...高光效果...}  ← 同时处理主文字和注音!
```

修改原则:

| 模板类型 | 是否加 `furi` | 原因 |
|---------|:---:|------|
| 文字高光 `template noblank multi` | ✅ → `syl furi noblank multi` | 注音需要同步高亮 |
| 文字 lead-in `template char` | ✅ → `syl furi char` | 注音需要同步入场 |
| 文字 lead-out `template noblank char` | ✅ → `syl furi noblank char` | 注音需要同步退场 |
| 粒子/装饰 `template notext` | ❌ 不加 | 装饰效果不需要给注音 |
| 矢量绘图 `\p1`/`\p2`/`\p3` | ❌ 不加 | 绘图装饰不适用于注音 |

⚠️ 注意:
- `syl furi` 是唯一允许的组合——不能写 `char furi`(应写 `syl furi char`)
- 如果只写 `furi`(不写 `syl`), 模板变成 furi-only 类, **不再处理主文字**!

#### 方式 B: Python 预渲染流

创建 `build_kfx_{song}.py` 脚本, 直接生成所有 fx Dialogue 行:

```python
# 典型结构:
# 1. 解析输入文件 → parse_k_tags()
# 2. 从参考文件提取 Script Info + Styles
# 3. 对每行每音节生成多层 fx:
#    - Main text (Layer 2): 主文字 + 颜色 + 动画
#    - Star (Layer 4): 星闪装饰
#    - Ring (Layer 0): 波纹扩散
#    - Glow (Layer 1): 发光效果
#    - Furigana: 注音行
# 4. 处理特殊段落: 回音(echo)、吟唱(chant)、中文特效
# 5. 输出完整 ASS 文件
```

运行方式:
```powershell
python -X utf8 build_kfx_{song}.py
```
⚠️ **必须加 `-X utf8`**, 否则 Windows 默认编码会导致日语/中文字符报错。

#### 中文翻译处理

| 段落 | 处理方式 | 说明 |
|------|---------|------|
| 非副歌段 | `\fad(300,300)` | 标准淡入淡出, 底部居中 |
| 副歌段 | `\pos(x,600)` | 手动定位 Y=600, 避免遮挡日语注音 |
| 特殊效果 | clip 切片 / 逐词出现 | Python 预渲染时可做更复杂的中文特效 |

**输出**: `*_KFX.ass` 模板文件(Aegisub Template 流)或完整 fx 文件(Python 预渲染流)

---

### Step 5: 验证与调试

1. **行数检查**
   - Aegisub Template 流: 模板文件通常 150~300 行
   - Python 预渲染流: fx 输出通常 3000~10000+ 行
   - 行数异常(过少/过多)说明有遗漏或重复

2. **搜索验证** — 从输出文件中搜索特定汉字的 fx 行, 与参考文件对比:
   - 时间戳是否正确(精确到 10ms)
   - ASS 标签顺序和格式是否匹配
   - clip 坐标范围是否合理

3. **常见问题清单**

   | 问题 | 症状 | 解决方案 |
   |------|------|---------|
   | `unicode.len` 参数错误 | Aegisub 报 "Expected 1 arguments, got 2" | 用括号包裹 `gsub()`: `unicode.len((str:gsub(" ","")))` |
   | Style not found: Default | 警告信息 | 在样式表末尾添加 Default 样式定义 |
   | 注音不显示 | fx 中无 furigana 行 | 检查是否使用了 `syl furi` 组合修饰符 |
   | 注音不同步 | 注音静态显示, 不跟随高亮 | 将 `template furi` 改为 `template syl furi ...` |
   | `\kf` 不识别 | Templater 不处理源行 | 将 `\kf` 转为 `\k` |
   | 中文遮挡注音 | 中文翻译与 furigana 重叠 | 调低中文 Y 坐标(如 640 → 600) |
   | 动画重叠 | 前一行退场与后一行入场冲突 | 入场不提前, 退场在 end_ms-300 结束 |

4. **运行 Aegisub 执行模板**(Template 流)
   ```
   Aegisub → 打开 *_KFX.ass → 自动化 → 卡拉OK模板
   → 等待处理 → 检查 fx 行数量 → 预览效果
   ```

**输出**: 验证报告 + 修复后的 KFX 文件

---

### Step 6: 精调优化

1. **颜色微调**: 在视频上预览, 调整颜色值适配实际画面
2. **时间微调**: 检查音节同步精度, 微调 K 值
3. **位置微调**: 检查文字位置(MarginV, `\pos`), 确保不遮挡画面
4. **粒子参数**: 调整粒子数量、速度、偏移范围
5. **段落过渡**: 确认段落切换处的视觉连贯性

---

### Step 7: 记录案例经验(ref)

**这是最重要的知识积累步骤。** 每次完成一个满意的 KFX 制作后, 必须记录案例经验。

**操作**: 在 `reference/案例/{歌曲名}/` 目录下创建以下文件:

```
reference/案例/{歌曲名}/
├── 制作记录.md      ← 核心文档: 设计思路、问题与解决、经验教训
├── build_kfx.ps1    ← 构建脚本(PS1 或 .py)
├── k帧.ass          ← 输入的 K 帧歌词(存档)
└── 成品_KFX.ass     ← 最终输出成品(存档)
```

**`制作记录.md` 必须包含以下章节**:

```markdown
# {歌曲名} — KFX 制作案例记录

> **歌曲**: {歌曲名}
> **歌手**: {歌手}
> **来源**: {番剧名} {OP/ED/Insert Song}
> **制作日期**: {日期}
> **参考模板**: {参考文件路径}
> **构建脚本**: {脚本文件名}

## 设计思路
- 为什么选择这个设计风格
- 与前作的差异点
- 参考来源的选择理由

## 制作流程
- 输入文件清单
- 构建脚本结构说明
- 歌曲段落映射表(时间 → Style → 效果 → 歌词概要)

## 遇到的问题与解决方案
- 每个问题: 现象 → 根因 → 修复方案 → 影响范围
- ⭐ 标记重要的可复用经验

## 注音统计
- 新增映射数量
- 上下文覆盖规则
- 特殊注音处理

## 文件清单
- 本案例涉及的所有文件

## 经验教训
- 可迁移到其他歌曲的通用经验(重点)
- 本歌曲特有的注意事项
```

**案例经验库的价值**:
- 后续制作新歌时, 首先查阅案例库中风格相近的记录
- 避免踩相同的坑
- 积累注音映射(furigana_map.txt 持续增长)
- 建立个人的设计风格库

---

## PowerShell 编码注意事项

Windows PowerShell 处理日语文件时有严重的编码陷阱:

### 1. 日语字符串不要写在 .ps1 中

PowerShell 脚本经过 GBK/UTF-8 编码转换后, 日语字符会被损坏。

**解决方案**: 将所有日语映射存储在独立的 UTF-8 文本文件中(如 `furigana_map.txt`), 运行时用 `[System.IO.File]::ReadAllLines($path, $utf8)` 读取。

### 2. 文件路径中含日语

使用 `Get-ChildItem` + `Where-Object` 通过模糊匹配找到文件:
```powershell
$allAss = Get-ChildItem -LiteralPath $dir -Filter "*.ass" -Recurse
$refFile = $allAss | Where-Object { $_.DirectoryName -match "3P" } | Select-Object -First 1
```

### 3. Unicode 字符比较

使用 `[char]0xXXXX` 码点, 不要直接写日语字符:
```powershell
$h97FF = [char]0x97FF  # 響
if ($stripped.Contains($h97FF)) { ... }
```

### 4. BOM 编码输出

ASS 文件需要 UTF-8 BOM 编码:
```powershell
$utf8Bom = New-Object System.Text.UTF8Encoding $true
[System.IO.File]::WriteAllLines($outputFile, $lines, $utf8Bom)
```

### 5. Join-Path 版本兼容

PowerShell v5 的 `Join-Path` 只支持 2 个参数:
```powershell
# 正确:
$path = Join-Path (Join-Path $scriptDir "reference") "music-ass"
```

### 6. Python 运行

```powershell
python -X utf8 build_kfx_{song}.py
```

---

## Aegisub Karaoke Templater 速查

### Effect 字段关键字

| Effect 值 | 作用 |
|-----------|------|
| `code once` | 脚本开始时执行一次, 定义全局变量/函数/形状 |
| `code line [all]` | 每行执行一次, 设置行级变量 |
| `code syl [all]` | 每个音节执行一次, 设置条件判定 |
| `template [syl] [furi] noblank multi` | 音节模板(多高亮+注音同步) |
| `template [syl] [furi] noblank char` | 逐字符模板(lead-in/lead-out) |
| `template noblank notext loop N` | 粒子循环(不输出文字, 循环 N 次) |
| `template notext noblank fxgroup X` | 条件装饰(仅 fxgroup.X=true 时执行) |
| `karaoke` | 源数据(被 Templater 读取并处理) |

### 修饰符

| 修饰符 | 作用 |
|--------|------|
| `noblank` | 跳过空白音节 |
| `notext` | 不输出文本(用于形状/粒子/装饰) |
| `multi` | 多高亮模式 |
| `char` | 逐字符处理 |
| `loop N` | 循环 N 次 |
| `all` | 匹配所有 style 的源行 |
| `fxgroup X` | 条件执行 |
| `syl furi` | ⭐ 同时处理主文字和注音 |

### 内联变量

| 变量 | 说明 |
|------|------|
| `$scenter`, `$smiddle` | 音节中心坐标 |
| `$lcenter`, `$lmiddle` | 行中心坐标 |
| `$sstart`, `$send`, `$sdur` | 音节起止时间(ms) |
| `$si`, `$syln` | 音节索引 / 总数 |
| `$j`, `$maxj` | 循环索引 / 总数 |
| `$swidth`, `$lwidth` | 音节/行宽度 |

### retime 模式

| 模式 | 效果 |
|------|------|
| `retime("syl", 0, 0)` | 精确音节时间 |
| `retime("start2syl", -N, 0)` | 行开始到音节开始(lead-in) |
| `retime("syl2end", 0, 0)` | 音节开始到行结束 |
| `retime("line", N, M)` | 行时间偏移 |
| `retime("set", start, end)` | 绝对时间 |

### Lua 内联代码 `!expr!`

```lua
!retime("syl", 0, 0)!           -- 重置到音节范围
!math.random(-20, 20)!           -- 随机数
!syl.i * 50!                     -- 音节索引计算
```

---

## ASS 特效标签速查

### 颜色(格式: `&HBBGGRR&` — BGR 顺序! )

| 标签 | 说明 |
|------|------|
| `\1c` | 主色(文字填充) |
| `\2c` | 次要色(卡拉OK) |
| `\3c` | 边框色 |
| `\4c` | 阴影色 |
| `\alpha` / `\1a~\4a` | 透明度(00=不透明, FF=全透明) |

### 文本样式

| 标签 | 示例 |
|------|------|
| `\fn<name>` | `{\fnFOT-PopJoy Std B}` |
| `\fs<size>` | `{\fs48}` |
| `\fscx<n>` / `\fscy<n>` | `{\fscx120\fscy80}` |
| `\fsp<px>` | `{\fsp5}` |

### 位置/移动

| 标签 | 说明 |
|------|------|
| `\an<1-9>` | 对齐(小键盘布局, 5=正中) |
| `\pos(x,y)` | 固定位置 |
| `\move(x1,y1,x2,y2[,t1,t2])` | 移动动画 |
| `\org(x,y)` | 旋转原点 |

### 动画

| 标签 | 说明 |
|------|------|
| `\fad(in, out)` | 淡入淡出(ms) |
| `\t(tags)` | 全时段标签动画 |
| `\t(t1, t2, tags)` | 定时动画 |
| `\t(t1, t2, accel, tags)` | 加速动画 |
| `\clip(x1,y1,x2,y2)` | 矩形裁剪 |
| `\iclip(x1,y1,x2,y2)` | 反向裁剪 |
| `\k<n>` / `\kf<n>` | 卡拉OK标签(厘秒) |
| `\p<n>` | 绘图模式 |

### 旋转

| 标签 | 说明 |
|------|------|
| `\frx<deg>` | X轴旋转(前后翻转) |
| `\fry<deg>` | Y轴旋转(左右翻转) |
| `\frz<deg>` | Z轴旋转 |

### `\t()` 可动画标签

`\fs` `\fsp` `\fscx` `\fscy` `\1c` `\2c` `\3c` `\4c` `\alpha` `\1a~\4a` `\bord` `\shad` `\blur` `\frz` `\frx` `\fry` `\clip()`

---

## 矢量形状库

### 使用方式

在 `code once` 中定义形状变量, 在 `template notext` 中通过 `\p1`/`\p2`/`\p3` + 形状字符串使用:

```lua
-- code once 中定义
feather = "m 26 37 l 38 27 l 45 19 ..."

-- template notext 中使用
{\an5\pos($scenter,$smiddle)\p2\fscx30\fscy30\frz!math.random(0,360)!}feather
```

### 预置形状

<details>
<summary>羽毛 (feather)</summary>

```
m 26 37 l 38 27 l 45 19 l 52 11 l 57 7 b 66 0 72 9 64 29 l 59 26 l 62 31
b 58 36 52 43 46 47 l 41 44 l 44 48 b 41 52 37 56 33 58 l 28 52 l 30 58
l 27 61 l 24 58 l 24 61 l 21 58 l 17 61 l 17 59 b 11 62 6 64 0 64 l 0 60
b 5 60 12 57 16 54 l 14 51 l 18 51 l 17 47 l 20 50 l 20 42 l 24 38 l 25 45
```
</details>

<details>
<summary>音符 (3种: note1 双八分, note2 四分, note3 附点)</summary>

```
-- note1 (双八分音符)
m 0 0 l 0 7 b 0 7 0 6 -1 7 b -1 7 -3 8 -2 9 b -2 9 -1 10 0 9 b 0 9 1 8 1 8
b 1 8 1 7 1 7 l 1 1 l 7 0 l 7 6 b 7 6 6 5 5 6 b 5 6 3 7 4 8 b 4 8 5 9 6 8
b 6 8 8 8 8 7 b 8 6 8 6 8 6 l 8 -1

-- note2 (四分音符)
m 0 0 l 0 9 b 0 9 -1 8 -3 9 b -3 9 -5 10 -4 12 b -4 12 -3 13 -1 12
b -1 12 1 11 1 10 b 1 10 1 9 1 9 l 1 -1

-- note3 (附点音符)
m 0 0 l 0 9 b 0 9 -1 8 -3 9 b -3 9 -5 10 -4 12 b -4 12 -3 13 -1 12
b -1 12 1 11 1 10 b 1 10 1 9 1 9 l 1 1 b 2 2 3 2 2 6 b 5 2 2 1 1 0
```
</details>

<details>
<summary>花朵 (3尺寸: hoa_big, hoa_mid, hoa_small)</summary>

```
-- 大
m 21 21 b 6 -7 46 -7 29 21 b 49 -2 63 34 30 28 b 63 44 31 65 25 32
b 26 65 -12 45 21 29 b -13 38 0 -5 21 21 m 25 22 b 21 22 21 28 25 28
b 29 28 29 22 25 22
-- 中
m 13 12 b 4 -4 28 -4 18 12 b 30 -1 38 20 18 17 b 38 26 19 39 15 19
b 16 39 -7 27 13 17 b -8 23 0 -3 13 12 m 15 13 b 13 13 13 17 15 17
b 18 17 18 13 15 13
-- 小
m 8 7 b 2 -2 17 -2 11 7 b 18 -1 23 11 11 9 b 23 14 11 21 9 10
b 9 21 -4 15 8 9 b -5 13 0 -2 8 7 m 9 7 b 8 7 8 9 9 9 b 11 9 11 7 9 7
```
</details>

<details>
<summary>蝴蝶翅膀 + 天使光环</summary>

```
-- 蝴蝶翅膀 (右翼, 左翼用 \fry180 镜像)
m 17 33 b 12 41 6 26 15 24 b 29 25 26 50 15 49 b 9 51 -4 41 2 22
b 11 3 28 -2 45 0 b 58 3 40 24 31 25 b 52 32 39 42 30 36 b 36 47 31 47 25 40
l 25 40 b 26 32 24 22 14 23 b 3 26 11 43 18 35

-- 天使光环 (椭圆环, \fscy50 压扁)
m 0 25 b 1 10 50 11 50 25 b 51 40 -1 40 0 25 m 2 23 b -5 38 49 39 49 25
b 50 14 6 11 2 23
```
</details>

<details>
<summary>齿轮、三角形、棍棒、矩形、圆形、雨滴</summary>

```
-- 三角形
triangle = "m 0 0 l -10 15 l 10 15"

-- 棍棒
stick = "m 0 0 l 3 -36 l 6 0 l 3 12"

-- 矩形 (glitter用)
rectangle = "m 0 0 l 0 100 l 100 100 l 100 0 l 0 0"

-- 圆形 (光晕用)
circle = "m 100 0 b 100 -55 55 -100 0 -100 b -55 -100 -100 -55 -100 0 b -100 55 -55 100 0 100 b 55 100 100 55 100 0"

-- 雨滴 (竖线条)
raindrop = "m 0 0 l 2 0 l 2 50 l 0 50 l 0 0"

-- 小羽毛 (简化版)
feather_small = "m 0 9 l -2 9 l -2 1 l -5 -2 l -8 -7 l -8 -12 l -7 -17 l -5 -20 l -1 -24 l 2 -21 l 4 -18 l 5 -13 l 5 -8 l 4 -4 l 3 -1 l 0 1 l 0 4 l 0 7"
```
</details>

<details>
<summary>草地 (4种)</summary>

```
grass1 = "m 0 0 b 8 -10 15 -4 21 -3 b 34 -2 32 -9 30 -11 b 25 -14 20 -6 27 -7"
grass2 = "m 0 0 b 8 -10 15 -4 21 -2 b 24 0 28 5 31 5 b 36 7 40 6 43 5"
-- (更多变体见参考文件)
```
</details>

---

## 素材库索引

制作新歌 KFX 时, 按以下分类查阅 `doc/素材库/` 中的 .ass 模板文件:

| 分类 | 目录 | 包含模板 | 适用情绪 |
|------|------|---------|---------|
| 基础模板 | `doc/素材库/01-基础模板/` | 量产三段式、简单淡入淡出 | 万能 |
| 卡拉OK换色 | `doc/素材库/02-卡拉OK换色/` | K 值换色、主边色切换 | 万能 |
| 粒子特效 | `doc/素材库/03-粒子特效/` | 雨滴、羽毛、雪花、glitter | 感伤/梦幻/热血 |
| 运动特效 | `doc/素材库/04-运动特效/` | 碎片组装、齿轮旋转 | 科技/命运 |
| clip遮罩 | `doc/素材库/05-clip遮罩/` | 帘幕展开、字体分割 | 优雅/创意 |
| 颜色渐变 | `doc/素材库/06-颜色渐变/` | 逐字渐变 | 彩虹/温暖 |
| 综合大作 | `doc/素材库/07-综合大作/` | 命运石之门、天气之子等 | 学习参考 |
| 绘图代码 | `doc/素材库/08-绘图代码/` | 矢量 shape 素材 | 所有装饰 |

### 选型流程

1. **听歌 + 分析情绪** → 判断整体氛围
2. **查阅设计方法论** → `doc/设计思想/OPED歌词特效设计思路.md`
3. **查阅情绪-特效对照表** → 找推荐组合
4. **从素材库选取** → `doc/素材库/` 对应分类
5. **参考综合大作** → `doc/素材库/07-综合大作/`
6. **混搭组合** → 不同段落可混用不同素材

---

## 案例经验库

已有 4 个完整制作案例可供参考:

| 案例 | 番剧 | 风格 | 流水线 | 关键经验 |
|------|------|------|--------|---------|
| 羽ばたきのバースデイ | 天使の3P! OP | 欢快可爱 | Aegisub Template | `syl furi` 注音同步、Aegisub 版本兼容性 |
| INNOCENT BLUE | 天使の3P! 挿入歌 | 欢快可爱 | Aegisub Template(复用) | 复用同动画模板、大量上下文注音覆盖 |
| 大切がきこえる | 天使の3P! 挿入歌 | 温暖抒情 | Aegisub Template(自包含) | 混合参考源、自包含脚本、时间阈值精确性 |
| Bravely You | Charlotte OP | 深沉感性 | Python 预渲染 | delay vs echo_delay 区分、配对消失、中文特效 |

案例详细记录位于 `reference/案例/{歌曲名}/制作记录.md`。

---

## 共通经验法则

1. **多 Layer 叠加**是创造视觉深度的关键(4~8 层/音节)
2. **自定义矢量形状**(`\p` 绘图模式)大幅提升丰富度
3. **段落完全差异化**: 不同段落用不同 Style、不同效果、不同颜色
4. **fxgroup 条件判定**是段落差异的核心
5. **假名注音必须用ひらがな**, 通过 `|<` 语法嵌入 karaoke 源行
6. **⭐ 注音用 `syl furi` 组合同步**, 不要用独立的 `template furi`
7. 高品质 KFX 通常 **5000~10000+** 行 fx 输出
8. **复用参考文件的模板代码**, 不要从零写模板
9. **运行 Python 必须加 `-X utf8`**
10. **时间戳从源文件提取**, 不要心算转换
11. **OPCN delay ≠ echo_delay**: 两者相差 ~1730ms, 不要混淆
12. **每次制作后记录案例经验**(Step 7), 知识持续积累

---

## 参考资源

### 本地资源
- **素材库总索引**: `doc/README.md`
- **设计方法论**: `doc/设计思想/OPED歌词特效设计思路.md`
- **分类模板**: `doc/素材库/`(8 大分类)
- **技术手册**: `doc/技术手册/ASS特效标签速查.md`
- **案例经验库**: `reference/案例/`
- **完整 KFX 参考**: `reference/music-ass/`
- **Seekladoom 合集**: `reference/Seekladoom-ASS-Effect-master/`
- **注音映射**: `furigana_map.txt`

### 在线资源
- **番剧信息**: [萌娘百科](https://zh.moegirl.org.cn/) + [Bangumi](https://bgm.tv/)
- **Aegisub Karaoke Templater**: https://aegisub.org/docs/latest/automation/karaoke_templater/
- **ASS 标签参考**: https://www.nikse.dk/subtitleedit/formats/assa-override-tags
- **481 特效模板合集**: https://github.com/Seekladoom/Aegisub-Karaoke-Effect-481-Templates
- **ASS 标签笔记**: https://note.tonycrane.cc/others/subs/ass/
- **Aegisub 自动化笔记**: https://note.tonycrane.cc/others/subs/aegisub/automation/
