package api

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"

	"github.com/gorilla/websocket"
	"shieldguard-backend/internal/engine"
	"shieldguard-backend/internal/models"
	"shieldguard-backend/internal/simulator"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow Angular dev server
	},
}

type Server struct {
	engine    *engine.Engine
	simulator *simulator.Simulator
	clients   map[*websocket.Conn]bool
	clientsMu sync.Mutex
	broadcast chan models.WSMessage
}

func NewServer(eng *engine.Engine) *Server {
	s := &Server{
		engine:    eng,
		clients:   make(map[*websocket.Conn]bool),
		broadcast: make(chan models.WSMessage, 256),
	}

	// Initialize the simulator with callback that pushes events to WebSockets
	s.simulator = simulator.NewSimulator(eng, func(tx *models.Transaction, score *models.RiskScore, alert *models.Alert) {
		// Broadcast the transaction
		s.Broadcast(models.WSMessage{
			Type:    "TRANSACTION",
			Payload: tx,
		})

		// If an alert was created, broadcast it immediately
		if alert != nil {
			s.Broadcast(models.WSMessage{
				Type:    "ALERT",
				Payload: alert,
			})
		}

		// Also broadcast updated stats
		s.Broadcast(models.WSMessage{
			Type:    "STATS",
			Payload: eng.GetStats(),
		})
	})

	// Start WebSocket broadcast listener
	go s.handleBroadcasts()

	// Restore the last saved simulator state after a backend restart.
	if eng.SimulatorShouldRun() {
		s.simulator.Start()
	}

	return s
}

func (s *Server) SetupRoutes() http.Handler {
	mux := http.NewServeMux()

	// WebSocket route
	mux.HandleFunc("/ws", s.handleWebSocket)

	// REST API routes
	mux.HandleFunc("/api/alerts", s.handleGetAlerts)
	mux.HandleFunc("/api/cards/freeze", s.handleFreezeCard)
	mux.HandleFunc("/api/cards/unfreeze", s.handleUnfreezeCard)
	mux.HandleFunc("/api/simulator/toggle", s.handleToggleSimulator)
	mux.HandleFunc("/api/simulator/status", s.handleSimulatorStatus)
	mux.HandleFunc("/api/simulator/inject", s.handleInjectFraud)
	mux.HandleFunc("/api/stats", s.handleGetStats)
	mux.HandleFunc("/api/health", func(w http.ResponseWriter, r *http.Request) {
		enabled, healthy, message := s.engine.PersistenceStatus()
		status := "UP"
		if enabled && !healthy {
			status = "DEGRADED"
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status":  status,
			"service": "ShieldGuard AI Engine",
			"persistence": map[string]interface{}{
				"enabled": enabled,
				"healthy": healthy,
				"error":   message,
			},
		})
	})

	// Serve the compiled Angular frontend from ./static/
	staticDir := findStaticDir()
	log.Printf("[+] Sirviendo frontend desde: %s", staticDir)
	mux.Handle("/", spaHandler(staticDir))

	return s.corsMiddleware(mux)
}

// findStaticDir locates the static/ directory relative to the executable
func findStaticDir() string {
	// Try relative to executable first (for compiled binary)
	exePath, err := os.Executable()
	if err == nil {
		candidate := filepath.Join(filepath.Dir(exePath), "static")
		if info, err := os.Stat(candidate); err == nil && info.IsDir() {
			return candidate
		}
	}
	// Fallback: relative to working directory (for go run)
	if info, err := os.Stat("static"); err == nil && info.IsDir() {
		return "static"
	}
	// Last resort
	return "static"
}

// spaHandler serves static files and falls back to index.html for SPA routing
func spaHandler(staticDir string) http.Handler {
	fs := http.Dir(staticDir)
	fileServer := http.FileServer(fs)

	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Skip API and WebSocket paths
		if strings.HasPrefix(r.URL.Path, "/api/") || r.URL.Path == "/ws" {
			http.NotFound(w, r)
			return
		}

		// Try to serve the exact file
		path := r.URL.Path
		if path == "/" {
			path = "/index.html"
		}
		fullPath := filepath.Join(staticDir, filepath.Clean(path))
		if _, err := os.Stat(fullPath); err == nil {
			fileServer.ServeHTTP(w, r)
			return
		}

		// SPA fallback: serve index.html for any unmatched route
		http.ServeFile(w, r, filepath.Join(staticDir, "index.html"))
	})
}

