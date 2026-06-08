"""Tests for the CLI entry point."""

import tflocal_gcp
from tflocal_gcp import cli
from tflocal_gcp.cli import main
from tflocal_gcp.overrides import OVERRIDE_FILENAME

_TF = 'provider "google" { project = "p" }\n'

_TF_GCS = """
terraform {
  backend "gcs" {
    bucket = "tf-state"
  }
}
provider "google" { project = "p" }
"""


def test_version_flag(capsys):
    code = main(["--version"])
    captured = capsys.readouterr()
    assert code == 0
    assert tflocal_gcp.__version__ in captured.out


def test_dry_run_writes_override_and_skips_terraform(tmp_path, monkeypatch):
    (tmp_path / "main.tf").write_text(_TF)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DRY_RUN", "1")

    code = main(["plan"])

    assert code == 0
    assert (tmp_path / OVERRIDE_FILENAME).is_file()


def test_run_invokes_terraform_and_cleans_up(tmp_path, monkeypatch):
    (tmp_path / "main.tf").write_text(_TF)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DRY_RUN", raising=False)

    calls = []

    class _Result:
        returncode = 0

    def fake_run(cmd, *args, **kwargs):
        calls.append(cmd)
        assert (tmp_path / OVERRIDE_FILENAME).is_file()  # exists during the run
        return _Result()

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    code = main(["apply", "-auto-approve"])

    assert code == 0
    assert calls and calls[0][1:] == ["apply", "-auto-approve"]
    assert not (tmp_path / OVERRIDE_FILENAME).exists()  # cleaned up after


def test_missing_terraform_returns_127(tmp_path, monkeypatch):
    (tmp_path / "main.tf").write_text(_TF)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DRY_RUN", raising=False)

    def fake_run(cmd, *args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    code = main(["plan"])

    assert code == 127
    assert not (tmp_path / OVERRIDE_FILENAME).exists()


def test_no_backend_env_without_gcs_backend(tmp_path, monkeypatch):
    (tmp_path / "main.tf").write_text(_TF)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DRY_RUN", raising=False)

    captured = {}

    class _Result:
        returncode = 0

    def fake_run(cmd, *args, **kwargs):
        captured["env"] = kwargs.get("env")
        return _Result()

    monkeypatch.setattr(cli.subprocess, "run", fake_run)
    main(["plan"])

    assert "STORAGE_EMULATOR_HOST" not in captured["env"]


def test_gcs_backend_injects_env_and_bootstraps_bucket(tmp_path, monkeypatch):
    (tmp_path / "main.tf").write_text(_TF_GCS)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DRY_RUN", raising=False)

    bootstrapped = []
    monkeypatch.setattr(
        cli, "ensure_state_bucket", lambda cfg, host: bootstrapped.append(cfg)
    )

    captured = {}

    class _Result:
        returncode = 0

    def fake_run(cmd, *args, **kwargs):
        captured["env"] = kwargs.get("env")
        return _Result()

    monkeypatch.setattr(cli.subprocess, "run", fake_run)
    main(["init"])

    assert captured["env"]["STORAGE_EMULATOR_HOST"] == "localhost:4443"
    assert bootstrapped, "state bucket should be bootstrapped on init"


def test_gcs_backend_does_not_bootstrap_on_plan(tmp_path, monkeypatch):
    (tmp_path / "main.tf").write_text(_TF_GCS)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DRY_RUN", raising=False)

    bootstrapped = []
    monkeypatch.setattr(
        cli, "ensure_state_bucket", lambda cfg, host: bootstrapped.append(cfg)
    )

    class _Result:
        returncode = 0

    monkeypatch.setattr(cli.subprocess, "run", lambda *a, **k: _Result())
    main(["plan"])

    assert bootstrapped == []  # bucket bootstrap only on init
