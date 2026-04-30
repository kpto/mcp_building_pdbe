"""FastMCP server exposing selected PDBe v2 endpoints."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from pdbe.client import PDBeClient, PDBeResult

mcp = FastMCP("PDBe")
pdbe_client = PDBeClient()


def _fetch_entry(endpoint_key: str, pdb_id: str) -> PDBeResult:
    return pdbe_client.fetch_entry(endpoint_key, pdb_id)


@mcp.tool()
def healthcheck() -> dict[str, str]:
    """Simple connectivity check for clients."""
    return {"status": "ok", "service": "pdbe-mcp"}


@mcp.tool()
def get_entry_summary(pdb_id: str) -> dict[str, Any]:
    """Get concise summary metadata for a PDB entry."""
    return _fetch_entry("summary", pdb_id)


@mcp.tool()
def get_entry_molecules(pdb_id: str) -> dict[str, Any]:
    """Get molecule and entity details for a PDB entry."""
    return _fetch_entry("molecules", pdb_id)


@mcp.tool()
def get_entry_ligands(pdb_id: str) -> dict[str, Any]:
    """Get modeled non-water ligand instances for a PDB entry."""
    return _fetch_entry("ligands", pdb_id)


@mcp.tool()
def get_entry_validation(pdb_id: str) -> dict[str, Any]:
    """Get validation summary quality scores for a PDB entry."""
    return _fetch_entry("validation", pdb_id)


@mcp.tool()
def get_uniprot_mappings(pdb_id: str) -> dict[str, Any]:
    """Get SIFTS PDB-to-UniProt residue mappings for a PDB entry."""
    return _fetch_entry("uniprot_mappings", pdb_id)


def main() -> None:
    """Run the MCP server."""
    mcp.run(transport="http", host="0.0.0.0")


if __name__ == "__main__":
    main()
