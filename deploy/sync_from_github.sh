#!/bin/sh
# 在群晖上运行：从 GitHub 下载一个静态网页仓库的最新版，更新到 Web Station 的 web 共享文件夹。
# 用法：放到群晖的 web 文件夹，命名为 site-sync.sh，用 root 定时运行（DSM「控制面板 → 任务计划 → 用户定义的脚本」）：
#   sh /volume1/web/site-sync.sh                                          → CRST 短片实录，http://<NAS>/crst-video/
#   sh /volume1/web/site-sync.sh sundyme/huashu-explainer huashu-explainer → http://<NAS>/huashu-explainer/
# 参数：[GitHub 仓库 owner/名字] [web 里的文件夹名]。可选环境变量：WEB（web 共享文件夹路径，默认 /volume1/web）、BRANCH（默认 main）
# 仓库必须公开，首页是仓库根目录的 index.html。
set -e
REPO=${1:-sundyme/crst-video-showcase}
NAME=${2:-crst-video}
WEB=${WEB:-/volume1/web}
BRANCH=${BRANCH:-main}
case "$NAME" in ""|*/*|.*) echo "文件夹名不对：$NAME"; exit 1;; esac
DEST=$WEB/$NAME
TMP=$WEB/.$NAME-tmp
URL=https://codeload.github.com/$REPO/tar.gz/refs/heads/$BRANCH

rm -rf "$TMP"; mkdir -p "$TMP"
curl -fsSL --retry 3 --max-time 600 "$URL" | tar -xz -C "$TMP"
SRC=$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -n 1)
[ -n "$SRC" ] && [ -f "$SRC/index.html" ] || { echo "下载的内容不完整（没有 index.html），没有更新"; rm -rf "$TMP"; exit 1; }
# 部署说明、脚本和仓库配置不放进网页目录
rm -rf "$SRC/README.md" "$SRC/.nojekyll" "$SRC/DEPLOY.md" "$SRC/deploy" "$SRC/.gitignore" "$SRC/.gitattributes" "$SRC/.github"
# Google Fonts 在国内常连不上，会卡住首屏：改成后台加载，连不上就直接用系统字体
find "$SRC" -name '*.html' -exec sed -i.bak 's#\(<link[^>]*rel="stylesheet"[^>]*fonts\.googleapis\.com[^>]*\)>#\1 media="print" onload="this.media='"'"'all'"'"'">#' {} +
find "$SRC" -name '*.html.bak' -exec rm -f {} +
chmod -R a+rX "$SRC"
# 先换上新版，再删旧版，网页不会出现半更新状态
rm -rf "$DEST.old"
[ -d "$DEST" ] && mv "$DEST" "$DEST.old"
mv "$SRC" "$DEST"
rm -rf "$DEST.old" "$TMP"
echo "$NAME 已更新：$(date '+%Y-%m-%d %H:%M')"
