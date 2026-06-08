# Contributing to tflocal-gcp

Thanks for your interest. This doc covers the full contribution workflow.

## Quick start

```bash
brew install uv                    # one-time
git clone https://github.com/gajeshbhat/tflocal-gcp
cd tflocal-gcp
make venv && make install          # creates .venv + editable install
make lint && make test             # verify the baseline
```

For the end-to-end test you also need `localgcp` and `terraform` on your PATH:

```bash
brew install slokam-ai/tap/localgcp
brew install hashicorp/tap/terraform
make e2e
```

## Making changes

1. Fork the repo and create a branch: `git checkout -b your-feature`.
2. Keep commits small and focused.
3. Follow the conventions in [`AGENTS.md`](AGENTS.md): small pure functions,
   no shell built-ins, cross-platform (`pathlib`, `subprocess`).
4. Sign every commit (see [Signing your commits](#signing-your-commits)).
5. Run `make lint && make test` before pushing. A failing tree won't be merged.
6. Open a PR against `main` and fill in the PR template.

## Signing your commits

All commits **must be cryptographically signed**. The `main` branch enforces
"Require signed commits", so unsigned commits are rejected and unsigned PRs
cannot be merged. Each commit must show as **Verified** on GitHub.

Set up signing once (SSH keys are the simplest; GPG also works):

```bash
# SSH signing (Git >= 2.34)
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true

# or GPG signing
git config --global user.signingkey <your-gpg-key-id>
git config --global commit.gpgsign true
```

Then add the **same** public key to your GitHub account as a *Signing key*
(Settings -> SSH and GPG keys), and use a verified email. With
`commit.gpgsign true` every `git commit` is signed automatically; otherwise sign
per-commit with `git commit -S`. Verify locally with `git log --show-signature`.

## Sign-off (DCO)

In addition to a cryptographic signature, every commit must carry a
`Signed-off-by` trailer certifying the [Developer Certificate of
Origin](https://developercertificate.org/). The **DCO** CI check
(`.github/workflows/dco.yml`) fails any PR with a commit that lacks it.

Add the trailer automatically with `-s`:

```bash
git commit -s -m "feat: add Spanner endpoint (experimental)"
# combine signing + sign-off:
git commit -S -s -m "..."
```

This appends `Signed-off-by: Your Name <you@example.com>` using your
`git config user.name` / `user.email`. To add it to existing commits on a
branch, run `git rebase --signoff <base>`.

## Adding a service endpoint

Follow the skill at [`.claude/skills/add-service-endpoint/SKILL.md`](.claude/skills/add-service-endpoint/SKILL.md).
In brief:

1. Add a `ServiceEndpoint` entry to `SERVICE_ENDPOINTS` in `endpoints.py`.
2. Mark it `verified` only if you have tested it end-to-end against localgcp;
   otherwise `experimental`.
3. Add a test row to `tests/test_endpoints.py`.
4. Add a row to the service table in `README.md`.

## Commit style

Use the [Conventional Commits](https://www.conventionalcommits.org) format:

```
feat: add Bigtable endpoint (experimental, port 9094)
fix: clean up override file when terraform is missing
chore: release v0.2.0
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`.

## Architecture decisions

For significant decisions (new module, change in how overrides work, new
transport mechanism) add an ADR in `docs/adr/` and update `docs/adr/README.md`.
See existing ADRs for the format.

## Releasing

Maintainers only — see [`.claude/skills/release/SKILL.md`](.claude/skills/release/SKILL.md).

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
