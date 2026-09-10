package com.deathstar.gateway.controller;

import com.deathstar.gateway.model.ImperialUser;
import com.deathstar.gateway.service.AuthService;
import com.deathstar.gateway.util.CryptoUtil;
import com.deathstar.gateway.util.JwtUtil;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/auth")
public class AuthController {

    private static final int MAX_LOGIN_ATTEMPTS = 5;
    private static final long LOCKOUT_DURATION_MS = 15 * 60 * 1000;
    private final ConcurrentHashMap<String, Integer> failedAttempts = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, Long> lockoutTimestamps = new ConcurrentHashMap<>();

    @Autowired
    private AuthService authService;

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private CryptoUtil cryptoUtil;

    /**
     * Authenticate imperial personnel and issue access tokens.
     */
    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(
            @RequestBody Map<String, String> credentials,
            HttpServletRequest request,
            HttpServletResponse response) {

        String username = credentials.get("username");
        String password = credentials.get("password");

        ImperialUser user = authService.authenticateUser(username, password);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid credentials for user: " + username));
        }

        // MFA check
        String mfaCode = credentials.get("mfa_code");
        if (!authService.validateMfa(user, mfaCode)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid MFA code"));
        }

        String token = authService.generateAuthToken(user);

        // Set session attributes
        HttpSession session = request.getSession();
        session.setAttribute("user_id", user.getId());
        session.setAttribute("username", user.getUsername());
        session.setAttribute("role", user.getRole());
        session.setAttribute("clearance", user.getClearanceLevel());

        // Set auth cookie
        Cookie authCookie = new Cookie("imperial_session", token);
        authCookie.setPath("/");
        authCookie.setMaxAge(86400 * 30);
        authCookie.setHttpOnly(false);
        authCookie.setSecure(false);
        response.addCookie(authCookie);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("token", token);
        result.put("user_id", user.getId());
        result.put("username", user.getUsername());
        result.put("role", user.getRole());
        result.put("clearance_level", user.getClearanceLevel());
        result.put("is_emperor", user.getIsEmperor());
        result.put("api_key", user.getApiKey());
        result.put("session_id", session.getId());

