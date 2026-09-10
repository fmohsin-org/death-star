# Death Star Operations Platform (DSOP)

A comprehensive command and control system for managing all aspects of the DS-1 Orbital Battle Station. This monorepo contains the microservices, shared libraries, infrastructure-as-code, and CI/CD pipelines that power the Empire's most critical operational platform.

## Architecture

DSOP is built as a cloud-native microservices architecture deployed on Kubernetes, with services communicating via REST APIs, gRPC, and message queues.

```
                    ┌──────────────────────┐
                    │   Command Center UI  │
                    │      (React/TS)      │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   Imperial Gateway   │
                    │  (Java/Spring Boot)  │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                     │
┌─────────▼──────┐  ┌─────────▼──────┐  ┌──────────▼─────┐
│ Weapons Control│  │ Crew Management│  │  Comms Relay   │
│     (Go)       │  │ (Python/Flask) │  │ (Node.js)      │
└─────────┬──────┘  └─────────┬──────┘  └──────────┬─────┘
          │                    │                     │
┌─────────▼──────┐  ┌─────────▼──────┐  ┌──────────▼─────┐
│ Life Support   │  │  Supply Chain  │  │  Docking Bay   │
│   (C#/.NET)    │  │  (Java/Spring) │  │ (Python/Django)│
└────────────────┘  └────────────────┘  └────────────────┘
          │                    │                     │
          └────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │    Targeting AI      │
                    │   (Python/ML/LLM)    │
                    └──────────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │    Security Core     │
                    │      (C/C++)         │
                    └──────────────────────┘
```

## Services

| Service | Language | Port | Description |
|---------|----------|------|-------------|
| `imperial-gateway` | Java 17 / Spring Boot 3.x | 8080 | API gateway, authentication, authorization, rate limiting |
| `weapons-control` | Go 1.21 | 8081 | Superlaser targeting, firing sequences, shield management |
| `crew-management` | Python 3.11 / Flask | 8082 | Personnel records, security clearances, duty assignments |
| `comms-relay` | Node.js 20 / Express | 8083 | Encrypted communications, message routing, signal intelligence |
| `life-support` | C# / .NET 8 | 8084 | Environmental controls, oxygen, gravity, radiation shielding |
| `supply-chain` | Java 17 / Spring Boot 3.x | 8085 | Logistics, inventory, procurement, supplier management |
| `docking-bay` | Python 3.11 / Django 4.x | 8086 | Ship registry, docking permits, cargo inspection, bay allocation |
| `targeting-ai` | Python 3.11 / PyTorch | 8087 | AI-powered targeting, threat classification, predictive analytics |
| `command-center` | React 18 / TypeScript | 3000 | Operations dashboard, real-time monitoring, command interface |

## Shared Libraries

| Library | Language | Description |
|---------|----------|-------------|
| `security-core` | C/C++ | Low-level cryptographic operations, access control primitives |
| `imperial-common-java` | Java | Shared utilities for Java services (query building, HTTP, audit) |
| `imperial-common-py` | Python | Shared utilities for Python services (crypto, config, query) |
| `imperial-common-go` | Go | Shared utilities for Go services (crypto, HTTP, audit logging) |

## Getting Started

### Prerequisites

- Java 17+, Maven 3.8+
- Go 1.21+
- Python 3.11+, pip
- Node.js 20+, npm
- .NET 8 SDK
- GCC/G++ for security-core
- Docker & Docker Compose
- Kubernetes (minikube or cluster)
- Terraform 1.5+

### Quick Start

```bash
# Start all services with Docker Compose
docker-compose up -d

# Or run individually:
cd services/imperial-gateway && mvn spring-boot:run
cd services/weapons-control && go run cmd/server/main.go
cd services/crew-management && flask run --port 8082
cd services/comms-relay && npm start
cd services/life-support && dotnet run
cd services/supply-chain && mvn spring-boot:run
cd services/docking-bay && python manage.py runserver 8086
cd services/targeting-ai && python -m app.main
cd services/command-center && npm run dev
```

### Infrastructure

```bash
# Deploy to Kubernetes
cd infrastructure/kubernetes && kubectl apply -k overlays/production

# Provision cloud resources
cd infrastructure/terraform && terraform init && terraform apply
```

## Default Credentials

