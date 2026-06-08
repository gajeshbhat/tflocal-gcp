# Example: Cloud Storage bucket on localgcp

A minimal Terraform config that creates a Cloud Storage bucket against a local
[localgcp](https://github.com/slokam-ai/localgcp) instance.

## Run it

```bash
# 1. Start the emulator (Cloud Storage on :4443)
localgcp up

# 2. From this directory, run Terraform via the wrapper
tflocal-gcp init
tflocal-gcp apply
```

The bucket is created in localgcp, not in real GCP. `main.tf` is never modified:
`tflocal-gcp` writes a temporary `localgcp_providers_override.tf` for the run and
deletes it afterwards.

To preview the generated override without running Terraform:

```bash
DRY_RUN=1 tflocal-gcp apply
```
