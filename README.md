# FrameMind AI — Video Intelligence Studio

A FastAPI + HTML/CSS/JavaScript AI video assistant. It accepts YouTube URLs or local media, transcribes English audio locally with Whisper (or Hinglish with Sarvam), analyzes the transcript with OpenAI, builds a local Chroma vector index, and supports transcript-grounded RAG chat.

## Stack

- Frontend: HTML, CSS, vanilla JavaScript
- Backend: FastAPI + Uvicorn
- English STT: local OpenAI Whisper
- Hinglish STT/translation: Sarvam AI
- Analysis + chat: OpenAI via `langchain-openai`
- Embeddings: `all-MiniLM-L6-v2` locally
- Vector DB: Chroma locally
- Media: yt-dlp + FFmpeg + pydub

## 1. Requirements

- Python 3.10+ (Python 3.11 recommended)
- FFmpeg installed as a Windows executable and available in PATH

Verify:

```powershell
ffmpeg -version
ffprobe -version
```

## 2. Environment

Copy `.env.example` to `.env` and set:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_STT_MODEL=saaras:v2.5
WHISPER_MODEL=small
```

`SARVAM_API_KEY` is only required when using Hinglish mode.

## 3. Install

```powershell
uv pip install -r Requirements.txt
```

## 4. Run

From the project directory:

```powershell
uv run uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Notes

The first English transcription may take longer because Whisper downloads the selected local model. The first RAG build may also download the local MiniLM embedding model.
