"""Service -> Terraform google provider custom-endpoint map.

Single place to declare how each localgcp service maps to a Terraform
``<service>_custom_endpoint`` provider attribute. To add a service, follow the
``add-service-endpoint`` skill.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_HOST = "localhost"

# Marker for whether an endpoint has been tested end-to-end against localgcp.
VERIFIED = "verified"
EXPERIMENTAL = "experimental"


@dataclass(frozen=True)
class ServiceEndpoint:
    """How one localgcp service maps to a provider custom endpoint."""

    service: str  # localgcp service key
    provider_attr: str  # google provider attribute, e.g. "storage_custom_endpoint"
    port: int  # localgcp port for the service
    path: str  # URL path incl. API version and trailing slash
    status: str  # VERIFIED or EXPERIMENTAL

    def url(self, host: str = DEFAULT_HOST) -> str:
        """Render the full custom-endpoint URL for the given host."""
        return f"http://{host}:{self.port}{self.path}"


# Ports mirror the localgcp README service table. Only Cloud Storage is verified
# end-to-end today; the rest are best-effort because their localgcp emulators are
# gRPC data-plane while the Terraform provider speaks REST control-plane.
SERVICE_ENDPOINTS: tuple[ServiceEndpoint, ...] = (
    ServiceEndpoint("storage", "storage_custom_endpoint", 4443, "/storage/v1/", VERIFIED),
    ServiceEndpoint("pubsub", "pubsub_custom_endpoint", 8085, "/v1/", EXPERIMENTAL),
    ServiceEndpoint("secretmanager", "secret_manager_custom_endpoint", 8086, "/v1/", EXPERIMENTAL),
    ServiceEndpoint("firestore", "firestore_custom_endpoint", 8088, "/v1/", EXPERIMENTAL),
    ServiceEndpoint("cloudtasks", "cloud_tasks_custom_endpoint", 8089, "/v2/", EXPERIMENTAL),
    ServiceEndpoint("kms", "kms_custom_endpoint", 8091, "/v1/", EXPERIMENTAL),
    ServiceEndpoint("logging", "logging_custom_endpoint", 8092, "/v2/", EXPERIMENTAL),
    ServiceEndpoint("vertexai", "vertex_ai_custom_endpoint", 8090, "/v1/", EXPERIMENTAL),
    ServiceEndpoint("cloudrun", "cloud_run_v2_custom_endpoint", 8093, "/v2/", EXPERIMENTAL),
    ServiceEndpoint("bigquery", "big_query_custom_endpoint", 9060, "/bigquery/v2/", EXPERIMENTAL),
    ServiceEndpoint("spanner", "spanner_custom_endpoint", 9010, "/v1/", EXPERIMENTAL),
    ServiceEndpoint("bigtable", "bigtable_custom_endpoint", 9094, "/v2/", EXPERIMENTAL),
)


def _resolved_port(ep: ServiceEndpoint) -> int:
    """Port for ``ep``, overridable via ``LOCALGCP_PORT_<SERVICE>``."""
    return int(os.environ.get(f"LOCALGCP_PORT_{ep.service.upper()}", ep.port))


def service_port(service: str, default: int | None = None) -> int | None:
    """Resolved port for ``service`` (honouring env overrides), else ``default``."""
    for ep in SERVICE_ENDPOINTS:
        if ep.service == service:
            return _resolved_port(ep)
    return default


def build_endpoints(host: str = DEFAULT_HOST) -> dict[str, str]:
    """Return a mapping of provider attribute -> custom-endpoint URL."""
    return {
        ep.provider_attr: f"http://{host}:{_resolved_port(ep)}{ep.path}"
        for ep in SERVICE_ENDPOINTS
    }
