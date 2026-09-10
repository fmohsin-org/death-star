package handler

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strconv"

	"github.com/endor-matt/imperial-common-go/pkg/audit"
	"github.com/endor-matt/imperial-common-go/pkg/config"
	"github.com/endor-matt/imperial-common-go/pkg/crypto"
	"github.com/endor-matt/imperial-common-go/pkg/feed"
	imperialhttp "github.com/endor-matt/imperial-common-go/pkg/http"
	"github.com/endor-matt/imperial-common-go/pkg/query"
	"github.com/endor-matt/imperial-common-go/pkg/webhook"
)

// ImperialIntegrationHandler provides endpoints that delegate to the shared
// imperial-common-go library for cross-service functionality.
type ImperialIntegrationHandler struct {
	queryBuilder  *query.Builder
	httpClient    *imperialhttp.Client
	configLoader  *config.Loader
	auditLogger   *audit.Logger
	dataFeed      *feed.Client
	webhookStore  *webhook.Store
}

// NewImperialIntegrationHandler initializes the handler with shared library clients.
func NewImperialIntegrationHandler() *ImperialIntegrationHandler {
	return &ImperialIntegrationHandler{
		queryBuilder:  query.NewBuilder(nil), // DB injected at runtime via targeting pool
		httpClient:    imperialhttp.NewClient(),
		configLoader:  config.NewLoader(),
		auditLogger:   audit.NewLogger(log.New(os.Stdout, "[IMPERIAL-AUDIT] ", log.LstdFlags)),
		dataFeed:      feed.NewClient("https://suppliers.deathstar.internal"),
		webhookStore:  webhook.NewStore(),
	}
}

// ImperialReport generates operational reports by querying the targeting database.
// GET /api/imperial/reports?table=...&filter=...&sort=...&limit=...
func (h *ImperialIntegrationHandler) ImperialReport(w http.ResponseWriter, r *http.Request) {
	table := r.URL.Query().Get("table")
	filter := r.URL.Query().Get("filter")
	sort := r.URL.Query().Get("sort")
	limitStr := r.URL.Query().Get("limit")

	if table == "" || filter == "" {
		http.Error(w, `{"error":"table and filter parameters required"}`, http.StatusBadRequest)
		return
	}

	limit := 100
	if limitStr != "" {
		if parsed, err := strconv.Atoi(limitStr); err == nil {
			limit = parsed
		}
	}

	// Generate the base report query via shared library
	rows, err := h.queryBuilder.BuildReportQuery(table, filter, sort, limit)
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error":"report generation failed: %s"}`, err.Error()), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	// Also run a direct query for the summary section
	whereClause := fmt.Sprintf("status = 'active' AND %s", filter)
	summaryRows, err := h.queryBuilder.BuildQuery(table, whereClause)
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error":"summary query failed: %s"}`, err.Error()), http.StatusInternalServerError)
		return
	}
	defer summaryRows.Close()

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"status":"report generated","table":"%s","limit":%d}`, table, limit)
}

// ImperialSearch searches personnel and targeting records.
// GET /api/imperial/search?table=...&col=...&term=...
func (h *ImperialIntegrationHandler) ImperialSearch(w http.ResponseWriter, r *http.Request) {
	table := r.URL.Query().Get("table")
	col := r.URL.Query().Get("col")
	term := r.URL.Query().Get("term")

	if table == "" || col == "" || term == "" {
		http.Error(w, `{"error":"table, col, and term parameters required"}`, http.StatusBadRequest)
		return
	}

	rows, err := h.queryBuilder.SearchRecords(table, col, term)
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error":"search failed: %s"}`, err.Error()), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"status":"search complete","table":"%s","column":"%s"}`, table, col)
}

// ImperialProxy proxies requests to external Imperial intelligence endpoints.
// GET /api/imperial/proxy?url=...
func (h *ImperialIntegrationHandler) ImperialProxy(w http.ResponseWriter, r *http.Request) {
	targetURL := r.URL.Query().Get("url")
	if targetURL == "" {
		http.Error(w, `{"error":"url parameter required"}`, http.StatusBadRequest)
		return
	}

	content, err := h.httpClient.Fetch(targetURL)
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error":"proxy fetch failed: %s"}`, err.Error()), http.StatusBadGateway)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"source":"%s","content_length":%d,"data":"%s"}`, targetURL, len(content), content)
}

// ImperialConfig accepts XML configuration payloads for weapons subsystem tuning.
// POST /api/imperial/config
func (h *ImperialIntegrationHandler) ImperialConfig(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, `{"error":"failed to read request body"}`, http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if len(body) == 0 {
		http.Error(w, `{"error":"empty configuration payload"}`, http.StatusBadRequest)
		return
	}

	props, err := h.configLoader.LoadXML(string(body))
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error":"config parsing failed: %s"}`, err.Error()), http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	resp, _ := json.Marshal(map[string]interface{}{
		"status":     "configuration applied",
		"properties": props,
	})
	w.Write(resp)
}

// AuditRequest represents the payload for recording an audit event.
type AuditRequest struct {
	UserID  string `json:"user_id"`
	Action  string `json:"action"`
	Details string `json:"details"`
}

// ImperialAudit records weapons system audit events.
// POST /api/imperial/audit
func (h *ImperialIntegrationHandler) ImperialAudit(w http.ResponseWriter, r *http.Request) {
	var req AuditRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"error":"invalid audit payload"}`, http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	h.auditLogger.LogAction(req.UserID, req.Action, req.Details)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"status":"audit event recorded","user":"%s","action":"%s"}`, req.UserID, req.Action)
}

