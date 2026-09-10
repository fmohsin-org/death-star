# Cross-Repo SAST Finding Tagging — Agent Specification

## Objective

Tag SAST findings in Endor Labs that represent cross-repository vulnerability flows with custom `meta.tags`. A cross-repo finding is one where attacker-controlled data flows from **application code** (source) into a **shared library** (sink) across repository or module boundaries.

## Environment

- **Tool**: `endorctl` CLI (must be on PATH or invoked via `npx -y endorctl`)
- **Auth**: Pre-configured via `~/.endorctl/config.yaml` or environment variables `ENDOR_API_CREDENTIALS_KEY`, `ENDOR_API_CREDENTIALS_SECRET`, `ENDOR_NAMESPACE`
- **Shell**: PowerShell preferred on Windows (avoids cmd.exe quoting issues). Bash on Linux/WSL.
- **Namespace**: Specified per-command with `-n <namespace>`

## Quoting Rules (Critical)

These rules prevent the most common failure mode:

| Shell | `--filter` / `--data` quoting | Example |
|-------|-------------------------------|---------|
| PowerShell | Single quotes `'...'` with normal double quotes inside | `--data '{"meta":{"tags":["t1"]}}'` |
| Bash | Single quotes or escaped double quotes | `--data '{"meta":{"tags":["t1"]}}'` |
| cmd.exe | **DO NOT USE** — nested quotes get mangled | Use PowerShell or a script file instead |

Never use backslash-escaped quotes (`\"`) in PowerShell — they pass as literal backslashes.

## Tag Schema

```
cross-repo-sast              # General cross-repo indicator
cross-repo-sast-<language>   # Sink is in a shared library of this language (e.g., java, go, python)
```

Each finding receives `cross-repo-sast` plus exactly one language-specific tag. Adapt the language suffix to your project's ecosystem.

## API Reference

### List projects
```
endorctl api list --resource Project -n <ns> --field-mask "meta.name,uuid"
```
**Returns**: `{ "list": { "objects": [{ "meta": { "name": "..." }, "uuid": "..." }, ...] } }`

### Count SAST findings
```
endorctl api list --resource Finding -n <ns> --filter 'spec.finding_categories contains [FINDING_CATEGORY_SAST]' --count
```
**Returns**: `{ "count_response": { "count": <int> } }`

### List SAST findings for a project
```
endorctl api list --resource Finding -n <ns> \
  --filter 'spec.finding_categories contains [FINDING_CATEGORY_SAST] and spec.project_uuid==<uuid>' \
  --list-all \
  --field-mask 'uuid,meta.name,meta.description,meta.tags,spec.dependency_file_paths,spec.level'
```
**IMPORTANT**: Always use `--list-all` to retrieve all findings in a single call. This avoids manual pagination entirely. You can also add `--traverse` to follow relational references.

**DO NOT** use `--page-id` and `--page-token` together — they are mutually exclusive and will error with `the flag --page-token cannot be given with --page-id`. If you must paginate manually (e.g., to limit memory), use `--page-size <int>` and then pass only `--page-id <next_page_id>` from the response for subsequent pages.

**Returns**: `{ "list": { "objects": [...], "response": {} } }`. When `response` is empty (`{}`), there are no more pages.

### Get single finding (full detail)
```
endorctl api get --resource Finding -n <ns> --uuid <uuid>
```

### Update finding tags
```
endorctl api update --resource Finding -n <ns> \
  --uuid <uuid> \
  --field-mask 'meta.tags' \
  --data '{"meta":{"tags":["tag1","tag2"]}}'
```
**IMPORTANT**: 
- `--field-mask 'meta.tags'` is REQUIRED or the command fails with `at least one fieldmask should be given`
- Tags use REPLACE semantics — the provided array completely replaces existing tags
- To preserve existing tags, read them first, merge, then write back
- Returns the full updated finding object on success (exit code 0)

### Remove all tags (undo)
```
endorctl api update --resource Finding -n <ns> \
  --uuid <uuid> \
  --field-mask 'meta.tags' \
  --data '{"meta":{"tags":[]}}'
```

