"""
Intent Classification Agent using hosted LLM (OpenAI-compatible API, e.g. Groq)
"""

import json
import logging

from utils.llm_client import call_llm, LLMClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Classifies user intent from extracted content and determines if clarification is needed
    """

    def classify(self, extracted_text: str, user_query: str = None) -> dict:
        """
        Classify user intent and determine if clarification is needed

        Args:
            extracted_text: Content extracted from user input
            user_query: Optional explicit user query

        Returns:
            Dictionary with intent, confidence, and clarification requirements
        """
        try:
            # Build classification prompt
            prompt = f"""You are an intent classifier for a multimodal AI assistant. Analyze the content and determine the user's goal.

Extracted Content (first 800 chars):
{extracted_text[:800]}

User Query: {user_query if user_query else "None provided"}

Determine:
1. What task does the user want? (Choose ONE from the valid intents below)
2. Is there enough information to proceed? (true/false)
3. If clarification is needed, what specific question should be asked?

Valid Intents:
- text_extraction: User wants to extract/see the text from an image/PDF
- youtube_transcript: User wants a YouTube video transcript
- summarization: User wants a summary of the content
- sentiment_analysis: User wants to know the sentiment/emotion
- code_explanation: User wants code explained or analyzed
- qa: User is asking a question or wants conversational help
- unknown: Cannot determine intent

Rules:
- If user says "summarize", "summary", or "give me key points" → summarization
- If user asks "what is the sentiment" or "is this positive/negative" → sentiment_analysis
- If content contains code and user says "explain" → code_explanation
- If user asks a question about the content → qa
- If no clear intent and no explicit instruction → needs_clarification = true

Respond ONLY with valid JSON:
{{
  "intent": "one of the valid intents above",
  "confidence": 0.0 to 1.0,
  "needs_clarification": true or false,
  "clarification_question": "specific question to ask, or null",
  "reasoning": "brief explanation of why you chose this intent"
}}"""

            logger.info("Classifying intent with hosted LLM...")

            messages = [
                {
                    "role": "system",
                    "content": "You are a precise intent classification engine for a multimodal assistant. Always respond with strict JSON that matches the required schema.",
                },
                {"role": "user", "content": prompt},
            ]

            content = call_llm(
                messages,
                temperature=0.1,
                max_tokens=400,
                response_format={"type": "json_object"},
            )

            intent_data = json.loads(content)

            logger.info(
                "Intent classified: %s (confidence: %s)",
                intent_data.get("intent", "unknown"),
                intent_data.get("confidence", 0),
            )

            return {
                "intent": intent_data.get("intent", "unknown"),
                "confidence": float(intent_data.get("confidence", 0.0)),
                "needs_clarification": bool(
                    intent_data.get("needs_clarification", False)
                ),
                "clarification_question": intent_data.get("clarification_question"),
                "reasoning": intent_data.get("reasoning", "No reasoning provided"),
                "success": True,
            }

        except (json.JSONDecodeError, LLMClientError, Exception) as e:
            logger.error(f"Intent classification error: {str(e)}")
            return self._get_fallback_intent()

    def _get_fallback_intent(self) -> dict:
        """
        Return fallback intent when classification fails
        """
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "needs_clarification": True,
            "clarification_question": "I couldn't determine what you'd like me to do. Could you please specify? For example: 'summarize this', 'analyze sentiment', 'explain this code', or ask a specific question.",
            "reasoning": "Classification service unavailable - requesting user clarification",
            "success": False,
        }


if __name__ == "__main__":
    # Test the classifier
    print("Intent classifier module loaded successfully")
    classifier = IntentClassifier()

    test_cases = [
        ("This is a test document with some content.", "Please summarize this"),
        ("def hello(): print('hi')", "What does this code do?"),
        ("I love this product!", None),
    ]

    for text, query in test_cases:
        result = classifier.classify(text, query)
        print(f"\nText: {text[:50]}")
        print(f"Query: {query}")
        print(f"Intent: {result['intent']} (confidence: {result['confidence']})")
