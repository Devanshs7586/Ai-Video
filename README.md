# 🎙️ FrameMind AI — AI Meeting & Video Intelligence Assistant

FrameMind AI is an end-to-end **AI-powered meeting and video intelligence platform** that transforms long-form audio and video content into searchable, structured knowledge.

The application can process **YouTube videos or uploaded media files**, transcribe speech, generate intelligent summaries, extract action items and key decisions, identify open questions, and build a **Retrieval-Augmented Generation (RAG)** knowledge base that allows users to chat directly with the content.

The project combines **FastAPI, OpenAI, Whisper, Sarvam AI, LangChain, HuggingFace embeddings, ChromaDB, FFmpeg, HTML, CSS and JavaScript** into a complete AI media-analysis pipeline.

---

## ✨ Features

### 🎬 Video & Audio Processing

- Process YouTube videos directly from a URL
- Upload local audio/video files
- Extract and normalise audio automatically
- Split long media into manageable chunks
- Process long-form meetings, lectures, interviews and videos

### 🎙️ AI Transcription

FrameMind AI provides two transcription modes:

**English**
- Local OpenAI Whisper transcription
- Runs locally without requiring a transcription API
- Configurable Whisper model

**Hinglish**
- Sarvam AI speech-to-text translation
- Designed for mixed Hindi + English speech
- Automatically processes long audio in smaller segments

### 🧠 AI Meeting Intelligence

After transcription, the transcript is analysed using an OpenAI language model to automatically generate:

- 📝 Professional summary
- 🏷️ AI-generated title
- ✅ Action items
- 🎯 Key decisions
- ❓ Open questions
- 📄 Full transcript

Long transcripts are processed using a chunked summarisation pipeline so that large meetings and videos can be analysed effectively.

### 💬 RAG-Based Chat

FrameMind AI converts the transcript into a searchable semantic knowledge base.

Users can then ask questions such as:

> What were the main decisions made?

> What tasks were assigned?

> Explain the most important topic discussed.

> What did the meeting say about the project deadline?

The RAG pipeline retrieves relevant transcript sections before generating the answer, helping keep responses grounded in the actual content.

### ⚡ Asynchronous Processing

Media analysis runs as background jobs rather than blocking the application.

The frontend can track stages such as:

`Audio Processing → Transcription → AI Intelligence → Knowledge Base → Complete`

---

# 🏗️ System Architecture

```text
                 ┌─────────────────────┐
                 │     User Input      │
                 │                     │
                 │ YouTube URL / File  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Audio Processor   │
                 │                     │
                 │ yt-dlp / FFmpeg     │
                 │ pydub / chunking    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Transcription    │
                 │                     │
                 │ English → Whisper   │
                 │ Hinglish → Sarvam   │
                 └──────────┬──────────┘
                            │
                            ▼
                    Full Transcript
                            │
             ┌──────────────┼───────────────┐
             │              │               │
             ▼              ▼               ▼
      ┌────────────┐ ┌─────────────┐ ┌─────────────┐
      │ Summarizer │ │  Extractor  │ │Vector Store │
      │            │ │             │ │             │
      │ OpenAI LLM │ │ Action Items│ │ MiniLM      │
      │ + LangChain│ │ Decisions   │ │ ChromaDB    │
      │            │ │ Questions   │ │             │
      └──────┬─────┘ └──────┬──────┘ └──────┬──────┘
             │              │               │
             │              │               ▼
             │              │        ┌─────────────┐
             │              │        │ RAG Engine  │
             │              │        │             │
             │              │        │ Retrieval + │
             │              │        │ OpenAI LLM  │
             │              │        └──────┬──────┘
             │              │               │
             └──────────────┼───────────────┘
                            ▼
                 ┌─────────────────────┐
                 │  FrameMind AI UI    │
                 │                     │
                 │ Summary             │
                 │ Insights            │
                 │ Transcript          │
                 │ RAG Chat            │
                 └─────────────────────┘
```

---

