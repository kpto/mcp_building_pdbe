from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pdbe-mcp")


@mcp.tool()
def hello(name: str) -> str:
    """Say hello to a user"""
    return f"Hello, {name}!"


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


if __name__ == "__main__":
    mcp.run()
