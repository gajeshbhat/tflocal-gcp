# Architecture Decision Records

Short, append-only records of significant decisions. They are the project's
durable memory: read them before revisiting a settled choice.

- One file per decision, numbered sequentially (`NNNN-title.md`).
- Format: Context, Decision, Consequences. Keep it crisp.
- Never edit a decision's intent after acceptance; supersede it with a new ADR.

## Index

- [0001](0001-language-python.md) — Use Python for the wrapper
- [0002](0002-license-mit.md) — License under MIT
- [0003](0003-src-layout.md) — Adopt the src/ layout
- [0004](0004-gcs-backend.md) — Redirect the gcs backend via STORAGE_EMULATOR_HOST
- [0005](0005-pypi-trusted-publishing.md) — Publish to PyPI via trusted publishing on tags
