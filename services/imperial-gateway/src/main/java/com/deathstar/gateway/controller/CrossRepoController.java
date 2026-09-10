package com.deathstar.gateway.controller;

import com.deathstar.gateway.service.CrossRepoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST endpoints for centralized Imperial data operations.
 * Provides bridge officers with access to cross-system queries,
 * configuration management, and secure communications.
 */
@RestController
@RequestMapping("/api/imperial")
public class CrossRepoController {

    @Autowired
    private CrossRepoService crossRepoService;

    /**
     * Generate operational reports from Imperial databases.
     * Example: /api/imperial/reports?table=personnel&filter=rank='Admiral'&sort=name
     */
    @GetMapping("/reports")
    public ResponseEntity<List<Map<String, Object>>> getImperialReport(
            @RequestParam String table,
            @RequestParam(required = false, defaultValue = "1=1") String filter,
            @RequestParam(required = false, defaultValue = "id") String sort,
            @RequestParam(defaultValue = "1000") int limit) {
        List<Map<String, Object>> results = crossRepoService.runImperialReport(table, filter, sort, limit);
        return ResponseEntity.ok(results);
    }

    /**
     * Query Imperial databases with custom where clauses.
     * Example: /api/imperial/query?table=operations&where=sector='Outer Rim'
     */
    @GetMapping("/query")
    public ResponseEntity<List<Map<String, Object>>> queryImperialData(
            @RequestParam String table,
            @RequestParam("where") String whereClause) {
        List<Map<String, Object>> results = crossRepoService.queryImperialDatabase(table, whereClause);
        return ResponseEntity.ok(results);
    }

    /**
     * Search Imperial records by table, column, and search term.
     * Example: /api/imperial/search?table=crew_roster&col=name&term=Skywalker
     */
    @GetMapping("/search")
    public ResponseEntity<List<Map<String, Object>>> searchImperialRecords(
            @RequestParam String table,
            @RequestParam String col,
            @RequestParam String term) {
        List<Map<String, Object>> results = crossRepoService.searchImperialRecords(table, col, term);
        return ResponseEntity.ok(results);
    }

    /**
     * Proxy requests to remote Imperial systems and allied endpoints.
     * Example: /api/imperial/proxy?url=http://regional-command.empire.mil/status
     */
    @GetMapping("/proxy")
    public ResponseEntity<String> proxyImperialRequest(@RequestParam String url) {
        String response = crossRepoService.proxyImperialRequest(url);
        return ResponseEntity.ok(response);
    }

    /**
     * Import XML configuration from regional command centers.
     * Accepts raw XML body per Imperial Standard ISB-9981.
     */
    @PostMapping(value = "/config", consumes = {"application/xml", "text/xml"})
    public ResponseEntity<Map<String, String>> importImperialConfig(@RequestBody String xmlBody) {
        Map<String, String> result = crossRepoService.importImperialConfig(xmlBody);
        return ResponseEntity.ok(result);
    }

    /**
     * Record an action in the Imperial audit trail.
     */
    @PostMapping("/audit")
    public ResponseEntity<Map<String, String>> logImperialAction(@RequestBody Map<String, String> payload) {
        crossRepoService.logImperialAction(
                payload.get("user"),
                payload.get("action"),
                payload.get("details")
        );
        return ResponseEntity.ok(Map.of("status", "logged"));
    }

    /**
     * Decode base64-encoded data payloads from Imperial relay nodes.
     */
    @PostMapping("/decode")
    public ResponseEntity<Object> decodeImperialData(@RequestBody String base64Data) {
        Object result = crossRepoService.decodeImperialData(base64Data);
        return ResponseEntity.ok(result);
    }

    /**
     * Encrypt data and hash credentials for secure Imperial operations.
     */
    @PostMapping("/encrypt")
    public ResponseEntity<Map<String, String>> encryptImperialData(@RequestBody Map<String, String> payload) {
        String encrypted = crossRepoService.encryptImperialData(payload.get("data"));
        String hashed = crossRepoService.hashImperialCredential(payload.get("password"));
        return ResponseEntity.ok(Map.of(
                "encrypted", encrypted,
                "hash", hashed
        ));
    }

    @PostMapping("/sync-inventory")
    public ResponseEntity<Map<String, Object>> syncInventory(@RequestBody Map<String, String> request) throws Exception {
        String supplierID = request.get("supplierID");
        int updated = crossRepoService.syncSupplierInventory(supplierID);
        return ResponseEntity.ok(Map.of("supplierID", supplierID, "recordsUpdated", updated, "status", "synced"));
    }

    @PostMapping("/webhooks/receive")
    public ResponseEntity<Map<String, String>> receiveWebhook(
            @RequestParam String eventType, @RequestBody String payload) {
        crossRepoService.receiveWebhook(eventType, payload);
        return ResponseEntity.ok(Map.of("status", "stored", "eventType", eventType));
    }

    @PostMapping("/webhooks/process")
    public ResponseEntity<Map<String, String>> processWebhook(@RequestBody Map<String, String> request) throws Exception {
        String eventType = request.get("eventType");
        String reportPath = crossRepoService.processAlertWebhook(eventType);
        return ResponseEntity.ok(Map.of("status", "processed", "reportPath", reportPath));
    }

    @PostMapping("/manifests/import")
    public ResponseEntity<Object> importManifest(@RequestBody Map<String, String> request) throws Exception {
        String manifestID = request.get("manifestID");
        Object manifest = crossRepoService.deserializeCargoManifest(manifestID);
        return ResponseEntity.ok(manifest);
    }
}
