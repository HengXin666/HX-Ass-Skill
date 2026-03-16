import codecs
path = r'd:\command\Github\HX-Ass-Skill\build_kfx_taisetsu.ps1'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
with open(path, 'w', encoding='utf-8-sig') as f:
    f.write(content)
print('Converted to UTF-8 BOM successfully')
