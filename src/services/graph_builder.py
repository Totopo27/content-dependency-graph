from typing import Dict, List, Set, NamedTuple, Optional
import networkx as nx
from src.domain.models import (
    ChannelCatalog,
    CurriculumGraph,
    GraphNode,
    GraphEdge,
    ConceptRelationType,
    VideoSegment,
)


class ProviderRecord(NamedTuple):
    published_at: str
    video_id: str
    segment: VideoSegment


class GraphBuilder:
    def __init__(self):
        self.nx_graph = nx.DiGraph()

    def build_from_catalog(self, catalog: ChannelCatalog) -> CurriculumGraph:
        """Constructs a Directed Acyclic Graph (DAG) from a channel catalog.

        Resolution rule:
        If Segment B requires Concept C_k, and Segment A teaches Concept C_k,
        and publication/sequence of A <= B, a directed edge A -> B is created.
        Strict chronological causality: Segments never depend on future segments.
        """
        # Map concept -> list of provider segments (chronologically ordered)
        concept_providers: Dict[str, List[ProviderRecord]] = {}
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
                    concept_providers[concept].append(
                        ProviderRecord(
                            published_at=video.published_at,
                            video_id=video.id,
                            segment=segment,
                        )
                    )

                for concept in segment.concepts_required:
                    all_required_concepts.add(concept)

        # Sort providers chronologically for deterministic lookup
        for concept in concept_providers:
            concept_providers[concept].sort(key=lambda p: (p.published_at, p.segment.start_time))

        # 2. Build dependency edges between segments
        for video in catalog.videos:
            for target_segment in video.segments:
                target_id = target_segment.segment_id
                for req_concept in target_segment.concepts_required:
                    providers = concept_providers.get(req_concept, [])
                    if not providers:
                        continue

                    # STRICT CAUSALITY: Providers must be published before or at the same time
                    # If within same video, provider segment must start before target segment
                    valid_providers = [
                        p for p in providers
                        if (p.published_at < video.published_at) or 
                           (p.video_id == video.id and p.segment.start_time < target_segment.start_time)
                    ]

                    if not valid_providers:
                        # Cannot be satisfied internally prior to this video
                        continue

                    # Pick the most recent valid provider prior to target
                    chosen_provider = valid_providers[-1]
                    source_segment = chosen_provider.segment
                    source_id = source_segment.segment_id

                    if source_id != target_id and not self.nx_graph.has_edge(source_id, target_id):
                        self.nx_graph.add_edge(
                            source_id,
                            target_id,
                            relation=ConceptRelationType.PREREQUISITE_OF.value,
                            concept=req_concept,
                            source_date=chosen_provider.published_at,
                            target_date=video.published_at,
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

        # 4. Cycle resolution based on edge timestamp order (prune illegal reverse edges)
        while not nx.is_directed_acyclic_graph(self.nx_graph):
            cycles = list(nx.simple_cycles(self.nx_graph))
            if not cycles:
                break
            cycle = cycles[0]
            # Find the edge in cycle with highest reverse temporal violation or remove last edge
            edge_to_remove = (cycle[-1], cycle[0])
            for i in range(len(cycle)):
                u, v = cycle[i], cycle[(i + 1) % len(cycle)]
                u_date = self.nx_graph.nodes[u].get("published_at", "")
                v_date = self.nx_graph.nodes[v].get("published_at", "")
                if u_date > v_date:  # violation: source newer than target
                    edge_to_remove = (u, v)
                    break

            self.nx_graph.remove_edge(*edge_to_remove)
            edges_list = [
                e for e in edges_list
                if not (e.source == edge_to_remove[0] and e.target == edge_to_remove[1])
            ]

        return CurriculumGraph(
            channel_id=catalog.channel_id,
            channel_title=catalog.channel_title,
            nodes=list(nodes_dict.values()),
            edges=edges_list,
            external_prerequisites=external_prerequisites,
        )
