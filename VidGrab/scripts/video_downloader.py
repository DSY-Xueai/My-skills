from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PLATFORM_PATTERNS: dict[str, tuple[str, ...]] = {
    "youtube": (r"(^|\.)youtube\.com$", r"(^|\.)youtu\.be$"),
    "bilibili": (r"(^|\.)bilibili\.com$", r"(^|\.)b23\.tv$"),
    "xhs": (r"(^|\.)xiaohongshu\.com$", r"(^|\.)xhslink\.com$"),
    "dy": (r"(^|\.)douyin\.com$", r"(^|\.)v\.douyin\.com$"),
    "ks": (r"(^|\.)kuaishou\.com$",),
    "wb": (r"(^|\.)weibo\.com$", r"(^|\.)m\.weibo\.cn$", r"(^|\.)weibo\.cn$"),
    "tieba": (r"(^|\.)tieba\.baidu\.com$",),
    "zhihu": (r"(^|\.)zhihu\.com$", r"(^|\.)zhuanlan\.zhihu\.com$"),
    "qq": (r"(^|\.)v\.qq\.com$",),
    "iqiyi": (r"(^|\.)iqiyi\.com$", r"(^|\.)iq\.com$"),
    "youku": (r"(^|\.)youku\.com$",),
    "mgtv": (r"(^|\.)mgtv\.com$",),
    "xigua": (r"(^|\.)ixigua\.com$",),
    "twitter": (r"(^|\.)x\.com$", r"(^|\.)twitter\.com$"),
}

PLATFORM_ALIASES: dict[str, str] = {
    "yt": "youtube",
    "youtube": "youtube",
    "bili": "bilibili",
    "bilibili": "bilibili",
    "xhs": "xhs",
    "douyin": "dy",
    "dy": "dy",
    "kuaishou": "ks",
    "ks": "ks",
    "weibo": "wb",
    "wb": "wb",
    "tieba": "tieba",
    "zhihu": "zhihu",
    "qq": "qq",
    "tencentvideo": "qq",
    "iqiyi": "iqiyi",
    "qiyi": "iqiyi",
    "youku": "youku",
    "mgtv": "mgtv",
    "mangotv": "mgtv",
    "xigua": "xigua",
    "twitter": "twitter",
    "x": "twitter",
}

MEDIA_EXTS = {".mp4", ".mov", ".mkv", ".flv", ".webm", ".m4v", ".mp3", ".m4a", ".aac", ".wav"}


def _host(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or parsed.netloc or "").lower().strip()
    return host[4:] if host.startswith("www.") else host


def detect_platform(url: str, forced_platform: str | None = None) -> str | None:
    if forced_platform:
        platform = PLATFORM_ALIASES.get(forced_platform.strip().lower())
        if platform:
            return platform

    host = _host(url)
    for platform, patterns in PLATFORM_PATTERNS.items():
        if any(re.search(pattern, host) for pattern in patterns):
            return platform
    return None


def _media_snapshot(output_dir: Path) -> dict[Path, float]:
    if not output_dir.exists():
        return {}
    return {
        path.resolve(): path.stat().st_mtime
        for path in output_dir.iterdir()
        if path.is_file() and path.suffix.lower() in MEDIA_EXTS
    }


def _newest_media_file(output_dir: Path, before: dict[Path, float]) -> str | None:
    candidates = []
    for path in output_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in MEDIA_EXTS:
            continue
        resolved = path.resolve()
        mtime = path.stat().st_mtime
        if resolved not in before or mtime > before[resolved]:
            candidates.append((mtime, resolved))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return str(candidates[0][1])


def _subtitle_file_for(video_file: str) -> Path | None:
    video_path = Path(video_file)
    candidates = [
        path
        for path in video_path.parent.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".srt"
        and path.name.startswith(video_path.stem)
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda path: ("-orig" in path.name.lower(), len(path.name)))
    return candidates[0]


def _embed_subtitle(video_file: str, subtitle_file: Path, warnings: list[str]) -> str:
    if not shutil.which("ffmpeg"):
        warnings.append("Subtitle embedding skipped: ffmpeg was not found.")
        return video_file

    video_path = Path(video_file)
    temp_path = video_path.with_name(f"{video_path.stem}.subtitled.tmp{video_path.suffix}")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(subtitle_file),
        "-map",
        "0",
        "-map",
        "1:0",
        "-c",
        "copy",
        "-c:s",
        "mov_text",
        "-metadata:s:s:0",
        "language=eng",
        str(temp_path),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        temp_path.replace(video_path)
    except Exception as exc:
        warnings.append(f"Subtitle embedding failed: {exc}")
        if temp_path.exists():
            temp_path.unlink()
    return str(video_path)


