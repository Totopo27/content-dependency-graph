import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.domain.models import ChannelCatalog, CurriculumGraph


class DatasetCollector:
    """Collects validated pedagogical training tuples (Flywheel) to feed future Kev fine-tuning.

    Captures tuples of:
    (transcript_chunk, candidate_concept, is_teaching, is_requiring, domain)
    """

    def __init__(self, output_dir: Optional[Path] = None):
        root = Path(__file__).parent.parent.parent
        self.output_dir = output_dir or (root / "data" / "training_pool")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / "kev_training_dataset.jsonl"

    def record_validated_catalog(
        self,
        catalog: ChannelCatalog,
        curriculum: CurriculumGraph,
        domain_tag: str = "general",
    ) -> int:
        """Extracts confirmed teaching and requirement signals from a validated graph.

        Appends records directly to the JSONL dataset pool.
        Returns the number of new training pairs added.
        """
        # Map video_id -> map of segment_id -> segment
        video_segments: Dict[str, Dict[str, Any]] = {}
        for v in catalog.videos:
            video_segments[v.id] = {s.segment_id: s for s in v.segments}

        records_written = 0
        with open(self.output_file, "a", encoding="utf-8") as f:
            for node in curriculum.nodes:
                meta = node.metadata
                video_id = meta.get("video_id")
                seg_id = node.id
                transcript_text = ""

                # Locate raw transcript text
                if video_id in video_segments and seg_id in video_segments[video_id]:
                    transcript_text = video_segments[video_id][seg_id].transcript_text

                if not transcript_text:
                    continue

                # 1. Positive signals for TEACHES
                for taught_concept in meta.get("concepts_taught", []):
                    entry = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "domain": domain_tag,
                        "channel_id": catalog.channel_id,
                        "segment_id": seg_id,
                        "transcript": transcript_text,
                        "concept": taught_concept,
                        "target_probabilities": {
                            "is_teaching": 0.95,
                            "is_requiring": 0.05,
                        },
                        "pedagogical_marker": "graph_validated_teaches",
                    }
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    records_written += 1

                # 2. Positive signals for REQUIRES
                for required_concept in meta.get("concepts_required", []):
                    entry = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "domain": domain_tag,
                        "channel_id": catalog.channel_id,
                        "segment_id": seg_id,
                        "transcript": transcript_text,
                        "concept": required_concept,
                        "target_probabilities": {
                            "is_teaching": 0.05,
                            "is_requiring": 0.95,
                        },
                        "pedagogical_marker": "graph_validated_requires",
                    }
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    records_written += 1

        return records_written
