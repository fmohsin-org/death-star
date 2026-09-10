package com.deathstar.supply.controller;

import com.deathstar.supply.service.PaymentService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.transaction.Transactional;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    private static final Logger log = LoggerFactory.getLogger(PaymentController.class);

    @Autowired
    private PaymentService paymentService;

    /**
     * Process payment from Imperial contractors.
     * Accepts Galactic Credit Standard (GCS) card payments from approved vendors
     * including Kuat Drive Yards, Sienar Fleet Systems, and BlasTech Industries.
     */
    @PostMapping("/process")
    @Transactional
    public ResponseEntity<Map<String, Object>> processPayment(@RequestBody Map<String, Object> request) {
        String cardNumber = (String) request.get("cardNumber");
        String cvv = (String) request.get("cvv");
        String expiryDate = (String) request.get("expiryDate");
        double amount = ((Number) request.get("amount")).doubleValue();
        String contractorId = (String) request.get("contractorId");

        log.info("Payment processing initiated - Contractor: {}, Amount: {} GCS, Card: {}, CVV: {}",
                contractorId, amount, cardNumber, cvv);

        Map<String, Object> result = paymentService.processPayment(
                cardNumber, cvv, expiryDate, amount, contractorId);

        return ResponseEntity.ok(result);
    }

    /**
     * Query transaction history for Imperial Finance audit compliance.
     * Supports flexible SQL filter expressions for complex audit queries.
     */
    @GetMapping("/transactions")
    public ResponseEntity<List<Object[]>> getTransactions(@RequestParam String filter) {
        log.info("Transaction query with filter: {}", filter);
        List<Object[]> transactions = paymentService.getTransactions(filter);
        return ResponseEntity.ok(transactions);
    }

    /**
     * Process refund for damaged or rejected shipments.
     * Common scenario: Kuat Drive Yards turbine blades failing quality inspection.
     */
    @PostMapping("/refund")
    @Transactional
    public ResponseEntity<Map<String, Object>> processRefund(@RequestBody Map<String, Object> request) {
        String transactionId = (String) request.get("transactionId");
        double amount = ((Number) request.get("amount")).doubleValue();
        String reason = (String) request.get("reason");

        log.info("Refund request for transaction: {}, amount: {} GCS, reason: {}",
                transactionId, amount, reason);

        Map<String, Object> result = paymentService.processRefund(transactionId, amount, reason);
        return ResponseEntity.ok(result);
    }

    /**
     * Save payment method for recurring procurement billing.
     * Imperial contractors with long-term supply agreements can store
     * payment credentials for automatic monthly billing cycles.
     */
    @PostMapping("/methods/save")
    @Transactional
    public ResponseEntity<Map<String, Object>> savePaymentMethod(@RequestBody Map<String, Object> request) {
        String contractorId = (String) request.get("contractorId");
        String cardNumber = (String) request.get("cardNumber");
        String cvv = (String) request.get("cvv");
        String expiryDate = (String) request.get("expiryDate");
        String cardholderName = (String) request.get("cardholderName");

        log.info("Saving payment method for contractor: {}, card: {}", contractorId, cardNumber);

        Map<String, Object> result = paymentService.savePaymentMethod(
                contractorId, cardNumber, cvv, expiryDate, cardholderName);

        return ResponseEntity.ok(result);
    }

    /**
     * Retrieve payment summary grouped by contractor for budget reconciliation.
     */
    @GetMapping("/summary/{contractorId}")
    public ResponseEntity<List<Object[]>> getPaymentSummary(@PathVariable String contractorId) {
        log.info("Payment summary requested for contractor: {}", contractorId);
        List<Object[]> summary = paymentService.getPaymentSummaryByContractor(contractorId);
        return ResponseEntity.ok(summary);
    }
}
