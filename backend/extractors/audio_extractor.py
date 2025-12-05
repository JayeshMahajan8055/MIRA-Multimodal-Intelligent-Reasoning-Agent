"""
Audio Transcription using OpenAI Whisper
"""

import whisper
import tempfile
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Whisper model once (globally)
logger.info("Loading Whisper model (this may take a minute on first run)...")
try:
    whisper_model = whisper.load_model(
        "base"
    )  # Options: tiny, base, small, medium, large
    logger.info("Whisper model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {str(e)}")
    whisper_model = None


def extract_from_audio(file_bytes: bytes, filename: str) -> dict:
    """
    Transcribe audio using Whisper

    Args:
        file_bytes: Audio file as bytes
        filename: Original filename (used to determine extension)

    Returns:
        Dictionary with transcribed text, language, and duration
    """
    if whisper_model is None:
        return {
            "text": "",
            "language": "unknown",
            "duration": 0,
            "success": False,
            "error": "Whisper model not loaded",
        }

    try:
        # Save to temporary file (Whisper needs a file path)
        file_extension = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        logger.info(f"Transcribing audio file: {filename}")

        # Transcribe using Whisper
        result = whisper_model.transcribe(tmp_path, fp16=False)

        # Cleanup temp file
        try:
            os.unlink(tmp_path)
        except:
            pass

        logger.info(f"Transcription completed. Language: {result['language']}")

        return {
            "text": result["text"].strip(),
            "language": result["language"],
            "duration": round(result.get("duration", 0), 2),
            "success": True,
        }

    except Exception as e:
        logger.error(f"Audio extraction error: {str(e)}")
        # Cleanup temp file if it exists
        try:
            if "tmp_path" in locals():
                os.unlink(tmp_path)
        except:
            pass

        return {
            "text": "",
            "language": "unknown",
            "duration": 0,
            "success": False,
            "error": str(e),
        }


if __name__ == "__main__":
    # Test the extractor
    print("Audio extractor module loaded successfully")
    print(f"Whisper model status: {'Loaded' if whisper_model else 'Not loaded'}")
