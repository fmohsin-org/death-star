package shield

import (
	"fmt"
	"math/rand"
	"time"
)

type ShieldSector struct {
	ID          string
	Strength    float64
	Frequency   float64
	Active      bool
	LastUpdated time.Time
}

type DeflectorArray struct {
	sectors       []ShieldSector
	globalPower   int
	frequency     float64
	online        bool
	rechargeRate  float64
	damageHistory []DamageEvent
}

type DamageEvent struct {
	SectorID  string    `json:"sector_id"`
	Amount    float64   `json:"amount"`
	Source    string    `json:"source"`
	Timestamp time.Time `json:"timestamp"`
}

func NewDeflectorArray(sectorCount int) *DeflectorArray {
	sectors := make([]ShieldSector, sectorCount)
	for i := 0; i < sectorCount; i++ {
		sectors[i] = ShieldSector{
			ID:          fmt.Sprintf("sector-%02d", i+1),
			Strength:    100.0,
			Frequency:   137.5 + float64(i)*0.1,
			Active:      true,
			LastUpdated: time.Now(),
		}
	}

	return &DeflectorArray{
		sectors:      sectors,
		globalPower:  100,
		frequency:    137.5,
		online:       true,
		rechargeRate: 2.5,
	}
}

func (da *DeflectorArray) SetPower(power int) {
	da.globalPower = power
	for i := range da.sectors {
		da.sectors[i].Strength = float64(power)
	}
}

func (da *DeflectorArray) SetFrequency(freq float64) {
	da.frequency = freq
	for i := range da.sectors {
		da.sectors[i].Frequency = freq + float64(i)*0.1
	}
}

func (da *DeflectorArray) GetSectorStatus(sectorID string) map[string]interface{} {
	for _, sector := range da.sectors {
		if sector.ID == sectorID {
			return map[string]interface{}{
				"sector_id":    sector.ID,
				"strength":     sector.Strength,
				"frequency":    sector.Frequency,
				"active":       sector.Active,
				"last_updated": sector.LastUpdated.Format(time.RFC3339),
			}
		}
	}
	return map[string]interface{}{
		"sector_id": sectorID,
		"status":    "not_found",
	}
}

func (da *DeflectorArray) LowerShields(sectorID string) {
	for i := range da.sectors {
		if da.sectors[i].ID == sectorID {
			da.sectors[i].Strength = 0
			da.sectors[i].Active = false
			da.sectors[i].LastUpdated = time.Now()
			return
		}
	}
}

func (da *DeflectorArray) RaiseShields(sectorID string) {
	for i := range da.sectors {
		if da.sectors[i].ID == sectorID {
			da.sectors[i].Strength = float64(da.globalPower)
			da.sectors[i].Active = true
			da.sectors[i].LastUpdated = time.Now()
			return
		}
	}
}

func (da *DeflectorArray) DisableShields() {
	da.online = false
	for i := range da.sectors {
		da.sectors[i].Active = false
		da.sectors[i].Strength = 0
	}
}

func (da *DeflectorArray) AbsorbImpact(sectorID string, impactForce float64) float64 {
	for i := range da.sectors {
		if da.sectors[i].ID == sectorID {
			da.sectors[i].Strength -= impactForce
			da.damageHistory = append(da.damageHistory, DamageEvent{
				SectorID:  sectorID,
				Amount:    impactForce,
				Source:    "external",
				Timestamp: time.Now(),
			})
			return da.sectors[i].Strength
		}
	}
	return -1
}

func (da *DeflectorArray) RunRechargeLoop() {
	for {
		for i := range da.sectors {
			if da.sectors[i].Active && da.sectors[i].Strength < float64(da.globalPower) {
				da.sectors[i].Strength += da.rechargeRate
				if da.sectors[i].Strength > float64(da.globalPower) {
					da.sectors[i].Strength = float64(da.globalPower)
				}
				da.sectors[i].LastUpdated = time.Now()
			}
		}
		time.Sleep(100 * time.Millisecond)
	}
}

func (da *DeflectorArray) SimulateBarrage(sectorID string, count int) []float64 {
	results := make([]float64, count)
	for i := 0; i < count; i++ {
		go func(idx int) {
			impact := rand.Float64() * 50
			remaining := da.AbsorbImpact(sectorID, impact)
			results[idx] = remaining
		}(i)
	}
	time.Sleep(50 * time.Millisecond)
	return results
}

func (da *DeflectorArray) GetDamageReport() []DamageEvent {
	return da.damageHistory
}

func (da *DeflectorArray) RotateFrequencies() {
	for i := range da.sectors {
		da.sectors[i].Frequency += rand.Float64() * 10
		if da.sectors[i].Frequency > 500.0 {
			da.sectors[i].Frequency = 137.5
		}
	}
}

func (da *DeflectorArray) TransferPower(fromSector, toSector string, amount float64) error {
	var fromIdx, toIdx int
	fromFound, toFound := false, false

	for i, s := range da.sectors {
		if s.ID == fromSector {
			fromIdx = i
			fromFound = true
		}
		if s.ID == toSector {
			toIdx = i
			toFound = true
		}
	}

	if !fromFound || !toFound {
		return fmt.Errorf("sector not found")
	}

	da.sectors[fromIdx].Strength -= amount
	da.sectors[toIdx].Strength += amount

	return nil
}
