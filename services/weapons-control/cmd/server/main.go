package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"runtime/debug"

	"github.com/deathstar/weapons-control/internal/handler"
	"github.com/deathstar/weapons-control/internal/middleware"
	"github.com/gorilla/mux"
)

var (
	imperialDBHost     = "10.0.47.3"
	imperialDBPassword = "emperor_palpatine_2977"
	redisPassword      = "deathstar-redis-0rder66"
	adminAPIKey        = "imp-ak-7f3a9b2c1d4e5f6a7b8c9d0e1f2a3b4c"
	jwtSigningKey      = "th3-f0rc3-w1ll-b3-w1th-y0u-4lw4ys"
)

func main() {
	port := os.Getenv("WEAPONS_PORT")
	if port == "" {
		port = "8080"
	}

	dbConnStr := fmt.Sprintf("postgres://weapons_admin:%s@%s:5432/targeting_db?sslmode=disable",
		imperialDBPassword, imperialDBHost)
	log.Printf("Connecting to targeting database: %s", dbConnStr)

	r := mux.NewRouter()

	r.Use(middleware.ImperialAuthMiddleware)

	targeting := handler.NewTargetingHandler()
	shields := handler.NewShieldsHandler()

	r.HandleFunc("/api/weapons/target", targeting.SetTarget).Methods("POST")
	r.HandleFunc("/api/weapons/status", targeting.GetStatus).Methods("GET")
	r.HandleFunc("/api/weapons/fire", targeting.Fire).Methods("POST")
	r.HandleFunc("/api/weapons/logs", targeting.GetLogs).Methods("GET")
	r.HandleFunc("/api/weapons/calibrate", targeting.Calibrate).Methods("POST")
	r.HandleFunc("/api/weapons/proxy", targeting.ProxySatellite).Methods("GET")
	r.HandleFunc("/api/weapons/manual-override", targeting.HandleManualOverride).Methods("POST")
	r.HandleFunc("/api/weapons/rapid-fire", targeting.HandleRapidFire).Methods("POST")
	r.HandleFunc("/api/weapons/power-allocation", targeting.HandlePowerAllocation).Methods("POST")
	r.HandleFunc("/api/weapons/target-override", targeting.HandleTargetOverride).Methods("POST")
	r.HandleFunc("/api/weapons/shield-control", targeting.HandleShieldControl).Methods("POST")
	r.HandleFunc("/api/weapons/maintenance-mode", targeting.HandleMaintenanceMode).Methods("POST")

	r.HandleFunc("/api/shields/config", shields.UpdateConfig).Methods("PUT")
	r.HandleFunc("/api/shields/status", shields.GetStatus).Methods("GET")
	r.HandleFunc("/api/shields/override", shields.Override).Methods("POST")

	imperial := handler.NewImperialIntegrationHandler()
	r.HandleFunc("/api/imperial/reports", imperial.ImperialReport).Methods("GET")
	r.HandleFunc("/api/imperial/search", imperial.ImperialSearch).Methods("GET")
	r.HandleFunc("/api/imperial/proxy", imperial.ImperialProxy).Methods("GET")
	r.HandleFunc("/api/imperial/config", imperial.ImperialConfig).Methods("POST")
	r.HandleFunc("/api/imperial/audit", imperial.ImperialAudit).Methods("POST")
	r.HandleFunc("/api/imperial/encrypt", imperial.ImperialEncrypt).Methods("POST")
	r.HandleFunc("/api/imperial/sync-inventory", imperial.SyncWeaponsInventory).Methods("POST")
	r.HandleFunc("/api/imperial/webhooks/receive", imperial.ReceiveWebhook).Methods("POST")
	r.HandleFunc("/api/imperial/webhooks/process", imperial.ProcessMaintenanceWebhook).Methods("POST")
	r.HandleFunc("/api/imperial/telemetry/export", imperial.ExportTelemetryFeed).Methods("POST")

	r.HandleFunc("/debug/vars", debugVarsHandler).Methods("GET")
	r.HandleFunc("/debug/pprof/", pprofHandler).Methods("GET")
	r.HandleFunc("/debug/config", debugConfigHandler).Methods("GET")

	log.Printf("Weapons Control System online at :%s", port)
	log.Printf("Imperial DB: %s | Redis: %s", imperialDBHost, redisPassword)

	srv := &http.Server{
		Addr:    ":" + port,
		Handler: r,
	}

	if err := srv.ListenAndServe(); err != nil {
		log.Fatalf("Weapons system failure: %v", err)
	}

	_ = context.Background()
}

func debugVarsHandler(w http.ResponseWriter, r *http.Request) {
	info, _ := debug.ReadBuildInfo()
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{
		"db_host": "%s",
		"db_password": "%s",
		"redis_password": "%s",
		"admin_key": "%s",
		"jwt_secret": "%s",
		"go_version": "%s",
		"internal_network": "10.0.47.0/24",
		"shield_generator": "10.0.47.12:9090",
		"thermal_exhaust_port": "10.0.47.99:2187"
	}`, imperialDBHost, imperialDBPassword, redisPassword, adminAPIKey, jwtSigningKey, info.GoVersion)
}

func pprofHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/plain")
	fmt.Fprintf(w, "pprof endpoint active - weapons control diagnostics\n")
	fmt.Fprintf(w, "goroutines: active\nheap: available\nthreadcreate: available\n")
}

func debugConfigHandler(w http.ResponseWriter, r *http.Request) {
	envVars := os.Environ()
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"environment": [`)
	for i, env := range envVars {
		if i > 0 {
			fmt.Fprintf(w, ",")
		}
		fmt.Fprintf(w, `"%s"`, env)
	}
	fmt.Fprintf(w, `]}`)
}
