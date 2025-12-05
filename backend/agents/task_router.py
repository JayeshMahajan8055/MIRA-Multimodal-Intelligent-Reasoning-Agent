"""
Task Router - Routes intent to appropriate task executor
"""

import logging
from tasks.summarizer import summarize_text
from tasks.sentiment import analyze_sentiment
from tasks.code_explainer import explain_code
from tasks.qa_handler import answer_question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskRouter:
    """
    Routes classified intents to the appropriate task executor
    """

    def __init__(self):
        self.task_map = {
            "text_extraction": self._handle_text_extraction,
            "youtube_transcript": self._handle_youtube,
            "summarization": self._handle_summarization,
            "sentiment_analysis": self._handle_sentiment,
            "code_explanation": self._handle_code,
            "qa": self._handle_qa,
            "unknown": self._handle_unknown,
        }

    def execute(self, intent: str, content: str, user_query: str = None) -> dict:
        """
        Execute the appropriate task based on intent

        Args:
            intent: Classified intent
            content: Extracted content to process
            user_query: Optional user query for context

        Returns:
            Task execution result
        """
        logger.info(f"Routing to task handler: {intent}")

        handler = self.task_map.get(intent, self._handle_unknown)

        try:
            result = handler(content, user_query)
            result["task_type"] = intent
            return result
        except Exception as e:
            logger.error(f"Task execution error: {str(e)}")
            return {
                "task_type": intent,
                "success": False,
                "error": str(e),
                "message": f"Failed to execute {intent} task",
            }

    def _handle_text_extraction(self, content: str, user_query: str = None) -> dict:
        """
        Handle text extraction request
        """
        return {
            "result_type": "text_extraction",
            "extracted_text": content,
            "character_count": len(content),
            "word_count": len(content.split()),
            "success": True,
        }

    def _handle_youtube(self, content: str, user_query: str = None) -> dict:
        """
        Handle YouTube transcript request
        """
        return {
            "result_type": "youtube_transcript",
            "transcript": content,
            "note": "YouTube transcript has been extracted",
            "success": True,
        }

    def _handle_summarization(self, content: str, user_query: str = None) -> dict:
        """
        Handle summarization request
        """
        summary_result = summarize_text(content)

        return {
            "result_type": "summarization",
            "summary": summary_result,
            "success": summary_result.get("success", False),
        }

    def _handle_sentiment(self, content: str, user_query: str = None) -> dict:
        """
        Handle sentiment analysis request
        """
        sentiment_result = analyze_sentiment(content)

        return {
            "result_type": "sentiment_analysis",
            "sentiment": sentiment_result,
            "success": sentiment_result.get("success", False),
        }

    def _handle_code(self, content: str, user_query: str = None) -> dict:
        """
        Handle code explanation request
        """
        code_result = explain_code(content)

        return {
            "result_type": "code_explanation",
            "analysis": code_result,
            "success": code_result.get("success", False),
        }

    def _handle_qa(self, content: str, user_query: str = None) -> dict:
        """
        Handle Q&A request
        """
        if user_query:
            qa_result = answer_question(user_query, content)
        else:
            qa_result = answer_question(
                "Can you help me understand this content?", content
            )

        return {
            "result_type": "qa",
            "response": qa_result,
            "success": qa_result.get("success", False),
        }

    def _handle_unknown(self, content: str, user_query: str = None) -> dict:
        """
        Handle unknown intent
        """
        return {
            "result_type": "unknown",
            "message": "I'm not sure what you'd like me to do. Please provide more specific instructions.",
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "success": False,
        }


if __name__ == "__main__":
    # Test the router
    print("Task router module loaded successfully")
    router = TaskRouter()

    test_content = "This is a test message for routing."
    result = router.execute("text_extraction", test_content)
    print(f"Test result: {result}")
