"""MCP server entry point."""

import asyncio
from mcp.server import Server, InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import ServerCapabilities

from .session import SessionManager
from .tools import register_tools


def main():
    """Start the DrawPPT MCP server."""
    asyncio.run(async_main())


async def async_main():
    """Async entry point."""
    server = Server("drawppt")
    session_manager = SessionManager()
    register_tools(server, session_manager)

    initialization_options = InitializationOptions(
        server_name="drawppt",
        server_version="0.2.0",
        capabilities=ServerCapabilities(),
    )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, initialization_options)


if __name__ == "__main__":
    main()
