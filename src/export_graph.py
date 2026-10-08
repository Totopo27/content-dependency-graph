import json
from pathlib import Path
from src.domain.models import ChannelCatalog
from src.services.graph_builder import GraphBuilder


def export_sample_graph():
    root = Path(__file__).parent.parent
    fixture_path = root / "tests" / "fixtures" / "sample_channel_data.json"
    output_dir = root / "web" / "public"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "curriculum_graph.json"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    catalog = ChannelCatalog.model_validate(data)
    builder = GraphBuilder()
    curriculum = builder.build_from_catalog(catalog)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(curriculum.model_dump(), f, indent=2)

    print(f"Curriculum graph exported to: {output_file}")


if __name__ == "__main__":
    export_sample_graph()
