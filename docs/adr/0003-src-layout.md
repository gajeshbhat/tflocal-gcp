# 3. Adopt the src/ layout

- Status: Accepted
- Date: 2026-06-06

## Context

`terraform-local` uses a flat `bin/` layout with raw scripts on `PATH` plus a
`.bat` shim for Windows. We want a clean, cross-platform package.

## Decision

Use the modern **`src/` layout** with the importable package at
`src/tflocal_gcp/` and a console entry point declared under
`[project.scripts]` (`tflocal-gcp = "tflocal_gcp.cli:main"`).

## Consequences

- Tests run against the installed package, catching packaging errors early.
- No accidental imports from the working directory.
- The entry point yields a correct launcher on every OS, so no `.bat` shim is
  needed.
- Build backend is `hatchling`, configured to package `src/tflocal_gcp`.
