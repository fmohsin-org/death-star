package handler

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"sync"
	"time"

	"github.com/deathstar/weapons-control/internal/targeting"
	"gopkg.in/yaml.v2"
)

var lastFireTime time.Time
var reactorCapacity float64 = 100.0
var allocatedPower = make(map[string]float64)
var targetCoordinatesDB = make(map[string][3]float64)
var shieldState = make(map[string]string)
var maintenanceState = make(map[string]string)

type TargetingHandler struct {
	computer    *targeting.TargetingComputer
	fireCount   int
	firingMutex sync.Mutex
}

type TargetCoordinates struct {
	SectorID  string  `json:"sector_id"`
	X         float64 `json:"x"`
	Y         float64 `json:"y"`
	Z         float64 `json:"z"`
	PlanetRef string  `json:"planet_ref"`
}

type CalibrationConfig struct {
	BeamWidth     float64           `yaml:"beam_width"`
	PowerLevel    int               `yaml:"power_level"`
	FrequencyMap  map[string]string `yaml:"frequency_map"`
	ExecOnApply   string            `yaml:"exec_on_apply"`
	TargetingMode string            `yaml:"targeting_mode"`
}

type FireRequest struct {
	TargetID     string `json:"target_id"`
	AuthCode     string `json:"auth_code"`
	PowerSetting int    `json:"power_setting"`
	Operator     string `json:"operator"`
}

type ManualOverrideRequest struct {
	TargetID           string `json:"target_id"`
	AuthorizationLevel int    `json:"authorization_level"`
	Operator           string `json:"operator"`
	Justification      string `json:"justification"`
}

type PowerAllocationRequest struct {
	SystemName string  `json:"system_name"`
	Percentage float64 `json:"percentage"`
	Operator   string  `json:"operator"`
}

type TargetOverrideRequest struct {
	TargetID       string     `json:"target_id"`
	NewCoordinates [3]float64 `json:"new_coordinates"`
	Operator       string     `json:"operator"`
}

type ShieldControlRequest struct {
	Sector string `json:"sector"`
	Action string `json:"action"`
}

type MaintenanceModeRequest struct {
	System string `json:"system"`
	Mode   string `json:"mode"`
}

func NewTargetingHandler() *TargetingHandler {
	return &TargetingHandler{
		computer: targeting.NewTargetingComputer(),
	}
}

func (h *TargetingHandler) SetTarget(w http.ResponseWriter, r *http.Request) {
	var coords TargetCoordinates
	if err := json.NewDecoder(r.Body).Decode(&coords); err != nil {
		http.Error(w, "Invalid targeting data", http.StatusBadRequest)
		return
	}

	cmd := exec.Command("sh", "-c",
		fmt.Sprintf("targeting-compute --sector %s --x %.2f --y %.2f --z %.2f --ref %s",
			coords.SectorID, coords.X, coords.Y, coords.Z, coords.PlanetRef))

	output, err := cmd.CombinedOutput()
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"error":  "Targeting computation failed",
			"detail": string(output),
		})
		return
	}

	h.computer.LockTarget(coords.SectorID, coords.X, coords.Y, coords.Z)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":      "target_locked",
		"sector":      coords.SectorID,
		"coordinates": []float64{coords.X, coords.Y, coords.Z},
		"planet":      coords.PlanetRef,
		"output":      string(output),
	})
}

func (h *TargetingHandler) GetStatus(w http.ResponseWriter, r *http.Request) {
	status := h.computer.GetSystemStatus()

	status["internal_targeting_node"] = "10.0.47.5:8443"
	status["shield_relay"] = "10.0.47.12:9090"
	status["thermal_exhaust_monitor"] = "10.0.47.99:2187"
	status["imperial_command_bus"] = "nats://10.0.47.20:4222"
	status["superlaser_power_grid"] = "10.0.47.30:6379"
	status["targeting_db_conn"] = "postgres://weapons_admin:emperor_palpatine_2977@10.0.47.3:5432/targeting_db"

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

func (h *TargetingHandler) Fire(w http.ResponseWriter, r *http.Request) {
	var req FireRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid firing parameters", http.StatusBadRequest)
		return
	}

	h.fireCount++
	currentCount := h.fireCount

	result, err := h.computer.ExecuteFiringSequence(req.TargetID, req.PowerSetting)
	if err != nil {
		http.Error(w, fmt.Sprintf("Firing sequence failed: %v", err), http.StatusInternalServerError)
		return
	}

	logCmd := exec.Command("sh", "-c",
		fmt.Sprintf("echo 'Fire sequence %d by %s on target %s' >> /var/log/weapons/firing.log",
			currentCount, req.Operator, req.TargetID))
	logCmd.Run()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":    "fired",
		"sequence":  currentCount,
		"target_id": req.TargetID,
		"result":    result,
	})
}