### Filter by tag
```
endorctl api list --resource Finding -n <ns> \
  --filter 'meta.tags contains ["cross-repo-sast"]' \
  --field-mask 'uuid,meta.name,meta.tags,spec.level'
```

## Algorithm: Identify Cross-Repo Findings

### Conceptual Background

A "cross-repo" SAST finding represents a vulnerability where the data flow crosses the boundary between two codebases:
- **Source (application)**: An HTTP endpoint or entry point receives attacker-controlled input
- **Propagation (application)**: The application passes the input to a shared library function
- **Sink (shared library)**: The library function performs a dangerous operation (SQL query, HTTP request, crypto, deserialization) with the unsanitized input

The cross-repo nature is critical because scanning either codebase in isolation misses the full picture: the library sees a sink but doesn't know user input reaches it; the application sees a function call but doesn't know the callee is dangerous.

### Data Sources Used for Determination

The primary data source is the Endor Labs API field `spec.dependency_file_paths` on each Finding object. This field is populated from the SARIF analysis output and lists every file involved in the vulnerability's data flow (source -> propagation -> sink).

The SARIF-to-API mapping is:
```
SARIF: runs[].results[].codeFlows[].threadFlows[].locations[].physicalLocation.artifactLocation.uri
  | (ingested by Endor Labs during scan)
API:  spec.dependency_file_paths[]
```

Additional corroborating fields (fetch via `endorctl api get --resource Finding`):
```
spec.explanation           -> Contains "Data Flow" table with Source/Propagation/Sink stages,
                              file paths, line numbers, and code snippets
spec.finding_metadata.custom.uri -> Points to the primary sink location (usually in the library)
spec.location_urls         -> Map of all involved files to source URLs
spec.finding_metadata.custom.code_snippet -> The vulnerable code at the sink
```

### Configuration: Define Your Boundaries

Before running the algorithm, define these project-specific values:

```pseudocode
# Path prefixes that identify application/service code (sources)
SERVICE_PREFIXES = ["services/", "apps/", ...]

# Path prefixes that identify shared libraries (sinks), mapped to language tags
LIB_PREFIX_TO_TAG = {
  "libs/common-java/":   "cross-repo-sast-java",
  "libs/common-go/":     "cross-repo-sast-go",
  "libs/common-python/": "cross-repo-sast-python",
  # Add more as needed for your project
}
```

These prefixes are determined by examining your monorepo's directory structure.

### Decision Algorithm for Monorepo

```pseudocode
FUNCTION is_cross_repo(finding, SERVICE_PREFIXES, LIB_PREFIX_TO_TAG):
  paths = finding.spec.dependency_file_paths

  has_service_path = ANY(
    ANY(path.startsWith(prefix) FOR prefix IN SERVICE_PREFIXES)
    FOR path IN paths
  )

  has_lib_path = ANY(
    ANY(path.startsWith(prefix) FOR prefix IN LIB_PREFIX_TO_TAG.keys())
    FOR path IN paths
  )

  RETURN has_service_path AND has_lib_path

FUNCTION determine_tags(finding, LIB_PREFIX_TO_TAG):
  tags = ["cross-repo-sast"]
  paths = finding.spec.dependency_file_paths

  FOR prefix, tag IN LIB_PREFIX_TO_TAG:
    IF ANY(path.startsWith(prefix) FOR path IN paths):
      tags.append(tag)

  RETURN tags
```

### Classification Examples

The following examples use a monorepo with `services/` and `libs/` prefixes:

