package engine

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"shieldguard-backend/internal/models"
)

const persistenceVersion = 1

type persistedState struct {
	Version          int                     `json:"version"`
	Profiles         map[string]*CardProfile `json:"profiles"`
	Alerts           []*models.Alert         `json:"alerts"`
	Transactions     []*models.Transaction   `json:"recentTransactions"`
	TotalProcessed   int64                   `json:"totalProcessed"`
	PreventedLossCLP int64                   `json:"preventedLossClp"`
	AutopoiesisCycle int                     `json:"autopoiesisCycle"`
	SimulatorRunning bool                    `json:"simulatorRunning"`
}

// NewPersistentEngine opens a durable JSON snapshot, creating the initial
// seeded state when the file does not exist. An invalid snapshot is an error;
// it is never silently replaced with fresh state.
func NewPersistentEngine(path string) (*Engine, error) {
	if path == "" {
		return nil, errors.New("persistence path cannot be empty")
	}

	e := newEngine()
	e.persistencePath = path

	data, err := os.ReadFile(path)
	if errors.Is(err, os.ErrNotExist) {
		e.mu.Lock()
		defer e.mu.Unlock()
		if err := e.persistLocked(); err != nil {
			return nil, fmt.Errorf("initialize persistent state: %w", err)
		}
		return e, nil
	}
	if err != nil {
		return nil, fmt.Errorf("read persistent state: %w", err)
	}

	var state persistedState
	if err := json.Unmarshal(data, &state); err != nil {
		return nil, fmt.Errorf("decode persistent state: %w", err)
	}
	if state.Version != persistenceVersion {
		return nil, fmt.Errorf("unsupported persistence version %d (expected %d)", state.Version, persistenceVersion)
	}
	if state.Profiles == nil {
		state.Profiles = make(map[string]*CardProfile)
	}
	if state.Alerts == nil {
		state.Alerts = make([]*models.Alert, 0)
	}
	if state.Transactions == nil {
		state.Transactions = make([]*models.Transaction, 0)
	}

	e.profiles = state.Profiles
	e.alerts = state.Alerts
	e.transactions = state.Transactions
	e.totalProcessed = state.TotalProcessed
	e.preventedLossCLP = state.PreventedLossCLP
	e.autopoiesisCycle = state.AutopoiesisCycle
	e.simulatorRunning = state.SimulatorRunning
	return e, nil
}

// persistLocked writes a complete snapshot through a synced temporary file,
// then replaces the prior snapshot. Callers must hold e.mu for writing.
func (e *Engine) persistLocked() error {
	if e.persistencePath == "" {
		return nil
	}

	state := persistedState{
		Version:          persistenceVersion,
		Profiles:         e.profiles,
		Alerts:           e.alerts,
		Transactions:     e.transactions,
		TotalProcessed:   e.totalProcessed,
		PreventedLossCLP: e.preventedLossCLP,
		AutopoiesisCycle: e.autopoiesisCycle,
		SimulatorRunning: e.simulatorRunning,
	}
	data, err := json.MarshalIndent(state, "", "  ")
	if err != nil {
		return e.recordPersistenceError(err)
	}

	directory := filepath.Dir(e.persistencePath)
	if err := os.MkdirAll(directory, 0700); err != nil {
		return e.recordPersistenceError(err)
	}
	temporary, err := os.CreateTemp(directory, ".shieldguard-state-*.tmp")
	if err != nil {
		return e.recordPersistenceError(err)
	}
	temporaryPath := temporary.Name()
	defer os.Remove(temporaryPath)

	if err := temporary.Chmod(0600); err != nil {
		temporary.Close()
		return e.recordPersistenceError(err)
	}
	if _, err := temporary.Write(data); err != nil {
		temporary.Close()
		return e.recordPersistenceError(err)
	}
	if err := temporary.Sync(); err != nil {
		temporary.Close()
		return e.recordPersistenceError(err)
	}
	if err := temporary.Close(); err != nil {
		return e.recordPersistenceError(err)
	}
	if err := os.Rename(temporaryPath, e.persistencePath); err != nil {
		return e.recordPersistenceError(err)
	}
	e.persistenceError = ""
	return nil
}

func (e *Engine) recordPersistenceError(err error) error {
	e.persistenceError = err.Error()
	log.Printf("[!] Error al guardar estado persistente en %s: %v", e.persistencePath, err)
	return err
}
