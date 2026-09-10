# Death Star Operations Platform — Intentionally Vulnerable Demo Monorepo

## What This Is

A massive intentionally vulnerable monorepo designed to showcase the full breadth of Endor Labs' AURI platform scanning capabilities across multiple languages, frameworks, and infrastructure technologies. Used by Endor Labs SAs for customer demos demonstrating multi-language, multi-service security scanning at enterprise scale.

## Architecture

9 microservices + 4 shared libraries + infrastructure-as-code + CI/CD pipelines, spanning Java, Go, Python, JavaScript, C#, and C/C++.

### Services

| Service | Language | Purpose |
|---------|----------|---------|
| imperial-gateway | Java 17 / Spring Boot 3.x | API gateway, auth, routing |
| weapons-control | Go 1.21 | Superlaser targeting, shields |
| crew-management | Python / Flask | Personnel, clearances |
| comms-relay | Node.js / Express | Communications, encryption |
| life-support | C# / .NET 8 | Environmental controls |
| supply-chain | Java 17 / Spring Boot 3.x | Logistics, procurement |
| docking-bay | Python / Django | Ship registry, cargo |
| targeting-ai | Python / ML | AI targeting, LLM chains |
| command-center | React 18 | Operations dashboard |

### Shared Libraries (Cross-Repo SAST)

| Library | Language | Purpose |
|---------|----------|---------|
| security-core | C/C++ | Low-level crypto, access control |
| imperial-common-java | Java | Query building, HTTP, audit |
| imperial-common-py | Python | Crypto, config, query |
| imperial-common-go | Go | Crypto, HTTP, audit |

## Key Rules

- **Every vulnerability must be REALISTIC** — no `// THIS IS VULNERABLE` comments
- **The README.md reads like a real project** — no mention of intentional vulnerabilities
- **Star Wars / Death Star themed** — personnel are Imperial officers, inventory is tibanna gas and kyber crystals
- **Multi-language** — Java 17, Go 1.21, Python 3.11, Node.js 20, C# .NET 8, C/C++
- **Cross-repo SAST** — shared libraries with vulnerable sinks consumed by multiple services

## Expected Findings

| Scan Module | Target Count | Languages |
|-------------|-------------|-----------|
| SCA | 150+ vulnerable dependencies | Java, Python, JS, Go, C# |
| AI SAST | 300+ code-level vulnerabilities | All 6 languages |
| Business Logic / AI SAST | 19 business logic flaws (source→sink data flows: auth bypass, race conditions, IDOR, missing authorization, sender impersonation, encryption downgrade) | Go, Python, Node.js, Java |
| Secrets | 200+ hardcoded secrets | Source, config, env, CI/CD, keys |
| Container | 100+ Dockerfile/K8s/Compose misconfigs | Docker, K8s, Helm |
| Container Reachability | OS-level reachability on 7 of 8 images | Docker (Reachable/Unreachable) |
| Malware | 20+ suspicious/malicious packages | npm, PyPI, Maven |
| CI/CD | 60+ pipeline issues | GitHub Actions (10+ workflows) |
| AI Governance | 30+ model/skill/MCP findings + 4 real HuggingFace models + 12 fictitious models + OpenAI gpt-4 + Anthropic claude-3-opus | Python, SKILL.md, MCP config |
| License | 20+ compliance issues | Java (GPL), JS (CC BY-NC), mixed |
| Cross-Repo SAST | 50+ cross-module taint flows + 11 reverse cross-repo (source in common, sink in service) | Java, Python, Go shared libs |
| AI Security Code Review | 300+ findings across 18 PRs | All 8 languages + IaC + CI/CD |
| **TOTAL** | **~2800+ findings** (including 19 business logic vulns with explicit source→sink data flows and enhanced AI model discovery) | |

## AI Security Code Review PRs

18 open PRs (#79-#96) designed to showcase Endor Labs AI Security Code Review across all services, languages, and infrastructure. Each PR introduces realistic vulnerabilities that trigger multiple review rule categories including `database`, `input_validation`, `cryptographic`, `sensitive_data_processing`, `access_control`, `api_endpoint`, `memory_management`, `configuration`, `network_security`, `infrastructure`, `ci_cd`, `ai`, and `payment_processing`. See DEMO_GUIDE.md for the full PR inventory and demo walkthrough.

## Artifact Signing

The project includes Endor Labs artifact signing workflows (`.github/workflows/sign-artifacts.yml` and `verify-artifacts.yml`) that build, sign, and verify all 9 container images, 2 JARs, SBOMs, and VEX documents. These are functional workflows that demonstrate secure supply chain practices, contrasting with the 62 intentional CI/CD findings in the other workflows. The stale SHA pins on actions are intentional for RSPM demo findings.

**Requires:** `ENDOR_NAMESPACE` as a repository secret. Trigger via `gh workflow run sign-artifacts.yml` or push a `v*` tag.

**Local demo:** `scripts/sign-artifacts.sh` — sign and verify individual services locally with `endorctl`.

## Reference Docs

- https://docs.api.endorlabs.com/scan/sca/
- https://docs.api.endorlabs.com/scan/sast/
- https://docs.api.endorlabs.com/scan/secrets/
- https://docs.api.endorlabs.com/scan/containers/
- https://docs.api.endorlabs.com/scan/containers/container-reachability/
- https://docs.api.endorlabs.com/scan/containers/artifact-signing/
- https://docs.api.endorlabs.com/scan/malware/
- https://docs.api.endorlabs.com/scan/ai-models/
- https://docs.api.endorlabs.com/scan/oss-licenses/
- https://docs.api.endorlabs.com/scan/rspm/
