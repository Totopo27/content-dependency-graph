import json
from pathlib import Path
import pytest
from src.domain.models import (
    ChannelCatalog,
    VideoMetadata,
    VideoSegment,
    ConceptRelationType,
    CurriculumGraph,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_channel_data.json"


def test_channel_catalog_fixture_loading():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    catalog = ChannelCatalog.model_validate(data)
    assert catalog.channel_id == "UC_test_backend_channel"
    assert len(catalog.videos) == 5
    assert catalog.videos[0].id == "vid_01"
    assert len(catalog.videos[0].segments) == 2


def test_video_segment_properties():
    segment = VideoSegment(
        segment_id="seg_01_01",
        video_id="vid_01",
        start_time=0,
        end_time=300,
        transcript_text="Explicamos el modelo cliente servidor.",
        concepts_taught=["http-basics"],
        concepts_required=[],
    )
    assert segment.duration == 300
    assert "http-basics" in segment.concepts_taught
    assert segment.is_foundational is True


def test_curriculum_graph_serialization_schema():
    graph = CurriculumGraph(
        channel_id="UC_test_backend_channel",
        channel_title="Backend Engineering Academy",
        nodes=[],
        edges=[],
        external_prerequisites=["cryptographic-hashing"],
    )
    json_data = graph.model_dump()
    assert json_data["channel_id"] == "UC_test_backend_channel"
    assert "cryptographic-hashing" in json_data["external_prerequisites"]