**CROSS-REPO = TRUE:**
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
// REASONING: has_service_path=true (SearchController), has_lib_path=true (QueryBuilder)
// TAGS: ["cross-repo-sast", "cross-repo-sast-java"]
// DATA FLOW: HTTP param -> SearchController -> SearchService -> QueryBuilder -> raw SQL
```

**CROSS-REPO = TRUE (cross-language flow):**
```json
{
  "spec": {
    "dependency_file_paths": [
      "libs/common-java/src/main/java/com/example/query/QueryBuilder.java",
      "services/ml-service/app/main.py",
      "services/ml-service/app/services/data_service.py"
    ]
  }
}
// REASONING: has_service_path=true (Python service), has_lib_path=true (Java library)
// NOTE: Cross-LANGUAGE flow — SAST can detect these in monorepos
// TAGS: ["cross-repo-sast", "cross-repo-sast-java"]
```

**CROSS-REPO = FALSE (application-only):**
```json
{
  "spec": {
    "dependency_file_paths": [
      "services/api-gateway/src/main/java/com/example/controller/GatewayController.java",
      "services/api-gateway/src/main/java/com/example/service/GatewayService.java"
    ]
  }
}
// REASONING: has_service_path=true BUT has_lib_path=false -> NOT cross-repo
// Self-contained vulnerability within one application component
```

**CROSS-REPO = FALSE (library-only in monorepo):**
```json
{
  "spec": {
    "dependency_file_paths": [
      "libs/common-java/src/main/java/com/example/query/QueryBuilder.java"
    ]
  }
}
// REASONING: has_service_path=false -> NOT cross-repo
// Flags the sink in isolation; no application caller is traced
```

**CROSS-REPO = FALSE (excluded library path):**
```json
{
  "spec": {
    "dependency_file_paths": [
      "libs/vendor/third_party/sqlite-3.31.1/tool/loadfts.c"
    ]
  }
}
// REASONING: path is in libs/ but not in any LIB_PREFIX_TO_TAG key -> excluded
// Vendored/third-party code is typically not your cross-repo boundary
```

### Algorithm for Standalone Library Projects

When shared libraries are scanned as independent projects, their findings contain only paths relative to the library root (e.g., `src/main/java/.../QueryBuilder.java` rather than `libs/common-java/src/...`).

**Strategy A — Cross-reference with monorepo findings (recommended):**

```pseudocode
1. COLLECT all cross-repo findings from the monorepo (using algorithm above)
2. FOR EACH monorepo cross-repo finding:
   a. EXTRACT the library file path(s) from dependency_file_paths
   b. STRIP the library prefix to get the relative path
   c. EXTRACT the vulnerability type from meta.description
3. FOR EACH finding in the standalone library project:
   a. CHECK if dependency_file_paths contains the relative path from step 2b
   b. CHECK if meta.description matches the vulnerability type from step 2c
   c. IF both match -> tag this finding as cross-repo
```

**Strategy B — Known sink file matching:**

Identify which library files contain dangerous sinks by examining the codebase architecture or by using monorepo cross-repo findings as a guide. Then tag findings in the standalone library project whose `dependency_file_paths` reference those known sink files.

```pseudocode
# Determine these per-project by examining code and monorepo findings
KNOWN_SINKS = [
  "query/QueryBuilder.java",
  "http/HttpClient.java",
  "crypto/CryptoService.java",
  # ... etc
]

FUNCTION is_cross_repo_in_library(finding, KNOWN_SINKS):
  FOR path IN finding.spec.dependency_file_paths:
    FOR sink IN KNOWN_SINKS:
      IF path contains sink:
        RETURN true
  RETURN false
```

## Execution Procedure

```
1. AUTHENTICATE
   - Verify auth: endorctl api list --resource Project -n <ns> --page-size 1
   - If 403: re-run endorctl init --auth-mode=api-key
   - If endorctl not found: check PATH, try npx -y endorctl, or use full binary path

2. GET PROJECT UUIDS
   - endorctl api list --resource Project -n <ns> --field-mask "meta.name,uuid"
   - Store mapping: project_name -> uuid

3. DEFINE BOUNDARIES
   - Determine SERVICE_PREFIXES and LIB_PREFIX_TO_TAG for your project structure
   - If tagging standalone library projects, determine KNOWN_SINKS