# 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| Server | Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| LLM | OpenAI |
| LLM Integration | LangChain |
| English Speech-to-Text | OpenAI Whisper |
| Hinglish Speech-to-Text | Sarvam AI |
| Embeddings | HuggingFace Sentence Transformers |
| Embedding Model | `all-MiniLM-L6-v2` |
| Vector Database | ChromaDB |
| Media Download | yt-dlp |
| Audio Processing | FFmpeg + pydub |
| Environment Management | python-dotenv |

---

# 🔄 How It Works

### 1. Media Ingestion

The user provides either:

- a YouTube URL, or
- a local audio/video file.

The media processor prepares the source for transcription.

### 2. Audio Processing

FrameMind AI uses **yt-dlp, FFmpeg and pydub** to obtain and prepare audio.

Long recordings are divided into smaller chunks so they can be processed reliably.

### 3. Speech-to-Text

The transcription engine automatically routes processing according to the selected language.

```text
English
   ↓
Local Whisper
```

```text
Hinglish
   ↓
Sarvam AI
   ↓
Speech-to-Text Translation
```

The resulting pieces are combined into a complete transcript.

### 4. AI Analysis

The transcript is sent through LangChain-powered OpenAI pipelines.

The system generates:

```text
Transcript
   │
   ├──► Title
   │
   ├──► Summary
   │
   ├──► Action Items
   │
   ├──► Key Decisions
   │
   └──► Open Questions
```

### 5. Vector Knowledge Base

The transcript is split into smaller semantic chunks.

Each chunk is transformed into embeddings using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The embeddings are stored locally using **ChromaDB**.

### 6. Retrieval-Augmented Generation

When the user asks a question:

```text
User Question
      ↓
Semantic Retrieval
      ↓
Relevant Transcript Chunks
      ↓
RAG Prompt
      ↓
OpenAI LLM
      ↓
Grounded Answer
```

This allows users to interact with the content instead of manually searching through an entire transcript.

---

# 📂 Project Structure

```text
Ai-Video/
│
├── app.py
│   └── FastAPI application and API endpoints
│
├── main.py
│   └── Core application/pipeline entry point
│
├── test.py
│   └── Pipeline testing
│
├── Requirements.txt
│   └── Python dependencies
│
├── .gitignore
│
├── core/
│   │
│   ├── transcriber.py
│   │   └── Whisper and Sarvam AI transcription
│   │
│   ├── summarizer.py
│   │   └── AI title generation and summarisation
│   │
│   ├── extractor.py
│   │   └── Action items, decisions and questions
│   │
│   ├── vector_store.py
│   │   └── Embeddings and ChromaDB vector storage
│   │
│   └── rag_engine.py
│       └── Retrieval-Augmented Generation Q&A
│
├── utils/
│   └── audio_processor.py
│       └── Media download, conversion and chunking
│
└── static/
    │
    ├── index.html
    ├── style.css
    └── app.js
```

---

# 🚀 Getting Started

## Prerequisites

Make sure you have:

- Python **3.10+**
- Python **3.11 recommended**
- FFmpeg
- OpenAI API key
- Sarvam AI API key *(only required for Hinglish transcription)*

---

## 1. Clone the Repository

```bash
git clone https://github.com/Devanshs7586/Ai-Video.git
cd Ai-Video
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

Using pip:

```bash
pip install -r Requirements.txt
```

Or using `uv`:

```bash
uv pip install -r Requirements.txt
```

---

# 🎞️ Install FFmpeg

FFmpeg must be installed and accessible from your system `PATH`.

Verify the installation:

```bash
ffmpeg -version
ffprobe -version
```

If both commands return version information, FFmpeg is configured correctly.

---

# 🔐 Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here

OPENAI_MODEL=gpt-4.1-mini

WHISPER_MODEL=small

SARVAM_API_KEY=your_sarvam_api_key_here

SARVAM_STT_MODEL=saaras:v2.5
```

### Required

```env
OPENAI_API_KEY
```

### Optional

`SARVAM_API_KEY` is required only when using **Hinglish transcription**.

The application defaults to:

```env
OPENAI_MODEL=gpt-4.1-mini
WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v2.5
```

> ⚠️ Never commit your `.env` file or API keys to GitHub.

---

# ▶️ Running the Application

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

Or with `uv`:

