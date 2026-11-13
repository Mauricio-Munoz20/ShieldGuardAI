package engine

import (
	"context"
	"testing"
	"time"

	"shieldguard-backend/internal/mlclient"
	"shieldguard-backend/internal/models"
)

type fixedScorer struct {
	prediction *models.MLPrediction
}

func (f fixedScorer) Predict(context.Context, mlclient.Features) (*models.MLPrediction, error) {
	return f.prediction, nil
}

func TestShadowModelDoesNotChangeRuleDecision(t *testing.T) {
	eng := NewEngine()
	eng.SetMLScorer(fixedScorer{prediction: &models.MLPrediction{
		ExperimentalScore: 99,
		ModelVersion:      "test-model",
		ModelScope:        "synthetic",
	}})

	tx := &models.Transaction{
		ID:           "TX-NORMAL-ML-SHADOW",
		CardNumber:   "•••• 4821",
		AmountCLP:    12000,
		MCC:          "5411",
		MerchantName: "Market",
		Channel:      "POS_CHIP",
		City:         "La Serena",
		Country:      "CL",
		Timestamp:    time.Now(),
	}

	score, alert := eng.Evaluate(tx)
	if alert != nil {
		t.Fatal("shadow ML prediction must not create a rule alert")
	}
	if score.RiskLevel != "NORMAL" || score.RecommendedAction != "APPROVE" {
		t.Fatalf("shadow ML prediction changed operational decision: level=%s action=%s", score.RiskLevel, score.RecommendedAction)
	}
	if score.MLPrediction == nil || score.MLPrediction.ExperimentalScore != 99 {
		t.Fatalf("expected experimental prediction to be attached, got %+v", score.MLPrediction)
	}
}

func TestFlaggedTransactionDoesNotUpdateHistoricalBaseline(t *testing.T) {
	eng := NewEngine()
	originalAverage := eng.profiles["•••• 4821"].HistoricalAvgCLP

	tx := &models.Transaction{
		ID:           "TX-FRAUD-1",
		CardNumber:   "•••• 4821",
		AmountCLP:    230000,
		MCC:          "5732",
		MerchantName: "Electronics shop",
		Channel:      "ECOMMERCE_CNP",
		City:         "Santiago",
		Country:      "CL",
		Timestamp:    time.Now(),
		IsSuspicious: true,
	}

	_, alert := eng.Evaluate(tx)
	if alert == nil {
		t.Fatal("expected suspicious transaction to create an alert")
	}
	if got := eng.profiles[tx.CardNumber].HistoricalAvgCLP; got != originalAverage {
		t.Fatalf("flagged transaction changed historical average to %d, want %d", got, originalAverage)
	}
}

func TestFirstFlaggedTransactionDoesNotSeedHistoricalBaseline(t *testing.T) {
	eng := NewEngine()
	tx := &models.Transaction{
		ID:           "TX-NEW-FRAUD-1",
		CardNumber:   "•••• 0000",
		AmountCLP:    230000,
		Timestamp:    time.Now(),
		IsSuspicious: true,
	}

	_, alert := eng.Evaluate(tx)
	if alert == nil {
		t.Fatal("expected suspicious transaction to create an alert")
	}
	profile := eng.profiles[tx.CardNumber]
	if profile.HistoricalAvgCLP != 0 || profile.TxCount != 0 {
		t.Fatalf("first flagged transaction seeded baseline (average=%d, count=%d), want 0 and 0", profile.HistoricalAvgCLP, profile.TxCount)
	}
}
