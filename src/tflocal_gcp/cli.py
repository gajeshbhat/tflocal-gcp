"""Command-line entry point for tflocal-gcp.

Orchestrates the run: parse ``*.tf``, write the override file, exec
``terraform`` with the user's arguments, then always clean up.
"""

from __future__ import annotations

import os
import subprocess
import sys

from . import __version__
from .backend import backend_env, ensure_state_bucket
from .hcl import find_gcs_backend, find_google_providers, parse_tf_files
from .overrides import (
    cleanup_override_files,
    generate_override_content,
    write_override_file,
)

# Terraform binary to invoke; override with TF_CMD for wrappers like tofu.
TF_CMD = os.environ.get("TF_CMD", "terraform")

# Host that serves the localgcp endpoints.
LOCALGCP_HOST = os.environ.get("LOCALGCP_HOST", "localhost")

# Fallback when the config declares no explicit google provider block.
_DEFAULT_PROVIDER = {"type": "google", "alias": None}


def _run_terraform(argv: list[str], env: dict[str, str] | None = None) -> int:
    """Exec ``terraform`` with ``argv``; return its exit code."""
    try:
        return subprocess.run([TF_CMD, *argv], env=env).returncode
    except FileNotFoundError:
        print(
            f"Error: '{TF_CMD}' not found on PATH. Install Terraform or set TF_CMD.",
            file=sys.stderr,
        )
        return 127


def main(argv: list[str] | None = None) -> int:
    """tflocal-gcp entry point. Returns the process exit code."""
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] in ("-v", "--version", "-version"):
        print(f"tflocal-gcp {__version__}")
        return 0

    directory = "."
    tf_files = parse_tf_files(directory)
    providers = find_google_providers(tf_files) or [_DEFAULT_PROVIDER]
    backend_cfg = find_gcs_backend(tf_files)

    content = generate_override_content(providers, host=LOCALGCP_HOST)
    override_path = write_override_file(directory, content)

    env = os.environ.copy()
    if backend_cfg is not None:
        env.update(backend_env(LOCALGCP_HOST))
        if argv and argv[0] == "init":
            ensure_state_bucket(backend_cfg, LOCALGCP_HOST)

    if os.environ.get("DRY_RUN"):
        print(f"tflocal-gcp: wrote {override_path} (DRY_RUN, terraform not invoked)")
        return 0

    try:
        return _run_terraform(argv, env=env)
    finally:
        cleanup_override_files([override_path])


if __name__ == "__main__":
    raise SystemExit(main())
