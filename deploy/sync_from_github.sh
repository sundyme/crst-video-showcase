#!/bin/sh
# 在群晖上运行：从 GitHub 下载最新网页，更新到 Web Station 的 web 共享文件夹。
# 用法：放到群晖上，用 root 定时运行（DSM「控制面板 → 任务计划 → 用户定义的脚本」），例如：
#   sh /volume1/web/crst-video-sync.sh
# 可选环境变量：WEB（web 共享文件夹路径，默认 /volume1/web）
# 网页地址：http://<NAS 的 IP>/crst-video/
set -e
WEB=${WEB:-/volume1/web}
DEST=$WEB/crst-video
TMP=$WEB/.crst-video-tmp
URL=https://codeload.github.com/sundyme/crst-video-showcase/tar.gz/refs/heads/main

rm -rf "$TMP"; mkdir -p "$TMP"
curl -fsSL --retry 3 --max-time 600 "$URL" | tar -xz -C "$TMP"
SRC=$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -n 1)
[ -f "$SRC/index.html" ] && [ -f "$SRC/skill/index.html" ] || { echo "下载的内容不完整，没有更新"; rm -rf "$TMP"; exit 1; }
rm -rf "$SRC/README.md" "$SRC/.nojekyll" "$SRC/DEPLOY.md" "$SRC/deploy"   # 部署说明和脚本不放进网页目录
chmod -R a+rX "$SRC"
# 先换上新版，再删旧版，网页不会出现半更新状态
rm -rf "$DEST.old"
[ -d "$DEST" ] && mv "$DEST" "$DEST.old"
mv "$SRC" "$DEST"
rm -rf "$DEST.old" "$TMP"
echo "网页已更新：$(date '+%Y-%m-%d %H:%M')"
