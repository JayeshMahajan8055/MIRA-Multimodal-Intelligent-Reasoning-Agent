## Agentic Multimodal App

AI-powered web app that can:

- **Extract text from images and PDFs**
- **Transcribe audio files**
- **Fetch YouTube transcripts**
- **Summarize content**
- **Analyze sentiment**
- **Explain code**
- **Answer questions (Q&A)**

Backend is built with **FastAPI**, and the frontend is a single-page HTML app.  
LLM intelligence (intent detection, summarization, QA, code explanation) uses a **hosted OpenAI‑compatible model** (e.g. Groq), so you **do not need Ollama** anymore.

---

## 1. Project Structure

```text
agentic-multimodal-app/
  backend/
    app.py                 # FastAPI main app
    agents/
      intent_classifier.py # Uses LLM to classify user intent
      task_router.py       # Routes intents to specific task handlers
    extractors/
      image_extractor.py   # OCR using Tesseract + pytesseract
      pdf_extractor.py     # Text extraction from PDF (pdf2image, PyPDF2)
      audio_extractor.py   # Audio transcription (Whisper)
      youtube_extractor.py # YouTube transcript fetch (yt-dlp)
    tasks/
      summarizer.py        # Summarization via LLM
      sentiment.py         # Sentiment analysis via HuggingFace transformers
      code_explainer.py    # Code explanation via LLM
      qa_handler.py        # Conversational Q&A via LLM
    utils/
      llm_client.py        # Shared client for OpenAI-compatible chat APIs
    tests/
      test_extractors.py   # Basic tests for extractors

  frontend/
    index.html             # Chat-like UI for interacting with the backend

  requirements.txt         # Python dependencies
```

---

## 2. Prerequisites

- **OS**: Windows, macOS or Linux
- **Python**: 3.11+ (project currently uses 3.12 in examples)
- **Virtual environment** (recommended)
- **Tesseract OCR** (for image text extraction)
- **FFmpeg** (recommended for some audio formats)
- **Hosted LLM provider** with OpenAI-compatible API (e.g. **Groq**)

### 2.1. Install system tools (Windows)

#### Tesseract OCR

1. Download the Windows installer (UB Mannheim build is common).
2. Install to the default path, e.g. `C:\Program Files\Tesseract-OCR`.
3. Ensure it is on your `PATH` (installer option or via System Properties → Environment Variables).
4. Verify:

```cmd
tesseract --version
```

#### FFmpeg (optional but recommended)

Install FFmpeg and add it to your `PATH` so `yt-dlp` and audio processing work reliably.

---

## 3. Setup & Installation

From the project root (`agentic-multimodal-app`):

```cmd
cd "C:\Users\admin\Desktop\New folder\agentic-multimodal-app"
python -m venv my_env
my_env\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:

- **FastAPI**, **uvicorn**, **python-multipart**
- **pytesseract**, **pdf2image**, **PyPDF2**, **Pillow**
- **openai-whisper**, **yt-dlp**
- **transformers**, **torch**, **sentencepiece**
- **python-dotenv**, **requests**, **aiofiles**, **pytest**

---

## 4. Configure the Hosted LLM (Groq or Similar)

The LLM is accessed via `backend/utils/llm_client.py`, which expects an **OpenAI‑compatible** chat completions API.

### 4.1. Create `.env` in `backend/`

Create a file: `backend/.env` with:

```env
LLM_API_KEY=YOUR_GROQ_API_KEY_HERE
LLM_BASE_URL=https://api.groq.com/openai/v1/chat/completions
LLM_MODEL=llama-3.1-8b-instant
```

- You can swap `LLM_MODEL` to any compatible model.
- For other providers, change `LLM_BASE_URL` and supply their API key.

> `backend/app.py` already calls `load_dotenv()` so these variables are available at runtime.

---

## 5. Running the Backend

From the project root:

```cmd
cd "C:\Users\admin\Desktop\New folder\agentic-multimodal-app"
my_env\Scripts\activate
cd backend
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`.

### 5.1. Health Check

```cmd
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "services": {
    "fastapi": "running",
    "ollama": "check localhost:11434"
  }
}
```

> The `ollama` field is legacy text; the app no longer requires Ollama when using the hosted LLM.

---

## 6. Running the Frontend

The frontend is a static `index.html` file.

Options:

- **Simple**: Open `frontend/index.html` directly in your browser.
- **Better (recommended)**: Serve it with a simple HTTP server (avoids some CORS/cache quirks):

```cmd
cd frontend
python -m http.server 3000
```

Then open `http://localhost:3000` in your browser.

The page shows:

- Chat-like message area
- File attach button (`📎 Attach File`)
- Text input box
- Send button

---

## 7. Using the App (End-to-End)

### 7.1. Extract Text from Images

