from typing import List, Dict, Any, Optional
import networkx as nx
from src.services.graph_builder import GraphBuilder


class PedagogicalPathSolver:
    def __init__(self, builder: GraphBuilder):
        self.builder = builder
        self.nx_graph = builder.nx_graph

    def get_prerequisite_path(self, target_segment_id: str) -> List[Dict[str, Any]]:
        """Computes the minimal topologically sorted learning path to reach target_segment_id.

        Returns an ordered list of node metadata dictionaries.
        """
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
