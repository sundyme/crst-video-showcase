# CRST 短片制作实录 · 网页

展示页和 skill 介绍页的静态网页，用 GitHub Pages 发布。

- 展示页：`index.html`
- Skill 介绍页：`skill/index.html`

源文件在私有项目仓库的 `docs/showcase` 和 `docs/skill`，这里是发布用的副本，改动请在项目里改后重新同步。

## 部署到公司内网（群晖 NAS）

对 Codex 或 Claude Code 说：

> 按 https://github.com/sundyme/crst-video-showcase 里的 DEPLOY.md，把网页部署到公司群晖 NAS，并设置自动更新

AI 会照 [DEPLOY.md](DEPLOY.md) 一步步做，需要你在群晖后台点的地方会列清单给你。部署用的脚本在 `deploy/`。

同一套脚本也能把别的公开静态网页仓库部署到 NAS，例如：

> 按 https://github.com/sundyme/crst-video-showcase 里的 DEPLOY.md，把 https://github.com/sundyme/huashu-explainer 也部署到公司群晖 NAS，并设置自动更新
