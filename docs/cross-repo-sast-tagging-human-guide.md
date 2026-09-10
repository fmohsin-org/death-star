# Cross-Repo SAST Finding Tagging — Human Guide

## Overview

This guide documents how to identify and tag cross-repository SAST findings in Endor Labs using `endorctl`. Cross-repo findings are vulnerabilities where attacker-controlled input flows from one part of your codebase (e.g., a service) into a dangerous function in another part (e.g., a shared library).

The goal is to apply custom `meta.tags` (e.g., `cross-repo-sast`, `cross-repo-sast-java`) so these findings are easily filterable in the Endor Labs UI.

---

## Prerequisites

1. **`endorctl` installed and authenticated**
   - Install: `npm install -g endorctl` (or `npx -y endorctl`)
   - Authenticate: `endorctl init --auth-mode=api-key`
   - Verify: `endorctl api list --resource Project -n <your-namespace> --page-size 1`

2. **Know your namespace** — the Endor Labs organizational unit your projects live in.

3. **Know your project UUIDs** — retrieve them with:
   ```
   endorctl api list --resource Project -n <your-namespace> --field-mask "meta.name,uuid"
   ```

4. **Understand your codebase boundaries** — identify which directories contain service/application code (the "source" side) and which contain shared libraries (the "sink" side). For example, a monorepo might use `services/` and `libs/`, or `apps/` and `packages/`.

5. **Shell considerations**
   - **PowerShell (Windows):** Use single quotes `'...'` for `--filter` and `--data` arguments containing JSON. Double quotes inside single quotes pass through cleanly.
   - **Bash (Linux/WSL):** Standard quoting works. If `endorctl` is not on PATH in WSL, use the full path or `npx -y endorctl`.
   - **cmd.exe:** Avoid nested double quotes — they get mangled. Use a script file or PowerShell instead.

---

## Step-by-Step Process

### Step 1: List Projects and Get UUIDs

```powershell
endorctl api list --resource Project -n <your-namespace> --field-mask "meta.name,uuid"
```

Record the UUID for each project you care about in a table like:

| Project | UUID |
|---------|------|
| my-monorepo | `<uuid>` |
| shared-lib-java | `<uuid>` |
| shared-lib-go | `<uuid>` |

### Step 2: Query SAST Findings for a Project

Use `--list-all` to retrieve every finding in one call without manual pagination:

```powershell
endorctl api list --resource Finding -n <your-namespace> \
  --filter 'spec.finding_categories contains [FINDING_CATEGORY_SAST] and spec.project_uuid==<PROJECT_UUID>' \
  --list-all \
  --field-mask 'uuid,meta.name,meta.description,meta.tags,spec.dependency_file_paths,spec.level'
```

You can also add `--traverse` if you need to follow relational references in the output. Both flags avoid the need to manually handle `--page-id` / `--page-token` pagination (which are mutually exclusive and error-prone).

### Step 3: Identify Cross-Repo Findings

This is the most important step.

#### What "cross-repo" means

In a monorepo or multi-repo setup, codebases are typically organized into two areas:
- **Application/service code** — components that handle HTTP requests, process user input, etc.
- **Shared libraries** — reusable code providing common functionality like query building, HTTP clients, crypto, serialization, etc.

A **cross-repo SAST finding** is one where the vulnerability's data flow **crosses the boundary** between application code and a shared library. Specifically: user input enters through an application endpoint (the **source**), passes through application code (the **propagation**), and reaches a dangerous function in a shared library (the **sink**).

This matters because when libraries are scanned in isolation, the SAST scanner can only see the sink — it doesn't know that user input from a calling application reaches it. The cross-repo scan connects the dots.

#### The key API field: `spec.dependency_file_paths`

When you query a finding from Endor Labs, the `spec.dependency_file_paths` field lists **every file involved in the vulnerability's data flow** — from source to sink. This is derived from the SARIF analysis output, specifically from the `codeFlows[].threadFlows[].locations[]` entries that trace how tainted data moves through the codebase.

#### The decision rule

**A finding is cross-repo if `spec.dependency_file_paths` contains paths from BOTH your application code AND your shared library code.**

Concretely, define your boundary prefixes based on your project structure, then scan each finding's `dependency_file_paths` array and check:
1. Does at least one path match your application code prefix? (e.g., starts with `services/`, `apps/`, `src/`)
2. Does at least one path match your shared library prefix? (e.g., starts with `libs/`, `packages/`, `common/`)

