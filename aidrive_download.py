import urllib.request, json, time
from pathlib import Path

API_KEY = "gsk-eyJjb2dlbl9pZCI6Ijg2NGI1NWZiLTFjOWQtNGFhYS04MTcyLWZiZTRmZmNkNjQyNSIsImtleV9pZCI6IjVlNjg2NGQ3LTUxZDItNDMyNy1hYzcwLTRjNzFiOWU4YTk5ZSIsImN0aW1lIjoxNzc1NDgzNTM0LCJjbGF1ZGVfYmlnX21vZGVsIjpudWxsLCJjbGF1ZGVfbWlkZGxlX21vZGVsIjpudWxsLCJjbGF1ZGVfc21hbGxfbW9kZWwiOm51bGx9fAslRuQHD6yWBe7ZCVlaBZWJTtmr0LQ6Fqffl60XRTHg"
BASE_URL = "https://www.genspark.ai/api/tool_cli/aidrive"
SAVE_DIR = Path.home() / "Desktop" / "aidrive_backup"

def api(action, **kwargs):
    body = json.dumps({"action": action, **kwargs}).encode()
    req = urllib.request.Request(BASE_URL, data=body,
        headers={"X-Api-Key": API_KEY,
                 "Content-Type": "application/json"})
    try:
        res = urllib.request.urlopen(req, timeout=30)
        return json.loads(res.read())
    except Exception as e:
        print(f"  APIエラー: {e}")
        return None

def get_url(path):
    d = api("get_readable_url", path=path)
    if not d:
        return None
    result = d.get("data", {}).get("result", "")
    for line in result.split("\n"):
        if line.startswith("http"):
            return line.strip()
    return None

def ls(path):
    d = api("ls", path=path)
    if not d:
        return []
    result = d.get("data", {}).get("result", "")
    items = []
    for line in result.split("\n"):
        if " | " in line and not line.startswith("Name"):
            parts = [p.strip() for p in line.split(" | ")]
            if len(parts) >= 2:
                items.append({"name": parts[0], "type": parts[1]})
    return items

def download(url, path):
    try:
        urllib.request.urlretrieve(url, path)
        return True
    except Exception as e:
        print(f"  DLエラー: {e}")
        return False

def walk(remote, local):
    local.mkdir(parents=True, exist_ok=True)
    for item in ls(remote):
        name = item["name"]
        rpath = f"{remote}/{name}"
        lpath = local / name
        if item["type"] == "directory":
            print(f"📁 {rpath}")
            walk(rpath, lpath)
        else:
            if lpath.exists():
                print(f"  ⏭ {name}")
                continue
            print(f"  ⬇ {name} ...", end=" ", flush=True)
            url = get_url(rpath)
            if url and download(url, lpath):
                print(f"✅ {lpath.stat().st_size // 1024}KB")
            else:
                print("❌")
            time.sleep(0.3)

SAVE_DIR.mkdir(parents=True, exist_ok=True)
print(f"保存先: {SAVE_DIR}")
walk("", SAVE_DIR)
print("完了！")
