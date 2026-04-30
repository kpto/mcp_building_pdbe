# PDBe FastMCP Server Design

Date: 2026-04-30

## Goal

Build a small Model Context Protocol server for a curated subset of the PDBe v2 REST API. The server will use FastMCP and expose a handful of high-value read-only tools for PDB entry lookups.

The first version deliberately avoids generating tools for the full OpenAPI surface. It should be easy to understand, easy to test, and straightforward to extend with additional curated tools later.

## Source API

The server targets the PDBe v2 API documented at:

- https://www.ebi.ac.uk/pdbe/api/v2/doc/
- https://www.ebi.ac.uk/pdbe/api/v2/openapi.json

PDBe's migration notice states that old PDBe APIs were replaced by the new API after the old API sunset date of 2026-01-12, so this project will use v2 endpoints.

## User-Facing MCP Tools

The initial tool subset is:

- `get_entry_summary(pdb_id: str)`
- `get_entry_molecules(pdb_id: str)`
- `get_entry_ligands(pdb_id: str)`
- `get_entry_validation(pdb_id: str)`
- `get_uniprot_mappings(pdb_id: str)`

Each tool accepts a single PDB ID, normalizes it to lowercase for PDBe entry endpoints, validates that it is a four-character PDB identifier, calls the relevant PDBe v2 endpoint, and returns structured JSON.

## Architecture

The project will be a small Python package:

- `server.py` creates the FastMCP server and registers tools.
- `pdbe/client.py` owns HTTP requests, URL construction, timeouts, and response normalization.
- `pdbe/validation.py` owns PDB ID normalization and validation.
- `tests/` contains unit and mocked HTTP tests.

The server will use:

- `fastmcp` for MCP tool registration and runtime.
- `httpx` for HTTP requests.
- `pydantic` only where structured models meaningfully improve tool input or output validation.
- `pytest` and `pytest-httpx` for tests that mock PDBe responses.

## Data Flow

1. An MCP client calls a FastMCP tool with `pdb_id`.
2. The tool normalizes and validates the ID.
3. The tool delegates to the PDBe client with a known endpoint key.
4. The client builds the full PDBe v2 URL and performs a GET request.
5. The response is returned as a JSON-compatible dictionary with:
   - `ok`: boolean
   - `source_url`: the PDBe URL called
   - `pdb_id`: normalized PDB ID
   - `data`: decoded PDBe response for successful calls
   - `error`: structured error details for failed calls

## Endpoint Mapping

The implementation will verify exact endpoint paths against the PDBe v2 OpenAPI document before coding the client mapping. The intended mappings are:

- Summary: entry summary data for a PDB ID.
- Molecules: macromolecule/entity data for a PDB ID.
- Ligands: ligand or ligand-monomer data for a PDB ID.
- Validation: model quality or validation summary data for a PDB ID.
- UniProt mappings: SIFTS/UniProt residue or entity mappings for a PDB ID.

If the OpenAPI schema names differ from these labels, the code will use the documented v2 paths while keeping the MCP tool names above.

## Error Handling

Invalid PDB IDs fail before any network call and return a structured error.

Network and API failures return structured errors rather than stack traces:

- timeout
- connection error
- non-2xx status code
- invalid JSON response

The MCP tools are read-only and do not mutate PDBe or local state.

## Testing

Tests will cover:

- PDB ID validation and normalization.
- URL construction for each tool.
- Successful mocked PDBe responses.
- Invalid PDB ID behavior without network calls.
- Timeout or non-2xx response handling.

Live PDBe smoke tests may be added as optional tests, but the default test suite must not depend on external network access.

## Non-Goals

The first version will not:

- Generate hundreds of tools from the OpenAPI schema.
- Cache PDBe responses.
- Implement authentication.
- Add write operations.
- Provide a web UI.

## Extension Path

After the initial subset works, the server can grow in two directions:

- Add more curated tools for common PDBe workflows.
- Add a guarded generic endpoint caller for advanced users who need endpoints outside the curated set.
