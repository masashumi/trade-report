import urllib.request, json, time
from pathlib import Path

API_KEY = "gsk-eyJjb2dlbl9pZCI6Ijg2NGI1NWZiLTFjOWQtNGFhYS04MTcyLWZiZTRmZmNkNjQyNSIsImtleV9pZCI6IjVlNjg2NGQ3LTUxZDItNDMyNy1hYzcwLTRjNzFiOWU4YTk5ZSIsImN0aW1lIjoxNzc1NDgzNTM0LCJjbGF1ZGVfYmlnX21vZGVsIjpudWxsLCJjbGF1ZGVfbWlkZGxlX21vZGVsIjpudWxsLCJjbGF1ZGVfc21hbGxfbW9kZWwiOm51bGx9fAslRuQHD6yWBe7ZCVlaBZWJTtmr0LQ6Fqffl60XRTHg"
BASE = "https://www.genspark.ai/api/tool_cli/aidrive"
SAVE = Path.home() / "Desktop" / "aidrive_backup"
HDR  = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

def call(action, path):
    req = urllib.request.Request(BASE, json.dumps({"action":action,"path":path}).encode(), HDR)
    res = urllib.request.urlopen(req, timeout=30)
    return json.loads(res.read()).get("session_state", {}).get("aidrive_result", {})

def ls(path):
    return call("ls", path).get("files", [])

def get_url(path):
    return call("get_readable_url", path).get("readable_url")

def dl(url, dest):
    urllib.request.urlretrieve(url, dest)

def walk(rpath, lpath):
    lpath.mkdir(parents=True, exist_ok=True)
    for f in ls(rpath):
        name = f["name"]
        rp   = f["path"]
        lp   = lpath / name
        if f["type"] == "directory":
            print(f"📁 {rp}")
            walk(rp, lp)
        else:
            if lp.exists():
                print(f"  ⏭ {name}")
                continue
            print(f"  ⬇ {name} ...", end=" ", flush=True)
            try:
                url = get_url(rp)
                dl(url, lp)
                print(f"✅ {lp.stat().st_size//1024}KB")
            except Exception as e:
                print(f"❌ {e}")
            time.sleep(0.3)

SAVE.mkdir(parents=True, exist_ok=True)
print(f"保存先: {SAVE}")
walk("/", SAVE)
print("完了！")
