from fastmcp import FastMCP

# create a MCP server instance
mcp = FastMCP("PDBe MCP Server")


@mcp.tool()  # this decorator registers the function as a tool that can be called by clients
# the repo is typed which is crucial for fastmcp to generate meta data
# of tools using the function signature and docstring
def healthcheck() -> dict[str, str]:
    """Simple connectivity check for clients."""  # this will be shown as the description of the tool
    return {"status": "ok", "service": "pdbe-mcp"}


@mcp.tool()
def lookup_entry(
    pdb_id: str,
) -> dict[
    str, str
]:  # input and output types will be used to generate JSON schema for validation
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
    mcp.run(
        transport="http",  # use http instead of stdio unless the server is purely for local only
        host="0.0.0.0",  # listen on all interfaces for serving the public, change to "localhost" to restrict to local only
    )


if __name__ == "__main__":
    main()
