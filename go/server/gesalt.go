package server

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/gorilla/mux"
	"github.com/nave433-blip/N4V3R41N-Suite/go/utils"
)

type ActivationRequest struct {
	UDID        string `json:"UDID"`
	DeviceModel string `json:"DeviceModel"`
}

func StartGesaltServer() {
	utils.LogInfo("Starting Gesalt Activation Server on 0.0.0.0:8000")
	r := mux.NewRouter()
	r.HandleFunc("/activation", func(w http.ResponseWriter, r *http.Request) {
		utils.LogInfo("Received activation request")
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "Activated",
			"time":   time.Now().Unix(),
		})
	}).Methods("POST")

	http.Handle("/", r)
	log.Fatal(http.ListenAndServe(":8000", nil))
}