4. FOR EACH PROJECT:
   a. QUERY all SAST findings using --list-all (DO NOT manually paginate):
      endorctl api list --resource Finding -n <ns> \
        --filter 'spec.finding_categories contains [FINDING_CATEGORY_SAST] and spec.project_uuid==<uuid>' \
        --list-all \
        --field-mask 'uuid,meta.name,meta.description,meta.tags,spec.dependency_file_paths,spec.level'
   
   b. IDENTIFY cross-repo findings using the algorithm above
   
   c. DETERMINE tags: ["cross-repo-sast", "cross-repo-sast-<lang>"]
   
   d. TEST one finding first:
      - Pick a single cross-repo finding and run the update command
      - VERIFY exit code == 0 AND response contains expected tags in meta.tags
      - Only proceed to batch if this succeeds
   
   e. FOR EACH remaining cross-repo finding:
      - READ existing meta.tags (from query result)
      - MERGE new tags with existing tags (dedup)
      - UPDATE (run in the SAME authenticated shell session, NOT via a detached script):
        endorctl api update --resource Finding -n <ns> \
          --uuid <uuid> \
          --field-mask 'meta.tags' \
          --data '{"meta":{"tags":["cross-repo-sast","cross-repo-sast-<lang>", ...existing...]}}'
      - VERIFY exit code == 0

5. VERIFY all tags applied:
   endorctl api list --resource Finding -n <ns> \
     --filter 'meta.tags contains ["cross-repo-sast"]' \
     --count
   Also verify per-language counts:
     --filter 'meta.tags contains ["cross-repo-sast-java"]' --count
     --filter 'meta.tags contains ["cross-repo-sast-go"]' --count
     --filter 'meta.tags contains ["cross-repo-sast-python"]' --count
```

### Critical Execution Constraints

1. **Always use `--list-all`** for querying findings. Manual pagination with `--page-id`/`--page-token` is fragile and error-prone (the flags are mutually exclusive).

2. **Always run `endorctl` in the authenticated shell session.** Running via a detached child process (e.g., `powershell -File script.ps1`) may lose the authentication context, causing updates to silently fail. Use inline loops in the same shell instead:
   ```powershell
   $uuids = @("uuid1","uuid2","uuid3")
   foreach ($u in $uuids) {
     endorctl api update --resource Finding -n <ns> --uuid $u --field-mask 'meta.tags' --data '{"meta":{"tags":["cross-repo-sast","cross-repo-sast-java"]}}' --output-type yaml 2>$null | Out-Null
     Write-Host "Tagged $u"
   }
   ```

3. **Never suppress stderr during debugging.** Only add `2>$null | Out-Null` after confirming commands succeed individually. Silent failures are the hardest to diagnose.

4. **Test one update before batching.** Always verify a single `endorctl api update` works and returns the expected tags before running a loop over dozens of findings.

## Error Handling

| Exit Code | Error Message | Cause | Fix |
|-----------|---------------|-------|-----|
| 3 | `invalid-args: at least one fieldmask should be given` | Missing `--field-mask` on update | Add `--field-mask 'meta.tags'` |
| 3 | `invalid-args: mask: proto: invalid path "..."` | Quoting failure — arguments merged | Use PowerShell with single quotes, not cmd.exe |
| 20 | `proto: syntax error ... invalid value \` | Backslash-escaped quotes in JSON | Use `'{"key":"val"}'` not `'{\"key\":\"val\"}'` |
| 3 | `403 Unauthorized request` | Wrong credentials or wrong namespace | Re-authenticate: `endorctl init --auth-mode=api-key` |
| 127 | `endorctl: command not found` | Binary not on PATH | Use full path, add to PATH, or use `npx -y endorctl` |
| 0 | Response missing expected tags | Field mask didn't include meta.tags, or data was malformed | Verify `--field-mask 'meta.tags'` and valid JSON in `--data` |
| 1 | `the flag --page-token cannot be given with --page-id` | Used both pagination flags together | Use `--list-all` instead, or use only `--page-id` for manual pagination |
| 0 | Tags not applied (silent failure in batch) | `endorctl` ran in a child process that lost auth context | Run updates in the same interactive shell where auth was established; don't use detached scripts |

## Rollback Procedure

To remove ALL cross-repo tags from ALL tagged findings:

```
1. LIST all tagged findings (use --list-all):
   endorctl api list --resource Finding -n <ns> \
     --filter 'meta.tags contains ["cross-repo-sast"]' \
     --field-mask 'uuid,meta.tags' --list-all

