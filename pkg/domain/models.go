package domain

import (
	"time"
)

type ConceptRelationType string

const (
	RelationTeaches        ConceptRelationType = "TEACHES"
	RelationRequires       ConceptRelationType = "REQUIRES"
	RelationPrerequisiteOf ConceptRelationType = "PREREQUISITE_OF"
	RelationSupersedes     ConceptRelationType = "SUPERSEDES"
)

type VideoSegment struct {
	SegmentID        string   `json:"segment_id"`
	VideoID          string   `json:"video_id,omitempty"`
	StartTime        int      `json:"start_time"`
	EndTime          int      `json:"end_time"`
	TranscriptText   string   `json:"transcript_text,omitempty"`
	ConceptsTaught   []string `json:"concepts_taught"`
	ConceptsRequired []string `json:"concepts_required"`
}

func (s *VideoSegment) Duration() int {
	if s.EndTime > s.StartTime {
		return s.EndTime - s.StartTime
	}
	return 0
}

func (s *VideoSegment) IsFoundational() bool {
	return len(s.ConceptsRequired) == 0
}

type VideoMetadata struct {
	ID          string         `json:"id"`
	Title       string         `json:"title"`
	PublishedAt string         `json:"published_at"`
	Duration    int            `json:"duration"`
	URL         string         `json:"url,omitempty"`
	Segments    []VideoSegment `json:"segments"`
}

type ChannelCatalog struct {
	ChannelID    string          `json:"channel_id"`
	ChannelTitle string          `json:"channel_title"`
	Videos       []VideoMetadata `json:"videos"`
}

type GraphNode struct {
	ID       string                 `json:"id"`
	Type     string                 `json:"type"` // "video_segment" | "concept"
	Label    string                 `json:"label"`
	Metadata map[string]interface{} `json:"metadata"`
}

type GraphEdge struct {
	Source   string              `json:"source"`
	Target   string              `json:"target"`
	Relation ConceptRelationType `json:"relation"`
}

type CurriculumGraph struct {
	ChannelID             string      `json:"channel_id"`
	ChannelTitle          string      `json:"channel_title"`
	GeneratedAt           string      `json:"generated_at"`
	Nodes                 []GraphNode `json:"nodes"`
	Edges                 []GraphEdge `json:"edges"`
	ExternalPrerequisites []string    `json:"external_prerequisites"`
}

func NewCurriculumGraph(channelID, channelTitle string) *CurriculumGraph {
	return &CurriculumGraph{
		ChannelID:             channelID,
		ChannelTitle:          channelTitle,
		GeneratedAt:           time.Now().UTC().Format(time.RFC3339),
		Nodes:                 make([]GraphNode, 0),
		Edges:                 make([]GraphEdge, 0),
		ExternalPrerequisites: make([]string, 0),
	}
}
