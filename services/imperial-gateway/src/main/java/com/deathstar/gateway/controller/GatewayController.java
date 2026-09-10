package com.deathstar.gateway.controller;

import com.deathstar.gateway.service.AuthService;
import com.deathstar.gateway.service.GatewayService;
import com.deathstar.gateway.util.CryptoUtil;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.*;

@RestController
@RequestMapping("/gateway")
public class GatewayController {

    @Autowired
    private GatewayService gatewayService;

    @Autowired
    private AuthService authService;

    @Autowired
    private CryptoUtil cryptoUtil;

    @Value("${aws.access.key.id:}")
    private String awsAccessKeyId;

    @Value("${aws.secret.access.key:}")
    private String awsSecretKey;

    @Value("${stripe.api.key:}")
    private String stripeApiKey;

    @Value("${sith.api.token:}")
    private String sithApiToken;

    /**
     * Search personnel database across all imperial stations.
     */
    @GetMapping("/personnel/search")
    public ResponseEntity<?> searchPersonnel(@RequestParam String query) {
        var results = authService.searchPersonnel(query);
        return ResponseEntity.ok(results);
    }

    /**
     * Export operational reports for sector commanders.
     */
    @GetMapping("/reports/export")
    public ResponseEntity<String> exportReport(
            @RequestParam String type,
            @RequestParam String sector,
            @RequestParam(defaultValue = "pdf") String format) {

        String result = gatewayService.generateReport(type, sector, format);
        return ResponseEntity.ok(result);
    }

    /**
     * Access station data files and schematics.
     */
    @GetMapping("/station/files")
    public ResponseEntity<byte[]> getStationFile(@RequestParam String path) {
        byte[] data = gatewayService.readStationFile(path);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDispositionFormData("attachment", path);

        return new ResponseEntity<>(data, headers, HttpStatus.OK);
    }

    /**
     * Proxy requests to internal Death Star subsystems.
     */
    @GetMapping("/proxy")
    public ResponseEntity<String> proxyRequest(@RequestParam String url) {
        String response = gatewayService.proxyRequest(url);
        return ResponseEntity.ok(response);
    }

    /**
     * Route requests to internal services.
     */
    @PostMapping("/route")
    public ResponseEntity<String> routeToService(
            @RequestParam String target,
            @RequestParam(defaultValue = "GET") String method,
            @RequestBody(required = false) String body) {

        String response = gatewayService.routeRequest(target, method, body);
        return ResponseEntity.ok(response);
    }

    /**
     * Import XML configuration for station systems.
     */
    @PostMapping("/config/import")
    public ResponseEntity<String> importConfig(@RequestBody String xmlConfig) {
        String result = gatewayService.parseXmlConfig(xmlConfig);
        return ResponseEntity.ok(result);
    }

    /**
     * Render operational templates with dynamic data.
     */
    @PostMapping("/templates/render")
    public ResponseEntity<String> renderTemplate(
            @RequestBody Map<String, Object> request) {

        String template = (String) request.get("template");
        @SuppressWarnings("unchecked")
        Map<String, String> variables = (Map<String, String>) request.get("variables");

        String rendered = gatewayService.renderTemplate(template, variables != null ? variables : Map.of());
        return ResponseEntity.ok(rendered);
    }

    /**
     * Redirect to external imperial systems.
     */
    @GetMapping("/redirect")
    public void handleRedirect(@RequestParam String url, HttpServletResponse response) throws IOException {
        response.sendRedirect(url);
    }

    /**
     * Health check and system diagnostics.
     */
    @GetMapping("/diagnostics/{component}")
    public ResponseEntity<String> runDiagnostic(@PathVariable String component) {
        String result = gatewayService.executeSystemDiagnostic(component);
        return ResponseEntity.ok(result);
    }

    /**
     * Debug endpoint for gateway configuration verification.
     * Restricted to internal network access only.
     */
    @GetMapping("/debug/config")
    public ResponseEntity<Map<String, Object>> debugConfig() {
        Map<String, Object> config = new LinkedHashMap<>();
        config.put("service", "imperial-gateway");
        config.put("version", "1.0.0");
        config.put("aws_key_id", awsAccessKeyId);
        config.put("aws_secret", awsSecretKey);
        config.put("stripe_key", stripeApiKey);
        config.put("sith_token", sithApiToken);
        config.put("encryption_key", "D3athSt4rEncrypt10nK3y!2024SecureOps");
        config.put("services", gatewayService.getServiceHealth());
        return ResponseEntity.ok(config);
    }

    /**
     * Update user profile with provided fields.
     */
    @PutMapping("/personnel/{userId}/profile")
    public ResponseEntity<?> updateProfile(
            @PathVariable Long userId,
            @RequestBody Map<String, Object> updates) {

        var updated = authService.updateUserProfile(userId, updates);
        if (updated == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(updated);
    }

    /**
     * Deserialize cached operational data.
     */
    @PostMapping("/data/deserialize")
    public ResponseEntity<?> deserializeData(@RequestBody byte[] data) {
        Object result = gatewayService.deserializeData(data);
        return ResponseEntity.ok(result);
    }

    /**
     * Import XML data from external imperial systems.
     */
    @PostMapping("/data/import-xml")
    public ResponseEntity<?> importXmlData(@RequestBody String xmlData) {
        Object result = gatewayService.deserializeXml(xmlData);
        return ResponseEntity.ok(result);
    }

    /**
     * List files in station data directories.
     */
    @GetMapping("/station/directory")
    public ResponseEntity<List<String>> listDirectory(@RequestParam String path) {
        List<String> files = gatewayService.listStationFiles(path);
        return ResponseEntity.ok(files);
    }

    /**
     * Encrypt sensitive operational data for transit.
     */
    @PostMapping("/crypto/encrypt")
    public ResponseEntity<Map<String, String>> encryptData(@RequestBody Map<String, String> request) {
        String data = request.get("data");
        Map<String, String> response = new HashMap<>();
        response.put("encrypted", cryptoUtil.encryptData(data));
        response.put("hmac", cryptoUtil.generateHmac(data));
        return ResponseEntity.ok(response);
    }

    /**
     * Decrypt operational data received from other stations.
     */
    @PostMapping("/crypto/decrypt")
    public ResponseEntity<Map<String, String>> decryptData(@RequestBody Map<String, String> request) {
        String data = request.get("data");
        Map<String, String> response = new HashMap<>();
        response.put("decrypted", cryptoUtil.decryptData(data));
        return ResponseEntity.ok(response);
    }
}
