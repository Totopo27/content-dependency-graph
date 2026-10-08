package graph_test

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"content-dependency-graph/pkg/domain"
	"content-dependency-graph/pkg/graph"
)

func loadFixture(t *testing.T) domain.ChannelCatalog {
	t.Helper()
	fixturePath := filepath.Join("..", "..", "tests", "fixtures", "sample_channel_data.json")
	data, err := os.ReadFile(fixturePath)
	if err != nil {
		t.Fatalf("Failed to read fixture: %v", err)
	}

	var catalog domain.ChannelCatalog
	if err := json.Unmarshal(data, &catalog); err != nil {
		t.Fatalf("Failed to unmarshal fixture: %v", err)
	}
	return catalog
}

func TestGraphBuilder_BuildFromCatalog(t *testing.T) {
	catalog := loadFixture(t)
	builder := graph.NewGraphBuilder()
	curriculum := builder.BuildFromCatalog(catalog)

	if curriculum.ChannelID != "UC_test_backend_channel" {
		t.Errorf("expected channel ID 'UC_test_backend_channel', got '%s'", curriculum.ChannelID)
	}

	if len(curriculum.Nodes) != 7 {
		t.Errorf("expected 7 segment nodes, got %d", len(curriculum.Nodes))
	}

	if len(curriculum.Edges) == 0 {
		t.Errorf("expected dependency edges, got 0")
	}

	// Verify external prerequisite isolation
	foundExternal := false
	for _, ext := range curriculum.ExternalPrerequisites {
		if ext == "cryptographic-hashing" {
			foundExternal = true
			break
		}
	}
	if !foundExternal {
		t.Errorf("expected 'cryptographic-hashing' in external prerequisites")
	}
}

func TestPathSolver_GetLearningPath(t *testing.T) {
	catalog := loadFixture(t)
	builder := graph.NewGraphBuilder()
	builder.BuildFromCatalog(catalog)

	solver := graph.NewPathSolver(builder)

	// Target: seg_05_01 (JWT Authentication)
	path, err := solver.GetLearningPath("seg_05_01")
	if err != nil {
		t.Fatalf("unexpected error solving path: %v", err)
	}

	if len(path) == 0 {
		t.Fatalf("expected non-empty learning path")
	}

	// Target must be the last step
	lastStep := path[len(path)-1]
	if lastStep.SegmentID != "seg_05_01" {
		t.Errorf("expected last step to be 'seg_05_01', got '%s'", lastStep.SegmentID)
	}

	// Index map to verify relative precedence
	indices := make(map[string]int)
	for i, step := range path {
		indices[step.SegmentID] = i
	}

	// seg_01_01 (HTTP basics) must precede seg_02_01 (REST API)
	if indices["seg_01_01"] >= indices["seg_02_01"] {
		t.Errorf("precedence violation: seg_01_01 should be before seg_02_01")
	}

	// seg_03_01 (SQL basics) must precede seg_04_01 (API + DB)
	if indices["seg_03_01"] >= indices["seg_04_01"] {
		t.Errorf("precedence violation: seg_03_01 should be before seg_04_01")
	}
}
