"""
Sentiment Analysis using HuggingFace Transformers
"""

from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load sentiment analysis model once (globally)
logger.info("Loading sentiment analysis model...")
try:
    sentiment_analyzer = pipeline(
        "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    logger.info("Sentiment model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load sentiment model: {str(e)}")
    sentiment_analyzer = None


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of text

    Args:
        text: Text to analyze

    Returns:
        Dictionary with label, confidence, and justification
    """
    if sentiment_analyzer is None:
        return {
            "label": "UNKNOWN",
            "confidence": 0.0,
            "justification": "Sentiment analysis model not loaded",
            "success": False,
            "error": "Model initialization failed",
        }

    try:
        # Limit text to model's max tokens (512 for DistilBERT)
        text_preview = text[:500] if len(text) > 500 else text

        if not text_preview.strip():
            return {
                "label": "NEUTRAL",
                "confidence": 0.0,
                "justification": "No text provided for analysis",
                "success": False,
                "error": "Empty text",
            }

        logger.info("Analyzing sentiment...")

        # Run sentiment analysis
        result = sentiment_analyzer(text_preview)[0]

        label = result["label"]  # POSITIVE or NEGATIVE
        confidence = round(result["score"], 3)

        # Generate justification
        if label == "POSITIVE":
            justification = f"The text expresses positive sentiment with {confidence*100:.1f}% confidence, indicating favorable tone and constructive content."
        else:
            justification = f"The text expresses negative sentiment with {confidence*100:.1f}% confidence, indicating critical or unfavorable tone."

        logger.info(f"Sentiment: {label} ({confidence})")

        return {
            "label": label,
            "confidence": confidence,
            "justification": justification,
            "success": True,
        }

    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}")
        return {
            "label": "UNKNOWN",
            "confidence": 0.0,
            "justification": f"Error during analysis: {str(e)}",
            "success": False,
            "error": str(e),
        }


if __name__ == "__main__":
    # Test the sentiment analyzer
    print("Sentiment analyzer module loaded successfully")
    test_texts = [
        "I love this product! It's amazing and works perfectly.",
        "This is terrible. I hate it and want my money back.",
        "The weather is cloudy today.",
    ]

    for text in test_texts:
        result = analyze_sentiment(text)
        print(f"\nText: {text}")
        print(f"Result: {result}")
