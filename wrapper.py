import httpx
from fastmcp import FastMCP

OPENAPI_SPEC_URL = "https://www.ebi.ac.uk/pdbe/api/v2/openapi.json"
API_BASE_URL = "https://www.ebi.ac.uk"
REQUEST_TIMEOUT_SECONDS = 30.0


def _normalize_schema_items(value: object) -> object:
    """Recursively normalize OpenAPI schemas for FastMCP parsing compatibility."""
    if isinstance(value, dict):
        normalized: dict[object, object] = {}
        for key, item in value.items():
            normalized_item = _normalize_schema_items(item)
            if key == "items" and isinstance(normalized_item, list):
                # Some specs use tuple-style array items as a list. FastMCP expects
                # 'items' to be a schema object, so wrap alternatives in anyOf.
                normalized[key] = {"anyOf": normalized_item}
            else:
                normalized[key] = normalized_item
        return normalized

    if isinstance(value, list):
        return [_normalize_schema_items(item) for item in value]

    return value


def build_server() -> FastMCP:
    """Create a FastMCP server by wrapping the PDBe API v2 OpenAPI spec."""
    raw_openapi_spec = httpx.get(
        OPENAPI_SPEC_URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ).json()
    openapi_spec = _normalize_schema_items(raw_openapi_spec)

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
        stateless_http=True,
    )


if __name__ == "__main__":
    main()
