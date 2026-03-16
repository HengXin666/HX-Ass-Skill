import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
r = subprocess.run(
    ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
     r'd:\command\Github\HX-Ass-Skill\build_kfx_taisetsu.ps1'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print('STDOUT:', r.stdout[:3000])
print('STDERR:', r.stderr[:3000])
print('RC:', r.returncode)