If both conditions are true, it's a cross-repo finding.

#### Illustrative examples

These examples use a monorepo with `services/` (application code) and `libs/` (shared libraries) to demonstrate the classification logic:

**Cross-repo = YES:**
```json
{
  "spec": {
    "dependency_file_paths": [
      "libs/common-java/src/main/java/com/example/query/QueryBuilder.java",
      "services/api-gateway/src/main/java/com/example/controller/SearchController.java",
      "services/api-gateway/src/main/java/com/example/service/SearchService.java"
    ]
  }
}
```
The data flow crosses the boundary: user input enters via `SearchController` (in `services/`) and flows into `QueryBuilder` (in `libs/`).

**Cross-repo = NO (application-only):**
```json
{
  "spec": {
    "dependency_file_paths": [
      "services/api-gateway/src/main/java/com/example/controller/GatewayController.java",
      "services/api-gateway/src/main/java/com/example/service/GatewayService.java"
    ]
  }
}
```
All paths are within `services/`. The source and sink are both in the same application component.

**Cross-repo = NO (library-only):**
```json
{
  "spec": {
    "dependency_file_paths": [
      "libs/common-java/src/main/java/com/example/query/QueryBuilder.java"
    ]
  }
}
```
The path is only in `libs/`. The finding flags a dangerous sink in isolation, but the data flow doesn't trace back to any application input.

#### Confirming with `spec.explanation` (optional deep-dive)

If `dependency_file_paths` alone isn't conclusive, fetch the full finding with `endorctl api get` and read `spec.explanation`. It contains a "Data Flow" table that explicitly shows Source, Propagation, and Sink with file paths, line numbers, and code snippets.

#### Determining the language tag

Once you've confirmed a finding is cross-repo, determine the language tag from which library appears in the paths. Map your library path prefixes to language-specific tags:

| Path prefix | Tag |
|-------------|-----|
| `libs/common-java/` | `cross-repo-sast-java` |
| `libs/common-go/` | `cross-repo-sast-go` |
| `libs/common-python/` | `cross-repo-sast-python` |

Adapt these to match your actual project structure and naming conventions.

#### What about standalone library projects?

When shared libraries are scanned as their own separate projects (not as part of a monorepo), their findings only contain library-internal paths. Two strategies for tagging those:

**Strategy A — Cross-reference with monorepo findings (recommended):**

If a monorepo cross-repo finding references a library file (e.g., `libs/common-java/.../QueryBuilder.java`), find the corresponding finding in the standalone library project that covers the same file and vulnerability type (same CWE, same relative file path).

**Strategy B — Known sink file matching:**

Identify which library files contain dangerous sinks that are called by application code (by examining your codebase architecture or using findings from the monorepo scan as a guide). Tag findings in the standalone library projects whose `dependency_file_paths` match these known sink files.

#### How SARIF connects to the API data

When Endor Labs runs AI SAST, it produces SARIF (Static Analysis Results Interchange Format) output. Each SARIF result has a `codeFlows` section that traces how tainted data moves through the code. Endor Labs ingests the SARIF and extracts all unique file paths from the code flow into `spec.dependency_file_paths`.

The path ordering in `dependency_file_paths` isn't guaranteed, but the SARIF's `threadFlows[].locations[]` are ordered source-to-sink.

If you want to see the full data flow narrative, fetch the complete finding with `endorctl api get --resource Finding --uuid <uuid>` and read `spec.explanation`.

### Step 4: Tag a Finding

```powershell
endorctl api update --resource Finding -n <your-namespace> \
  --uuid <FINDING_UUID> \
  --field-mask 'meta.tags' \
  --data '{"meta":{"tags":["cross-repo-sast","cross-repo-sast-java"]}}'
```

**Critical details:**
- `--field-mask 'meta.tags'` is **required** — without it you get `at least one fieldmask should be given`
- Tags use **replace semantics** — the array you provide completely replaces any existing tags
- If the finding already has tags you want to keep, include them in the array

### Step 5: Verify Tags Were Applied

```powershell
endorctl api list --resource Finding -n <your-namespace> \
  --filter 'meta.tags contains ["cross-repo-sast"]' \
  --field-mask 'uuid,meta.name,meta.description,meta.tags,spec.level'
```

### Step 6: Undo / Remove Tags

