"""
Test suite for content extractors
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extractors.youtube_extractor import is_youtube_url, extract_youtube_url


class TestYouTubeExtractor:
    """Test YouTube URL detection and extraction"""

    def test_youtube_url_detection_standard(self):
        """Test standard YouTube URL detection"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert is_youtube_url(url) == True

    def test_youtube_url_detection_short(self):
        """Test short YouTube URL detection"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert is_youtube_url(url) == True

    def test_youtube_url_detection_with_text(self):
        """Test YouTube URL in text"""
        text = "Check out this video: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert is_youtube_url(text) == True

    def test_non_youtube_url(self):
        """Test non-YouTube URL"""
        url = "https://www.google.com"
        assert is_youtube_url(url) == False

    def test_youtube_url_extraction(self):
        """Test extracting YouTube URL from text"""
        text = "Watch https://www.youtube.com/watch?v=dQw4w9WgXcQ for more"
        url = extract_youtube_url(text)
        assert "youtube.com/watch?v=" in url

    def test_short_url_extraction(self):
        """Test extracting short YouTube URL"""
        text = "Check https://youtu.be/dQw4w9WgXcQ"
        url = extract_youtube_url(text)
        assert "youtube.com/watch?v=" in url


class TestImageExtractor:
    """Test image OCR extraction"""

    def test_image_extractor_import(self):
        """Test that image extractor can be imported"""
        from extractors.image_extractor import extract_from_image

        assert callable(extract_from_image)

    def test_image_extractor_empty_input(self):
        """Test image extractor with empty input"""
        from extractors.image_extractor import extract_from_image

        result = extract_from_image(b"")
        assert "error" in result or result.get("success") == False


class TestPDFExtractor:
    """Test PDF extraction"""

    def test_pdf_extractor_import(self):
        """Test that PDF extractor can be imported"""
        from extractors.pdf_extractor import extract_from_pdf

        assert callable(extract_from_pdf)

    def test_pdf_extractor_empty_input(self):
        """Test PDF extractor with empty input"""
        from extractors.pdf_extractor import extract_from_pdf

        result = extract_from_pdf(b"")
        assert "error" in result or result.get("success") == False


class TestAudioExtractor:
    """Test audio transcription"""

    def test_audio_extractor_import(self):
        """Test that audio extractor can be imported"""
        from extractors.audio_extractor import extract_from_audio

        assert callable(extract_from_audio)


class TestTaskModules:
    """Test that all task modules can be imported"""

    def test_summarizer_import(self):
        """Test summarizer import"""
        from tasks.summarizer import summarize_text

        assert callable(summarize_text)

    def test_sentiment_import(self):
        """Test sentiment analyzer import"""
        from tasks.sentiment import analyze_sentiment

        assert callable(analyze_sentiment)

    def test_code_explainer_import(self):
        """Test code explainer import"""
        from tasks.code_explainer import explain_code

        assert callable(explain_code)

    def test_qa_handler_import(self):
        """Test Q&A handler import"""
        from tasks.qa_handler import answer_question

        assert callable(answer_question)


class TestAgentModules:
    """Test that all agent modules can be imported"""

    def test_intent_classifier_import(self):
        """Test intent classifier import"""
        from agents.intent_classifier import IntentClassifier

        classifier = IntentClassifier()
        assert classifier is not None

    def test_task_router_import(self):
        """Test task router import"""
        from agents.task_router import TaskRouter

        router = TaskRouter()
        assert router is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