```bash
uv run uvicorn app:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

in your browser.

---

# 🔌 API Overview

FrameMind AI exposes a FastAPI backend used by the frontend.

### Health Check

```http
GET /api/health
```

Checks application configuration including OpenAI, Sarvam AI and the selected Whisper model.

### Create Analysis Job

```http
POST /api/jobs
```

Starts processing a YouTube URL or uploaded media file.

The server returns a unique job ID.

### Job Status

```http
GET /api/jobs/{job_id}
```

Returns the current processing state, progress and analysis results.

### RAG Chat

```http
POST /api/jobs/{job_id}/chat
```

Allows the user to ask questions about the processed meeting/video.

---

# 🧠 AI Pipeline

```text
Media
  ↓
Audio Extraction
  ↓
Audio Chunking
  ↓
Speech Recognition
  ↓
Full Transcript
  ↓
────────────────────────────
  ↓           ↓            ↓
Summary    Extraction    Embeddings
  ↓           ↓            ↓
OpenAI      OpenAI       MiniLM
                           ↓
                        ChromaDB
                           ↓
                        Retriever
                           ↓
                     RAG + OpenAI
                           ↓
                    Contextual Chat
```

---

# 📦 Major Dependencies

The project uses:

```text
fastapi
uvicorn
python-multipart

yt-dlp
pydub
ffmpeg-python

openai-whisper
torch
torchaudio

langchain
langchain-core
langchain-community
langchain-openai

openai

chromadb
langchain-chroma

sentence-transformers
langchain-huggingface
huggingface-hub

langchain-text-splitters
tiktoken

python-dotenv
numpy
tqdm
requests
```

---

# 💡 Example Use Cases

FrameMind AI can be used for:

- 🧑‍💼 Business meeting analysis
- 🎓 Lecture summarisation
- 🎥 YouTube video analysis
- 🎙️ Podcast analysis
- 💻 Technical meeting documentation
- 📋 Automatic action-item extraction
- 🧠 Knowledge extraction from long recordings
- 🔍 Searching large transcripts
- 💬 Conversational Q&A over meetings
- 🇮🇳 English/Hinglish content analysis

---

# 🔒 Privacy & Local Processing

Several important parts of the pipeline run locally:

- English transcription through Whisper
- Sentence-transformer embeddings
- ChromaDB vector storage

OpenAI is used for language-model-based analysis and RAG responses.

Hinglish transcription uses Sarvam AI when that mode is selected.

Users should consider the privacy requirements of their recordings before sending meeting or media content to external APIs.

---

# ⚠️ Important Notes

### First Run

The first English transcription may take longer because Whisper needs to download the selected model.

The first RAG operation may also take additional time while the HuggingFace embedding model is downloaded.

### CPU Processing

Whisper can run locally on CPU, although transcription speed depends heavily on the selected model and hardware.

### Generated Files

Uploaded files, downloaded media, temporary audio chunks and the local vector database should not be committed to Git.

---

# 🗺️ Future Improvements

Potential future enhancements include:

- [ ] Speaker diarisation
- [ ] Real-time meeting transcription
- [ ] Multi-speaker identification
- [ ] PDF meeting-report export
- [ ] DOCX meeting-report export
- [ ] Persistent meeting history
- [ ] Persistent chat history
- [ ] Additional language support
- [ ] Meeting comparison
- [ ] Authentication and user accounts
- [ ] Docker deployment
- [ ] Cloud deployment
- [ ] Slack / Microsoft Teams integration
- [ ] Calendar integration

---

# 🤝 Contributing

Contributions, suggestions and improvements are welcome.

To contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Commit your changes.
5. Push the branch.
6. Open a pull request.

---

# 👨‍💻 Author

**Devansh Sharma**

AI/ML Developer focused on building practical applications using:

- Machine Learning
- Deep Learning
- Generative AI
- Retrieval-Augmented Generation
- LLM Applications
- AI Automation

GitHub: `Devanshs7586`

---

# ⭐ Support

If you find this project useful, consider giving the repository a ⭐.

It helps support the project and future development.

---

## FrameMind AI

**Turn meetings and long-form media into structured, searchable AI-powered knowledge.**
