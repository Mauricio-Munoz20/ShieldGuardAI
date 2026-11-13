package api

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"shieldguard-backend/internal/engine"
	"shieldguard-backend/internal/simulator"
)

func TestSimulatorMutationEndpointsRequirePost(t *testing.T) {
	eng := engine.NewEngine()
	handler := (&Server{engine: eng, simulator: simulator.NewSimulator(eng, nil)}).SetupRoutes()

	for _, path := range []string{"/api/simulator/toggle", "/api/simulator/inject"} {
		t.Run(path, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, path, nil)
			res := httptest.NewRecorder()
			handler.ServeHTTP(res, req)

			if res.Code != http.StatusMethodNotAllowed {
				t.Fatalf("GET %s returned status %d, want %d", path, res.Code, http.StatusMethodNotAllowed)
			}
		})
	}

	statusReq := httptest.NewRequest(http.MethodGet, "/api/simulator/status", nil)
	statusRes := httptest.NewRecorder()
	handler.ServeHTTP(statusRes, statusReq)
	if statusRes.Code != http.StatusOK {
		t.Fatalf("GET /api/simulator/status returned status %d, want %d", statusRes.Code, http.StatusOK)
	}
	var status struct {
		Running bool `json:"running"`
	}
	if err := json.Unmarshal(statusRes.Body.Bytes(), &status); err != nil {
		t.Fatalf("decode simulator status: %v", err)
	}
	if status.Running {
		t.Fatal("new simulator reports running, want false")
	}
}
