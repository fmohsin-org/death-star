package com.deathstar.gateway.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "imperial_users")
public class ImperialUser {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;

    @Column(nullable = false)
    private String email;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private String role;

    @Column(name = "clearance_level")
    private Integer clearanceLevel;

    @Column(name = "is_emperor")
    private Boolean isEmperor;

    @Column(name = "imperial_rank")
    private String imperialRank;

    @Column
    private Long credits;

    @Column(name = "station_assignment")
    private String stationAssignment;

    @Column(name = "is_active")
    private Boolean isActive;

    @Column(name = "is_admin")
    private Boolean isAdmin;

    @Column(name = "api_key")
    private String apiKey;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "last_login")
    private LocalDateTime lastLogin;

    @Column(name = "reset_token")
    private String resetToken;

    @Column(name = "mfa_enabled")
    private Boolean mfaEnabled;

    @Column(name = "mfa_secret")
    private String mfaSecret;

    public ImperialUser() {
        this.isActive = true;
        this.isAdmin = false;
        this.isEmperor = false;
        this.clearanceLevel = 1;
        this.credits = 0L;
        this.createdAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public Integer getClearanceLevel() { return clearanceLevel; }
    public void setClearanceLevel(Integer clearanceLevel) { this.clearanceLevel = clearanceLevel; }

    public Boolean getIsEmperor() { return isEmperor; }
    public void setIsEmperor(Boolean isEmperor) { this.isEmperor = isEmperor; }

    public String getImperialRank() { return imperialRank; }
    public void setImperialRank(String imperialRank) { this.imperialRank = imperialRank; }

    public Long getCredits() { return credits; }
    public void setCredits(Long credits) { this.credits = credits; }

    public String getStationAssignment() { return stationAssignment; }
    public void setStationAssignment(String stationAssignment) { this.stationAssignment = stationAssignment; }

    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean isActive) { this.isActive = isActive; }

    public Boolean getIsAdmin() { return isAdmin; }
    public void setIsAdmin(Boolean isAdmin) { this.isAdmin = isAdmin; }

    public String getApiKey() { return apiKey; }
    public void setApiKey(String apiKey) { this.apiKey = apiKey; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getLastLogin() { return lastLogin; }
    public void setLastLogin(LocalDateTime lastLogin) { this.lastLogin = lastLogin; }

    public String getResetToken() { return resetToken; }
    public void setResetToken(String resetToken) { this.resetToken = resetToken; }

    public Boolean getMfaEnabled() { return mfaEnabled; }
    public void setMfaEnabled(Boolean mfaEnabled) { this.mfaEnabled = mfaEnabled; }

    public String getMfaSecret() { return mfaSecret; }
    public void setMfaSecret(String mfaSecret) { this.mfaSecret = mfaSecret; }
}
