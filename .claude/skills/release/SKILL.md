---
name: release
description: Cut a new tflocal-gcp release - bump the version, update the changelog, tag, and publish to PyPI. Use when shipping a new version.
---

# Release checklist

1. Ensure `main` is green: `make lint && make test` (and `make e2e` if able).
2. Bump `version` in `pyproject.toml` (semver).
3. Update `__version__` in `src/tflocal_gcp/__init__.py` to match.
4. Add a Change Log entry in `README.md` with a one-line summary.
5. Optionally sanity-check the build locally: `make dist`.
6. Commit: `chore: release vX.Y.Z`.
7. Tag and push: `git tag vX.Y.Z && git push --tags`.

The `vX.Y.Z` tag triggers `.github/workflows/release.yml`, which builds the
distributions, publishes them to PyPI via trusted publishing (OIDC, no tokens),
and creates the GitHub release with auto-generated notes.

## Rules

- The `pyproject.toml` version and `__version__` must always match.
- The tag (`vX.Y.Z`) must match the `pyproject.toml` version.
- Never tag a dirty or failing tree.
- Publishing runs automatically from the tag; only push the tag with explicit
  maintainer approval. PyPI must be configured as a trusted publisher for the
  repo, and the `pypi` environment must exist in the repo settings.
