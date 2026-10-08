# Issue 03: NetworkX Graph Builder & Pedagogical Path Solver

## Status: Ready
**Milestone**: M2  
**Blocked by**: Issue 01, Issue 02  

### Description
Implement the DAG graph constructor using NetworkX. Calculate the dependency edges based on concepts taught vs required and chronological order. Implement topological sorting and ancestor traversal to compute the minimal prerequisite learning path for any selected target video.

### Deliverables
1. `src/services/graph_builder.py`:
   - Directed graph construction with nodes (`Segment`, `Concept`) and edges (`TEACHES`, `REQUIRES`, `PREREQUISITE_OF`).
   - Cycle detection and acyclic resolution.
   - Classification of orphan required concepts as `External Prerequisite`.
2. `src/services/path_solver.py`:
   - `get_learning_path(target_video_id) -> List[VideoSegment]`: Computes minimal sub-DAG and topologically ordered sequence.
3. Unit tests demonstrating that given a multi-tier dependency chain, the path solver returns the correct prerequisite order without broken dependencies.
