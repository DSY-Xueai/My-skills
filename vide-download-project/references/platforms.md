# Platforms

## Platform Detection

Use hostname matching. Strip `www.` before matching.

| Platform | Hosts |
| --- | --- |
| `youtube` | `youtube.com`, `youtu.be` |
| `bilibili` | `bilibili.com`, `b23.tv` |
| `xhs` | `xiaohongshu.com`, `xhslink.com` |
| `dy` | `douyin.com`, `v.douyin.com` |
| `ks` | `kuaishou.com` |
| `wb` | `weibo.com`, `m.weibo.cn`, `weibo.cn` |
| `tieba` | `tieba.baidu.com` |
| `zhihu` | `zhihu.com`, `zhuanlan.zhihu.com` |
| `qq` | `v.qq.com` |
| `iqiyi` | `iqiyi.com`, `iq.com` |
| `youku` | `youku.com` |
| `mgtv` | `mgtv.com` |
| `xigua` | `ixigua.com` |
| `twitter` | `x.com`, `twitter.com` |

## Forced Platform Aliases

Normalize aliases before routing:

| Alias | Platform |
| --- | --- |
| `yt` | `youtube` |
| `youtube` | `youtube` |
| `bili` | `bilibili` |
| `bilibili` | `bilibili` |
| `xhs` | `xhs` |
| `douyin`, `dy` | `dy` |
| `kuaishou`, `ks` | `ks` |
| `weibo`, `wb` | `wb` |
| `tieba` | `tieba` |
| `zhihu` | `zhihu` |
| `qq`, `tencentvideo` | `qq` |
| `iqiyi`, `qiyi` | `iqiyi` |
| `youku` | `youku` |
| `mgtv`, `mangotv` | `mgtv` |
| `xigua` | `xigua` |
| `twitter`, `x` | `twitter` |

## Practical Caveats

- YouTube may return bot/login challenges. Classify these as `cookie_expired` so callers know to update cookies.
- Twitter/X public videos may work without cookies, but private, age-limited, or risk-controlled content needs cookies.
- Mango TV often requires cookies.
- Iqiyi extraction can break when yt-dlp changes. If needed, isolate any monkey patch in a separate downloader adapter instead of spreading platform-specific fixes through the app.
- Douyin and Xiaohongshu often depend on fresh cookies. This skill only covers the `cookies.txt` path input.
