package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"

	"content-dependency-graph/pkg/domain"
	"content-dependency-graph/pkg/graph"
)

func setupTestServer(t *testing.T) (*domain.CurriculumGraph, *graph.PathSolver) {
	t.Helper()
	fixturePath := filepath.Join("..", "..", "tests", "fixtures", "sample_channel_data.json")
	data, err := osReadFile(fixturePath)
	if err != nil {
		t.Fatalf("Failed to read fixture: %v", err)
	}

	var catalog domain.ChannelCatalog
	if err := json.Unmarshal(data, &catalog); err != nil {
		t.Fatalf("Failed to unmarshal catalog: %v", err)
	}

	builder := graph.NewGraphBuilder()
	curriculum := builder.BuildFromCatalog(catalog)
	solver := graph.NewPathSolver(builder)
	return curriculum, solver
}

func TestAPIGraphHandler(t *testing.T) {
	curriculum, _ := setupTestServer(t)

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")
		json.NewEncoder(w).Encode(curriculum)
	})

	req := httptest.NewRequest(http.MethodGet, "/api/graph", nil)
	rr := httptest.NewRecorder()
	handler.ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Errorf("expected status 200, got %d", rr.Code)
	}

	var resp domain.CurriculumGraph
	if err := json.Unmarshal(rr.Body.Bytes(), &resp); err != nil {
		t.Fatalf("failed to decode response: %v", err)
	}

	if resp.ChannelID != "UC_test_backend_channel" {
		t.Errorf("expected channel ID 'UC_test_backend_channel', got '%s'", resp.ChannelID)
	}
	if len(resp.Nodes) != 7 {
		t.Errorf("expected 7 nodes, got %d", len(resp.Nodes))
	}
}

func TestAPIPathHandler_Success(t *testing.T) {
	_, solver := setupTestServer(t)

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		targetID := r.URL.Query().Get("target")
		if targetID == "" {
			http.Error(w, "missing 'target' query parameter", http.StatusBadRequest)
			return
		}

		path, err := solver.GetLearningPath(targetID)
		if err != nil {
			http.Error(w, err.Error(), http.StatusNotFound)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"target": targetID,
			"steps":  path,
		})
	})

	req := httptest.NewRequest(http.MethodGet, "/api/path?target=seg_05_01", nil)
	rr := httptest.NewRecorder()
	handler.ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Errorf("expected status 200, got %d", rr.Code)
	}

	var resp struct {
		Target string                `json:"target"`
		Steps  []domain.VideoSegment `json:"steps"`
	}
	if err := json.Unmarshal(rr.Body.Bytes(), &resp); err != nil {
		t.Fatalf("failed to decode response: %v", err)
	}

	if resp.Target != "seg_05_01" {
		t.Errorf("expected target 'seg_05_01', got '%s'", resp.Target)
	}
	if len(resp.Steps) == 0 {
		t.Errorf("expected non-empty steps")
	}
}

func TestAPIPathHandler_MissingTarget(t *testing.T) {
	_, solver := setupTestServer(t)

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		targetID := r.URL.Query().Get("target")
		if targetID == "" {
			http.Error(w, "missing 'target' query parameter", http.StatusBadRequest)
			return
		}

		path, err := solver.GetLearningPath(targetID)
		if err != nil {
			http.Error(w, err.Error(), http.StatusNotFound)
			return
		}

		json.NewEncoder(w).Encode(map[string]interface{}{
			"target": targetID,
			"steps":  path,
		})
	})

	req := httptest.NewRequest(http.MethodGet, "/api/path", nil)
	rr := httptest.NewRecorder()
	handler.ServeHTTP(rr, req)

	if rr.Code != http.StatusBadRequest {
		t.Errorf("expected status 400 for missing target, got %d", rr.Code)
	}
}

func osReadFile(name string) ([]byte, error) {
	return os.ReadFile(name)
}
