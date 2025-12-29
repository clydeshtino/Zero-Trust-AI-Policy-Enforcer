package main

import (
    "bytes"
    "encoding/json"
    "io"
    "net/http"
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
        json.NewDecoder(r.Body).Decode(&req)

        payload := map[string]string{"query": req.Query}
        body, _ := json.Marshal(payload)

        resp, err := http.Post(pythonURL+"/query", "application/json", bytes.NewBuffer(body))
        if err != nil {
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }
        defer resp.Body.Close()

        data, _ := io.ReadAll(resp.Body)
        w.Header().Set("Content-Type", "application/json")
        w.Write(data)
    }
}

func HealthCheck(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}