---
name: wechat-exporter
description: 完整爬取/导出微信公众号文章的工作流助手。当用户提到"下载微信公众号文章"、"爬取微信公众号文章"、"批量导出微信公众号"、"备份微信公众号内容"、"抓取微信公众号文章"、"保存微信公众号文章"时立即使用本 skill。无论用户说的是"爬"、"抓"、"导出"、"备份"还是"下载"，只要涉及微信公众号文章批量获取，都应触发本 skill。
---

# 微信公众号文章导出工作流

两种场景，选对路径：

| 场景 | 方案 |
|------|------|
| 用户给了具体文章 URL（`mp.weixin.qq.com/s/...`） | → 路径 A：curl + Python 直接抓取 |
| 批量导出整个公众号 / 多篇文章 | → 路径 B：wechat-article-exporter 在线工具 |

---

## 路径 A：单篇文章 URL → 直接下载转换

### 环境说明（已验证有效）

- **抓取**：用 `curl`（系统自带），加浏览器 User-Agent，能正常拿到微信文章 HTML
- **解析**：用 `python`（注意：Windows 上必须用 `python`，不能用 `python3`，后者是 Microsoft Store 占位符）
- **文件路径**：Windows 下 Python 无法访问 `/tmp/`，中间文件和输出文件都用实际 Windows 路径（如 `E:/test_file/`）
- **终端编码**：Windows 终端是 GBK，print 中文会乱码——直接写文件，用 `sys.stdout.buffer.write(...encode('utf-8'))` 输出状态

### 不可用的方法

- `WebFetch` 工具：`mp.weixin.qq.com` 被网络策略拦截，无法使用
- `var msg_title` 正则：当前微信 HTML 里已无此变量，提取不到标题

### 完整脚本（可直接复用）

**第一步：下载 HTML**

```bash
curl -sL --max-time 20 \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" \
  -H "Accept-Language: en-US,zh;q=0.9" \
  "https://mp.weixin.qq.com/s/ARTICLE_ID" > "OUTPUT_DIR/wechat_article.html"
```

**第二步：解析并转 Markdown**

