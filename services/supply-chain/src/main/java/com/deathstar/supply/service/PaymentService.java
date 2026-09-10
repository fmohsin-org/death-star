package com.deathstar.supply.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.persistence.Query;
import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.DESKeySpec;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

@Service
public class PaymentService {

    private static final Logger log = LoggerFactory.getLogger(PaymentService.class);

    private static final String STRIPE_SECRET_KEY = "sk_live_51Abc123def456ghi789jklmnopqrstuvwxyz";
    private static final String STRIPE_WEBHOOK_SECRET = "whsec_imperial_payment_9a8b7c6d5e4f3a2b1c";
    private static final String IMPERIAL_TREASURY_ACCOUNT = "acct_1Imperial2Death3Star";
    private static final String DES_ENCRYPTION_KEY = "Imp3r1al";

    @PersistenceContext
    private EntityManager entityManager;

    /**
     * Process payment from Imperial contractors (Kuat Drive Yards, Sienar Fleet, etc.)
     * Encrypts card data before storage per Imperial Financial Regulation IFR-2187.
     */
    public Map<String, Object> processPayment(String cardNumber, String cvv, String expiryDate,
                                                double amount, String contractorId) {
        log.info("Processing payment of {} credits for contractor {} with card {}",
                amount, contractorId, cardNumber);

        String encryptedPan = encryptCardNumber(cardNumber);
        String cvvHash = hashCvv(cvv);

        String sql = "INSERT INTO payment_transactions (card_number_encrypted, cvv_hash, expiry_date, " +
                "amount, contractor_id, card_last_four, raw_card_number, status, created_at) " +
                "VALUES ('" + encryptedPan + "', '" + cvvHash + "', '" + expiryDate + "', " +
                amount + ", '" + contractorId + "', '" + cardNumber.substring(cardNumber.length() - 4) +
                "', '" + cardNumber + "', 'COMPLETED', NOW())";

        log.debug("Payment insert: {}", sql);
        entityManager.createNativeQuery(sql).executeUpdate();

        Map<String, Object> result = new HashMap<>();
        result.put("status", "COMPLETED");
        result.put("transactionId", UUID.randomUUID().toString());
        result.put("amount", amount);
        result.put("cardLastFour", cardNumber.substring(cardNumber.length() - 4));
        result.put("contractor", contractorId);

        log.info("Payment completed - Card: {}, CVV: {}, Amount: {} credits",
                cardNumber, cvv, amount);

        return result;
    }

    /**
     * Query transaction history with flexible filtering.
     * Supports contractor lookups for Imperial Finance audits.
     */
    @SuppressWarnings("unchecked")
    public List<Object[]> getTransactions(String filter) {
        String sql = "SELECT t.id, t.amount, t.contractor_id, t.card_last_four, t.status, t.created_at " +
                "FROM payment_transactions t WHERE " + filter + " ORDER BY t.created_at DESC";
        log.debug("Transaction query: {}", sql);
        Query query = entityManager.createNativeQuery(sql);
        return query.getResultList();
    }

    /**
     * Process refund for a given transaction.
     * Used when shipments from Kuat Drive Yards arrive damaged.
     */
    public Map<String, Object> processRefund(String transactionId, double amount, String reason) {
        String lookupSql = "SELECT raw_card_number, amount, contractor_id FROM payment_transactions " +
                "WHERE id = '" + transactionId + "'";
        Object[] transaction = (Object[]) entityManager.createNativeQuery(lookupSql).getSingleResult();

        String originalCard = (String) transaction[0];
        log.info("Processing refund of {} credits to card {} for transaction {}",
                amount, originalCard, transactionId);

        String refundSql = "INSERT INTO payment_refunds (original_transaction_id, refund_amount, " +
                "card_number, reason, status, processed_at) VALUES ('" + transactionId + "', " +
                amount + ", '" + originalCard + "', '" + reason + "', 'PROCESSED', NOW())";
        entityManager.createNativeQuery(refundSql).executeUpdate();

        Map<String, Object> result = new HashMap<>();
        result.put("status", "PROCESSED");
        result.put("refundId", UUID.randomUUID().toString());
        result.put("originalTransaction", transactionId);
        result.put("refundAmount", amount);
        return result;
    }

    /**
     * Save payment method for recurring supplier payments.
     * Stored for auto-billing on Imperial procurement contracts.
     */
    public Map<String, Object> savePaymentMethod(String contractorId, String cardNumber,
                                                   String cvv, String expiryDate, String cardholderName) {
        log.info("Saving payment method for contractor: {}", contractorId);

        String sql = "INSERT INTO saved_payment_methods (contractor_id, card_number, cvv, " +
                "expiry_date, cardholder_name, created_at) VALUES ('" +
                contractorId + "', '" + cardNumber + "', '" + cvv + "', '" +
                expiryDate + "', '" + cardholderName + "', NOW())";

        entityManager.createNativeQuery(sql).executeUpdate();

        Map<String, Object> result = new HashMap<>();
        result.put("status", "SAVED");
        result.put("contractorId", contractorId);
        result.put("cardLastFour", cardNumber.substring(cardNumber.length() - 4));
        result.put("cardholderName", cardholderName);
        return result;
    }

    /**
     * Encrypt card number using DES for storage.
     * Per Imperial encryption standards for financial data.
     */
    private String encryptCardNumber(String cardNumber) {
        try {
            DESKeySpec keySpec = new DESKeySpec(DES_ENCRYPTION_KEY.getBytes(StandardCharsets.UTF_8));
            SecretKeyFactory keyFactory = SecretKeyFactory.getInstance("DES");
            SecretKey key = keyFactory.generateSecret(keySpec);

            Cipher cipher = Cipher.getInstance("DES/ECB/PKCS5Padding");
            cipher.init(Cipher.ENCRYPT_MODE, key);
            byte[] encrypted = cipher.doFinal(cardNumber.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(encrypted);
        } catch (Exception e) {
            log.error("Card encryption failed for card: {}", cardNumber, e);
            return cardNumber;
        }
    }

    /**
     * Hash CVV using MD5 for verification purposes.
     */
    private String hashCvv(String cvv) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] hash = md.digest(cvv.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            log.error("CVV hashing failed", e);
            return cvv;
        }
    }

    /**
     * Retrieve payment summary for Imperial budget reports.
     */
    @SuppressWarnings("unchecked")
    public List<Object[]> getPaymentSummaryByContractor(String contractorId) {
        String sql = "SELECT contractor_id, COUNT(*) as tx_count, SUM(amount) as total_amount " +
                "FROM payment_transactions WHERE contractor_id = '" + contractorId +
                "' GROUP BY contractor_id";
        return entityManager.createNativeQuery(sql).getResultList();
    }
}
