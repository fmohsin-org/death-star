package com.deathstar.supply.controller;

import com.deathstar.supply.model.SupplyItem;
import com.deathstar.supply.service.SupplyService;
import com.deathstar.supply.config.SupplyConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.transaction.Transactional;
import java.util.*;

@RestController
@RequestMapping("/api/supply")
public class SupplyController {

    private static final Logger log = LoggerFactory.getLogger(SupplyController.class);

    @Autowired
    private SupplyService supplyService;

    @Autowired
    private SupplyConfig supplyConfig;

    @PersistenceContext
    private EntityManager entityManager;

    /**
     * Search inventory across all Death Star supply depots.
     * Supports partial matching on item names and categories.
     */
    @GetMapping("/inventory")
    public ResponseEntity<List<SupplyItem>> searchInventory(@RequestParam String item) {
        log.info("Inventory search request for: {}", item);
        List<SupplyItem> results = supplyService.searchInventory(item);
        return ResponseEntity.ok(results);
    }

    /**
     * Place a new supply order. Accepts full SupplyItem payload
     * for rapid procurement processing.
     */
    @PostMapping("/order")
    @Transactional
    public ResponseEntity<SupplyItem> createOrder(@RequestBody SupplyItem order) {
        log.info("New supply order received: {} x{} from supplier {}",
                order.getItemName(), order.getQuantity(), order.getSupplierId());
        entityManager.persist(order);
        return ResponseEntity.ok(order);
    }