def _classify_error(message: str) -> str:
    lowered = message.lower()
    if any(token in lowered for token in ("sign in", "login", "cookie", "not a bot")):
        return "cookie_expired"
    if any(token in lowered for token in ("403", "forbidden", "risk", "blocked", "signature")):
        return "platform_blocked"
    if "timed out" in lowered or "timeout" in lowered:
        return "timeout"
    return "download_error"


def _result(
    *,
    platform: str | None,
    final_status: str,
    error_code: str | None,
    error_message: str | None,
    video_file: str | None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "platform": platform,
        "final_status": final_status,
        "error_code": error_code,
        "error_message": error_message,
        "video_file": video_file,
        "warnings": warnings or [],
    }


def download_video(
    url: str,
    *,
    output_dir: str,
    forced_platform: str | None = None,
    cookie_file: str | None = None,
) -> dict[str, Any]:
    platform = detect_platform(url, forced_platform)
    if not platform:
        return _result(
            platform=None,
            final_status="failed",
            error_code="unsupported_url",
            error_message=f"Unsupported URL: {url}",
            video_file=None,
        )

    try:
        import yt_dlp
    except ImportError as exc:
        return _result(
            platform=platform,
            final_status="failed",
            error_code="system_error",
            error_message=str(exc),
            video_file=None,
        )

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    before = _media_snapshot(out_dir)
    outtmpl = str(out_dir / "%(title).180B.%(ext)s")

    warnings: list[str] = []
    ydl_opts: dict[str, Any] = {
        "format": (
            "bestvideo[vcodec^=avc1][height<=1080]+bestaudio[acodec^=mp4a]/"
            "bestvideo[vcodec^=avc1][height<=1080]+bestaudio/"
            "best[ext=mp4][vcodec^=avc1][acodec^=mp4a][height<=1080]/"
            "best[height<=1080]/best"
        ),
        "outtmpl": outtmpl,
        "merge_output_format": "mp4",
        "postprocessor_args": {"ffmpeg": ["-c:v", "libx264", "-c:a", "aac"]},
        "noplaylist": True,
        "concurrent_fragment_downloads": 8,
        "fragment_retries": 5,
        "retries": 3,
        "socket_timeout": 30,
        "quiet": True,
        "no_warnings": False,
    }
    if cookie_file:
        ydl_opts["cookiefile"] = str(Path(cookie_file).expanduser().resolve())

    ydl_opts["logger"] = _WarningLogger(warnings)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
    except Exception as exc:
        message = str(exc)
        return _result(
            platform=platform,
            final_status="failed",
            error_code=_classify_error(message),
            error_message=message,
            video_file=None,
            warnings=warnings,
        )

    video_file = _newest_media_file(out_dir, before)
    if not video_file:
        return _result(
            platform=platform,
            final_status="failed",
            error_code="download_error",
            error_message="No media file was produced.",
            video_file=None,
            warnings=warnings,
        )

    subtitle_opts: dict[str, Any] = {
        "skip_download": True,
        "outtmpl": outtmpl,
        "noplaylist": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en.*", "ko.*", "zh-Hans", "zh-Hant", "zh.*"],
        "subtitlesformat": "srt",
        "convertsubtitles": "srt",
        "quiet": True,
        "no_warnings": False,
        "logger": _WarningLogger(warnings),
    }
    if cookie_file:
        subtitle_opts["cookiefile"] = str(Path(cookie_file).expanduser().resolve())

    try:
        with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
            ydl.extract_info(url, download=True)
    except Exception as exc:
        warnings.append(f"Subtitle download failed: {exc}")

    subtitle_file = _subtitle_file_for(video_file)
    if subtitle_file:
        video_file = _embed_subtitle(video_file, subtitle_file, warnings)

    return _result(
        platform=platform,
        final_status="succeeded",
        error_code=None,
        error_message=None,
        video_file=video_file,
        warnings=warnings,
    )


class _WarningLogger:
    def __init__(self, warnings: list[str]) -> None:
        self._warnings = warnings

    def debug(self, msg: str) -> None:
        return

    def info(self, msg: str) -> None:
        return

    def warning(self, msg: str) -> None:
        if msg:
            self._warnings.append(str(msg))

    def error(self, msg: str) -> None:
        if msg:
            self._warnings.append(str(msg))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Standalone yt-dlp video downloader.")
    parser.add_argument("url")
    parser.add_argument("--output-dir", default="downloads")
    parser.add_argument("--platform", dest="forced_platform")
    parser.add_argument("--cookies", dest="cookie_file")
    parser.add_argument("--json-output", action="store_true")
    args = parser.parse_args(argv)

    result = download_video(
        args.url,
        output_dir=args.output_dir,
        forced_platform=args.forced_platform,
        cookie_file=args.cookie_file,
    )

    if args.json_output:
        print(json.dumps(result, ensure_ascii=True))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["final_status"] == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
