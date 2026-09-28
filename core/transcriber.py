import os
import requests
import whisper
from pydub import AudioSegment

SARVAM_PIECE_SECONDS = 25
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

_model = None


def load_model():
    global _model
    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        _model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded.")
    return _model


def _validate_audio_file(path: str, minimum_ms: int = 1000) -> AudioSegment:
    if not os.path.exists(path):
        raise RuntimeError(f"Audio file does not exist: {path}")
    if os.path.getsize(path) <= 1000:
        raise RuntimeError(f"Audio file is empty or invalid: {path}")

    audio = AudioSegment.from_wav(path)
    if len(audio) < minimum_ms:
        raise RuntimeError(f"Audio is too short for transcription ({len(audio)} ms): {path}")
    return audio


def transcribe_chunk_whisper(chunk_path: str) -> str:
    _validate_audio_file(chunk_path)
    model = load_model()

    # fp16=False is the safe choice for CPU-based Windows installations.
    result = model.transcribe(chunk_path, task="transcribe", fp16=False)
    return result.get("text", "").strip()


def _send_to_sarvam(piece_path: str) -> str:
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    headers = {"api-subscription-key": SARVAM_API_KEY}
    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": SARVAM_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        print(f"\nSarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()
    return response.json().get("transcript", "").strip()


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = _validate_audio_file(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000
    transcripts = []
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start:start + piece_ms]
        if len(piece) < 500:
            continue

        piece = piece.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav", parameters=["-acodec", "pcm_s16le"])

        try:
            print(f"  -> Sarvam piece {i + 1}/{total_pieces} ...")
            text = _send_to_sarvam(piece_path)
            if text:
                transcripts.append(text)
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return " ".join(transcripts).strip()


def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_whisper(chunk_path)


def transcribe_all(chunks: list, language: str = "english") -> str:
    if not chunks:
        raise RuntimeError("No audio chunks were provided for transcription.")

    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"
    print(f"Using {engine} for transcription.")

    transcripts = []
    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")
        text = transcribe_chunk(chunk, language=language)
        if text:
            transcripts.append(text)

    full_transcript = " ".join(transcripts).strip()
    if not full_transcript:
        raise RuntimeError(
            "Transcription returned no speech. Check that the source contains audible speech."
        )

    print("Transcription complete.")
    return full_transcript
