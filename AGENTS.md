# AGENTS.md

Primary source of truth for humans and AI agents working on this repository.
Tool-specific files (`CLAUDE.md`, `.github/copilot-instructions.md`,
`.cursor/rules/project.mdc`) all defer to this document.

## What this project is

`tflocal-gcp` is a thin wrapper around the `terraform` CLI that runs Terraform
against [localgcp](https://github.com/slokam-ai/localgcp), the local GCP
emulator. It is the GCP analog of LocalStack's `terraform-local` (`tflocal`).

It works by generating a temporary Terraform **override file**
(`localgcp_providers_override.tf`) that points the `google` / `google-beta`
provider at localgcp's local endpoints, runs the requested `terraform` command,
then deletes the override file. The user's own `.tf` files are never modified
and stay cloud-ready.

## How it works

1. Parse the local `*.tf` files (HCL) to discover `google` / `google-beta`
   providers and their aliases.
2. Build a service -> custom-endpoint map from `endpoints.py`, pointing each
   supported service at the matching localgcp port.
3. Write `localgcp_providers_override.tf` with `<service>_custom_endpoint`
   attributes plus a dummy `access_token` (bypasses Google credential lookup).
4. Exec `terraform <args>` as a subprocess, forwarding signals.
5. Always clean up the override file on exit.

## Architecture (module map)

- `src/tflocal_gcp/cli.py` — entry point (`main`): arg handling, orchestration,
  subprocess exec, cleanup.
- `src/tflocal_gcp/endpoints.py` — the `service -> (provider attr, port, path,
  status)` map and URL rendering. Single place to add a new service.
- `src/tflocal_gcp/overrides.py` — generate / write / clean up the override file.
- `src/tflocal_gcp/hcl.py` — parse `*.tf`, extract providers, aliases, backend.
- `src/tflocal_gcp/backend.py` — point the `gcs` backend at localgcp
  (`STORAGE_EMULATOR_HOST` + dummy token) and bootstrap the state bucket on `init`.

## Conventions

- Python, modern `src/` layout. Target Python >= 3.9, cross-platform
  (macOS primary; Linux + Windows verified in CI).
- Cross-platform code only: use `pathlib`/`os.path`, `subprocess`; no shell
  built-ins, no `.bat` shims (entry point via `[project.scripts]`).
- Lint/format with `ruff`. Keep functions small and pure where possible.
- Comments match surrounding density. No verbose, explanatory filler.
- Distribution name and CLI command are both `tflocal-gcp`; import package is
  `tflocal_gcp`.

## Service support policy

Service endpoints are marked `verified` or `experimental` in `endpoints.py`.
Only Cloud Storage is `verified` today (REST on `:4443`, plus the `gcs`
backend). Everything else is best-effort because localgcp's other emulators are
gRPC data-plane while the Terraform provider speaks REST control-plane. Be
honest about this in docs; do not claim coverage we have not tested.

## Build, test, lint

```bash
make install   # pip install -e ".[dev]"
make test      # pytest
make lint      # ruff check
make format    # ruff format + --fix
```

## Scope rules for agents

- Do exactly what is asked; do not create unrequested files or docs.
- Prefer editing existing files over adding new ones.
- After changing a public API, update all call sites and tests.
- Record significant decisions as an ADR in `docs/adr/`.
- Reusable procedures live as Claude skills in `.claude/skills/`.
