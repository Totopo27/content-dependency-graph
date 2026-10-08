import json
import logging
from typing import Dict, Any, Optional
import httpx
from src.domain.models import VideoSegment
from src.services.extractor import ConceptExtractionService, EXTRACTION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_MODEL = "richardyoung/qwen2.5-coder-14b-instruct-abliterated:latest"
DEFAULT_OLLAMA_URL = "http://localhost:11434"

EXTRACTION_USER_PROMPT_TEMPLATE = """Analyze this video segment transcript and extract taught and required concepts:
Transcript:
\"\"\"{transcript_text}\"\"\"

Return a valid JSON object strictly matching this format:
{{
  "concepts_taught": ["concept 1", "concept 2"],
  "concepts_required": ["prerequisite 1", "prerequisite 2"]
}}
Do not include explanations or markdown outside the JSON object.
"""


class OllamaExtractionClient:
    """Client for automated concept extraction from transcripts via Ollama local API."""

    def __init__(
        self,
        model: str = DEFAULT_OLLAMA_MODEL,
        base_url: str = DEFAULT_OLLAMA_URL,
        timeout_seconds: float = 120.0,
        extraction_service: Optional[ConceptExtractionService] = None,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.extraction_service = extraction_service or ConceptExtractionService()

    def is_available(self) -> bool:
        """Checks if the local Ollama daemon is reachable and responding."""
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def extract_from_transcript(
        self,
        segment_id: str,
        transcript_text: str,
        start_time: int = 0,
        end_time: int = 0,
    ) -> VideoSegment:
        """Sends transcript chunk to Ollama with structured JSON format enforcement,

        then parses and normalizes concepts into a validated VideoSegment.
        """
        user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(
            transcript_text=transcript_text
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1,
            },
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            logger.error("Ollama extraction request failed for %s: %s", segment_id, e)
            raise RuntimeError(f"Ollama extraction failed: {e}") from e

        content = data.get("message", {}).get("content", "{}")
        try:
            raw_json = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse JSON response from Ollama for %s: %s", segment_id, e
            )
            raw_json = {"concepts_taught": [], "concepts_required": []}

        raw_json["start_time"] = start_time
        raw_json["end_time"] = end_time
        raw_json["transcript_text"] = transcript_text

        return self.extraction_service.process_raw_extraction(segment_id, raw_json)
