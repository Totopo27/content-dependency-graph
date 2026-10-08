import pytest
from unittest.mock import MagicMock, patch
from src.services.youtube_worker import (
    YouTubeTranscriptWorker,
    extract_video_id,
)
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound


def test_extract_video_id_variants():
    assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    with pytest.raises(ValueError):
        extract_video_id("invalid-id-too-short")


def test_fetch_video_transcript_success_with_dataclasses():
    worker = YouTubeTranscriptWorker(target_languages=["en"])

    # Simulate FetchedTranscriptSnippet dataclass with attributes
    mock_snippet_1 = MagicMock()
    mock_snippet_1.text = "Hello world"
    mock_snippet_1.start = 0.0
    mock_snippet_1.duration = 4.5

    mock_snippet_2 = MagicMock()
    mock_snippet_2.text = "Second sentence"
    mock_snippet_2.start = 4.5
    mock_snippet_2.duration = 5.0

    mock_transcript = MagicMock()
    mock_transcript.fetch.return_value = [mock_snippet_1, mock_snippet_2]

    mock_transcript_list = MagicMock()
    mock_transcript_list.find_transcript.return_value = mock_transcript

    with patch.object(worker.api, "list", return_value=mock_transcript_list):
        result = worker.fetch_video_transcript("test_vid_01")

        assert len(result) == 2
        assert result[0] == {"text": "Hello world", "start": 0.0, "duration": 4.5}
        assert result[1] == {"text": "Second sentence", "start": 4.5, "duration": 5.0}


def test_fetch_video_transcript_transcripts_disabled():
    worker = YouTubeTranscriptWorker()

    with patch.object(worker.api, "list", side_effect=TranscriptsDisabled("test_vid_02")):
        result = worker.fetch_video_transcript("test_vid_02")
        assert result == []


def test_fetch_video_transcript_no_transcript_found():
    worker = YouTubeTranscriptWorker()

    with patch.object(worker.api, "list", side_effect=NoTranscriptFound("test_vid_03", ["es", "en"], None)):
        result = worker.fetch_video_transcript("test_vid_03")
        assert result == []


def test_fetch_video_transcript_network_error():
    worker = YouTubeTranscriptWorker()

    with patch.object(worker.api, "list", side_effect=Exception("Connection timed out")):
        result = worker.fetch_video_transcript("test_vid_04")
        assert result == []


def test_chunk_transcript_grouping_and_remainder():
    worker = YouTubeTranscriptWorker()

    raw_items = [
        {"text": "Part 1", "start": 0, "duration": 100},
        {"text": "Part 2", "start": 100, "duration": 150},
        {"text": "Part 3", "start": 250, "duration": 100},  # total 350s -> should trigger first chunk (>= 300)
        {"text": "Part 4", "start": 350, "duration": 50},   # remainder (400s total)
    ]

    chunks = worker.chunk_transcript(raw_items, chunk_duration_sec=300)

    assert len(chunks) == 2
    # First chunk covers 0s to 350s
    assert chunks[0]["start_time"] == 0
    assert chunks[0]["end_time"] == 350
    assert chunks[0]["transcript_text"] == "Part 1 Part 2 Part 3"

    # Remainder covers 350s to 400s
    assert chunks[1]["start_time"] == 350
    assert chunks[1]["end_time"] == 400
    assert chunks[1]["transcript_text"] == "Part 4"


def test_chunk_transcript_empty():
    worker = YouTubeTranscriptWorker()
    assert worker.chunk_transcript([]) == []
