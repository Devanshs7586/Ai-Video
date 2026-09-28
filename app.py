from dotenv import load_dotenv
load_dotenv()

import os
import shutil
import threading
import traceback
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="AI Video Assistant", version="2.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

jobs = {}
rag_chains = {}
lock = threading.Lock()


def set_job(job_id: str, **updates):
    with lock:
        jobs.setdefault(job_id, {}).update(updates)


def run_analysis(job_id: str, source: str, language: str):
    try:
        set_job(job_id, status="processing", stage="audio", progress=10,
                message="Preparing audio and creating transcription chunks…")
        chunks = process_input(source)

        set_job(job_id, stage="transcription", progress=32,
                message=f"Transcribing with {'Sarvam AI' if language == 'hinglish' else 'local Whisper'}…")
        transcript = transcribe_all(chunks, language=language)
        if not transcript.strip():
            raise RuntimeError("No transcript was generated from the supplied media.")

        set_job(job_id, stage="intelligence", progress=58,
                message="OpenAI is generating the title and meeting intelligence…")
        title = generate_title(transcript)
        summary = summarize(transcript)
        action_items = extract_action_items(transcript)
        decisions = extract_key_decisions(transcript)
        questions = extract_questions(transcript)

        set_job(job_id, stage="knowledge", progress=82,
                message="Building the local semantic knowledge base…")
        rag_chain = build_rag_chain(transcript, job_id=job_id)
        rag_chains[job_id] = rag_chain

        word_count = len(transcript.split())
        set_job(
            job_id,
            status="complete",
            stage="complete",
            progress=100,
            message="Analysis complete.",
            result={
                "title": title.strip(),
                "summary": summary.strip(),
                "action_items": action_items.strip(),
                "decisions": decisions.strip(),
                "questions": questions.strip(),
                "transcript": transcript.strip(),
                "word_count": word_count,
                "language": language,
            },
        )
    except Exception as exc:
        traceback.print_exc()
        set_job(job_id, status="error", stage="error", progress=100,
                message=str(exc), error=str(exc))


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "sarvam_configured": bool(os.getenv("SARVAM_API_KEY")),
        "whisper_model": os.getenv("WHISPER_MODEL", "small"),
    }


@app.post("/api/jobs")
async def create_job(
    source_url: Optional[str] = Form(default=None),
    language: str = Form(default="english"),
    file: Optional[UploadFile] = File(default=None),
):
    language = language.lower().strip()
    if language not in {"english", "hinglish"}:
        raise HTTPException(status_code=400, detail="Language must be english or hinglish.")
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured in .env")
    if language == "hinglish" and not os.getenv("SARVAM_API_KEY"):
        raise HTTPException(status_code=500, detail="SARVAM_API_KEY is required for Hinglish mode.")

    if not source_url and not file:
        raise HTTPException(status_code=400, detail="Provide a YouTube URL or upload a media file.")

    job_id = uuid.uuid4().hex[:12]
    source = source_url.strip() if source_url else ""

    if file:
        safe_name = Path(file.filename or "upload.bin").name
        destination = UPLOAD_DIR / f"{job_id}_{safe_name}"
        with destination.open("wb") as out:
            shutil.copyfileobj(file.file, out)
        source = str(destination)

    set_job(job_id, status="queued", stage="queued", progress=3,
            message="Analysis queued…", result=None, error=None)

    thread = threading.Thread(target=run_analysis, args=(job_id, source, language), daemon=True)
    thread.start()
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


class ChatRequest(BaseModel):
    question: str


@app.post("/api/jobs/{job_id}/chat")
def chat(job_id: str, body: ChatRequest):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.get("status") != "complete":
        raise HTTPException(status_code=409, detail="Analysis is not complete yet.")
    rag_chain = rag_chains.get(job_id)
    if not rag_chain:
        raise HTTPException(status_code=410, detail="Chat session is unavailable. Re-analyse the media.")
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    return {"answer": ask_question(rag_chain, question)}
