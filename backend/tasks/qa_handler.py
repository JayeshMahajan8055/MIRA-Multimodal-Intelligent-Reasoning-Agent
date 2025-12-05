"""
Conversational Q&A Handler using hosted LLM (OpenAI-compatible API)
"""

import json
import logging

from utils.llm_client import call_llm, LLMClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def answer_question(question: str, context: str = None) -> dict:
    """
    Answer conversational questions

    Args:
        question: User's question
        context: Optional context/background information

    Returns:
        Dictionary with answer
    """
    try:
        if context:
            user_content = f"""Based on the following context, answer the question in a friendly and helpful manner.

Context:
{context[:2000]}

Question: {question}
"""
        else:
            user_content = f"""Answer the following question in a friendly and helpful manner:

Question: {question}
"""

        logger.info("Generating Q&A response with hosted LLM...")

        messages = [
            {
                "role": "system",
                "content": "You are a friendly and helpful AI assistant. Provide clear, conversational answers.",
            },
            {"role": "user", "content": user_content},
        ]

        answer = call_llm(
            messages,
            temperature=0.7,
            max_tokens=400,
        ).strip()

        logger.info("Q&A response generated successfully")

        return {"answer": answer, "has_context": context is not None, "success": True}

    except (LLMClientError, Exception) as e:
        logger.error(f"Q&A error: {str(e)}")
        return {
            "answer": f"I apologize, but I encountered an error talking to the language model: {str(e)}. Please check your API key and network, then try again.",
            "has_context": context is not None,
            "success": False,
            "error": str(e),
        }


if __name__ == "__main__":
    # Test the Q&A handler
    print("Q&A handler module loaded successfully")
    result = answer_question("What is machine learning?")
    print(json.dumps(result, indent=2))
