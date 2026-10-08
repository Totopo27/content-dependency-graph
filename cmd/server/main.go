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
	fixturePath := flag.String("fixture", filepath.Join("web", "curriculum_graph.json"), "Path to curriculum graph JSON or catalog JSON")
	flag.Parse()

	data, err := os.ReadFile(*fixturePath)
	if err != nil {
		log.Fatalf("Failed to read graph/catalog data: %v", err)
	}

	var curriculum *domain.CurriculumGraph
	var solver *graph.PathSolver

	// First try unmarshaling as CurriculumGraph directly
	var directCurriculum domain.CurriculumGraph
	if err := json.Unmarshal(data, &directCurriculum); err == nil && len(directCurriculum.Nodes) > 0 {
		curriculum = &directCurriculum
		// Build graph builder from curriculum nodes & edges for solver
		builder := graph.NewGraphBuilder()
		for _, node := range curriculum.Nodes {
			builder.AddManualNode(node)
		}
		for _, edge := range curriculum.Edges {
			builder.AddManualEdge(edge.Source, edge.Target)
		}
		solver = graph.NewPathSolver(builder)
	} else {
		// Fallback to unmarshaling as ChannelCatalog
		var catalog domain.ChannelCatalog
		if err := json.Unmarshal(data, &catalog); err != nil {
			log.Fatalf("Failed to unmarshal data as CurriculumGraph or ChannelCatalog: %v", err)
		}
		builder := graph.NewGraphBuilder()
		curriculum = builder.BuildFromCatalog(catalog)
		solver = graph.NewPathSolver(builder)
	}

	// API: Get entire curriculum graph
	http.HandleFunc("/api/graph", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
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

		w.Header().Set("Content-Type", "application/json; charset=utf-8")
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