```python
# 用 python（非 python3）执行
import re, sys

with open('OUTPUT_DIR/wechat_article.html', encoding='utf-8', errors='replace') as f:
    html = f.read()

# 标题：从 og:title meta 提取
title = 'wechat-article'
for pat in [r'property="og:title"\s+content="(.*?)"', r'content="(.*?)"\s+property="og:title"']:
    m = re.search(pat, html)
    if m:
        title = m.group(1).strip()
        break

# 正文：id="js_content" 区域
start = html.find('id="js_content"')
end = -1
for marker in ['id="js_content_blocked"', '<div class="rich_media_tool"', 'class="rich_media_extra_info"']:
    end = html.find(marker, start)
    if end != -1:
        break
content_html = html[start:end] if end != -1 else html[start:start+200000]

def html_to_md(s):
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = re.sub(r'<style[^>]*>.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<script[^>]*>.*?</script>', '', s, flags=re.S)
    for n in range(6, 0, -1):
        s = re.sub(rf'<h{n}[^>]*>(.*?)</h{n}>', lambda m, n=n: '\n' + '#'*n + ' ' + re.sub(r'<[^>]+>', '', m.group(1)).strip() + '\n', s, flags=re.S)
    s = re.sub(r'<strong[^>]*>(.*?)</strong>', lambda m: '**' + re.sub(r'<[^>]+>', '', m.group(1)) + '**', s, flags=re.S)
    s = re.sub(r'<b[^>]*>(.*?)</b>', lambda m: '**' + re.sub(r'<[^>]+>', '', m.group(1)) + '**', s, flags=re.S)
    s = re.sub(r'<em[^>]*>(.*?)</em>', lambda m: '*' + re.sub(r'<[^>]+>', '', m.group(1)) + '*', s, flags=re.S)
    s = re.sub(r'<pre[^>]*>(.*?)</pre>', lambda m: '\n```\n' + re.sub(r'<[^>]+>', '', m.group(1)).strip() + '\n```\n', s, flags=re.S)
    s = re.sub(r'<code[^>]*>(.*?)</code>', lambda m: '`' + re.sub(r'<[^>]+>', '', m.group(1)) + '`', s, flags=re.S)
    s = re.sub(r'<a[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>', lambda m: '[' + re.sub(r'<[^>]+>', '', m.group(2)) + '](' + m.group(1) + ')', s, flags=re.S)
    def img_to_md(m):
        mm = re.search(r'(?:data-src|src)=["\']([^"\']+)["\']', m.group(0), flags=re.S)
        return '![](' + mm.group(1).strip() + ')' if mm else ''
    s = re.sub(r'<img\b[^>]*>', img_to_md, s, flags=re.S)
    s = re.sub(r'<li[^>]*>(.*?)</li>', lambda m: '- ' + re.sub(r'<[^>]+>', '', m.group(1)).strip(), s, flags=re.S)
    s = re.sub(r'<[uo]l[^>]*>', '', s)
    s = re.sub(r'</[uo]l>', '\n', s)
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<p[^>]*>(.*?)</p>', lambda m: '\n' + re.sub(r'<[^>]+>', '', m.group(1)).strip() + '\n', s, flags=re.S)
    s = re.sub(r'<section[^>]*>', '\n', s)
    s = re.sub(r'</section>', '\n', s)
    s = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', lambda m: '\n> ' + re.sub(r'<[^>]+>', '', m.group(1)).strip().replace('\n', '\n> ') + '\n', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    s = s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&nbsp;', ' ').replace('&#39;', "'")
    s = s.replace('•', '-')
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()

md = html_to_md(content_html)

# 清理残留的 HTML 属性碎片和 id="js_content" 开头行
md = re.sub(r'^id="js_content"[^\n]*\n\n?', '', md)
md = re.sub(r'(!\[[^\]]*\]\([^)]+\))\s+[^!\[\n]*(?:px|em|%)[^!\[\n]*[">]+', r'\1\n', md)
md = re.sub(r"!\[\]\((https?://[^\s\"')>]+)[^)\n]*(?:\)|>)", r'![](\1)', md)

# 清理文章头尾的元信息行。只处理边缘连续区块，避免误删正文中提到的作者、来源、链接。
# 注意：Markdown 输出只允许标题和正文；不要从 meta 或页面头部主动写入作者、来源、原文、发布时间等字段。
def is_edge_meta_line(line):
    t = line.strip()
    t = re.sub(r'^(?:[-*•]\s*)+', '', t)
    t = re.sub(r'^[>*_`\s]+|[>*_`\s]+$', '', t)
    return bool(
        re.match(r'^(?:来源|出处|原文|原文链接|文章链接|链接|作者|作\s*者|by|撰文|编辑|发布|发布日期|发布时间|日期|时间|公众号|公众号名|微信号)\s*[:：].*$', t, flags=re.I)
        or re.match(r'^(?:作者|作\s*者|by|撰文|编辑|来源|出处|公众号)\s*[|/／｜].*$', t, flags=re.I)
        or re.match(r'^(?:[^\w\s])?\s*https?://mp\.weixin\.qq\.com/s/\S+\s*$', t, flags=re.I)
    )

edge_lines = md.splitlines()
while edge_lines and (not edge_lines[0].strip() or is_edge_meta_line(edge_lines[0])):
    edge_lines.pop(0)
while edge_lines and (not edge_lines[-1].strip() or is_edge_meta_line(edge_lines[-1])):
    edge_lines.pop()
md = '\n'.join(edge_lines)

# 清理公众号常见文末宣传区（作者署名、关注二维码、引导互动、无关尾图）
def plain_line(line):
    t = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', line)
    return re.sub(r'[\s*_`"“”\'’‘「」『』【】\[\]（）()<>《》:：|｜/／、，。；;,.!！?-]+', '', t.strip())

def is_decorative_line(line):
    t = line.strip()
    return bool(t and re.match(r'^[\W_]+$', t) and not re.search(r'[\u4e00-\u9fffA-Za-z0-9]', t))

def is_short_footer_lead(line):
    p = plain_line(line)
    return bool(
        re.match(r'^\d{1,2}$', p)
        or re.match(r'^(?:0\d|[一二三四五六七八九十]{1,3})$', p)
        or re.search(r'(点击|下方|卡片|后台|对话|回复|私信|领取|关注|添加|扫码|长按)', p)
    )

def is_footer_promo_line(line):
    t = line.strip()
    p = plain_line(t)
    return bool(
        re.match(r'^@\s*作者\s*/', t)
        or re.search(r'(点赞|点个赞).*(在看|转发|分享|三连)', p)
        or re.search(r'(长按|扫码|扫描|识别).*(关注|公众号|二维码|加群|添加)', p)
        or re.search(r'(点击|下方|卡片).*(关注|公众号|微信|加群|领取)', p)
        or re.search(r'(关注|加入|添加).*(公众号|微信|社群|交流群|读者群|后台)', p)
        or re.search(r'(公众号|微信号|后台).*(回复|对话|聊天|领取|获取|关注)', p)
        or re.search(r'(历史发布|往期文章|更多内容).*(公众号|关注|后台|回复)', p)
        or ('希望本文能对你有所启发' in p)
        or ('也感谢你的点赞与分享' in p)
        or ('预览时标签不可点' in p)
    )

lines = md.splitlines()
footer_start = -1
for i, line in enumerate(lines):
    if is_footer_promo_line(line):
        footer_start = i
        # 文末推广常有“04”“点击下方卡片”这类短引导行在触发句之前。
        # 命中推广句后向上回退，连同这些引导行一起切掉。
        j = i - 1
        blanks = 0
        while j >= 0:
            prev = lines[j]
            if not prev.strip():
                blanks += 1
                if blanks <= 2:
                    j -= 1
                    continue
                break
            if is_decorative_line(prev) or is_short_footer_lead(prev):
                footer_start = j
                blanks = 0
                j -= 1
                continue
            break
        break
if footer_start != -1:
    lines = lines[:footer_start]

drop_line_pats = [
    r'^如果想要第一时间收到推送.*$',
    r'^如果你有更有趣的玩法.*$',
    r'^更多的内容正在不断填坑中.*$',
    r'^希望本文能对你有所启发.*$',
    r'^记得关注.*$',
    r'^.*长按.*扫码.*关注.*$',
    r'^.*扫码.*关注.*$',
    r'^.*识别.*二维码.*$',
    r'^.*关注.*公众号.*$',
    r'^.*后台.*回复.*$',
    r'^.*后台.*对话.*$',
    r'^.*点击.*下方.*卡片.*$',
    r'^.*点.*赞.*在看.*$',
    r'^.*点赞.*分享.*$',
    r'^.*三连.*$',
    r'^也感谢你的点赞与分享.*$',
    r'^预览时标签不可点.*$',
]
lines = [
    line for line in lines
    if not is_decorative_line(line) and not any(re.match(p, plain_line(line)) for p in drop_line_pats)
]

while lines and (not lines[-1].strip() or is_decorative_line(lines[-1]) or re.match(r'^[*\-_\s]+$', lines[-1].strip())):
    lines.pop()
while lines and re.match(r'^!\[[^\]]*\]\([^)]+\)$', lines[-1].strip()):
    lines.pop()
    while lines and (not lines[-1].strip() or is_decorative_line(lines[-1]) or re.match(r'^[*\-_\s]+$', lines[-1].strip())):
        lines.pop()

md = '\n'.join(lines)
md = re.sub(r'\n{3,}', '\n\n', md).strip()

output = f'# {title}\n\n{md}\n'

with open('OUTPUT_DIR/article.md', 'w', encoding='utf-8') as f:
    f.write(output)

sys.stdout.buffer.write(f'DONE len={len(output)}\n'.encode('utf-8'))
```

**关键注意事项**：
- 将 `OUTPUT_DIR` 替换为实际 Windows 路径（如 `E:/test_file`）
- 将 `ARTICLE_ID` 替换为实际文章 ID
- 微信图片 URL 有时效性（数天），需要长期保存时单独下载图片
- 如果需要本地化图片，只从清理后的 Markdown 提取图片 URL；不要从原始 DOM 图片列表直接下载，避免保存已剔除的文末关注二维码、互动引导图等尾部推广内容
- 输出 Markdown 默认只保留标题和正文，不主动添加来源、原文链接、作者、发布时间等元信息；这些字段在不同文章中写法不固定，若出现在正文头尾，用通用边缘元信息规则清理

---

## 路径 B：批量导出整个公众号

使用开源工具 **wechat-article-exporter**（[GitHub](https://github.com/wechat-article/wechat-article-exporter)）。

### 使用在线版（零部署，推荐）

1. 打开 **https://down.mptext.top**
2. 用**微信公众平台账号**（非个人微信号）扫码登录
3. 搜索目标公众号，加载全部文章列表
4. 按需筛选（标题/作者/时间/原创/合集），或全选
5. 选择导出格式后批量下载

| 格式 | 适用场景 |
|------|---------|
| **HTML** | 100% 还原排版样式，带图片，**首选** |
| **Markdown** | Obsidian、Notion 等笔记软件 |
| **DOCX** | Word 编辑 |
| **Excel** | 元数据统计（标题/日期/阅读量） |
| **TXT / JSON** | 纯文本 / 结构化数据 |

### Docker 私有部署

```yaml
services:
  wechat-article-exporter:
    image: ghcr.io/wechat-article/wechat-article-exporter:latest
    ports:
      - "3000:3000"
    volumes:
      - ./data:/app/.data
    restart: always
```

```bash
docker compose up -d
# 访问 http://localhost:3000
```

### 获取评论和阅读量（进阶）

需抓包获取 Credentials（`__biz` / `key` / `uin` / `pass_ticket`）：

1. 安装 mitmproxy，配置手机代理
2. 手机微信打开目标公众号任意文章
3. 从 `mp.weixin.qq.com` 请求中提取上述四个参数
4. 在工具"设置 → Credentials"中填入

详见：https://docs.mptext.top/advanced/wxdown-service.html

---

## 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|---------|
| 扫码登录失败 | 用的是个人微信号 | 必须用公众平台账号（mp.weixin.qq.com）扫码 |
| 搜索不到公众号 | 公众号关闭了被搜索 | 无法通过此工具获取 |
| 加载文章很慢 | 文章多 + 接口频率限制 | 正常现象，工具自动续传 |
| HTML 图片不显示 | 微信图片链接过期 | 尽快下载，或在线打开 HTML |
| session expired | 登录会话超时 | 重新扫码 |
