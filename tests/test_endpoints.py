"""Tests for the service -> custom-endpoint map."""

from tflocal_gcp.endpoints import (
    SERVICE_ENDPOINTS,
    VERIFIED,
    build_endpoints,
    service_port,
)


def _by_service(name):
    return next(ep for ep in SERVICE_ENDPOINTS if ep.service == name)


def test_storage_is_verified():
    storage = _by_service("storage")
    assert storage.status == VERIFIED
    assert storage.provider_attr == "storage_custom_endpoint"


def test_storage_url_renders_with_default_host():
    storage = _by_service("storage")
    assert storage.url() == "http://localhost:4443/storage/v1/"


def test_url_respects_custom_host():
    storage = _by_service("storage")
    assert storage.url("127.0.0.1") == "http://127.0.0.1:4443/storage/v1/"


def test_build_endpoints_keys_are_provider_attrs():
    endpoints = build_endpoints()
    assert endpoints["storage_custom_endpoint"] == "http://localhost:4443/storage/v1/"
    assert all(attr.endswith("_custom_endpoint") for attr in endpoints)


def test_provider_attrs_are_unique():
    attrs = [ep.provider_attr for ep in SERVICE_ENDPOINTS]
    assert len(attrs) == len(set(attrs))


def test_vertex_ai_and_bigtable_are_mapped():
    assert _by_service("vertexai").provider_attr == "vertex_ai_custom_endpoint"
    assert _by_service("bigtable").provider_attr == "bigtable_custom_endpoint"


def test_service_port_returns_resolved_port():
    assert service_port("storage") == 4443
    assert service_port("unknown", default=1234) == 1234


def test_port_override_via_env(monkeypatch):
    monkeypatch.setenv("LOCALGCP_PORT_STORAGE", "9999")
    assert service_port("storage") == 9999
    assert build_endpoints()["storage_custom_endpoint"] == (
        "http://localhost:9999/storage/v1/"
    )