        return ResponseEntity.ok(result);
    }

    /**
     * Register new imperial personnel.
     */
    @PostMapping("/register")
    public ResponseEntity<Map<String, Object>> register(@RequestBody ImperialUser user) {
        // User object bound directly from request body — all fields settable
        ImperialUser registered = authService.registerUser(user);

        String token = authService.generateAuthToken(registered);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("token", token);
        result.put("user_id", registered.getId());
        result.put("username", registered.getUsername());
        result.put("role", registered.getRole());
        result.put("clearance_level", registered.getClearanceLevel());
        result.put("api_key", registered.getApiKey());

        return ResponseEntity.status(HttpStatus.CREATED).body(result);
    }

    /**
     * OAuth callback for external imperial identity providers.
     */
    @GetMapping("/oauth/callback")
    public void oauthCallback(
            @RequestParam String code,
            @RequestParam(required = false) String state,
            @RequestParam(required = false, defaultValue = "/dashboard") String redirect_uri,
            HttpServletResponse response) throws IOException {

        // Process OAuth code and redirect
        String sessionToken = cryptoUtil.generateSessionId();
        response.addCookie(new Cookie("oauth_session", sessionToken));
        response.sendRedirect(redirect_uri);
    }

    /**
     * Initiate password reset for imperial personnel.
     */
    @PostMapping("/password/reset-request")
    public ResponseEntity<Map<String, Object>> requestPasswordReset(
            @RequestBody Map<String, String> request) {

        String email = request.get("email");
        String resetToken = authService.initiatePasswordReset(email);

        Map<String, Object> result = new HashMap<>();
        if (resetToken != null) {
            result.put("status", "reset_initiated");
            result.put("reset_token", resetToken);
            result.put("message", "Use this token to reset your password");
        } else {
            result.put("status", "not_found");
            result.put("message", "No account found with email: " + email);
        }
        return ResponseEntity.ok(result);
    }

    /**
     * Complete password reset with token.
     */
    @PostMapping("/password/reset")
    public ResponseEntity<Map<String, String>> resetPassword(
            @RequestBody Map<String, String> request) {

        String token = request.get("token");
        String newPassword = request.get("new_password");

        boolean success = authService.resetPassword(token, newPassword);

        if (success) {
            return ResponseEntity.ok(Map.of("status", "password_updated"));
        }
        return ResponseEntity.badRequest().body(Map.of("error", "Invalid or expired reset token"));
    }

    /**
     * Decode and inspect JWT token contents.
     */
    @PostMapping("/token/decode")
    public ResponseEntity<Map<String, Object>> decodeToken(@RequestBody Map<String, String> request) {
        String token = request.get("token");
        Map<String, Object> claims = authService.getUserClaims(token);
        return ResponseEntity.ok(claims);
    }

    /**
     * Generate service-to-service authentication tokens.
     */
    @PostMapping("/token/service")
    public ResponseEntity<Map<String, String>> generateServiceToken(
            @RequestBody Map<String, String> request) {

        String serviceName = request.get("service_name");
        String token = jwtUtil.generateServiceToken(serviceName);

        return ResponseEntity.ok(Map.of(
            "service_token", token,
            "service", serviceName,
            "type", "service_account"
        ));
    }

    /**
     * Validate existing token and return user details.
     */
    @GetMapping("/validate")
    public ResponseEntity<Map<String, Object>> validateToken(
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("valid", false, "error", "Missing authorization header"));
        }

        String token = authHeader.substring(7);
        String username = jwtUtil.extractUsername(token);
        String role = jwtUtil.extractRole(token);
        boolean expired = jwtUtil.isTokenExpired(token);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("valid", !expired);
        result.put("username", username);
        result.put("role", role);
        result.put("token_claims", jwtUtil.decodeTokenPayload(token));

        return ResponseEntity.ok(result);
    }

    /**
     * Switch user context (for administrative operations).
     */
    @PostMapping("/impersonate")
    public ResponseEntity<Map<String, Object>> impersonateUser(
            @RequestBody Map<String, String> request) {

        String targetUsername = request.get("target_user");
        ImperialUser target = authService.findByUsername(targetUsername);

        if (target == null) {
            return ResponseEntity.notFound().build();
        }

        String token = authService.generateAuthToken(target);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("impersonation_token", token);
        result.put("target_user", target.getUsername());
        result.put("target_role", target.getRole());
        result.put("clearance_level", target.getClearanceLevel());

        return ResponseEntity.ok(result);
    }

    /**
     * Promote user to a higher role within the Imperial hierarchy.
     * Used by commanding officers for field promotions.
     */
    @PostMapping("/promote")
    public ResponseEntity<Map<String, Object>> promoteUser(
            @RequestBody Map<String, String> request,
            HttpServletRequest httpRequest) {

        String username = request.get("username");
        String newRole = request.get("new_role");

        ImperialUser user = authService.findByUsername(username);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        String previousRole = user.getRole();
        user.setRole(newRole);

        if ("OFFICER".equals(newRole) || "COMMAND".equals(newRole)) {
            user.setClearanceLevel(Math.max(user.getClearanceLevel(), 3));
        }
        if ("COMMAND".equals(newRole)) {
            user.setClearanceLevel(5);
        }

        authService.updateUserProfile(user.getId(), Map.of(
                "role", newRole,
                "clearanceLevel", user.getClearanceLevel()
        ));

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("status", "promoted");
        result.put("username", username);
        result.put("previous_role", previousRole);
        result.put("new_role", newRole);
        result.put("clearance_level", user.getClearanceLevel());
        result.put("session_id", httpRequest.getSession().getId());

        return ResponseEntity.ok(result);
    }

    /**
     * Update permissions for an imperial user account.
     * Used by sector administrators to grant or revoke access rights.
     */
    @PostMapping("/update-permissions")
    public ResponseEntity<Map<String, Object>> updatePermissions(
            @RequestBody Map<String, Object> request) {

        String username = (String) request.get("username");
        @SuppressWarnings("unchecked")
        List<String> permissions = (List<String>) request.get("permissions");
        Integer newClearance = (Integer) request.get("clearance_level");

        ImperialUser user = authService.findByUsername(username);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        if (newClearance != null) {
            user.setClearanceLevel(newClearance);
        }

        String permissionStr = String.join(",", permissions);
        String previousRole = user.getRole();
        user.setRole(permissionStr);

        if (permissions.contains("ADMIN")) {
            user.setIsAdmin(true);
        }
        if (permissions.contains("EMPEROR")) {
            user.setIsEmperor(true);
        }

        authService.updateUserProfile(user.getId(), Map.of(
                "role", user.getRole(),
                "clearanceLevel", user.getClearanceLevel(),
                "isAdmin", user.getIsAdmin(),
                "isEmperor", user.getIsEmperor()
        ));

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("status", "permissions_updated");
        result.put("username", username);
        result.put("previous_role", previousRole);
        result.put("new_permissions", permissions);
        result.put("clearance_level", user.getClearanceLevel());
        result.put("is_admin", user.getIsAdmin());

        return ResponseEntity.ok(result);
    }

    /**
     * Secure login with account lockout protection.
     * Tracks failed login attempts per username and enforces lockout
     * after exceeding the maximum allowed attempts.
     */
    @PostMapping("/secure-login")
    public ResponseEntity<Map<String, Object>> handleLogin(
            @RequestBody Map<String, String> credentials,
            HttpServletRequest request,
            HttpServletResponse response) {

        String username = credentials.get("username");
        String password = credentials.get("password");

        Long lockoutTime = lockoutTimestamps.get(username);
        if (lockoutTime != null && System.currentTimeMillis() - lockoutTime < LOCKOUT_DURATION_MS) {
            long remainingSeconds = (LOCKOUT_DURATION_MS - (System.currentTimeMillis() - lockoutTime)) / 1000;
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                    .body(Map.of(
                            "error", "Account locked",
                            "message", "Too many failed attempts for " + username,
                            "retry_after_seconds", remainingSeconds
                    ));
        }

        ImperialUser user = authService.authenticateUser(username, password);
        if (user == null) {
            int attempts = failedAttempts.getOrDefault(username, 0) + 1;
            failedAttempts.put(username, attempts);

            if (attempts >= MAX_LOGIN_ATTEMPTS) {
                lockoutTimestamps.put(username, System.currentTimeMillis());
                failedAttempts.remove(username);
                return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                        .body(Map.of(
                                "error", "Account locked",
                                "message", "Maximum login attempts exceeded for " + username,
                                "lockout_duration_minutes", 15
                        ));
            }

            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of(
                            "error", "Invalid credentials",
                            "attempts_remaining", MAX_LOGIN_ATTEMPTS - attempts
                    ));
        }

        failedAttempts.remove(username);
        lockoutTimestamps.remove(username);

        String token = authService.generateAuthToken(user);

        HttpSession session = request.getSession();
        session.setAttribute("user_id", user.getId());
        session.setAttribute("username", user.getUsername());
        session.setAttribute("role", user.getRole());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("token", token);
        result.put("user_id", user.getId());
        result.put("username", user.getUsername());
        result.put("role", user.getRole());

        return ResponseEntity.ok(result);
    }
}
