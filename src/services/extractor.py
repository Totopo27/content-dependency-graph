from typing import List, Dict, Any, Optional
from src.domain.models import VideoSegment
from src.services.normalizer import ConceptNormalizer, ExtractionResult, RawConceptTag


EXTRACTION_SYSTEM_PROMPT = """You are an expert curriculum reverse-engineering parser.
Analyze the provided video transcript segment and extract:
1. concepts_taught: Concepts explained thoroughly or implemented from scratch in this segment.
2. concepts_required: Concepts assumed, mentioned as prior knowledge, or used as unexplained dependencies.

Always return a strictly valid JSON object matching the ExtractionResult schema.
"""


class ConceptExtractionService:
    def __init__(self, normalizer: Optional[ConceptNormalizer] = None):
        self.normalizer = normalizer or ConceptNormalizer()

    def process_raw_extraction(
        self, segment_id: str, raw_payload: Dict[str, Any]
    ) -> VideoSegment:
        """Parses a structured LLM response, normalizes concepts, and returns a hydrated VideoSegment."""
        raw_taught = [
            item.get("raw_name", "") if isinstance(item, dict) else str(item)
            for item in raw_payload.get("concepts_taught", [])
        ]
        raw_required = [
            item.get("raw_name", "") if isinstance(item, dict) else str(item)
            for item in raw_payload.get("concepts_required", [])
        ]

        normalized_taught = self.normalizer.normalize_list(raw_taught)
        normalized_required = self.normalizer.normalize_list(raw_required)

        return VideoSegment(
            segment_id=segment_id,
            start_time=raw_payload.get("start_time", 0),
            end_time=raw_payload.get("end_time", 0),
            transcript_text=raw_payload.get("transcript_text", ""),
            concepts_taught=normalized_taught,
            concepts_required=normalized_required,
        )
