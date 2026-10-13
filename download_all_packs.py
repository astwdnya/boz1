import os
import sys
import time
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACK_DIR = os.path.join(BASE_DIR, 'nacht', 'pack')
MANIFEST_PATH = os.path.join(BASE_DIR, 'nacht', 'manifest.json')
REMOTE_PACK_BASE = 'https://vel.gg/bo1z/nacht/pack/'

def get_pack_tasks():
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    tasks = []
    for entry in manifest['files']:
        path = entry['path']
        br = entry.get('br')

        if entry.get('opus'):
            parts = len(br) if isinstance(br, list) else len(br.split())
            for k in range(parts):
                tasks.append((path + '.kop', k))
        elif entry.get('dxs'):
            parts = len(br) if isinstance(br, list) else len(br.split())
            for k in range(parts):
                tasks.append((path + '.dxs', k))
        else:
            parts = len(br) if isinstance(br, list) else (len(br.split()) if isinstance(br, str) and br else 1)
            if parts > 1 or (isinstance(br, list) and len(br) == 1):
                for k in range(parts):
                    tasks.append((path, k))
            else:
                tasks.append((path, None))
    return tasks

def download_part_with_retry(task, max_retries=5):
    path, part = task
    if part is not None:
        filename = f"{path}.part{part}"
        url = f"{REMOTE_PACK_BASE}{path}?part={part}"
    else:
        filename = path
        url = f"{REMOTE_PACK_BASE}{path}"

    dest = os.path.join(PACK_DIR, filename)
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return f"[EXISTS] {filename} ({os.path.getsize(dest)} bytes)"

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                # Write to temp file then atomic rename
                tmp_dest = dest + '.tmp'
                with open(tmp_dest, 'wb') as out:
                    out.write(data)
                if os.path.exists(dest):
                    os.remove(dest)
                os.rename(tmp_dest, dest)
                return f"[OK] {filename} ({len(data)} bytes)"
        except Exception as e:
            if attempt < max_retries:
                time.sleep(1.5 * attempt)
            else:
                return f"[FAIL] {filename} (after {max_retries} attempts): {e}"

def main():
    os.makedirs(PACK_DIR, exist_ok=True)
    tasks = get_pack_tasks()
    print(f"Total parts to ensure: {len(tasks)}")

    # 4 workers to stay reliable against socket drops
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(download_part_with_retry, t): t for t in tasks}
        completed = 0
        failed_count = 0
        for f in as_completed(futures):
            completed += 1
            res = f.result()
            print(f"[{completed}/{len(tasks)}] {res}")
            if "[FAIL]" in res:
                failed_count += 1

    print("=" * 50)
    print(f"Finished: {completed} processed, {failed_count} failures.")

if __name__ == '__main__':
    main()