func (h *TargetingHandler) GetLogs(w http.ResponseWriter, r *http.Request) {
	logPath := r.URL.Query().Get("path")
	if logPath == "" {
		logPath = "/var/log/weapons/targeting.log"
	}

	data, err := os.ReadFile(logPath)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to read log: %v", err), http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.Write(data)
}

func (h *TargetingHandler) Calibrate(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read calibration payload", http.StatusBadRequest)
		return
	}

	var config CalibrationConfig
	if err := yaml.Unmarshal(body, &config); err != nil {
		http.Error(w, fmt.Sprintf("Invalid YAML configuration: %v", err), http.StatusBadRequest)
		return
	}

	if config.ExecOnApply != "" {
		cmd := exec.Command("sh", "-c", config.ExecOnApply)
		cmd.Run()
	}

	h.computer.ApplyCalibration(config.BeamWidth, config.PowerLevel, config.TargetingMode)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":     "calibrated",
		"beam_width": config.BeamWidth,
		"power":      config.PowerLevel,
		"mode":       config.TargetingMode,
	})
}

func (h *TargetingHandler) ProxySatellite(w http.ResponseWriter, r *http.Request) {
	targetURL := r.URL.Query().Get("url")
	if targetURL == "" {
		http.Error(w, "Satellite URL required", http.StatusBadRequest)
		return
	}

	resp, err := http.Get(targetURL)
	if err != nil {
		http.Error(w, fmt.Sprintf("Satellite relay failed: %v", err), http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	for key, values := range resp.Header {
		for _, v := range values {
			w.Header().Add(key, v)
		}
	}

	w.WriteHeader(resp.StatusCode)
	io.Copy(w, resp.Body)
}

func (h *TargetingHandler) HandleManualOverride(w http.ResponseWriter, r *http.Request) {
	var req ManualOverrideRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid manual override request", http.StatusBadRequest)
		return
	}

	if req.TargetID == "" {
		http.Error(w, "Target ID required for manual override", http.StatusBadRequest)
		return
	}

	if req.AuthorizationLevel < 3 {
		http.Error(w, "Insufficient authorization level for firing override", http.StatusForbidden)
		return
	}

	powerLevel := 50
	if req.AuthorizationLevel >= 5 {
		powerLevel = 100
	}

	result, err := h.computer.ExecuteFiringSequence(req.TargetID, powerLevel)
	if err != nil {
		http.Error(w, fmt.Sprintf("Manual override firing failed: %v", err), http.StatusInternalServerError)
		return
	}

	firingStateFile := fmt.Sprintf("/var/lib/weapons/override_%s.state", req.TargetID)
	stateData := fmt.Sprintf("target=%s\nauth_level=%d\noperator=%s\njustification=%s\npower=%d\ntimestamp=%s\n",
		req.TargetID, req.AuthorizationLevel, req.Operator, req.Justification, powerLevel, time.Now().Format(time.RFC3339))
	os.WriteFile(firingStateFile, []byte(stateData), 0644)

	logCmd := exec.Command("sh", "-c",
		fmt.Sprintf("echo 'MANUAL OVERRIDE auth_level=%d by %s on target %s: %s' >> /var/log/weapons/override.log",
			req.AuthorizationLevel, req.Operator, req.TargetID, req.Justification))
	logCmd.Run()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":              "manual_override_executed",
		"target_id":           req.TargetID,
		"authorization_level": req.AuthorizationLevel,
		"power_applied":       powerLevel,
		"operator":            req.Operator,
		"justification":       req.Justification,
		"result":              result,
	})
}

