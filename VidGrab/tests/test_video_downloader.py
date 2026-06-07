from __future__ import annotations

import importlib.util
import subprocess
import sys
import types
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "video_downloader.py"


def load_downloader():
    spec = importlib.util.spec_from_file_location("video_downloader", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_download_uses_compatible_mp4_audio_and_subtitle_options(tmp_path, monkeypatch):
    calls = []
    ffmpeg_calls = []

    class FakeYoutubeDL:
        def __init__(self, opts):
            self.opts = opts
            calls.append(opts)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def extract_info(self, url, download):
            if self.opts.get("skip_download"):
                (tmp_path / "video.en.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nhello\n", encoding="utf-8")
                return {"title": "video"}
            (tmp_path / "video.mp4").write_bytes(b"media")
            return {"title": "video"}

    def fake_run(cmd, check, capture_output, text):
        ffmpeg_calls.append(cmd)
        Path(cmd[-1]).write_bytes(b"embedded")
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setitem(sys.modules, "yt_dlp", types.SimpleNamespace(YoutubeDL=FakeYoutubeDL))
    monkeypatch.setattr("shutil.which", lambda name: "ffmpeg" if name == "ffmpeg" else None)
    monkeypatch.setattr("subprocess.run", fake_run)

    downloader = load_downloader()
    result = downloader.download_video("https://www.youtube.com/watch?v=E2YpAXiLRkg", output_dir=str(tmp_path))

    assert result["final_status"] == "succeeded"
    assert len(calls) == 2
    assert "vcodec^=avc1" in calls[0]["format"]
    assert "acodec^=mp4a" in calls[0]["format"]
    assert calls[0]["postprocessor_args"]["ffmpeg"] == ["-c:v", "libx264", "-c:a", "aac"]
    assert "writesubtitles" not in calls[0]
    assert calls[1]["skip_download"] is True
    assert calls[1]["writesubtitles"] is True
    assert calls[1]["writeautomaticsub"] is True
    assert calls[1]["subtitlesformat"] == "srt"
    assert ffmpeg_calls
    assert "-c:s" in ffmpeg_calls[0]
    assert "mov_text" in ffmpeg_calls[0]
    assert result["warnings"] == []