2. FOR EACH finding (run in the SAME authenticated shell):
   - Compute remaining_tags = existing_tags - {"cross-repo-sast", "cross-repo-sast-java", "cross-repo-sast-go", "cross-repo-sast-python"}
   - UPDATE with remaining_tags (or empty array if none left):
     endorctl api update --resource Finding -n <ns> \
       --uuid <uuid> \
       --field-mask 'meta.tags' \
       --data '{"meta":{"tags":[...remaining...]}}'

3. VERIFY rollback:
   endorctl api list --resource Finding -n <ns> \
     --filter 'meta.tags contains ["cross-repo-sast"]' --count
   Expected: { "count_response": { "count": 0 } }
```

## SARIF-to-API Field Mapping

Understanding how the SARIF output maps to Endor Labs API fields is essential for debugging or extending this workflow.

When Endor Labs runs AI SAST, it produces SARIF output. The platform ingests this SARIF and populates Finding objects. Here's how the key SARIF fields map:

```
SARIF FIELD                                              -> ENDOR LABS API FIELD
-----------------------------------------------------------------------------------------------
runs[].results[].ruleId (e.g. "CWE-89")                 -> spec.extra_key (contains CWE)
runs[].results[].level ("error"|"warning"|"note")        -> spec.level (CRITICAL|HIGH|MEDIUM|LOW)
runs[].results[].message.text                            -> spec.explanation (full analysis)
                                                            spec.finding_metadata.custom.message
runs[].results[].locations[0].physicalLocation
  .artifactLocation.uri                                  -> spec.finding_metadata.custom.uri
runs[].results[].codeFlows[].threadFlows[]
  .locations[].physicalLocation.artifactLocation.uri     -> spec.dependency_file_paths[]
runs[].results[].properties.tags                         -> spec.finding_metadata.custom.sast_tags
runs[].results[].properties.cweIds                       -> spec.finding_metadata.custom.cwes[]
runs[].tool.driver.name                                  -> spec.method
```

The critical mapping for cross-repo detection:
```
SARIF codeFlows -> API spec.dependency_file_paths
```

The SARIF `codeFlows` section contains `threadFlows` with ordered `locations` showing how tainted data propagates. Each location has a file URI. Endor Labs extracts all unique file URIs from the thread flow and stores them as `spec.dependency_file_paths`. This is the field we inspect to determine if the finding crosses the application/library boundary.

## Data Model Reference

```
Finding {
  uuid: string                          # Unique identifier
  meta: {
    name: string                        # e.g. "ai_sast_with_critical_finding"
    description: string                 # e.g. "SQL Injection"
    tags: string[]                      # CUSTOM TAGS — this is what we set
    create_time: timestamp
    update_time: timestamp
  }
  spec: {
    finding_categories: enum[]          # e.g. [FINDING_CATEGORY_SAST]
    finding_tags: enum[]                # SYSTEM TAGS — read-only, e.g. FINDING_TAGS_AI
    level: enum                         # FINDING_LEVEL_CRITICAL|HIGH|MEDIUM|LOW
    project_uuid: string                # Links to Project
    dependency_file_paths: string[]     # Files involved in the finding
    summary: string                     # Short description
    explanation: string                 # Full analysis with data flow
    source_code_version: {
      ref: string                       # Branch
      sha: string                       # Commit hash
    }
  }
  tenant_meta: {
    namespace: string                   # e.g. "auri"
  }
}
```

---

## Appendix: Death-Star Demo Project Reference

The following data is specific to the "Death Star Operations Platform" demo monorepo (namespace: `auri`) and is provided as a concrete worked example.

### Project Configuration

| Project | UUID |
|---------|------|
| death-star | `69d31cfb4d93d8d6a8408210` |
| imperial-common-java | `69d09687ac1c33ece6baabdf` |
| imperial-common-go | `69d09687edd655592b0fe0fc` |
| imperial-common-py | `69d096876de301718c19fec4` |

### Boundary Configuration

```pseudocode
SERVICE_PREFIXES = ["services/"]

