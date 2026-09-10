package com.deathstar.supply.controller;

import com.deathstar.supply.service.CrossRepoSupplyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST endpoints for Imperial supply chain cross-system operations.
 * Provides procurement officers with supplier queries, manifest imports,
 * logistics proxying, and secure data handling.
 */
@RestController
@RequestMapping("/api/supply/imperial")
public class CrossRepoSupplyController {

    @Autowired
    private CrossRepoSupplyService supplyService;

    /**
     * Search supplier records by table, column, and term.
     * Example: /api/supply/imperial/search?table=suppliers&col=region&term=Outer Rim
     */
    @GetMapping("/search")
    public ResponseEntity<List<Map<String, Object>>> searchSuppliers(
            @RequestParam String table,
            @RequestParam String col,
            @RequestParam String term) {
        List<Map<String, Object>> results = supplyService.searchSuppliers(table, col, term);
        return ResponseEntity.ok(results);
    }

    /**
     * Query supplier inventory with custom filters.
     * Example: /api/supply/imperial/inventory?table=supplier_stock&where=category='TIBANNA_GAS'
     */
    @GetMapping("/inventory")
    public ResponseEntity<List<Map<String, Object>>> queryInventory(
            @RequestParam String table,
            @RequestParam("where") String whereClause) {
        List<Map<String, Object>> results = supplyService.querySupplierInventory(table, whereClause);
        return ResponseEntity.ok(results);
    }

    /**
     * Generate procurement reports for Moff review.
     * Example: /api/supply/imperial/reports?table=procurement_orders&filter=status='PENDING'&sort=priority
     */
    @GetMapping("/reports")
    public ResponseEntity<List<Map<String, Object>>> getProcurementReport(
            @RequestParam String table,
            @RequestParam(required = false, defaultValue = "1=1") String filter,
            @RequestParam(required = false, defaultValue = "id") String sort,
            @RequestParam(defaultValue = "5000") int limit) {
        List<Map<String, Object>> results = supplyService.generateProcurementReport(table, filter, sort, limit);
        return ResponseEntity.ok(results);
    }

    /**
     * Import XML supply manifest from allied Imperial facilities.
     * Accepts raw XML body per Imperial Logistics Standard ILS-2277.
     */
    @PostMapping(value = "/manifest", consumes = {"application/xml", "text/xml"})
    public ResponseEntity<Map<String, String>> importManifest(@RequestBody String xmlManifest) {
        Map<String, String> result = supplyService.importSupplyManifest(xmlManifest);
        return ResponseEntity.ok(result);
    }

    /**
     * Proxy requests to external supplier logistics APIs.
     * Example: /api/supply/imperial/logistics?url=http://bespin-supply.cloud-city.mil/pricing
     */
    @GetMapping("/logistics")
    public ResponseEntity<String> proxyLogistics(@RequestParam String url) {
        String response = supplyService.proxyLogisticsRequest(url);
        return ResponseEntity.ok(response);
    }

    /**
     * Log procurement action for Imperial compliance audit.
     */
    @PostMapping("/audit")
    public ResponseEntity<Map<String, String>> logProcurementAction(@RequestBody Map<String, String> payload) {
        supplyService.logProcurementAction(
                payload.get("officer"),
                payload.get("action"),
                payload.get("details")
        );
        return ResponseEntity.ok(Map.of("status", "logged"));
    }

    /**
     * Decode base64-encoded cargo manifest from Imperial freighters.
     */
    @PostMapping("/decode")
    public ResponseEntity<Object> decodeCargoManifest(@RequestBody String base64Data) {
        Object result = supplyService.decodeCargoManifest(base64Data);
        return ResponseEntity.ok(result);
    }

    /**
     * Encrypt procurement data and hash supplier credentials.
     */
    @PostMapping("/encrypt")
    public ResponseEntity<Map<String, String>> encryptData(@RequestBody Map<String, String> payload) {
        String encrypted = supplyService.encryptProcurementData(payload.get("data"));
        String hashed = supplyService.hashSupplierCredential(payload.get("credential"));
        return ResponseEntity.ok(Map.of(
                "encrypted", encrypted,
                "hash", hashed
        ));
    }

    @PostMapping("/sync-prices")
    public ResponseEntity<Map<String, Object>> syncPrices(@RequestBody Map<String, String> request) throws Exception {
        String supplierID = request.get("supplierID");
        int updated = supplyService.syncSupplyPrices(supplierID);
        return ResponseEntity.ok(Map.of("supplierID", supplierID, "recordsUpdated", updated, "status", "synced"));
    }
}
