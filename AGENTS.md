# Repository Guidelines

## Project Structure & Module Organization

This repository contains a small Python FastMCP server for selected PDBe v2 API endpoints. Core source lives in `pdbe/`: `client.py` contains the HTTP client and endpoint registry, and `validation.py` contains PDB identifier helpers. `server.py` exposes the MCP tools and delegates to `PDBeClient`. Tests live in `tests/` and mirror the source responsibilities: client behavior, server delegation, and validation rules. Design notes and implementation plans are stored under `docs/superpowers/`.

## Build, Test, and Development Commands

- `uv sync`: install the project dependencies from `pyproject.toml` and `uv.lock`.
- `uv run python server.py`: run the FastMCP server locally.
- `uv run pytest -v`: run the full pytest suite with verbose output.
- `uv run pytest tests/test_client.py -v`: run a focused test file while iterating on client behavior.

There is no dedicated build command configured in the active `pyproject.toml`; keep changes runnable through `uv` unless packaging metadata is added.

## Coding Style & Naming Conventions

Use Python 3.12-compatible syntax, type hints, and small focused functions. Follow the existing style: four-space indentation, module docstrings for source files, `from __future__ import annotations`, and explicit return types on public helpers. Use `snake_case` for functions, variables, endpoint keys, and test names. Prefer structured dictionaries matching the existing result shape: `ok`, `source_url`, `pdb_id`, `data`, and `error`.

## Testing Guidelines

Tests use `pytest`; HTTP behavior is mocked with `pytest-httpx` via the `httpx_mock` fixture. Add or update tests whenever endpoints, validation rules, or MCP tool delegation changes. Name tests by behavior, for example `test_fetch_entry_returns_timeout_error`. Avoid live network calls in tests; mock PDBe responses and failures instead.

## Commit & Pull Request Guidelines

Git history uses short, lower-case summaries such as `uv init , uv add fastmcp` and `get a common mcp base wrapper with a subset of functions`. Keep commit messages concise and imperative when possible. Pull requests should describe the behavior changed, list the tests run, and mention any PDBe endpoint additions or response-shape changes. Include linked issues when available.

## Security & Configuration Tips

Do not commit credentials, tokens, or local environment files. PDBe calls should remain read-only and validate PDB IDs before network access. Keep generated caches such as `.pytest_cache/`, `.venv/`, and `__pycache__/` out of commits.
