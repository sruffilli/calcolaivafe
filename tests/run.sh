#!/usr/bin/env bash
# Test automatici: esecuzione degli script sui file sample con servizi esterni finti.
# exit 0 = pass, 75 = impossibile eseguire qui (manca uv), altro = fail.
set -u
cd "$(dirname "$0")/.." || exit 1
if ! command -v uv >/dev/null 2>&1; then
  echo "uv non trovato: test non eseguibili (https://github.com/astral-sh/uv)" >&2
  exit 75
fi
exec uv run -q tests/test_scripts.py
