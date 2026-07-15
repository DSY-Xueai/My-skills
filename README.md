<div align="center">

#  DSY Skills

#### 可安装到 Codex、Claude Code 等 Agent 里的 Skill 集合。

[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)

![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square&logo=openai&logoColor=white)
![OpenCode](https://img.shields.io/badge/OpenCode-Skill-3B82F6?style=flat-square)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-8B5CF6?style=flat-square)

</div>

## Skills

| Skill | 功能 |
| --- | --- |
| VidGrab | 让 Agent 帮你处理视频下载任务，包括解析链接、调用 yt-dlp、处理 cookies、字幕和下载失败问题。 |
| wechat-exporter | 让 Agent 导出微信公众号文章，支持单篇链接转 Markdown，以及通过 wechat-article-exporter 批量备份公众号内容。 |

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
## wechat-exporter

wechat-exporter 是一个微信公众号文章导出 Skill。安装后，你可以让 Agent 将单篇公众号文章保存为 Markdown，或通过 wechat-article-exporter 批量导出公众号历史文章。

### 能做什么

- 将单篇微信公众号文章转换为 Markdown
- 清理文章头尾元信息和文末推广内容
- 批量导出公众号历史文章
- 支持 HTML、Markdown、DOCX、Excel、TXT 和 JSON 格式
- 说明微信图片链接时效和本地化保存方式
- 排查扫码登录、公众号搜索和会话失效问题

### 适合这样说

```text
把这篇微信公众号文章保存成 Markdown：<url>
帮我批量导出这个公众号的历史文章
帮我备份微信公众号内容
这个公众号导出失败了，帮我判断原因
```
