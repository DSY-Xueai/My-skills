# Implementation Guide

## Goal

Build a reusable download module that can be embedded into any app. The transferable feature is only the downloader contract.

## Downloader Contract

Expose one function or command with these inputs:

- `url`: required source URL.
- `output_dir`: required directory for downloaded media.
- `forced_platform`: optional platform id or alias.
- `cookie_file`: optional cookies.txt path.
- `timeout_seconds`: optional process timeout if using a subprocess wrapper.

Return a dictionary or JSON object:

```json
{
  "platform": "youtube",
  "final_status": "succeeded",
  "error_code": null,
  "error_message": null,
  "video_file": "downloads/example.mp4",
  "warnings": []
}
```

Use `final_status = "succeeded"` only when a media file exists.

## Recommended yt-dlp Defaults

Use these defaults unless the target app has a clear reason to differ:

- `format`: prefer H.264/AAC MP4 at 1080p or lower, with fallback to best 1080p-or-lower media.
- `merge_output_format`: `mp4`
- `postprocessor_args`: use ffmpeg `-c:v libx264 -c:a aac` so fallback downloads are still broadly playable.
- `noplaylist`: `True`
- `concurrent_fragment_downloads`: `8`
- `fragment_retries`: `5`
- `retries`: `3`
- `socket_timeout`: `30`
- `writesubtitles`: `True`
- `writeautomaticsub`: `True`
- `subtitlesformat`: `srt`
- `convertsubtitles`: `srt`
- embed the first available SRT into the MP4 as `mov_text`, while keeping the external SRT file.
- `restrictfilenames`: `False`
- `quiet`: `True`
- `no_warnings`: `False`

For URL input that may include playlist parameters, single-video mode is important. Without it, a normal video link can accidentally expand into a playlist and make the download run far longer than expected.

The compatibility preference avoids AV1/Opus outputs that some default Windows players cannot decode.
Embedding SRT as an MP4 subtitle track avoids players missing external `.en.srt` files by default.

## File Detection

Do not depend only on yt-dlp's returned filename. Before download, snapshot existing media files in the output directory. After download, pick the newest created or modified media file.

Media extensions to consider:

`mp4`, `mov`, `mkv`, `flv`, `webm`, `m4v`, `mp3`, `m4a`, `aac`, `wav`

## Error Code Normalization

Normalize downloader/library errors into a small stable set:

- `unsupported_url`: platform detection failed.
- `cookie_expired`: login required, cookies missing/expired, bot checks, or cookie-specific auth failures.
- `platform_blocked`: 403, forbidden, risk control, signature expired, or platform block.
- `timeout`: subprocess or network timeout.
- `download_error`: yt-dlp ran but did not produce a valid media file.
- `system_error`: missing dependency, filesystem failure, import failure, or unexpected runtime error.

Keep the raw message in `error_message` for debugging.

## Cookies

Do not include real cookies in the skill. Users must provide their own `cookies.txt` when a platform requires login. The downloader should only accept a path and pass it to yt-dlp.
