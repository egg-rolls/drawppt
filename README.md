# DrawPPT

MCP server for creating PPTX files with pixel-precise control.

## Project Structure

```
DrawPPT/
├── src/drawppt/          # Source code
│   ├── server.py         # MCP server entry point
│   ├── session.py        # Session management
│   ├── slide.py          # Slide operations
│   ├── elements/         # Element types
│   └── tools.py          # MCP tool definitions
├── input/                # Input files (images, etc.)
├── output/               # Generated PPTX files
├── docs/                 # Documentation
│   ├── PRD.md
│   ├── PBD.md
│   └── SPEC.md
└── pyproject.toml
```

## Installation

```bash
pip install -e .
```

## Usage

### MCP Configuration

```json
{
  "mcpServers": {
    "drawppt": {
      "command": "drawppt",
      "args": []
    }
  }
}
```

### Available Tools (18)

| Category | Tool | Description |
|----------|------|-------------|
| Session | `create_session` | Create new session |
| Session | `delete_session` | Delete session |
| Slide | `add_slide` | Append slide |
| Slide | `insert_slide` | Insert at position |
| Slide | `delete_slide` | Delete slide |
| Element | `add_textbox` | Add text box |
| Element | `add_image` | Add image |
| Element | `add_shape` | Add shape |
| Element | `update_textbox` | Update text box |
| Element | `update_image` | Update image |
| Element | `update_shape` | Update shape |
| Element | `delete_element` | Delete element |
| Z-Order | `bring_to_front` | Move to top layer |
| Z-Order | `send_to_back` | Move to bottom layer |
| Z-Order | `bring_forward` | Move up one layer |
| Z-Order | `send_backward` | Move down one layer |
| Preview | `preview_slides` | JSON preview |
| Export | `export_pptx` | Export to PPTX |

### Coordinate System

- Origin: top-left (0, 0)
- X: 0 to 1920 (pixels)
- Y: 0 to 1080 (pixels)
- Based on 1920x1080 (16:9) design resolution

## Version History

- v0.1: Basic session, slide, element CRUD, JSON preview, export
- v0.2: Update/delete elements, z-order, insert/delete slides
