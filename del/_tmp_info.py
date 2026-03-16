import os
f = r'C:\Users\Heng_Xin\Documents\Lyrics\Lia - Bravely You (28055813)_KFX.ass'
lines = open(f, 'r', encoding='utf-8-sig').read().splitlines()
print(f'Lines: {len(lines)}')
print(f'Size: {os.path.getsize(f)} bytes ({os.path.getsize(f)/1024:.1f} KB)')

# Count fx, Comment, echo, chant lines
fx_count = sum(1 for l in lines if ',fx,' in l)
comment_count = sum(1 for l in lines if l.startswith('Comment:'))
opjp_b = sum(1 for l in lines if ',OPJP-B,' in l)
opjp_a = sum(1 for l in lines if ',OPJP-A,' in l)
opjp_c = sum(1 for l in lines if ',OPJP-C,' in l)
opcn = sum(1 for l in lines if ',OPCN,' in l and ',fx,' in l)
opcn_a = sum(1 for l in lines if ',OPCN-A,' in l and ',fx,' in l)
opcn_c = sum(1 for l in lines if ',OPCN-C,' in l and ',fx,' in l)
furi = sum(1 for l in lines if ',OPJP-furigana,' in l)
print(f'FX lines: {fx_count}')
print(f'Comment lines: {comment_count}')
print(f'Echo (OPJP-B): {opjp_b}')
print(f'Chant JP (OPJP-A): {opjp_a}, (OPJP-C): {opjp_c}')
print(f'CN (OPCN): {opcn}')
print(f'CN chant (OPCN-A): {opcn_a}, (OPCN-C): {opcn_c}')
print(f'Furigana: {furi}')

# Count input file lines
fi = r'C:\Users\Heng_Xin\Documents\Lyrics\Lia - Bravely You (28055813).ass'
ilines = open(fi, 'r', encoding='utf-8-sig').read().splitlines()
orig = sum(1 for l in ilines if ',orig,' in l)
ts = sum(1 for l in ilines if ',ts,' in l)
print(f'\nInput file: {orig} orig, {ts} ts lines')
