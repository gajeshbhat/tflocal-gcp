# Security Policy

## Supported versions

Only the latest release receives security fixes. Patch the version in
`pyproject.toml`, tag, and publish.

## Reporting a vulnerability

**Do not open a public issue for security vulnerabilities.**

Report privately via
[GitHub Security Advisories](https://github.com/gajeshbhat/tflocal-gcp/security/advisories/new).

Please include:
- A description of the vulnerability and its potential impact.
- Steps to reproduce or a minimal proof-of-concept.
- Any suggested remediation, if you have one.

You will receive a response within **5 business days**. We aim to release a fix
within **14 days** of confirmation.

## Scope

This tool runs locally against the [localgcp](https://github.com/slokam-ai/localgcp)
emulator. It is **not** intended for use against real GCP environments or in
production pipelines. The dummy `access_token` it injects is intentionally
insecure and must never be used outside of local development.
