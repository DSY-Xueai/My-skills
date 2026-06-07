# DSY Skills

可安装到 Codex、Claude Code 等 Agent 里的 Skill 集合。

## Skills

| Skill | 功能 |
| --- | --- |
| VidGrab | 让 Agent 帮你处理视频下载任务，包括解析链接、调用 yt-dlp、处理 cookies、字幕和下载失败问题。 |

## 安装

在支持 Skill 的 Agent 里，直接说：

```text
帮我安装这个 skill：https://github.com/DSY-Xueai/DSY-skills/tree/main/<skill_name>
```

把 `<skill_name>` 换成要安装的 skill 目录名，例如 `VidGrab`。

## VidGrab

VidGrab 是一个视频下载 Skill。安装后，你可以让 Agent 根据视频链接完成下载、排查下载失败原因、处理需要 cookies 的平台，并输出结构化下载结果。

### 能做什么

- 下载公开视频链接
- 识别常见视频平台
- 处理需要登录 cookies 的下载任务
- 避免误下载整个播放列表
- 下载可用字幕
- 分析下载失败原因

### 适合这样说

```text
用 VidGrab 下载这个视频：<url>
这个视频下载失败了，帮我判断原因
给我的项目加一个视频下载功能
帮我用 cookies.txt 下载这个链接
```
