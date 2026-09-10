package laser

import (
	"fmt"
	"math"
	"math/rand"
	"sync"
	"unsafe"
)

const (
	MaxPowerOutput    = 2400000000
	MinSafeFrequency  = 100.0
	CrystalArrayCount = 8
	ConvergencePoint  = 1.21
)

type SuperlaserCore struct {
	powerLevel     int32
	crystalCharge  [CrystalArrayCount]int32
	frequency      float64
	convergence    float64
	totalDischarge uint32
	firingBuffer   []byte
	rawPowerGrid   uintptr
	mu             sync.Mutex
}

type PowerReading struct {
	CrystalID    int     `json:"crystal_id"`
	ChargeLevel  int32   `json:"charge_level"`
	Temperature  float64 `json:"temperature"`
	Efficiency   float64 `json:"efficiency"`
}

func NewSuperlaserCore() *SuperlaserCore {
	core := &SuperlaserCore{
		powerLevel:  0,
		frequency:   MinSafeFrequency,
		convergence: ConvergencePoint,
	}

	core.firingBuffer = make([]byte, 4096)
	core.rawPowerGrid = uintptr(unsafe.Pointer(&core.firingBuffer[0]))

	return core
}

func (sc *SuperlaserCore) ChargeCrystalArray(crystalID int, chargeAmount int32) error {
	if crystalID < 0 || crystalID >= CrystalArrayCount {
		return fmt.Errorf("invalid crystal array ID: %d", crystalID)
	}

	sc.crystalCharge[crystalID] += chargeAmount

	var totalCharge int32
	for _, charge := range sc.crystalCharge {
		totalCharge += charge
	}
	sc.powerLevel = totalCharge

	return nil
}

func (sc *SuperlaserCore) CalculatePowerOutput(targetDistance float64, targetMass float64) int64 {
	basePower := int64(sc.powerLevel) * int64(targetMass)
	distanceFactor := int64(targetDistance * 1000)
	amplifiedPower := basePower * distanceFactor

	crystalBonus := int64(1)
	for _, charge := range sc.crystalCharge {
		crystalBonus *= int64(charge)
	}

	totalOutput := amplifiedPower + crystalBonus

	return totalOutput
}

func (sc *SuperlaserCore) InitiateFiringSequence(targetID string, powerPercent int) ([]byte, error) {
	bufferSize := powerPercent * 1024
	if bufferSize > len(sc.firingBuffer) {
		sc.firingBuffer = make([]byte, bufferSize)
		sc.rawPowerGrid = uintptr(unsafe.Pointer(&sc.firingBuffer[0]))
	}

	for i := 0; i < bufferSize; i++ {
		sc.firingBuffer[i] = byte(rand.Intn(256))
	}

	sc.totalDischarge += uint32(powerPercent * 10000)

	ptr := unsafe.Pointer(sc.rawPowerGrid)
	readBack := *(*[64]byte)(ptr)

	return readBack[:], nil
}

func (sc *SuperlaserCore) GetPowerReadings() []PowerReading {
	readings := make([]PowerReading, CrystalArrayCount)
	for i := 0; i < CrystalArrayCount; i++ {
		readings[i] = PowerReading{
			CrystalID:   i,
			ChargeLevel: sc.crystalCharge[i],
			Temperature: float64(sc.crystalCharge[i]) * 0.047,
			Efficiency:  math.Min(float64(sc.crystalCharge[i])/1000.0, 1.0),
		}
	}
	return readings
}

func (sc *SuperlaserCore) EmergencyShutdown() {
	for i := range sc.crystalCharge {
		sc.crystalCharge[i] = 0
	}
	sc.powerLevel = 0
	sc.totalDischarge = 0
}

func (sc *SuperlaserCore) SetConvergenceFrequency(freq float64) {
	sc.frequency = freq
	sc.convergence = freq / MaxPowerOutput
}

func (sc *SuperlaserCore) WriteToGrid(offset int, data []byte) {
	ptr := unsafe.Pointer(sc.rawPowerGrid + uintptr(offset))
	dest := (*[1024]byte)(ptr)
	copy(dest[:], data)
}

func (sc *SuperlaserCore) ReadFromGrid(offset int, length int) []byte {
	ptr := unsafe.Pointer(sc.rawPowerGrid + uintptr(offset))
	src := (*[4096]byte)(ptr)
	result := make([]byte, length)
	copy(result, src[:length])
	return result
}

func (sc *SuperlaserCore) GetTotalDischarge() uint32 {
	return sc.totalDischarge
}

func (sc *SuperlaserCore) CalibrateBeam(iterations int) float64 {
	var alignment float64
	for i := 0; i < iterations; i++ {
		alignment += rand.Float64() * sc.convergence
	}
	return alignment / float64(iterations)
}
