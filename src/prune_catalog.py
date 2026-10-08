import json
from pathlib import Path
from src.domain.models import ChannelCatalog
from src.services.graph_builder import GraphBuilder

def sanitize_and_prune():
    fixture_path = Path("tests/fixtures/matt_pocock_ai_skills.json")
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Clean title mojibake and prune empty segments
    cleaned_videos = []
    for v in data["videos"]:
        title = v["title"].replace("—", " - ").replace("–", " - ").replace("â€“", " - ")
        v["title"] = title
        
        pruned_segments = []
        for s in v["segments"]:
            taught = s.get("concepts_taught", [])
            required = s.get("concepts_required", [])
            # Only keep segments that teach or require concepts
            if taught or required:
                pruned_segments.append(s)
        
        v["segments"] = pruned_segments
        if pruned_segments:
            cleaned_videos.append(v)

    data["videos"] = cleaned_videos
    data["channel_title"] = data.get("channel_title", "").replace("—", " - ").replace("–", " - ").replace("â€“", " - ")

    with open(fixture_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # 2. Recompile curriculum graph
    catalog = ChannelCatalog.model_validate(data)
    builder = GraphBuilder()
    curriculum = builder.build_from_catalog(catalog)

    with open("web/curriculum_graph.json", "w", encoding="utf-8") as f:
        json.dump(curriculum.model_dump(), f, indent=2, ensure_ascii=False)

    with open("web/public/curriculum_graph.json", "w", encoding="utf-8") as f:
        json.dump(curriculum.model_dump(), f, indent=2, ensure_ascii=False)

    print(f"Pruned successfully: {len(curriculum.nodes)} meaningful lessons, {len(curriculum.edges)} edges, {len(curriculum.external_prerequisites)} external prereqs.")

if __name__ == "__main__":
    sanitize_and_prune()
