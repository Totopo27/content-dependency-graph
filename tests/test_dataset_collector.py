import json
from pathlib import Path
from src.domain.models import ChannelCatalog
from src.services.graph_builder import GraphBuilder
from src.services.dataset_collector import DatasetCollector


def test_dataset_collector_flywheel(tmp_path):
    root = Path(__file__).parent.parent
    fixture_path = root / "tests" / "fixtures" / "sample_channel_data.json"

    with open(fixture_path, "r", encoding="utf-8") as f:
        catalog = ChannelCatalog.model_validate(json.load(f))

    builder = GraphBuilder()
    curriculum = builder.build_from_catalog(catalog)

    collector = DatasetCollector(output_dir=tmp_path)
    count = collector.record_validated_catalog(catalog, curriculum, domain_tag="backend_engineering")

    assert count > 0
    dataset_file = tmp_path / "kev_training_dataset.jsonl"
    assert dataset_file.exists()

    with open(dataset_file, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]

    assert len(lines) == count
    first = lines[0]
    assert first["domain"] == "backend_engineering"
    assert "transcript" in first
    assert "concept" in first
    assert "target_probabilities" in first
    assert "is_teaching" in first["target_probabilities"]
    assert "is_requiring" in first["target_probabilities"]