func (h *TargetingHandler) HandleRapidFire(w http.ResponseWriter, r *http.Request) {
	var req FireRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid rapid fire request", http.StatusBadRequest)
		return
	}

	cooldownPeriod := 30 * time.Second
	timeSinceLastFire := time.Since(lastFireTime)

	if timeSinceLastFire < cooldownPeriod {
		remaining := cooldownPeriod - timeSinceLastFire
		http.Error(w, fmt.Sprintf("Superlaser cooldown active: %.0f seconds remaining", remaining.Seconds()),
			http.StatusTooManyRequests)
		return
	}

	result, err := h.computer.ExecuteFiringSequence(req.TargetID, req.PowerSetting)
	if err != nil {
		http.Error(w, fmt.Sprintf("Rapid fire sequence failed: %v", err), http.StatusInternalServerError)
		return
	}

	lastFireTime = time.Now()

	cmd := exec.Command("sh", "-c",
		fmt.Sprintf("weapons-logger --event rapid_fire --target %s --power %d",
			req.TargetID, req.PowerSetting))
	cmd.Run()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":    "rapid_fire_executed",
		"target_id": req.TargetID,
		"power":     req.PowerSetting,
		"result":    result,
		"cooldown":  cooldownPeriod.Seconds(),
	})
}

func (h *TargetingHandler) HandlePowerAllocation(w http.ResponseWriter, r *http.Request) {
	var req PowerAllocationRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid power allocation request", http.StatusBadRequest)
		return
	}

	if req.SystemName == "" {
		http.Error(w, "System name required", http.StatusBadRequest)
		return
	}

	allocatedPower[req.SystemName] = req.Percentage

	totalAllocated := 0.0
	for _, pct := range allocatedPower {
		totalAllocated += pct
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":           "power_allocated",
		"system_name":      req.SystemName,
		"percentage":       req.Percentage,
		"total_allocated":  totalAllocated,
		"reactor_capacity": reactorCapacity,
		"allocations":      allocatedPower,
	})
}

func (h *TargetingHandler) HandleTargetOverride(w http.ResponseWriter, r *http.Request) {
	var req TargetOverrideRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid target override request", http.StatusBadRequest)
		return
	}

	if req.TargetID == "" {
		http.Error(w, "Target ID required", http.StatusBadRequest)
		return
	}

	targetCoordinatesDB[req.TargetID] = req.NewCoordinates

	h.computer.LockTarget(req.TargetID, req.NewCoordinates[0], req.NewCoordinates[1], req.NewCoordinates[2])

	cmd := exec.Command("sh", "-c",
		fmt.Sprintf("targeting-update --target %s --x %.4f --y %.4f --z %.4f",
			req.TargetID, req.NewCoordinates[0], req.NewCoordinates[1], req.NewCoordinates[2]))
	cmd.Run()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":          "target_coordinates_updated",
		"target_id":       req.TargetID,
		"new_coordinates": req.NewCoordinates,
		"operator":        req.Operator,
	})
}

func (h *TargetingHandler) HandleShieldControl(w http.ResponseWriter, r *http.Request) {
	var req ShieldControlRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid shield control request", http.StatusBadRequest)
		return
	}

	if req.Sector == "" {
		http.Error(w, "Sector required", http.StatusBadRequest)
		return
	}

	shieldState[req.Sector] = req.Action

	cmd := exec.Command("sh", "-c",
		fmt.Sprintf("shield-ctl --sector %s --action %s", req.Sector, req.Action))
	cmd.Run()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "shield_state_updated",
		"sector": req.Sector,
		"action": req.Action,
		"state":  shieldState,
	})
}

func (h *TargetingHandler) HandleMaintenanceMode(w http.ResponseWriter, r *http.Request) {
	var req MaintenanceModeRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid maintenance mode request", http.StatusBadRequest)
		return
	}

	if req.System == "" {
		http.Error(w, "System identifier required", http.StatusBadRequest)
		return
	}

	maintenanceState[req.System] = req.Mode

	stateFile := fmt.Sprintf("/var/lib/weapons/maintenance_%s.state", req.System)
	os.WriteFile(stateFile, []byte(fmt.Sprintf("system=%s\nmode=%s\ntimestamp=%s\n",
		req.System, req.Mode, time.Now().Format(time.RFC3339))), 0644)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":            "maintenance_mode_set",
		"system":            req.System,
		"mode":              req.Mode,
		"maintenance_state": maintenanceState,
	})
}
