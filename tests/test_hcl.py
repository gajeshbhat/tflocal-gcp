"""Tests for parsing *.tf files into providers and backend config."""

from tflocal_gcp.hcl import (
    find_gcs_backend,
    find_google_providers,
    parse_tf_files,
)

_CONFIG = """
terraform {
  required_providers {
    google = { source = "hashicorp/google" }
  }
  backend "gcs" {
    bucket = "tf-state"
    prefix = "env/x"
  }
}

provider "google" {
  project = "local-project"
}

provider "google" {
  alias   = "eu"
  project = "p2"
}

provider "google-beta" {
  project = "p3"
}

provider "aws" {
  region = "us-east-1"
}
"""


def _write(tmp_path, body, name="main.tf"):
    (tmp_path / name).write_text(body)
    return parse_tf_files(str(tmp_path))


def test_parse_skips_unparseable_files(tmp_path, capsys):
    (tmp_path / "bad.tf").write_text('provider "google" {')
    parsed = parse_tf_files(str(tmp_path))
    assert parsed == {}
    assert "could not parse" in capsys.readouterr().err


def test_find_google_providers_includes_aliases(tmp_path):
    providers = find_google_providers(_write(tmp_path, _CONFIG))
    assert {"type": "google", "alias": None} in providers
    assert {"type": "google", "alias": "eu"} in providers
    assert {"type": "google-beta", "alias": None} in providers


def test_find_google_providers_excludes_other_providers(tmp_path):
    providers = find_google_providers(_write(tmp_path, _CONFIG))
    assert all(p["type"] in ("google", "google-beta") for p in providers)
    assert len(providers) == 3


def test_find_google_providers_empty_when_none(tmp_path):
    body = 'provider "aws" { region = "us-east-1" }\n'
    assert find_google_providers(_write(tmp_path, body)) == []


def test_find_gcs_backend(tmp_path):
    backend = find_gcs_backend(_write(tmp_path, _CONFIG))
    assert backend is not None
    assert backend["bucket"] == '"tf-state"'


def test_find_gcs_backend_absent(tmp_path):
    body = 'provider "google" { project = "p" }\n'
    assert find_gcs_backend(_write(tmp_path, body)) is None
