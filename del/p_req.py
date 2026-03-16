import urllib.request, urllib.parse, json, time, os
from concurrent.futures import ThreadPoolExecutor, as_completed

PID_FILE = 'sent_pids.txt'  # 已发送PID记录文件(持久化去重)

# 读取历史PID
try:
    with open(PID_FILE, 'r') as f:
        sent_pids = set(line.strip() for line in f if line.strip())
except:
    sent_pids = set()
print(f'历史PID: {len(sent_pids)}条')

# ===== 配置区 =====
TAGS = ['loli', '貧乳', '小桃']    # 修改tag, 日文效果最好
R18 = 1                     # 0=非R18  1=R18  2=混合
NUM_WANT = 16               # 想要几张
SIZE_LIMIT = 5 * 1024 * 1024  # 5MB, 企业微信5MB+收不到
OUT_DIR = '/tmp'            # 输出目录
# =================

candidates = []
for _ in range(10):
    if len(candidates) >= NUM_WANT * 3:
        break
    try:
        params = urllib.parse.urlencode({
            'r18': R18, 'num': 20,
            'tag': TAGS,
            'excludeAI': 'false'
        }, doseq=True)
        req = urllib.request.Request(
            f'https://api.lolicon.app/setu/v2?{params}',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
        new = 0
        for item in data['data']:
            pid = str(item['pid'])
            if pid not in sent_pids and not any(c['pid'] == pid for c in candidates):
                candidates.append({
                    'pid': pid,
                    'url': item['urls']['original'],
                    'ext': item['ext']
                })
                new += 1
        print(f'API批次: +{new}张 (总候选 {len(candidates)})')
    except Exception as e:
        print(f'API err: {e}')
    time.sleep(0.3)

print(f'候选共: {len(candidates)}张')


def download(item, idx):
    path = os.path.join(OUT_DIR, f'img_{idx}.{item["ext"]}')
    try:
        req = urllib.request.Request(item['url'], headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.pixiv.net/'
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            chunks = []
            total = 0
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                total += len(chunk)
                if total > SIZE_LIMIT:
                    return None, item['pid'], f'SKIP {total // 1024}K (too large)'
                chunks.append(chunk)
            raw = b''.join(chunks)
        with open(path, 'wb') as f:
            f.write(raw)
        return path, item['pid'], f'OK {total // 1024}K'
    except Exception as e:
        return None, item['pid'], f'FAIL {e}'


saved = []
used_pids = []
with ThreadPoolExecutor(max_workers=8) as ex:
    futures = {ex.submit(download, c, i + 1): c for i, c in enumerate(candidates)}
    for fut in as_completed(futures):
        path, pid, msg = fut.result()
        print(f'{msg}  pid={pid}')
        if path:
            real_idx = len(saved) + 1
            final = os.path.join(OUT_DIR, f'final_{real_idx}.{futures[fut]["ext"]}')
            os.rename(path, final)
            saved.append((pid, final))
            used_pids.append(pid)
        if len(saved) >= NUM_WANT:
            break

# 更新PID记录
all_pids = sent_pids | set(used_pids)
with open(PID_FILE, 'w') as f:
    for pid in all_pids:
        f.write(pid + '\n')

print(f'\nDONE: {len(saved)} 张, 历史总记录: {len(all_pids)}')
for pid, path in saved:
    print(f'FILE: {path}')
