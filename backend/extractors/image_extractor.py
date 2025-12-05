"""
Image Text Extraction using Tesseract OCR
"""

import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import pytesseract
from PIL import Image
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_from_image(file_bytes: bytes) -> dict:
    """
    Extract text from image using Tesseract OCR

    Args:
        file_bytes: Image file as bytes

    Returns:
        Dictionary with extracted text, confidence score, and method
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(file_bytes))

        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Get OCR data with confidence scores
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        # Extract text
        text = pytesseract.image_to_string(image)

        # Calculate average confidence (filter out -1 values)
        confidences = [int(conf) for conf in data["conf"] if str(conf) != "-1"]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        logger.info(f"OCR completed. Confidence: {avg_confidence:.2f}%")

        return {
            "text": text.strip(),
            "confidence": round(avg_confidence, 2),
            "method": "tesseract_ocr",
            "success": True,
        }

    except Exception as e:
        logger.error(f"Image extraction error: {str(e)}")
        return {
            "text": "",
            "confidence": 0,
            "method": "tesseract_ocr",
            "success": False,
            "error": str(e),
        }


if __name__ == "__main__":
    # Test the extractor
    print("Image extractor module loaded successfully")
