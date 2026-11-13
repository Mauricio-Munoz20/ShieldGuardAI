package simulator

import (
	"fmt"
	"math/rand"
	"sync"
	"time"

	"shieldguard-backend/internal/engine"
	"shieldguard-backend/internal/models"
)

type OnTransactionCallback func(tx *models.Transaction, score *models.RiskScore, alert *models.Alert)

type Simulator struct {
	mu         sync.Mutex
	engine     *engine.Engine
	callback   OnTransactionCallback
	isRunning  bool
	stopChan   chan struct{}
	normalPool []models.Transaction
}

func NewSimulator(eng *engine.Engine, cb OnTransactionCallback) *Simulator {
	s := &Simulator{
		engine:    eng,
		callback:  cb,
		stopChan:  make(chan struct{}),
		isRunning: false,
	}
	s.initNormalPool()
	return s
}

func (s *Simulator) initNormalPool() {
	s.normalPool = []models.Transaction{
		{CardNumber: "•••• 1142", AmountCLP: 14500, MCC: "5411", MerchantName: "Lider Express", Channel: "POS_CONTACTLESS", City: "Santiago", Country: "CL"},
		{CardNumber: "•••• 3391", AmountCLP: 32000, MCC: "5541", MerchantName: "Copec Pronto", Channel: "POS_CHIP", City: "La Serena", Country: "CL"},
		{CardNumber: "•••• 5520", AmountCLP: 4500, MCC: "5814", MerchantName: "Starbucks Mall Plaza", Channel: "POS_CONTACTLESS", City: "Coquimbo", Country: "CL"},
		{CardNumber: "•••• 8812", AmountCLP: 18990, MCC: "5912", MerchantName: "Farmacias Ahumada", Channel: "POS_CHIP", City: "Coquimbo", Country: "CL"},
		{CardNumber: "•••• 6643", AmountCLP: 8990, MCC: "4899", MerchantName: "Netflix Mensual", Channel: "ECOMMERCE_CNP", City: "Santiago", Country: "CL"},
		{CardNumber: "•••• 2219", AmountCLP: 27500, MCC: "5411", MerchantName: "Jumbo Peñuelas", Channel: "POS_CHIP", City: "Coquimbo", Country: "CL"},
	}
}

// Start launches the background transaction generator
func (s *Simulator) Start() {
	s.mu.Lock()
	if s.isRunning {
		s.mu.Unlock()
		return
	}
	s.isRunning = true
	stopChan := make(chan struct{})
	s.stopChan = stopChan
	s.mu.Unlock()

	go s.runLoop(stopChan)
}

// Stop pauses the generator
func (s *Simulator) Stop() {
	s.mu.Lock()
	defer s.mu.Unlock()
	if !s.isRunning {
		return
	}
	s.isRunning = false
	close(s.stopChan)
}

// IsRunning returns whether the generator is currently active
func (s *Simulator) IsRunning() bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.isRunning
}

func (s *Simulator) runLoop(stopChan <-chan struct{}) {
	ticker := time.NewTicker(2200 * time.Millisecond)
	defer ticker.Stop()

	// Every 8-12 normal transactions, inject an autofraud case
	txCount := 0

	for {
		select {
		case <-stopChan:
			return
		case <-ticker.C:
			txCount++
			if txCount%9 == 0 {
				// Automatic periodic autofraud injection
				s.InjectScenario("AUTOFRAUDE_RETAIL")
			} else {
				s.generateNormal()
			}
		}
	}
}

func (s *Simulator) generateNormal() {
	sample := s.normalPool[rand.Intn(len(s.normalPool))]
	tx := models.Transaction{
		ID:           fmt.Sprintf("TX-%d", time.Now().UnixNano()%1000000),
		CardNumber:   sample.CardNumber,
		AccountID:    fmt.Sprintf("ACC-%s", sample.CardNumber[len(sample.CardNumber)-4:]),
		AmountCLP:    sample.AmountCLP + int64(rand.Intn(4000)-2000),
		Currency:     "CLP",
		MCC:          sample.MCC,
		MerchantName: sample.MerchantName,
		Channel:      sample.Channel,
		City:         sample.City,
		Country:      sample.Country,
		Timestamp:    time.Now(),
		IsSuspicious: false,
	}

	score, alert := s.engine.Evaluate(&tx)
	if s.callback != nil {
		s.callback(&tx, score, alert)
	}
}

// InjectScenario allows manual or automated triggering of specific fraud patterns
func (s *Simulator) InjectScenario(scenarioType string) (*models.Transaction, *models.RiskScore, *models.Alert) {
	var tx models.Transaction

	switch scenarioType {
	case "AUTOFRAUDE_RETAIL":
		// Retail electronics scenario for the console demo. The score is calculated from the active profile.
		tx = models.Transaction{
			ID:           fmt.Sprintf("TX-AF-%d", time.Now().UnixNano()%100000),
			CardNumber:   "•••• 4821",
			AccountID:    "ACC-4821",
			AmountCLP:    230000,
			Currency:     "CLP",
			MCC:          "5732", // Electronics
			MerchantName: "MercadoLibre Chile - Smart TV",
			Channel:      "ECOMMERCE_CNP",
			City:         "Santiago",
			Country:      "CL",
			Timestamp:    time.Now(),
			IsSuspicious: true,
		}

	case "SIMULTANEO_ATM":
		// Remote eCommerce scenario for the console demo. The score is calculated from the active profile.
		tx = models.Transaction{
			ID:           fmt.Sprintf("TX-AF-%d", time.Now().UnixNano()%100000),
			CardNumber:   "•••• 7754",
			AccountID:    "ACC-7754",
			AmountCLP:    84990,
			Currency:     "CLP",
			MCC:          "5311", // Department Store
			MerchantName: "Falabella.com eCommerce",
			Channel:      "ECOMMERCE_CNP",
			City:         "Miami / Proxy US",
			Country:      "US",
			Timestamp:    time.Now(),
			IsSuspicious: true,
		}

	case "MICRO_BURST":
		// Small online purchase scenario for the console demo. The score is calculated from the active profile.
		tx = models.Transaction{
			ID:           fmt.Sprintf("TX-AF-%d", time.Now().UnixNano()%100000),
			CardNumber:   "•••• 9032",
			AccountID:    "ACC-9032",
			AmountCLP:    12500,
			Currency:     "CLP",
			MCC:          "7995", // Gambling / Crypto micro
			MerchantName: "BetGlobal Gaming",
			Channel:      "ECOMMERCE_CNP",
			City:         "Valparaíso",
			Country:      "CL",
			Timestamp:    time.Now(),
			IsSuspicious: true,
		}

	default:
		tx = models.Transaction{
			ID:           fmt.Sprintf("TX-AF-%d", time.Now().UnixNano()%100000),
			CardNumber:   "•••• 4821",
			AccountID:    "ACC-4821",
			AmountCLP:    175000,
			Currency:     "CLP",
			MCC:          "5732",
			MerchantName: "PC Factory Online",
			Channel:      "ECOMMERCE_CNP",
			City:         "Santiago",
			Country:      "CL",
			Timestamp:    time.Now(),
			IsSuspicious: true,
		}
	}

	score, alert := s.engine.Evaluate(&tx)
	if s.callback != nil {
		s.callback(&tx, score, alert)
	}

	return &tx, score, alert
}
