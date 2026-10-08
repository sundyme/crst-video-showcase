#!/usr/bin/env python3
"""从 GitHub 下载最新网页，复制到群晖 web 共享文件夹里的 crst-video/（Mac / Windows 通用，只用标准库）。
在一台能访问 GitHub、并且已经连上 NAS 共享文件夹的电脑上运行：

  python3 deploy/push_to_nas.py <web 共享文件夹路径>
    Mac：     python3 deploy/push_to_nas.py /Volumes/web
    Windows： python deploy\\push_to_nas.py \\\\192.168.1.20\\web      （或映射的盘符，例如 Z:\\）

先把新版完整复制成 crst-video.new，检查无误后再替换旧的 crst-video，网页不会出现更新到一半的状态。
"""
import io, os, shutil, sys, tarfile, time, urllib.request
from pathlib import Path

URL = 'https://codeload.github.com/sundyme/crst-video-showcase/tar.gz/refs/heads/main'
SKIP = {'README.md', '.nojekyll', 'DEPLOY.md', 'deploy', '.git', '.gitignore'}

def main():
    try: sys.stdout.reconfigure(errors='replace')   # Windows 控制台编码不支持的字符用 ? 代替，不报错
    except Exception: pass
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    web = Path(sys.argv[1])
    if not web.is_dir(): print(f'找不到 {web}：先在访达 / 资源管理器里连上 NAS 的 web 共享文件夹'); sys.exit(1)
    print('下载最新网页…', flush=True)
    for i in range(3):
        try: data = urllib.request.urlopen(URL, timeout=600).read(); break
        except Exception as e:
            if i == 2: print(f'下载失败：{e}'); sys.exit(1)
            time.sleep(5)
    new, dest, old = web / 'crst-video.new', web / 'crst-video', web / 'crst-video.old'
    for p in (new, old):
        if p.exists(): shutil.rmtree(p)
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as t:
        for m in t.getmembers():
            parts = Path(m.name).parts[1:]   # 去掉 GitHub 包里的顶层目录
            if not parts or parts[0] in SKIP or not (m.isfile() or m.isdir()): continue
            if '..' in parts or Path(m.name).is_absolute(): continue
            target = new.joinpath(*parts)
            if m.isdir(): target.mkdir(parents=True, exist_ok=True); continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with t.extractfile(m) as src, open(target, 'wb') as out: shutil.copyfileobj(src, out)
    if not (new / 'index.html').exists() or not (new / 'skill' / 'index.html').exists():
        print('下载的内容不完整，没有更新'); shutil.rmtree(new, ignore_errors=True); sys.exit(1)
    if dest.exists(): dest.rename(old)
    new.rename(dest)
    shutil.rmtree(old, ignore_errors=True)
    n = sum(1 for _ in dest.rglob('*') if _.is_file())
    print(f'已更新 {dest}（{n} 个文件，{time.strftime("%Y-%m-%d %H:%M")}）')

if __name__ == '__main__':
    main()
