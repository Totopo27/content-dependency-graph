import json
from pathlib import Path
import pytest
from src.domain.models import ChannelCatalog
from src.services.graph_builder import GraphBuilder
from src.services.path_solver import PedagogicalPathSolver

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_channel_data.json"


@pytest.fixture
def sample_catalog() -> ChannelCatalog:
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ChannelCatalog.model_validate(data)


def test_graph_builder_dag_properties(sample_catalog):
    builder = GraphBuilder()
    curriculum = builder.build_from_catalog(sample_catalog)

    # 1. Must produce valid CurriculumGraph
    assert curriculum.channel_id == "UC_test_backend_channel"
    assert len(curriculum.nodes) == 7  # 7 total segments across 5 videos
    assert len(curriculum.edges) > 0

    # 2. Must detect external prerequisite orphan
    assert "cryptographic-hashing" in curriculum.external_prerequisites

    # 3. NetworkX representation must be an acyclic DAG
    assert builder.nx_graph.is_directed()
    import networkx as nx
    assert nx.is_directed_acyclic_graph(builder.nx_graph)


def test_path_solver_prerequisite_sequence(sample_catalog):
    builder = GraphBuilder()
    builder.build_from_catalog(sample_catalog)
    solver = PedagogicalPathSolver(builder)

    # Target: seg_05_01 (JWT Authentication, which depends on api-database-integration)
    path = solver.get_prerequisite_path("seg_05_01")

    step_segment_ids = [step["segment_id"] for step in path]

    # Verify that foundational HTTP and SQL precede Database Integration and JWT
    assert "seg_01_01" in step_segment_ids  # HTTP basics
    assert "seg_01_02" in step_segment_ids  # HTTP methods
    assert "seg_02_01" in step_segment_ids  # REST design
    assert "seg_02_02" in step_segment_ids  # JSON endpoints
    assert "seg_03_01" in step_segment_ids  # SQL basics
    assert "seg_04_01" in step_segment_ids  # API DB integration
    assert step_segment_ids[-1] == "seg_05_01"  # Target must be last step

    # Verify ordering consistency: seg_01_01 must be before seg_02_01
    assert step_segment_ids.index("seg_01_01") < step_segment_ids.index("seg_02_01")
    # seg_03_01 (SQL) must be before seg_04_01 (API + DB)
    assert step_segment_ids.index("seg_03_01") < step_segment_ids.index("seg_04_01")