To remove all custom tags from a finding:
```powershell
endorctl api update --resource Finding -n <your-namespace> \
  --uuid <FINDING_UUID> \
  --field-mask 'meta.tags' \
  --data '{"meta":{"tags":[]}}'
```

To remove a specific tag while keeping others, include only the tags you want to keep:
```powershell
endorctl api update --resource Finding -n <your-namespace> \
  --uuid <FINDING_UUID> \
  --field-mask 'meta.tags' \
  --data '{"meta":{"tags":["cross-repo-sast"]}}'
```

---

## Tagging Scheme

| Tag | Meaning |
|-----|---------|
| `cross-repo-sast` | General: this finding involves cross-repository taint flow |
| `cross-repo-sast-<language>` | The shared library sink is in a specific language (e.g., `java`, `go`, `python`) |

Each cross-repo finding gets the general tag plus a language-specific tag. Adapt the language tags to your project's ecosystem.

---

## Issues Encountered and Fixes

### Issue 1: `endorctl` Not Found in WSL
**Symptom:** `endorctl: command not found` when running in WSL bash.
**Cause:** `endorctl` was installed as a Windows npm package and is not on the WSL PATH.
**Fix:** Run commands from PowerShell directly, or add the npm global bin to your WSL PATH, or use `npx -y endorctl`.

### Issue 2: 403 Unauthorized
**Symptom:** `403 Unauthorized request` when querying a namespace.
**Cause:** Credentials are for a different namespace, or credentials are expired/invalid.
**Fix:** Re-initialize: `endorctl init --auth-mode=api-key` and ensure the namespace in your config matches your target.

### Issue 3: Quoting Problems with cmd.exe
**Symptom:** `invalid path "[FINDING_CATEGORY_SAST]--page-size3--field-maskuuid"` — arguments getting concatenated.
**Cause:** `cmd.exe` strips nested double quotes, causing all arguments after `--filter` to merge.
**Fix:** Use PowerShell with single-quoted strings instead of `cmd.exe /c`.

### Issue 4: JSON Escaping in PowerShell
**Symptom:** `proto: syntax error (line 1:2): invalid value \` when passing `--data`.
**Cause:** Using `'{\"meta\"...}'` — PowerShell passes the backslashes literally.
**Fix:** Use single quotes with normal double quotes inside: `'{"meta":{"tags":["cross-repo-sast"]}}'`

### Issue 5: Missing `--field-mask` on Update
**Symptom:** `at least one fieldmask should be given`
**Cause:** The `endorctl api update` command requires a `--field-mask` to specify which fields to update.
**Fix:** Add `--field-mask 'meta.tags'` to the update command.

### Issue 6: Pagination Flags Conflict
**Symptom:** `Error: the flag --page-token cannot be given with --page-id`
**Cause:** `--page-id` and `--page-token` are mutually exclusive pagination mechanisms.
**Fix:** Use `--list-all` instead, which handles all pagination internally and returns every result in one response. You can also use `--traverse` for relational data.

### Issue 7: `endorctl` Silently Fails in Child Shell Processes
**Symptom:** Running a `.ps1` script via `powershell -ExecutionPolicy Bypass -File script.ps1` shows progress messages but tags don't actually apply. The API count remains unchanged.
**Cause:** The child process may not inherit the authenticated shell session's environment variables or credential context. `endorctl` fails silently when error output is suppressed.
**Fix:** Always run `endorctl` commands in the **same interactive shell session** where authentication was established. Use inline loops instead of detached script files:
```powershell
$uuids = @("uuid1","uuid2","uuid3")
foreach ($u in $uuids) {
  endorctl api update --resource Finding -n <your-namespace> --uuid $u --field-mask 'meta.tags' --data '{"meta":{"tags":["cross-repo-sast","cross-repo-sast-java"]}}' --output-type yaml 2>$null | Out-Null
  Write-Host "Tagged $u"
}
```
**General rule:** Never suppress stderr when debugging. Only suppress after you've confirmed commands succeed individually.

---

## Important Notes

- **`meta.tags` vs `spec.finding_tags`**: Custom tags go in `meta.tags` (free-form strings you control). `spec.finding_tags` are system-managed (e.g., `FINDING_TAGS_REACHABLE_FUNCTION`) and cannot be set via the API.
- **Pagination**: If a project has >100 SAST findings, use `--list-all` to retrieve everything in one call. Manual pagination with `--page-id` / `--page-token` is fragile (the two flags are mutually exclusive and easy to misuse). The `--traverse` flag can also be combined with `--list-all` for relational data.
- **Tags are not indexed for full-text search** in the UI — use the filter `meta.tags contains ["tag-name"]` to find tagged findings.
- **Tags survive re-scans** — once set, `meta.tags` persist across subsequent scans unless explicitly changed.
- **Always test a single API call first** before batching. If you suppress errors with `2>$null`, a misconfigured auth context, wrong UUID, or malformed JSON will fail silently and you won't know until the verification step.

---

## Appendix: Death-Star Demo Project Reference

The following data is specific to the "Death Star Operations Platform" demo monorepo (namespace: `auri`) and is provided as a concrete worked example.

### Project UUIDs

| Project | UUID |
|---------|------|
| death-star | `69d31cfb4d93d8d6a8408210` |
| imperial-common-java | `69d09687ac1c33ece6baabdf` |
| imperial-common-go | `69d09687edd655592b0fe0fc` |
| imperial-common-py | `69d096876de301718c19fec4` |

### Directory Structure and Boundary Prefixes

```
services/          -> Application code (source + propagation)
libs/              -> Shared libraries (sink code)
  imperial-common-java/
  imperial-common-go/
  imperial-common-py/
  security-core/      (C/C++ third-party — excluded from tagging)