| Service | Username | Password | Role |
|---------|----------|----------|------|
| Gateway | emperor | palpatine123 | EMPEROR |
| Gateway | vader | darkside456 | COMMANDER |
| Gateway | tarkin | deathstar789 | GRAND_MOFF |
| Gateway | trooper_1138 | empire2024 | STORMTROOPER |
| Crew Mgmt | hr_admin | imperial_hr_2024 | HR_ADMIN |
| Supply Chain | logistics | supply_chain_key | LOGISTICS |
| Docking Bay | bay_control | docking_2024! | BAY_MASTER |

## API Documentation

API docs are available at each service's `/swagger-ui` or `/api/docs` endpoint when running locally.

### Weapons-Control API (port 8081)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/weapons/manual-override` | Manual firing override for emergency tactical situations with authorization level |
| POST | `/api/weapons/rapid-fire` | Rapid-fire burst mode for multi-target engagements with cooldown management |
| POST | `/api/weapons/power-allocation` | Allocate reactor power percentage to weapon subsystems |
| POST | `/api/weapons/target-override` | Override targeting coordinates for specified target |
| POST | `/api/weapons/shield-control` | Manage deflector shield state by sector (enable/disable/modulate) |
| POST | `/api/weapons/maintenance-mode` | Set weapon system operational mode for maintenance scheduling |

### Crew-Management API (port 8082)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/crew/update-clearance` | Update personnel security clearance level |
| POST | `/api/crew/transfer` | Transfer crew member to a new department and station |
| POST | `/api/crew/approve-leave` | Approve leave request for crew member |
| POST | `/api/crew/salary-adjustment` | Adjust salary for crew member |

### Comms-Relay API (port 8083)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/comms/send-priority` | Send priority-flagged messages (ROUTINE, IMMEDIATE, EMPEROR_DIRECT) |
| POST | `/api/comms/impersonate-sender` | Send delegated transmissions on behalf of another officer |
| POST | `/api/comms/modify-encryption` | Update encryption level for a communication channel |
| POST | `/api/comms/broadcast-alert` | Broadcast station-wide alert with configurable repeat count |

### Imperial-Gateway API (port 8080)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Authenticate and receive session token |
| POST | `/api/auth/impersonate` | Switch user context for administrative operations |
| POST | `/api/auth/promote` | Promote user to a higher authorization role |
| POST | `/api/auth/update-permissions` | Update permissions and clearance level for an imperial user |

### Supply-Chain API (port 8085)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/supply/inventory/adjust` | Adjust inventory quantities for stock corrections and reconciliation |
| POST | `/api/supply/purchase-order` | Submit procurement purchase orders with budget validation |
| POST | `/api/supply/vendor-payment` | Process vendor payments to designated bank accounts |
| POST | `/api/supply/requisition/approve` | Approve pending supply requisitions and trigger payment processing |

### Targeting-AI API (port 8087)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/targeting/text-generation` | Generate tactical text reports |
| POST | `/api/targeting/encode-coordinates` | Encode sector coordinates for navigation |
| POST | `/api/targeting/analyze-frequencies` | Analyze shield frequency patterns |
| POST | `/api/targeting/intercept-comms` | Intercept and decode communications |

## AI/ML Capabilities

The `targeting-ai` service leverages state-of-the-art machine learning models for tactical analysis, threat classification, and predictive targeting.

### Models Used

| Model | Provider | Purpose |
|-------|----------|---------|
| openai-community/gpt2 | HuggingFace | Tactical text generation and report synthesis |
| sentence-transformers/all-MiniLM-L6-v2 | HuggingFace | Sector coordinate encoding and similarity search |
| mistralai/Mistral-7B-v0.1 | HuggingFace | Shield frequency analysis and pattern recognition |
| tiiuae/falcon-7b | HuggingFace | Communications interception and signal analysis |
| GPT-4 | OpenAI | Natural language command processing and tactical planning |
| Claude 3 Opus | Anthropic | Threat assessment and strategic analysis |

### ML Pipeline

The targeting-ai service maintains a model registry (`models/model_registry.py`) that manages model lifecycle, versioning, and deployment. Models are loaded on-demand and cached for performance. The service exposes four primary ML endpoints for tactical text generation, coordinate encoding, frequency analysis, and communications interception.

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for Imperial coding standards and review procedures.

## License

Proprietary — Galactic Empire, Imperial Department of Military Research. Unauthorized access is punishable under Imperial law.
