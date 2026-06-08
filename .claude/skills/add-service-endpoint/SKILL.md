---
name: add-service-endpoint
description: Add support for a new GCP service to tflocal-gcp by wiring its localgcp port to the matching Terraform google provider custom endpoint. Use when extending service coverage.
---

# Add a service endpoint

Steps to add a new GCP service to the override map.

1. Confirm the localgcp port and protocol for the service in the localgcp
   README (the `Service / Protocol / Port` table).
2. Find the matching Terraform google provider attribute, named
   `<service>_custom_endpoint` (e.g. `pubsub_custom_endpoint`). Verify it exists
   in the provider reference.
3. Add a `ServiceEndpoint` entry to `SERVICE_ENDPOINTS` in
   `src/tflocal_gcp/endpoints.py`:
   - `service`: localgcp service key
   - `provider_attr`: the `<service>_custom_endpoint` name
   - `port`: localgcp port
   - `path`: URL path including the API version and trailing slash
   - `status`: `verified` only if tested end-to-end against localgcp; otherwise
     `experimental`.
4. Add or update a unit test in `tests/test_endpoints.py` asserting the rendered
   URL for the new entry.
5. Update the service table in `README.md`.
6. Run `make format && make test`.

## Rules

- Default to `experimental`. Promote to `verified` only with a passing
  end-to-end check against a running localgcp.
- Do not invent provider attributes; confirm the exact name first.
