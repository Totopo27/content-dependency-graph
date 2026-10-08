package graph

import (
	"errors"
	"content-dependency-graph/pkg/domain"
)

type PathSolver struct {
	builder *GraphBuilder
}

func NewPathSolver(builder *GraphBuilder) *PathSolver {
	return &PathSolver{builder: builder}
}

// GetLearningPath calculates the minimal ancestor tree and topologically orders it.
func (ps *PathSolver) GetLearningPath(targetSegmentID string) ([]domain.VideoSegment, error) {
	if _, exists := ps.builder.nodes[targetSegmentID]; !exists {
		return nil, errors.New("target segment not found in graph")
	}

	// 1. Gather all upstream ancestors using reverse BFS
	ancestors := make(map[string]bool)
	queue := []string{targetSegmentID}

	// Build reverse adjacency list
	reverseEdges := make(map[string][]string)
	for src, targets := range ps.builder.edges {
		for _, tgt := range targets {
			reverseEdges[tgt] = append(reverseEdges[tgt], src)
		}
	}

	for len(queue) > 0 {
		curr := queue[0]
		queue = queue[1:]

		for _, parent := range reverseEdges[curr] {
			if !ancestors[parent] {
				ancestors[parent] = true
				queue = append(queue, parent)
			}
		}
	}

	// Induced sub-graph node set
	subNodes := make(map[string]bool)
	for a := range ancestors {
		subNodes[a] = true
	}
	subNodes[targetSegmentID] = true

	// Compute in-degrees within the subgraph
	subInDeg := make(map[string]int)
	for id := range subNodes {
		subInDeg[id] = 0
	}
	for src, targets := range ps.builder.edges {
		if subNodes[src] {
			for _, tgt := range targets {
				if subNodes[tgt] {
					subInDeg[tgt]++
				}
			}
		}
	}

	// Kahn's algorithm for topological sorting
	readyQueue := make([]string, 0)
	for id, deg := range subInDeg {
		if deg == 0 {
			readyQueue = append(readyQueue, id)
		}
	}

	var orderedIDs []string
	for len(readyQueue) > 0 {
		curr := readyQueue[0]
		readyQueue = readyQueue[1:]
		orderedIDs = append(orderedIDs, curr)

		for _, neighbor := range ps.builder.edges[curr] {
			if subNodes[neighbor] {
				subInDeg[neighbor]--
				if subInDeg[neighbor] == 0 {
					readyQueue = append(readyQueue, neighbor)
				}
			}
		}
	}

	if len(orderedIDs) != len(subNodes) {
		return nil, errors.New("cyclic dependency detected: unable to topologically sort all prerequisite segments")
	}

	// Convert ordered IDs into domain.VideoSegment instances
	var result []domain.VideoSegment
	for _, id := range orderedIDs {
		node := ps.builder.nodes[id]
		meta := node.Metadata

		var taught, required []string
		if t, ok := meta["concepts_taught"].([]string); ok {
			taught = t
		}
		if r, ok := meta["concepts_required"].([]string); ok {
			required = r
		}

		result = append(result, domain.VideoSegment{
			SegmentID:        id,
			VideoID:          meta["video_id"].(string),
			StartTime:        meta["start_time"].(int),
			EndTime:          meta["end_time"].(int),
			ConceptsTaught:   taught,
			ConceptsRequired: required,
		})
	}

	return result, nil
}
