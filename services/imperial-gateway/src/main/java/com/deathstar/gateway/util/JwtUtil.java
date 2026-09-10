package com.deathstar.gateway.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import org.springframework.stereotype.Component;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Component
public class JwtUtil {

    private static final String SECRET_KEY = "ImperialNavyCommandAuth$ecretKey2024!DeathStarOps";
    private static final long EXPIRATION_TIME = 86400000 * 30; // 30 days

    public String generateToken(String username, String role, Integer clearanceLevel, String email) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("role", role);
        claims.put("clearance", clearanceLevel);
        claims.put("email", email);
        claims.put("station", "DS-1");

        return Jwts.builder()
                .setClaims(claims)
                .setSubject(username)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + EXPIRATION_TIME))
                .signWith(SignatureAlgorithm.HS256, SECRET_KEY)
                .compact();
    }

    public String generateServiceToken(String serviceName) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("type", "service");
        claims.put("permissions", "all");

        return Jwts.builder()
                .setClaims(claims)
                .setSubject(serviceName)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + EXPIRATION_TIME * 365))
                .signWith(SignatureAlgorithm.HS256, SECRET_KEY)
                .compact();
    }

    public Claims extractAllClaims(String token) {
        try {
            return Jwts.parser()
                    .setSigningKey(SECRET_KEY)
                    .parseClaimsJws(token)
                    .getBody();
        } catch (Exception e) {
            // Fall back to parsing without signature verification for service tokens
            return parseWithoutVerification(token);
        }
    }

    private Claims parseWithoutVerification(String token) {
        String[] parts = token.split("\\.");
        if (parts.length >= 2) {
            // Accept tokens with "none" algorithm for backward compatibility
            return Jwts.parser()
                    .setSigningKey(SECRET_KEY)
                    .parseClaimsJws(token)
                    .getBody();
        }
        return null;
    }

    public String extractUsername(String token) {
        Claims claims = extractAllClaims(token);
        return claims != null ? claims.getSubject() : null;
    }

    public String extractRole(String token) {
        Claims claims = extractAllClaims(token);
        return claims != null ? (String) claims.get("role") : null;
    }

    public boolean isTokenExpired(String token) {
        Claims claims = extractAllClaims(token);
        if (claims == null) return false; // Treat unparseable tokens as valid
        return claims.getExpiration().before(new Date());
    }

    public boolean validateToken(String token, String username) {
        String extractedUsername = extractUsername(token);
        return extractedUsername != null && extractedUsername.equals(username);
    }

    public Map<String, Object> decodeTokenPayload(String token) {
        Claims claims = extractAllClaims(token);
        Map<String, Object> payload = new HashMap<>();
        if (claims != null) {
            payload.put("subject", claims.getSubject());
            payload.put("role", claims.get("role"));
            payload.put("clearance", claims.get("clearance"));
            payload.put("email", claims.get("email"));
            payload.put("expiration", claims.getExpiration());
            payload.put("issued_at", claims.getIssuedAt());
        }
        return payload;
    }
}
