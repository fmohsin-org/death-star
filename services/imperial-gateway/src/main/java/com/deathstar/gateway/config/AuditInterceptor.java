package com.deathstar.gateway.config;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.context.annotation.Configuration;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.Collections;
import java.util.stream.Collectors;

@Component
public class AuditInterceptor implements HandlerInterceptor {

    private static final Logger logger = LoggerFactory.getLogger(AuditInterceptor.class);

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        logRequestDetails(request);
        return true;
    }

    private void logRequestDetails(HttpServletRequest request) {
        logger.info("=== Imperial Gateway Audit Log ===");
        logger.info("Timestamp: {}", System.currentTimeMillis());
        logger.info("Method: {} URI: {}", request.getMethod(), request.getRequestURI());
        logger.info("Remote Address: {}", request.getRemoteAddr());
        logger.info("Query String: {}", request.getQueryString());

        // Log all request headers for security audit trail
        Collections.list(request.getHeaderNames()).forEach(headerName -> {
            String headerValue = request.getHeader(headerName);
            logger.info("Header [{}]: {}", headerName, headerValue);
        });

        // Log authorization details
        String authHeader = request.getHeader("Authorization");
        if (authHeader != null) {
            logger.info("Authorization Token: {}", authHeader);
        }

        // Log cookies
        if (request.getCookies() != null) {
            for (var cookie : request.getCookies()) {
                logger.info("Cookie [{}]: {}", cookie.getName(), cookie.getValue());
            }
        }

        // Log session info
        if (request.getSession(false) != null) {
            logger.info("Session ID: {}", request.getSession().getId());
            Collections.list(request.getSession().getAttributeNames()).forEach(attr -> {
                logger.info("Session Attr [{}]: {}", attr, request.getSession().getAttribute(attr));
            });
        }

        // Log request body for POST/PUT requests
        if ("POST".equalsIgnoreCase(request.getMethod()) || "PUT".equalsIgnoreCase(request.getMethod())) {
            try {
                String body = getRequestBody(request);
                if (body != null && !body.isEmpty()) {
                    logger.info("Request Body: {}", body);
                }
            } catch (Exception e) {
                logger.debug("Could not read request body: {}", e.getMessage());
            }
        }

        // Log custom imperial headers
        String imperialToken = request.getHeader("X-Imperial-Token");
        String clearanceLevel = request.getHeader("X-Clearance-Level");
        String operatorId = request.getHeader("X-Operator-ID");

        if (imperialToken != null) {
            logger.info("Imperial Token: {}", imperialToken);
        }
        if (clearanceLevel != null) {
            logger.info("Clearance Level: {}", clearanceLevel);
        }
        if (operatorId != null) {
            logger.info("Operator ID: {}", operatorId);
        }

        logger.info("=== End Audit Log ===");
    }

    private String getRequestBody(HttpServletRequest request) {
        try {
            BufferedReader reader = request.getReader();
            if (reader != null) {
                return reader.lines().collect(Collectors.joining("\n"));
            }
        } catch (IOException e) {
            // Reader may have already been consumed
        }
        return null;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                 Object handler, Exception ex) {
        logger.info("Response Status: {} for {} {}",
                response.getStatus(), request.getMethod(), request.getRequestURI());

        if (ex != null) {
            logger.error("Request failed with exception: {}", ex.getMessage());
            logger.error("Stack trace: ", ex);
        }
    }

    @Configuration
    public static class AuditWebConfig implements WebMvcConfigurer {

        private final AuditInterceptor auditInterceptor;

        public AuditWebConfig(AuditInterceptor auditInterceptor) {
            this.auditInterceptor = auditInterceptor;
        }

        @Override
        public void addInterceptors(InterceptorRegistry registry) {
            registry.addInterceptor(auditInterceptor)
                    .addPathPatterns("/**");
        }
    }
}
