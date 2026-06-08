"""Point Terraform's ``gcs`` backend at localgcp's Cloud Storage emulator.

Setting ``STORAGE_EMULATOR_HOST`` both redirects the backend's storage client to
localgcp and makes it skip Google credential discovery. On ``init`` we also
create the state bucket if it does not already exist.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Any

from .endpoints import DEFAULT_HOST, service_port
from .overrides import DUMMY_ACCESS_TOKEN

# Default Cloud Storage port if the service is somehow not in the map.
_STORAGE_PORT_DEFAULT = 4443

# Project sent when creating the state bucket; localgcp ignores its value.
_BOOTSTRAP_PROJECT = "local"


def _unquote(value: Any) -> Any:
    """Strip the surrounding quotes python-hcl2 keeps on string literals."""
    if isinstance(value, str) and len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def _storage_port() -> int:
    return service_port("storage", _STORAGE_PORT_DEFAULT) or _STORAGE_PORT_DEFAULT


def backend_env(host: str = DEFAULT_HOST) -> dict[str, str]:
    """Env vars that make Terraform's gcs backend talk to localgcp."""
    return {
        "STORAGE_EMULATOR_HOST": f"{host}:{_storage_port()}",
        "GOOGLE_OAUTH_ACCESS_TOKEN": DUMMY_ACCESS_TOKEN,
    }


def ensure_state_bucket(
    backend_cfg: dict[str, Any] | None,
    host: str = DEFAULT_HOST,
) -> None:
    """Create the gcs backend state bucket in localgcp if it is missing."""
    bucket = _unquote(backend_cfg.get("bucket")) if backend_cfg else None
    if not bucket:
        return

    base = f"http://{host}:{_storage_port()}/storage/v1/b"

    try:
        urllib.request.urlopen(f"{base}/{bucket}", timeout=5)
        return  # already exists
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            print(
                f"Warning: could not check state bucket '{bucket}': {exc}",
                file=sys.stderr,
            )
            return
    except OSError as exc:
        print(
            f"Warning: localgcp not reachable at {host}:{_storage_port()}: {exc}",
            file=sys.stderr,
        )
        return

    payload = json.dumps({"name": bucket}).encode()
    req = urllib.request.Request(
        f"{base}?project={_BOOTSTRAP_PROJECT}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        print(f"tflocal-gcp: created state bucket '{bucket}' in localgcp")
    except OSError as exc:
        print(
            f"Warning: could not create state bucket '{bucket}': {exc}",
            file=sys.stderr,
        )
