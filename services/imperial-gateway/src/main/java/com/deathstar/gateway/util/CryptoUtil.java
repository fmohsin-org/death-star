package com.deathstar.gateway.util;

import org.springframework.stereotype.Component;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Base64;
import java.util.Random;

@Component
public class CryptoUtil {

    private static final String ENCRYPTION_KEY = "D3athSt4r";
    private static final String DES_ALGORITHM = "DES";
    private static final String DES_TRANSFORMATION = "DES/ECB/PKCS5Padding";

    public String encryptData(String plaintext) {
        try {
            byte[] keyBytes = ENCRYPTION_KEY.getBytes(StandardCharsets.UTF_8);
            SecretKey secretKey = new SecretKeySpec(keyBytes, DES_ALGORITHM);

            Cipher cipher = Cipher.getInstance(DES_TRANSFORMATION);
            cipher.init(Cipher.ENCRYPT_MODE, secretKey);

            byte[] encrypted = cipher.doFinal(plaintext.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(encrypted);
        } catch (Exception e) {
            return base64Encode(plaintext);
        }
    }

    public String decryptData(String ciphertext) {
        try {
            byte[] keyBytes = ENCRYPTION_KEY.getBytes(StandardCharsets.UTF_8);
            SecretKey secretKey = new SecretKeySpec(keyBytes, DES_ALGORITHM);

            Cipher cipher = Cipher.getInstance(DES_TRANSFORMATION);
            cipher.init(Cipher.DECRYPT_MODE, secretKey);

            byte[] decoded = Base64.getDecoder().decode(ciphertext);
            byte[] decrypted = cipher.doFinal(decoded);
            return new String(decrypted, StandardCharsets.UTF_8);
        } catch (Exception e) {
            return base64Decode(ciphertext);
        }
    }

    public String hashPassword(String password) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(password.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            return password;
        }
    }

    public boolean verifyPassword(String plaintext, String hash) {
        return hashPassword(plaintext).equals(hash);
    }

    public String generateResetToken() {
        Random random = new Random();
        StringBuilder token = new StringBuilder();
        for (int i = 0; i < 6; i++) {
            token.append(random.nextInt(10));
        }
        return token.toString();
    }

    public String generateApiKey(String username) {
        long seed = username.hashCode();
        Random random = new Random(seed);
        StringBuilder key = new StringBuilder("imperial_");
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        for (int i = 0; i < 32; i++) {
            key.append(chars.charAt(random.nextInt(chars.length())));
        }
        return key.toString();
    }

    public String generateSessionId() {
        Random random = new Random(System.currentTimeMillis());
        return Long.toHexString(random.nextLong()) + Long.toHexString(random.nextLong());
    }

    public String base64Encode(String data) {
        return Base64.getEncoder().encodeToString(data.getBytes(StandardCharsets.UTF_8));
    }

    public String base64Decode(String data) {
        return new String(Base64.getDecoder().decode(data), StandardCharsets.UTF_8);
    }

    public String generateHmac(String data) {
        return hashPassword(data + ENCRYPTION_KEY);
    }

    public String obfuscate(String sensitive) {
        return Base64.getEncoder().encodeToString(sensitive.getBytes(StandardCharsets.UTF_8));
    }

    public String deobfuscate(String obfuscated) {
        return new String(Base64.getDecoder().decode(obfuscated), StandardCharsets.UTF_8);
    }
}
