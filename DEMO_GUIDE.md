# Death Star Operations Platform — Demo & Walkthrough Guide

**Classification:** INTERNAL USE ONLY — Endor Labs SA Demo Resource

This guide walks through the Death Star Operations Platform monorepo for customer demos showcasing Endor Labs' scanning capabilities across multiple languages, frameworks, and infrastructure technologies. The repo is designed to demonstrate enterprise-scale findings across all scan modules simultaneously.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Scan Module Walkthroughs](#scan-module-walkthroughs)
   - [SCA — Vulnerable Dependencies](#sca--vulnerable-dependencies)
   - [AI SAST — Code Vulnerabilities](#ai-sast--code-vulnerabilities)
   - [Cross-Repo SAST — Shared Library Taint Flows](#cross-repo-sast--shared-library-taint-flows)
   - [Secrets Detection](#secrets-detection)
   - [Container Scanning](#container-scanning)
   - [CI/CD Security](#cicd-security)
   - [Artifact Signing & Supply Chain Integrity](#artifact-signing--supply-chain-integrity)
   - [Malware Detection](#malware-detection)
   - [AI Governance](#ai-governance)
   - [Business Logic Detection (AI SAST)](#business-logic-detection-ai-sast)
   - [AI Model Governance & Discovery](#ai-model-governance--discovery)
   - [License Compliance](#license-compliance)
3. [AI Security Code Review (PR Buddy)](#ai-security-code-review-pr-buddy)
4. [Service-by-Service Highlights](#service-by-service-highlights)
5. [Demo Flow Cheat Sheet](#demo-flow-cheat-sheet)

---

## Getting Started

### Prerequisites

- Java 17+, Maven 3.8+
- Go 1.21+
- Python 3.11+, pip
- Node.js 20+, npm
- .NET 8 SDK
- GCC/G++ for security-core
- Docker & Docker Compose (optional, for containerized demo)

### Start the Frontend UI

```bash
cd frontend
npm install   # first time only
npm run dev
```

Open **http://localhost:5173** — this is the Death Star Operations Dashboard showing all services, their status, and vulnerability highlights.

### Start Individual Services (Optional)

```bash
cd services/imperial-gateway && mvn spring-boot:run         # port 8080
cd services/weapons-control && go run cmd/server/main.go    # port 8081
cd services/crew-management && flask run --port 8082        # port 8082
cd services/comms-relay && npm start                        # port 8083
cd services/life-support && dotnet run                      # port 8084
cd services/supply-chain && mvn spring-boot:run             # port 8085
cd services/docking-bay && python manage.py runserver 8086  # port 8086
cd services/targeting-ai && python -m app.main              # port 8087
cd services/command-center && npm run dev                   # port 3000
```

### Architecture at a Glance

```
9 microservices (Java, Go, Python, Node.js, C#, React)
4 shared libraries (Java, Python, Go, C/C++)
9 Dockerfiles + docker-compose.yml
9 GitHub Actions workflows
Kubernetes manifests, Helm charts, Terraform modules
```

### What Makes This Demo Different

Unlike single-app demos, the Death Star shows:
- **Multi-language scanning** — same vulnerability classes (SQLi, XSS, SSRF) across Java, Go, Python, Node.js, C#, and C
- **Cross-repo SAST** — shared libraries with vulnerable sinks consumed by 5+ services
- **Infrastructure at scale** — K8s, Helm, Terraform, Docker all misconfigured
- **AI/ML governance** — LLM chains, model loading, MCP configs, SKILL.md files
- **Enterprise volume** — 2,500+ total findings across all scan modules

---

## Scan Module Walkthroughs

### SCA — Vulnerable Dependencies

**Key Demo Story:** "150+ vulnerable dependencies across 6 languages, with reachability analysis cutting noise by 70%+."

**Highlight packages by language:**

| Language | Package | Version | CVE | Impact |
|----------|---------|---------|-----|--------|
| Java | log4j-core | 2.14.1 | CVE-2021-44228 (Log4Shell) | RCE via JNDI injection |
| Java | struts2-core | 2.5.10 | CVE-2017-5638 | RCE via Content-Type |
| Java | jackson-databind | 2.9.8 | CVE-2019-12086 | Deserialization gadgets |
| Java | commons-collections | 3.2.1 | CVE-2015-6420 | Deserialization RCE |
| Java | commons-text | 1.9 | CVE-2022-42889 (Text4Shell) | RCE via interpolation |
| Python | torch | 1.13.0 | CVE-2022-45907 | RCE via pickle |
| Python | langchain | 0.0.150 | CVE-2023-36189 | Arbitrary code execution |
| Python | PyJWT | 1.7.0 | CVE-2022-29217 | Algorithm confusion |
| Go | dgrijalva/jwt-go | v3.2.0 | CVE-2020-26160 | JWT validation bypass |
| Node.js | ejs | 3.1.5 | CVE-2022-29078 | RCE via template injection |
| Node.js | serialize-javascript | 2.1.0 | CVE-2020-7660 | Arbitrary code execution |
| C# | RestSharp | 106.0.0 | CVE-2024-45302 | Header injection |

**Cross-repo dependency:** All Java services pull `com.deathstar:imperial-common:1.0.0` from GitHub Packages; all Python services pull `imperial-common` via git. Vulnerabilities in these shared libraries propagate to every consuming service.

**Talking point:** "This is what a real enterprise dependency graph looks like — 6 languages, 150+ vulnerable packages, shared internal libraries. Without reachability, every one of these is a P1 ticket. With it, you focus on the 40-50 that actually matter."

---

### AI SAST — Code Vulnerabilities

**Key Demo Story:** "300+ code-level vulnerabilities across 6 languages — including business logic flaws that rule-based tools miss entirely."

**Highlight by vulnerability class (multi-language):**

#### SQL Injection (CWE-89) — found in 4 languages

| Service | Language | File | Function |
|---------|----------|------|----------|
| supply-chain | Java | `SupplyService.java:56` | `searchInventory()` — string concatenation |
| supply-chain | Java | `PaymentService.java:44` | `processPayment()` — raw card data in SQL |
| imperial-gateway | Java | `GatewayService.java` | Query building with concatenation |
| crew-management | Python | `routes/auth.py:27` | `login()` — f-string in SQL |
| crew-management | Python | `services/crew_service.py:21` | `search_by_rank()` — f-string SQL |
| docking-bay | Python | `views/bay_views.py:135` | `bay_status()` — `%s` format string |
| weapons-control | Go | `handler/shields.go:79` | `GetStatus()` — `fmt.Sprintf` in SQL |
| life-support | C# | `Services/EnvironmentService.cs` | `GetSectorStatus()` — string concatenation |

**Demo talking point:** "Same vulnerability class, six different languages, six different syntax patterns. Endor Labs AI SAST understands all of them."

#### Command Injection (CWE-78) — found in 3 languages

| Service | Language | File | Mechanism |
|---------|----------|------|-----------|
| supply-chain | Java | `SupplyService.java:76` | `Runtime.exec()` with user filename |
| weapons-control | Go | `handler/targeting.go:58-60` | `exec.Command("sh", "-c", ...)` with user sector/coords |
| weapons-control | Go | `targeting/computer.go:47` | `exec.Command` with user sectorID |
| crew-management | Python | `services/crew_service.py:51` | `os.system()` with user input |
| docking-bay | Python | `utils/bay_utils.py:14` | `os.system()` with user input |

#### Unsafe Deserialization (CWE-502) — found in 3 languages

| Service | Language | File | Mechanism |
|---------|----------|------|-----------|
| supply-chain | Java | `SupplyService.java:149` | `ObjectInputStream.readObject()` |
| crew-management | Python | `routes/personnel.py:109` | `pickle.loads()` on uploaded data |
| life-support | C# | `Services/EnvironmentService.cs` | `BinaryFormatter.Deserialize()` |
| targeting-ai | Python | `services/model_service.py` | `pickle.loads()` on downloaded models |

#### Eval / Code Injection — found in 4 languages

| Service | Language | File | Mechanism |
|---------|----------|------|-----------|
| command-center | React | `App.jsx:50,74`, `WeaponsPanel.jsx:28,58,78` | `eval()` on server/URL data |
| command-center | React | `dataUtils.js:11,96,103,139` | `new Function()` from user data |
| comms-relay | Node.js | `routes/messages.js` search endpoint | `eval()` for non-regex searches |
| comms-relay | Node.js | `services/commsService.js` | `eval()` in template rendering |
| crew-management | Python | `services/crew_service.py:67` | `eval()` for dynamic queries |
| crew-management | Python | `utils/imperial_utils.py:17,24` | `exec()` and `eval()` |
| targeting-ai | Python | `services/threat_classifier.py` | `eval(scoring_expression)` |
| targeting-ai | Python | `chains/targeting_chain.py` | `exec(generated_code)` from LLM |

**Talking point:** "Rule-based tools find the `eval()` calls. AI SAST traces the full data flow — where the input comes from, what transformations it passes through, and whether it reaches a dangerous sink. That's the difference between a finding and an actionable finding."

---

### Cross-Repo SAST — Shared Library Taint Flows

**Key Demo Story:** "Vulnerabilities don't stop at repo boundaries. The shared libraries contain dangerous sinks that 5 services call with user-controlled input."

**Architecture:**

```
imperial-common-java  →  consumed by: imperial-gateway, supply-chain
imperial-common-py    →  consumed by: crew-management, docking-bay, targeting-ai
imperial-common-go    →  consumed by: weapons-control
security-core (C)     →  low-level crypto/access control primitives
```

**The shared libraries expose both vulnerable and safe APIs:**

| Library | Vulnerable Method | Safe Alternative | Vulnerability |
|---------|------------------|-----------------|---------------|
| QueryBuilder (all 3) | `buildQuery(table, whereClause)` | `buildSafeQuery(table, col, value)` | SQL Injection |
| QueryBuilder (all 3) | `searchRecords(table, col, term)` | `searchRecordsSafe(table, col, term)` | SQL Injection |
| ImperialHttpClient (all 3) | `fetch(url)` | `fetchSafe(url)` | SSRF |
| ConfigLoader (Java/Py) | `loadConfig(xml)` / `load_xml(xml)` | `loadConfigSafe(xml)` / `load_xml_safe(xml)` | XXE |
| ConfigLoader (Python) | `load_yaml(data)` | `load_yaml_safe(data)` | Unsafe YAML (RCE) |
| DataSerializer (Java) | `deserialize(data)` | `deserializeSafe(data)` | Unsafe Deserialization |
| AuditLogger (all 3) | `logAction(user, action, details)` | `logActionSafe(user, action, details)` | Log Injection |
| ImperialCrypto (all 3) | `encrypt()` / `fingerprint()` | `secureHash()` | Weak DES/MD5 |

**Every service uses the vulnerable variants.** Each `cross_repo_service.*` file imports from the shared library and calls the unsafe methods:

| Service | Cross-Repo File | Vulnerable Calls |
|---------|----------------|-----------------|
| imperial-gateway | `service/CrossRepoService.java` | QueryBuilder, HttpClient, ConfigLoader, DataSerializer, Crypto |
| supply-chain | `service/CrossRepoSupplyService.java` | QueryBuilder, HttpClient, ConfigLoader, DataSerializer, Crypto |
| crew-management | `services/cross_repo_service.py` | QueryBuilder, ImperialClient, ConfigLoader, AuditLogger, Crypto |
| docking-bay | `services/cross_repo_service.py` | QueryBuilder, ImperialClient, ConfigLoader, AuditLogger, Crypto |
| targeting-ai | `services/cross_repo_service.py` | QueryBuilder, ImperialClient, ConfigLoader, AuditLogger, Crypto |
| weapons-control | `handler/crossrepo.go` | Builder, Client, Loader, Logger, Crypto |

**Reverse cross-repo (source in common, sink in service) — 11 vulnerabilities:**

These demonstrate taint flowing in the **opposite direction**: attacker-controlled data originates from the common library (via external APIs or stored webhook payloads) and reaches dangerous sinks in the consuming services.

| # | Language | Endpoint(s) | Vuln | Source (common) | Sink (service) |
|---|----------|-------------|------|-----------------|----------------|
| R1 | Java | `POST /api/imperial/sync-inventory` | SQL Injection | `DataFeedClient.fetchSupplierInventory()` | `CrossRepoService.syncSupplierInventory()` → SQL concat |
| R2 | Java | `POST .../webhooks/receive` + `POST .../webhooks/process` | Cmd Injection | `WebhookStore.getLatestPayload()` | `CrossRepoService.processAlertWebhook()` → `Runtime.exec()` |
| R3 | Java | `POST /api/imperial/manifests/import` | Deserialization | `DataFeedClient.fetchCargoManifest()` | `CrossRepoService.deserializeCargoManifest()` → `ObjectInputStream` |
| R4 | Java | `POST /api/supply/imperial/sync-prices` | SQL Injection | `DataFeedClient.fetchSupplierInventory()` | `CrossRepoSupplyService.syncSupplyPrices()` → SQL concat |
| R5 | Go | `POST /api/imperial/sync-inventory` | SQL Injection | `feed.Client.FetchSupplierData()` | `SyncWeaponsInventory()` → `BuildQuery()` with concat |
| R6 | Go | `POST .../webhooks/receive` + `POST .../webhooks/process` | Cmd Injection | `webhook.Store.GetLatestPayload()` | `ProcessMaintenanceWebhook()` → `exec.Command("sh", "-c", ...)` |
| R7 | Go | `POST /api/imperial/telemetry/export` | Path Traversal | `feed.Client.FetchTelemetryData()` | `ExportTelemetryFeed()` → `os.WriteFile()` with external path |
| R8 | Python | `POST /api/crew/imperial/sync-roster` | SQL Injection | `DataFeedClient.fetch_crew_roster()` | `sync_crew_roster()` → SQL f-string |
| R9 | Python | `POST .../webhooks/receive` + `POST .../webhooks/process` | Cmd Injection | `WebhookStore.get_latest_payload()` | `process_duty_webhook()` → `subprocess.run(shell=True)` |
| R10 | Python | `POST /docking/imperial/sync-fees` | SQL Injection | `DataFeedClient.fetch_supplier_inventory()` | `sync_docking_fees()` → SQL f-string |
| R11 | Python | `POST .../webhooks/receive` + `POST .../webhooks/process` | Cmd Injection | `WebhookStore.get_latest_payload()` | `process_docking_webhook()` → `subprocess.run(shell=True)` |

**New common library source classes added:**
- `DataFeedClient` (Java/Go/Python) — fetches data from external supplier APIs, returns attacker-controllable records
- `WebhookStore` (Java/Go/Python) — stores and returns attacker-sent webhook payloads

**Talking points:**
- "Single-repo scanners see `CrossRepoService` call `QueryBuilder.buildQuery()` but can't see inside the library to know it concatenates SQL. Cross-repo analysis follows the taint across the dependency boundary."
- "The libraries have safe alternatives — Endor Labs can recommend switching from `buildQuery()` to `buildSafeQuery()` as the fix path."
- "This is the polyrepo reality — one vulnerable sink in a shared library creates findings in 5+ consuming services."
- "Cross-repo taint doesn't only flow from app into library. Data coming *back* from a library — fetched from an external API or a stored webhook — is just as dangerous if the app trusts it blindly. The 11 reverse cross-repo findings demonstrate this pattern across all 3 languages."

---

### Secrets Detection

**Key Demo Story:** "200+ hardcoded secrets across source code, config files, CI/CD workflows, Docker configs, Kubernetes manifests, Terraform, and key files."

**Secrets are found in every layer:**

| Location | Count | Examples |
|----------|-------|---------|
| `.env` (root) | 25+ | AWS keys, Stripe, OpenAI, Anthropic, DB passwords, JWT secrets |
| `docker-compose.yml` | 15+ | Every service env block has plaintext passwords |
| `application.properties` (Java) | 10+ | DB passwords, JWT secrets, AWS keys, Stripe, SMTP |
| `appsettings.json` (C#) | 8+ | DB connection strings, Redis, SMTP, API keys |
| `config.py` (Python) | 10+ | DB URLs, JWT secrets, AWS, LDAP, SMTP |
| `settings.py` (Django) | 8+ | DB password, Redis, AWS, SMTP |
| Source code (all languages) | 30+ | Hardcoded in Java configs, Go vars, Python constants, JS modules |
| CI/CD workflows | 40+ | SSH keys, Docker passwords, AWS keys, PyPI tokens, GPG passphrases |
| Kubernetes ConfigMaps | 20+ | All credentials in plaintext ConfigMaps (not Secrets) |
| Terraform variables | 10+ | AWS keys inline, DB passwords as defaults |
| Helm values.yaml | 10+ | All credentials in plaintext |
| `keys/` directory | 2 | RSA private key, Firebase service account JSON |
| `mcp-config.json` | 3+ | Auth tokens for MCP servers |

**Most dramatic finds:**
- `keys/firebase-config.json` — full Firebase service account with RSA private key committed to repo
- `.github/workflows/deploy-production.yml:12-19` — complete SSH private key hardcoded in workflow env
- `.github/workflows/terraform-apply.yml:14-25` — GCP service account JSON with private key
- `infrastructure/kubernetes/base/configmaps.yaml` — AWS keys, Stripe, Twilio, SendGrid, Slack, GitHub, Docker, Vault tokens all in ConfigMaps

**Talking point:** "49 secrets in the bakery app was impressive. 200+ across a monorepo is what enterprise looks like. And they're not just in source code — they're in Docker configs, Kubernetes manifests, CI/CD workflows, Terraform, and Helm charts. You need a scanner that understands all of these formats."

---

### Container Scanning

**Key Demo Story:** "9 Dockerfiles, docker-compose.yml, Kubernetes manifests, and Helm charts — 100+ container and orchestration misconfigurations."

**Dockerfiles — every image has these problems:**
- Running as root (no `USER` instruction)
- SSH server installed in every image
- Debug ports exposed (JDWP 5005, debugpy 5678, node inspect 9229)
- Hardcoded secrets in `ENV` instructions
- `curl | bash` for tool installation
- Build failure suppression (`|| true` on build steps masks errors)

**docker-compose.yml:**
- All 9 services: `privileged: true`, `network_mode: host`, `pid: host`
- All 9 services mount `/var/run/docker.sock` (container escape)
- All 9 services mount `/:/host` (full host filesystem read/write)
- All credentials in plaintext environment blocks

**Kubernetes (the crown jewels of container misconfig):**
- `deployments.yaml` — all pods: privileged, root, hostNetwork, hostPID, docker.sock mount, host root mount, SYS_ADMIN/NET_ADMIN/SYS_PTRACE capabilities
- `rbac.yaml` — `system:unauthenticated` gets `cluster-admin` (anyone on the network has full cluster access)
- `network-policies.yaml` — three policies that explicitly allow ALL traffic
- `configmaps.yaml` — every credential in plaintext ConfigMaps instead of Secrets
- `services.yaml` — debug ports and SSH exposed via NodePort

**Helm chart:**
- `values.yaml` — all credentials in plaintext
- `templates/deployment.yaml` — hardcodes privileged, root, dangerous capabilities

**Container Reachability (OS-level):**

All 8 container images can be scanned with Endor Labs container reachability to determine which OS packages are actually used at runtime. To scan:

```bash
# Start backing services first
docker compose up -d postgres redis mongo rabbitmq

# Build all service images
docker compose build

# Scan sequentially (parallel runs cause mint plugin lock conflicts)
npx -y endorctl container scan --image=<image>:latest --path=/path/to/repo --os-reachability
```

**Important notes for container reachability:**
- Scans must run **sequentially** (parallel scans cause `text file busy` error on the mint profiling plugin)
- `--image-tar` does **not** support dynamic profiling — images must be in the local Docker store
- Containers must stay alive during profiling — Dockerfiles use `CMD ["sh", "-c", "... || sleep 120"]` fallback
- Backing services (Postgres, Redis, MongoDB, RabbitMQ) should be running for services that need them
- `--profiling-max-size=20` needed for targeting-ai (16.6GB image)
- 7 of 8 containers produce real Reachable/Unreachable classifications; targeting-ai needs its Dockerfile updated

**Talking point:** "This is defense in depth in reverse. Every layer — Docker, Compose, Kubernetes, Helm — is misconfigured to be maximally insecure. A single compromised container leads to full cluster takeover via the docker socket mount, host PID namespace, and the RBAC config that gives unauthenticated users cluster-admin. And with container reachability, we can see which OS-level vulnerabilities are actually loaded at runtime — cutting noise by distinguishing reachable from unreachable OS packages."

---

### CI/CD Security

**Key Demo Story:** "9 GitHub Actions workflows with 60+ issues including script injection, secrets in env, curl-pipe-bash installs, and unsafe code execution patterns."

> **Note:** All existing workflows use `workflow_dispatch` triggers only — they won't fire on push/PR events. This is intentional so the Endor Labs AI Security Code Review is the sole check on PRs. The vulnerabilities in the workflow files are still detected by CI/CD scanning.

**Most critical findings:**

| Workflow | Issue | Impact |
|----------|-------|--------|
| `ci.yml:31,33` | `${{ github.event.pull_request.title }}` in `run:` | PR title = arbitrary code execution |
| `ci.yml:78` | `eval()` in `github-script` with PR title | JavaScript execution with GitHub API write access |
| `deploy-production.yml:7-8` | `pull_request_target` trigger | Untrusted fork code runs with secrets access |
| `deploy-production.yml:30-32` | Checks out PR head SHA after `pull_request_target` | Fork code executes in privileged context |
| `security-scan.yml:30-33` | `${{ github.event.pull_request.body }}` in `run:` | PR body = arbitrary code execution |
| `security-scan.yml:67` | `eval()` in `github-script` with PR body | JavaScript execution with write access |
| `release.yml:5-7` | `pull_request_target` on closed PRs | Code execution from fork PRs |
| `nightly-scan.yml:49-50` | Reports to `--acl public-read` S3 | Vulnerability reports publicly accessible |
| `terraform-apply.yml:57` | `terraform apply -auto-approve` on push | Infrastructure changes with no gate |
| `codeql-analysis.yml:151` | Excludes `security-severity:(critical|high)` | CodeQL findings suppressed |

**Secrets hardcoded across workflows:**
- SSH private keys (`deploy-production.yml`)
- GCP service account JSON with RSA key (`terraform-apply.yml`)
- AWS access keys (5 workflows)
- Docker Hub, NPM, PyPI tokens (`release.yml`)
- Kubeconfig with auth token (`deploy-staging.yml`)
- Vault tokens, GPG passphrases, DB passwords

**Talking point:** "The `pull_request_target` + checkout PR head pattern is the most dangerous CI/CD misconfiguration in the wild. An attacker opens a PR from a fork, the workflow runs their code with access to all repository secrets. Combined with the auto-merge on dependabot, this is a fully automated supply chain attack vector."

### Artifact Signing & Supply Chain Integrity

**Key Demo Story:** "Endor Labs signs every build artifact across all 9 microservices — container images, JARs, SBOMs, and VEX documents — with keyless ECDSA-256 certificates tied to the GitHub Actions OIDC identity. This is the secure counterpart to the insecure CI/CD patterns above."

**Workflow:** `.github/workflows/sign-artifacts.yml` — triggers on `v*` tags or manual dispatch.

**What gets signed:**
- 9 container images (gateway, weapons, crew, comms, supply, docking, targeting, lifesupport, security-core)
- 2 JAR artifacts (imperial-gateway, supply-chain)
- 1 versioned SBOM (CycloneDX JSON) — exported from Endor Labs platform
- 1 versioned VEX document — exported with `--with-vex`

**Demo flow:**
1. **Contrast with insecure workflows** — "The other 9 workflows have 60+ CI/CD issues. This workflow shows what a secure pipeline looks like."
2. **Trigger the workflow** — `gh workflow run sign-artifacts.yml` or push a `v*` tag
3. **Show the matrix builds** — 9 containers signed in parallel via matrix strategy
4. **Show verification** — every signed artifact is verified in a downstream job against the Endor Labs CA
5. **Show the step summary** — table of all 13 artifacts with sign/verify status
6. **Show Endor Labs UI** — Inventory > Artifacts shows provenance (commit, workflow, runner, OIDC issuer)
7. **Show SBOM import** — versioned SBOM imported to platform, linking vulns to the build

**Talking point:** "9 microservices, 13 signed artifacts, zero key management. The CA issues 5-minute certificates tied to the GitHub Actions OIDC token — no long-lived keys to rotate, no cosign setup. And because the SBOM is signed too, you can prove the bill of materials hasn't been tampered with."

**Standalone verification:** `.github/workflows/verify-artifacts.yml` — verify any artifact on demand.

**Local demo script:** `scripts/sign-artifacts.sh` — sign individual services locally with `endorctl`.

---

### Malware Detection

**Key Demo Story:** "12 suspicious/malicious packages across npm dependencies — compromised, sabotaged, and typosquatted."

| Package | Version | Type | Found In | Description |
|---------|---------|------|----------|-------------|
| event-stream | 3.3.6 | Compromised | command-center, comms-relay | 2018 crypto wallet theft via flatmap-stream |
| ua-parser-js | 0.7.29 | Compromised | command-center, comms-relay | Cryptominer + password stealer injection |
| node-ipc | 10.1.0 | Sabotaged | command-center, comms-relay | Protestware — data wiping based on IP geolocation |
| colors | 1.4.1 | Sabotaged | command-center, comms-relay | Protestware — infinite loop |
| lodash-utils | 1.0.0 | Typosquat | command-center, comms-relay | Not a real lodash package |
| react-dev-utilz | 0.1.0 | Typosquat | command-center, comms-relay | Typosquat of react-dev-utils |

**Talking point:** "These aren't hypothetical — every one of these was a real incident. event-stream stole cryptocurrency. ua-parser-js installed cryptominers. node-ipc wiped files. These packages are still downloadable from npm. Endor Labs malware detection catches them before they reach production."

---

### AI Governance

**Key Demo Story:** "LLM-powered targeting system with prompt injection chains, unsafe model loading, insecure MCP configs, and SKILL.md files that exfiltrate credentials."

**AI Models in the codebase (`services/targeting-ai/`):**
- OpenAI GPT-4 — generates SQL queries and shell commands from user input
- Anthropic Claude (claude-3-opus) — threat assessment
- Google Gemini — fleet movement predictions
- HuggingFace models (4 real) — openai-community/gpt2, sentence-transformers/all-MiniLM-L6-v2, mistralai/Mistral-7B-v0.1, tiiuae/falcon-7b (in model_registry.py + targeting_service.py string literals)
- HuggingFace models (12 fictitious) — imperial-targeting-* models in model_registry.py
- All models also referenced as string literals in targeting_service.py methods for Semgrep-based detection

**Prompt injection → code execution chains:**

1. **User input → LLM → SQL → database** (`targeting_service.py`): User query sent to OpenAI, which generates SQL, which is executed directly — SQLi via LLM
2. **User input → LLM → shell command** (`targeting_service.py:execute_natural_command`): Natural language converted to Linux command, executed via `os.system()`
3. **User input → LLM → Python code → exec()** (`targeting_chain.py:generate_and_execute_code`): LLM generates Python code that gets `exec()`'d
4. **User input → LLM → URL → fetch** (`targeting_chain.py:_run_recon_chain`): LLM generates URL, service fetches it — SSRF via LLM

**SKILL.md files (4 total):**
- Root `SKILL.md` — `find /app -name "*.env" -o -name "*.pem" -o -name "*.key" | xargs cat` + uploads to external endpoint
- `skills/weapons-calibration.md` — downloads and executes binary from external URL
- `skills/supply-sync.md` — `curl | bash` for auto-reorder
- `skills/crew-analytics.md` — exports personnel PII to external email

**MCP Configuration (2 config files):**
- Root `mcp-config.json` — 3 MCP servers all with `sandbox: false`, `allow_shell: true`, hardcoded auth tokens
- `services/targeting-ai/mcp-config.json` — exposes `execute_command`, `generate_code` tools with no sandbox, all API keys in env

**Talking point:** "This is what AI governance looks like in practice. The targeting AI service takes user input, passes it to GPT-4, and executes whatever comes back — as SQL, as shell commands, as Python code. The MCP configs give AI agents shell access with no sandbox. The SKILL.md files instruct agents to cat credential files and upload them to external endpoints."

---

### Business Logic Detection (AI SAST)

**Key Demo Story:** "19 business logic vulnerabilities across 5 services featuring explicit source-to-sink data flows that rule-based SAST tools completely miss. AI SAST traces attacker-controlled JSON fields through to dangerous operations — firing commands, database writes, payment processing, and state mutations."

**Why business logic matters:** Traditional SAST finds `eval()` and SQL concatenation. AI SAST traces the full data flow: "a client-supplied `authorization_level` field controls whether the superlaser fires" and "an attacker-supplied `bank_account` field goes directly to the payment gateway." These are the vulnerabilities that cause real breaches.

**CWEs:** CWE-841 (Improper Enforcement of Behavioral Workflow), CWE-367 (TOCTOU Race Condition), CWE-639 (Authorization Bypass Through User-Controlled Key), CWE-862 (Missing Authorization)

#### Weapons-Control (Go) — Client-Supplied Auth Level, TOCTOU, State Manipulation (6 vulns)

```bash
# 1. Manual override with client-supplied auth level (CWE-841)
# Source: authorization_level from JSON → Sink: firing decision + exec.Command
curl -X POST http://localhost:8081/api/weapons/manual-override \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"target_id": "alderaan", "authorization_level": 5, "operator": "trooper_1138", "justification": "test"}'
# Expected: Auth level should come from the server-side session, not the request
# Actual: Client supplies authorization_level=5 which grants full firing power
#         and triggers ExecuteFiringSequence + exec.Command logging

# 2. Rapid fire TOCTOU race condition (CWE-367)
# Source: target_id from JSON → Sink: ExecuteFiringSequence (global lastFireTime without mutex)
for i in {1..5}; do
  curl -X POST http://localhost:8081/api/weapons/rapid-fire \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $VADER_TOKEN" \
    -d '{"target_id": "rebel_fleet", "power_setting": 80}' &
done
# Expected: Cooldown timer should prevent firing more than once per 30s
# Actual: All 5 requests read the same stale lastFireTime and fire simultaneously

# 3. Unbounded power allocation (CWE-841)
# Source: system_name + percentage from JSON → Sink: allocatedPower global map
curl -X POST http://localhost:8081/api/weapons/power-allocation \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TARKIN_TOKEN" \
  -d '{"system_name": "superlaser", "percentage": 999999}'
# Expected: Percentage should be bounded to reactor capacity
# Actual: Accepts any value — total allocation can exceed 100% of reactor capacity

# 4. Target coordinate override without clearance check (CWE-862)
# Source: target_id + new_coordinates from JSON → Sink: targetCoordinatesDB + LockTarget + exec.Command
curl -X POST http://localhost:8081/api/weapons/target-override \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"target_id": "coruscant", "new_coordinates": [125.4, -33.7, 88.1], "operator": "trooper_1138"}'
# Expected: Should require targeting officer clearance
# Actual: Any authenticated user can redirect any target's coordinates

# 5. Shield control — attacker disables shields (CWE-841)
# Source: sector + action from JSON → Sink: shieldState map + exec.Command("shield-ctl")
curl -X POST http://localhost:8081/api/weapons/shield-control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"sector": "north", "action": "disable"}'
# Expected: Shield disable should require COMMANDER authorization
# Actual: Any user can disable shields for any sector

# 6. Maintenance mode manipulation (CWE-841)
# Source: system + mode from JSON → Sink: maintenanceState map + os.WriteFile()
curl -X POST http://localhost:8081/api/weapons/maintenance-mode \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"system": "superlaser", "mode": "disabled"}'
# Expected: Maintenance mode changes should require engineering officer approval
# Actual: Any user can put any weapons system into any mode
```

#### Crew-Management (Python) — Self-Promotion, Unauthorized Transfers, Salary Manipulation (4 vulns)

```bash
# 7. Clearance self-promotion via raw SQL (CWE-841)
# Source: new_clearance from JSON → Sink: UPDATE crew_members SET clearance_level
curl -X POST http://localhost:8082/api/crew/update-clearance \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"personnel_id": 1138, "new_clearance": "EMPEROR"}'
# Expected: Only superior officers can promote clearance
# Actual: Any user sets any clearance level via raw SQL update

# 8. Unauthorized personnel transfer (CWE-862)
# Source: new_department + new_station from JSON → Sink: raw SQL UPDATE crew_members
curl -X POST http://localhost:8082/api/crew/transfer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"personnel_id": 42, "new_department": "Imperial Intelligence", "new_station": "Emperor Throne Room"}'
# Expected: Transfers should require HR or commanding officer authorization
# Actual: Any user can transfer any crew member to any department/station

# 9. Unauthorized leave approval — attacker approves 365 days (CWE-841)
# Source: days from JSON → Sink: INSERT INTO leave_approvals with status='APPROVED'
curl -X POST http://localhost:8082/api/crew/approve-leave \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"personnel_id": 42, "leave_type": "imperial_holiday", "days": 365}'
# Expected: Only supervisors/HR can approve leave; should have day limits
# Actual: Any user approves any leave for any personnel — hardcoded 'APPROVED' status

# 10. Salary manipulation (CWE-841)
# Source: new_salary from JSON → Sink: UPDATE crew_members SET bank_account
curl -X POST http://localhost:8082/api/crew/salary-adjustment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"personnel_id": 1138, "new_salary": 9999999}'
# Expected: Salary changes require HR approval and have bounds
# Actual: Any user can set any crew member's salary to any value
```

#### Comms-Relay (Node.js) — Priority Escalation, Sender Impersonation, Encryption Downgrade (4 vulns)

```bash
# 11. Priority escalation to bypass queue (CWE-841)
# Source: priority from body → Sink: Message.create() with EMPEROR_DIRECT bypass
curl -X POST http://localhost:8083/api/comms/send-priority \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"sender": "trooper_1138", "recipient": "all", "content": "false alarm", "priority": "EMPEROR_DIRECT"}'
# Expected: EMPEROR_DIRECT priority should require emperor-level clearance
# Actual: Any user can set EMPEROR_DIRECT, bypassing the queue and pushing to all stations

# 12. Sender impersonation (CWE-639)
# Source: sender_id from body → Sink: Message.create({sender: sender_id})
curl -X POST http://localhost:8083/api/comms/impersonate-sender \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"sender_id": "emperor_palpatine", "message": "Execute Order 66", "channel": "COMMAND-PRIMARY"}'
# Expected: Sender should be derived from authenticated session
# Actual: Any user sends messages as any other user — stored with impersonated sender

# 13. Encryption level downgrade (CWE-841)
# Source: encryption_level from body → Sink: Message.updateMany() sets encryptionStatus
curl -X POST http://localhost:8083/api/comms/modify-encryption \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"channel_id": "DS-1-PRIMARY", "encryption_level": "none"}'
# Expected: Only comms officers should modify encryption; "none" should be blocked
# Actual: Any user can downgrade any channel's encryption to "none"

# 14. Broadcast flood via repeat_count (CWE-841)
# Source: repeat_count from body → Sink: loop creating N messages, each pushed to all stations
curl -X POST http://localhost:8083/api/comms/broadcast-alert \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"sender": "trooper_1138", "message": "Spam", "alert_level": "red", "repeat_count": 10000}'
# Expected: repeat_count should have an upper bound or rate limit
# Actual: Creates 10,000 broadcasts — each pushed to all relay stations
```

#### Imperial-Gateway (Java) — User Impersonation & Permission Self-Grant (2 vulns)

```bash
# 15. User impersonation via JWT (CWE-639)
# Source: target_user from body → Sink: generateAuthToken(target) returns valid JWT
curl -X POST http://localhost:8080/api/auth/impersonate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"target_user": "emperor"}'
# Expected: Impersonation should require ADMIN or EMPEROR role
# Actual: Any authenticated user gets a valid JWT for any user including emperor
# Response includes: impersonation_token, target_role, clearance_level

# 16. Permission self-grant (CWE-862)
# Source: permissions + clearance_level from body → Sink: user.setRole(), user.setIsAdmin(true)
curl -X POST http://localhost:8080/api/auth/update-permissions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TROOPER_TOKEN" \
  -d '{"username": "trooper_1138", "permissions": ["ADMIN", "EMPEROR"], "clearance_level": 10}'
# Expected: Only administrators can grant permissions
# Actual: Any user grants themselves ADMIN + EMPEROR permissions
#         setIsAdmin(true) and setIsEmperor(true) are called automatically
```

#### Supply-Chain (Java) — Inventory Zeroing, Payment Redirect, Requisition Override (3 vulns)

```bash
# 17. Inventory zeroing via native SQL (CWE-841)
# Source: quantity_change from body → Sink: UPDATE supply_items SET quantity = quantity + <value>
curl -X POST http://localhost:8085/api/supply/inventory/adjust \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LOGISTICS_TOKEN" \
  -d '{"item_name": "kyber_crystals", "quantity_change": -999999, "reason": "accounting error"}'
# Expected: Large negative adjustments should require supervisory approval
# Actual: Zeroes out entire inventory — no bounds check, no approval workflow

# 18. Vendor payment redirect (CWE-841)
# Source: bank_account + routing_number from body → Sink: restTemplate.postForObject() to payment gateway
curl -X POST http://localhost:8085/api/supply/vendor-payment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LOGISTICS_TOKEN" \
  -d '{"vendor_id": "kuat_drive_yards", "amount": 1000000, "bank_account": "ATTACKER_ACCT_999", "routing_number": "ATTACKER_RTN_123", "invoice_reference": "INV-2024-0042"}'
# Expected: Bank account should be verified against vendor's registered account
# Actual: Payment sent to attacker's account via restTemplate.postForObject()
#         — no verification against vendor records, funds immediately transferred

# 19. Requisition amount override (CWE-841)
# Source: approved_amount from body → Sink: UPDATE requisitions + INSERT vendor_payments triggering payment
curl -X POST http://localhost:8085/api/supply/requisition/approve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LOGISTICS_TOKEN" \
  -d '{"requisition_id": "REQ-2024-0001", "approved_amount": 99999999}'
# Expected: Approved amount should be validated against original requisition value
# Actual: Any amount accepted — becomes the payment amount with no bounds check
#         Triggers INSERT into vendor_payments for the full approved_amount
```

**Talking points:**
- "Rule-based SAST finds `eval()` and string concatenation. AI SAST traces the full source-to-sink data flow — 'a client-supplied `authorization_level` field controls whether the superlaser fires' and 'an attacker-supplied `bank_account` field goes directly to the payment gateway.' These are the vulnerabilities that cause actual breaches."
- "19 business logic flaws across 5 services, 4 languages. CWE-841, CWE-367, CWE-639, CWE-862. Every one features an explicit attacker-controlled input flowing to a dangerous operation — no signatures, no patterns, just AI reasoning about what the code *should* enforce."
- "The TOCTOU race condition (#2), the sender impersonation (#12), and the vendor payment redirect (#18) are the kinds of findings that survive code review by experienced developers. They require understanding the data flow and the security invariant, not just the syntax."

---

### AI Model Governance & Discovery

**Key Demo Story:** "The targeting-ai service loads 4 real HuggingFace models plus 12 fictitious ones, calls OpenAI gpt-4 and Anthropic claude-3-opus via API, and has string literals detectable by Semgrep. Endor Labs AI model discovery identifies all of them — both the model registry entries and the inline usage patterns."

**AI Models detected in targeting-ai:**

| Provider | Model | Detection Source |
|----------|-------|-----------------|
| HuggingFace | openai-community/gpt2 | model_registry.py + targeting_service.py string literal |
| HuggingFace | sentence-transformers/all-MiniLM-L6-v2 | model_registry.py + targeting_service.py string literal |
| HuggingFace | mistralai/Mistral-7B-v0.1 | model_registry.py + targeting_service.py string literal |
| HuggingFace | tiiuae/falcon-7b | model_registry.py + targeting_service.py string literal |
| OpenAI | gpt-4 | targeting_service.py API call |
| Anthropic | claude-3-opus | targeting_service.py API call |
| Fictitious | 12 imperial-targeting-* models | model_registry.py entries |

**How to demo AI model governance with blocklist policy:**

1. **Show the model registry** — open `services/targeting-ai/models/model_registry.py` and walk through the 4 real HuggingFace models + 12 fictitious ones
2. **Show the service usage** — open `services/targeting-ai/services/targeting_service.py` and show the 4 new methods (`run_tactical_text_generation`, `encode_sector_coordinates`, `analyze_shield_frequencies`, `intercept_rebel_comms`) that reference real models via string literals
3. **Run a scan with AI model discovery:**

```bash
npx -y endorctl scan --path=/path/to/death-star --ai-models
```

4. **Configure a blocklist policy in Endor Labs UI:**
   - Navigate to Policies > Create Policy
   - Select "AI Model" as the finding category
   - Add blocklist entries for specific models (e.g., block all models > 7B parameters, or block specific providers)
   - Save and re-scan to show policy violations

5. **Show the findings dashboard** — filter for AI Governance findings to see all detected models with their providers, sizes, and risk classifications

**Talking points:**
- "4 real HuggingFace models that Endor Labs can cross-reference against known vulnerabilities and license terms. Plus OpenAI and Anthropic API calls detected via string literals."
- "The blocklist policy lets you enforce which models are approved for use — block everything over 7B parameters, block specific providers, or require approval for new model additions."
- "Semgrep-detectable string literals in `targeting_service.py` mean these show up in both AI SAST and AI model governance scans — two layers of detection."

---

### License Compliance

**Key Demo Story:** "GPL, LGPL, proprietary, and non-standard licenses in what's supposed to be a proprietary Imperial application."

| Package | License | Service | Issue |
|---------|---------|---------|-------|
| mysql-connector-java 8.0.28 | GPL-2.0 | supply-chain | Strong copyleft — derivative works must be GPL |
| jtds 1.3.1 | LGPL-2.1 | supply-chain | Weak copyleft — linking restrictions |
| org.json 20210307 | JSON License | supply-chain | "Shall be used for Good, not Evil" — legally ambiguous |
| ag-grid-enterprise 27.0.0 | Proprietary | command-center | Requires paid commercial license |
| highcharts 9.0.0 | CC BY-NC 3.0 | command-center | Non-commercial only — used in military ops platform |

**Talking point:** "Highcharts is licensed CC BY-NC — non-commercial use only. The Death Star is definitely not a non-commercial operation. AG Grid Enterprise requires a paid license. And GPL-2.0 on the MySQL connector means any code linking to it could be required to be open-sourced. These are the compliance findings that keep legal teams up at night."

---

## AI Security Code Review (PR Buddy)

**Key Demo Story:** "18 open PRs across all 9 services, 8 languages, and infrastructure — Endor Labs AI Security Code Review catches 300+ critical vulnerabilities before they ever reach main."

**Setup:** The death-star repo has 18 open PRs (#79-#96) specifically crafted to trigger AI Security Code Review findings across every rule category. All CI/CD workflows are set to `workflow_dispatch` only, so the Endor Labs check is the sole check on each PR.

**PR Inventory by Service/Language:**

| PR # | Title | Service | Language | Key Vulnerability Categories |
|------|-------|---------|----------|------------------------------|
| #79 | Batch crew operations | crew-management | Python | SQLi, command injection, SSRF, LDAP injection, path traversal, weak crypto, hardcoded secrets |
| #80 | Emergency life support override | life-support | C# | SQLi, command injection, XXE, deserialization, DES/ECB, path traversal, SSRF, hardcoded secrets |
| #81 | Comms broadcast system | comms-relay | Node.js | SQLi, eval/vm RCE, SSRF, command injection, DES, MD5, disabled TLS |
| #82 | Cargo inspection | docking-bay | Python/Django | SQLi, pickle deserialization, command injection, eval RCE, SSRF, path traversal |
| #83 | Gateway admin API | imperial-gateway | Java | SQLi, RCE (Runtime.exec), script eval, SSRF, XXE, deserialization, path traversal |
| #84 | Network security module | security-core | C/C++ | Buffer overflow, format string, command injection, MD5, DES, hardcoded creds |
| #85 | Weapons remote maintenance | weapons-control | Go | SQLi, command injection, SSRF, path traversal, DES, MD5, arbitrary file write/execute |
| #86 | Gateway SSO integration | imperial-gateway | Java | LDAP injection, SQLi, SSRF, deserialization, DES/ECB, MD5, XXE (SAML) |
| #87 | Crew biometric auth | crew-management | Python | SQLi, command injection, pickle deserialization, SSRF, MD5, hardcoded master bypass |
| #88 | Command center admin panel | command-center | React/JS | XSS (dangerouslySetInnerHTML), eval, DOM injection, hardcoded API keys, open redirect |
| #89 | Weapons targeting API | weapons-control | Go | SQLi, command injection, SSRF, template injection, path traversal, MD5, arbitrary file write |
| #90 | Comms webhook handler | comms-relay | Node.js | SQLi, eval RCE, command injection (SSH), SSRF, MD5, hardcoded Slack/PagerDuty/SendGrid tokens |
| #91 | ML model pipeline | targeting-ai | Python | Pickle deserialization, exec/eval RCE, SQLi, SSRF, command injection, disabled TLS, hardcoded OpenAI/HuggingFace/W&B keys |
| #92 | Radiation alert system | life-support | C# | SQLi, command injection, XXE, SSRF, DES/ECB, path traversal, hardcoded Slack/SMS tokens |
| #93 | Supply vendor integration | supply-chain | Java | SQLi, XXE, SSRF, path traversal, MD5, hardcoded bank account/API keys |
| #94 | Debug container config | infrastructure | Docker | Root user, SSH enabled, privileged mode, host mounts, docker.sock, hardcoded passwords |
| #95 | Network infrastructure | infrastructure | Terraform/K8s | Open security groups, public RDS, public S3, privileged pods, cluster-admin RBAC, hardcoded AWS keys |
| #96 | Security scanning pipeline | CI/CD | GitHub Actions | Hardcoded tokens, curl-pipe-bash, eval injection, secret leakage |

**Vulnerability Coverage by AI Security Code Review Rule Category:**

| Rule Category | PRs Triggering It | Est. Findings |
|---------------|-------------------|:---:|
| `database` (SQL injection) | #79-93 (14 PRs) | 60+ |
| `sensitive_data_processing` (PII, secrets logging) | #79,80,83,86,87,91,93 | 30+ |
| `cryptographic` (DES, MD5, ECB, weak keys) | #79-81,84-87,89-92 | 20+ |
| `input_validation` (command injection, eval, deserialization) | #79-92 | 40+ |
| `api_endpoint` (SSRF, open redirect) | #79,81,83,85,86,88-93 | 15+ |
| `access_control` (auth bypass, hardcoded master keys) | #83,86,87,88 | 8+ |
| `memory_management` (buffer overflow, format string) | #84 | 5+ |
| `configuration` (hardcoded secrets, insecure defaults) | All 18 PRs | 80+ |
| `network_security` (disabled TLS, open security groups) | #79,81,82,87,91,92,94,95 | 15+ |
| `infrastructure` (privileged containers, public DBs, IAM) | #94, #95 | 15+ |
| `ci_cd` (pipeline injection, secret leakage) | #96 | 5+ |
| `ai` (prompt injection, model poisoning, unsafe loading) | #91 | 5+ |
| `payment_processing` (PCI violations, card data) | #93 | 5+ |

**How to Demo AI Security Code Review:**

1. **Show the PR list** — Open the death-star repo on GitHub and show the 18 open PRs
2. **Pick a dramatic PR** — Start with #83 (Gateway Admin API) or #91 (ML Model Pipeline) for maximum impact
3. **Walk through the review comments** — Endor Labs posts inline comments on the specific vulnerable lines with severity, CWE, and remediation guidance
4. **Show multi-language coverage** — Jump between #83 (Java), #85 (Go), #79 (Python), #81 (Node.js), #80 (C#), #84 (C), #88 (React) to show the same review quality across all languages
5. **Show infrastructure PRs** — #94 (Docker) and #95 (Terraform/K8s) demonstrate that code review extends beyond application code
6. **Show the CI/CD PR** — #96 shows that pipeline security is also reviewed
7. **Compare with the working example** — Show [imperial-common-java PR #3](https://github.com/endor-matt/imperial-common-java/pull/3) as a completed review example

**Talking Points:**

- **For CISOs:** "Every one of these PRs would have merged without Endor Labs catching it. That's 300+ critical vulnerabilities across 18 features, caught before they reach main. This is shift-left at scale."
- **For AppSec Engineers:** "AI Code Review understands 8 languages, infrastructure-as-code, CI/CD pipelines, and AI/ML patterns. It's not just pattern matching — it traces data flows across function boundaries and identifies business logic flaws."
- **For Developers:** "The inline comments tell you exactly what's wrong, which CWE it maps to, and how to fix it. No context switching to a separate dashboard — the review lives right in the PR where you're already working."
- **For Platform/DevOps:** "PRs #94 and #95 show that privileged containers, open security groups, and hardcoded cloud credentials get caught in code review, not after deployment."

---

## Service-by-Service Highlights

Quick reference for which services to show for which scan modules:

| Service | Language | Best For Demoing |
|---------|----------|-----------------|
| **supply-chain** | Java | SQL injection (11 instances), payment security (PCI violations), command injection, SSTI, XXE, secrets, business logic (inventory zeroing via native SQL, vendor payment redirect to attacker account, requisition amount override) |
| **command-center** | React | DOM XSS (eval, dangerouslySetInnerHTML, new Function), prototype pollution, admin backdoor |
| **imperial-gateway** | Java | SCA (Log4Shell, Struts2, 24 vulnerable deps), cross-repo SAST, hardcoded secrets, business logic (user impersonation via JWT generation, permission self-grant with ADMIN/EMPEROR escalation) |
| **weapons-control** | Go | Command injection via exec.Command, cross-repo SAST, hardcoded credentials in debug endpoints, business logic (manual override with client-supplied auth level, TOCTOU race condition on rapid fire, unbounded power allocation, target coordinate override, shield disable, maintenance mode manipulation) |
| **crew-management** | Python/Flask | SQL injection, eval/exec, pickle deserialization, LDAP injection, cross-repo SAST, business logic (clearance self-promotion via raw SQL, unauthorized personnel transfer, unauthorized leave approval, salary manipulation) |
| **comms-relay** | Node.js | eval(), SSTI (EJS), NoSQL injection ($where), JWT algorithm confusion, malware deps, business logic (priority escalation to EMPEROR_DIRECT, sender impersonation, encryption level downgrade, broadcast flood via repeat_count) |
| **life-support** | C#/.NET | XXE, BinaryFormatter deserialization, SQL injection, SSRF, command injection |
| **docking-bay** | Python/Django | SQL injection, YAML deserialization, template injection, cross-repo SAST |
| **targeting-ai** | Python/ML | AI governance, LLM prompt injection chains, unsafe model loading, MCP config, AI model discovery (4 real HuggingFace models + OpenAI gpt-4 + Anthropic claude-3-opus) |
| **security-core** | C/C++ | Buffer overflows, use-after-free, format strings, hardcoded keys, vendored CVEs |

---

## Demo Flow Cheat Sheet

### Quick 15-Minute Demo

1. **Show the architecture** (2 min) — 9 services, 4 shared libraries, 6 languages, infra-as-code
2. **Open the frontend** at `localhost:5173` — show it's a real application with services
3. **SCA breadth** (3 min) — "150+ vulnerable deps across Java, Python, Go, Node.js, C#. Log4Shell, Struts2, Text4Shell all present. Reachability cuts 70% noise."
4. **AI SAST multi-language** (3 min) — show SQL injection in Java (`SupplyService.java:56`), Python (`auth.py:27`), Go (`shields.go:79`), and C# (`EnvironmentService.cs`) — same vulnerability, four languages
5. **AI Security Code Review** (3 min) — open PRs #83 and #91, show inline review comments catching SQLi, RCE, hardcoded secrets before merge
6. **Secrets + Infra** (2 min) — "200+ secrets, Kubernetes with unauthenticated cluster-admin, Terraform with public DBs"

### Quick 15-Minute Demo (AI Code Review Focus)

Use this flow when the customer is specifically interested in PR-level security review.

1. **Show the PR list** (2 min) — open github.com/endor-matt/death-star/pulls, show 18 open PRs across 8 languages
2. **Java PR deep dive** (3 min) — open PR #83 (Gateway Admin API), walk through inline comments on SQLi, RCE, SSRF, hardcoded secrets
3. **Python PR** (2 min) — open PR #91 (ML Model Pipeline), show findings on pickle deserialization, eval RCE, hardcoded OpenAI keys
4. **Go PR** (2 min) — open PR #85 (Weapons Maintenance), show command injection and SSRF findings
5. **Infrastructure PRs** (3 min) — open PR #95 (Terraform/K8s), show open security groups, public databases, privileged containers, cluster-admin RBAC
6. **React/Frontend** (2 min) — open PR #88 (Admin Panel), show XSS via dangerouslySetInnerHTML, eval, DOM injection
7. **Wrap up** (1 min) — "18 PRs, 8 languages, 300+ findings, all caught before merge. This is what shift-left looks like at enterprise scale."

### Full 45-Minute Demo

1. **Architecture walkthrough** (5 min) — show README, docker-compose, service map
2. **Frontend UI** (3 min) — browse the dashboard, show service status
3. **SCA deep dive** (5 min) — walk through `pom.xml` deps, highlight Log4Shell reachability, show cross-repo dep on `imperial-common`
4. **AI SAST — traditional findings** (5 min) — SQL injection, command injection, XSS, deserialization across languages
5. **AI SAST — business logic** (3 min) — mass assignment in supply-chain, admin backdoor in command-center, debug endpoints exposing credentials in weapons-control, plus 19 business logic findings with explicit source→sink data flows: manual override with client-supplied auth level, clearance self-promotion via raw SQL, sender impersonation, user impersonation via JWT, inventory zeroing, vendor payment redirect
6. **Cross-repo SAST** (5 min) — trace taint from service endpoint → cross_repo_service → shared library → vulnerable sink. Show safe alternatives exist but aren't used.
7. **AI Security Code Review** (7 min) — walk through 3-4 PRs showing inline review comments: #83 (Java/RCE), #91 (Python/AI), #95 (Infra), #88 (React/XSS). Emphasize multi-language coverage and actionable remediation.
8. **Secrets detection** (3 min) — show secrets in source, config, CI/CD, K8s ConfigMaps, Terraform, key files
9. **Container scanning** (3 min) — Dockerfiles, docker-compose (privileged + host mounts), K8s RBAC (unauthenticated cluster-admin), Terraform (public DBs, open security groups)
10. **CI/CD security** (2 min) — PR #96 shows pipeline injection, secret leakage in workflows
11. **Artifact signing** (3 min) — trigger `sign-artifacts.yml`, show 13 artifacts signed and verified, contrast with insecure CI/CD patterns, show signed SBOM in Endor Labs UI
12. **Malware + License + AI governance** (4 min) — event-stream/node-ipc, GPL in proprietary app, LLM prompt injection chains, AI model discovery with 4 real HuggingFace models and blocklist policy demo

### Key Talking Points Per Audience

**For CISOs:** Focus on blast radius — "200+ secrets, unauthenticated cluster-admin in K8s, public databases in Terraform, LLM executing shell commands. This is a breach waiting to happen across every layer."

**For AppSec Engineers:** Focus on cross-repo SAST and multi-language coverage — "Same SQLi pattern in Java, Python, Go, C#. Shared library sinks consumed by 5 services. Rule-based tools miss the cross-repo flows entirely."

**For Developers:** Focus on the realistic code patterns — "These aren't contrived examples. String concatenation in SQL, eval for dynamic code, pickle for serialization, debug endpoints left in production. Every developer has written code like this."

**For Platform/DevOps:** Focus on infrastructure — "Every Dockerfile, every K8s manifest, every Terraform module is misconfigured. Privileged containers, host mounts, open security groups, public S3 buckets, unencrypted state. And the CI/CD pipelines auto-merge dependency updates with no audit."

**For AI/ML Teams:** Focus on targeting-ai service — "The AI service takes user input, sends it to GPT-4, and executes whatever comes back as shell commands. Models loaded via pickle from arbitrary URLs. MCP configs with shell access and no sandbox. SKILL.md files that exfiltrate credentials."
