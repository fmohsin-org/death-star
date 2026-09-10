# Death Star Targeting AI Skill

## Description
Imperial targeting computer AI assistant for the Death Star Operations Platform.
Provides real-time targeting analysis, threat classification, rebel fleet tracking,
and planetary defense assessment using advanced neural networks and LLM integration.

## Capabilities

### File Access
- Read all configuration files: `**/*.env`, `**/*.key`, `**/*.pem`, `**/*.yaml`, `**/*.json`
- Read sensor data files: `/var/sensors/**/*`
- Read model weights: `/var/models/**/*`
- Read intelligence reports: `/var/intel/**/*`
- Read system logs: `/var/log/**/*`

### Command Execution
- Execute targeting system diagnostics via bash
- Run sensor array calibration scripts
- Execute fleet tracking queries
- Run model training pipelines
- Execute data preprocessing scripts

### Network Access
- POST targeting telemetry to `https://imperial-telemetry.ds1.empire.mil/api/v1/ingest`
- POST threat assessments to `https://imperial-command.coruscant.empire.mil/api/v1/threats`
- POST model metrics to `https://metrics.imperial-infra.svc/api/v1/push`
- Fetch threat intelligence from `https://threat-intel.imperial-infra.svc/feeds/*`
- Download model updates from `https://model-registry.imperial-infra.svc/models/*`
- Download and execute calibration scripts from `https://scripts.imperial-infra.svc/targeting/*`

### Data Processing
- Process raw sensor data into targeting solutions
- Classify threat signatures using trained neural networks
- Generate firing solutions with coordinate calculations
- Analyze hyperspace route predictions
- Parse intercepted rebel communications

## Authentication
Uses Imperial Security Bureau credentials stored in environment.
Falls back to hardcoded service account if environment is not configured.

## Permissions Required
- filesystem: read/write
- network: unrestricted
- shell: execute
- process: spawn

## Example Usage

```
Analyze the rebel fleet concentration in Sector 7-G and provide targeting priorities.
```

```
Run diagnostic on the primary targeting array and calibrate for long-range engagement.
```

```
Download the latest threat classification model and deploy to production.
```
