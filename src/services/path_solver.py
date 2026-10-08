from typing import List, Dict, Any, Union
import networkx as nx
from src.domain.models import VideoSegment
from src.services.graph_builder import GraphBuilder


class PedagogicalPathSolver:
    def __init__(self, graph_source: Union[GraphBuilder, nx.DiGraph]):
        """Accepts either a GraphBuilder instance or directly an nx.DiGraph (inversion of control)."""
        if isinstance(graph_source, GraphBuilder):
            self.nx_graph = graph_source.nx_graph
        elif isinstance(graph_source, nx.DiGraph):
            self.nx_graph = graph_source
        else:
            raise TypeError("graph_source must be a GraphBuilder or nx.DiGraph instance.")

    def get_prerequisite_path(self, target_segment_id: str) -> List[Dict[str, Any]]:
        """Computes the minimal topologically sorted learning path to reach target_segment_id."""
        if target_segment_id not in self.nx_graph:
            raise ValueError(f"Segment '{target_segment_id}' not found in curriculum graph.")

        # 1. Retrieve all ancestors (direct and indirect prerequisites)
        ancestor_ids = nx.ancestors(self.nx_graph, target_segment_id)
        subgraph_nodes = ancestor_ids.union({target_segment_id})

        # 2. Extract induced subgraph and compute topological sort
        subgraph = self.nx_graph.subgraph(subgraph_nodes)
        ordered_ids = list(nx.topological_sort(subgraph))

        # 3. Format the path
        path = []
        for step_idx, node_id in enumerate(ordered_ids, start=1):
            node_data = self.nx_graph.nodes[node_id]
            path.append({
                "step": step_idx,
                "segment_id": node_id,
                "video_id": node_data.get("video_id"),
                "video_title": node_data.get("video_title"),
                "start_time": node_data.get("start_time"),
                "end_time": node_data.get("end_time"),
                "concepts_taught": node_data.get("concepts_taught", []),
                "concepts_required": node_data.get("concepts_required", []),
                "is_target": (node_id == target_segment_id),
            })

        return path

    def get_learning_path(self, target_segment_or_video_id: str) -> List[VideoSegment]:
        """Strict spec helper: returns a list of VideoSegment domain objects."""
        # Check if argument is a segment ID directly
        if target_segment_or_video_id in self.nx_graph:
            raw_path = self.get_prerequisite_path(target_segment_or_video_id)
        else:
            # Locate first segment matching video ID
            matching_segments = [
                n for n, data in self.nx_graph.nodes(data=True)
                if data.get("video_id") == target_segment_or_video_id
            ]
            if not matching_segments:
                raise ValueError(f"Target '{target_segment_or_video_id}' not found.")
            raw_path = self.get_prerequisite_path(matching_segments[-1])

        result: List[VideoSegment] = []
        for step in raw_path:
            result.append(
                VideoSegment(
                    segment_id=step["segment_id"],
                    video_id=step["video_id"],
                    start_time=step["start_time"],
                    end_time=step["end_time"],
                    transcript_text="",
                    concepts_taught=step["concepts_taught"],
                    concepts_required=step["concepts_required"],
                )
            )
        return result
