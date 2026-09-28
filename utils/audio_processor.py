import os
import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = "downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        original = ydl.prepare_filename(info)
        filename = os.path.splitext(original)[0] + ".wav"

    if not os.path.exists(filename) or os.path.getsize(filename) <= 1000:
        raise RuntimeError("YouTube audio download/conversion produced an invalid WAV file.")
    return filename


def convert_to_wav(input_path: str) -> str:
    """Convert audio/video to mono 16 kHz PCM WAV suitable for Whisper."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)

    if len(audio) <= 0:
        raise RuntimeError("The uploaded media contains no readable audio.")

    audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    audio.export(output_path, format="wav", parameters=["-acodec", "pcm_s16le"])

    if not os.path.exists(output_path) or os.path.getsize(output_path) <= 1000:
        raise RuntimeError("FFmpeg produced an invalid or empty WAV file.")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    """Split WAV into valid chunks and skip empty/tiny trailing chunks."""
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    audio = AudioSegment.from_wav(wav_path)
    if len(audio) <= 0:
        raise RuntimeError("Audio file is empty after conversion.")

    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]

        # Very short fragments can trigger zero-length tensors in Whisper.
        if len(chunk) < 1000:
            continue

        chunk = chunk.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav", parameters=["-acodec", "pcm_s16le"])

        if os.path.exists(chunk_path) and os.path.getsize(chunk_path) > 1000:
            chunks.append(chunk_path)

    if not chunks:
        raise RuntimeError(
            "No valid audio chunks were generated. The source may contain no audio "
            "or FFmpeg conversion may have failed."
        )
    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks