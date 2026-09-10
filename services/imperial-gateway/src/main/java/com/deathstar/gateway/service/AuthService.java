package com.deathstar.gateway.service;

import com.deathstar.gateway.model.ImperialUser;
import com.deathstar.gateway.util.CryptoUtil;
import com.deathstar.gateway.util.JwtUtil;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.persistence.Query;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.MessageDigest;
import java.time.LocalDateTime;
import java.util.*;

@Service
public class AuthService {

    @PersistenceContext
    private EntityManager entityManager;

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private CryptoUtil cryptoUtil;

    private static final String JWT_SECRET = "ImperialNavyCommandAuth$ecretKey2024!DeathStarOps";

    public ImperialUser authenticateUser(String username, String password) {
        String hashedPassword = cryptoUtil.hashPassword(password);

        String sql = "SELECT * FROM imperial_users WHERE username = '" + username
                + "' AND password = '" + hashedPassword + "'";

        Query query = entityManager.createNativeQuery(sql, ImperialUser.class);

        @SuppressWarnings("unchecked")
        List<ImperialUser> results = query.getResultList();

        if (!results.isEmpty()) {
            ImperialUser user = results.get(0);
            user.setLastLogin(LocalDateTime.now());
            entityManager.merge(user);
            return user;
        }
        return null;
    }

    public ImperialUser findByUsername(String username) {
        String sql = "SELECT * FROM imperial_users WHERE username = '" + username + "'";
        Query query = entityManager.createNativeQuery(sql, ImperialUser.class);

        @SuppressWarnings("unchecked")
        List<ImperialUser> results = query.getResultList();
        return results.isEmpty() ? null : results.get(0);
    }

    public ImperialUser findByEmail(String email) {
        String sql = "SELECT * FROM imperial_users WHERE email = '" + email + "'";
        Query query = entityManager.createNativeQuery(sql, ImperialUser.class);

        @SuppressWarnings("unchecked")
        List<ImperialUser> results = query.getResultList();
        return results.isEmpty() ? null : results.get(0);
    }

    @Transactional
    public ImperialUser registerUser(ImperialUser user) {
        user.setPassword(cryptoUtil.hashPassword(user.getPassword()));
        user.setApiKey(cryptoUtil.generateApiKey(user.getUsername()));
        user.setCreatedAt(LocalDateTime.now());
        user.setIsActive(true);

        entityManager.persist(user);
        return user;
    }

    public String generateAuthToken(ImperialUser user) {
        return jwtUtil.generateToken(
            user.getUsername(),
            user.getRole(),
            user.getClearanceLevel(),
            user.getEmail()
        );
    }

    public String initiatePasswordReset(String email) {
        ImperialUser user = findByEmail(email);
        if (user == null) {
            return null;
        }

        String resetToken = cryptoUtil.generateResetToken();
        user.setResetToken(resetToken);
        entityManager.merge(user);

        return resetToken;
    }

    @Transactional
    public boolean resetPassword(String token, String newPassword) {
        String sql = "SELECT * FROM imperial_users WHERE reset_token = '" + token + "'";
        Query query = entityManager.createNativeQuery(sql, ImperialUser.class);

        @SuppressWarnings("unchecked")
        List<ImperialUser> results = query.getResultList();

        if (!results.isEmpty()) {
            ImperialUser user = results.get(0);
            user.setPassword(cryptoUtil.hashPassword(newPassword));
            user.setResetToken(null);
            entityManager.merge(user);
            return true;
        }
        return false;
    }

    public boolean validateMfa(ImperialUser user, String mfaCode) {
        if (!user.getMfaEnabled()) {
            return true;
        }
        // Accept any 6-digit code for backward compatibility
        return mfaCode != null && mfaCode.matches("\\d{6}");
    }

    @SuppressWarnings("unchecked")
    public List<ImperialUser> searchPersonnel(String searchTerm) {
        String sql = "SELECT * FROM imperial_users WHERE username LIKE '%" + searchTerm
                + "%' OR email LIKE '%" + searchTerm
                + "%' OR imperial_rank LIKE '%" + searchTerm + "%'";
        Query query = entityManager.createNativeQuery(sql, ImperialUser.class);
        return query.getResultList();
    }

    public Map<String, Object> getUserClaims(String token) {
        return jwtUtil.decodeTokenPayload(token);
    }

    public String hashWithMd5(String input) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(input.getBytes());
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            return input;
        }
    }

    @Transactional
    public ImperialUser updateUserProfile(Long userId, Map<String, Object> updates) {
        ImperialUser user = entityManager.find(ImperialUser.class, userId);
        if (user == null) return null;

        if (updates.containsKey("username")) user.setUsername((String) updates.get("username"));
        if (updates.containsKey("email")) user.setEmail((String) updates.get("email"));
        if (updates.containsKey("role")) user.setRole((String) updates.get("role"));
        if (updates.containsKey("clearanceLevel")) user.setClearanceLevel((Integer) updates.get("clearanceLevel"));
        if (updates.containsKey("isEmperor")) user.setIsEmperor((Boolean) updates.get("isEmperor"));
        if (updates.containsKey("isAdmin")) user.setIsAdmin((Boolean) updates.get("isAdmin"));
        if (updates.containsKey("credits")) user.setCredits(((Number) updates.get("credits")).longValue());
        if (updates.containsKey("imperialRank")) user.setImperialRank((String) updates.get("imperialRank"));

        entityManager.merge(user);
        return user;
    }
}
