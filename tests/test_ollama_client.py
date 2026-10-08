import pytest
from unittest.mock import patch, MagicMock
from src.services.ollama_client import OllamaExtractionClient
from src.domain.models import VideoSegment


def test_ollama_client_is_available():
    with patch("httpx.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_instance.get.return_value = mock_response
        mock_client_cls.return_value.__enter__.return_value = mock_instance

        client = OllamaExtractionClient()
        assert client.is_available() is True


def test_ollama_client_extract_from_transcript_success():
    fake_ollama_response = {
        "message": {
            "content": (
                '{"concepts_taught": ["REST API", "JSON API"],'
                ' "concepts_required": ["HTTP", "PostgreSQL database"]}'
            )
        }
    }

    with patch("httpx.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = fake_ollama_response
        mock_instance.post.return_value = mock_response
        mock_client_cls.return_value.__enter__.return_value = mock_instance

        client = OllamaExtractionClient()
        transcript = (
            "In this video we build a REST API endpoint returning JSON data from a"
            " PostgreSQL database over HTTP."
        )

        segment: VideoSegment = client.extract_from_transcript(
            segment_id="seg_ollama_01",
            transcript_text=transcript,
            start_time=0,
            end_time=300,
        )

        assert segment.segment_id == "seg_ollama_01"
        assert segment.start_time == 0
        assert segment.end_time == 300
        assert segment.duration == 300
        # Check normalized slugs
        assert "rest-api-design" in segment.concepts_taught
        assert "json-api-endpoints" in segment.concepts_taught
        assert "http-basics" in segment.concepts_required
        assert "postgresql" in segment.concepts_required


def test_ollama_client_handles_malformed_json_fallback():
    fake_ollama_response = {
        "message": {"content": "This is non-json text that cannot be parsed"}
    }

    with patch("httpx.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = fake_ollama_response
        mock_instance.post.return_value = mock_response
        mock_client_cls.return_value.__enter__.return_value = mock_instance

        client = OllamaExtractionClient()
        segment = client.extract_from_transcript(
            segment_id="seg_ollama_fallback",
            transcript_text="some text",
            start_time=10,
            end_time=60,
        )

        assert segment.segment_id == "seg_ollama_fallback"
        assert segment.concepts_taught == []
        assert segment.concepts_required == []
