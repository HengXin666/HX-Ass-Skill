# HX-ASS-Skill

番剧主题 ASS 卡拉OK特效制作技能包。

## 简介

将 K 轴 ASS 歌词文件（日文 + 中文翻译 + 可选罗马音）转换为高质量的番剧主题 ASS 卡拉OK特效文件，支持振假名注音。输出为模板前状态，可直接在 Aegisub 中执行"应用卡拉OK模板"。

## 目录结构

```
hx-ass-skill/
├── SKILL.md                    # 技能说明文档
├── assets/                     # 资源文件
│   ├── 案例/                   # 制作案例（4个完整案例）
│   ├── music-ass/              # KFX参考作品
│   └── 素材库/                 # 可复用模板（8类）
├── references/                 # 参考文档
│   ├── 技术手册/               # ASS标签速查
│   ├── 知识库/                 # ASS特效知识库、振假名教程
│   └── 设计思想/               # OPED特效设计思路
└── scripts/                    # 辅助脚本
    ├── validate_kfx.py         # KFX验证器
    └── record_case.py          # 案例记录器
```

## 快速开始

1. 阅读 `hx-ass-skill/SKILL.md` 了解完整工作流程
2. 参考 `assets/案例/` 中的已有案例
3. 使用 `references/` 中的文档学习技术细节

## 作者

Heng_Xin

## 许可证

- [GNU 3.0 License](LICENSE)