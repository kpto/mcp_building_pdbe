# mcp_building_pdbe

Starter template for a FastMCP 3.x server.

## What is included

- `healthcheck` tool: confirms the server is reachable.
- `lookup_entry` tool: placeholder tool that validates a PDB ID.
- `main.py`: runnable FastMCP server entrypoint.

## Run locally

```bash
pip install -r requirements.txt
```

If you use `uv`:

```bash
uv sync
uv run python main.py
```

If you use your existing virtual environment:

```bash
python main.py
```

## Next steps

1. Replace `lookup_entry` in `main.py` with real PDBe API calls.
2. Add more MCP tools/resources/prompts for your workflow.
3. Connect this server to your MCP client config.
