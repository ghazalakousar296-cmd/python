import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple

from flask import Flask, jsonify, render_template, request
from yt_dlp import YoutubeDL

from script import transcribe_audio


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DOWNLOAD_ROOT = BASE_DIR / "downloads"
DOWNLOAD_ROOT.mkdir(exist_ok=True)

FFMPEG_PATH = os.getenv(
    "FFMPEG_PATH",
    r"C:\ffmpeg\bin\ffmpeg.exe" if os.name == "nt" else "ffmpeg",
)

app = Flask(__name__)


def _download_video_audio(youtube_url: str) -> Tuple[Path, Path]:
    """
    Download the provided YouTube URL using yt-dlp and return the source file path and temp dir.
    """
    if not youtube_url:
        raise ValueError("You must provide a valid YouTube URL.")

    temp_dir = Path(tempfile.mkdtemp(dir=str(DOWNLOAD_ROOT)))
    ydl_opts = {
        "outtmpl": str(temp_dir / "%(title)s.%(ext)s"),
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        source_path = Path(ydl.prepare_filename(info))

    return source_path, temp_dir


def _convert_to_wav(source_path: Path) -> Path:
    """
    Use ffmpeg to convert the downloaded audio/video file into mono 16kHz WAV.
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Downloaded file is missing: {source_path}")

    wav_path = source_path.with_suffix(".wav")
    command = [
        FFMPEG_PATH,
        "-y",
        "-i",
        str(source_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(wav_path),
    ]

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        logger.error("ffmpeg failed: %s", completed.stderr)
        raise RuntimeError("Conversion to WAV failed. Check ffmpeg logs for details.")

    return wav_path


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/transcribe")
def transcribe_route():
    payload = request.get_json(silent=True) or {}
    youtube_url = payload.get("videoUrl")
    logger.info("Received transcription request for URL: %s", youtube_url)

    if not youtube_url:
        return jsonify({"error": "Missing videoUrl in request body."}), 400

    source_path = None
    working_dir = None
    try:
        source_path, working_dir = _download_video_audio(youtube_url)
        wav_path = _convert_to_wav(source_path)
        transcription = transcribe_audio(str(wav_path))
        text_only = transcription.get("text") if isinstance(transcription, dict) else None

        return jsonify(
            {
                "text": text_only,
                "raw": transcription,
            }
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Transcription failed")
        return jsonify({"error": str(exc)}), 500
    finally:
        if working_dir and working_dir.exists():
            shutil.rmtree(working_dir, ignore_errors=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)

