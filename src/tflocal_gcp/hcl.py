"""Parse the local ``*.tf`` files to discover google providers and backend.

The CLI uses these helpers to learn which providers and aliases to override and
whether a ``gcs`` backend is configured.
"""

from __future__ import annotations

import glob
import os
import sys
from typing import Any

import hcl2

# Provider types that tflocal-gcp redirects at localgcp.
GOOGLE_PROVIDER_TYPES = ("google", "google-beta")

# python-hcl2 marks parsed block bodies with this key; ignore it when walking.
_BLOCK_MARKER = "__is_block__"


def _unquote(value: Any) -> Any:
    """Strip the surrounding quotes python-hcl2 keeps on string literals."""
    if isinstance(value, str) and len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


def parse_tf_files(directory: str = ".") -> dict[str, Any]:
    """Parse every ``*.tf`` file in ``directory`` into a dict keyed by filename.

    Returns ``{filename: parsed_hcl_dict}``. Files that fail to parse are
    skipped with a warning.
    """
    parsed: dict[str, Any] = {}
    for path in sorted(glob.glob(os.path.join(directory, "*.tf"))):
        try:
            with open(path, encoding="utf-8") as fp:
                parsed[os.path.basename(path)] = hcl2.load(fp)
        except Exception as exc:  # best-effort: skip files we cannot parse
            print(f"Warning: could not parse '{path}': {exc}", file=sys.stderr)
    return parsed


def find_google_providers(tf_files: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the ``google`` / ``google-beta`` providers as ``{type, alias}``.

    One entry per provider block in the configuration, including aliases.
    """
    providers: list[dict[str, Any]] = []
    for parsed in tf_files.values():
        for block in parsed.get("provider", []):
            for label, body in block.items():
                if label == _BLOCK_MARKER:
                    continue
                ptype = _unquote(label)
                if ptype not in GOOGLE_PROVIDER_TYPES:
                    continue
                alias = _unquote(body.get("alias")) if isinstance(body, dict) else None
                providers.append({"type": ptype, "alias": alias})
    return providers


def find_gcs_backend(tf_files: dict[str, Any]) -> dict[str, Any] | None:
    """Return the ``gcs`` backend config block if one is present, else ``None``."""
    for parsed in tf_files.values():
        for tf_block in parsed.get("terraform", []):
            for backend in tf_block.get("backend", []):
                for label, body in backend.items():
                    if label == _BLOCK_MARKER:
                        continue
                    if _unquote(label) == "gcs":
                        return body if isinstance(body, dict) else {}
    return None
