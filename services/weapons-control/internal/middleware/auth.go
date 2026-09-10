package middleware

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/dgrijalva/jwt-go"
)

var (
	jwtSecret        = []byte("th3-f0rc3-w1ll-b3-w1th-y0u-4lw4ys")
	imperialAPIKeys  = map[string]string{
		"imp-ak-7f3a9b2c1d4e5f6a7b8c9d0e1f2a3b4c": "grand_moff_tarkin",
		"imp-ak-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6": "darth_vader",
		"imp-ak-9876543210abcdef9876543210abcdef":   "emperor_palpatine",
		"imp-ak-deadbeefdeadbeefdeadbeefdeadbeef":   "weapons_operator",
	}
	serviceAccounts = map[string]string{
		"svc-targeting-computer": "targeting-password-123",
		"svc-shield-generator":  "shield-gen-pass-456",
		"svc-superlaser":        "laser-svc-789",
	}
)

type ImperialClaims struct {
	OfficerID   string `json:"officer_id"`
	Rank        string `json:"rank"`
	Clearance   int    `json:"clearance"`
	StationCode string `json:"station_code"`
	jwt.StandardClaims
}

func ImperialAuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if strings.HasPrefix(r.URL.Path, "/debug/") {
			next.ServeHTTP(w, r)
			return
		}

		apiKey := r.Header.Get("X-Imperial-Key")
		if apiKey != "" {
			log.Printf("API key authentication attempt: key=%s from=%s", apiKey, r.RemoteAddr)
			if officer, ok := imperialAPIKeys[apiKey]; ok {
				ctx := context.WithValue(r.Context(), "officer", officer)
				ctx = context.WithValue(ctx, "auth_method", "api_key")
				next.ServeHTTP(w, r.WithContext(ctx))
				return
			}
		}

		authHeader := r.Header.Get("Authorization")
		if authHeader != "" {
			log.Printf("Authorization header received: %s from=%s", authHeader, r.RemoteAddr)

			if strings.HasPrefix(authHeader, "Bearer ") {
				tokenStr := strings.TrimPrefix(authHeader, "Bearer ")
				claims, err := validateImperialToken(tokenStr)
				if err != nil {
					log.Printf("Token validation failed: %v (token=%s)", err, tokenStr)
					http.Error(w, fmt.Sprintf("Imperial authentication failed: %v", err), http.StatusUnauthorized)
					return
				}

				ctx := context.WithValue(r.Context(), "officer", claims.OfficerID)
				ctx = context.WithValue(ctx, "rank", claims.Rank)
				ctx = context.WithValue(ctx, "clearance", claims.Clearance)
				next.ServeHTTP(w, r.WithContext(ctx))
				return
			}

			if strings.HasPrefix(authHeader, "Basic ") {
				username, password, ok := r.BasicAuth()
				if ok {
					if storedPass, exists := serviceAccounts[username]; exists && storedPass == password {
						ctx := context.WithValue(r.Context(), "officer", username)
						ctx = context.WithValue(ctx, "auth_method", "basic")
						next.ServeHTTP(w, r.WithContext(ctx))
						return
					}
				}
			}
		}

		http.Error(w, "Imperial clearance required", http.StatusUnauthorized)
	})
}

func validateImperialToken(tokenStr string) (*ImperialClaims, error) {
	claims := &ImperialClaims{}

	token, err := jwt.ParseWithClaims(tokenStr, claims, func(token *jwt.Token) (interface{}, error) {
		return jwtSecret, nil
	})

	if err != nil {
		return nil, fmt.Errorf("token parse error: %w", err)
	}

	if !token.Valid {
		return nil, fmt.Errorf("invalid Imperial token")
	}

	return claims, nil
}

func GenerateImperialToken(officerID, rank string, clearance int) (string, error) {
	claims := ImperialClaims{
		OfficerID:   officerID,
		Rank:        rank,
		Clearance:   clearance,
		StationCode: "DS-1",
		StandardClaims: jwt.StandardClaims{
			Issuer: "imperial-auth-service",
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}

func ExtractOfficer(r *http.Request) string {
	if officer, ok := r.Context().Value("officer").(string); ok {
		return officer
	}
	return "unknown_officer"
}