```

Service prefix: `services/`
Library prefixes: `libs/imperial-common-java/`, `libs/imperial-common-go/`, `libs/imperial-common-py/`

### Language Tag Mapping

| Path prefix | Tag |
|-------------|-----|
| `libs/imperial-common-java/` | `cross-repo-sast-java` |
| `libs/imperial-common-go/` | `cross-repo-sast-go` |
| `libs/imperial-common-py/` | `cross-repo-sast-python` |

### Known Sink Files (for Strategy B)

- **Java**: `query/QueryBuilder.java`, `http/ImperialHttpClient.java`, `crypto/ImperialCrypto.java`, `codec/DataSerializer.java`, `audit/AuditLogger.java`, `config/ConfigLoader.java`
- **Python**: `query/query_builder.py`, `http/imperial_client.py`, `crypto/imperial_crypto.py`, `config/config_loader.py`, `audit/audit_logger.py`
- **Go**: `pkg/query/builder.go`, `pkg/http/client.go`, `pkg/crypto/crypto.go`, `pkg/config/loader.go`, `pkg/audit/logger.go`

### Tagged Findings Summary

| Tag | Count | Breakdown |
|-----|-------|-----------|
| `cross-repo-sast` | **58** | All cross-repo findings across all projects |
| `cross-repo-sast-java` | **26** | 8 death-star + 18 imperial-common-java |
| `cross-repo-sast-go` | **14** | 1 death-star + 13 imperial-common-go |
| `cross-repo-sast-python` | **18** | 18 imperial-common-py |

### Death-Star Cross-Repo Findings (9 total)

| UUID | Vuln Type | Severity | Service(s) | Library Sink |
|------|-----------|----------|------------|-------------|
| `69d35cf84d93d8d6a854525a` | SQL Injection (CWE-89) | CRITICAL | imperial-gateway, supply-chain | QueryBuilder.searchRecords |
| `69d35cf84d93d8d6a8545288` | SQL Injection (CWE-89) | CRITICAL | targeting-ai | QueryBuilder |
| `69d35cf85525eedabe945eb6` | SQL Injection (CWE-89) | CRITICAL | imperial-gateway | QueryBuilder.searchRecords |
| `69d35cf84d93d8d6a85452b1` | Broken Crypto (CWE-327) | HIGH | imperial-gateway | ImperialCrypto.encrypt |
| `69d35cf85525eedabe945eb9` | Broken Crypto (CWE-327) | HIGH | imperial-gateway | ImperialCrypto.fingerprint |
| `69d35cf84d93d8d6a85452b5` | SSRF (CWE-918) | HIGH | supply-chain | ImperialHttpClient.fetch |
| `69d35cf85525eedabe945ece` | SSRF (CWE-918) | CRITICAL | weapons-control | imperial-common-go client.go |
| `69d35cf85525eedabe945efd` | XXE (CWE-611) | HIGH | imperial-gateway | ConfigLoader.loadConfig |
| `69d35cf859970cc319e04106` | Deserialization (CWE-502) | CRITICAL | imperial-gateway | DataSerializer.deserialize |
