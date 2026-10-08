#!/usr/bin/env python3
"""从 GitHub 下载一个静态网页仓库的最新版，复制到群晖 web 共享文件夹（Mac / Windows 通用，只用标准库）。
在一台能访问 GitHub、并且已经连上 NAS 共享文件夹的电脑上运行：

  python3 push_to_nas.py <web 共享文件夹路径> [GitHub 仓库 owner/名字] [web 里的文件夹名]
    Mac：     python3 push_to_nas.py /Volumes/web                       → CRST 短片实录，放到 web/crst-video/
    Windows： python push_to_nas.py \\\\192.168.1.20\\web                 （或映射的盘符，例如 Z:\\）
    别的仓库：python3 push_to_nas.py /Volumes/web sundyme/huashu-explainer huashu-explainer

仓库必须公开，首页是仓库根目录的 index.html。
先把新版完整复制成 <文件夹名>.new，检查无误后再替换旧版，网页不会出现更新到一半的状态。
"""
import io, re, shutil, sys, tarfile, time, urllib.request
from pathlib import Path

SKIP = {'README.md', '.nojekyll', 'DEPLOY.md', 'deploy', '.git', '.gitignore', '.gitattributes', '.github'}
# Google Fonts 在国内常连不上，会卡住首屏：改成后台加载，连不上就直接用系统字体
FONT_LINK = re.compile(rb'(<link[^>]*rel="stylesheet"[^>]*fonts\.googleapis\.com[^>]*)>')

def main():
    try: sys.stdout.reconfigure(errors='replace')   # Windows 控制台编码不支持的字符用 ? 代替，不报错
    except Exception: pass
    if len(sys.argv) < 2 or len(sys.argv) > 4: print(__doc__); sys.exit(2)
    web = Path(sys.argv[1])
    repo = sys.argv[2] if len(sys.argv) > 2 else 'sundyme/crst-video-showcase'
    name = sys.argv[3] if len(sys.argv) > 3 else 'crst-video'
    if not re.fullmatch(r'[\w.-]+/[\w.-]+', repo): print(f'仓库名不对：{repo}（格式 owner/名字）'); sys.exit(2)
    if not re.fullmatch(r'[\w-][\w.-]*', name): print(f'文件夹名不对：{name}'); sys.exit(2)
    if not web.is_dir(): print(f'找不到 {web}：先在访达 / 资源管理器里连上 NAS 的 web 共享文件夹'); sys.exit(1)
    url = f'https://codeload.github.com/{repo}/tar.gz/refs/heads/main'
    print(f'下载 {repo} 的最新网页…', flush=True)
    for i in range(3):
        try: data = urllib.request.urlopen(url, timeout=600).read(); break
        except Exception as e:
            if i == 2: print(f'下载失败：{e}'); sys.exit(1)
            time.sleep(5)
    new, dest, old = web / f'{name}.new', web / name, web / f'{name}.old'
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
            body = t.extractfile(m).read()
            if target.suffix == '.html': body = FONT_LINK.sub(lambda m: m.group(1) + b' media="print" onload="this.media=\'all\'">', body)
            target.write_bytes(body)
    if not (new / 'index.html').exists():
        print('下载的内容不完整（没有 index.html），没有更新'); shutil.rmtree(new, ignore_errors=True); sys.exit(1)
    if dest.exists(): dest.rename(old)
    new.rename(dest)
    shutil.rmtree(old, ignore_errors=True)
    n = sum(1 for _ in dest.rglob('*') if _.is_file())
    print(f'已更新 {dest}（{n} 个文件，{time.strftime("%Y-%m-%d %H:%M")}）')

if __name__ == '__main__':
    main()
