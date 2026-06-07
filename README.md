<div align="center">

# DSY Skills

#### 我自己沉淀的一些 AI Skill，统一放在这里

[![Skills](https://img.shields.io/badge/Skills-1-10B981?style=for-the-badge)](#-skills)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)

![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square&logo=openai&logoColor=white)
![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square&logo=anthropic&logoColor=white)

</div>

这里的每个 Skill 都是 Agent 可以直接加载的结构化指令集。目标很简单：把已经跑通、可复用的做事方法沉淀下来，下次让 Agent 少走弯路。

---

## 目录

| 名字 | 一句话 |
| --- | --- |
| [**vide-download-project**](#vide-download-project) | 把视频下载能力迁移到其他项目：yt-dlp、平台识别、cookies.txt、JSON 结果和错误分类 |

---

## 安装方式

在 Codex、Claude Code 等支持 Skill 的 Agent 里，直接说：

```text
帮我安装这个 skill：https://github.com/DSY-Xueai/DSY-skills/tree/main/vide-download-project
```

也可以手动 clone 后，把需要的 skill 目录复制到本地 skills 目录。

---

## Skills

### vide-download-project

> 把 Vide Download 项目里已经沉淀好的下载边界，复用到新的代码库里。

这个 Skill 适合在新项目里实现、迁移或修复视频下载能力。它不追求做完整应用，只抽取核心下载域：URL 平台识别、可选 cookies.txt、yt-dlp 下载参数、字幕处理、标准 JSON 返回值和稳定错误码。

**它能做什么**

- 根据 URL hostname 或强制平台参数识别平台。
- 使用 yt-dlp 下载单个视频，避免误展开 playlist。
- 优先输出 1080p 以内、兼容性更好的 H.264/AAC MP4。
- 支持调用方传入自己的 `cookies.txt`，不内置任何真实 cookies。
- 将登录、风控、cookie 过期等问题归类成稳定错误码，方便上层 UI 或 API 处理。
- 提供可直接复用的 Python downloader 脚本和测试。

**适合**

- 给已有 App 增加视频下载能力。
- 把 Vide Download 项目的下载逻辑迁移到另一个代码库。
- 修复 yt-dlp 下载边界、平台识别、cookie 错误分类、JSON 输出格式。

**怎么触发**

```text
用 vide-download-project 帮我实现一个视频下载模块
把这个项目的视频下载能力接入 yt-dlp
修一下下载失败时 cookies 过期的错误分类
给现有 downloader 加平台识别和 JSON 返回
```

**运行要求**

```powershell
python -m pip install -U yt-dlp
```

如果需要合并音视频或转码，主机还需要安装 `ffmpeg` 并加入 `PATH`。

**文件入口**

→ [SKILL.md](./vide-download-project/SKILL.md) · [实现指南](./vide-download-project/references/implementation-guide.md) · [平台表](./vide-download-project/references/platforms.md) · [下载脚本](./vide-download-project/scripts/video_downloader.py)

---

<div align="center">

Made by [@DSY-Xueai](https://github.com/DSY-Xueai)

</div>
