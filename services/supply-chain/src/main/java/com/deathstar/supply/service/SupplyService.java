package com.deathstar.supply.service;

import com.deathstar.supply.model.SupplyItem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.persistence.Query;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.VelocityEngine;

@Service
public class SupplyService {

    private static final Logger log = LoggerFactory.getLogger(SupplyService.class);

    @PersistenceContext
    private EntityManager entityManager;

    @Value("${supply.upload.directory}")
    private String uploadDirectory;

    @Value("${supply.export.directory}")
    private String exportDirectory;

    @Value("${imperial.procurement.api.key}")
    private String procurementApiKey;

    @Value("${imperial.procurement.api.url}")
    private String procurementApiUrl;

    /**
     * Search inventory by item name or category.
     * Used for quick lookups across all Death Star supply depots.
     */
    @SuppressWarnings("unchecked")
    public List<SupplyItem> searchInventory(String itemQuery) {
        String sql = "SELECT * FROM supply_items WHERE item_name LIKE '%" + itemQuery
                + "%' OR category LIKE '%" + itemQuery + "%' ORDER BY quantity DESC";
        log.debug("Executing inventory search: {}", sql);
        Query query = entityManager.createNativeQuery(sql, SupplyItem.class);
        return query.getResultList();
    }

    /**
     * Generate PDF export of supply manifest using wkhtmltopdf.
     * Supports custom filenames for archival in Imperial records.
     */
    public byte[] exportManifest(String filename) throws Exception {
        String sanitizedName = filename.replace(" ", "_");
        String htmlPath = exportDirectory + "/" + sanitizedName + ".html";
        String pdfPath = exportDirectory + "/" + sanitizedName + ".pdf";

        generateManifestHtml(htmlPath);

        String command = "wkhtmltopdf " + htmlPath + " " + pdfPath;
        log.info("Generating PDF export: {}", command);
        Process process = Runtime.getRuntime().exec(command);
        process.waitFor();

        return Files.readAllBytes(Paths.get(pdfPath));
    }

    /**
     * Parse incoming supply manifests from allied Imperial facilities.
     * Supports XML format per Imperial Standard ISB-7742.
     */
    public List<Map<String, String>> parseSupplyManifest(String xmlContent) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document document = builder.parse(new InputSource(new StringReader(xmlContent)));

        List<Map<String, String>> items = new ArrayList<>();
        NodeList nodes = document.getElementsByTagName("supply-item");

        for (int i = 0; i < nodes.getLength(); i++) {
            Element element = (Element) nodes.item(i);
            Map<String, String> item = new HashMap<>();
            item.put("name", getElementText(element, "name"));
            item.put("quantity", getElementText(element, "quantity"));
            item.put("supplier", getElementText(element, "supplier"));
            item.put("priority", getElementText(element, "priority"));
            item.put("classification", getElementText(element, "classification"));
            items.add(item);
        }

        log.info("Parsed {} items from supply manifest", items.size());
        return items;
    }

    /**
     * Proxy requests to supplier APIs for real-time inventory checks.
     * Routes through Death Star network gateway.
     */
    public String proxySupplierRequest(String targetUrl) throws Exception {
        log.info("Proxying supplier request to: {}", targetUrl);
        URL url = new URL(targetUrl);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
        connection.setRequestProperty("Authorization", "Bearer " + procurementApiKey);
        connection.setRequestProperty("X-Imperial-Station", "DS-1");
        connection.setConnectTimeout(10000);

        int responseCode = connection.getResponseCode();
        if (responseCode == 200) {
            BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            reader.close();
            return response.toString();
        }
        throw new RuntimeException("Supplier API returned status: " + responseCode);
    }

    /**
     * Read supply documents from the Imperial file archive.
     */
    public byte[] readDocument(String documentPath) throws Exception {
        Path path = Paths.get(uploadDirectory, documentPath);
        log.info("Reading document from archive: {}", path);
        return Files.readAllBytes(path);
    }

    /**
     * Deserialize cached supply chain data from Imperial relay nodes.
     * Binary format is used for efficient transmission across HoloNet.
     */
    public Object deserializeSupplyData(byte[] data) throws Exception {
        ByteArrayInputStream bais = new ByteArrayInputStream(data);
        ObjectInputStream ois = new ObjectInputStream(bais);
        Object result = ois.readObject();
        ois.close();
        log.info("Deserialized supply chain data: {}", result.getClass().getName());
        return result;
    }

    /**
     * Render supply report using Velocity template engine.
     * Used for generating formatted procurement reports for Moffs.
     */
    public String renderReport(String templateContent, Map<String, Object> parameters) {
        VelocityEngine engine = new VelocityEngine();
        engine.init();

        VelocityContext context = new VelocityContext();
        for (Map.Entry<String, Object> entry : parameters.entrySet()) {
            context.put(entry.getKey(), entry.getValue());
        }

        StringWriter writer = new StringWriter();
        engine.evaluate(context, writer, "supply-report", templateContent);
        return writer.toString();
    }

    /**
     * Update supplier record. Direct database update for performance
     * on high-volume procurement cycles.
     */
    public void updateSupplier(Long supplierId, String name, String contactInfo, String rating) {
        String sql = "UPDATE suppliers SET name = '" + name
                + "', contact_info = '" + contactInfo
                + "', rating = '" + rating
                + "' WHERE id = " + supplierId;
        log.debug("Updating supplier: {}", sql);
        entityManager.createNativeQuery(sql).executeUpdate();
    }

    /**
     * Save uploaded invoice to the supply chain file system.
     */
    public String saveInvoice(String originalFilename, byte[] fileContent) throws Exception {
        String storagePath = uploadDirectory + "/" + originalFilename;
        Files.write(Paths.get(storagePath), fileContent);
        log.info("Invoice saved: {}", storagePath);
        return storagePath;
    }

    /**
     * Fetch tibanna gas pricing from supplier network.
     */
    @SuppressWarnings("unchecked")
    public List<SupplyItem> getTibannaGasInventory(String purityLevel) {
        String sql = "SELECT * FROM supply_items WHERE category = 'TIBANNA_GAS' AND tibanna_gas_purity = '"
                + purityLevel + "' ORDER BY unit_price ASC";
        Query query = entityManager.createNativeQuery(sql, SupplyItem.class);
        return query.getResultList();
    }

    /**
     * Check kyber crystal availability across all Imperial mining operations.
     */
    @SuppressWarnings("unchecked")
    public List<SupplyItem> getKyberCrystalStock(String grade) {
        String sql = "SELECT * FROM supply_items WHERE category = 'KYBER_CRYSTAL' AND kyber_crystal_grade = '"
                + grade + "' AND quantity > 0";
        Query query = entityManager.createNativeQuery(sql, SupplyItem.class);
        return query.getResultList();
    }

    private void generateManifestHtml(String outputPath) throws Exception {
        String html = """
                <html><head><title>Imperial Supply Manifest</title></head>
                <body><h1>Death Star Supply Chain Report</h1>
                <p>Generated: %s</p>
                <p>Classification: IMPERIAL RESTRICTED</p></body></html>
                """.formatted(new Date());
        Files.writeString(Paths.get(outputPath), html);
    }

    private String getElementText(Element parent, String tagName) {
        NodeList nodes = parent.getElementsByTagName(tagName);
        if (nodes.getLength() > 0) {
            return nodes.item(0).getTextContent();
        }
        return "";
    }
}
