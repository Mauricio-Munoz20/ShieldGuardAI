package models

import "time"

// Transaction represents an incoming payment transaction (ISO 8583 mapped payload)
type Transaction struct {
	ID           string    `json:"id"`
	CardNumber   string    `json:"cardNumber"` // Masked, e.g. "•••• 4821"
	AccountID    string    `json:"accountId"`
	AmountCLP    int64     `json:"amountClp"`
	Currency     string    `json:"currency"`
	MCC          string    `json:"mcc"` // Merchant Category Code (e.g. 5411 = Supermarket, 5732 = Electronics)
	MerchantName string    `json:"merchantName"`
	Channel      string    `json:"channel"` // "POS_CHIP", "POS_CONTACTLESS", "ECOMMERCE_CNP", "ATM"
	City         string    `json:"city"`
	Country      string    `json:"country"`
	Timestamp    time.Time `json:"timestamp"`
	IsSuspicious bool      `json:"isSuspicious"`
}

// RiskScore contains the evaluation performed by ShieldGuard AI's behavioral engine
type RiskScore struct {
	Score             int           `json:"score"`             // 0 to 100%
	RiskLevel         string        `json:"riskLevel"`         // "NORMAL", "REVISAR", "AUTOFRAUDE_PROBABLE"
	Confidence        int           `json:"confidence"`        // Confidence %
	TriggeredRules    []string      `json:"triggeredRules"`    // Human-readable explainable factors
	RecommendedAction string        `json:"recommendedAction"` // "APPROVE", "FLAG_REVIEW", "PROACTIVE_FREEZE"
	MLPrediction      *MLPrediction `json:"mlPrediction,omitempty"`
}

// MLPrediction is an experimental shadow prediction. It never drives the
// current rule-based risk level or recommended action.
type MLPrediction struct {
	ExperimentalScore     int      `json:"experimentalScore"`
	ModelVersion          string   `json:"modelVersion"`
	ModelScope            string   `json:"modelScope"`
	ProbabilityCalibrated bool     `json:"probabilityCalibrated"`
	ReasonCodes           []string `json:"reasonCodes"`
}

// Alert is an operational incident surfaced on the Risk Console
type Alert struct {
	ID              string     `json:"id"`
	TransactionID   string     `json:"transactionId"`
	CardNumber      string     `json:"cardNumber"`
	AmountCLP       int64      `json:"amountClp"`
	MerchantName    string     `json:"merchantName"`
	RiskScore       RiskScore  `json:"riskScore"`
	Status          string     `json:"status"` // "PENDIENTE", "CONGELADO_PREVENTIVO", "REVERTIDO", "FRAUDE_CONFIRMADO"
	CreatedAt       time.Time  `json:"createdAt"`
	ActionTakenBy   string     `json:"actionTakenBy,omitempty"`
	ActionTimestamp *time.Time `json:"actionTimestamp,omitempty"`
}

// CardStatus tracks the current operational state of a card in the backend
type CardStatus struct {
	CardNumber       string     `json:"cardNumber"`
	IsFrozen         bool       `json:"isFrozen"`
	FrozenReason     string     `json:"frozenReason,omitempty"`
	FrozenAt         *time.Time `json:"frozenAt,omitempty"`
	HistoricalAvgCLP int64      `json:"historicalAvgClp"`
	TxCountLast24h   int        `json:"txCountLast24h"`
}

// SystemStats represents aggregate metrics for the dashboard
type SystemStats struct {
	TotalProcessed   int64   `json:"totalProcessed"`
	TotalAlerts      int     `json:"totalAlerts"`
	ActiveFreezes    int     `json:"activeFreezes"`
	PreventedLossCLP int64   `json:"preventedLossClp"`
	AverageLatencyMs float64 `json:"averageLatencyMs"`
	AutopoiesisCycle int     `json:"autopoiesisCycle"`
}

// WSMessage is the payload sent over WebSocket to the Angular frontend
type WSMessage struct {
	Type    string      `json:"type"` // "TRANSACTION", "ALERT", "CARD_STATUS", "STATS"
	Payload interface{} `json:"payload"`
}
