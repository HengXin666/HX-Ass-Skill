import os, shutil

dst = r'd:\command\Github\HX-Ass-Skill\reference\案例\Bravely You'
os.makedirs(dst, exist_ok=True)

shutil.copy2(
    r'C:\Users\Heng_Xin\Documents\Lyrics\Lia - Bravely You (28055813)_KFX.ass',
    os.path.join(dst, '成品_KFX.ass')
)
shutil.copy2(
    r'C:\Users\Heng_Xin\Documents\Lyrics\Lia - Bravely You (28055813).ass',
    os.path.join(dst, 'k帧.ass')
)
print('Copied successfully!')
