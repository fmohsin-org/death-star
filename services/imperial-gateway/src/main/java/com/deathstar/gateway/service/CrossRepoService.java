package com.deathstar.gateway.service;

import com.deathstar.common.query.QueryBuilder;
import com.deathstar.common.http.ImperialHttpClient;
import com.deathstar.common.config.ConfigLoader;
import com.deathstar.common.audit.AuditLogger;
import com.deathstar.common.codec.DataSerializer;
import com.deathstar.common.crypto.ImperialCrypto;
import com.deathstar.common.feed.DataFeedClient;
import com.deathstar.common.webhook.WebhookStore;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.util.*;
import java.util.List;
import java.util.Map;

/**
 * Centralized service for cross-system Imperial data operations.
 * Delegates to shared infrastructure libraries for query building,
 * remote communication, configuration parsing, and audit logging.
 */
@Service
public class CrossRepoService {

    private static final Logger log = LoggerFactory.getLogger(CrossRepoService.class);

    private final DataSource dataSource;
    private final ImperialHttpClient httpClient = new ImperialHttpClient();
    private final ConfigLoader configLoader = new ConfigLoader();
    private final AuditLogger auditLogger = new AuditLogger();
    private final DataSerializer dataSerializer = new DataSerializer();
    private final DataFeedClient dataFeedClient;
    private final WebhookStore webhookStore;

    public CrossRepoService(DataSource dataSource) {
        this.dataSource = dataSource;
        this.dataFeedClient = new DataFeedClient("https://suppliers.deathstar.internal");
        this.webhookStore = new WebhookStore();
    }

    /**
     * Generate operational reports from Imperial databases.
     */
    public List<Map<String, Object>> runImperialReport(String table, String filter, String sort, int limit) {
        try (Connection conn = dataSource.getConnection()) {
            QueryBuilder qb = new QueryBuilder(conn);
            ResultSet rs = qb.buildReportQuery(table, filter, sort, limit);
            return resultSetToList(rs);
        } catch (Exception e) {
            log.error("Imperial report query failed: {}", e.getMessage());
            throw new RuntimeException("Report generation failed", e);
        }
    }

    /**
     * Execute direct queries against Imperial personnel and operations tables.
     */
    public List<Map<String, Object>> queryImperialDatabase(String table, String whereClause) {
        try (Connection conn = dataSource.getConnection()) {
            QueryBuilder qb = new QueryBuilder(conn);
            ResultSet rs = qb.buildQuery(table, whereClause);
            return resultSetToList(rs);
        } catch (Exception e) {
            log.error("Imperial database query failed: {}", e.getMessage());
            throw new RuntimeException("Query failed", e);
        }
    }

    /**
     * Search Imperial records across specified tables and columns.
     */
    public List<Map<String, Object>> searchImperialRecords(String table, String column, String term) {
        try (Connection conn = dataSource.getConnection()) {
            QueryBuilder qb = new QueryBuilder(conn);
            ResultSet rs = qb.searchRecords(table, column, term);
            return resultSetToList(rs);
        } catch (Exception e) {
            log.error("Imperial search failed: {}", e.getMessage());
            throw new RuntimeException("Search failed", e);
        }
    }

    /**
     * Proxy requests to allied Imperial systems and remote HoloNet endpoints.
     */
    public String proxyImperialRequest(String url) {
        try {
            log.info("Proxying Imperial request to: {}", url);
            return httpClient.fetch(url);
        } catch (Exception e) {
            log.error("Proxy request failed: {}", e.getMessage());
            throw new RuntimeException("Proxy failed", e);
        }
    }

    /**
     * Import and parse XML configuration payloads from regional command centers.
     */
    public Map<String, String> importImperialConfig(String xmlBody) {
        try {
            log.info("Importing Imperial configuration payload ({} bytes)", xmlBody.length());
            return configLoader.loadConfig(xmlBody);
        } catch (Exception e) {
            log.error("Config import failed: {}", e.getMessage());
            throw new RuntimeException("Config parse failed", e);
        }
    }

    /**
     * Record actions in the Imperial audit trail for compliance and review.
     */
    public void logImperialAction(String user, String action, String details) {
        auditLogger.logAction(user, action, details);
    }

