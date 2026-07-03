# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DrawPPT is an MCP (Model Context Protocol) server that enables AI agents to create, edit, and export PPTX files with pixel-precise control. It uses python-pptx for PPTX generation and exposes 18 tools via MCP protocol.

## Build & Run Commands

```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Run MCP server (entry point)
drawppt

# Run tests
pytest

# Run single test
pytest tests/test_specific.py::test_function_name
```

## Architecture

### MCP Server Layer
- `server.py`: Entry point, creates MCP Server instance with stdio transport
- `tools.py`: Defines all 18 MCP tools using `@server.list_tools()` and `@server.call_tool()` decorators

### Core Data Model
- `session.py`: SessionManager handles multiple concurrent editing sessions, each representing one PPTX file
- `slide.py`: Slide class with Background support (solid/gradient/image)
- `elements/base.py`: Base Element class with coordinate conversion (px → EMU)

### Element Types (in `elements/`)
- `textbox.py`: Multi-line text with font control, alignment, spacing
- `image.py`: Image insertion with path validation
- `shape.py`: 8 shape types mapped to python-pptx MSO_SHAPE enum

### Coordinate System
- Design resolution: 1920×1080 pixels (16:9)
- Origin: top-left (0,0)
- Conversion: `EMU_PER_PX = 914400 / 96` (at 96 DPI)

## MCP Protocol Details

The server uses MCP SDK with these patterns:
```python
# Tool registration
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return TOOLS

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    result = await _handle_tool(name, arguments, session_manager)
    return [TextContent(type="text", text=result)]
```

## Key Design Decisions

1. **Pixel coordinates**: All positions/sizes in pixels (0-1920 x 0-1080), converted to EMU internally
2. **Session-based**: One session = one PPTX file with multiple slides
3. **Z-order**: Elements ordered by z_order field; bring_to_front/send_to_back adjust this
4. **No PNG preview**: Only JSON preview mode (PNG rendering not implemented)
5. **Input/Output folders**: `input/` for source files (images), `output/` for generated PPTX (gitignored)

## Adding New Elements

1. Create new class in `elements/` inheriting from `Element`
2. Implement `apply_to_slide()` and `to_dict()`
3. Add to `elements/__init__.py`
4. Add tool definitions in `tools.py` (add_xxx, update_xxx)
5. Register in SHAPE_MAP if it's a shape type
