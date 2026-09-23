# Cloudability API v3 — Postman Collection

**Version:** 2.0.2  
**Date:** 9-18-2026  
**Authors:** Brad Giles (brad.giles@ibm.com) · IBM Bob (AI Assistant)

---

## File Descriptions

| File | Purpose |
|---|---|
| `Cloudability API Collection v2.0.2 9-18-2026.postman_collection.json` | **Primary collection** Full documentation, some test scripts and Postman visualizers |
| `Cloudability API Environment v2.0.2 9-18-2026.postman_environment.json` | **Environment file.** Contains variables for credentials, resource IDs, cloud account IDs, and filters. Import alongside the collection and fill in credentials before running calls. |

> ⚠️ **Security:** Do not commit the environment file to source control since it could contain credentials. Each user should fill in their own credentials after importing.

---

## Feature List

### Collection Structure 

| Section | Calls | Notes |
|---|---|---|
| 000 Authentication | 3 | Frontdoor OpenToken flow; API key guide; `skip_auto_auth` support |
| 050 Credentialing | 12 | AWS (5), Azure (3), GCP (4 incl. GCP Setup Summary workflow) |
| 100 Business Mappings | 5 | Full CRUD |
| 150 Business Metrics | 5 | Uses `/v3/internal/` path — internal API warning included |
| 200 Account Groups & Entries | 8 | 2 sub-folders; size and batching recommendations included |
| 300 Users | 4 | Create + Delete with SSO/SAML organization warnings |
| 400 Views | 5 | Includes Get View by ID |
| 500 Forecast | 2 | |
| 600 Budgets | 9 | 2 sub-folders (Budgets + Subscriptions); alert threshold behavior documented |
| 700 Cost Reporting | 12 | Full filter operators table (12 operators); 20+ dimensions reference; visualizers on 7 calls |
| 800 Rightsizing | 18 | 5 sub-folders: AWS (8), Azure (3), GCP (4), Containers (3), Examples (4) |

### Documentation

Every folder and every call includes:
- What the call does and when to use it
- Required headers with example values
- All query parameters with descriptions, types, and example values
- Request body fields (POST/PUT) with types and required/optional flags
- Usage notes, caveats, and cross-references between related calls
- Links to IBM documentation (require Frontdoor/w3id browser access)

### Pre-Request Auto-Authentication Script

A collection-level pre-request script runs before every call:
- Checks `token_expires_at` before each call — re-authenticates automatically when the token is expired
- Posts to `https://frontdoor.apptio.com/api/auth/token` for a fresh token
- Auto-sets `apptio-current-environment` on first successful auth (calls `GET /api/environments`)
- Supports `skip_auto_auth=true` environment variable to bypass auto-auth entirely
- All `[Auth]` log messages visible in the Postman Console

### Test Scripts and Environment Variable Capture

Test scripts on multiple calls that:
- Validate HTTP status codes
- Validate response shape (arrays, required fields present)
- Auto-capture key IDs into environment variables for use in subsequent calls:

### Example Responses

Inline example responses on priority calls using realistic anonymized data that matches the actual API response shape:
- 000 Authentication 
- 050 Credentialing — AWS, Azure, GCP
- 600 Budgets 
- 700 Cost Reporting 
- 800 Rightsizing — Examples sub-folder 

---

## Known Limitations

**LIM-1 — IBM docs links require authenticated access**  
All reference links in the collection use `ibm.com/docs` URLs which require browser + IBM Frontdoor SSO. They return 403 from scripts. The public `developer.ibm.com/apis/catalog` is accessible without auth but does not contain the same detailed endpoint documentation.

**LIM-2 — Business Metrics use an internal API path**  
Section 150 Business Metrics calls `/v3/internal/business-mappings/metrics` which is not in the public IBM docs. It works with a valid API key but may change without notice. A warning is included in the 150 folder description.

**LIM-3 — Enqueue job status field names unverified**  
The Check Enqueue Job Status call (700 Cost Reporting) documents status values as `pending` / `processing` / `complete` / `failed`. These are derived from IBM docs and general API patterns. 

**LIM-4 — Container Workloads field name assumptions**  
The Container Workloads visualizer assumes specific response field names (`clusterName`, `currentCpuRequest`, etc.). Real field names should be verified against a live response. 

---

## Quick Start

See guidance embedded in the Collection documentation
