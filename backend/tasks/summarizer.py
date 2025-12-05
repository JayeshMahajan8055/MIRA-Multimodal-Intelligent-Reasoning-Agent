"""
Text Summarization in 3 formats using hosted LLM (OpenAI-compatible API)
"""

import json
import logging

from utils.llm_client import call_llm, LLMClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def summarize_text(text: str) -> dict:
    """
    Generate summary in 3 formats:
    1. One-line summary
    2. 3 bullet points
    3. 5-sentence paragraph

    Args:
        text: Text to summarize

    Returns:
        Dictionary with all three summary formats
    """
    try:
        # Limit text length to avoid context overflow
        text_preview = text[:4000] if len(text) > 4000 else text

        prompt = f"""Summarize the following text in THREE distinct formats:

1. ONE-LINE: Create a single sentence summary (max 20 words)
2. BULLETS: Create exactly 3 bullet points capturing key information
3. PARAGRAPH: Create a 5-sentence detailed summary

Text to summarize:
{text_preview}

Respond ONLY with valid JSON in this exact format:
{{
  "one_line": "your one sentence summary here",
  "bullets": ["first bullet point", "second bullet point", "third bullet point"],
  "five_sentences": "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
}}"""

        logger.info("Generating summary using hosted LLM...")

        messages = [
            {
                "role": "system",
                "content": "You are a helpful summarization assistant. Always respond with VALID JSON only, matching the requested schema.",
            },
            {"role": "user", "content": prompt},
        ]

        content = call_llm(
            messages,
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"},
        )

        summary_data = json.loads(content)

        logger.info("Summary generated successfully")

        return {
            "one_line": summary_data.get("one_line", "Summary not available"),
            "bullets": summary_data.get("bullets", ["Point 1", "Point 2", "Point 3"]),
            "five_sentences": summary_data.get(
                "five_sentences", "Detailed summary not available."
            ),
            "success": True,
        }

    except (json.JSONDecodeError, LLMClientError) as e:
        logger.error(f"JSON / LLM error in summarization: {str(e)}")
        # Fallback summary
        return {
            "one_line": "Unable to generate structured summary",
            "bullets": [
                "Summary generation failed",
                "Please try again",
                "Check Ollama service",
            ],
            "five_sentences": "The summarization service encountered an error. This could be due to the LLM provider being unavailable. Please check your API key and network connection, then try again.",
            "success": False,
            "error": str(e),
        }

    except Exception as e:
        logger.error(f"Summarization error: {str(e)}")
        return {
            "one_line": "Error generating summary",
            "bullets": [
                "An error occurred",
                "Check logs for details",
                "Ensure Ollama is running",
            ],
            "five_sentences": f"Failed to generate summary due to: {str(e)}. Please check that Ollama is running and the model is available.",
            "success": False,
            "error": str(e),
        }


if __name__ == "__main__":
    # Test the summarizer
    print("Summarizer module loaded successfully")
    test_text = "Artificial intelligence is transforming the world. Machine learning algorithms can now process vast amounts of data. This technology is being applied in healthcare, finance, and many other industries."
    result = summarize_text(test_text)
    print(json.dumps(result, indent=2))
