"""
FastAPI Main Application
Agentic Multimodal Input Processing System
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Import extractors
from extractors.image_extractor import extract_from_image
from extractors.pdf_extractor import extract_from_pdf
from extractors.audio_extractor import extract_from_audio
from extractors.youtube_extractor import (
    is_youtube_url,
    extract_youtube_url,
    extract_youtube_transcript,
)

# Import agents
from agents.intent_classifier import IntentClassifier
from agents.task_router import TaskRouter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Multimodal App",
    description="AI-powered system for processing text, images, PDFs, and audio",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
if os.path.exists("../frontend"):
    app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Initialize AI components (they now use hosted LLM via utils.llm_client)
intent_classifier = IntentClassifier()
task_router = TaskRouter()

# Store conversation context (in production, use proper session management)
conversation_contexts = {}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic Multimodal App API",
        "status": "running",
        "endpoints": {
            "process": "/process (POST)",
            "clarify": "/clarify (POST)",
            "health": "/health (GET)",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {"fastapi": "running", "ollama": "check localhost:11434"},
    }


@app.post("/process")
async def process_input(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form("default"),
):
    """
    Main endpoint to process all types of input

    Args:
        text: Optional text input
        file: Optional file upload (image, PDF, audio)
        session_id: Session identifier for conversation context

    Returns:
        JSON response with extraction results, intent, and task output
    """
    logs = []
    extracted_content = ""
    extraction_metadata = {}

    try:
        logger.info(f"Processing request - Text: {bool(text)}, File: {bool(file)}")
        logs.append("Processing your request...")

        # ======================
        # STEP 1: Content Extraction
        # ======================

        if file:
            file_bytes = await file.read()
            filename = file.filename.lower()
            logs.append(f"Received file: {file.filename}")

            # Image files
            if filename.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                logs.append("Extracting text from image using OCR...")
                result = extract_from_image(file_bytes)

                if result.get("success"):
                    extracted_content = result["text"]
                    extraction_metadata = {
                        "type": "image",
                        "method": result["method"],
                        "confidence": result["confidence"],
                    }
                    logs.append(
                        f"✓ OCR completed (confidence: {result['confidence']}%)"
                    )
                else:
                    logs.append(f"✗ OCR failed: {result.get('error', 'Unknown error')}")
                    raise HTTPException(
                        status_code=400, detail="Image extraction failed"
                    )

            # PDF files
            elif filename.endswith(".pdf"):
                logs.append("Extracting text from PDF...")
                result = extract_from_pdf(file_bytes)

                if result.get("success"):
                    extracted_content = result["text"]
                    extraction_metadata = {
                        "type": "pdf",
                        "method": result["method"],
                        "pages": result["pages"],
                    }
                    logs.append(
                        f"✓ PDF extraction completed ({result['pages']} pages, method: {result['method']})"
                    )
                else:
                    logs.append(
                        f"✗ PDF extraction failed: {result.get('error', 'Unknown error')}"
                    )
                    raise HTTPException(status_code=400, detail="PDF extraction failed")

            # Audio files
            elif filename.endswith((".mp3", ".wav", ".m4a", ".ogg", ".flac")):
                logs.append("Transcribing audio using Whisper...")
                result = extract_from_audio(file_bytes, filename)

                if result.get("success"):
                    extracted_content = result["text"]
                    extraction_metadata = {
                        "type": "audio",
                        "language": result["language"],
                        "duration": result["duration"],
                    }
                    logs.append(
                        f"✓ Audio transcribed ({result['duration']}s, language: {result['language']})"
                    )
                else:
                    logs.append(
                        f"✗ Audio transcription failed: {result.get('error', 'Unknown error')}"
                    )
                    raise HTTPException(
                        status_code=400, detail="Audio transcription failed"
                    )

            else:
                logs.append(f"✗ Unsupported file type: {filename}")
                raise HTTPException(
                    status_code=400, detail=f"Unsupported file type: {filename}"
                )

        elif text:
            # Check for YouTube URL
            if is_youtube_url(text):
                logs.append("Detected YouTube URL, fetching transcript...")
                url = extract_youtube_url(text)
                result = extract_youtube_transcript(url)

                if result.get("success"):
                    extracted_content = result["text"]
                    extraction_metadata = {
                        "type": "youtube",
                        "title": result["title"],
                        "duration": result["duration"],
                    }
                    logs.append(f"✓ YouTube transcript fetched: {result['title']}")
                else:
                    logs.append(
                        f"ℹ YouTube transcript unavailable: {result.get('error', 'Unknown error')}"
                    )
                    extracted_content = text
                    extraction_metadata = {"type": "text"}
            else:
                # Plain text input
                extracted_content = text
                extraction_metadata = {"type": "text"}
                logs.append("Processing text input...")

        else:
            logs.append("✗ No input provided")
            raise HTTPException(
                status_code=400, detail="No input provided (text or file required)"
            )

        # Check if extraction produced content
        if not extracted_content or len(extracted_content.strip()) < 5:
            logs.append("⚠ Warning: Very little content extracted")
            return JSONResponse(
                {
                    "status": "error",
                    "message": "Could not extract meaningful content from input",
                    "logs": logs,
                }
            )

        # ======================
        # STEP 2: Intent Classification
        # ======================

        logs.append("Analyzing your intent...")
        intent_result = intent_classifier.classify(extracted_content, text)

        if not intent_result.get("success"):
            logs.append("⚠ Intent classification failed, requesting clarification")
        else:
            logs.append(
                f"✓ Intent identified: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})"
            )

        # ======================
        # STEP 3: Check for Clarification
        # ======================

        if intent_result.get("needs_clarification"):
            logs.append("ℹ Clarification needed from user")

            # Store context for follow-up
            conversation_contexts[session_id] = {
                "extracted_content": extracted_content,
                "extraction_metadata": extraction_metadata,
            }

            return JSONResponse(
                {
                    "status": "needs_clarification",
                    "extracted_content": (
                        extracted_content[:500] + "..."
                        if len(extracted_content) > 500
                        else extracted_content
                    ),
                    "extraction_metadata": extraction_metadata,
                    "question": intent_result.get("clarification_question"),
                    "reasoning": intent_result.get("reasoning"),
                    "logs": logs,
                    "session_id": session_id,
                }
            )

        # ======================
        # STEP 4: Execute Task
        # ======================

        logs.append(f"Executing task: {intent_result['intent']}...")
        final_result = task_router.execute(
            intent_result["intent"], extracted_content, text
        )

        if final_result.get("success"):
            logs.append("✓ Task completed successfully")
        else:
            logs.append("⚠ Task completed with warnings")

        # ======================
        # STEP 5: Return Results
        # ======================

        return JSONResponse(
            {
                "status": "success",
                "extracted_content": (
                    extracted_content[:1000] + "..."
                    if len(extracted_content) > 1000
                    else extracted_content
                ),
                "extraction_metadata": extraction_metadata,
                "intent": {
                    "type": intent_result["intent"],
                    "confidence": intent_result["confidence"],
                    "reasoning": intent_result.get("reasoning"),
                },
                "result": final_result,
                "logs": logs,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        logs.append(f"✗ Error: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": str(e), "logs": logs}, status_code=500
        )


@app.post("/clarify")
async def clarify_intent(
    clarification: str = Form(...), session_id: str = Form("default")
):
    """
    Handle clarification responses from user

    Args:
        clarification: User's clarification response
        session_id: Session identifier to retrieve context

    Returns:
        JSON response with task execution results
    """
    logs = ["Processing your clarification..."]

    try:
        # Retrieve stored context
        context = conversation_contexts.get(session_id)

        if not context:
            logs.append("✗ Session context not found")
            raise HTTPException(
                status_code=400,
                detail="Session expired or invalid. Please resubmit your input.",
            )

        extracted_content = context["extracted_content"]
        extraction_metadata = context["extraction_metadata"]

        # Re-classify with clarification
        logs.append("Re-analyzing intent with your clarification...")
        intent_result = intent_classifier.classify(extracted_content, clarification)

        if intent_result.get("needs_clarification"):
            logs.append("ℹ Still need more clarification")
            return JSONResponse(
                {
                    "status": "needs_clarification",
                    "question": intent_result.get("clarification_question"),
                    "logs": logs,
                }
            )

        logs.append(f"✓ Intent clarified: {intent_result['intent']}")

        # Execute task
        logs.append(f"Executing task: {intent_result['intent']}...")
        final_result = task_router.execute(
            intent_result["intent"], extracted_content, clarification
        )

        if final_result.get("success"):
            logs.append("✓ Task completed successfully")

        # Clean up context
        if session_id in conversation_contexts:
            del conversation_contexts[session_id]

        return JSONResponse(
            {
                "status": "success",
                "extracted_content": (
                    extracted_content[:1000] + "..."
                    if len(extracted_content) > 1000
                    else extracted_content
                ),
                "extraction_metadata": extraction_metadata,
                "intent": {
                    "type": intent_result["intent"],
                    "confidence": intent_result["confidence"],
                },
                "result": final_result,
                "logs": logs,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clarification error: {str(e)}", exc_info=True)
        logs.append(f"✗ Error: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": str(e), "logs": logs}, status_code=500
        )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Agentic Multimodal App server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
