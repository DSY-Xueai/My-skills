<div align="center">

# DSY Skills

#### AI Agent 可直接加载的实用 Skill

[![Skills](https://img.shields.io/badge/Skills-1-10B981?style=for-the-badge)](#-skills)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)

![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square&logo=openai&logoColor=white)
![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square&logo=anthropic&logoColor=white)

</div>

这里收集的是可直接安装到 Codex、Claude Code 等 Agent 里的 Skill。每个 Skill 都只保留完成任务所需的指令、脚本和参考资料。

---

## 目录

| 名字 | 一句话 |
| --- | --- |
| [**VidGrab**](#vidgrab) | 帮 Agent 实现、接入或修复视频下载功能 |

---

## 安装方式

在 Codex、Claude Code 等支持 Skill 的 Agent 里，直接说：

```text
帮我安装这个 skill：https://github.com/DSY-Xueai/DSY-skills/tree/main/VidGrab
```

也可以手动 clone 后，把需要的 skill 目录复制到本地 skills 目录。

---

## Skills

### VidGrab

> 让 Agent 能稳定处理视频下载相关开发任务。

VidGrab 用于实现、接入或修复视频下载功能。它提供一个清晰的下载器约定，并附带可复用的 Python 脚本，适合需要 `yt-dlp`、平台识别、登录 cookies、字幕处理和结构化返回结果的项目。

**它能做什么**

- 识别 YouTube、Bilibili、抖音、小红书、微博、X/Twitter 等常见视频平台。
- 使用 `yt-dlp` 下载单个视频，并避免误下载整个播放列表。
- 优先生成兼容性更好的 MP4 文件，适配常见播放器。
- 下载可用字幕，转换为 SRT，并在条件允许时嵌入 MP4。
- 支持调用方传入自己的 `cookies.txt`，用于登录或风控场景。
- 返回统一 JSON 结果，包含状态、文件路径、错误码和警告信息。
- 将登录失效、平台拦截、超时、系统错误等失败原因归类，方便上层处理。

**适合**

- 给桌面端、Web 后端或自动化工具增加视频下载功能。
- 统一下载任务的成功/失败返回格式。
- 处理平台识别、cookies、字幕、播放列表误展开等常见问题。
- 快速得到一个可运行的 Python 下载器，再按项目需要嵌入。

**怎么触发**

```text
用 VidGrab 帮我实现一个视频下载模块
给这个项目接入 yt-dlp 下载功能
修一下视频下载 cookies 失效时的错误分类
给现有 downloader 加平台识别和 JSON 返回
```

**运行要求**

```powershell
python -m pip install -U yt-dlp
```

如果需要合并音视频或转码，主机还需要安装 `ffmpeg` 并加入 `PATH`。

**文件入口**

→ [SKILL.md](./VidGrab/SKILL.md) · [实现指南](./VidGrab/references/implementation-guide.md) · [平台表](./VidGrab/references/platforms.md) · [下载脚本](./VidGrab/scripts/video_downloader.py)

---

<div align="center">

Made by [@DSY-Xueai](https://github.com/DSY-Xueai)

</div>
