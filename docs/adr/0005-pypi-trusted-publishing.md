# 5. Publish to PyPI via trusted publishing on tags

- Status: Accepted
- Date: 2026-06-06

## Context

We need a release pipeline that ships `tflocal-gcp` to PyPI. The traditional
approach uploads with `twine` using a long-lived API token stored as a CI
secret. Tokens leak, expire, and need rotation. PyPI now supports
[trusted publishing](https://docs.pypi.org/trusted-publishers/), where a GitHub
Actions workflow authenticates via short-lived OIDC credentials and no token is
stored anywhere.

## Decision

Release on a `vX.Y.Z` tag push via `.github/workflows/release.yml`:

1. Build the sdist and wheel with `python -m build`.
2. Publish to PyPI with `pypa/gh-action-pypi-publish` using OIDC
   (`id-token: write`), scoped to a `pypi` GitHub environment.
3. Create a GitHub release from the tag with auto-generated notes.

The tag must match the `version` in `pyproject.toml` (and `__version__`).

## Consequences

- No PyPI API token is stored in the repository; auth is short-lived per run.
- A one-time setup is required: register the repo + workflow as a trusted
  publisher on PyPI and create the `pypi` environment in repo settings.
- Releases are reproducible from a tag and require no local credentials.
- The `release` skill documents the human steps (bump, changelog, tag); the
  workflow owns build and publish.