1. Click **📎 Attach File**, choose an image (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`) with text.
2. (Optional) In the text box, type: `extract the text from this image`.
3. Click **Send**.

Backend path:

- `image_extractor.py` uses **Tesseract OCR** via `pytesseract`.
- Response includes `📄 Extracted Text`, `character_count`, and `word_count`.

### 7.2. Extract Text from PDFs

1. Attach a `.pdf` file.
2. (Optional) type: `extract text from this PDF`.
3. Click **Send**.

Backend path:

- `pdf_extractor.py` uses `pdf2image` + `pytesseract` and/or direct text extraction via `PyPDF2`.

### 7.3. Transcribe Audio Files

1. Attach an audio file (`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`).
2. (Optional) type: `transcribe this audio`.
3. Click **Send**.

Backend path:

- `audio_extractor.py` uses **Whisper** (`openai-whisper`) to transcribe.

### 7.4. Fetch YouTube Transcripts

1. **Do not** attach a file.
2. In the text input, paste a YouTube URL, e.g.:  
   `https://www.youtube.com/watch?v=XXXXXXXXXXX`
3. (Optional) add: `summarize this video`.
4. Click **Send**.

Backend path:

- `youtube_extractor.py` uses **yt-dlp** to download/capture subtitles and build a transcript.

### 7.5. Summarize Content

You can summarize:

- **Plain text**:
  - No file; text box:  
    `Artificial intelligence is revolutionizing industries. Summarize this.`
- **Extracted content** (image/PDF/audio/YouTube):
  - Attach or paste URL as above.
  - Add instruction: `summarize this`.

Backend path:

- `agents/intent_classifier.py` detects **summarization** intent.
- `tasks/summarizer.py` calls the hosted LLM via `utils/llm_client.py`.

Output:

- One-line summary
- 3 bullet points
- 5-sentence detailed summary

### 7.6. Analyze Sentiment

1. Text box example:  
   `I love this product, it changed my life! What is the sentiment of this?`
2. Click **Send**.

Backend path:

- `sentiment.py` uses HuggingFace `transformers` pipeline  
  (`distilbert-base-uncased-finetuned-sst-2-english`) locally.

Output:

- Label (**POSITIVE/NEGATIVE**)
- Confidence
- Natural language justification

### 7.7. Explain Code

1. Paste code into the text box, e.g.:

```text
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

Explain this code.
```

2. Click **Send**.

Backend path:

- Intent classifier detects **code_explanation**.
- `tasks/code_explainer.py` prompts the LLM via `llm_client`.

Output:

- Plain-English explanation
- Detected language
- Possible bugs or issues
- Time and space complexity

### 7.8. Answer Questions (Q&A)

**Without file**:

- Text box: `What is machine learning?`

**With file/context**:

1. Attach a PDF or text-heavy image.
2. Text box:  
   `Based on this document, what are the main risks?`

Backend path:

- Intent classifier identifies **qa** intent.
- `tasks/qa_handler.py` calls the LLM with optional context.

Output:

- Conversational answer in the **“💬 Answer”** section.

---

## 8. How Intent & Tasks Work

1. **Extraction**: `backend/app.py` extracts text from:
   - Uploaded file (image/PDF/audio)
   - YouTube URL
   - Plain text input
2. **Intent Classification**:
   - `agents/intent_classifier.py` sends extracted content + user query to the LLM.
   - LLM returns JSON describing:
     - `intent` (e.g. `summarization`, `sentiment_analysis`, `code_explanation`, `qa`, `text_extraction`, `youtube_transcript`)
     - `confidence`
     - Whether clarification is needed.
3. **Task Routing**:
   - `agents/task_router.py` maps intent → task handler in `tasks/`.
4. **Task Execution**:
   - Tasks call either:
     - Hosted LLM via `utils/llm_client.py` (summarizer, code explainer, QA, intent classifier), or
     - Local models (sentiment via transformers).
5. **Response**:
   - `app.py` packages `extracted_content`, `intent`, `result`, and `logs`.
   - Frontend uses `index.html` script to render rich sections (summary, sentiment, code analysis, etc.).

---

## 9. Environment Variables Summary

Set in `backend/.env`:

- **LLM_API_KEY** – API key for your LLM provider (e.g. Groq).
- **LLM_BASE_URL** – Chat completions endpoint, default:  
  `https://api.groq.com/openai/v1/chat/completions`
- **LLM_MODEL** – Model name, e.g. `llama-3.1-8b-instant`.

You can also add other env vars (e.g. proxy, timeouts) if needed and read them in `llm_client.py`.

---

## 10. Troubleshooting

- **Image extraction error: “tesseract is not installed or it's not in your PATH”**
  - Install Tesseract and ensure `tesseract --version` works in a new terminal.
  - Optionally set `pytesseract.pytesseract.tesseract_cmd` in `image_extractor.py`.

- **LLM-related errors (classification, summary, QA, code explanation)**
  - Check `LLM_API_KEY` in `backend/.env`.
  - Ensure `LLM_BASE_URL` and `LLM_MODEL` are correct for your provider.
  - Watch backend logs for `LLMClientError` messages.

- **CORS / Network issues**
  - Backend listens on `http://localhost:8000` with permissive CORS (`allow_origins=["*"]`).
  - Ensure the backend is running before using the frontend.

- **Performance**
  - Very large PDFs or videos can take time; consider testing with smaller inputs first.
  - You can tune `max_tokens` and `temperature` in `utils/llm_client.py` and task modules.

---

## 11. Running Tests

From the project root:

```cmd
cd "C:\Users\admin\Desktop\New folder\agentic-multimodal-app"
my_env\Scripts\activate
pytest
```

This runs the tests in `backend/tests/test_extractors.py`.

---

## 12. Extending the App

- Add new intents in `agents/intent_classifier.py` prompt and `task_router.py`.
- Create new task modules under `backend/tasks/` and wire them in `TaskRouter`.
- Customize prompts and models in the task modules and `llm_client.py`.

This architecture lets you plug new multimodal capabilities into a single unified interface with minimal changes.


