---
name: vidgrab
description: Build, integrate, or repair video downloading features with yt-dlp, platform detection, caller-provided cookies.txt support, subtitle handling, normalized JSON results, and stable error classification.
---

# VidGrab

## Purpose

Use this skill to implement a focused video downloader. Cover URL platform detection, optional caller-provided cookies, yt-dlp configuration, subtitle handling, normalized JSON results, and stable error codes.

## Use The Bundled Resources

- Read `references/implementation-guide.md` before designing a new downloader.
- Read `references/platforms.md` when adding platform detection, aliases, cookies, or error handling.
- Reuse `scripts/video_downloader.py` as the minimal standalone downloader when Python + yt-dlp is acceptable.

## Runtime Requirements

For the bundled script or a Python implementation:

```powershell
python -m pip install -U yt-dlp
```

Install `ffmpeg` on the host and make it available on `PATH` when merged audio/video output is required.

## Minimal Architecture

Implement the download feature as a small boundary:

1. Accept `url`, optional `forced_platform`, optional `cookie_file`, and `output_dir`.
2. Detect the platform from the hostname or forced platform alias.
3. Download with yt-dlp using safe defaults:
   - single-video mode;
   - no playlist expansion;
   - 1080p-or-lower compatible H.264/AAC MP4 output;
   - available subtitles/auto subtitles saved as SRT and embedded into MP4;
   - concurrent fragment downloads;
   - UTF-8 JSON output.
4. Return a normalized result object:
   - `platform`
   - `final_status`: `succeeded` or `failed`
   - `error_code`
   - `error_message`
   - `video_file`
   - `warnings`

## Cookie Strategy

- Do not bundle any real `cookies.txt` from the source project or local machine.
- Accept cookies only as an optional caller-provided file path, preferably Netscape `cookies.txt`.
- Let the user of the skill provide and refresh their own cookies.
- Treat login, bot-check, expired cookie, and cookie-required failures as `cookie_expired` so the caller knows cookies may need to be supplied or refreshed.

## Verification

For the bundled script:

```powershell
python scripts/video_downloader.py --help
```

For a real download smoke test:

```powershell
python scripts/video_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir downloads --json-output
```

Use a known public test URL when possible. Do not make live platform smoke tests part of deterministic CI because platform behavior and rate limits change.
