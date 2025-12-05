"""
Code Explanation and Analysis using hosted LLM (OpenAI-compatible API)
"""

import json
import logging

from utils.llm_client import call_llm, LLMClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def explain_code(code_text: str) -> dict:
    """
    Explain code, detect bugs, and analyze complexity

    Args:
        code_text: Code snippet to analyze

    Returns:
        Dictionary with explanation, language, bugs, and complexity
    """
    try:
        prompt = f"""Analyze the following code snippet:

```
{code_text}
```

Provide a detailed analysis with:
1. What the code does (in plain English, 2-3 sentences)
2. Programming language detected
3. Any bugs, issues, or potential problems (list them, or empty array if none)
4. Time complexity (Big O notation)
5. Space complexity (Big O notation)

Respond ONLY with valid JSON in this exact format:
{{
  "explanation": "Plain English explanation of what the code does",
  "language": "detected programming language",
  "bugs": ["bug or issue 1", "bug or issue 2"] or [],
  "time_complexity": "O(n) or O(1) etc.",
  "space_complexity": "O(n) or O(1) etc."
}}"""

        logger.info("Analyzing code with hosted LLM...")

        messages = [
            {
                "role": "system",
                "content": "You are an expert code analysis engine. Always return STRICT JSON matching the requested schema.",
            },
            {"role": "user", "content": prompt},
        ]

        content = call_llm(
            messages,
            temperature=0.2,
            max_tokens=600,
            response_format={"type": "json_object"},
        )

        code_analysis = json.loads(content)

        logger.info(
            f"Code analysis completed. Language: {code_analysis.get('language', 'unknown')}"
        )

        return {
            "explanation": code_analysis.get(
                "explanation", "Code explanation not available"
            ),
            "language": code_analysis.get("language", "unknown"),
            "bugs": code_analysis.get("bugs", []),
            "time_complexity": code_analysis.get("time_complexity", "O(?)"),
            "space_complexity": code_analysis.get("space_complexity", "O(?)"),
            "success": True,
        }

    except (json.JSONDecodeError, LLMClientError) as e:
        logger.error(f"JSON / LLM error in code explanation: {str(e)}")
        return {
            "explanation": "Failed to parse code analysis response",
            "language": "unknown",
            "bugs": ["JSON parsing error occurred"],
            "time_complexity": "O(?)",
            "space_complexity": "O(?)",
            "success": False,
            "error": str(e),
        }

    except Exception as e:
        logger.error(f"Code explanation error: {str(e)}")
        return {
            "explanation": f"Error analyzing code: {str(e)}",
            "language": "unknown",
            "bugs": ["Analysis failed - ensure LLM provider is reachable"],
            "time_complexity": "O(?)",
            "space_complexity": "O(?)",
            "success": False,
            "error": str(e),
        }


if __name__ == "__main__":
    # Test the code explainer
    print("Code explainer module loaded successfully")
    test_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    result = explain_code(test_code)
    print(json.dumps(result, indent=2))