LIB_PREFIX_TO_TAG = {
  "libs/imperial-common-java/": "cross-repo-sast-java",
  "libs/imperial-common-go/":   "cross-repo-sast-go",
  "libs/imperial-common-py/":   "cross-repo-sast-python",
}
```

Directory structure:
```
services/              -> 9 microservices (Java, Go, Python, Node.js, C#, React)
  imperial-gateway/
  weapons-control/
  crew-management/
  supply-chain/
  docking-bay/
  targeting-ai/
  comms-relay/
  life-support/
  command-center/
libs/                  -> 4 shared libraries
  imperial-common-java/
  imperial-common-go/
  imperial-common-py/
  security-core/         (C/C++ third-party — excluded from tagging)
```

### Known Sink Files (Strategy B)

```
JAVA_SINKS = [
  "query/QueryBuilder.java",
  "http/ImperialHttpClient.java",
  "crypto/ImperialCrypto.java",
  "codec/DataSerializer.java",
  "audit/AuditLogger.java",
  "config/ConfigLoader.java"
]

GO_SINKS = [
  "pkg/query/builder.go",
  "pkg/http/client.go",
  "pkg/crypto/crypto.go",
  "pkg/config/loader.go",
  "pkg/audit/logger.go"
]

PYTHON_SINKS = [
  "query/query_builder.py",
  "http/imperial_client.py",
  "crypto/imperial_crypto.py",
  "config/config_loader.py",
  "audit/audit_logger.py"
]
```

### Death-Star Cross-Repo Findings (9 total)

| UUID | Vuln Type | Severity | Service(s) | Library Sink | Lang Tag |
|------|-----------|----------|------------|-------------|----------|
| `69d35cf84d93d8d6a854525a` | SQL Injection (CWE-89) | CRITICAL | imperial-gateway, supply-chain | QueryBuilder.searchRecords | java |
| `69d35cf84d93d8d6a8545288` | SQL Injection (CWE-89) | CRITICAL | targeting-ai | QueryBuilder | java |
| `69d35cf85525eedabe945eb6` | SQL Injection (CWE-89) | CRITICAL | imperial-gateway | QueryBuilder.searchRecords | java |
| `69d35cf84d93d8d6a85452b1` | Broken Crypto (CWE-327) | HIGH | imperial-gateway | ImperialCrypto.encrypt | java |
| `69d35cf85525eedabe945eb9` | Broken Crypto (CWE-327) | HIGH | imperial-gateway | ImperialCrypto.fingerprint | java |
| `69d35cf84d93d8d6a85452b5` | SSRF (CWE-918) | HIGH | supply-chain | ImperialHttpClient.fetch | java |
| `69d35cf85525eedabe945ece` | SSRF (CWE-918) | CRITICAL | weapons-control | imperial-common-go client.go | go |
| `69d35cf85525eedabe945efd` | XXE (CWE-611) | HIGH | imperial-gateway | ConfigLoader.loadConfig | java |
| `69d35cf859970cc319e04106` | Deserialization (CWE-502) | CRITICAL | imperial-gateway | DataSerializer.deserialize | java |

### Verified Tag Counts

| Tag | Count | Breakdown |
|-----|-------|-----------|
| `cross-repo-sast` | **58** | All cross-repo findings across all 4 projects |
| `cross-repo-sast-java` | **26** | 8 death-star + 18 imperial-common-java |
| `cross-repo-sast-go` | **14** | 1 death-star + 13 imperial-common-go |
| `cross-repo-sast-python` | **18** | 18 imperial-common-py |

Strategy B was used for all standalone library projects. It worked because every SAST finding in these libraries was located in a known cross-repo sink file.
