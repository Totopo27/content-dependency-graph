package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"content-dependency-graph/pkg/domain"
	"content-dependency-graph/pkg/graph"
)

func main() {
	port := flag.Int("port", 8080, "HTTP server port")
	fixturePath := flag.String("fixture", filepath.Join("tests", "fixtures", "sample_channel_data.json"), "Path to sample catalog JSON")
	flag.Parse()

	data, err := os.ReadFile(*fixturePath)
	if err != nil {
		log.Fatalf("Failed to read fixture: %v", err)
	}

	var catalog domain.ChannelCatalog
	if err := json.Unmarshal(data, &catalog); err != nil {
		log.Fatalf("Failed to unmarshal catalog: %v", err)
	}

	builder := graph.NewGraphBuilder()
	curriculum := builder.BuildFromCatalog(catalog)
	solver := graph.NewPathSolver(builder)

	// API: Get entire curriculum graph
	http.HandleFunc("/api/graph", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")
		json.NewEncoder(w).Encode(curriculum)
	})

	// API: Solve learning path for a target segment
	http.HandleFunc("/api/path", func(w http.ResponseWriter, r *http.Request) {
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

	// Serve static web UI
	fs := http.FileServer(http.Dir("web"))
	http.Handle("/", fs)

	addr := fmt.Sprintf(":%d", *port)
	fmt.Printf("🚀 Content Dependency Graph Go Server running at http://localhost%s\n", addr)
	fmt.Printf("   - API Graph: http://localhost%s/api/graph\n", addr)
	fmt.Printf("   - API Path:  http://localhost%s/api/path?target=seg_05_01\n", addr)
	log.Fatal(http.ListenAndServe(addr, nil))
}
