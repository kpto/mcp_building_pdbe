# PDBe FastMCP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a small FastMCP server exposing five read-only PDBe v2 tools.

**Architecture:** Keep MCP registration in `server.py`, shared PDBe HTTP behavior in `pdbe/client.py`, and PDB ID validation in `pdbe/validation.py`. Each tool delegates to one fixed endpoint path and returns a structured success or error dictionary.

**Tech Stack:** Python, FastMCP, httpx, pytest, pytest-httpx.

---

## File Structure

- Create `pyproject.toml`: package metadata, dependencies, and pytest config.
- Create `README.md`: setup, run, and tool reference.
- Create `server.py`: FastMCP server and five tool functions.
- Create `pdbe/__init__.py`: package marker.
- Create `pdbe/validation.py`: `normalize_pdb_id`.
- Create `pdbe/client.py`: endpoint mapping, URL construction, and HTTP GET handling.
- Create `tests/test_validation.py`: PDB ID tests.
- Create `tests/test_client.py`: mocked HTTP tests for URL construction and error handling.
- Create `tests/test_server.py`: tool registration and tool delegation tests.

## Endpoint Mapping

- `get_entry_summary`: `/pdb/entry/summary/{pdb_id}`
- `get_entry_molecules`: `/pdb/entry/molecules/{pdb_id}`
- `get_entry_ligands`: `/pdb/entry/ligand_monomers/{pdb_id}`
- `get_entry_validation`: `/validation/summary_quality_scores/entry/{pdb_id}`
- `get_uniprot_mappings`: `/mappings/uniprot/{pdb_id}`

## Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `pdbe/__init__.py`

- [ ] **Step 1: Add packaging files**

Create a Python project with runtime dependencies `fastmcp` and `httpx`, plus test dependencies `pytest` and `pytest-httpx`.

- [ ] **Step 2: Add README usage**

Document installation with `uv sync`, running with `uv run python server.py`, and the five MCP tools.

## Task 2: PDB ID Validation

**Files:**
- Create: `pdbe/validation.py`
- Test: `tests/test_validation.py`

- [ ] **Step 1: Write failing validation tests**

Cover lowercase normalization, whitespace trimming, invalid length, and invalid characters.

- [ ] **Step 2: Run validation tests and verify failure**

Run: `uv run pytest tests/test_validation.py -v`

Expected before implementation: import or function-not-found failure.

- [ ] **Step 3: Implement `normalize_pdb_id`**

Implement a function that strips whitespace, lowercases the value, requires exactly four alphanumeric characters, and raises `ValueError` with a useful message otherwise.

- [ ] **Step 4: Run validation tests and verify pass**

Run: `uv run pytest tests/test_validation.py -v`

## Task 3: PDBe HTTP Client

**Files:**
- Create: `pdbe/client.py`
- Test: `tests/test_client.py`

- [ ] **Step 1: Write failing client tests**

Cover source URL generation, successful JSON response, invalid PDB ID returning a structured error, non-2xx responses, timeouts, and invalid JSON.

- [ ] **Step 2: Run client tests and verify failure**

Run: `uv run pytest tests/test_client.py -v`

Expected before implementation: import or class-not-found failure.

- [ ] **Step 3: Implement endpoint mapping and HTTP handling**

Create `PDBeClient`, `PDBeEndpoint`, and a `fetch_entry(endpoint_key, pdb_id)` method that returns dictionaries containing `ok`, `source_url`, `pdb_id`, `data`, and `error`.

- [ ] **Step 4: Run client tests and verify pass**

Run: `uv run pytest tests/test_client.py -v`

## Task 4: FastMCP Server Tools

**Files:**
- Create: `server.py`
- Test: `tests/test_server.py`

- [ ] **Step 1: Write failing server tests**

Cover that all five tool functions call the expected client endpoint keys and return the client result.

- [ ] **Step 2: Run server tests and verify failure**

Run: `uv run pytest tests/test_server.py -v`

Expected before implementation: import or function-not-found failure.

- [ ] **Step 3: Implement FastMCP tools**

Create `mcp = FastMCP("PDBe")`, instantiate `PDBeClient`, register the five tools with `@mcp.tool()`, and call `mcp.run()` under `if __name__ == "__main__"`.

- [ ] **Step 4: Run server tests and verify pass**

Run: `uv run pytest tests/test_server.py -v`

## Task 5: Verification

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -v`

- [ ] **Step 2: Run import smoke check**

Run: `uv run python -c "import server; print(server.mcp.name)"`

- [ ] **Step 3: Update README if commands differ**

Keep README aligned with the commands that actually work in this environment.

