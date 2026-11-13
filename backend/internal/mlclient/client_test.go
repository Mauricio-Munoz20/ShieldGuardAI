package mlclient

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestPredictSendsFeaturesAndParsesShadowResult(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost || r.URL.Path != "/internal/v1/predict" {
			t.Fatalf("unexpected request %s %s", r.Method, r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"experimentalScore":82.4,"modelVersion":"catboost-demo-1","modelScope":"synthetic","probabilityCalibrated":false,"reasonCodes":["card_not_present_channel"]}`))
	}))
	defer server.Close()

	client := New(server.URL)
	prediction, err := client.Predict(context.Background(), Features{
		AmountCLP: 120000, AmountVsBaseline: 3.4, TxCountCard: 21,
		MinutesSinceLastTx: 37, Channel: "ECOMMERCE_CNP", MCC: "5732", CityChanged: true,
	})
	if err != nil {
		t.Fatalf("Predict returned error: %v", err)
	}
	if prediction.ExperimentalScore != 82 || prediction.ModelVersion != "catboost-demo-1" {
		t.Fatalf("unexpected prediction: %+v", prediction)
	}
	if prediction.ProbabilityCalibrated || len(prediction.ReasonCodes) != 1 {
		t.Fatalf("unexpected model metadata: %+v", prediction)
	}
}
