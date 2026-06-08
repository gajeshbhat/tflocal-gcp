# 1. Use Python for the wrapper

- Status: Accepted
- Date: 2026-06-06

## Context

`tflocal-gcp` is the GCP analog of LocalStack's `terraform-local`, which is
written in Python. The wrapper must parse Terraform HCL, generate an override
file, and exec the `terraform` CLI. localgcp itself is written in Go, so a Go
wrapper (or a `localgcp` subcommand) was also considered.

## Decision

Implement the wrapper in **Python**.

- Faithful 1:1 port of the proven `terraform-local` design.
- `python-hcl2` gives reliable HCL parsing with no custom parser.
- `pipx` / `pip` distribution is simple and cross-platform.
- The wrapper only shells out to `terraform`; runtime performance is irrelevant.

## Consequences

- Different language from localgcp (Go); the two ship and version separately.
- Requires a Python runtime on the user's machine.
- Cross-platform behaviour is handled via `pathlib`/`subprocess` and a
  `[project.scripts]` entry point (no batch shims).
