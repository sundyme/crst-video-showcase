# 部署到公司群晖 NAS（写给帮忙部署的 AI：Codex 或 Claude Code）

用户请你把这个仓库里的网页（「CRST 短片制作实录」和 Skill 介绍页）部署到公司内网的群晖 NAS，并让它以后自动更新。用户多半不懂代码：

- 全程用中文、大白话说明你在做什么。
- 能自己做的直接做。
- 需要用户在群晖网页后台（DSM）里点的，给出一步步的操作清单。

## 目标

- 同事在内网用 `http://<NAS 地址>/crst-video/` 打开短片实录，`http://<NAS 地址>/crst-video/skill/` 打开 Skill 介绍页，视频能播放。
- 这个仓库更新后，NAS 上的网页能自动跟上（每天至少一次）。

## 先问用户 / 先确认

1. **NAS 的内网地址**：IP 或名字，例如 `192.168.1.20`。用户不知道的话，请他在 DSM「控制面板 → 网络 → 网络界面」里查。
2. **Web Station 开了没有**：运行 `curl -sI http://<NAS 地址>/`。
   - 有 HTTP 响应（不是连接被拒）就是开了。
   - 没开的话，请用户在 DSM 里操作：
     1. 「套件中心」搜索 **Web Station**，安装。安装后会自动建好共享文件夹 **web**。
     2. 打开 Web Station，在「网页服务门户」里确认**默认服务器**启用（HTTP 80）。
     3. 开了防火墙的，在「控制面板 → 安全性 → 防火墙」里允许内网访问 80 端口。
3. **这台电脑能不能访问 NAS 的 web 共享文件夹**：
   - Mac：看 `/Volumes/web` 是否存在。
   - Windows：在 PowerShell 里运行 `Test-Path \\<NAS 地址>\web`。
   - 不能访问的话，请用户自己连上，你不要索要或代输密码：
     - Mac：访达 → 前往 → 连接服务器 → `smb://<NAS 地址>/web`
     - Windows：资源管理器地址栏输入 `\\<NAS 地址>\web`
4. **NAS 能不能访问外网（GitHub）**：不确定就先按路线 A 试；A 的首次运行失败，再改走路线 B。

## 路线 A（首选）：NAS 自己定时从 GitHub 更新

不依赖任何电脑开机。

1. **把同步脚本放到 web 共享文件夹，名字叫 `crst-video-sync.sh`**。直接从 GitHub 下载原文件，不要自己重新输入（必须保持 LF 换行，CRLF 会导致脚本在 NAS 上运行失败）：
   - Mac：`curl -fsSL https://raw.githubusercontent.com/sundyme/crst-video-showcase/main/deploy/sync_from_github.sh -o /Volumes/web/crst-video-sync.sh`
   - Windows：`curl.exe -fsSL https://raw.githubusercontent.com/sundyme/crst-video-showcase/main/deploy/sync_from_github.sh -o \\<NAS 地址>\web\crst-video-sync.sh`
2. **请用户在 DSM 里建定时任务**（你没法操作 DSM 网页后台）。把下面这份清单发给用户：
   1. 打开「控制面板 → 任务计划 → 新增 → 计划的任务 → 用户定义的脚本」。
   2. 常规：任务名填 `CRST 网页同步`，用户选 **root**。
   3. 计划：每天一次，例如 03:00。想更快同步可以选每小时。
   4. 任务设置 → 运行命令，填：`sh /volume1/web/crst-video-sync.sh`
      - web 文件夹不在 volume1 的，按 File Station 里 web 文件夹「属性」显示的位置改。
   5. 保存，在列表里选中这个任务，点「运行」，先执行一次。
3. 用户说运行过了，你做「验收」。第一次下载约 60 MB，等一两分钟再验收。打不开的话：
   - 请用户在任务计划里看这个任务的运行结果。
   - 如果是网络错误，说明 NAS 不能访问 GitHub，改走路线 B。

如果用户开了 SSH，并且愿意自己在终端里输入密码，也可以请他运行 `ssh <管理员账号>@<NAS 地址>`，登录后运行 `sudo sh /volume1/web/crst-video-sync.sh` 来手动执行一次。定时任务仍然建议在 DSM 的任务计划里建。

## 路线 B：由这台电脑推送到 NAS

适合 NAS 不能访问外网的情况。

1. **下载推送脚本并运行**。它会从 GitHub 下载最新网页，完整复制成 `crst-video.new`，检查后再替换旧的 `crst-video`：
   - 下载：`https://raw.githubusercontent.com/sundyme/crst-video-showcase/main/deploy/push_to_nas.py`，存到本机任意目录。
   - Mac：`python3 push_to_nas.py /Volumes/web`
   - Windows：`python push_to_nas.py \\<NAS 地址>\web`
     - 没有 `python`，或者弹出 Microsoft Store 时，依次试 `py -3`、`uv run --no-project python`。
2. **自动更新（先征得用户同意）**：在这台电脑上建一个每天运行的任务。注意这台电脑关机时不会更新。
   - Windows：`schtasks /Create /SC DAILY /ST 09:30 /TN "CRST 网页同步" /TR "<python 完整路径> <脚本完整路径> \\<NAS 地址>\web"`
   - Mac：用 `launchd`（`~/Library/LaunchAgents/` 下放一个 plist，`StartCalendarInterval` 设每天一次），或者 `crontab -e` 加一行。
   - 共享文件夹要在登录后自动连上：Windows 映射网络驱动器时勾选「登录时重新连接」；Mac 把服务器加入「登录项」。

## 验收

- `curl -s -o /dev/null -w "%{http_code}" http://<NAS 地址>/crst-video/`：应该是 200。
- `curl -s -o /dev/null -w "%{http_code}" http://<NAS 地址>/crst-video/skill/`：应该是 200。
- `curl -s -o /dev/null -w "%{http_code}" http://<NAS 地址>/crst-video/media/mistakes_h.mp4`：应该是 200。
- 最后把 `http://<NAS 地址>/crst-video/` 发给用户，告诉他可以转给同事。如果 IT 配了内网域名，用域名更好记。

## 出错时

| 现象 | 处理 |
|---|---|
| 打开的是群晖登录页 | 地址里带了 `:5000` 或 `:5001`。网页在 80 端口，地址不要带端口 |
| 403 | 请用户在 File Station 的 web 文件夹「属性 → 权限」里给 **http** 用户「读取」权限 |
| 404 | 确认 `web/crst-video/index.html` 存在；Web Station 默认服务器的根目录应是 web 共享文件夹 |
| 连接被拒或超时 | Web Station 没装 / 没启用，或者防火墙没放行 80 端口，见「先问用户」第 2 条 |
| 任务运行报 `$'\r': command not found` | 脚本被转成了 CRLF。按路线 A 第 1 步重新用 curl 下载覆盖 |
| Windows 上 `\\<NAS 地址>\web` 打不开 | 请用户在资源管理器里先打开一次并输入群晖账号密码，勾选「记住凭据」 |

## 规矩

- 不索要、不打印任何密码。需要登录时请用户自己在系统窗口或终端里输入。
- 只动 web 共享文件夹里的 `crst-video`、`crst-video.new`、`crst-video.old` 和 `crst-video-sync.sh`，不碰里面的其他东西。
- 除了上面写到的，不改群晖的其他设置。要改先问用户。
- 结束时给用户一个简短清单：
  - 网页地址；
  - 用的哪条路线；
  - 多久自动更新一次；
  - 用户还需要做什么。