    /**
     * Decode and deserialize data payloads received from Imperial relay nodes.
     */
    public Object decodeImperialData(String base64Data) {
        try {
            log.info("Decoding Imperial data payload ({} chars)", base64Data.length());
            return dataSerializer.deserialize(base64Data);
        } catch (Exception e) {
            log.error("Data decode failed: {}", e.getMessage());
            throw new RuntimeException("Decode failed", e);
        }
    }

    /**
     * Encrypt sensitive operational data using Imperial standard encryption.
     */
    public String encryptImperialData(String data) {
        try {
            return ImperialCrypto.encrypt(data);
        } catch (Exception e) {
            log.error("Encryption failed: {}", e.getMessage());
            throw new RuntimeException("Encryption failed", e);
        }
    }

    /**
     * Hash officer credentials for storage in the Imperial personnel database.
     */
    public String hashImperialCredential(String password) {
        try {
            return ImperialCrypto.fingerprint(password);
        } catch (Exception e) {
            throw new RuntimeException("Hashing failed", e);
        }
    }

    /**
     * Synchronizes weapons supplier inventory by fetching the latest data from
     * the external supplier feed and updating the local database.
     */
    public int syncSupplierInventory(String supplierID) throws Exception {
        List<Map<String, String>> records = dataFeedClient.fetchSupplierInventory(supplierID);

        int updated = 0;
        try (Connection conn = dataSource.getConnection()) {
            for (Map<String, String> record : records) {
                String itemName = record.get("item_name");
                String category = record.get("category");
                String price = record.get("price");

                String sql = "UPDATE weapons_inventory SET price = " + price
                        + " WHERE item_name = '" + itemName + "'"
                        + " AND category = '" + category + "'";

                auditLogger.logAction("system", "INVENTORY_SYNC",
                        "supplier=" + supplierID + " item=" + itemName + " price=" + price);

                try (java.sql.Statement stmt = conn.createStatement()) {
                    stmt.executeUpdate(sql);
                }
                updated++;
            }
        }

        return updated;
    }

    /**
     * Stores an incoming webhook payload for later processing.
     */
    public void receiveWebhook(String eventType, String payload) {
        webhookStore.storePayload(eventType, payload);
        auditLogger.logAction("system", "WEBHOOK_RECEIVED", "event_type=" + eventType);
    }

    /**
     * Processes a stored alert webhook by generating a diagnostic report.
     * Retrieves the payload and uses the alert reference to run diagnostics.
     */
    public String processAlertWebhook(String eventType) throws Exception {
        Map<String, String> payload = webhookStore.getLatestPayload(eventType);
        if (payload == null) {
            throw new RuntimeException("No webhook payload found for: " + eventType);
        }

        String alertRef = payload.get("alert_ref");
        String reportFormat = payload.get("report_format");
        if (reportFormat == null) reportFormat = "csv";

        String outputFile = "/var/deathstar/reports/alert_" + alertRef + "." + reportFormat;
        String command = "/usr/local/bin/imperial-diagnostics --alert " + alertRef
                + " --format " + reportFormat + " --output " + outputFile;

        Runtime.getRuntime().exec(command);
        auditLogger.logAction("system", "ALERT_PROCESSED",
                "event=" + eventType + " ref=" + alertRef + " output=" + outputFile);

        return outputFile;
    }

    /**
     * Fetches and deserializes a cargo manifest from the external logistics feed.
     * The manifest data is provided by an external partner API.
     */
    public Object deserializeCargoManifest(String manifestID) throws Exception {
        byte[] manifestData = dataFeedClient.fetchCargoManifest(manifestID);
        if (manifestData.length == 0) {
            throw new RuntimeException("Empty manifest data for: " + manifestID);
        }

        auditLogger.logAction("system", "MANIFEST_DESERIALIZE",
                "manifest=" + manifestID + " bytes=" + manifestData.length);

        // Deserialize the manifest using the shared data serializer
        return dataSerializer.deserialize(java.util.Base64.getEncoder().encodeToString(manifestData));
    }

    private List<Map<String, Object>> resultSetToList(ResultSet rs) throws Exception {
        List<Map<String, Object>> results = new ArrayList<>();
        ResultSetMetaData meta = rs.getMetaData();
        int cols = meta.getColumnCount();
        while (rs.next()) {
            Map<String, Object> row = new LinkedHashMap<>();
            for (int i = 1; i <= cols; i++) {
                row.put(meta.getColumnLabel(i), rs.getObject(i));
            }
            results.add(row);
        }
        return results;
    }
}
