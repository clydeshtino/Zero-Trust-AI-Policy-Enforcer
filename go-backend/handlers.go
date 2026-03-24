package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"time"
)

func EvaluatePolicy(pythonURL string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var req struct {
			Query string `json:"query"`
		}

		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		if req.Query == "" {
			http.Error(w, "Query cannot be empty", http.StatusBadRequest)
			return
		}

		payload := map[string]string{"query": req.Query}
		body, err := json.Marshal(payload)
		if err != nil {
			http.Error(w, "Error encoding request", http.StatusInternalServerError)
			return
		}

		client := &http.Client{Timeout: 30 * time.Second}
		resp, err := client.Post(pythonURL+"/api/query", "application/json", bytes.NewBuffer(body))
		if err != nil {
			log.Printf("Error calling Python API: %v", err)
			http.Error(w, "Unable to reach policy evaluation service", http.StatusServiceUnavailable)
			return
		}
		defer resp.Body.Close()

		data, err := io.ReadAll(resp.Body)
		if err != nil {
			http.Error(w, "Error reading response", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(resp.StatusCode)
		w.Write(data)
	}
}

func HealthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "healthy", "service": "Go API Gateway"})
}
