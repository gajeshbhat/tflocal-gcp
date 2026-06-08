.PHONY: install test e2e lint format dist clean

# Create the virtual environment (first-time or after a clean).
# Requires uv: brew install uv
venv:
	uv venv --python python3.14

# Install the package in editable mode with dev extras.
install:
	uv pip install -e ".[dev]"

test:
	uv run pytest

# End-to-end test against a real localgcp (requires localgcp + terraform on PATH).
e2e:
	RUN_E2E=1 uv run pytest tests/test_e2e.py -v

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests
	uv run ruff check --fix src tests

# Build the sdist and wheel into dist/ (CI publishes these on a vX.Y.Z tag).
dist:
	rm -rf dist
	uv run python -m build

clean:
	rm -rf .venv build dist *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
