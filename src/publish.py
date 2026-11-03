"""Copy a rendered set into posts/<id>/, push to GitHub, print image URLs and caption as JSON.

Usage: python3 src/publish.py <id>
Run after: python3 src/render.py content/<id>.json [--cover covers/<id>.png]
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], check=True, capture_output=True, text=True).stdout.strip()


def raw_base():
    url = git("remote", "get-url", "origin")
    m = re.search(r"github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$", url)
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    return f"https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{branch}"


def main():
    pid = sys.argv[1]
    src = ROOT / "out" / pid
    imgs = sorted(src.glob("[0-9][0-9].jpg"))
    if not imgs:
        sys.exit(f"렌더 결과 없음: {src}")
    dst = ROOT / "posts" / pid
    dst.mkdir(parents=True, exist_ok=True)
    for old in dst.glob("[0-9][0-9].jpg"):
        old.unlink()
    for f in imgs:
        shutil.copy(f, dst / f.name)
    shutil.copy(src / "caption.txt", dst / "caption.txt")
    git("add", f"posts/{pid}", f"content/{pid}.json")
    if git("status", "--porcelain", f"posts/{pid}", f"content/{pid}.json"):
        git("-c", "user.name=MELZZI bot", "-c", "user.email=noreply@anthropic.com", "commit", "-m", f"카드뉴스 {pid} 렌더링")
    git("pull", "--rebase", "origin", git("rev-parse", "--abbrev-ref", "HEAD"))
    git("push", "origin", "HEAD")
    sha = git("rev-parse", "--short", "HEAD")
    base = raw_base()
    urls = [f"{base}/posts/{pid}/{f.name}" for f in imgs]
    print(json.dumps({"id": pid, "commit": sha, "urls": urls,
                      "caption": (dst / "caption.txt").read_text(encoding="utf-8")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
