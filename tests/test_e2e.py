"""End-to-end test against a real, running localgcp.

Opt-in: set ``RUN_E2E=1`` and have both ``localgcp`` and ``terraform`` on PATH.
The test starts localgcp, runs ``tflocal-gcp init``/``apply`` against the
bundled example, asserts the bucket exists in the emulator, then destroys it.
"""

import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from tflocal_gcp.cli import main

RUN_E2E = os.environ.get("RUN_E2E") == "1"
EXAMPLE = Path(__file__).resolve().parents[1] / "example"
GCS_BASE = "http://localhost:4443/storage/v1/b"
BUCKET = "my-local-bucket"

pytestmark = pytest.mark.skipif(
    not RUN_E2E, reason="set RUN_E2E=1 to run end-to-end tests"
)


def _require(tool: str) -> str:
    path = shutil.which(tool)
    if path is None:
        pytest.skip(f"'{tool}' not found on PATH")
    return path


def _wait_for_gcs(timeout: float = 30.0) -> None:
    """Block until localgcp's Cloud Storage REST API answers, or fail."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{GCS_BASE}?project=local", timeout=2)
            return
        except urllib.error.HTTPError:
            return  # any HTTP response means the server is up
        except OSError:
            time.sleep(0.5)
    pytest.fail("localgcp Cloud Storage did not become ready in time")


def _bucket_exists(name: str) -> bool:
    try:
        urllib.request.urlopen(f"{GCS_BASE}/{name}", timeout=5)
        return True
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise


@pytest.fixture
def localgcp():
    localgcp_bin = _require("localgcp")
    proc = subprocess.Popen(
        [localgcp_bin, "up"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_gcs()
        yield
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture
def workdir(tmp_path):
    shutil.copy(EXAMPLE / "main.tf", tmp_path / "main.tf")
    return tmp_path


def test_apply_creates_bucket_in_localgcp(localgcp, workdir, monkeypatch):
    _require("terraform")
    monkeypatch.chdir(workdir)
    monkeypatch.delenv("DRY_RUN", raising=False)

    assert main(["init"]) == 0
    try:
        assert main(["apply", "-auto-approve"]) == 0
        assert _bucket_exists(BUCKET), "bucket should exist after apply"
    finally:
        main(["destroy", "-auto-approve"])

    assert not _bucket_exists(BUCKET), "bucket should be gone after destroy"
