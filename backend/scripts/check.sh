#!/usr/bin/env bash
# Espelha o pipeline de CI: ruff -> mypy -> pytest.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> ruff check"
uv run ruff check .

echo "==> ruff format --check"
uv run ruff format --check .

echo "==> mypy --strict"
uv run mypy

echo "==> pytest"
uv run pytest -q "$@"

echo "OK"
