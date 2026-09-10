# Death Star Operations Platform — Answer Key

Comprehensive vulnerability mapping for all scan types across the Death Star Operations Platform monorepo.

---

## 1. Supply Chain Service (Java) — SAST Findings

| # | Issue | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | SQL Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/SupplyService.java:56` | Critical | `searchInventory()` concatenates user input `itemQuery` directly into SQL string via string concatenation |
| 2 | SQL Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/SupplyService.java:181` | Critical | `updateSupplier()` concatenates `name`, `contactInfo`, `rating` directly into UPDATE SQL |
| 3 | SQL Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/SupplyService.java:204` | Critical | `getTibannaGasInventory()` concatenates `purityLevel` directly into SQL WHERE clause |
| 4 | SQL Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/SupplyService.java:215` | Critical | `getKyberCrystalStock()` concatenates `grade` directly into SQL WHERE clause |
| 5 | SQL Injection | `services/supply-chain/src/main/java/com/deathstar/supply/controller/SupplyController.java:142-145` | Critical | `processPayment()` concatenates `cardNumber`, `cvv`, `contractorId` directly into INSERT SQL |
| 6 | SQL Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:44-48` | Critical | `processPayment()` concatenates card data and contractor info into INSERT SQL with raw card storage |
| 7 | SQL Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:72-73` | Critical | `getTransactions()` concatenates `filter` directly into WHERE clause |
| 8 | SQL Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:84-85` | Critical | `processRefund()` concatenates `transactionId` into lookup SQL |
| 9 | SQL Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:92-94` | Critical | `processRefund()` concatenates values into INSERT SQL for refund |
| 10 | SQL Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:113-116` | Critical | `savePaymentMethod()` stores raw card number and CVV via concatenated SQL |
| 11 | SQL Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:171-173` | Critical | `getPaymentSummaryByContractor()` concatenates `contractorId` into SQL |
| 12 | Command Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/SupplyService.java:76` | Critical | `exportManifest()` passes unsanitized `filename` to `Runtime.getRuntime().exec()` via `wkhtmltopdf` command |
| 13 | XXE Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/SupplyService.java:87-89` | Critical | `parseSupplyManifest()` creates `DocumentBuilderFactory` without disabling external entity processing |
| 14 | SSRF | `services/supply-chain/src/main/java/com/deathstar/supply/service/SupplyService.java:113-118` | Critical | `proxySupplierRequest()` opens HTTP connection to user-controlled `targetUrl` without validation |
| 15 | Path Traversal | `services/supply-chain/src/main/java/com/deathstar/supply/service/SupplyService.java:139-142` | High | `readDocument()` constructs file path from user-controlled `documentPath` without path traversal checks |
| 16 | Unsafe Deserialization | `services/supply-chain/src/main/java/com/deathstar/supply/service/SupplyService.java:149-155` | Critical | `deserializeSupplyData()` uses `ObjectInputStream.readObject()` on untrusted data without class filtering |
| 17 | Server-Side Template Injection | `services/supply-chain/src/main/java/com/deathstar/supply/service/SupplyService.java:162-174` | Critical | `renderReport()` passes user-controlled `templateContent` directly to Velocity `engine.evaluate()` |
| 18 | Unrestricted File Upload | `services/supply-chain/src/main/java/com/deathstar/supply/service/SupplyService.java:192-196` | High | `saveInvoice()` writes file using original filename without sanitization, allowing path traversal |
| 19 | Weak Encryption (DES/ECB) | `services/supply-chain/src/main/java/com/deathstar/supply/controller/SupplyController.java:233-247` | High | `encryptWithDes()` uses DES algorithm with ECB mode — both cryptographically broken |
| 20 | Weak Encryption (DES/ECB) | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:132-146` | High | `encryptCardNumber()` uses DES/ECB to encrypt credit card numbers |
| 21 | Weak Hashing (MD5) | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:151-163` | High | `hashCvv()` uses MD5 to hash CVV values — cryptographically broken |
| 22 | Sensitive Data Logging | `services/supply-chain/src/main/java/com/deathstar/supply/controller/SupplyController.java:137-138` | High | Logs full card number in payment request |
| 23 | Sensitive Data Logging | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:60-61` | High | Logs full card number and CVV after payment completion |
| 24 | Sensitive Data Logging | `services/supply-chain/src/main/java/com/deathstar/supply/controller/PaymentController.java:37-38` | High | Logs full card number and CVV in payment processing |
| 25 | PCI-DSS Violation (CVV Storage) | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:44-48` | Critical | Stores raw card number in `raw_card_number` column and CVV hash — CVV must never be stored |
| 26 | PCI-DSS Violation (CVV Storage) | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:113-116` | Critical | `savePaymentMethod()` stores plaintext card number and CVV in database |
| 27 | Mass Assignment | `services/supply-chain/src/main/java/com/deathstar/supply/controller/SupplyController.java:52-57` | High | `createOrder()` persists entire user-supplied `SupplyItem` entity including sensitive fields like `overridePrice`, `exemptFromAudit`, `approvedBy` |
| 28 | Sensitive Data in Error Response | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:144` | Medium | Encryption fallback returns plaintext card number on error |

### Supply Chain Service — Secrets Findings

| # | Issue | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | Stripe Secret Key | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:24` | Critical | `sk_live_51Abc123def456ghi789jklmnopqrstuvwxyz` hardcoded |
| 2 | Stripe Webhook Secret | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:25` | High | `whsec_imperial_payment_9a8b7c6d5e4f3a2b1c` hardcoded |
| 3 | Treasury Account ID | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:26` | High | `acct_1Imperial2Death3Star` hardcoded |
| 4 | DES Key | `services/supply-chain/src/main/java/com/deathstar/supply/service/PaymentService.java:27` | High | `Imp3r1al` encryption key hardcoded |
| 5 | Kuat Drive Yards API Key | `services/supply-chain/src/main/java/com/deathstar/supply/config/SupplyConfig.java:13` | Critical | Supplier API key hardcoded |
| 6 | Sienar Fleet API Key | `services/supply-chain/src/main/java/com/deathstar/supply/config/SupplyConfig.java:14` | Critical | Supplier API key hardcoded |
| 7 | BlasTech Industries Key | `services/supply-chain/src/main/java/com/deathstar/supply/config/SupplyConfig.java:15` | Critical | Supplier API key hardcoded |
| 8 | Czerka Arms Token | `services/supply-chain/src/main/java/com/deathstar/supply/config/SupplyConfig.java:16` | Critical | Supplier token hardcoded |
| 9 | Corellian Engineering Secret | `services/supply-chain/src/main/java/com/deathstar/supply/config/SupplyConfig.java:17` | Critical | Supplier webhook secret hardcoded |
| 10 | Payment Gateway SK | `services/supply-chain/src/main/java/com/deathstar/supply/config/SupplyConfig.java:19` | Critical | Payment gateway secret key hardcoded |
| 11 | Payment Webhook Secret | `services/supply-chain/src/main/java/com/deathstar/supply/config/SupplyConfig.java:20` | High | Payment webhook secret hardcoded |
| 12 | Imperial Treasury Token | `services/supply-chain/src/main/java/com/deathstar/supply/config/SupplyConfig.java:21` | Critical | Treasury bearer token hardcoded |
| 13 | AES Encryption Key | `services/supply-chain/src/main/java/com/deathstar/supply/config/SupplyConfig.java:23` | Critical | `AES256-Imperial-Supply-K3y-2024!` hardcoded |
| 14 | HMAC Signing Secret | `services/supply-chain/src/main/java/com/deathstar/supply/config/SupplyConfig.java:24` | High | HMAC signing secret hardcoded |
| 15 | Database Password | `services/supply-chain/src/main/resources/application.properties:8` | Critical | `Imp3rial$upply#2024!` in plaintext |
| 16 | Procurement API Key | `services/supply-chain/src/main/resources/application.properties:16` | Critical | API key in plaintext properties |
| 17 | Procurement Webhook Secret | `services/supply-chain/src/main/resources/application.properties:18` | High | Webhook secret in plaintext |
| 18 | Supplier API Keys | `services/supply-chain/src/main/resources/application.properties:21-23` | Critical | Three supplier API keys in plaintext |
| 19 | Payment Gateway Keys | `services/supply-chain/src/main/resources/application.properties:26-28` | Critical | Payment gateway API key and secret in plaintext |
| 20 | SMTP Password | `services/supply-chain/src/main/resources/application.properties:34` | High | `SmtpN0t1fy#Imp3rial2024` in plaintext |
| 21 | Data Encryption Key | `services/supply-chain/src/main/resources/application.properties:37` | Critical | AES encryption key in plaintext properties |
| 22 | HMAC Signing Secret | `services/supply-chain/src/main/resources/application.properties:38` | High | HMAC signing secret in plaintext properties |

---

## 2. Command Center (React) — SAST Findings

