# ASS 特效标签速查手册

> 面向 AI KFX 制作的快速参考

---

## 一、Override Tags(覆盖标签)

### 定位与对齐
| 标签 | 说明 | 示例 |
|------|------|------|
| `\an1~9` | 对齐方式(小键盘布局) | `\an5` = 居中 |
| `\pos(x,y)` | 固定位置 | `\pos($center,$middle)` |
| `\move(x1,y1,x2,y2)` | 匀速移动 | `\move(0,0,100,100)` |
| `\move(x1,y1,x2,y2,t1,t2)` | 定时移动 | `\move(0,0,100,100,0,500)` |

### 字体与文本
| 标签 | 说明 | 示例 |
|------|------|------|
| `\fn字体名` | 字体 | `\fnFaux Snow BRK` |
| `\fs数值` | 字号 | `\fs70` |
| `\fscx数值` | 水平缩放% | `\fscx130` |
| `\fscy数值` | 垂直缩放% | `\fscy130` |
| `\fsp数值` | 字间距 | `\fsp3` |
| `\b1` / `\i1` | 粗体/斜体 | — |

### 颜色
| 标签 | 说明 | 格式 |
|------|------|------|
| `\1c&HBBGGRR&` | 主色(填充) | `\1c&H00FFFFFF&` = 白 |
| `\2c&HBBGGRR&` | 次色(卡拉OK用) | — |
| `\3c&HBBGGRR&` | 边框色 | `\3c&H00000000&` = 黑 |
| `\4c&HBBGGRR&` | 阴影色 | — |
| `\1a&HXX&` | 主色透明度 (00=不透明, FF=全透明) | `\1a&H80&` |

> ⚠️ ASS 颜色是 **BGR** 顺序, 不是 RGB!

### 边框与阴影
| 标签 | 说明 | 示例 |
|------|------|------|
| `\bord数值` | 边框宽度 | `\bord2` |
| `\shad数值` | 阴影距离 | `\shad0` |
| `\blur数值` | 高斯模糊(整数倍) | `\blur2` |
| `\be数值` | 边缘模糊 | `\be1` |

### 旋转与变换
| 标签 | 说明 | 示例 |
|------|------|------|
| `\frx数值` | X轴3D旋转 | `\frx360` |
| `\fry数值` | Y轴3D旋转 | `\fry360` |
| `\frz数值` | Z轴2D旋转 | `\frz360` |

### 裁切
| 标签 | 说明 |
|------|------|
| `\clip(x1,y1,x2,y2)` | 矩形裁切(只显示区域内) |
| `\iclip(x1,y1,x2,y2)` | 反向裁切(隐藏区域内) |
| `\clip(drawing)` | 矢量裁切 |

### 动画
| 标签 | 说明 | 示例 |
|------|------|------|
| `\t(标签)` | 全时间段动画 | `\t(\frz360)` |
| `\t(t1,t2,标签)` | 定时动画 | `\t(0,500,\1c&HFF0000&)` |
| `\t(t1,t2,加速,标签)` | 加速动画 | `\t(0,500,0.5,\fscx200)` |
| `\fad(淡入ms,淡出ms)` | 淡入淡出 | `\fad(200,200)` |

### 绘图模式
| 标签 | 说明 |
|------|------|
| `\p1~\p6` | 开启绘图模式(数值=缩放倍数) |
| `\p0` | 关闭绘图模式 |

---

## 二、Karaoke Templater 语法

### Effect 字段关键字

| 类型 | 说明 |
|------|------|
| `code once` | 初始化代码(只执行一次) |
| `code syl` | 每音节执行的代码 |
| `code syl all` | 包含空白音节 |
| `template` | 模板行 |
| `template char` | 逐字符模板 |
| `template syl` | 逐音节模板 |
| `template noblank` | 跳过空白 |
| `template notext` | 只生成辅助(不生成文字) |
| `template loop N` | 循环N次 |
| `template fxgroup name` | 条件分组 |
| `template multi` | 多行匹配 |

### 内联表达式 `!expr!`

在模板行 Text 中用 `!` 包裹 Lua 表达式:

```
!retime("syl",0,0)!
!$center + math.random(-10,10)!
!math.floor($si/$syln * 255)!
```

### 常用函数

| 函数 | 说明 |
|------|------|
| `retime(mode, start_offset, end_offset)` | 重设时间轴 |
| `relayer(n)` | 设置图层号 |
| `maxloop(n)` | 设置最大循环数 |
| `_G.ass_color(R,G,B)` | 生成颜色字符串 |
| `_G.ass_alpha(a)` | 生成透明度字符串 |
| `remember(key, value)` | 记忆变量 |
| `recall.key` | 读取记忆变量 |
| `math.random(a,b)` | 随机整数 |
| `math.floor(x)` | 向下取整 |
| `math.sin/cos/pi` | 三角函数 |
| `string.format(fmt,...)` | 格式化字符串 |

### 时间轴变量

| 变量 | 含义 |
|------|------|
| `$sdur` | 当前音节时长(ms) |
| `$ldur` | 当前行时长(ms) |
| `$dur` | 当前处理单元时长 |
| `$si` | 音节索引(1-based) |
| `$syln` | 行内音节总数 |
| `j` | 当前 loop 迭代值 |
| `maxj` | loop 最大值 |

### 坐标变量

| 变量 | 含义 | 级别 |
|------|------|------|
| `$center` / `$middle` | 字符中心 | char |
| `$scenter` / `$smiddle` | 音节中心 | syl |
| `$sleft` / `$sright` | 音节左右边界 | syl |
| `$lleft` / `$lright` | 行左右边界 | line |
| `$top` / `$bottom` | 字符顶底 | char |
| `$width` / `$height` | 字符宽高 | char |
| `$swidth` / `$sheight` | 音节宽高 | syl |
| `$lwidth` / `$lheight` | 行宽高 | line |

---

## 三、常用 retime 模式速查

```
行时间轴: |========= 整行 =========|
音节:     |  syl1 | syl2 | syl3   |

retime("line", A, B)
  → [行开始+A, 行结束+B]

retime("syl", A, B)
  → [音节开始+A, 音节结束+B]

retime("syl2end", A, B)
  → [音节开始+A, 行结束+B]

retime("start2syl", A, B)
  → [行开始+A, 音节开始+B]

retime("postline", A, B)
  → [行结束+A, 行结束+B+offset]
```

---

## 四、Seekladoom K值字幕文件索引

在 `reference/Seekladoom-ASS-Effect-master/K值字幕文件/` 目录下有 **86个** 已打K值的原始字幕文件。

按风格分类:
- **燃曲合集** (40首): Bang Dream, DARLING in the FRANXX, 刀剑神域, 鬼灭之刃, 来自深渊...
- **可爱俏皮**: 天使降临, 贤惠幼妻仙狐小姐, 干物妹小埋...
- **抒情**: 紫罗兰永恒花园, 终将成为你, 恋如雨止, 比宇宙更远的地方...
- **其他**: 全金属狂潮, 游戏人生Zero, 钢之炼金术师...
