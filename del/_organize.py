# -*- coding: utf-8 -*-
"""整理根目录脚本：有用→案例，临时→del"""
import shutil, os

os.chdir(r'd:\command\Github\HX-Ass-Skill')

# === 有用脚本 → 案例文件夹 ===
moves_case = [
    ('build_kfx.ps1', 'reference/案例/羽ばたきのバースデイ/build_kfx.ps1'),
    ('build_kfx_innocent_blue.ps1', 'reference/案例/INNOCENT BLUE/build_kfx_innocent_blue.ps1'),
    ('build_kfx_taisetsu.ps1', 'reference/案例/大切がきこえる/build_kfx_taisetsu.ps1'),
    ('generate_habataki.py', 'reference/案例/羽ばたきのバースデイ/generate_habataki.py'),
    ('generate_taisetsu.py', 'reference/案例/大切がきこえる/generate_taisetsu.py'),
]

# === 临时/一次性脚本 → del ===
del_files = [
    '_analyze_ref.py',       # Bravely You 参考文件结构分析
    '_fix_encoding.py',      # 修 taisetsu ps1 编码
    '_run_build.py',         # 包装运行 taisetsu ps1
    '_tmp_calc.py',          # echo 时间计算草稿
    '_tmp_calc2.py',         # OPCN delay 计算草稿
    '_tmp_copy.py',          # 复制文件到案例
    '_tmp_final_verify.py',  # 输出验证
    '_tmp_info.py',          # 输出文件统计
    '_tmp_ref_opcn.py',      # 参考 OPCN 分析
    '_tmp_ref_opcn2.py',     # 参考 OPCN 分析2
    '_tmp_ref3.py',          # 参考 section3 分析
    '_tmp_ref4.py',          # 参考样式分析
    '_tmp_search.py',        # 搜索输入文件
    '_tmp_verify.py',        # OPCN 验证
    '_tmp_verify2.py',       # 输出验证2
    '_open_aegisub.ps1',     # 打开 Aegisub (绑定特定文件)
    'get_aegisub.ps1',       # 查 Aegisub 最新版
    'install_aegisub.ps1',   # 安装 Aegisub
    'list_aegisub.ps1',      # 列出 Aegisub 目录
    'p_req.py',              # Pixiv 图片下载器 (和项目无关)
]

os.makedirs('del', exist_ok=True)

print('=== 移动到案例文件夹 ===')
for src, dst in moves_case:
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f'  OK  {src} -> {dst}')
    else:
        print(f'  SKIP {src} (not found)')

print()
print('=== 移动到 del/ ===')
for f in del_files:
    if os.path.exists(f):
        shutil.move(f, os.path.join('del', f))
        print(f'  OK  {f} -> del/{f}')
    else:
        print(f'  SKIP {f} (not found)')

print('\nDONE!')
