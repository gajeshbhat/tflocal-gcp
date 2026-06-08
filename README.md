# tflocal-gcp — Terraform with localgcp

`tflocal-gcp` is a thin wrapper around the `terraform` CLI that runs your
Terraform against [localgcp](https://github.com/slokam-ai/localgcp), the local
GCP emulator. It is the GCP analog of LocalStack's
[`terraform-local`](https://github.com/localstack/terraform-local).

Run `terraform` against a local Google Cloud — no credentials, no cloud bill,
offline-friendly — **without editing your `.tf` files**.

> Status: early. Core override + `terraform` exec works; Cloud Storage is the
> first verified service, others are best-effort. See the service table below.

## How it works

`tflocal-gcp` uses Terraform's override mechanism. For each run it writes a
temporary `localgcp_providers_override.tf` that points the `google` /
`google-beta` provider at localgcp's endpoints (via `<service>_custom_endpoint`
attributes) and sets a dummy `access_token` to bypass Google credential lookup.
It then execs `terraform` with your arguments and deletes the override file on
exit. Your own configuration is never modified and stays cloud-ready.

## Prerequisites

- Python >= 3.9
- `terraform`
- [localgcp](https://github.com/slokam-ai/localgcp)

## Installation

```bash
pipx install tflocal-gcp   # recommended
# or
pip install tflocal-gcp
```

## Usage

`tflocal-gcp` takes the same arguments as `terraform`:

```bash
localgcp up                # start the emulator
tflocal-gcp init
tflocal-gcp apply
```

See [`example/`](example/) for a runnable Cloud Storage sample.

## Service support

localgcp's emulators are mostly gRPC data-plane, while the Terraform Google
provider speaks REST control-plane. Cloud Storage is verified end-to-end; the
rest are wired up but best-effort.

| Service        | Provider attribute             | Port | Status       |
| -------------- | ------------------------------ | ---- | ------------ |
| Cloud Storage  | `storage_custom_endpoint`      | 4443 | verified     |
| Pub/Sub        | `pubsub_custom_endpoint`       | 8085 | experimental |
| Secret Manager | `secret_manager_custom_endpoint` | 8086 | experimental |
| Firestore      | `firestore_custom_endpoint`    | 8088 | experimental |
| Cloud Tasks    | `cloud_tasks_custom_endpoint`  | 8089 | experimental |
| Vertex AI      | `vertex_ai_custom_endpoint`    | 8090 | experimental |
| Cloud KMS      | `kms_custom_endpoint`          | 8091 | experimental |
| Cloud Logging  | `logging_custom_endpoint`      | 8092 | experimental |
| Cloud Run      | `cloud_run_v2_custom_endpoint` | 8093 | experimental |
| BigQuery       | `big_query_custom_endpoint`    | 9060 | experimental |
| Spanner        | `spanner_custom_endpoint`      | 9010 | experimental |
| Bigtable       | `bigtable_custom_endpoint`     | 9094 | experimental |

## Remote state (gcs backend)

If your config uses a `gcs` backend, `tflocal-gcp` points it at localgcp's
Cloud Storage emulator by setting `STORAGE_EMULATOR_HOST` (plus a dummy token)
for the `terraform` subprocess. On `init` the state bucket is created
automatically if it does not yet exist. Your `backend` block stays
cloud-ready and unmodified.

```hcl
terraform {
  backend "gcs" {
    bucket = "tf-state"
  }
}
```

## Configuration

| Variable | Description |
| -------- | ----------- |
| `DRY_RUN` | Write the override file without invoking Terraform |
| `TF_CMD`  | Terraform command to call (default: `terraform`) |
| `LOCALGCP_HOST` | Host serving the localgcp endpoints (default: `localhost`) |
| `LOCALGCP_PORT_<SERVICE>` | Override a service port, e.g. `LOCALGCP_PORT_STORAGE=4443` |

## Development

```bash
make install   # editable install with dev extras
make test      # run tests
make lint      # ruff check
make format    # ruff format + autofix
make e2e       # end-to-end test against a running localgcp
make dist      # build the sdist and wheel into dist/
```

`make e2e` is opt-in: it needs both `localgcp` and `terraform` on your `PATH`.
It starts the emulator, runs `init`/`apply` against [`example/`](example/),
checks the bucket was created, then destroys it.

Project conventions and architecture live in [`AGENTS.md`](AGENTS.md);
decisions are recorded in [`docs/adr/`](docs/adr/).

## Releasing

Pushing a `vX.Y.Z` tag triggers the release workflow, which builds the
distributions and publishes them to PyPI via
[trusted publishing](https://docs.pypi.org/trusted-publishers/) (no API tokens).
The tag must match the `version` in `pyproject.toml`. See the
[`release`](.claude/skills/release/SKILL.md) skill for the full checklist.

## Change Log

- **0.1.0** — Initial release: provider override generation, `terraform`
  execution and cleanup, per-service endpoint map (Cloud Storage verified),
  `LOCALGCP_HOST` / `LOCALGCP_PORT_<SERVICE>` overrides, and `gcs` backend
  redirection with automatic state-bucket creation.

## License

[MIT](LICENSE).
