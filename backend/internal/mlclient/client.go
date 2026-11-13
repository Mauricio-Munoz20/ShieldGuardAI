package mlclient

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"shieldguard-backend/internal/models"
)

type Features struct {
	AmountCLP          int64   `json:"amount_clp"`
	AmountVsBaseline   float64 `json:"amount_vs_baseline"`
	TxCountCard        int     `json:"tx_count_card"`
	MinutesSinceLastTx float64 `json:"minutes_since_last_tx"`
	Channel            string  `json:"channel"`
	MCC                string  `json:"mcc"`
	CityChanged        bool    `json:"city_changed"`
}

type request struct {
	Features Features `json:"features"`
}

type response struct {
	ExperimentalScore     float64  `json:"experimentalScore"`
	ModelVersion          string   `json:"modelVersion"`
	ModelScope            string   `json:"modelScope"`
	ProbabilityCalibrated bool     `json:"probabilityCalibrated"`
	ReasonCodes           []string `json:"reasonCodes"`
	Error                 string   `json:"error"`
}

type Scorer interface {
	Predict(context.Context, Features) (*models.MLPrediction, error)
}

type Client struct {
	baseURL string
	http    *http.Client
}

func New(baseURL string) *Client {
	return &Client{
		baseURL: strings.TrimRight(baseURL, "/"),
		http:    &http.Client{Timeout: 120 * time.Millisecond},
	}
}

func (c *Client) Predict(ctx context.Context, features Features) (*models.MLPrediction, error) {
	body, err := json.Marshal(request{Features: features})
	if err != nil {
		return nil, fmt.Errorf("encode model request: %w", err)
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.baseURL+"/internal/v1/predict", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create model request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.http.Do(req)
	if err != nil {
		return nil, fmt.Errorf("model service unavailable: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("model service returned status %d", resp.StatusCode)
	}
	var prediction response
	if err := json.NewDecoder(resp.Body).Decode(&prediction); err != nil {
		return nil, fmt.Errorf("decode model response: %w", err)
	}
	if prediction.ExperimentalScore < 0 || prediction.ExperimentalScore > 100 || prediction.ModelVersion == "" {
		return nil, fmt.Errorf("model service returned an invalid prediction")
	}
	return &models.MLPrediction{
		ExperimentalScore:     int(prediction.ExperimentalScore + 0.5),
		ModelVersion:          prediction.ModelVersion,
		ModelScope:            prediction.ModelScope,
		ProbabilityCalibrated: prediction.ProbabilityCalibrated,
		ReasonCodes:           prediction.ReasonCodes,
	}, nil
}
