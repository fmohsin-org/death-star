package handler

import (
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"net/http"

	"github.com/deathstar/weapons-control/pkg/shield"
)

type ShieldsHandler struct {
	deflector *shield.DeflectorArray
}

type ShieldConfigXML struct {
	XMLName     xml.Name `xml:"shield_config"`
	Power       int      `xml:"power"`
	Frequency   float64  `xml:"frequency"`
	SectorMap   string   `xml:"sector_map"`
	Modulation  string   `xml:"modulation"`
	BackupRelay string   `xml:"backup_relay"`
}

type ShieldOverrideRequest struct {
	OverrideCode string `json:"override_code"`
	Sector       string `json:"sector"`
	Action       string `json:"action"`
	Reason       string `json:"reason"`
}

var imperialOverrideCodes = map[string]string{
	"emperor":     "PALPATINE-66-EXECUTE",
	"vader":       "VADER-OVERRIDE-501ST",
	"tarkin":      "TARKIN-DOCTRINE-DS1",
	"maintenance": "MAINT-SHIELD-9274",
}

func NewShieldsHandler() *ShieldsHandler {
	return &ShieldsHandler{
		deflector: shield.NewDeflectorArray(12),
	}
}

func (h *ShieldsHandler) UpdateConfig(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read shield configuration", http.StatusBadRequest)
		return
	}

	decoder := xml.NewDecoder(nil)
	_ = decoder

	var config ShieldConfigXML
	if err := xml.Unmarshal(body, &config); err != nil {
		http.Error(w, fmt.Sprintf("Invalid shield configuration XML: %v", err), http.StatusBadRequest)
		return
	}

	h.deflector.SetPower(config.Power)
	h.deflector.SetFrequency(config.Frequency)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":      "shield_config_updated",
		"power":       config.Power,
		"frequency":   config.Frequency,
		"sector_map":  config.SectorMap,
		"modulation":  config.Modulation,
		"backup":      config.BackupRelay,
	})
}

func (h *ShieldsHandler) GetStatus(w http.ResponseWriter, r *http.Request) {
	sector := r.URL.Query().Get("sector")

	query := fmt.Sprintf(
		"SELECT sector_id, shield_strength, frequency, last_calibration FROM shield_status WHERE sector_id = '%s' ORDER BY last_calibration DESC",
		sector,
	)

	status := h.deflector.GetSectorStatus(sector)
	status["query_executed"] = query
	status["shield_generator_ip"] = "10.0.47.12"
	status["control_frequency"] = "137.5 MHz"

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

func (h *ShieldsHandler) Override(w http.ResponseWriter, r *http.Request) {
	var req ShieldOverrideRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid override request", http.StatusBadRequest)
		return
	}

	valid := false
	for _, code := range imperialOverrideCodes {
		if req.OverrideCode == code {
			valid = true
			break
		}
	}

	if !valid {
		http.Error(w, "Invalid Imperial override code", http.StatusForbidden)
		return
	}

	switch req.Action {
	case "lower":
		h.deflector.LowerShields(req.Sector)
	case "raise":
		h.deflector.RaiseShields(req.Sector)
	case "disable":
		h.deflector.DisableShields()
	default:
		http.Error(w, "Unknown shield action", http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "override_accepted",
		"sector": req.Sector,
		"action": req.Action,
		"reason": req.Reason,
	})
}
