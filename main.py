from fastmcp import FastMCP

mcp = FastMCP("PDBe MCP Server")


@mcp.tool()
def healthcheck() -> dict[str, str]:
    """Simple connectivity check for clients."""
    return {"status": "ok", "service": "pdbe-mcp"}


@mcp.tool()
def lookup_entry(pdb_id: str) -> dict[str, str]:
    """Placeholder PDBe lookup tool.

    This starter validates and normalizes the PDB entry id.
    Replace the return block with a real PDBe API call.
    """
    normalized = pdb_id.strip().lower()
    if len(normalized) != 4 or not normalized.isalnum():
        raise ValueError("pdb_id must be a 4-character alphanumeric id (e.g. 1cbs)")

    return {
        "pdb_id": normalized,
        "message": "Starter response. Integrate PDBe API calls here.",
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