func (s *Server) corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func (s *Server) handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("Error upgrading to WebSocket: %v", err)
		return
	}

	s.clientsMu.Lock()
	s.clients[conn] = true
	s.clientsMu.Unlock()

	// Send current initial state
	initialAlerts := s.engine.GetAlerts()
	s.sendToConn(conn, models.WSMessage{
		Type:    "INITIAL_ALERTS",
		Payload: initialAlerts,
	})
	s.sendToConn(conn, models.WSMessage{
		Type:    "STATS",
		Payload: s.engine.GetStats(),
	})
	transactions := s.engine.GetTransactions()
	for i := len(transactions) - 1; i >= 0; i-- {
		s.sendToConn(conn, models.WSMessage{
			Type:    "TRANSACTION",
			Payload: transactions[i],
		})
	}

	go func() {
		defer func() {
			s.clientsMu.Lock()
			delete(s.clients, conn)
			s.clientsMu.Unlock()
			conn.Close()
		}()

		for {
			_, _, err := conn.ReadMessage()
			if err != nil {
				break
			}
		}
	}()
}

func (s *Server) sendToConn(conn *websocket.Conn, msg models.WSMessage) {
	s.clientsMu.Lock()
	defer s.clientsMu.Unlock()
	conn.WriteJSON(msg)
}

func (s *Server) Broadcast(msg models.WSMessage) {
	s.broadcast <- msg
}

func (s *Server) handleBroadcasts() {
	for msg := range s.broadcast {
		s.clientsMu.Lock()
		for client := range s.clients {
			err := client.WriteJSON(msg)
			if err != nil {
				client.Close()
				delete(s.clients, client)
			}
		}
		s.clientsMu.Unlock()
	}
}

func (s *Server) handleGetAlerts(w http.ResponseWriter, r *http.Request) {
	alerts := s.engine.GetAlerts()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(alerts)
}

func (s *Server) handleGetStats(w http.ResponseWriter, r *http.Request) {
	stats := s.engine.GetStats()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

type FreezeRequest struct {
	CardNumber string `json:"cardNumber"`
	Reason     string `json:"reason"`
	Operator   string `json:"operator"`
}

func (s *Server) handleFreezeCard(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req FreezeRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if req.Operator == "" {
		req.Operator = "Mauricio Muñoz (Gerente Riesgo)"
	}
	if req.Reason == "" {
		req.Reason = "Autofraude probable Ley 20.009 detectado"
	}

	status, err := s.engine.FreezeCard(req.CardNumber, req.Reason, req.Operator)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Broadcast update
	s.Broadcast(models.WSMessage{
		Type:    "CARD_FROZEN",
		Payload: status,
	})
	s.Broadcast(models.WSMessage{
		Type:    "STATS",
		Payload: s.engine.GetStats(),
	})

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

func (s *Server) handleUnfreezeCard(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req FreezeRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if req.Operator == "" {
		req.Operator = "Mauricio Muñoz (Reversa Operacional)"
	}

	status, err := s.engine.UnfreezeCard(req.CardNumber, req.Operator)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Broadcast update
	s.Broadcast(models.WSMessage{
		Type:    "CARD_UNFROZEN",
		Payload: status,
	})
	s.Broadcast(models.WSMessage{
		Type:    "STATS",
		Payload: s.engine.GetStats(),
	})

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

func (s *Server) handleToggleSimulator(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	if s.simulator.IsRunning() {
		s.simulator.Stop()
	} else {
		s.simulator.Start()
	}
	s.engine.SetSimulatorRunning(s.simulator.IsRunning())

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]bool{"running": s.simulator.IsRunning()})
}

func (s *Server) handleSimulatorStatus(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]bool{"running": s.simulator.IsRunning()})
}

type InjectRequest struct {
	Scenario string `json:"scenario"`
}

func (s *Server) handleInjectFraud(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req InjectRequest
	if r.Body != nil {
		json.NewDecoder(r.Body).Decode(&req)
	}
	if req.Scenario == "" {
		req.Scenario = "AUTOFRAUDE_RETAIL"
	}

	tx, score, alert := s.simulator.InjectScenario(req.Scenario)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"transaction": tx,
		"score":       score,
		"alert":       alert,
	})
}
