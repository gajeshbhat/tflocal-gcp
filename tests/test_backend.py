"""Tests for gcs backend wiring (env + state bucket bootstrap)."""

import urllib.error

from tflocal_gcp import backend
from tflocal_gcp.overrides import DUMMY_ACCESS_TOKEN


def test_backend_env_points_at_localgcp():
    env = backend.backend_env()
    assert env["STORAGE_EMULATOR_HOST"] == "localhost:4443"
    assert env["GOOGLE_OAUTH_ACCESS_TOKEN"] == DUMMY_ACCESS_TOKEN


def test_backend_env_honours_host_and_port(monkeypatch):
    monkeypatch.setenv("LOCALGCP_PORT_STORAGE", "5555")
    env = backend.backend_env(host="127.0.0.1")
    assert env["STORAGE_EMULATOR_HOST"] == "127.0.0.1:5555"


def test_ensure_state_bucket_noop_without_bucket(monkeypatch):
    called = []
    monkeypatch.setattr(backend.urllib.request, "urlopen", lambda *a, **k: called.append(a))
    backend.ensure_state_bucket(None)
    backend.ensure_state_bucket({})
    assert called == []


def _http_error(code):
    return urllib.error.HTTPError("u", code, "msg", {}, None)


def test_ensure_state_bucket_creates_when_missing(monkeypatch):
    requests = []

    def fake_urlopen(req, *args, **kwargs):
        # First call is the existence GET (str URL) -> 404; second is POST.
        if isinstance(req, str):
            raise _http_error(404)
        requests.append(req)

        class _Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        return _Resp()

    monkeypatch.setattr(backend.urllib.request, "urlopen", fake_urlopen)
    backend.ensure_state_bucket({"bucket": '"tf-state"'})

    assert len(requests) == 1
    assert requests[0].get_method() == "POST"
    assert "project=local" in requests[0].full_url
    assert b'"name": "tf-state"' in requests[0].data


def test_ensure_state_bucket_skips_when_present(monkeypatch):
    requests = []

    def fake_urlopen(req, *args, **kwargs):
        if isinstance(req, str):
            return object()  # GET succeeds -> bucket exists
        requests.append(req)

    monkeypatch.setattr(backend.urllib.request, "urlopen", fake_urlopen)
    backend.ensure_state_bucket({"bucket": "tf-state"})
    assert requests == []  # no POST issued


def test_ensure_state_bucket_handles_unreachable(monkeypatch, capsys):
    def fake_urlopen(req, *args, **kwargs):
        raise OSError("connection refused")

    monkeypatch.setattr(backend.urllib.request, "urlopen", fake_urlopen)
    backend.ensure_state_bucket({"bucket": "tf-state"})  # must not raise
    assert "not reachable" in capsys.readouterr().err
