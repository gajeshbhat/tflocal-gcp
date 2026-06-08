# 4. Redirect the gcs backend via STORAGE_EMULATOR_HOST

- Status: Accepted
- Date: 2026-06-06

## Context

The provider override file only redirects the `google` / `google-beta`
*providers*. Terraform's `backend "gcs"` block runs earlier (during `init`,
before providers load) and uses its own embedded storage client, so a custom
endpoint in the override file does not affect it. We still want remote state to
land in localgcp's Cloud Storage emulator without the user editing their
`backend` block or supplying real credentials.

## Decision

Detect a `backend "gcs"` block in the parsed `*.tf` files and, when present,
inject two environment variables into the `terraform` subprocess:

- `STORAGE_EMULATOR_HOST` — points the backend's storage client at localgcp and
  makes it skip Google credential discovery.
- `GOOGLE_OAUTH_ACCESS_TOKEN` — the same dummy token used in the override file.

On `init` we also bootstrap the state bucket: a `GET` against the GCS JSON API
checks for existence, and a `POST` creates it if missing. This lives in
`backend.py` (`backend_env`, `ensure_state_bucket`) and is wired into
`cli.main`.

## Consequences

- Remote state works against localgcp with an unmodified `gcs` backend block.
- The bucket is created automatically, matching the zero-setup experience of the
  rest of the tool.
- Bootstrap failures (localgcp unreachable, non-404 errors) warn but never abort
  the run, so the behaviour degrades gracefully.
- The env vars are scoped to the subprocess and only set when a `gcs` backend is
  actually present, leaving non-backend runs untouched.
