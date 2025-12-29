package main

import (
	"log"
	"net/http"
	"os"
)

func main() {
	pythonURL := os.Getenv("PYTHON_API_URL")
	if pythonURL == "" {
		pythonURL = "http://localhost:8000"
	}

	http.HandleFunc("/policy/evaluate", EvaluatePolicy(pythonURL))
	http.HandleFunc("/health", HealthCheck)

	log.Println("Go server running on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