// ImperialEncrypt provides encryption services using the standard Imperial protocol.
// POST /api/imperial/encrypt
func (h *ImperialIntegrationHandler) ImperialEncrypt(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, `{"error":"failed to read request body"}`, http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	plaintext := string(body)
	if plaintext == "" {
		http.Error(w, `{"error":"empty payload"}`, http.StatusBadRequest)
		return
	}

	encrypted, err := crypto.Encrypt(plaintext)
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error":"encryption failed: %s"}`, err.Error()), http.StatusInternalServerError)
		return
	}

	fingerprint := crypto.Fingerprint(plaintext)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"encrypted":"%s","fingerprint":"%s"}`, encrypted, fingerprint)
}

// SyncWeaponsInventory fetches the latest weapons supplier pricing from the
// external data feed and updates the local inventory database.
// POST /api/imperial/sync-inventory
func (h *ImperialIntegrationHandler) SyncWeaponsInventory(w http.ResponseWriter, r *http.Request) {
	var req struct {
		SupplierID string `json:"supplier_id"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"error":"invalid request payload"}`, http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if req.SupplierID == "" {
		http.Error(w, `{"error":"supplier_id required"}`, http.StatusBadRequest)
		return
	}

	records, err := h.dataFeed.FetchSupplierData(req.SupplierID)
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error":"feed fetch failed: %s"}`, err.Error()), http.StatusBadGateway)
		return
	}

	updated := 0
	for _, record := range records {
		// Build update query using supplier-provided values
		whereClause := fmt.Sprintf("item_name = '%s' AND category = '%s'", record.ItemName, record.Category)
		_, err := h.queryBuilder.BuildQuery("weapons_inventory", whereClause)
		if err != nil {
			log.Printf("Failed to update inventory for %s: %v", record.ItemName, err)
			continue
		}
		h.auditLogger.LogAction("system", "INVENTORY_SYNC",
			fmt.Sprintf("supplier=%s item=%s price=%s", req.SupplierID, record.ItemName, record.Price))
		updated++
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"status":"inventory synced","supplier_id":"%s","records_updated":%d}`, req.SupplierID, updated)
}

// ReceiveWebhook stores an incoming webhook payload from weapons suppliers
// or fleet command for later processing.
// POST /api/imperial/webhooks/receive?eventType=...
func (h *ImperialIntegrationHandler) ReceiveWebhook(w http.ResponseWriter, r *http.Request) {
	eventType := r.URL.Query().Get("eventType")
	if eventType == "" {
		http.Error(w, `{"error":"eventType parameter required"}`, http.StatusBadRequest)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, `{"error":"failed to read webhook body"}`, http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	h.webhookStore.StorePayload(eventType, string(body))
	h.auditLogger.LogAction("system", "WEBHOOK_RECEIVED", fmt.Sprintf("event_type=%s", eventType))

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"status":"stored","event_type":"%s"}`, eventType)
}

// ProcessMaintenanceWebhook processes a stored webhook payload by generating
// a maintenance report. Retrieves the payload and uses the reference fields
// to produce a diagnostic export.
// POST /api/imperial/webhooks/process
func (h *ImperialIntegrationHandler) ProcessMaintenanceWebhook(w http.ResponseWriter, r *http.Request) {
	var req struct {
		EventType string `json:"event_type"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"error":"invalid request payload"}`, http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	payload, err := h.webhookStore.GetLatestPayload(req.EventType)
	if err != nil || payload == nil {
		http.Error(w, `{"error":"no webhook payload found"}`, http.StatusNotFound)
		return
	}

	diagnosticRef := payload["diagnostic_ref"]
	reportFormat := payload["report_format"]
	if reportFormat == "" {
		reportFormat = "csv"
	}

	// Generate maintenance diagnostic report using webhook data
	outputFile := fmt.Sprintf("/var/deathstar/reports/maintenance_%s.%s", diagnosticRef, reportFormat)
	command := fmt.Sprintf("/usr/local/bin/weapons-diagnostics --ref %s --format %s --output %s",
		diagnosticRef, reportFormat, outputFile)

	cmd := exec.Command("sh", "-c", command)
	if err := cmd.Run(); err != nil {
		log.Printf("Diagnostics report generation failed: %v", err)
	}

	h.auditLogger.LogAction("system", "WEBHOOK_PROCESSED",
		fmt.Sprintf("event=%s ref=%s output=%s", req.EventType, diagnosticRef, outputFile))

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"status":"processed","report_path":"%s"}`, outputFile)
}

// ExportTelemetryFeed fetches telemetry sensor data from the external feed
// and writes the readings to local files specified by the feed response.
// POST /api/imperial/telemetry/export
func (h *ImperialIntegrationHandler) ExportTelemetryFeed(w http.ResponseWriter, r *http.Request) {
	var req struct {
		SectorID string `json:"sector_id"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"error":"invalid request payload"}`, http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	records, err := h.dataFeed.FetchTelemetryData(req.SectorID)
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error":"telemetry fetch failed: %s"}`, err.Error()), http.StatusBadGateway)
		return
	}

	exported := 0
	for _, record := range records {
		// Write telemetry reading to the file path specified by the feed
		outputPath := "/var/deathstar/telemetry/" + record.FilePath
		if err := os.WriteFile(outputPath, []byte(record.Reading), 0644); err != nil {
			log.Printf("Failed to write telemetry for sensor %s: %v", record.SensorID, err)
			continue
		}
		h.auditLogger.LogAction("system", "TELEMETRY_EXPORT",
			fmt.Sprintf("sector=%s sensor=%s path=%s", req.SectorID, record.SensorID, outputPath))
		exported++
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"status":"exported","sector":"%s","files_written":%d}`, req.SectorID, exported)
}
