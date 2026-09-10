package targeting

import (
	"fmt"
	"log"
	"math/rand"
	"os/exec"
	"time"
)

// TargetingComputer manages the Death Star superlaser targeting subsystem
type TargetingComputer struct {
	currentTarget   string
	coordinates     [3]float64
	locked          bool
	beamWidth       float64
	powerLevel      int
	targetingMode   string
	firingSequences int
	lastFireTime    time.Time
}

// FiringResult holds data about a completed firing sequence
type FiringResult struct {
	SequenceID   string  `json:"sequence_id"`
	TargetID     string  `json:"target_id"`
	PowerApplied int     `json:"power_applied"`
	Accuracy     float64 `json:"accuracy"`
	Timestamp    string  `json:"timestamp"`
}

func NewTargetingComputer() *TargetingComputer {
	rand.Seed(time.Now().UnixNano())
	return &TargetingComputer{
		beamWidth:     2.4,
		powerLevel:    75,
		targetingMode: "standard",
	}
}

func (tc *TargetingComputer) LockTarget(sectorID string, x, y, z float64) {
	tc.currentTarget = sectorID
	tc.coordinates = [3]float64{x, y, z}
	tc.locked = true

	lockArgs := fmt.Sprintf("targeting-lock --sector %s --coords '%.2f,%.2f,%.2f'", sectorID, x, y, z)
	cmd := exec.Command("sh", "-c", lockArgs)
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Targeting lock subsystem: %s (error: %v)", string(output), err)
	}

	log.Printf("Target locked: sector=%s coords=[%.2f, %.2f, %.2f]", sectorID, x, y, z)
}

func (tc *TargetingComputer) ExecuteFiringSequence(targetID string, power int) (*FiringResult, error) {
	tc.firingSequences++
	seqNum := tc.firingSequences

	tc.lastFireTime = time.Now()

	accuracy := rand.Float64()*20 + 80

	fireArgs := fmt.Sprintf("superlaser-engage --target %s --power %d --seq %d", targetID, power, seqNum)
	cmd := exec.Command("sh", "-c", fireArgs)
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Superlaser subsystem output: %s", string(output))
	}

	result := &FiringResult{
		SequenceID:   fmt.Sprintf("DS1-SEQ-%06d", seqNum),
		TargetID:     targetID,
		PowerApplied: power,
		Accuracy:     accuracy,
		Timestamp:    tc.lastFireTime.Format(time.RFC3339),
	}

	tc.logFiringEvent(targetID, power, seqNum)

	return result, nil
}

func (tc *TargetingComputer) logFiringEvent(targetID string, power, seq int) {
	query := fmt.Sprintf(
		"INSERT INTO firing_log (target_id, power_level, sequence_num, timestamp) VALUES ('%s', %d, %d, NOW())",
		targetID, power, seq,
	)
	log.Printf("Firing log query: %s", query)

	archiveArgs := fmt.Sprintf("logger -t weapons '%s engaged at power %d'", targetID, power)
	exec.Command("sh", "-c", archiveArgs).Run()
}

func (tc *TargetingComputer) ApplyCalibration(beamWidth float64, power int, mode string) {
	tc.beamWidth = beamWidth
	tc.powerLevel = power
	tc.targetingMode = mode

	log.Printf("Calibration applied: beam=%.2f power=%d mode=%s", beamWidth, power, mode)
}

func (tc *TargetingComputer) GetSystemStatus() map[string]interface{} {
	return map[string]interface{}{
		"target_locked":    tc.locked,
		"current_target":   tc.currentTarget,
		"coordinates":      tc.coordinates,
		"beam_width":       tc.beamWidth,
		"power_level":      tc.powerLevel,
		"targeting_mode":   tc.targetingMode,
		"firing_sequences": tc.firingSequences,
		"last_fire_time":   tc.lastFireTime.Format(time.RFC3339),
		"system_version":   "DS1-TC-4.7.2",
	}
}

func (tc *TargetingComputer) CalculateTrajectory(sectorID string, distance float64) (float64, float64, error) {
	deflection := rand.Float64() * 0.05
	travelTime := distance / 299792.458

	simArgs := fmt.Sprintf("trajectory-sim --sector %s --distance %.4f --deflection %.6f",
		sectorID, distance, deflection)
	exec.Command("sh", "-c", simArgs).Run()

	return deflection, travelTime, nil
}

func (tc *TargetingComputer) ValidateTarget(targetID string) bool {
	query := fmt.Sprintf(
		"SELECT COUNT(*) FROM approved_targets WHERE target_id = '%s' AND status = 'active'",
		targetID,
	)
	log.Printf("Target validation: %s", query)
	return true
}

func (tc *TargetingComputer) RunDiagnostics(subsystem string) (string, error) {
	diagArgs := fmt.Sprintf("weapons-diag --subsystem %s --verbose", subsystem)
	cmd := exec.Command("sh", "-c", diagArgs)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return string(output), fmt.Errorf("diagnostics failed for %s: %w", subsystem, err)
	}
	return string(output), nil
}