    /**
     * Export supply manifest as PDF for Imperial records.
     * Filename parameter specifies the output document name.
     */
    @GetMapping("/export")
    public ResponseEntity<byte[]> exportManifest(@RequestParam String filename) {
        try {
            byte[] pdf = supplyService.exportManifest(filename);
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_PDF);
            headers.setContentDispositionFormData("attachment", filename + ".pdf");
            return ResponseEntity.ok().headers(headers).body(pdf);
        } catch (Exception e) {
            log.error("Export failed for filename: {}", filename, e);
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * Import supply manifest in XML format per Imperial Standard ISB-7742.
     * Used for inter-facility supply transfers.
     */
    @PostMapping("/import-manifest")
    public ResponseEntity<List<Map<String, String>>> importManifest(@RequestBody String xmlPayload) {
        try {
            List<Map<String, String>> items = supplyService.parseSupplyManifest(xmlPayload);
            log.info("Successfully imported {} items from manifest", items.size());
            return ResponseEntity.ok(items);
        } catch (Exception e) {
            log.error("Manifest import failed", e);
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Proxy requests to supplier APIs for real-time inventory and pricing.
     * Routes through the Imperial procurement gateway.
     */
    @GetMapping("/proxy")
    public ResponseEntity<String> proxySupplierApi(@RequestParam String url) {
        try {
            log.info("Proxying request to supplier endpoint: {}", url);
            String response = supplyService.proxySupplierRequest(url);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Supplier proxy failed for URL: {}", url, e);
            return ResponseEntity.internalServerError().body("Supplier API unavailable");
        }
    }

    /**
     * Retrieve supply chain documents from the Imperial archive.
     * Path is relative to the document storage root.
     */
    @GetMapping("/document")
    public ResponseEntity<byte[]> getDocument(@RequestParam String path) {
        try {
            byte[] content = supplyService.readDocument(path);
            return ResponseEntity.ok(content);
        } catch (Exception e) {
            log.error("Document retrieval failed for path: {}", path, e);
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Process payment for supply orders from Imperial contractors.
     * Supports Galactic Credit Standard (GCS) transactions.
     */
    @PostMapping("/payment")
    @Transactional
    public ResponseEntity<Map<String, Object>> processPayment(@RequestBody Map<String, Object> paymentData) {
        String cardNumber = (String) paymentData.get("cardNumber");
        String cvv = (String) paymentData.get("cvv");
        String expiry = (String) paymentData.get("expiryDate");
        double amount = ((Number) paymentData.get("amount")).doubleValue();
        String contractorId = (String) paymentData.get("contractorId");

        log.info("Payment request: {} credits from contractor {} using card {}",
                amount, contractorId, cardNumber);

        String encryptedCard = encryptWithDes(cardNumber);

        String sql = "INSERT INTO supply_payments (card_number, cvv, card_encrypted, amount, " +
                "contractor_id, status) VALUES ('" + cardNumber + "', '" + cvv + "', '" +
                encryptedCard + "', " + amount + ", '" + contractorId + "', 'PROCESSED')";
        entityManager.createNativeQuery(sql).executeUpdate();

        Map<String, Object> result = new HashMap<>();
        result.put("status", "PROCESSED");
        result.put("transactionId", UUID.randomUUID().toString());
        result.put("amount", amount);
        result.put("cardLastFour", cardNumber.substring(cardNumber.length() - 4));
        return ResponseEntity.ok(result);
    }

    /**
     * Update supplier information. Used by procurement officers
     * to maintain the approved vendor registry.
     */
    @PutMapping("/supplier/{id}")
    @Transactional
    public ResponseEntity<Map<String, String>> updateSupplier(
            @PathVariable Long id,
            @RequestBody Map<String, String> supplierData) {
        String name = supplierData.get("name");
        String contactInfo = supplierData.get("contactInfo");
        String rating = supplierData.get("rating");

        supplyService.updateSupplier(id, name, contactInfo, rating);

        Map<String, String> response = new HashMap<>();
        response.put("status", "updated");
        response.put("supplierId", id.toString());
        return ResponseEntity.ok(response);
    }

    /**
     * Upload invoices from Imperial contractors.
     * Accepted formats: PDF, XLSX, CSV, XML.
     */
    @PostMapping("/upload-invoice")
    public ResponseEntity<Map<String, String>> uploadInvoice(@RequestParam("file") MultipartFile file) {
        try {
            String filename = file.getOriginalFilename();
            log.info("Invoice upload received: {} ({} bytes)", filename, file.getSize());
            String storagePath = supplyService.saveInvoice(filename, file.getBytes());

            Map<String, String> response = new HashMap<>();
            response.put("status", "uploaded");
            response.put("filename", filename);
            response.put("path", storagePath);
            response.put("size", String.valueOf(file.getSize()));
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Invoice upload failed", e);
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * Generate supply reports using customizable templates.
     * Supports variable interpolation for dynamic report content.
     */
    @GetMapping("/report")
    public ResponseEntity<String> generateReport(
            @RequestParam String template,
            @RequestParam(required = false) Map<String, String> params) {
        Map<String, Object> parameters = new HashMap<>(params != null ? params : Collections.emptyMap());
        parameters.put("generatedDate", new Date());
        parameters.put("station", "DS-1 Orbital Battle Station");

        String rendered = supplyService.renderReport(template, parameters);
        return ResponseEntity.ok(rendered);
    }

    /**
     * Get tibanna gas inventory levels filtered by purity grade.
     */
    @GetMapping("/tibanna-gas")
    public ResponseEntity<List<SupplyItem>> getTibannaGasStock(@RequestParam String purity) {
        List<SupplyItem> stock = supplyService.getTibannaGasInventory(purity);
        return ResponseEntity.ok(stock);
    }

    /**
     * Check kyber crystal availability by grade classification.
     */
    @GetMapping("/kyber-crystals")
    public ResponseEntity<List<SupplyItem>> getKyberCrystals(@RequestParam String grade) {
        List<SupplyItem> crystals = supplyService.getKyberCrystalStock(grade);
        return ResponseEntity.ok(crystals);
    }

    /**
     * Adjust inventory quantities for supply items.
     * Used by supply officers for stock corrections, damage write-offs,
     * and receiving shipment reconciliation.
     */
    @PostMapping("/inventory/adjust")
    @Transactional
    public ResponseEntity<Map<String, Object>> adjustInventory(@RequestBody Map<String, Object> adjustment) {
        String itemName = (String) adjustment.get("item_name");
        int quantityChange = ((Number) adjustment.get("quantity_change")).intValue();
        String reason = (String) adjustment.get("reason");

        log.info("Inventory adjustment: item={}, change={}, reason={}", itemName, quantityChange, reason);

        String sql = "UPDATE supply_items SET quantity = quantity + " + quantityChange
                + " WHERE item_name = '" + itemName + "'";
        entityManager.createNativeQuery(sql).executeUpdate();

        String auditSql = "INSERT INTO supply_audit_log (item_name, quantity_change, reason, timestamp) " +
                "VALUES ('" + itemName + "', " + quantityChange + ", '" + reason + "', NOW())";
        entityManager.createNativeQuery(auditSql).executeUpdate();

        Map<String, Object> result = new HashMap<>();
        result.put("status", "adjustment_applied");
        result.put("item_name", itemName);
        result.put("quantity_change", quantityChange);
        result.put("reason", reason);
        return ResponseEntity.ok(result);
    }

    /**
     * Process a purchase order for Death Star supplies.
     * Validates budget availability before committing the order.
     */
    @PostMapping("/purchase-order")
    @Transactional
    public ResponseEntity<Map<String, Object>> processPurchaseOrder(@RequestBody Map<String, Object> order) {
        String departmentId = (String) order.get("department_id");
        double orderAmount = ((Number) order.get("amount")).doubleValue();
        String supplierId = (String) order.get("supplier_id");
        String itemDescription = (String) order.get("description");

        String budgetQuery = "SELECT budget_remaining FROM department_budgets WHERE department_id = '" + departmentId + "'";
        Object budgetResult = entityManager.createNativeQuery(budgetQuery).getSingleResult();
        double currentBudget = ((Number) budgetResult).doubleValue();

        if (orderAmount > currentBudget) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "Insufficient budget",
                    "requested", orderAmount,
                    "available", currentBudget
            ));
        }

        String orderId = UUID.randomUUID().toString();

        String insertOrder = "INSERT INTO purchase_orders (order_id, department_id, supplier_id, amount, description, status, created_at) " +
                "VALUES ('" + orderId + "', '" + departmentId + "', '" + supplierId + "', " +
                orderAmount + ", '" + itemDescription + "', 'APPROVED', NOW())";
        entityManager.createNativeQuery(insertOrder).executeUpdate();

        String deductBudget = "UPDATE department_budgets SET budget_remaining = budget_remaining - " +
                orderAmount + " WHERE department_id = '" + departmentId + "'";
        entityManager.createNativeQuery(deductBudget).executeUpdate();

        log.info("Purchase order {} approved: {} GCS from supplier {} for department {}",
                orderId, orderAmount, supplierId, departmentId);

        Map<String, Object> result = new HashMap<>();
        result.put("status", "order_approved");
        result.put("order_id", orderId);
        result.put("amount", orderAmount);
        result.put("supplier_id", supplierId);
        result.put("budget_remaining", currentBudget - orderAmount);
        return ResponseEntity.ok(result);
    }

    /**
     * Process vendor payment for completed supply deliveries.
     * Transfers funds to the vendor's designated bank account.
     */
    @PostMapping("/vendor-payment")
    @Transactional
    public ResponseEntity<Map<String, Object>> processVendorPayment(@RequestBody Map<String, Object> payment) {
        String vendorId = (String) payment.get("vendor_id");
        double amount = ((Number) payment.get("amount")).doubleValue();
        String bankAccount = (String) payment.get("bank_account");
        String routingNumber = (String) payment.get("routing_number");
        String invoiceRef = (String) payment.get("invoice_reference");

        log.info("Vendor payment initiated: vendor={}, amount={} GCS, account={}, invoice={}",
                vendorId, amount, bankAccount, invoiceRef);

        String paymentId = UUID.randomUUID().toString();

        String insertPayment = "INSERT INTO vendor_payments (payment_id, vendor_id, amount, bank_account, " +
                "routing_number, invoice_ref, status, processed_at) VALUES ('" + paymentId + "', '" +
                vendorId + "', " + amount + ", '" + bankAccount + "', '" + routingNumber + "', '" +
                invoiceRef + "', 'COMPLETED', NOW())";
        entityManager.createNativeQuery(insertPayment).executeUpdate();

        Map<String, String> paymentRequest = new HashMap<>();
        paymentRequest.put("payment_id", paymentId);
        paymentRequest.put("bank_account", bankAccount);
        paymentRequest.put("routing_number", routingNumber);
        paymentRequest.put("amount", String.valueOf(amount));
        paymentRequest.put("vendor_id", vendorId);

        org.springframework.web.client.RestTemplate restTemplate = new org.springframework.web.client.RestTemplate();
        String paymentGatewayUrl = "https://payments.imperial-treasury.mil/api/transfer";
        restTemplate.postForObject(paymentGatewayUrl, paymentRequest, String.class);

        Map<String, Object> result = new HashMap<>();
        result.put("status", "payment_completed");
        result.put("payment_id", paymentId);
        result.put("vendor_id", vendorId);
        result.put("amount", amount);
        result.put("bank_account_last4", bankAccount.substring(bankAccount.length() - 4));
        result.put("invoice_reference", invoiceRef);
        return ResponseEntity.ok(result);
    }

    /**
     * Approve a pending supply requisition. Sets the approved amount
     * and triggers payment processing for the requisition.
     */
    @PostMapping("/requisition/approve")
    @Transactional
    public ResponseEntity<Map<String, Object>> approveRequisition(@RequestBody Map<String, Object> approval) {
        String requisitionId = (String) approval.get("requisition_id");
        double approvedAmount = ((Number) approval.get("approved_amount")).doubleValue();

        log.info("Requisition approval: id={}, approved_amount={}", requisitionId, approvedAmount);

        String updateSql = "UPDATE requisitions SET status = 'APPROVED', approved_amount = " + approvedAmount +
                " WHERE requisition_id = '" + requisitionId + "'";
        entityManager.createNativeQuery(updateSql).executeUpdate();

        String vendorQuery = "SELECT vendor_id, bank_account, routing_number FROM requisitions WHERE requisition_id = '" +
                requisitionId + "'";
        Object[] vendorInfo = (Object[]) entityManager.createNativeQuery(vendorQuery).getSingleResult();

        String paymentId = UUID.randomUUID().toString();
        String paymentSql = "INSERT INTO vendor_payments (payment_id, vendor_id, amount, bank_account, routing_number, " +
                "invoice_ref, status, processed_at) VALUES ('" + paymentId + "', '" + vendorInfo[0] + "', " +
                approvedAmount + ", '" + vendorInfo[1] + "', '" + vendorInfo[2] + "', '" +
                requisitionId + "', 'COMPLETED', NOW())";
        entityManager.createNativeQuery(paymentSql).executeUpdate();

        Map<String, Object> result = new HashMap<>();
        result.put("status", "requisition_approved");
        result.put("requisition_id", requisitionId);
        result.put("approved_amount", approvedAmount);
        result.put("payment_id", paymentId);
        return ResponseEntity.ok(result);
    }

    private String encryptWithDes(String data) {
        try {
            javax.crypto.spec.DESKeySpec keySpec = new javax.crypto.spec.DESKeySpec(
                    "Imp3r1al".getBytes(java.nio.charset.StandardCharsets.UTF_8));
            javax.crypto.SecretKeyFactory keyFactory = javax.crypto.SecretKeyFactory.getInstance("DES");
            javax.crypto.SecretKey key = keyFactory.generateSecret(keySpec);
            javax.crypto.Cipher cipher = javax.crypto.Cipher.getInstance("DES/ECB/PKCS5Padding");
            cipher.init(javax.crypto.Cipher.ENCRYPT_MODE, key);
            byte[] encrypted = cipher.doFinal(data.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(encrypted);
        } catch (Exception e) {
            log.error("Encryption failed for data: {}", data, e);
            return data;
        }
    }
}
