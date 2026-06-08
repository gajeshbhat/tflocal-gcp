"""Tests for override file generation, write, and cleanup helpers."""

import os

from tflocal_gcp.overrides import (
    DUMMY_ACCESS_TOKEN,
    OVERRIDE_FILENAME,
    cleanup_override_files,
    generate_override_content,
    write_override_file,
)


def test_generate_override_renders_provider_with_endpoints():
    content = generate_override_content([{"type": "google", "alias": None}])
    assert 'provider "google" {' in content
    assert f'access_token = "{DUMMY_ACCESS_TOKEN}"' in content
    assert 'storage_custom_endpoint = "http://localhost:4443/storage/v1/"' in content
    assert "alias" not in content


def test_generate_override_includes_alias_block():
    content = generate_override_content([{"type": "google", "alias": "eu"}])
    assert 'alias        = "eu"' in content


def test_generate_override_honours_host():
    content = generate_override_content(
        [{"type": "google-beta", "alias": None}], host="127.0.0.1"
    )
    assert 'provider "google-beta" {' in content
    assert "http://127.0.0.1:4443/storage/v1/" in content


def test_generate_override_renders_one_block_per_provider():
    content = generate_override_content(
        [
            {"type": "google", "alias": None},
            {"type": "google", "alias": "eu"},
        ]
    )
    assert content.count('provider "google" {') == 2


def test_write_and_cleanup_round_trip(tmp_path):
    path = write_override_file(str(tmp_path), "# test")
    assert os.path.basename(path) == OVERRIDE_FILENAME
    assert os.path.isfile(path)

    cleanup_override_files([path])
    assert not os.path.exists(path)


def test_cleanup_ignores_missing_files(tmp_path):
    missing = str(tmp_path / OVERRIDE_FILENAME)
    cleanup_override_files([missing])  # must not raise
