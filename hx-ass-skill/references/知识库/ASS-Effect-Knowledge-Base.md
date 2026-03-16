# ASS 特效字幕完全知识体系

> **知识来源**: [Seekladoom/Seekladoom-ASS-Effect](https://github.com/Seekladoom/Seekladoom-ASS-Effect)
> **项目定位**: 日本动画 OP/ED 卡拉 OK 歌词特效字幕制作 · 特效模板 · 绘图代码 · 工具链资源集
> **许可证**: GPL v2 (禁止盈利)

---

## 目录

- [一、ASS 格式基础](#一ass-格式基础)
- [二、ASS 特效标签完全手册](#二ass-特效标签完全手册)
- [三、VSFilterMod 扩展标签](#三vsfiltermod-扩展标签)
- [四、Aegisub 卡拉 OK 模板系统](#四aegisub-卡拉ok-模板系统)
- [五、ASS 矢量绘图系统](#五ass-矢量绘图系统)
- [六、特效设计思路与方法论](#六特效设计思路与方法论)
- [七、中日字体匹配方案](#七中日字体匹配方案)
- [八、完整工具链](#八完整工具链)
- [九、实战案例拆解](#九实战案例拆解)
- [十、项目资源索引](#十项目资源索引)

---

## 一、ASS 格式基础

### 1.1 文件结构

ASS (Advanced SubStation Alpha) 字幕文件由以下段落组成:

```ini
[Script Info]        ; 脚本元信息
[Aegisub Project Garbage]  ; Aegisub 工程信息 (可选)
[V4+ Styles]         ; 样式定义
[Events]             ; 事件 (字幕行)
```

### 1.2 Script Info 段

```ini
[Script Info]
ScriptType: v4.00+           ; ASS 版本
PlayResX: 1920               ; 画面宽度 (坐标系基准)
PlayResY: 1080               ; 画面高度 (坐标系基准)
ScaledBorderAndShadow: yes   ; 边框/阴影是否随分辨率缩放
YCbCr Matrix: TV.709         ; 色彩空间矩阵
WrapStyle: 0                 ; 换行模式 (0=智能, 1=行尾, 2=不换行, 3=同0但下端对齐)
Timer: 100.0000              ; 计时器百分比
```

**关键概念**: `PlayResX/Y` 决定了所有坐标的参考系。常见值:
- `1920×1080` — Full HD
- `1280×720` — HD
- 所有 `\pos`、`\clip`、绘图坐标都基于这个坐标系

### 1.3 Style 定义

```
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour,
        Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle,
        BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
```

示例:
```
Style: OPJP,FOT-TsukuGo Pro B,53,&H00030303,&H000000FF,&H00B7B7B8,&H00000000,
       0,0,0,0,100,100,1,0,1,2,0,8,10,10,10,1
```

**颜色格式**: `&HAABBGGRR` (注意是 **BGR** 不是 RGB!)
- `&H00FFFFFF` = 白色 (完全不透明)
- `&HFF000000` = 黑色 (完全透明)
- AA = 透明度, 00=不透明, FF=全透明

**Alignment 对齐 (数字小键盘布局)**:
```
7 (左上)  8 (上中)  9 (右上)
4 (左中)  5 (正中)  6 (右中)
1 (左下)  2 (下中)  3 (右下)
```

**BorderStyle**:
- `1` = 边框 + 阴影 (常用)
- `3` = 不透明背景框

### 1.4 Events 行

```
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
```

- **Dialogue** — 普通字幕行
- **Comment** — 注释行 (不渲染, 但模板系统会读取)

```
Dialogue: 0,0:00:00.00,0:00:05.00,OPJP,,0,0,0,,{\k55}響{\k60}け!{\k36}生{\k34}ま{\k52}れ...
Comment: 2,0:00:00.00,0:00:00.00,Default,,0,0,0,template char noblank,...
```

---

## 二、ASS 特效标签完全手册

> 所有特效标签都写在 `{}` 花括号内，作为 Text 字段的一部分。

### 2.1 颜色与透明度

| 标签 | 说明 | 示例 |
|------|------|------|
| `\1c&HBBGGRR&` | 主要颜色 (填充色) | `\1c&H0096FF&` |
| `\2c&HBBGGRR&` | 次要颜色 (卡拉 OK 变色前的颜色) | `\2c&H0096FF&` |
| `\3c&HBBGGRR&` | 边框颜色 | `\3c&H0096FF&` |
| `\4c&HBBGGRR&` | 阴影颜色 | `\4c&H0096FF&` |
| `\1a&HAA&` | 主要颜色透明度 | `\1a&H64&` (约 40% 透明) |
| `\2a&HAA&` | 次要颜色透明度 | `\2a&H64&` |
| `\3a&HAA&` | 边框透明度 | `\3a&H64&` |
| `\4a&HAA&` | 阴影透明度 | `\4a&H64&` |
| `\alpha&HAA&` | 全部颜色透明度 | `\alpha&HFF&` (全透明) |

**透明度值**: `00` = 完全不透明, `FF` = 完全透明

### 2.2 字体与文字

| 标签 | 说明 | 示例 |
|------|------|------|
| `\fn<name>` | 字体名称 | `\fn思源黑体 Medium` |
| `\fs<size>` | 字体大小 | `\fs200` |
| `\fscx<pct>` | 水平缩放 (百分比) | `\fscx200` (200%) |
| `\fscy<pct>` | 垂直缩放 (百分比) | `\fscy200` |
| `\fsp<px>` | 字符间距 (像素) | `\fsp20` |
| `\b1` / `\b0` | 粗体 开/关 | |
| `\i1` / `\i0` | 斜体 开/关 | |
| `\u1` / `\u0` | 下划线 开/关 | |
| `\s1` / `\s0` | 删除线 开/关 | |
| `\fe<id>` | 字体字符集编码 | `\fe128` (日文 Shift_JIS) |

### 2.3 边框与阴影

| 标签 | 说明 | 示例 |
|------|------|------|
| `\bord<px>` | 边框宽度 | `\bord10` |
| `\xbord<px>` | 横向边框宽度 | `\xbord10` |
| `\ybord<px>` | 纵向边框宽度 | `\ybord10` |
| `\shad<px>` | 阴影距离 | `\shad10` |
| `\xshad<px>` | 横向阴影偏移 | `\xshad10` |
| `\yshad<px>` | 纵向阴影偏移 | `\yshad10` |

### 2.4 模糊

| 标签 | 说明 | 示例 |
|------|------|------|
| `\be<n>` | 边框模糊 (简单均值) | `\be2` |
| `\blur<n>` | 高斯模糊 (更平滑, **推荐**) | `\blur2` |

### 2.5 位置与移动

| 标签 | 说明 | 示例 |
|------|------|------|
| `\an<1-9>` | 对齐方式 (小键盘布局) | `\an5` (居中) |
| `\pos(x,y)` | 固定位置 | `\pos(960,540)` |
| `\move(x1,y1,x2,y2)` | 移动 (全程) | `\move(960,540,1260,540)` |
| `\move(x1,y1,x2,y2,t1,t2)` | 移动 (指定时间段) | |
| `\org(x,y)` | 旋转原点 | `\org(640,540)` |

### 2.6 旋转与变换

| 标签 | 说明 | 示例 |
|------|------|------|
| `\frx<deg>` | X 轴旋转 (俯仰) | `\frx30` |
| `\fry<deg>` | Y 轴旋转 (偏航) | `\fry30` |
| `\frz<deg>` | Z 轴旋转 (平面旋转) | `\frz30` |
| `\fax<factor>` | X 轴剪切 (斜体效果) | `\fax-0.1` |
| `\fay<factor>` | Y 轴剪切 | `\fay-0.1` |

### 2.7 遮罩 (Clip)

| 标签 | 说明 | 示例 |
|------|------|------|
| `\clip(x1,y1,x2,y2)` | 矩形遮罩 (仅显示区域内) | `\clip(740,470,960,620)` |
| `\iclip(x1,y1,x2,y2)` | 反向矩形遮罩 (隐藏区域内) | `\iclip(740,470,960,620)` |
| `\clip(drawcmd)` | 矢量遮罩 | `\clip(m 740 480 l 980 480 740 620)` |
| `\iclip(drawcmd)` | 反向矢量遮罩 | |

**重要**: Clip 是极其强大的标签，可以实现:
- **字体分割效果** — 上半用黑体下半用宋体 (见 "黑宋 clip" 示例)
- **逐字揭露动画** — 配合 `\t` 实现文字从左到右出现
- **任意形状的遮罩** — 用矢量路径定义

### 2.8 渐变与淡入淡出

| 标签 | 说明 | 示例 |
|------|------|------|
| `\fad(t_in,t_out)` | 简单淡入淡出 (毫秒) | `\fad(200,200)` |
| `\fade(a1,a2,a3,t1,t2,t3,t4)` | 复杂渐变 | `\fade(255,32,224,0,200,700,1000)` |

### 2.9 动画标签 `\t`

**`\t` 是 ASS 动画的核心!**

```
\t(t1, t2, style_override)        ; 在 t1~t2 时间内从当前状态过渡到目标状态
\t(t1, t2, accel, style_override) ; 带加速度参数
```

**支持 `\t` 动画的标签** (可放在 `\t()` 中):

| 类别 | 标签 |
|------|------|
| 颜色 | `\1c`, `\2c`, `\3c`, `\4c` |
| 透明度 | `\1a`, `\2a`, `\3a`, `\4a`, `\alpha` |
| 边框/阴影 | `\bord`, `\xbord`, `\ybord`, `\shad`, `\xshad`, `\yshad` |
| 模糊 | `\be`, `\blur` |
| 缩放 | `\fscx`, `\fscy`, `\fs` |
| 间距 | `\fsp` |
| 旋转 | `\frx`, `\fry`, `\frz` |
| 剪切 | `\fax`, `\fay` |
| 遮罩 | `\clip` (矩形), `\iclip` (矩形) |

示例 — 颜色渐变动画:
```
{\1c&H0096FF&\t(0,1000,\1c&HFFFFFF&)}
; 在 0~1000ms 内, 主色从蓝色渐变到白色
```

示例 — 旋转放大动画:
```
{\frz0\fscx50\fscy50\t(0,1000,\frz180\fscx150\fscy150)}
; 在 0~1000ms 内, 从 0° 旋转到 180°, 同时从 50% 放大到 150%
```

### 2.10 卡拉 OK 标签

| 标签 | 说明 | 效果 |
|------|------|------|
| `\k<centi>` | 逐字变色 (瞬间) | 到达时间后瞬间变为次要颜色 |
| `\K<centi>` / `\kf<centi>` | 逐字填充 (从左到右) | 扫描式填充效果 |
| `\ko<centi>` | 逐字描边 | 到达时间后显示描边 |

时间单位: **厘秒** (centisecond, 1/100秒)。`\k36` = 360ms

### 2.11 换行与空格

| 标签 | 说明 |
|------|------|
| `\n` | 软换行 (WrapStyle 决定是否生效) |
| `\N` | 硬换行 (总是换行) |
| `\h` | 硬空格 (不可断的空格) |

### 2.12 其他标签

| 标签 | 说明 | 示例 |
|------|------|------|
| `\r<style>` | 重置为指定样式 | `\rOPCN` |
| `\p<n>` | 进入绘图模式 (`n≥1`) | `\p1` |
| `\pbo<px>` | 绘图基线偏移 | `\pbo-50` |

---

## 三、VSFilterMod 扩展标签

> 这些标签**不属于标准 ASS 规范**, 需要 VSFilterMod 渲染器支持。
> 标准 libass 不支持, 因此在一般播放器中不生效。

### 3.1 颜色渐变 (四角渐变)

| 标签 | 说明 |
|------|------|
| `\1vc(TL,TR,BR,BL)` | 主色四角渐变 |
| `\2vc(...)` | 次色四角渐变 |
| `\3vc(...)` | 边框色四角渐变 |
| `\4vc(...)` | 阴影色四角渐变 |
| `\1va(TL,TR,BR,BL)` | 主色四角透明度渐变 |
| `\2va(...)` | 次色四角透明度渐变 |
| `\3va(...)` | 边框四角透明度渐变 |
| `\4va(...)` | 阴影四角透明度渐变 |

示例:
```
{\1vc(&H00FFFF&,&HFFFF00&,&HFF00FF&,&H000000&)}
; 四个角分别为 青/黄/品/黑 的渐变填充
```

### 3.2 扭曲与变形

| 标签 | 说明 | 示例 |
|------|------|------|
| `\distort(u1,v1,u2,v2,u3,v3)` | UV 扭曲映射 | `\distort(1,0,1.2,1,-0.2,1)` |
| `\rnd<n>` | 边界随机变形 | `\rnd30` |
| `\rndx<n>` | X 轴边界变形 | `\rndx30` |
| `\rndy<n>` | Y 轴边界变形 | `\rndy30` |
| `\rndz<n>` | Z 轴边界变形 | `\rndz30` |

### 3.3 高级移动

| 标签 | 说明 |
|------|------|
| `\mover(x1,y1,x2,y2,a1,a2,r1,r2,t1,t2)` | 极性移动 (圆形轨迹) |
| `\moves3(x1,y1,x2,y2,x3,y3,t1,t2)` | 三点贝塞尔曲线移动 |
| `\moves4(x1,y1,x2,y2,x3,y3,x4,y4,t1,t2)` | 四点贝塞尔曲线移动 |
| `\movevc(x1,y1,x2,y2,t1,t2)` | 可移动矢量 clip |

### 3.4 其他 MOD 标签

| 标签 | 说明 |
|------|------|
| `\fsc<n>` | 统一字体缩放 (替代 fscx+fscy) |
| `\fsvp<n>` | 纵向偏移 (逐字高低错落) |
| `\frs<deg>` | 基线倾斜角度 |
| `\jitter(...)` | 抖动效果 |
| `\z<n>` | Z 坐标 (配合 `\frx`/`\fry` 实现透视) |
| `\1img(file)` | 图片蒙版/挂图 |

---

## 四、Aegisub 卡拉 OK 模板系统

> 这是 Aegisub 内置的自动化引擎, 用于将 K 值时间轴 + 模板行 → 生成特效字幕行。

### 4.1 核心概念

模板系统的工作流:
```
K 值行 (karaoke)  →  模板行 (template)  →  自动化执行  →  fx 行 (最终特效)
```

### 4.2 K 值行 (karaoke)

```
Comment: 0,0:00:54.43,0:00:59.92,OPJP,,0,0,0,karaoke,
{\k55}響{\k60}け!{\k36}生{\k34}ま{\k52}れ{\k40}た{\k26}て{\k39}の{\k27}夢{\k19}つ{\k23}め{\k64}込ん{\k54}で
```

- Effect 字段为 `karaoke`
- 每个 `\k` 值表示该音节持续时间 (单位: 厘秒)
- `\k55` = 这个字/音节持续 550ms

### 4.3 模板行 (template)

模板行的 Effect 字段格式: `template [修饰符...]`

**基本修饰符**:

| 修饰符 | 说明 |
|--------|------|
| `char` | 逐字处理 (默认是逐音节 syl) |
| `noblank` | 跳过空白字符 |
| `notext` | 不输出原文本 (用于纯图形特效) |
| `loop N` | 循环 N 次 |

**常用模板变量** (Lua 内联代码用 `!...!` 包裹):

| 变量 | 说明 |
|------|------|
| `$center` | 当前字符水平中心 |
| `$middle` | 当前字符垂直中心 |
| `$sleft` / `$sright` | 音节左/右边界 |
| `$stop` / `$sbottom` | 音节上/下边界 |
| `$sdur` | 音节持续时间 (ms) |
| `$si` | 当前音节索引 (从 1 开始) |
| `$syln` | 总音节数 |

**retime 函数** — 控制每个字符的显示时间:

| 调用 | 含义 |
|------|------|
| `!retime("start2syl", offset1, offset2)!` | 从行开头到当前音节 |
| `!retime("syl", offset1, offset2)!` | 当前音节时间段 |
| `!retime("syl2end", offset1, offset2)!` | 从当前音节到行末 |
| `!retime("line", offset1, offset2)!` | 整行时间 |

### 4.4 经典三段式模板 (入场 → 高亮 → 退场)

这是最常用的卡拉 OK 特效模式:

```lua
-- 入场: 从行首到音节开始, 每个字依次出现
Comment: template char noblank,
  !retime("start2syl",($si-1)*30-200,0)!
  {\an5\pos($center,$middle)\1c&H000000&\3c&HFFFFFF&\blur2\fad(200,0)}

-- 高亮: 音节播放期间, 颜色翻转
Comment: template char noblank,
  !retime("syl",0,0)!
  {\an5\pos($center,$middle)\blur2\1c&H000000&\3c&HFFFFFF&
   \t(0,$sdur,\1c&HFFFFFF&\3c&H000000&)}

-- 退场: 从音节结束到行末, 渐出
Comment: template char noblank,
  !retime("syl2end",0,($si-1)*30+200)!
  {\an5\pos($center,$middle)\1c&HFFFFFF&\3c&H000000&\blur2\fad(0,200)}
```

**效果**: 每个字按顺序淡入出现 → 轮到该字时颜色翻转 (黑→白) → 之后保持并最终淡出

### 4.5 code 行 (Lua 代码块)

```lua
-- 全局变量定义
Comment: code once, Triangle = { "m 50 0 l 112 100 l -12 100 l 50 0" }

-- 每个音节执行
Comment: code syl all, fxgroup.firstsyl = syl.i == 1

-- 颜色计算函数
Comment: template noblank,
  !retime("line",0,0)!
  {\an5\pos($center,$middle)
   \3c!_G.ass_color(241-($si/$syln)*13, 146-($si/$syln)*146, 1+($si/$syln)*30)!}
```

**`_G.ass_color(r, g, b)`** — 内置函数, 将 RGB 值转为 ASS 颜色格式 (自动转 BGR)

### 4.6 fxgroup 条件分组

```lua
-- 定义条件: 只在第一个音节触发
Comment: code syl all, fxgroup.firstsyl = syl.i == 1

-- 使用条件: 这个模板只在 firstsyl 为 true 时生效
Comment: template notext fxgroup firstsyl, {\an5\pos($center,$middle)\p1}!Triangle[1]!
```

### 4.7 循环与动态图形

```lua
-- 旋转矩形效果: 每个字高亮时, 生成 10 个不断旋大的空心矩形
Comment: template noblank notext loop 10,
  !retime("syl",(j-1)*50-50,(j-1)*50-$sdur)!
  {\an5\pos($center,$middle)\bord0\1c&H7314E1&\frz!j*-18!\p1}
  m 0 0 l !30+j*6! 0 l !30+j*6! !30+j*6! l 0 !30+j*6!
  m !15-j*1.5! !15+j*7.5! l !15+j*7.5! !15+j*7.5!
  l !15+j*7.5! !15-j*1.5! l !15-j*1.5! !15-j*1.5!
```

- `loop 10` → 变量 `j` 从 1 到 10
- 每次循环绘制不同大小和旋转角度的矩形
- 两个 `m` 路径组成空心效果 (外矩形 + 内矩形, 利用奇偶填充规则)

---

## 五、ASS 矢量绘图系统

### 5.1 绘图模式基础

进入绘图模式: `\p1` (开启), `\p0` (关闭)

`\p<n>` 中 n 值决定坐标精度:
- `\p1` — 1 像素精度
- `\p2` — 1/2 像素精度 (坐标值要 ×2)
- `\p4` — 1/4 像素精度

### 5.2 绘图命令

| 命令 | 说明 | 语法 |
|------|------|------|
| `m` | 移动画笔 (起点) | `m x y` |
| `l` | 直线到 | `l x y` |
| `b` | 三次贝塞尔曲线 | `b x1 y1 x2 y2 x3 y3` |
| `s` | 三次B样条曲线 | `s x1 y1 x2 y2 ...` |
| `p` | 扩展B样条 | `p x y` |
| `c` | 闭合B样条 | `c` |

### 5.3 基本图形示例

**矩形**:
```
{\p1}m 0 0 l 500 0 l 500 500 l 0 500 l 0 0
```

**三角形**:
```
{\p1}m 50 0 l 112 100 l -12 100 l 50 0
```

**空心矩形** (利用奇偶填充):
```
{\p1}m 0 0 l 90 0 l 90 90 l 0 90
     m 10 10 l 80 10 l 80 80 l 10 80
```

> **奇偶填充规则**: 两个封闭路径重叠区域会被"挖空", 因此内部矩形区域不填色

**圆形** (用贝塞尔曲线近似):
```
{\p1}m 220.29 303.85 b 174.22 303.85 136.73 266.37 136.73 220.29
     136.73 174.22 174.22 136.73 220.29 136.73
     266.37 136.73 303.85 174.22 303.85 220.29
     303.85 266.37 266.37 303.85 220.29 303.85
```

### 5.4 复杂矢量图形

项目中的瞄准镜绘图代码展示了极其复杂的矢量图形:
- **18 种瞄准镜** — 包含同心圆、十字线、刻度、对角线等
- **12 种雪花** — 六角对称的精细矢量
- **35 种雪花设计图** — 从 Freepik 等矢量素材转换而来
- **枪械、冷兵器** — 详细的武器轮廓

**EPS → ASS 转换工作流**:
```
Adobe Illustrator 制作/打开 .ai/.eps
  → 导出为 EPS 路径数据
  → 工具转换为 ASS 绘图命令 (m/l/b)
  → 粘贴到 ASS 文件的 Text 字段
```

### 5.5 `\N` 多路径分离

ASS 绘图中可以用 `\N` (硬换行) 分隔多个独立的绘图路径组:

```
m 219.35 114.98 b ... l ... ; 第一组路径
\N
m 243.37 220.29 b ...       ; 第二组路径 (独立渲染)
```

这允许在同一个 Dialogue 行中绘制多个不相连的图形。

---

## 六、特效设计思路与方法论

> 来自项目中的 `OPED歌词特效设计思路/` 目录

### 6.1 可直接从 OP/ED 画面中提取的灵感

1. **STAFF 流** — 从 STAFF 字幕的运动方式 (淡入淡出、滑动、缩放) 获取灵感
2. **LOGO 流** — 从动画标题 LOGO 的设计风格 (颜色、质感、排版) 提取
3. **道具流** — 从画面中出现的道具/物件提取图形元素
4. **人物流** — 人物造型的配色、服装特征等融入字幕设计

### 6.2 不一定能直接看到的灵感源

1. **歌词含义流** — 根据歌词内容选择特效 (如"雪"用雪花粒子、"火"用暖色调)
2. **题材流** — 动画题材决定风格 (校园=清新、战斗=硬朗、恐怖=阴暗)
3. **技术流** — 纯粹展示 ASS 特效技术的创意
4. **色彩流** — 从 OP/ED 画面的主色调提取配色方案

### 6.3 打破常规的思维

1. **不匹配** — 有意使用与画面风格相反的字幕特效, 制造反差感
2. **反套路** — 常见效果的逆向运用 (如退场效果用在入场)
3. **混搭** — 不同风格特效的组合

### 6.4 风格转化与融合

1. **LOGO 颜色用在 STAFF 上** — 统一色彩体系
2. **应援色运用** — 用角色/团体的应援色做配色
3. **跨番联动** — 类似题材作品间的风格借鉴

---

## 七、中日字体匹配方案

> 日本动画字幕需要同时显示日文和中文, 字体匹配是关键

### 7.1 匹配原则

- **字面大小一致** — 日文字体通常偏小, 需要调整 `\fs` 或选择字面相近的字体
- **风格一致** — 黑体配黑体、宋体配宋体、手写体配手写体
- **粗细一致** — Regular 配 Regular, Bold 配 Bold

### 7.2 项目提供的匹配方案

| 风格 | 日文字体 (示例) | 中文字体 (示例) |
|------|-----------------|-----------------|
| 黑体 | 思源黑体 (7字重) | 思源黑体 SC |
| 宋体 | 思源宋体 (7字重) | 思源宋体 SC |
| 筑紫黑体 | FOT-TsukuGo Pro B | 方正韵动中黑_GBK |
| 筑紫明朝 | FOT-TsukuMin Pro E | 方正中粗雅宋_GBK |
| 书法/古风 | 多种日文书法字体 | 方正楷体_GBK 等 |
| 可爱手写 | 多种日文手写字体 | 华康/方正手写体 |
| 哥特风 | 哥特体 | 对应风格中文 |
| 科幻风 | 科幻体 | 对应风格中文 |
| 力量感 | 粗黑/impact 类 | 对应风格中文 |
| 泛 CJK | 思源 (泛CJK) | 思源 (泛CJK) |

### 7.3 GBK 字体注意事项

- **真 GBK** — 字体内含完整 GBK 编码, 可直接使用
- **伪 GBK** — 方正部分字体标记为 GBK 但实际缺字, 需注意
- **建议**: 使用 Fontworks、思源等字体, 或者 Aegisub 的字体搜集器检查缺字

### 7.4 Furigana (注音假名) 样式

项目中大量使用 `-furigana` 后缀样式:

```
Style: OPJP,FOT-TsukuGo Pro B,53,...,8,...    ; 主歌词
Style: OPJP-furigana,FOT-TsukuGo Pro B,26.5,...,8,...  ; 注音 (约主字体一半大小)
```

Aegisub 的 furigana 系统会自动将注音假名排列在对应汉字上方。

---

## 八、完整工具链

### 8.1 核心工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **Aegisub** | 字幕编辑 | 核心工具, 内置卡拉OK模板引擎 |
| **Aegisub 3.3.2** | 高级版本 | 支持 OpenType 竖排文本 |
| **Kara Effector** | 特效生成 | 另一套特效模板系统, 6 类特效: lead-in / hi-light / lead-out / shape / translation / function |
| **NyuFX** | 特效模板 | 基于 Lua 的另一套模板写法 |
| **PyonFX** | Python 特效库 | 用 Python 编程生成特效字幕 |

### 8.2 渲染器

| 渲染器 | 标准标签 | MOD 标签 | 说明 |
|--------|----------|----------|------|
| **libass** | ✅ | ❌ | 大多数播放器默认使用 |
| **VSFilter** | ✅ | ❌ | 经典渲染器 |
| **VSFilterMod** | ✅ | ✅ | 支持 MOD 扩展标签 |
| **xySubFilter** | ✅ | 部分 | 高性能渲染器 |

### 8.3 播放器配置

**外挂特效字幕的正确播放方式**:
- **PotPlayer**: MadVR + xySubFilter
- **MPC-HC/BE**: xySubFilter
- 需要卸载默认字幕渲染器, 挂载 VSFilterMod 或 xySubFilter

### 8.4 压制流程

OpenType 竖排文本的压制:
```
VapourSynth + ShiftMediaProject 的 assrender.dll
```

### 8.5 辅助工具

- **VSCode ASS 语法高亮** — 项目提供了 `VSCode-Style.tmTheme` 主题文件
- **Adobe Illustrator** — 制作矢量素材 → 导出为 ASS 绘图代码
- **上古工具集** — Aegisub 1.07、PopSub 0.75、效果器 v2 等历史工具

---

## 九、实战案例拆解

### 9.1 逐字淡入淡出 + 换色 (卡拉OK基础效果)

**模板**:
```
template char noblank: !retime("start2syl",($si-1)*30-200,0)!
  {\an5\pos($center,$middle)\1c&H000000&\3c&HFFFFFF&\blur2\fad(200,0)}

template char noblank: !retime("syl",0,0)!
  {\an5\pos($center,$middle)\blur2\1c&H000000&\3c&HFFFFFF&
   \t(0,$sdur,\1c&HFFFFFF&\3c&H000000&)}

template char noblank: !retime("syl2end",0,($si-1)*30+200)!
  {\an5\pos($center,$middle)\1c&HFFFFFF&\3c&H000000&\blur2\fad(0,200)}
```

**原理分析**:
1. **入场**: 每个字间隔 30ms 依次淡入 (200ms fad), 初始状态 = 黑字白边框
2. **高亮**: 到该字的 K 值时间时, 用 `\t` 动画将颜色翻转 (黑→白, 边框白→黑)
3. **退场**: 唱过之后保持翻转颜色, 最终全部淡出

### 9.2 旋转矩形特效

**模板**:
```lua
template noblank notext loop 10:
  !retime("syl",(j-1)*50-50,(j-1)*50-$sdur)!
  {\an5\pos($center,$middle)\bord0\1c&H7314E1&\frz!j*-18!\p1}
  m 0 0 l !30+j*6! 0 l !30+j*6! !30+j*6! l 0 !30+j*6!
  m !15-j*1.5! !15+j*7.5! l !15+j*7.5! !15+j*7.5!
  l !15+j*7.5! !15-j*1.5! l !15-j*1.5! !15-j*1.5!
```

**分解**:
- `notext` — 不输出原文字, 只画图形
- `loop 10` — 生成 10 帧, 每帧间隔 50ms
- `\frz!j*-18!` — 每帧旋转 -18°, 10 帧共 -180°
- 矩形尺寸 `30+j*6` 逐帧增大
- 两个 `m` 路径构成空心矩形

**效果**: 每个字高亮时, 一个紫色空心矩形从小到大旋转展开

### 9.3 逐字颜色渐变

```lua
template noblank: !retime("line",0,0)!
  {\an5\pos($center,$middle)
   \3c!_G.ass_color(241-($si/$syln)*13, 146-($si/$syln)*146, 1+($si/$syln)*30)!}
```

**原理**: 根据字符索引 `$si` 和总数 `$syln` 的比例, 计算出每个字的颜色分量, 实现从橙到红 (或其他颜色) 的平滑渐变。

### 9.4 黑宋 Clip 效果 (上下字体分割)

```
template noblank (Layer 0):
  {\an5\pos($center,$middle)\iclip($sleft,$top,$sright,$middle)\fn思源黑体 Medium}

template noblank (Layer 1):
  {\an5\pos($center,$middle)\iclip($sleft,$middle,$sright,$bottom)\fn思源宋体 SemiBold}
```

**原理**:
- 同一个字渲染两次, 分别在不同 Layer
- Layer 0 用 `\iclip` 裁掉上半部 → 只显示下半 → 用黑体
- Layer 1 用 `\iclip` 裁掉下半部 → 只显示上半 → 用宋体
- 效果: 每个字上半是宋体、下半是黑体 (或反之)

### 9.5 量产模板结构 (多 Style 多特效共存)

```
Style: OP JP, FOT-TsukuGo Pro B, 53, ...     ; 日文歌词
Style: OP CN, 方正韵动中黑_GBK, 40, ...       ; 中文翻译
Style: STAFF, 方正楷体_GBK, 30, ...           ; STAFF 字幕
Style: TEXT JP, FOT-TsukuMin Pro E, 40, ...    ; 画面文字翻译
Style: IN1 JP, @FOT-Greco Std B, 32, ...       ; 竖排日文 (@ 前缀 = 竖排)
```

**注意 `@` 前缀**: 在字体名前加 `@` 表示使用竖排模式, 配合对应 Alignment 使用。

---

## 十、项目资源索引

### 10.1 特效成品 (根目录 .ass 文件)

| 文件名 | 内容 |
|--------|------|
| `GRAND ESCAPE MV KFX EMOTION/LOGO.ass` | 天气之子 · 超大规模 KFX (各 3.89MB) |
| `SAO3 OP2 SC 第1/2版画面.ass` | 刀剑神域 OP2 特效 |
| `命运石之门 0 OP1/OP2.ass` | 命运石之门0 两首 OP 特效 |
| `Bofuri OP.ass` | 盾之勇者成名录 OP |
| `Little Busters! OP 全歌词.ass` (×3) | 三种不同特效风格 |
| `JOJO3 欧拉木大对轰字幕.ass` | JOJO 特殊字幕 |
| `歌词特效-量产模板.ass` | 完整的多 Style 量产模板结构 |

### 10.2 教学资源

| 目录/文件 | 内容 |
|-----------|------|
| `简单效果示例+问题教学模板/` | 14 个入门级 ASS 文件 |
| `其他/ASS 特效标签合集.ass` | 标准标签速查手册 |
| `其他/ASS MOD特效标签合集.ass` | VSFilterMod 扩展标签手册 |
| `OPED歌词特效设计思路/` | 设计方法论文档 |
| `中日字体匹配/` | 15 个字体匹配方案 |

### 10.3 K 值时间轴库

| 目录 | 内容 |
|------|------|
| `K值字幕文件/` | ~90 个日本动画 OP/ED K 值 |
| `K值字幕文件/燃曲合集/` | 40 首精选燃曲 |
| `K值字幕文件/可爱俏皮合集/` | 萌系/可爱风格合集 |

### 10.4 矢量素材

| 目录/文件 | 内容 |
|-----------|------|
| `绘图代码/` | 瞄准镜(18种)、雪花(12+35种)、武器(12种) |
| `绘图代码/EPS素材/` | 6 个 EPS 矢量源文件 |
| `绘图代码/AI素材/` | Illustrator 源文件 |

### 10.5 工具与插件

| 文件 | 内容 |
|------|------|
| `AutoTags.rar` | 自动化标签工具 |
| `HandwritingFX.7z` | 手写特效工具 |
| `Kara Effector 3.5.rar` | Kara Effector 工具包 |
| `上古ASS字幕制作工具/` | 7 个历史工具存档 |
| `部分上古ASS字幕工具.rar` | 更多历史工具 |
| `其他/VSCode-Style.tmTheme` | VSCode 语法高亮主题 |

---

## 附录 A: 快速参考卡片

### A.1 颜色常用值

```
白色: &H00FFFFFF   黑色: &H00000000
红色: &H000000FF   蓝色: &H00FF0000
绿色: &H0000FF00   黄色: &H0000FFFF
青色: &H00FFFF00   品红: &H00FF00FF
```

### A.2 常用特效组合

```
淡入淡出: {\fad(200,200)}
模糊淡入: {\blur3\fad(200,0)}
居中定位: {\an5\pos(960,540)}
逐字高亮: {\k36}字{\k36}幕
颜色翻转: {\1c&H000000&\3c&HFFFFFF&\t(0,360,\1c&HFFFFFF&\3c&H000000&)}
矩形绘图: {\p1}m 0 0 l 100 0 l 100 100 l 0 100
```

### A.3 模板速查

```
逐字模板:        template char noblank
逐音节模板:      template noblank
纯图形模板:      template noblank notext
循环模板:        template noblank notext loop 10
全局代码:        code once
逐音节代码:      code syl all
K值行:           karaoke
```

---

*本文档基于 Seekladoom/Seekladoom-ASS-Effect 项目的全面分析而成。该项目涵盖 314 个文件, 193 个 ASS 文件, 覆盖了 ASS 特效字幕的方方面面。*
