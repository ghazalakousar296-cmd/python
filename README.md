# Modern Video Transcriber

Web-based Flask application that downloads a YouTube video with `yt-dlp`, converts the media to high-quality audio via `ffmpeg`, and transcribes it with Groq's Whisper-large-v3-turbo model. The UI is built with Bootstrap and provides status updates plus copy-ready transcripts.

## Prerequisites

- Python 3.10+
- `ffmpeg` installed locally (default path assumed: `C:\ffmpeg\bin\ffmpeg.exe` on Windows). Set the `FFMPEG_PATH` env var if ffmpeg lives elsewhere or isn't on your `PATH`.
- A Groq API key with access to `whisper-large-v3-turbo`

## Setup

1. Install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows (PowerShell)
   pip install -r requirements.txt
   ```

2. Export the Groq API key (PowerShell example):

   ```powershell
   $env:GROQ_API_KEY="your_key_here"
   ```

   Optionally point the app to a custom ffmpeg binary:

   ```powershell
   $env:FFMPEG_PATH="C:\path\to\ffmpeg.exe"
   ```

3. Run the Flask server:

   ```bash
   python app.py
   ```

   Navigate to `http://localhost:5000` and paste a YouTube URL to start transcribing.

## How it works

1. The frontend sends the YouTube URL to `/transcribe`.
2. `yt-dlp` downloads the video/audio stream into a temporary folder.
3. `ffmpeg` (already installed on disk `C`) converts the file to mono 16 kHz WAV.
4. The resulting audio file is handed to `script.py`'s `transcribe_audio` function, which calls Groq Whisper.
5. The transcript (and raw JSON payload) is returned to the browser and rendered instantly.

Temporary downloads are removed after each request to keep the workspace clean.

