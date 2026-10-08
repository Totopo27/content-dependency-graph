import json
from pathlib import Path
import networkx as nx
from src.domain.models import ChannelCatalog
from src.services.graph_builder import GraphBuilder


def export_sample_graph():
    root = Path(__file__).parent.parent
    fixture_path = root / "tests" / "fixtures" / "sample_channel_data.json"
    web_dir = root / "web"
    public_dir = web_dir / "public"

    public_dir.mkdir(parents=True, exist_ok=True)
    json_output_public = public_dir / "curriculum_graph.json"
    json_output_web = web_dir / "curriculum_graph.json"
    graphml_output = public_dir / "curriculum_graph.graphml"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    catalog = ChannelCatalog.model_validate(data)
    builder = GraphBuilder()
    curriculum = builder.build_from_catalog(catalog)

    # 1. Export JSON with generated_at timestamp
    graph_dict = curriculum.model_dump()
    with open(json_output_public, "w", encoding="utf-8") as f:
        json.dump(graph_dict, f, indent=2)

    with open(json_output_web, "w", encoding="utf-8") as f:
        json.dump(graph_dict, f, indent=2)

    # 2. Export GraphML (for Gephi, Cytoscape, NetworkX ingestion)
    # Convert list attributes to strings for GraphML compatibility
    g_export = builder.nx_graph.copy()
    for _, attrs in g_export.nodes(data=True):
        if "concepts_taught" in attrs:
            attrs["concepts_taught"] = ",".join(attrs["concepts_taught"])
        if "concepts_required" in attrs:
            attrs["concepts_required"] = ",".join(attrs["concepts_required"])

    nx.write_graphml(g_export, str(graphml_output))

    print(f"Curriculum graph exported to JSON ({json_output_public}) and GraphML ({graphml_output})")


if __name__ == "__main__":
    export_sample_graph()
