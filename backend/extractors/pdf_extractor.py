"""
PDF Text Extraction with OCR fallback
"""

import PyPDF2
from pdf2image import convert_from_bytes
import pytesseract
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_from_pdf(file_bytes: bytes) -> dict:
    """
    Extract text from PDF - tries text extraction first, falls back to OCR

    Args:
        file_bytes: PDF file as bytes

    Returns:
        Dictionary with extracted text, page count, and method used
    """
    try:
        # Step 1: Try text-based extraction first (faster)
        logger.info("Attempting text-based PDF extraction...")
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""

        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            text += page_text + "\n"

        # Check if we got meaningful text
        if text.strip() and len(text.strip()) > 50:
            logger.info(f"Text extraction successful. Pages: {len(pdf_reader.pages)}")
            return {
                "text": text.strip(),
                "pages": len(pdf_reader.pages),
                "method": "text_extraction",
                "success": True,
            }

        # Step 2: Fallback to OCR for scanned PDFs
        logger.info("Text extraction failed. Falling back to OCR...")
        images = convert_from_bytes(file_bytes, dpi=200)
        ocr_text = ""

        for i, img in enumerate(images):
            logger.info(f"OCR processing page {i+1}/{len(images)}...")
            page_text = pytesseract.image_to_string(img)
            ocr_text += page_text + "\n"

        logger.info(f"OCR completed. Pages: {len(images)}")
        return {
            "text": ocr_text.strip(),
            "pages": len(images),
            "method": "ocr_fallback",
            "success": True,
        }

    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        return {
            "text": "",
            "pages": 0,
            "method": "failed",
            "success": False,
            "error": str(e),
        }


if __name__ == "__main__":
    # Test the extractor
    print("PDF extractor module loaded successfully")
