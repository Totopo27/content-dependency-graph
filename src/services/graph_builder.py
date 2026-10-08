from typing import Dict, List, Set, Tuple
import networkx as nx
from src.domain.models import (
    ChannelCatalog,
    CurriculumGraph,
    GraphNode,
    GraphEdge,
    ConceptRelationType,
    VideoSegment,
)


class GraphBuilder:
    def __init__(self):
        self.nx_graph = nx.DiGraph()

    def build_from_catalog(self, catalog: ChannelCatalog) -> CurriculumGraph:
        """Constructs a Directed Acyclic Graph (DAG) from a channel catalog.

        Resolution rule:
        If Segment B requires Concept C_k, and Segment A teaches Concept C_k,
        and publication/sequence of A <= B, a directed edge A -> B is created.
        """
        # Map concept -> list of provider segments (chronologically ordered)
        concept_providers: Dict[str, List[Tuple[str, str, VideoSegment]]] = {}
        all_required_concepts: Set[str] = set()
        all_taught_concepts: Set[str] = set()

        nodes_dict: Dict[str, GraphNode] = {}
        edges_list: List[GraphEdge] = []

        # 1. Register all segments as nodes and index taught concepts
        for video in catalog.videos:
            for segment in video.segments:
                seg_id = segment.segment_id
                nodes_dict[seg_id] = GraphNode(
                    id=seg_id,
                    type="video_segment",
                    label=f"{video.title} [{segment.start_time}-{segment.end_time}s]",
                    metadata={
                        "video_id": video.id,
                        "video_title": video.title,
                        "start_time": segment.start_time,
                        "end_time": segment.end_time,
                        "published_at": video.published_at,
                        "concepts_taught": segment.concepts_taught,
                        "concepts_required": segment.concepts_required,
                    },
                )
                self.nx_graph.add_node(seg_id, **nodes_dict[seg_id].metadata)

                for concept in segment.concepts_taught:
                    all_taught_concepts.add(concept)
                    if concept not in concept_providers:
                        concept_providers[concept] = []
                    concept_providers[concept].append((video.published_at, video.id, segment))

                for concept in segment.concepts_required:
                    all_required_concepts.add(concept)

        # 2. Build dependency edges between segments
        for video in catalog.videos:
            for target_segment in video.segments:
                target_id = target_segment.segment_id
                for req_concept in target_segment.concepts_required:
                    providers = concept_providers.get(req_concept, [])
                    if providers:
                        # Prioritize most recent provider prior to or equal to target video
                        valid_providers = [
                            p for p in providers if p[0] <= video.published_at
                        ]
                        # Fallback to earliest if all were published after (edge case)
                        chosen_provider = valid_providers[-1] if valid_providers else providers[0]
                        source_segment = chosen_provider[2]
                        source_id = source_segment.segment_id

                        if source_id != target_id and not self.nx_graph.has_edge(source_id, target_id):
                            self.nx_graph.add_edge(
                                source_id, target_id, relation=ConceptRelationType.PREREQUISITE_OF.value, concept=req_concept
                            )
                            edges_list.append(
                                GraphEdge(
                                    source=source_id,
                                    target=target_id,
                                    relation=ConceptRelationType.PREREQUISITE_OF,
                                )
                            )

        # 3. Identify orphan concepts as external prerequisites
        external_prerequisites = sorted(list(all_required_concepts - all_taught_concepts))

        # 4. Break any accidental cycles to guarantee DAG
        if not nx.is_directed_acyclic_graph(self.nx_graph):
            cycles = list(nx.simple_cycles(self.nx_graph))
            for cycle in cycles:
                # Remove edge between last and first to break cycle
                if len(cycle) >= 2 and self.nx_graph.has_edge(cycle[-1], cycle[0]):
                    self.nx_graph.remove_edge(cycle[-1], cycle[0])
                    edges_list = [
                        e for e in edges_list if not (e.source == cycle[-1] and e.target == cycle[0])
                    ]

        return CurriculumGraph(
            channel_id=catalog.channel_id,
            channel_title=catalog.channel_title,
            nodes=list(nodes_dict.values()),
            edges=edges_list,
            external_prerequisites=external_prerequisites,
        )
