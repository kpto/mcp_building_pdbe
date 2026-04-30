import httpx
from fastmcp import FastMCP

OPENAPI_SPEC_URL = "https://www.ebi.ac.uk/pdbe/api/v2/openapi.json"
API_BASE_URL = "https://www.ebi.ac.uk"
REQUEST_TIMEOUT_SECONDS = 30.0


def build_server() -> FastMCP:
    """Create a FastMCP server by wrapping the PDBe API v2 OpenAPI spec."""
    openapi_spec = httpx.get(OPENAPI_SPEC_URL, timeout=REQUEST_TIMEOUT_SECONDS).json()
    api_client = httpx.AsyncClient(
        base_url=API_BASE_URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    return FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=api_client,
        name="PDBe API v2 MCP Wrapper",
        tags={"pdbe", "openapi", "v2"},
    )


mcp = build_server()


def main() -> None:
    mcp.run(
        transport="http",
        host="0.0.0.0",
    )


if __name__ == "__main__":
    main()