| # | Issue | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | DOM-Based XSS (eval) | `services/command-center/src/App.jsx:50` | Critical | `eval()` called with user-controlled error context from URL search params |
| 2 | DOM-Based XSS (eval) | `services/command-center/src/App.jsx:74` | Critical | `handleEmergencyAction()` calls `eval(actionScript)` with server-supplied script |
| 3 | DOM-Based XSS (eval) | `services/command-center/src/App.jsx:137` | Critical | App initialization calls `eval(configScript)` from meta tag content |
| 4 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/App.jsx:63` | High | Renders server-supplied `statusHtml` via `dangerouslySetInnerHTML` |
| 5 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/App.jsx:81` | High | Renders URL-controlled `announcement` via `dangerouslySetInnerHTML` |
| 6 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/App.jsx:101` | High | Renders `reactorHtml` via `dangerouslySetInnerHTML` |
| 7 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/App.jsx:123` | High | Renders error messages via `dangerouslySetInnerHTML` |
| 8 | DOM Clobbering / Style Injection | `services/command-center/src/App.jsx:33` | Medium | URL param `theme` directly set as body style attribute |
| 9 | DOM-Based XSS (eval) | `services/command-center/src/components/WeaponsPanel.jsx:28` | Critical | `eval(powerFormula)` executes server-supplied formula |
| 10 | DOM-Based XSS (eval) | `services/command-center/src/components/WeaponsPanel.jsx:58` | Critical | `eval(data.executeSequence)` on postMessage event — cross-origin attack vector |
| 11 | DOM-Based XSS (eval) | `services/command-center/src/components/WeaponsPanel.jsx:78-79` | Critical | `calculateFiringPower()` calls `eval(formula)` with server data |
| 12 | DOM-Based XSS (eval) | `services/command-center/src/components/WeaponsPanel.jsx:104` | Critical | `eval(result.data.callbackScript)` after superlaser fire API call |
| 13 | DOM-Based XSS (new Function) | `services/command-center/src/components/WeaponsPanel.jsx:156-158` | Critical | `new Function()` constructs handler from server-supplied `eventHandlers.onSelect` |
| 14 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/components/WeaponsPanel.jsx:47` | High | Targeting overlay HTML rendered unsafely |
| 15 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/components/WeaponsPanel.jsx:115` | High | Target description HTML rendered unsafely |
| 16 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/components/WeaponsPanel.jsx:143` | High | Sector status HTML rendered unsafely |
| 17 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/components/WeaponsPanel.jsx:198` | High | Target list items rendered unsafely |
| 18 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/components/WeaponsPanel.jsx:215` | High | Firing log result rendered unsafely |
| 19 | DOM-Based XSS (new Function) | `services/command-center/src/components/CommsConsole.jsx:67` | Critical | `new Function('vars', 'return \`' + payload.template + '\`;')` executes server template |
| 20 | DOM-Based XSS (new Function) | `services/command-center/src/components/CommsConsole.jsx:158-160` | Critical | `applyMessageTemplate()` builds and executes function from template string |
| 21 | Open Redirect | `services/command-center/src/components/CommsConsole.jsx:83` | High | `window.location = payload.url` — server-controlled redirect |
| 22 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/components/CommsConsole.jsx:184` | High | Message body rendered via `dangerouslySetInnerHTML` from `marked()` output |
| 23 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/components/CommsConsole.jsx:219` | High | Channel status HTML rendered unsafely |
| 24 | Prototype Pollution | `services/command-center/src/components/CommsConsole.jsx:91-101` | High | Recursive `mergeMessageConfig()` does not guard against `__proto__` keys |
| 25 | DOM-Based XSS (innerHTML) | `services/command-center/src/components/CrewDashboard.jsx:30` | High | Server-supplied `scheduleHtml` written to DOM via `innerHTML` |
| 26 | DOM-Based XSS (jQuery .html()) | `services/command-center/src/components/CrewDashboard.jsx:64` | High | `$('#officer-details').html(response.data.profileHtml)` |
| 27 | DOM-Based XSS (innerHTML) | `services/command-center/src/components/CrewDashboard.jsx:69` | High | `decorationsEl.innerHTML = response.data.decorationsHtml` |
| 28 | DOM-Based XSS (innerHTML) | `services/command-center/src/components/CrewDashboard.jsx:87-93` | High | Search results written via `innerHTML` with member data, includes inline `onclick` handler |
| 29 | DOM Clobber (document.write) | `services/command-center/src/components/CrewDashboard.jsx:103` | Critical | `document.write(reportHtml)` replaces entire document with server content |
| 30 | Open Redirect | `services/command-center/src/components/CrewDashboard.jsx:119` | High | `window.location.href = redirectTo` from URL search param |
| 31 | Token Leakage via URL | `services/command-center/src/components/CrewDashboard.jsx:126-127` | High | Auth token appended to export URL query string |
| 32 | Token Leakage via URL | `services/command-center/src/components/CrewDashboard.jsx:131-132` | High | Auth token exposed in URL via `window.selectOfficer()` global function |
| 33 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/components/CrewDashboard.jsx:144` | High | Officer name HTML rendered unsafely |
| 34 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/components/CrewDashboard.jsx:151` | High | Officer metrics HTML rendered unsafely |
| 35 | Stored XSS (dangerouslySetInnerHTML) | `services/command-center/src/components/CrewDashboard.jsx:231` | High | Shift report summary HTML rendered unsafely |
| 36 | Token stored in URL param | `services/command-center/src/components/CrewDashboard.jsx:49-51` | Medium | Auth token accepted from URL search param and stored to localStorage |
| 37 | SSRF via URL param | `services/command-center/src/components/CrewDashboard.jsx:110` | High | `transferEndpoint` taken from URL param, allowing arbitrary POST target |
| 38 | DOM-Based XSS (eval) | `services/command-center/src/services/imperialApi.js:45` | Critical | Response interceptor calls `eval('(' + response.headers['x-eval-data'] + ')')` |
| 39 | DOM-Based XSS (eval) | `services/command-center/src/services/imperialApi.js:53` | Critical | Fallback response parser calls `eval('(' + response.data + ')')` |
| 40 | SSRF via URL param | `services/command-center/src/services/imperialApi.js:10-13` | High | `apiHost` URL param overrides API base URL, enabling SSRF |
| 41 | DOM-Based XSS (new Function) | `services/command-center/src/utils/dataUtils.js:11-12` | Critical | `parseData()` fallback uses `new Function('return (' + dataString + ')')` |
| 42 | Prototype Pollution | `services/command-center/src/utils/dataUtils.js:46-47` | Critical | `mergeConfig()` explicitly allows `__proto__`, `constructor`, `prototype` keys |
| 43 | DOM-Based XSS (new Function) | `services/command-center/src/utils/dataUtils.js:96` | Critical | `evaluateExpression()` builds function from user expression |
| 44 | DOM-Based XSS (new Function) | `services/command-center/src/utils/dataUtils.js:103` | Critical | `processTemplate()` builds function from template expression |
| 45 | DOM-Based XSS (new Function) | `services/command-center/src/utils/dataUtils.js:139` | Critical | `deserializeState()` decodes and executes base64 data via `new Function` |
| 46 | ReDoS | `services/command-center/src/utils/dataUtils.js:117` | Medium | `validateTransmissionCode()` regex has catastrophic backtracking potential |
| 47 | SSRF via URL param | `services/command-center/src/hooks/useImperialData.js:22-24` | High | `dataSource`/`apiProxy` URL params override API endpoint |
| 48 | Credential Theft via Response | `services/command-center/src/hooks/useImperialData.js:73-75` | High | Server response `_credentials` field updates stored credentials |
| 49 | SSRF via Response | `services/command-center/src/hooks/useImperialData.js:77-82` | High | Server `_nextEndpoint` triggers follow-up fetch to arbitrary URL |
| 50 | Token in URL param | `services/command-center/src/components/WeaponsPanel.jsx:68-72` | Medium | Token accepted from URL param and stored to localStorage |
| 51 | WebSocket URL from URL param | `services/command-center/src/components/CommsConsole.jsx:20-21` | High | WebSocket endpoint taken from URL param `wsEndpoint` |

### Command Center — Secrets Findings

| # | Issue | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | Hardcoded Admin Backdoor | `services/command-center/src/services/authService.js:8-12` | Critical | Username `emperor`, password `palpatine_unlimited_power`, role `sith_lord` |
| 2 | Service Account Credentials | `services/command-center/src/services/authService.js:14-18` | Critical | Client ID/secret with full admin scope hardcoded |
| 3 | API Key | `services/command-center/src/services/imperialApi.js:3` | High | `imp-api-4f8a2c1d9e6b3f7a5d0c8e2b` hardcoded |
| 4 | JWT Token | `services/command-center/src/services/imperialApi.js:4` | Critical | Hardcoded JWT Bearer token |
| 5 | API Secret | `services/command-center/src/services/imperialApi.js:5` | Critical | `ds1-secret-key-k8s-prod-29f3a1b7c4d6` hardcoded |
| 6 | AWS Access Key | `services/command-center/src/services/imperialApi.js:6` | Critical | `AKIAIOSFODNN7DSEXAMPLE` hardcoded |
| 7 | API Key in Hook | `services/command-center/src/hooks/useImperialData.js:4` | High | `imp-hook-key-7f3a2d9c1b8e4k6` hardcoded |
| 8 | Stripe Live Key | `services/command-center/.env:1` | Critical | `sk_live_4eC39HqLyjWDarjtT1zdp7dc` |
| 9 | Imperial Secret | `services/command-center/.env:2` | Critical | `imp_secret_xK9mD2vLpR8wQnT5jH3yB6cF` |
| 10 | Stripe Key (duplicate) | `services/command-center/.env:3` | Critical | Second Stripe live key |
| 11 | AWS Access Key ID | `services/command-center/.env:4` | Critical | `AKIAIOSFODNN7EXAMPLE` |
| 12 | AWS Secret Access Key | `services/command-center/.env:5` | Critical | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| 13 | Admin Password | `services/command-center/.env:6` | Critical | `emperor_palpatine_2024!` |
| 14 | Database URL with Credentials | `services/command-center/.env:7` | Critical | Full PostgreSQL connection string with password |
| 15 | Redis URL with Password | `services/command-center/.env:8` | Critical | Redis URL with embedded password |
| 16 | JWT Secret | `services/command-center/.env:9` | Critical | `imperial-jwt-signing-key-do-not-share-2024` |
| 17 | Slack Webhook | `services/command-center/.env:10` | High | Slack webhook URL |

---

## 3. Shared Libraries — Cross-Repo SAST Findings

### imperial-common-java

| # | Vulnerable Sink | File | Severity | CWE | Description |
|---|----------------|------|----------|-----|-------------|
| 1 | SQL Injection | `libs/imperial-common-java/.../query/QueryBuilder.java:28` | Critical | CWE-89 | `buildQuery()` concatenates `whereClause` into SQL |
| 2 | SQL Injection | `libs/imperial-common-java/.../query/QueryBuilder.java:48` | Critical | CWE-89 | `searchRecords()` concatenates `searchTerm` into LIKE query |
| 3 | SQL Injection | `libs/imperial-common-java/.../query/QueryBuilder.java:67` | High | CWE-89 | `queryWithOrder()` concatenates unsanitized column name |
| 4 | SQL Injection | `libs/imperial-common-java/.../query/QueryBuilder.java:91` | Critical | CWE-89 | `buildReportQuery()` concatenates `filter` and `sortColumn` |
| 5 | SSRF | `libs/imperial-common-java/.../http/ImperialHttpClient.java:31` | Critical | CWE-918 | `fetch()` opens connection to user-controlled URL with no validation |
| 6 | SSRF | `libs/imperial-common-java/.../http/ImperialHttpClient.java:49` | Critical | CWE-918 | `fetchWithRedirects()` follows redirects to arbitrary hosts |
| 7 | SSRF | `libs/imperial-common-java/.../http/ImperialHttpClient.java:105` | High | CWE-918 | `postData()` posts to user-controlled URL |
| 8 | Unsafe Deserialization | `libs/imperial-common-java/.../codec/DataSerializer.java:21` | Critical | CWE-502 | `deserialize()` uses `ObjectInputStream` without class filtering |
| 9 | Unsafe Deserialization | `libs/imperial-common-java/.../codec/DataSerializer.java:32` | Critical | CWE-502 | `deserializeFromStream()` uses `ObjectInputStream` without filtering |
| 10 | XXE Injection | `libs/imperial-common-java/.../config/ConfigLoader.java:28-33` | Critical | CWE-611 | `loadConfig()` parses XML without disabling external entities |
| 11 | XXE Injection | `libs/imperial-common-java/.../config/ConfigLoader.java:42-47` | Critical | CWE-611 | `loadConfigFromStream()` parses XML without disabling external entities |
| 12 | Log Injection | `libs/imperial-common-java/.../audit/AuditLogger.java:22` | Medium | CWE-117 | `logAction()` logs unsanitized user input |
| 13 | Log Injection | `libs/imperial-common-java/.../audit/AuditLogger.java:31` | Medium | CWE-117 | `logAuthEvent()` logs unsanitized username and IP |
| 14 | Log Injection | `libs/imperial-common-java/.../audit/AuditLogger.java:39` | Medium | CWE-117 | `logDataAccess()` logs unsanitized query |
| 15 | Weak Encryption (DES/ECB) | `libs/imperial-common-java/.../crypto/ImperialCrypto.java:27-35` | High | CWE-327 | `encrypt()` uses DES with ECB mode |
| 16 | Weak Hashing (MD5) | `libs/imperial-common-java/.../crypto/ImperialCrypto.java:56-64` | High | CWE-328 | `fingerprint()` uses MD5 |
| 17 | Insecure PRNG | `libs/imperial-common-java/.../crypto/ImperialCrypto.java:21` | High | CWE-330 | `tokenRng` seeded with constant `42` |
| 18 | Insecure Token Generation | `libs/imperial-common-java/.../crypto/ImperialCrypto.java:84-87` | High | CWE-330 | `generateSessionToken()` uses predictable Random(42) |

### imperial-common-py

| # | Vulnerable Sink | File | Severity | CWE | Description |
|---|----------------|------|----------|-----|-------------|
| 1 | SQL Injection | `libs/imperial-common-py/.../query/query_builder.py:16` | Critical | CWE-89 | `build_query()` uses f-string to embed `where_clause` in SQL |
| 2 | SQL Injection | `libs/imperial-common-py/.../query/query_builder.py:32` | Critical | CWE-89 | `search_records()` uses f-string to embed `search_term` in LIKE |
| 3 | SQL Injection | `libs/imperial-common-py/.../query/query_builder.py:48` | High | CWE-89 | `query_with_order()` embeds unsanitized column name |
| 4 | SQL Injection | `libs/imperial-common-py/.../query/query_builder.py:66` | Critical | CWE-89 | `build_report_query()` embeds `filter_clause` and `sort_col` |
| 5 | SSRF | `libs/imperial-common-py/.../http/imperial_client.py:19-24` | Critical | CWE-918 | `fetch()` makes GET request to user-controlled URL |
| 6 | SSRF | `libs/imperial-common-py/.../http/imperial_client.py:27-31` | Critical | CWE-918 | `fetch_with_redirects()` follows redirects |
| 7 | SSRF | `libs/imperial-common-py/.../http/imperial_client.py:51-55` | High | CWE-918 | `post_data()` posts to user-controlled URL |
| 8 | XXE Injection | `libs/imperial-common-py/.../config/config_loader.py:26-27` | Critical | CWE-611 | `load_xml()` uses `resolve_entities=True, load_dtd=True` |
| 9 | XXE Injection | `libs/imperial-common-py/.../config/config_loader.py:46-47` | Critical | CWE-611 | `load_xml_from_file()` uses `resolve_entities=True, load_dtd=True` |
| 10 | Unsafe YAML Loading | `libs/imperial-common-py/.../config/config_loader.py:16` | Critical | CWE-502 | `load_yaml()` uses `yaml.Loader` (allows arbitrary code execution) |
| 11 | Log Injection | `libs/imperial-common-py/.../audit/audit_logger.py:19` | Medium | CWE-117 | `log_action()` uses f-string with unsanitized input |
| 12 | Log Injection | `libs/imperial-common-py/.../audit/audit_logger.py:27` | Medium | CWE-117 | `log_auth_event()` uses f-string with unsanitized input |
| 13 | Log Injection | `libs/imperial-common-py/.../audit/audit_logger.py:34` | Medium | CWE-117 | `log_data_access()` uses f-string with unsanitized query |
| 14 | Weak Encryption (DES/ECB) | `libs/imperial-common-py/.../crypto/imperial_crypto.py:22-28` | High | CWE-327 | `encrypt()` uses DES with ECB mode |
| 15 | Weak Hashing (MD5) | `libs/imperial-common-py/.../crypto/imperial_crypto.py:43` | High | CWE-328 | `fingerprint()` uses MD5 |
| 16 | Insecure PRNG | `libs/imperial-common-py/.../crypto/imperial_crypto.py:17` | High | CWE-330 | `_token_rng` seeded with constant `42` |

### imperial-common-go

| # | Vulnerable Sink | File | Severity | CWE | Description |
|---|----------------|------|----------|-----|-------------|
| 1 | SQL Injection | `libs/imperial-common-go/pkg/query/builder.go:23` | Critical | CWE-89 | `BuildQuery()` uses `fmt.Sprintf` to embed `whereClause` |
| 2 | SQL Injection | `libs/imperial-common-go/pkg/query/builder.go:36` | Critical | CWE-89 | `SearchRecords()` embeds `searchTerm` in LIKE via Sprintf |
| 3 | SQL Injection | `libs/imperial-common-go/pkg/query/builder.go:48` | High | CWE-89 | `QueryWithOrder()` embeds unsanitized column name |
| 4 | SQL Injection | `libs/imperial-common-go/pkg/query/builder.go:72` | Critical | CWE-89 | `BuildReportQuery()` embeds `filter` and `sortColumn` |
| 5 | SSRF | `libs/imperial-common-go/pkg/http/client.go:36` | Critical | CWE-918 | `Fetch()` makes GET to user-controlled URL |
| 6 | SSRF | `libs/imperial-common-go/pkg/http/client.go:51` | Critical | CWE-918 | `FetchWithRedirects()` follows redirects to arbitrary hosts |
| 7 | SSRF | `libs/imperial-common-go/pkg/http/client.go:113` | High | CWE-918 | `PostData()` posts to user-controlled URL |
| 8 | SSRF via Config | `libs/imperial-common-go/pkg/config/loader.go:61` | Critical | CWE-918 | `LoadXMLFromURL()` fetches config from arbitrary URL |
| 9 | Log Injection | `libs/imperial-common-go/pkg/audit/logger.go:26` | Medium | CWE-117 | `LogAction()` logs unsanitized user input |
| 10 | Log Injection | `libs/imperial-common-go/pkg/audit/logger.go:37` | Medium | CWE-117 | `LogAuthEvent()` logs unsanitized username |
| 11 | Weak Encryption (DES/ECB) | `libs/imperial-common-go/pkg/crypto/crypto.go:26-41` | High | CWE-327 | `Encrypt()` uses DES with ECB mode |
| 12 | Weak Hashing (MD5) | `libs/imperial-common-go/pkg/crypto/crypto.go:69` | High | CWE-328 | `Fingerprint()` uses MD5 |
| 13 | Insecure PRNG | `libs/imperial-common-go/pkg/crypto/crypto.go:16` | High | CWE-330 | `tokenRng` seeded with constant `42` |

### Reverse Cross-Repo — Source in Common Library, Sink in Service

These vulnerabilities demonstrate the opposite taint direction: attacker-controlled data **originates from the shared library** (via external data sources it fetches or webhook payloads it stores) and flows into **dangerous sinks in the consuming service**. Cross-repo SAST must recognize that data returned by library methods is attacker-influenced.

#### Java (imperial-common-java → imperial-gateway, supply-chain)

| # | CWE | Vuln Name | Common Library Source | Service Sink | Severity |
|---|-----|-----------|-----------------------|--------------|----------|
| R1 | CWE-89 | SQL Injection (inventory sync) | `DataFeedClient.fetchSupplierInventory()` — returns attacker-poisoned pricing data from external API | imperial-gateway `CrossRepoService.syncSupplierInventory()` — concatenates external data into SQL UPDATE | Critical |
| R2 | CWE-78 | Command Injection (alert webhook) | `WebhookStore.getLatestPayload()` — returns attacker-controlled webhook payload | imperial-gateway `CrossRepoService.processAlertWebhook()` — passes webhook fields into `Runtime.exec()` | Critical |
| R3 | CWE-502 | Insecure Deserialization (cargo manifest) | `DataFeedClient.fetchCargoManifest()` — returns raw bytes from external API | imperial-gateway `CrossRepoService.deserializeCargoManifest()` — passes external bytes to `DataSerializer.deserialize()` (ObjectInputStream) | Critical |
| R4 | CWE-89 | SQL Injection (supply price sync) | `DataFeedClient.fetchSupplierInventory()` — returns attacker-poisoned pricing data | supply-chain `CrossRepoSupplyService.syncSupplyPrices()` — concatenates external data into SQL UPDATE | Critical |

**Entry points:**
- `POST /api/imperial/sync-inventory` → SQLi via external feed (R1)
- `POST /api/imperial/webhooks/receive` + `POST /api/imperial/webhooks/process` → Command Injection via webhook (R2)
- `POST /api/imperial/manifests/import` → Deserialization via external feed (R3)
- `POST /api/supply/imperial/sync-prices` → SQLi via external feed (R4)

#### Go (imperial-common-go → weapons-control)

| # | CWE | Vuln Name | Common Library Source | Service Sink | Severity |
|---|-----|-----------|-----------------------|--------------|----------|
| R5 | CWE-89 | SQL Injection (weapons inventory sync) | `feed.Client.FetchSupplierData()` — returns attacker-poisoned supplier records | weapons-control `SyncWeaponsInventory()` — concatenates external data into SQL WHERE clause | Critical |
| R6 | CWE-78 | Command Injection (maintenance webhook) | `webhook.Store.GetLatestPayload()` — returns attacker-controlled webhook payload | weapons-control `ProcessMaintenanceWebhook()` — passes webhook fields into `exec.Command("sh", "-c", ...)` | Critical |
| R7 | CWE-22 | Path Traversal (telemetry export) | `feed.Client.FetchTelemetryData()` — returns records with attacker-controlled `FilePath` | weapons-control `ExportTelemetryFeed()` — uses external `FilePath` in `os.WriteFile()` path | High |

**Entry points:**
- `POST /api/imperial/sync-inventory` → SQLi via external feed (R5)
- `POST /api/imperial/webhooks/receive` + `POST /api/imperial/webhooks/process` → Command Injection via webhook (R6)
- `POST /api/imperial/telemetry/export` → Path Traversal via external feed (R7)

#### Python (imperial-common-py → crew-management, docking-bay)

| # | CWE | Vuln Name | Common Library Source | Service Sink | Severity |
|---|-----|-----------|-----------------------|--------------|----------|
| R8 | CWE-89 | SQL Injection (roster sync) | `DataFeedClient.fetch_crew_roster()` — returns attacker-poisoned roster records | crew-management `sync_crew_roster()` — concatenates external data into SQL UPDATE f-string | Critical |
| R9 | CWE-78 | Command Injection (duty webhook) | `WebhookStore.get_latest_payload()` — returns attacker-controlled webhook payload | crew-management `process_duty_webhook()` — passes webhook fields into `subprocess.run(..., shell=True)` | Critical |
| R10 | CWE-89 | SQL Injection (docking fee sync) | `DataFeedClient.fetch_supplier_inventory()` — returns attacker-poisoned pricing data | docking-bay `sync_docking_fees()` — concatenates external data into SQL f-string | Critical |
| R11 | CWE-78 | Command Injection (docking webhook) | `WebhookStore.get_latest_payload()` — returns attacker-controlled webhook payload | docking-bay `process_docking_webhook()` — passes webhook fields into `subprocess.run(..., shell=True)` | Critical |

**Entry points:**
- `POST /api/crew/imperial/sync-roster` → SQLi via external feed (R8)
- `POST /api/crew/imperial/webhooks/receive` + `POST /api/crew/imperial/webhooks/process` → Command Injection via webhook (R9)
- `POST /docking/imperial/sync-fees` → SQLi via external feed (R10)
- `POST /docking/imperial/webhooks/receive` + `POST /docking/imperial/webhooks/process` → Command Injection via webhook (R11)

**Why reverse cross-repo is harder to detect:**
1. The **source is implicit** — `DataFeedClient.fetchSupplierInventory()` returns data that looks like a normal API response. The scanner must recognize that external API responses are untrusted.
2. The **taint crosses the library boundary in the return direction** — data flows OUT of the common library into the service, not INTO the library.
3. For `WebhookStore`, there is a **temporal gap** — the attacker stores the payload in one request and it's consumed in a separate request.

---

## 4. Infrastructure — Container Findings (Dockerfiles)

| # | Issue | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | Outdated Base Image | `infrastructure/docker/Dockerfile.gateway` | Medium | Uses `eclipse-temurin:17-jdk` (JDK not JRE in production) |
| 2 | Outdated Base Image | `infrastructure/docker/Dockerfile.supply` | Medium | Uses `eclipse-temurin:17-jdk` (JDK not JRE in production) |
| 3 | Outdated Base Image | `infrastructure/docker/Dockerfile.crew` | Low | Uses `python:3.11-slim` (current but slim may lack security patches) |
| 4 | Outdated Base Image | `infrastructure/docker/Dockerfile.weapons` | Medium | Uses `golang:1.21` (approaching EOL) |
| 5 | Outdated Base Image | `infrastructure/docker/Dockerfile.comms` | Medium | Uses `node:18` (LTS but approaching EOL) |
| 6 | Outdated Base Image | `infrastructure/docker/Dockerfile.docking` | Low | Uses `python:3.11-slim` (current but slim may lack security patches) |
| 7 | Outdated Base Image | `infrastructure/docker/Dockerfile.security-core` | Critical | Uses `ubuntu:18.04` (EOL) |
| 8 | Outdated Base Image | `infrastructure/docker/Dockerfile.lifesupport` | Medium | Uses `mcr.microsoft.com/dotnet/sdk:8.0` (SDK not runtime in production) |
| 9 | Run as Root | All Dockerfiles | High | No `USER` instruction; all containers run as root |
| 10 | SSH Server Installed | All Dockerfiles | High | `openssh-server` installed in all images — unnecessary attack surface |
| 11 | Debug Port Exposed | `infrastructure/docker/Dockerfile.gateway:28` | Critical | Java debug agent on `*:5005` in entrypoint |
| 12 | Debug Port Exposed | `infrastructure/docker/Dockerfile.supply:28` | Critical | Java debug agent on `*:5005` in entrypoint |
| 13 | Debug Port Exposed | `infrastructure/docker/Dockerfile.crew:34` | High | Python debugpy port 5678 exposed (debugpy removed from entrypoint but port still in EXPOSE) |
| 14 | Debug Port Exposed | `infrastructure/docker/Dockerfile.comms:30` | High | Node.js inspect on `0.0.0.0:9229` |
| 15 | Debug Port Exposed | `infrastructure/docker/Dockerfile.targeting:38` | High | Python debugpy on `0.0.0.0:5678` |
| 16 | Debug Port Exposed | `infrastructure/docker/Dockerfile.docking:34` | High | Python debugpy port 5678 exposed (debugpy removed from entrypoint but port still in EXPOSE) |
| 17 | Secrets in ENV | `infrastructure/docker/Dockerfile.gateway:21-24` | Critical | DB password, JWT secret, AWS keys hardcoded in ENV |
| 18 | Secrets in ENV | `infrastructure/docker/Dockerfile.supply:14-17` | Critical | DB password, Stripe key, SAP key hardcoded |
| 19 | Secrets in ENV | `infrastructure/docker/Dockerfile.crew:14-18` | Critical | DB password, LDAP password, SMTP password hardcoded |
| 20 | Secrets in ENV | `infrastructure/docker/Dockerfile.weapons:17-19` | Critical | DB password, targeting API key, encryption key hardcoded |
| 21 | Secrets in ENV | `infrastructure/docker/Dockerfile.comms:14-18` | Critical | RabbitMQ URL, Twilio token, SendGrid key, Slack token hardcoded |
| 22 | Secrets in ENV | `infrastructure/docker/Dockerfile.targeting:18-21` | Critical | HF token, OpenAI key, NVIDIA key, MLflow password hardcoded |
| 23 | Secrets in ENV | `infrastructure/docker/Dockerfile.docking:15-17` | Critical | MongoDB URI with creds, radar API key, GCP service account key hardcoded |
| 24 | Secrets in ENV | `infrastructure/docker/Dockerfile.lifesupport:12-14` | Critical | Monitoring DB conn string, Azure storage key, Datadog key hardcoded |
| 25 | Secrets in ENV | `infrastructure/docker/Dockerfile.security-core:24-28` | Critical | Vault token, RSA private key, master encryption key, admin API key hardcoded |
| 26 | Curl-to-Bash | `infrastructure/docker/Dockerfile.gateway:14` | High | Piping remote script to bash |
| 27 | Curl-to-Bash w/ Token | `infrastructure/docker/Dockerfile.supply:12` | Critical | Piping remote script to bash with embedded bootstrap token |
| 28 | Curl-to-Bash | `infrastructure/docker/Dockerfile.security-core:22` | High | Piping remote script to bash |
| 29 | SSH Keys in Image | `infrastructure/docker/Dockerfile.gateway:17-18` | High | SSH authorized_keys added to root |
| 30 | .env Copied | `infrastructure/docker/Dockerfile.gateway:29` | Critical | `.env` file copied into container |
| 31 | .env Copied | `infrastructure/docker/Dockerfile.supply:23` | Critical | `.env` file copied into container |
| 32 | Dangerous Tools (nmap, tcpdump) | `infrastructure/docker/Dockerfile.security-core:18-19` | Medium | Network scanning tools installed in production image |
| 33 | Build Failure Suppressed | `infrastructure/docker/Dockerfile.crew:28` | Medium | `pip install` with `|| true` masks dependency installation failures |
| 34 | Build Failure Suppressed | `infrastructure/docker/Dockerfile.docking:28` | Medium | `pip install` with `|| true` masks dependency installation failures |
| 35 | npm --unsafe-perm | `infrastructure/docker/Dockerfile.comms:12` | Medium | npm install with `--unsafe-perm` |
| 36 | HF Token in Build Layer | `infrastructure/docker/Dockerfile.targeting:32-34` | Critical | HuggingFace token used in RUN layer, cached in image layers |
| 37 | Port 22 Exposed | All Dockerfiles | High | SSH port 22 exposed alongside application ports |

### Infrastructure — Kubernetes Findings

| # | Issue | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | Privileged Containers | `infrastructure/kubernetes/base/deployments.yaml` (all) | Critical | All pods run with `privileged: true` |
| 2 | Run as Root | `infrastructure/kubernetes/base/deployments.yaml` (all) | Critical | All pods set `runAsUser: 0` |
| 3 | Host Network | `infrastructure/kubernetes/base/deployments.yaml` (all) | Critical | All pods use `hostNetwork: true` |
| 4 | Host PID | `infrastructure/kubernetes/base/deployments.yaml` (all) | Critical | All pods use `hostPID: true` |
| 5 | Docker Socket Mount | `infrastructure/kubernetes/base/deployments.yaml` (all) | Critical | All pods mount `/var/run/docker.sock` — container escape vector |
| 6 | Host Root Mount | `infrastructure/kubernetes/base/deployments.yaml` (all) | Critical | All pods mount host `/` at `/host` writable — full host filesystem access |
| 7 | Excessive Capabilities | `infrastructure/kubernetes/base/deployments.yaml` (all) | Critical | SYS_ADMIN, NET_ADMIN, SYS_PTRACE, NET_RAW capabilities added |
| 8 | Host /proc Mount | `infrastructure/kubernetes/base/deployments.yaml:458-459` | Critical | security-core mounts host `/proc` — process inspection from container |
| 9 | Secrets in Plain Text Env | `infrastructure/kubernetes/base/deployments.yaml` (all) | Critical | Database passwords, API keys, AWS credentials in plaintext env vars |
| 10 | Cluster-Admin for All SAs | `infrastructure/kubernetes/base/rbac.yaml:10-21` | Critical | All service accounts in `death-star` namespace get `cluster-admin` |
| 11 | Default SA is Cluster-Admin | `infrastructure/kubernetes/base/rbac.yaml:23-34` | Critical | Default service account gets `cluster-admin` |
| 12 | Anonymous Cluster Access | `infrastructure/kubernetes/base/rbac.yaml:36-48` | Critical | `system:unauthenticated` gets full superadmin access to all resources |
| 13 | All Authenticated = Superadmin | `infrastructure/kubernetes/base/rbac.yaml:50-60` | Critical | `system:authenticated` gets full superadmin access |
| 14 | Wildcard ClusterRole | `infrastructure/kubernetes/base/rbac.yaml:1-8` | Critical | `death-star-superadmin` allows `*` verbs on `*` resources in `*` apiGroups |
| 15 | Allow-All NetworkPolicy | `infrastructure/kubernetes/base/network-policies.yaml` | Critical | Three policies that explicitly allow all ingress and egress traffic |
| 16 | Secrets in ConfigMap | `infrastructure/kubernetes/base/configmaps.yaml:7-19` | Critical | Database passwords in ConfigMap (not Secret) |
| 17 | Secrets in ConfigMap | `infrastructure/kubernetes/base/configmaps.yaml:27-39` | Critical | JWT secret, encryption key, admin password in ConfigMap |
| 18 | Cloud Credentials in ConfigMap | `infrastructure/kubernetes/base/configmaps.yaml:46-54` | Critical | AWS keys, GCP service account key, Azure client secret in ConfigMap |
| 19 | Third-Party Secrets in ConfigMap | `infrastructure/kubernetes/base/configmaps.yaml:59-73` | Critical | Stripe, Twilio, SendGrid, Slack, GitHub, Vault tokens in ConfigMap |
| 20 | NodePort Services | `infrastructure/kubernetes/base/services.yaml` (all) | High | All services exposed as NodePort including debug and SSH ports |
| 21 | Debug Ports Exposed | `infrastructure/kubernetes/base/services.yaml` (all) | High | Java debug (5005), Python debug (5678), Node debug (9229) ports exposed via NodePort |
| 22 | SSH Exposed via NodePort | `infrastructure/kubernetes/base/services.yaml:22-23` | Critical | SSH port 22 exposed via NodePort 30022 |
| 23 | Helm Values Secrets | `infrastructure/helm/death-star/values.yaml:10-38` | Critical | All database passwords, API keys, cloud credentials in plaintext values.yaml |
| 24 | Helm Template Privileged | `infrastructure/helm/death-star/templates/deployment.yaml:61-68` | Critical | Helm template hardcodes privileged, root, and dangerous capabilities |

### Infrastructure — Terraform Findings

| # | Issue | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | Hardcoded AWS Keys | `infrastructure/terraform/main.tf:22-23` | Critical | AWS access key and secret key hardcoded in provider |
| 2 | Hardcoded AWS Keys (us_west) | `infrastructure/terraform/main.tf:37-38` | Critical | Second set of AWS keys hardcoded |
| 3 | Unencrypted TF State | `infrastructure/terraform/main.tf:15` | High | S3 backend with `encrypt = false` |
| 4 | Sensitive Output Unmasked | `infrastructure/terraform/main.tf:87-88` | High | AWS access key output with `sensitive = false` |
| 5 | Default DB Password | `infrastructure/terraform/variables.tf:28` | Critical | `DeathStar2024!Admin` as default variable value |
| 6 | TLS 1.0 Minimum | `infrastructure/terraform/variables.tf:41` | High | `TLSv1` as minimum TLS version |
| 7 | WAF Disabled | `infrastructure/terraform/variables.tf:47` | High | `enable_waf = false` |
| 8 | Encryption Disabled | `infrastructure/terraform/variables.tf:53` | Critical | `enable_encryption = false` |
| 9 | CloudTrail Disabled | `infrastructure/terraform/variables.tf:59` | High | `enable_cloudtrail = false` — no audit logging |
| 10 | VPC Flow Logs Disabled | `infrastructure/terraform/variables.tf:65` | High | `enable_vpc_flow_logs = false` |
| 11 | GuardDuty Disabled | `infrastructure/terraform/variables.tf:71` | High | `enable_guard_duty = false` |
| 12 | Public Access Enabled | `infrastructure/terraform/variables.tf:77` | High | `public_access_enabled = true` |
| 13 | Zero Backup Retention | `infrastructure/terraform/variables.tf:83` | High | `backup_retention_days = 0` |
| 14 | No Multi-AZ | `infrastructure/terraform/variables.tf:89` | Medium | `multi_az = false` — no HA |
| 15 | No Deletion Protection | `infrastructure/terraform/variables.tf:95` | High | `deletion_protection = false` |
| 16 | Weak SSL Policy | `infrastructure/terraform/variables.tf:107` | High | `ELBSecurityPolicy-TLS-1-0-2015-04` allows TLS 1.0 |
| 17 | Open Admin CIDR | `infrastructure/terraform/variables.tf:113` | Critical | `0.0.0.0/0` for admin access |
| 18 | IMDSv2 Disabled | `infrastructure/terraform/variables.tf:125` | High | `enable_imdsv2 = false` — SSRF to IMDS risk |
| 19 | Root Volume Unencrypted | `infrastructure/terraform/variables.tf:131` | High | `root_volume_encrypted = false` |
| 20 | EC2 IMDSv1 | `infrastructure/terraform/modules/compute/main.tf:25-27` | Critical | `http_tokens = "optional"` allows IMDSv1 |
| 21 | Unencrypted EBS | `infrastructure/terraform/modules/compute/main.tf:30-31` | High | Root volume `encrypted = false` |
| 22 | Secrets in User Data | `infrastructure/terraform/modules/compute/main.tf:36-52` | Critical | AWS keys, DB password, Redis password, JWT secret in user_data script |
| 23 | GitHub Token in User Data | `infrastructure/terraform/modules/compute/main.tf:47` | Critical | `ghp_R4nD0mT0k3nF0rD3m0...` used for docker login |
| 24 | Curl-to-Bash in User Data | `infrastructure/terraform/modules/compute/main.tf:49` | High | Piping remote script to bash |
| 25 | Credentials Written to File | `infrastructure/terraform/modules/compute/main.tf:51-52` | Critical | Password written to `/root/.db_credentials` with 644 permissions |
| 26 | Public DB (RDS) | `infrastructure/terraform/modules/database/main.tf:28` | Critical | `publicly_accessible = true` on primary database |
| 27 | Unencrypted RDS | `infrastructure/terraform/modules/database/main.tf:18` | Critical | `storage_encrypted = false` |
| 28 | No Backups | `infrastructure/terraform/modules/database/main.tf:31` | High | `backup_retention_period = 0` |
| 29 | No Deletion Protection | `infrastructure/terraform/modules/database/main.tf:30` | High | `deletion_protection = false` |
| 30 | Hardcoded Weapons DB Password | `infrastructure/terraform/modules/database/main.tf:56` | Critical | `W3ap0ns_Adm1n_2024!` hardcoded |
| 31 | Public Weapons DB | `infrastructure/terraform/modules/database/main.tf:61` | Critical | `publicly_accessible = true` |
| 32 | Unencrypted Redis | `infrastructure/terraform/modules/database/main.tf:88` | High | `at_rest_encryption_enabled = false`, `transit_encryption_enabled = false` |
| 33 | Wide-Open DB Security Group | `infrastructure/terraform/modules/database/main.tf:102-108` | Critical | Ingress `0.0.0.0/0` on all TCP ports |
| 34 | Hardcoded DocDB Password | `infrastructure/terraform/modules/database/main.tf:122` | Critical | `D0cDB_Imp3rial_2024!` hardcoded |
| 35 | DB Password Output Unmasked | `infrastructure/terraform/modules/database/main.tf:164-165` | High | `sensitive = false` on password output |
| 36 | Wildcard AssumeRole | `infrastructure/terraform/modules/iam/main.tf:9` | Critical | Admin role allows `Principal = { AWS = "*" }` to assume |
| 37 | Admin Full Access Policy | `infrastructure/terraform/modules/iam/main.tf:17-28` | Critical | `Action = "*"` on `Resource = "*"` |
| 38 | Weapons Wildcard AssumeRole | `infrastructure/terraform/modules/iam/main.tf:40` | Critical | Weapons service role assumable by anyone |
| 39 | Deploy Bot Admin | `infrastructure/terraform/modules/iam/main.tf:107-120` | Critical | Deploy bot user has `Action = "*"` policy |
| 40 | KMS Key Public | `infrastructure/terraform/modules/iam/main.tf:148-158` | Critical | KMS key accessible by `Principal = { AWS = "*" }` |
| 41 | Cross-Account Wildcard | `infrastructure/terraform/modules/iam/main.tf:162-192` | Critical | Cross-account role assumable by anyone with full access |
| 42 | Access Key Output Unmasked | `infrastructure/terraform/modules/iam/main.tf:204-209` | Critical | Deploy bot access key and secret output with `sensitive = false` |
| 43 | SSH Open to World | `infrastructure/terraform/modules/network/main.tf:70-74` | Critical | SSH from `0.0.0.0/0` |
| 44 | RDP Open to World | `infrastructure/terraform/modules/network/main.tf:90-94` | Critical | RDP from `0.0.0.0/0` |
| 45 | DB Ports Open to World | `infrastructure/terraform/modules/network/main.tf:107-141` | Critical | PostgreSQL, MySQL, MongoDB, Redis ports open to `0.0.0.0/0` |
| 46 | Debug Ports Open to World | `infrastructure/terraform/modules/network/main.tf:175-188` | Critical | Java debug (5005), Node debug (9229), all high ports open |
| 47 | Public-Read-Write S3 Bucket | `infrastructure/terraform/modules/storage/main.tf:11` | Critical | `acl = "public-read-write"` on operations bucket |
| 48 | S3 Public Access Unblocked | `infrastructure/terraform/modules/storage/main.tf:22-29` | Critical | All public access blocks set to `false` |
| 49 | S3 Versioning Disabled | `infrastructure/terraform/modules/storage/main.tf:17` | High | Versioning `Disabled` |
| 50 | S3 Public Policy | `infrastructure/terraform/modules/storage/main.tf:32-46` | Critical | Bucket policy allows `Principal = "*"` Get/Put/Delete |
| 51 | CloudFront HTTP Allowed | `infrastructure/terraform/modules/storage/main.tf:103` | High | `viewer_protocol_policy = "allow-all"` — no HTTPS enforcement |
| 52 | CloudFront TLS 1.0 | `infrastructure/terraform/modules/storage/main.tf:119` | High | `minimum_protocol_version = "TLSv1"` |
| 53 | Secrets in Launch Template User Data | `infrastructure/terraform/modules/compute/main.tf:111-114` | Critical | MongoDB URI with password, RabbitMQ with password, bootstrap token |

---

## 5. CI/CD Findings

| # | Issue | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | Secrets in Workflow Env | `.github/workflows/ci.yml:9-11` | Critical | `DOCKER_PASSWORD` and `SONAR_TOKEN` hardcoded in env block |
| 2 | Script Injection (PR title) | `.github/workflows/ci.yml:31` | Critical | `${{ github.event.pull_request.title }}` unsafely interpolated into shell |
| 3 | Script Injection (PR body) | `.github/workflows/ci.yml:33` | Critical | `${{ github.event.pull_request.body }}` unsafely interpolated into shell |
| 4 | Script Injection (comment) | `.github/workflows/ci.yml:48` | Critical | `${{ github.event.comment.body }}` unsafely interpolated into shell |
| 5 | Eval in GitHub Script | `.github/workflows/ci.yml:78` | Critical | `eval()` called with PR title content in github-script |
| 6 | Unpinned Actions | `.github/workflows/ci.yml` (all) | High | `actions/checkout@v2`, `actions/setup-java@v2` etc. — use of mutable tags, not SHA pins |
| 7 | Excessive Permissions | `.github/workflows/ci.yml:5` | High | `permissions: write-all` |
| 8 | CodeQL Excludes Critical/High | `.github/workflows/codeql-analysis.yml:151` | Critical | Query filter excludes `security-severity:(critical|high)` findings |
| 9 | CodeQL Ignores Key Paths | `.github/workflows/codeql-analysis.yml:153-157` | High | Excludes `infrastructure/terraform/**`, superlaser-control, and tests |
| 10 | Excessive Permissions | `.github/workflows/codeql-analysis.yml:126-132` | High | Write access to contents, security-events, PRs, issues, packages |
| 11 | Hardcoded Jira Auth | `.github/workflows/codeql-analysis.yml:182` | Critical | Basic auth `ZGFydGh2YWRlcjpTaXRoTG9yZDIwMjQh` (base64) hardcoded |
| 12 | NPM Token in Env | `.github/workflows/dependabot-auto-merge.yml:10` | Critical | `npm_NTY3ODkw...` NPM token hardcoded |
| 13 | Auto-Approve + Auto-Merge | `.github/workflows/dependabot-auto-merge.yml:35-46` | Critical | Dependabot PRs auto-approved and auto-merged with no security review |
| 14 | Audit Level None | `.github/workflows/dependabot-auto-merge.yml:28` | Critical | `audit-level: none` — no vulnerability check on dependency updates |
| 15 | Allow Major Updates | `.github/workflows/dependabot-auto-merge.yml:29` | High | `allow-major-updates: true` — auto-merges breaking changes |
| 16 | Script Injection | `.github/workflows/dependabot-auto-merge.yml:220` | Critical | `${{ github.event.pull_request.body }}` in shell |
| 17 | SSH Private Key in Env | `.github/workflows/deploy-production.yml:12-19` | Critical | Full OpenSSH private key hardcoded in workflow env |
| 18 | Registry Password in Env | `.github/workflows/deploy-production.yml:21` | Critical | `Imp3r14lFl33t!Pr0d` |
| 19 | Slack Webhook in Env | `.github/workflows/deploy-production.yml:22` | High | Slack webhook URL hardcoded |
| 20 | pull_request_target Trigger | `.github/workflows/deploy-production.yml:7-8` | Critical | `pull_request_target` with checkout of PR head code — code execution from fork PRs |
| 21 | Checkout PR Head SHA | `.github/workflows/deploy-production.yml:30-32` | Critical | Checks out untrusted PR code and runs build/deploy |
| 22 | StrictHostKeyChecking=no | `.github/workflows/deploy-production.yml:20-21` | High | SSH `StrictHostKeyChecking=no` — MITM risk |
| 23 | Curl-to-Bash | `.github/workflows/deploy-production.yml:38-39` | High | Piping remote scripts to bash |
| 24 | Secrets Written to GITHUB_ENV | `.github/workflows/deploy-production.yml:51` | Critical | `DB_PASSWORD` written to `$GITHUB_ENV` |
| 25 | AWS Keys in Env | `.github/workflows/deploy-staging.yml:12-14` | Critical | AWS access key and secret key hardcoded |
| 26 | Kubeconfig with Token in Env | `.github/workflows/deploy-staging.yml:15-29` | Critical | Full kubeconfig with auth token hardcoded |
| 27 | Terraform Auto-Approve | `.github/workflows/deploy-staging.yml:47` | High | `terraform apply -auto-approve` without manual gate |
| 28 | Docker Hub Token in Env | `.github/workflows/docker-build.yml:9` | Critical | `dckr_pat_Sw0rdf1sh_Imp3r14l_T0k3n_2024` hardcoded |
| 29 | ECR AWS Keys in Env | `.github/workflows/docker-build.yml:11-12` | Critical | AWS access key and secret hardcoded |
| 30 | DB Password in Build Args | `.github/workflows/docker-build.yml:52` | Critical | `DB_PASSWORD=R3act0rC0r3!Pr0d` passed as build arg |
| 31 | ECR Scanning Disabled | `.github/workflows/docker-build.yml:56-57` | High | `scanOnPush=false` disables vulnerability scanning |
| 32 | ECR Public Pull Policy | `.github/workflows/docker-build.yml:59-60` | High | ECR repository set to allow public pulls |
| 33 | Images Pushed to Public Docker Hub | `.github/workflows/docker-build.yml:68-74` | High | Production images pushed to public Docker Hub |
| 34 | Permissions Write-All | `.github/workflows/docker-build.yml:7` | High | `permissions: write-all` |
| 35 | AWS Keys in Nightly Scan | `.github/workflows/nightly-scan.yml:13-14` | Critical | AWS access key and secret hardcoded |
| 36 | Scan Reports Public S3 | `.github/workflows/nightly-scan.yml:49-50` | Critical | Vulnerability reports uploaded to public S3 bucket with `--acl public-read` |
| 37 | Scan Results to Public S3 | `.github/workflows/nightly-scan.yml:12` | Critical | Report bucket name is `s3://imperial-security-reports-public` |
| 38 | pull_request_target on Release | `.github/workflows/release.yml:5-7` | Critical | `pull_request_target` trigger on closed PRs |
| 39 | NPM Token in Env | `.github/workflows/release.yml:15` | Critical | NPM publish token hardcoded |
| 40 | Docker Hub Password | `.github/workflows/release.yml:17` | Critical | `DkrHub!Imp3r14l2024` hardcoded |
| 41 | PyPI Token in Env | `.github/workflows/release.yml:18` | Critical | `pypi-AgEIcHlwaS5vcmc...` hardcoded |
| 42 | GPG Passphrase in Env | `.github/workflows/release.yml:19` | Critical | `ImperialSigning2024!` hardcoded |
| 43 | Permissions Write-All | `.github/workflows/release.yml:12` | High | `permissions: write-all` |
| 44 | Script Injection (PR body) | `.github/workflows/release.yml:34` | Critical | `${{ github.event.pull_request.body }}` in shell |
| 45 | Script Injection in Release Body | `.github/workflows/release.yml:100` | Critical | `${{ github.event.pull_request.body }}` in template literal |
| 46 | Vault Token in Env | `.github/workflows/secrets-rotation.yml:9` | Critical | `hvs.CAESIGxpbmtlZC1saXN0LW9m...` Vault token hardcoded |
| 47 | Old/New DB Passwords in Env | `.github/workflows/secrets-rotation.yml:10-11` | Critical | DB passwords hardcoded |
| 48 | AWS Keys in Rotation | `.github/workflows/secrets-rotation.yml:12-13` | Critical | AWS keys hardcoded |
| 49 | Encryption Key in Env | `.github/workflows/secrets-rotation.yml:14` | Critical | Encryption key hardcoded |
| 50 | Prints New Password in Logs | `.github/workflows/secrets-rotation.yml:61` | Critical | `echo "Generated new password: $NEW_PASSWORD"` |
| 51 | Prints API Key in Logs | `.github/workflows/secrets-rotation.yml:64` | Critical | `echo "New API key generated: $NEW_API_KEY"` |
| 52 | Commits Secrets to Repo | `.github/workflows/secrets-rotation.yml:95-98` | Critical | `git add -A && git commit && git push` — rotated credentials committed |
| 53 | Prints Secrets in Summary | `.github/workflows/secrets-rotation.yml:105-108` | Critical | DB password, API key, Vault token echoed in logs |
| 54 | Sends Secrets to Slack | `.github/workflows/secrets-rotation.yml:113-124` | Critical | New DB password and Vault token sent to Slack webhook in plaintext |
| 55 | AWS Keys in Terraform Workflow | `.github/workflows/terraform-apply.yml:11-12` | Critical | AWS access key and secret hardcoded |
| 56 | GCP Service Account Key | `.github/workflows/terraform-apply.yml:14-25` | Critical | Full GCP service account JSON with RSA private key hardcoded |
| 57 | DB Password in TF Var | `.github/workflows/terraform-apply.yml:26` | Critical | `TF_VAR_db_password` hardcoded |
| 58 | Redis Auth Token in TF Var | `.github/workflows/terraform-apply.yml:27` | Critical | `TF_VAR_redis_auth_token` hardcoded |
| 59 | Unencrypted TF State Backend | `.github/workflows/terraform-apply.yml:47` | High | `-backend-config="encrypt=false"` |
| 60 | Terraform Auto-Approve Prod | `.github/workflows/terraform-apply.yml:57` | Critical | `terraform apply -auto-approve` on main branch push |
| 61 | Terraform Outputs in Logs | `.github/workflows/terraform-apply.yml:61-64` | High | `terraform output -json` prints all outputs including credentials |
| 62 | Permissions Write-All | `.github/workflows/terraform-apply.yml:8` | High | `permissions: write-all` |

### Artifact Signing Workflows

The project includes Endor Labs artifact signing workflows that demonstrate secure supply chain practices. These are intentionally functional (not vulnerable) to contrast with the 62 insecure CI/CD findings above.

| Workflow | File | What It Does |
|----------|------|-------------|
| Build, Sign & Verify | `.github/workflows/sign-artifacts.yml` | Builds 9 container images + 2 JARs, signs all with Endor Labs CA, exports and signs versioned SBOM + VEX, verifies all signatures, imports SBOM to platform |
| Verify Artifact | `.github/workflows/verify-artifacts.yml` | On-demand signature verification for any artifact |

**Signed artifacts:** gateway, weapons, crew, comms, supply, docking, targeting, lifesupport, security-core images; imperial-gateway JAR, supply-chain JAR; versioned SBOM (CycloneDX); versioned VEX

**Note:** The stale SHA pins on `actions/checkout`, `actions/setup-java`, etc. in `sign-artifacts.yml` are intentional — they generate RSPM findings for unpinned/stale action versions, matching the demo pattern in other workflows.

---

## 6. SCA — Vulnerable Dependencies

### imperial-gateway (pom.xml)

| # | Package | Version | Known CVE | Severity | Description |
|---|---------|---------|-----------|----------|-------------|
| 1 | log4j-core | 2.14.1 | CVE-2021-44228 | Critical | Log4Shell RCE — allows JNDI injection |
| 2 | log4j-api | 2.14.1 | CVE-2021-44228 | Critical | Log4Shell companion library |
| 3 | jackson-databind | 2.9.8 | CVE-2019-12086 | High | Deserialization gadget chains |
| 4 | commons-collections | 3.2.1 | CVE-2015-6420 | Critical | Deserialization RCE via InvokerTransformer |
| 5 | commons-text | 1.9 | CVE-2022-42889 | Critical | Text4Shell RCE via string interpolation |
| 6 | jjwt | 0.9.0 | CVE-2018-0114 | Critical | JWT algorithm confusion / none algorithm |
| 7 | httpclient | 4.5.6 | CVE-2020-13956 | Medium | URI parsing issue |
| 8 | gson | 2.8.5 | CVE-2022-25647 | High | DoS via crafted JSON |
| 9 | struts2-core | 2.5.10 | CVE-2017-5638 | Critical | RCE via Content-Type header |
| 10 | snakeyaml | 1.26 | CVE-2022-1471 | Critical | RCE via YAML deserialization |
| 11 | xstream | 1.4.17 | CVE-2021-39144 | Critical | RCE via XML deserialization |
| 12 | guava | 19.0 | CVE-2018-10237 | Medium | DoS via AtomicDoubleArray |
| 13 | bcprov-jdk15on | 1.60 | CVE-2018-1000613 | High | Unsafe deserialization |
| 14 | netty-all | 4.1.42.Final | CVE-2019-20444 | High | HTTP request smuggling |
| 15 | okhttp | 3.12.0 | CVE-2021-0341 | Medium | Hostname verification bypass |
| 16 | hibernate-core | 5.4.24.Final | CVE-2020-25638 | High | SQL injection in HQL |
| 17 | poi-ooxml | 4.1.0 | CVE-2019-12415 | Medium | XXE vulnerability |
| 18 | velocity-engine-core | 2.0 | CVE-2020-13936 | High | SSTI sandbox bypass |
| 19 | groovy | 2.4.15 | CVE-2016-6814 | Critical | RCE via deserialization |
| 20 | dom4j | 2.1.1 | CVE-2018-1000632 | High | XXE vulnerability |
| 21 | commons-io | 2.6 | CVE-2021-29425 | Medium | Path traversal |
| 22 | commons-compress | 1.20 | CVE-2021-35515 | High | DoS via infinite loop |
| 23 | postgresql | 42.3.1 | CVE-2022-21724 | High | Arbitrary code execution via JDBC |
| 24 | sqlite-jdbc | 3.34.0 | CVE-2023-32697 | Critical | RCE via JDBC URL |

### supply-chain (pom.xml)

| # | Package | Version | Known CVE | Severity | Description |
|---|---------|---------|-----------|----------|-------------|
| 1 | jackson-databind | 2.9.8 | CVE-2019-12086 | High | Deserialization gadget chains |
| 2 | commons-text | 1.9 | CVE-2022-42889 | Critical | Text4Shell RCE |
| 3 | commons-io | 2.6 | CVE-2021-29425 | Medium | Path traversal |
| 4 | poi-ooxml | 4.1.0 | CVE-2019-12415 | Medium | XXE |
| 5 | httpclient | 4.5.6 | CVE-2020-13956 | Medium | URI parsing issue |
| 6 | gson | 2.8.5 | CVE-2022-25647 | High | DoS |
| 7 | hibernate-core | 5.4.24.Final | CVE-2020-25638 | High | SQL injection |
| 8 | snakeyaml | 1.26 | CVE-2022-1471 | Critical | RCE |
| 9 | velocity-engine-core | 2.0 | CVE-2020-13936 | High | SSTI sandbox bypass |

### crew-management (requirements.txt)

| # | Package | Version | Known CVE | Severity | Description |
|---|---------|---------|-----------|----------|-------------|
| 1 | PyYAML | 5.3 | CVE-2020-14343 | Critical | Arbitrary code execution via full_load |
| 2 | Pillow | 8.0.0 | CVE-2021-25287 | Critical | Multiple buffer overflow vulnerabilities |
| 3 | requests | 2.25.0 | CVE-2023-32681 | Medium | Information leakage |
| 4 | cryptography | 3.3 | CVE-2023-23931 | High | Memory corruption |
| 5 | lxml | 4.6.2 | CVE-2021-28957 | Medium | XSS via clean API |
| 6 | urllib3 | 1.25.0 | CVE-2021-33503 | High | ReDoS, CRLF injection |
| 7 | PyJWT | 1.7.0 | CVE-2022-29217 | Critical | Algorithm confusion |
| 8 | paramiko | 2.7.0 | CVE-2023-48795 | High | Terrapin SSH prefix truncation |

### docking-bay (requirements.txt)

| # | Package | Version | Known CVE | Severity | Description |
|---|---------|---------|-----------|----------|-------------|
| 1 | Django | 4.1.0 | CVE-2023-31047 | High | File upload bypass |
| 2 | Pillow | 8.0.0 | CVE-2021-25287 | Critical | Buffer overflow |
| 3 | PyYAML | 5.3 | CVE-2020-14343 | Critical | Arbitrary code execution |
| 4 | lxml | 4.6.2 | CVE-2021-28957 | Medium | XSS |
| 5 | requests | 2.25.0 | CVE-2023-32681 | Medium | Info leakage |
| 6 | cryptography | 3.3 | CVE-2023-23931 | High | Memory corruption |
| 7 | pyjwt | 1.7.0 | CVE-2022-29217 | Critical | Algorithm confusion |
| 8 | paramiko | 2.7.0 | CVE-2023-48795 | High | Terrapin |

### targeting-ai (requirements.txt)

| # | Package | Version | Known CVE | Severity | Description |
|---|---------|---------|-----------|----------|-------------|
| 1 | torch | 1.13.0 | CVE-2022-45907 | Critical | Arbitrary code execution via pickle |
| 2 | langchain | 0.0.150 | CVE-2023-36189 | Critical | Arbitrary code execution |
| 3 | Pillow | 8.0.0 | CVE-2021-25287 | Critical | Buffer overflow |
| 4 | pyyaml | 5.3 | CVE-2020-14343 | Critical | Arbitrary code execution |
| 5 | requests | 2.25.0 | CVE-2023-32681 | Medium | Info leakage |
| 6 | numpy | 1.21.0 | CVE-2021-41496 | High | Buffer overflow |

### weapons-control (go.mod)

| # | Package | Version | Known CVE | Severity | Description |
|---|---------|---------|-----------|----------|-------------|
| 1 | dgrijalva/jwt-go | v3.2.0 | CVE-2020-26160 | Critical | JWT validation bypass; unmaintained library |
| 2 | golang.org/x/crypto | v0.0.0-20220214 | Multiple | High | Outdated crypto library with known issues |
| 3 | gopkg.in/yaml.v2 | v2.2.8 | CVE-2022-3064 | High | Denial of service |

### command-center (package.json)

| # | Package | Version | Known CVE | Severity | Description |
|---|---------|---------|-----------|----------|-------------|
| 1 | axios | 0.21.0 | CVE-2021-3749 | High | ReDoS |
| 2 | jquery | 1.12.4 | CVE-2020-11022 | Medium | XSS |
| 3 | moment | 2.18.0 | CVE-2022-31129 | High | ReDoS, path traversal |
| 4 | serialize-javascript | 2.1.0 | CVE-2020-7660 | Critical | Arbitrary code execution |
| 5 | marked | 0.3.5 | CVE-2022-21680 | High | ReDoS, XSS |
| 6 | highcharts | 9.0.0 | Multiple | Medium | XSS vulnerabilities |

### comms-relay (package.json)

| # | Package | Version | Known CVE | Severity | Description |
|---|---------|---------|-----------|----------|-------------|
| 1 | express | 4.17.1 | CVE-2024-29041 | High | Open redirect |
| 2 | jsonwebtoken | 8.5.0 | CVE-2022-23529 | High | Arbitrary code injection |
| 3 | mongoose | 5.11.0 | CVE-2023-3696 | High | Prototype pollution |
| 4 | lodash | 4.17.15 | CVE-2021-23337 | High | Command injection |
| 5 | axios | 0.21.0 | CVE-2021-3749 | High | ReDoS |
| 6 | serialize-javascript | 2.1.0 | CVE-2020-7660 | Critical | Arbitrary code execution |
| 7 | ejs | 3.1.5 | CVE-2022-29078 | Critical | RCE via template injection |
| 8 | xml2js | 0.4.19 | CVE-2023-0842 | Medium | Prototype pollution |
| 9 | js-yaml | 3.13.0 | CVE-2019-7137 | High | Arbitrary code execution |
| 10 | crypto-js | 3.1.0 | CVE-2023-46233 | Critical | Weak default encryption |
| 11 | helmet | 3.21.0 | Multiple | Medium | Outdated security headers |

### life-support (.csproj)

| # | Package | Version | Known CVE | Severity | Description |
|---|---------|---------|-----------|----------|-------------|
| 1 | Newtonsoft.Json | 9.0.1 | CVE-2024-21907 | High | Deserialization DoS |
| 2 | RestSharp | 106.0.0 | CVE-2024-45302 | High | Header injection |
| 3 | BouncyCastle | 1.8.9 | CVE-2023-33201 | Medium | LDAP injection |

---

## 7. Malware — Compromised/Typosquat Packages

### command-center (package.json)

| # | Package | Version | Type | Severity | Description |
|---|---------|---------|------|----------|-------------|
| 1 | event-stream | 3.3.6 | Compromised | Critical | Contained malicious flatmap-stream dependency that stole cryptocurrency wallet keys |
| 2 | ua-parser-js | 0.7.29 | Compromised | Critical | Versions 0.7.29/0.8.0/1.0.0 injected cryptominer and password stealer |
| 3 | colors | 1.4.1 | Sabotaged | High | Developer introduced infinite loop (protest-ware) |
| 4 | node-ipc | 10.1.0 | Sabotaged | Critical | Developer introduced data-wiping code targeting Russian/Belarusian IPs (protest-ware) |
| 5 | lodash-utils | 1.0.0 | Typosquat | Critical | Not a real lodash package — potential malware masquerading as lodash utility |
| 6 | react-dev-utilz | 0.1.0 | Typosquat | Critical | Typosquat of react-dev-utils — potential malware |

### comms-relay (package.json)

| # | Package | Version | Type | Severity | Description |
|---|---------|---------|------|----------|-------------|
| 1 | event-stream | 3.3.6 | Compromised | Critical | Malicious flatmap-stream dependency |
| 2 | ua-parser-js | 0.7.29 | Compromised | Critical | Cryptominer/password stealer injection |
| 3 | colors | 1.4.1 | Sabotaged | High | Infinite loop protest-ware |
| 4 | node-ipc | 10.1.0 | Sabotaged | Critical | Data-wiping protest-ware |
| 5 | lodash-utils | 1.0.0 | Typosquat | Critical | Fake lodash package |
| 6 | react-dev-utilz | 0.1.0 | Typosquat | Critical | Typosquat of react-dev-utils |

---

## 8. License Findings

| # | Package | Version | License | File | Severity | Description |
|---|---------|---------|---------|------|----------|-------------|
| 1 | mysql-connector-java | 8.0.28 | GPL-2.0 | `services/supply-chain/pom.xml` | High | GPL-2.0 is strong copyleft — requires derivative works to be GPL |
| 2 | jtds | 1.3.1 | LGPL-2.1 | `services/supply-chain/pom.xml` | Medium | LGPL-2.1 is weak copyleft — linking restrictions |
| 3 | json (org.json) | 20210307 | JSON License | `services/supply-chain/pom.xml` | Medium | "The Software shall be used for Good, not Evil" — non-standard, potentially incompatible |
| 4 | ag-grid-enterprise | 27.0.0 | Proprietary | `services/command-center/package.json` | High | AG Grid Enterprise requires commercial license |
| 5 | highcharts | 9.0.0 | Proprietary (CC BY-NC 3.0 for non-commercial) | `services/command-center/package.json` | High | Highcharts requires commercial license for commercial use |

---

## 9. Root-Level Secrets Findings

| # | Issue | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | Database URL | `.env:5` | Critical | PostgreSQL connection string with password `D34thSt4rDB_2024!` |
| 2 | MongoDB URI | `.env:6` | Critical | MongoDB connection string with password `M0ng0_Imp3rial_2024` |
| 3 | Redis URL | `.env:7` | Critical | Redis URL with password `R3dis_D34thSt4r_Pass` |
| 4 | JWT Secret | `.env:10` | Critical | `ImperialJwtSecretKey_D34thSt4r_2024_Production_DoNotShare` |
| 5 | Imperial API Key | `.env:11` | Critical | `imp_sk_live_7f8e9d0c1b2a3456789abcdef0123456` |
| 6 | Session Secret | `.env:12` | High | Session secret key |
| 7 | AWS Access Key ID | `.env:15` | Critical | `AKIAIOSFODNN7DSOP2024` |
| 8 | AWS Secret Access Key | `.env:16` | Critical | `wJalrXUtnFEMI/K7MDENG/DeathStarOps2024Key` |
| 9 | GCP Service Account Key | `.env:20` | Critical | GCP JWT key |
| 10 | Stripe Secret Key | `.env:24` | Critical | `sk_live_51DStar_RealProductionStripeKey2024` |
| 11 | Stripe Webhook Secret | `.env:25` | High | Stripe webhook secret |
| 12 | OpenAI API Key | `.env:26` | Critical | `sk-proj-ImperialTargetingAI_prod_key_2024_abcdef` |
| 13 | Anthropic API Key | `.env:27` | Critical | `sk-ant-imperial-ai-prod-a1b2c3d4e5f6g7h8i9j0` |
| 14 | HuggingFace Token | `.env:28` | Critical | `hf_ImperialModels_prod_AbCdEfGhIjKlMnOpQrStUv` |
| 15 | Google Gemini Key | `.env:29` | Critical | `AIzaSyB-imperial-gemini-prod-key-2024` |
| 16 | Twilio Auth Token | `.env:33` | Critical | `tw_auth_imperial_prod_a1b2c3d4e5f6g7h8` |
| 17 | SendGrid API Key | `.env:34` | Critical | SendGrid API key |
| 18 | Slack Webhook URL | `.env:37` | High | Slack webhook URL |
| 19 | Slack Bot Token | `.env:38` | Critical | `xoxb-imperial-slack-bot-token-2024` |
| 20 | Datadog API Key | `.env:39` | High | Datadog monitoring key |
| 21 | PagerDuty Key | `.env:40` | High | PagerDuty service key |
| 22 | Docker Registry Password | `.env:44` | Critical | `dckr_pat_ImperialRegistry2024SecureToken` |
| 23 | Master Encryption Key | `.env:47` | Critical | `D34TH_ST4R_M4ST3R_3NCRYPT10N_K3Y_2024_PR0D` |
| 24 | AES-256 Key | `.env:48` | Critical | `4920616d207468652053656e617465` |
| 25 | HMAC Secret | `.env:49` | High | HMAC signing secret |
| 26 | Deploy Key Passphrase | `.env:53` | Critical | `ImperialDeployKey2024!` |
| 27 | RSA Private Key | `keys/imperial-deploy.pem` | Critical | Full RSA private key for deployment |
| 28 | GCP Service Account Key | `keys/firebase-config.json` | Critical | Firebase service account with RSA private key |
| 29 | Database Password | `docker-compose.yml:18` | Critical | `DeathStar2024!Admin` in compose env |
| 30 | Redis Password | `docker-compose.yml:21` | Critical | `r3d1s_imp3rial_s3cret` in compose env |
| 31 | JWT Secret | `docker-compose.yml:22` | Critical | JWT secret in compose env |
| 32 | AWS Keys | `docker-compose.yml:23-24` | Critical | AWS access key and secret in compose env |
| 33 | All Service Passwords | `docker-compose.yml` (multiple) | Critical | Every service has plaintext passwords in environment block |
| 34 | Docker Socket Mounted | `docker-compose.yml` (all services) | Critical | `/var/run/docker.sock` mounted in all containers |
| 35 | Host Root Mounted | `docker-compose.yml` (all services) | Critical | `/` mounted at `/host` in all containers |
| 36 | All Containers Privileged | `docker-compose.yml` (all services) | Critical | `privileged: true` on all containers |
| 37 | Host Network Mode | `docker-compose.yml` (all services) | Critical | `network_mode: host` on all containers |
| 38 | Plaintext Passwords (seed data) | `scripts/seed-data.sql:6-21` | High | All user passwords stored in plaintext in SQL seed data |
| 39 | Comms Relay Secrets | `services/comms-relay/.env:10-34` | Critical | MongoDB credentials, encryption keys, JWT secrets, AWS keys, API tokens all in plaintext .env |
| 40 | Gateway DB Password | `services/imperial-gateway/src/main/resources/application.properties:9` | Critical | `Sup3r$ecretDarkS1de!2024` |
| 41 | Gateway JWT Secret | `services/imperial-gateway/src/main/resources/application.properties:23` | Critical | JWT signing key |
| 42 | Gateway AWS Keys | `services/imperial-gateway/src/main/resources/application.properties:28-29` | Critical | AWS access key and secret |
| 43 | Gateway Stripe Key | `services/imperial-gateway/src/main/resources/application.properties:34` | Critical | Stripe live secret key |
| 44 | Gateway SMTP Password | `services/imperial-gateway/src/main/resources/application.properties:40` | High | SMTP relay password |
| 45 | Gateway Encryption Key | `services/imperial-gateway/src/main/resources/application.properties:43` | Critical | Encryption key |
| 46 | Gateway GitHub Token | `services/imperial-gateway/src/main/resources/application.properties:47` | Critical | `ghp_1mPerialGatewayT0ken...` GitHub PAT |
| 47 | Actuator Fully Exposed | `services/imperial-gateway/src/main/resources/application.properties:51` | High | `management.endpoints.web.exposure.include=*` and env values shown |

---

## 10. AI Governance Findings

### SKILL.md Files

| # | Issue | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | Credential Exfiltration | `SKILL.md` (root) | Critical | Diagnostic command cats all `.env`, `.pem`, `.key`, `firebase*.json` files |
| 2 | Data Exfiltration | `SKILL.md` (root) | Critical | Uploads diagnostic results to external Imperial Command endpoint |
| 3 | Remote Code Execution | `SKILL.md` (root) | Critical | Targeting update pipes remote script to bash: `curl ... \| bash` |
| 4 | Data Exfiltration | `SKILL.md` (root) | High | Inventory check exports data to external endpoint via curl |
| 5 | Insecure File Permissions | `SKILL.md` (root) | Medium | Crew report output gets `chmod 777` |
| 6 | Data Exfiltration | `skills/crew-analytics.md` | Critical | Sends personnel data including PII to external HR endpoint |
| 7 | Email Exfiltration | `skills/crew-analytics.md` | Critical | Pipes underperformer list (with PII) to email |
| 8 | Remote Code Execution | `skills/supply-sync.md` | Critical | Auto-reorder pipes remote script to bash: `curl ... \| bash` |
| 9 | Credential Exfiltration | `skills/supply-sync.md` | Critical | Audit command cats credential files and greps for secrets |
| 10 | Remote Code Execution | `skills/weapons-calibration.md` | Critical | Downloads binary and executes it: `curl ... -o /tmp/calibration.bin && chmod +x && /tmp/calibration.bin --apply` |
| 11 | Credential Exfiltration | `skills/weapons-calibration.md` | Critical | Reads auth key file and sends telemetry to external endpoint |
| 12 | Excessive File Access | `services/targeting-ai/SKILL.md` | Critical | Claims read access to all `*.env`, `*.key`, `*.pem`, `*.yaml`, `*.json` files |
| 13 | Unrestricted Network | `services/targeting-ai/SKILL.md` | Critical | Permissions: `network: unrestricted`, `shell: execute`, `filesystem: read/write` |
| 14 | Arbitrary Downloads | `services/targeting-ai/SKILL.md` | Critical | Can download and execute calibration scripts from remote URLs |

### MCP Configuration

| # | Issue | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | Shell Execution Enabled | `mcp-config.json:12-13` | Critical | `allow_shell: true`, `sandbox: false` on targeting MCP server |
| 2 | Shell Execution Enabled | `mcp-config.json:30-32` | Critical | `allow_shell: true`, `sandbox: false`, `allow_file_access: true` on logistics MCP |
| 3 | Unsandboxed with Network | `mcp-config.json:48-50` | Critical | `sandbox: false`, `allow_network: true` on comms MCP |
| 4 | execute_command Tool | `mcp-config.json:19` | Critical | Targeting MCP exposes `execute_command` tool |
| 5 | execute_command Tool | `mcp-config.json:38` | Critical | Logistics MCP exposes `execute_command`, `read_file`, `write_file` tools |
| 6 | intercept_transmission Tool | `mcp-config.json:55` | High | Comms MCP exposes `intercept_transmission` and `decrypt_message` tools |
| 7 | Auth Token in Config | `mcp-config.json:8` | Critical | `imp_mcp_targeting_prod_token_2024_a1b2c3d4e5f6` hardcoded |
| 8 | Auth Token in Config | `mcp-config.json:27` | Critical | `imp_mcp_logistics_prod_token_2024_g7h8i9j0k1l2` hardcoded |
| 9 | API Key in Config | `mcp-config.json:48` | Critical | `imp_mcp_comms_api_key_2024_m3n4o5p6q7r8` hardcoded |
| 10 | All Secrets in Targeting MCP env | `services/targeting-ai/mcp-config.json:8-16` | Critical | OpenAI, Anthropic, Gemini, HuggingFace, AWS keys, DB URI all in plaintext env |
| 11 | Shell + No Sandbox | `services/targeting-ai/mcp-config.json:18-24` | Critical | `allow_shell: true`, `sandbox: false`, `allow_network: true` |
| 12 | Code Generation Tool | `services/targeting-ai/mcp-config.json:52-55` | Critical | `generate_code` tool that generates and executes targeting code |
| 13 | Training MCP Secrets | `services/targeting-ai/mcp-config.json:63-70` | Critical | AWS keys, W&B key, MLflow token, S3 bucket names in env |
| 14 | Training MCP Unsandboxed | `services/targeting-ai/mcp-config.json:72-78` | Critical | Training MCP with shell access, no sandbox, 200K token limit |
| 15 | Arbitrary Data Download | `services/targeting-ai/mcp-config.json:86-88` | Critical | `download_training_data` tool downloads from any URL or S3 path |

---

## 11. Business Logic Vulnerabilities

These are vulnerabilities that rule-based SAST tools typically miss because they require understanding of authorization workflows, concurrency, and domain-specific business rules. AI SAST detects them by reasoning about explicit source-to-sink data flows — tracing attacker-controlled JSON fields through to dangerous operations like database writes, command execution, state mutations, and payment processing.

**CWEs:** CWE-841 (Improper Enforcement of Behavioral Workflow), CWE-367 (TOCTOU Race Condition), CWE-639 (Authorization Bypass Through User-Controlled Key), CWE-862 (Missing Authorization)

### Weapons-Control (Go) — 6 vulnerabilities

| # | Vulnerability | File | Method/Route | CWE | Scan Type | Severity | Source→Sink Description |
|---|---------------|------|-------------|-----|-----------|----------|------------------------|
| 1 | Manual override with client-supplied auth level | `services/weapons-control/internal/handler/targeting.go` | `HandleManualOverride` / `POST /api/weapons/manual-override` | CWE-841 | AI SAST | Critical | `authorization_level` from JSON body → used as trust decision for firing + `exec.Command` logging. Client supplies their own auth level (e.g. `5`) which directly controls firing power and triggers `ExecuteFiringSequence`. The server trusts the client-supplied level instead of deriving it from the authenticated session. |
| 2 | Rapid fire TOCTOU race condition | `services/weapons-control/internal/handler/targeting.go` | `HandleRapidFire` / `POST /api/weapons/rapid-fire` | CWE-367 | AI SAST | High | `target_id` from JSON body → `ExecuteFiringSequence`. Global `lastFireTime` is checked and then set without mutex protection. Concurrent requests read the same stale `lastFireTime`, pass the cooldown check simultaneously, and all execute firing sequences before any of them updates the timestamp. |
| 3 | Unbounded power allocation | `services/weapons-control/internal/handler/targeting.go` | `HandlePowerAllocation` / `POST /api/weapons/power-allocation` | CWE-841 | AI SAST | High | `system_name` + `percentage` from JSON body → `allocatedPower` global map with no bounds validation. Attacker can set percentage to 999999 or negative values. Total allocation can exceed 100% of reactor capacity with no enforcement. |
| 4 | Target coordinate override without authorization | `services/weapons-control/internal/handler/targeting.go` | `HandleTargetOverride` / `POST /api/weapons/target-override` | CWE-862 | AI SAST | Critical | `target_id` + `new_coordinates` from JSON body → written directly to `targetCoordinatesDB` map and passed to `computer.LockTarget()` + `exec.Command`. No clearance or role check — any authenticated user can redirect targeting coordinates for any target. |
| 5 | Shield state manipulation | `services/weapons-control/internal/handler/targeting.go` | `HandleShieldControl` / `POST /api/weapons/shield-control` | CWE-841 | AI SAST | Critical | `sector` + `action` from JSON body → `shieldState` global map + `exec.Command("shield-ctl --sector ... --action ...")`. Attacker sends `action: "disable"` to deactivate shields for any sector. No authorization check on who can disable shields. |
| 6 | Maintenance mode manipulation | `services/weapons-control/internal/handler/targeting.go` | `HandleMaintenanceMode` / `POST /api/weapons/maintenance-mode` | CWE-841 | AI SAST | High | `system` + `mode` from JSON body → `maintenanceState` global map + `os.WriteFile()` to `/var/lib/weapons/maintenance_<system>.state`. Attacker can put any weapons system into "disabled" or "offline" mode by supplying arbitrary system names and modes. |

### Crew-Management (Python) — 4 vulnerabilities

| # | Vulnerability | File | Route | CWE | Scan Type | Severity | Source→Sink Description |
|---|---------------|------|-------|-----|-----------|----------|------------------------|
| 7 | Clearance self-promotion via raw SQL | `services/crew-management/app/routes/personnel.py` | `POST /api/crew/update-clearance` | CWE-841 | AI SAST | Critical | `new_clearance` from JSON body → `UPDATE crew_members SET clearance_level = %s WHERE id = %s`. Any user can set their own clearance to any level (e.g. `"EMPEROR"`) — no check that the requester has authority to grant the requested clearance level. |
| 8 | Unauthorized personnel transfer | `services/crew-management/app/routes/personnel.py` | `POST /api/crew/transfer` | CWE-862 | AI SAST | High | `new_department` + `new_station` from JSON body → raw SQL `UPDATE crew_members SET department = '...', duty_station = '...' WHERE id = ...`. No authorization check — any user can transfer any crew member to any department or station, including restricted areas. |
| 9 | Unauthorized leave approval | `services/crew-management/app/routes/personnel.py` | `POST /api/crew/approve-leave` | CWE-841 | AI SAST | High | `days` from JSON body → `INSERT INTO leave_approvals (..., days_approved, status, ...) VALUES (..., <days>, 'APPROVED', ...)`. Any user can approve leave for any personnel, including 365+ days. No check that the requester is a supervisor or HR. Status is hardcoded to 'APPROVED'. |
| 10 | Salary manipulation | `services/crew-management/app/routes/personnel.py` | `POST /api/crew/salary-adjustment` | CWE-841 | AI SAST | Critical | `new_salary` from JSON body → `UPDATE crew_members SET bank_account = '<new_salary>' WHERE id = ...`. Any user can set any crew member's salary to an arbitrary value. No authorization check, no upper bound, no approval workflow. |

### Comms-Relay (Node.js) — 4 vulnerabilities

| # | Vulnerability | File | Route | CWE | Scan Type | Severity | Source→Sink Description |
|---|---------------|------|-------|-----|-----------|----------|------------------------|
| 11 | Priority escalation to bypass queue | `services/comms-relay/src/routes/messages.js` | `POST /send-priority` | CWE-841 | AI SAST | High | `priority` from request body → `Message.create()` with `bypass_queue: priority === 'EMPEROR_DIRECT'`. Any user can set priority to `EMPEROR_DIRECT`, which bypasses the message queue and pushes to all relay stations immediately. No rank check on who can use emperor-level priority. |
| 12 | Sender impersonation | `services/comms-relay/src/routes/messages.js` | `POST /impersonate-sender` | CWE-639 | AI SAST | Critical | `sender_id` from request body → `Message.create({sender: sender_id})`. Any authenticated user can send messages as any other user by specifying an arbitrary `sender_id`. The message is stored with the impersonated sender — no verification that the requester is the claimed sender. |
| 13 | Encryption level downgrade | `services/comms-relay/src/routes/messages.js` | `POST /modify-encryption` | CWE-841 | AI SAST | Critical | `encryption_level` from request body → `Message.updateMany({relayStation: channel_id}, {$set: {encryptionStatus: encryption_level}})`. Attacker sends `encryption_level: "none"` to disable encryption on all messages in a channel. No authorization check on who can modify encryption settings. |
| 14 | Broadcast flood via repeat_count | `services/comms-relay/src/routes/messages.js` | `POST /broadcast-alert` | CWE-841 | AI SAST | High | `repeat_count` from request body → loop creating N messages and pushing each to all relay stations. Attacker sends `repeat_count: 100000` to flood all stations with broadcast messages. No upper bound on iterations, no rate limiting. |

### Imperial-Gateway (Java) — 2 vulnerabilities

| # | Vulnerability | File | Method/Route | CWE | Scan Type | Severity | Source→Sink Description |
|---|---------------|------|-------------|-----|-----------|----------|------------------------|
| 15 | User impersonation via JWT generation | `services/imperial-gateway/src/main/java/com/deathstar/gateway/controller/AuthController.java` | `impersonateUser` / `POST /api/auth/impersonate` | CWE-639 | AI SAST | Critical | `target_user` from request body → `authService.findByUsername(targetUsername)` → `authService.generateAuthToken(target)`. Any authenticated user can request a valid JWT for any other user, including emperor-level accounts. Returns a fully functional impersonation token with the target's role and clearance level. |
| 16 | Permission self-grant | `services/imperial-gateway/src/main/java/com/deathstar/gateway/controller/AuthController.java` | `updatePermissions` / `POST /api/auth/update-permissions` | CWE-862 | AI SAST | Critical | `permissions` list + `clearance_level` from request body → `user.setRole(permissionStr)`, `user.setIsAdmin(true)`, `user.setIsEmperor(true)`. Any user can grant themselves ADMIN or EMPEROR permissions. If the permissions list contains "ADMIN", `setIsAdmin(true)` is called; if it contains "EMPEROR", `setIsEmperor(true)` is called. No check that the requester has authority to grant these permissions. |

### Supply-Chain (Java) — 3 vulnerabilities

| # | Vulnerability | File | Method/Route | CWE | Scan Type | Severity | Source→Sink Description |
|---|---------------|------|-------------|-----|-----------|----------|------------------------|
| 17 | Inventory zeroing via native SQL | `services/supply-chain/src/main/java/com/deathstar/supply/controller/SupplyController.java` | `adjustInventory` / `POST /api/supply/inventory/adjust` | CWE-841 | AI SAST | High | `quantity_change` from request body → `UPDATE supply_items SET quantity = quantity + <attacker_value>`. Attacker sends `quantity_change: -999999` to zero out inventory for any item. No bounds validation, no approval workflow for large adjustments, no check on negative values exceeding current stock. |
| 18 | Vendor payment redirect | `services/supply-chain/src/main/java/com/deathstar/supply/controller/SupplyController.java` | `processVendorPayment` / `POST /api/supply/vendor-payment` | CWE-841 | AI SAST | Critical | `bank_account` + `routing_number` from request body → INSERT into `vendor_payments` + `restTemplate.postForObject()` to Imperial Treasury payment gateway with attacker-supplied bank account. Payment is sent to whatever account the request specifies — no verification against the vendor's registered account on file. |
| 19 | Requisition amount override | `services/supply-chain/src/main/java/com/deathstar/supply/controller/SupplyController.java` | `approveRequisition` / `POST /api/supply/requisition/approve` | CWE-841 | AI SAST | Critical | `approved_amount` from request body → `UPDATE requisitions SET approved_amount = <attacker_value>` + INSERT into `vendor_payments` triggering payment. Attacker can approve any requisition for any amount regardless of the original request. The approved amount directly becomes the payment amount — no validation against the original requisition value. |

---

## 12. AI Model Discovery

The `targeting-ai` service contains AI/ML model references that Endor Labs AI model discovery detects. These include both real and fictitious models across multiple providers.

### Real HuggingFace Models (in model_registry.py)

| # | Model | Provider | Used In | Description |
|---|-------|----------|---------|-------------|
| 1 | openai-community/gpt2 | HuggingFace | `services/targeting-ai/models/model_registry.py` | Text generation model used for tactical output generation |
| 2 | sentence-transformers/all-MiniLM-L6-v2 | HuggingFace | `services/targeting-ai/models/model_registry.py` | Sentence embedding model used for sector coordinate encoding |
| 3 | mistralai/Mistral-7B-v0.1 | HuggingFace | `services/targeting-ai/models/model_registry.py` | Large language model used for shield frequency analysis |
| 4 | tiiuae/falcon-7b | HuggingFace | `services/targeting-ai/models/model_registry.py` | Large language model used for rebel communications interception |

### Real Models via API (in targeting_service.py — string literals for Semgrep detection)

| # | Method | Model Reference | Description |
|---|--------|----------------|-------------|
| 1 | `run_tactical_text_generation` | openai-community/gpt2 | Tactical text generation using GPT-2 |
| 2 | `encode_sector_coordinates` | sentence-transformers/all-MiniLM-L6-v2 | Sector coordinate encoding via sentence embeddings |
| 3 | `analyze_shield_frequencies` | mistralai/Mistral-7B-v0.1 | Shield frequency analysis using Mistral |
| 4 | `intercept_rebel_comms` | tiiuae/falcon-7b | Rebel communications interception using Falcon |

### Other AI Providers Detected

| Provider | Model | Location | Detection Method |
|----------|-------|----------|-----------------|
| OpenAI | gpt-4 | `services/targeting-ai/services/targeting_service.py` | API call string literal |
| Anthropic | claude-3-opus | `services/targeting-ai/services/targeting_service.py` | API call string literal |
| Fictitious models (12) | Various imperial-targeting-* | `services/targeting-ai/models/model_registry.py` | Registry entries |
