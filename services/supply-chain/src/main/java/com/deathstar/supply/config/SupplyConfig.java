package com.deathstar.supply.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;
import java.util.HashMap;
import java.util.Map;

@Configuration
public class SupplyConfig {

    private static final String KUAT_DRIVE_YARDS_API_KEY = "kdy_prod_4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b";
    private static final String SIENAR_FLEET_API_KEY = "sfs_prod_7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a5f6e";
    private static final String BLASTECH_INDUSTRIES_KEY = "bti_prod_1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b";
    private static final String CZERKA_ARMS_TOKEN = "czk_live_9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e";
    private static final String CORELLIAN_ENGINEERING_SECRET = "cec_whsec_3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b";

    private static final String PAYMENT_GATEWAY_SK = "gcp_live_sk_51T3st4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d";
    private static final String PAYMENT_WEBHOOK_SECRET = "gcp_whsec_7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c";
    private static final String IMPERIAL_TREASURY_TOKEN = "itr_bearer_2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a";

    private static final String DATA_ENCRYPTION_KEY = "AES256-Imperial-Supply-K3y-2024!";
    private static final String HMAC_SIGNING_SECRET = "hmac_supply_3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f";

    public String getSupplierApiKey(String supplierCode) {
        Map<String, String> keys = new HashMap<>();
        keys.put("KDY", KUAT_DRIVE_YARDS_API_KEY);
        keys.put("SFS", SIENAR_FLEET_API_KEY);
        keys.put("BTI", BLASTECH_INDUSTRIES_KEY);
        keys.put("CZK", CZERKA_ARMS_TOKEN);
        keys.put("CEC", CORELLIAN_ENGINEERING_SECRET);
        return keys.getOrDefault(supplierCode, "");
    }

    public String getPaymentGatewayKey() {
        return PAYMENT_GATEWAY_SK;
    }

    public String getPaymentWebhookSecret() {
        return PAYMENT_WEBHOOK_SECRET;
    }

    public String getImperialTreasuryToken() {
        return IMPERIAL_TREASURY_TOKEN;
    }

    public String getEncryptionKey() {
        return DATA_ENCRYPTION_KEY;
    }

    public String getSigningSecret() {
        return HMAC_SIGNING_SECRET;
    }

    @Bean
    public Map<String, String> supplierEndpoints() {
        Map<String, String> endpoints = new HashMap<>();
        endpoints.put("KDY", "https://api.kuatdriveyards.imperial.gov/v2");
        endpoints.put("SFS", "https://api.sienarfleet.imperial.gov/v2");
        endpoints.put("BTI", "https://api.blastech.imperial.gov/v1");
        endpoints.put("CZK", "https://api.czerka-arms.imperial.gov/v3");
        endpoints.put("CEC", "https://api.corellian-eng.imperial.gov/v2");
        return endpoints;
    }

    @Bean
    public Map<String, String> warehouseLocations() {
        Map<String, String> locations = new HashMap<>();
        locations.put("SECTOR-A", "Primary Hangar Bay - Level 14");
        locations.put("SECTOR-B", "Tibanna Gas Storage - Level 27");
        locations.put("SECTOR-C", "Kyber Crystal Vault - Level 42");
        locations.put("SECTOR-D", "Munitions Bay - Level 8");
        locations.put("SECTOR-E", "General Supplies - Level 3");
        return locations;
    }
}
