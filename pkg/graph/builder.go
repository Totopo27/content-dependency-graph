package graph

import (
	"sort"
	"content-dependency-graph/pkg/domain"
)

type providerRecord struct {
	publishedAt string
	videoID     string
	startTime   int
	segment     domain.VideoSegment
}

type GraphBuilder struct {
	nodes map[string]domain.GraphNode
	edges map[string][]string // adjacency list: source -> []targets
	inDeg map[string]int      // in-degree tracking
}

func NewGraphBuilder() *GraphBuilder {
	return &GraphBuilder{
		nodes: make(map[string]domain.GraphNode),
		edges: make(map[string][]string),
		inDeg: make(map[string]int),
	}
}

func (gb *GraphBuilder) AddManualNode(node domain.GraphNode) {
	gb.nodes[node.ID] = node
	if _, exists := gb.inDeg[node.ID]; !exists {
		gb.inDeg[node.ID] = 0
	}
}

func (gb *GraphBuilder) AddManualEdge(sourceID, targetID string) {
	gb.edges[sourceID] = append(gb.edges[sourceID], targetID)
	gb.inDeg[targetID]++
}

func (gb *GraphBuilder) BuildFromCatalog(catalog domain.ChannelCatalog) *domain.CurriculumGraph {
	curriculum := domain.NewCurriculumGraph(catalog.ChannelID, catalog.ChannelTitle)

	conceptProviders := make(map[string][]providerRecord)
	allRequired := make(map[string]bool)
	allTaught := make(map[string]bool)

	// 1. Index all video segments as nodes
	for _, video := range catalog.Videos {
		for _, seg := range video.Segments {
			seg.VideoID = video.ID
			nodeMeta := map[string]interface{}{
				"video_id":          video.ID,
				"video_title":       video.Title,
				"start_time":        seg.StartTime,
				"end_time":          seg.EndTime,
				"published_at":      video.PublishedAt,
				"concepts_taught":   seg.ConceptsTaught,
				"concepts_required": seg.ConceptsRequired,
			}

			node := domain.GraphNode{
				ID:       seg.SegmentID,
				Type:     "video_segment",
				Label:    video.Title,
				Metadata: nodeMeta,
			}

			gb.nodes[seg.SegmentID] = node
			if _, exists := gb.inDeg[seg.SegmentID]; !exists {
				gb.inDeg[seg.SegmentID] = 0
			}

			for _, c := range seg.ConceptsTaught {
				allTaught[c] = true
				conceptProviders[c] = append(conceptProviders[c], providerRecord{
					publishedAt: video.PublishedAt,
					videoID:     video.ID,
					startTime:   seg.StartTime,
					segment:     seg,
				})
			}

			for _, c := range seg.ConceptsRequired {
				allRequired[c] = true
			}
		}
	}

	// Sort providers chronologically
	for c := range conceptProviders {
		sort.Slice(conceptProviders[c], func(i, j int) bool {
			if conceptProviders[c][i].publishedAt != conceptProviders[c][j].publishedAt {
				return conceptProviders[c][i].publishedAt < conceptProviders[c][j].publishedAt
			}
			return conceptProviders[c][i].startTime < conceptProviders[c][j].startTime
		})
	}

	// 2. Build dependency edges enforcing strict chronological causality
	addedEdges := make(map[string]bool)

	for _, video := range catalog.Videos {
		for _, targetSeg := range video.Segments {
			targetID := targetSeg.SegmentID

			for _, reqConcept := range targetSeg.ConceptsRequired {
				providers := conceptProviders[reqConcept]
				if len(providers) == 0 {
					continue
				}

				// Find latest valid provider published before or earlier in the same video
				var validProvider *providerRecord
				for i := len(providers) - 1; i >= 0; i-- {
					p := providers[i]
					if p.publishedAt < video.PublishedAt || (p.videoID == video.ID && p.startTime < targetSeg.StartTime) {
						validProvider = &p
						break
					}
				}

				if validProvider == nil {
					continue
				}

				sourceID := validProvider.segment.SegmentID
				edgeKey := sourceID + "->" + targetID

				if sourceID != targetID && !addedEdges[edgeKey] {
					addedEdges[edgeKey] = true
					gb.edges[sourceID] = append(gb.edges[sourceID], targetID)
					gb.inDeg[targetID]++

					curriculum.Edges = append(curriculum.Edges, domain.GraphEdge{
						Source:   sourceID,
						Target:   targetID,
						Relation: domain.RelationPrerequisiteOf,
					})
				}
			}
		}
	}

	// Populate curriculum nodes
	for _, node := range gb.nodes {
		curriculum.Nodes = append(curriculum.Nodes, node)
	}

	// Identify external prerequisites
	for req := range allRequired {
		if !allTaught[req] {
			curriculum.ExternalPrerequisites = append(curriculum.ExternalPrerequisites, req)
		}
	}
	sort.Strings(curriculum.ExternalPrerequisites)

	return curriculum
}
