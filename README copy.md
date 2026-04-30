# PDBe FastMCP Server

Small FastMCP server exposing a curated subset of the PDBe v2 REST API.

## Setup

```bash
uv sync
```

## Run

```bash
uv run python server.py
```

or:

```bash
uv run pdbe-mcp
```

## Tools

- `get_entry_summary(pdb_id)`: concise metadata for a PDB entry.
- `get_entry_molecules(pdb_id)`: molecule/entity details for a PDB entry.
- `get_entry_ligands(pdb_id)`: modeled non-water ligands for a PDB entry.
- `get_entry_validation(pdb_id)`: validation summary quality scores.
- `get_uniprot_mappings(pdb_id)`: SIFTS PDB-to-UniProt residue mappings.

Each tool accepts a four-character PDB ID and returns structured JSON containing `ok`, `source_url`, `pdb_id`, `data`, and `error`.

## Test

```bash
uv run pytest -v
```

