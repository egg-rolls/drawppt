# DrawPPT

MCP server for creating PPTX files with pixel-precise control.

## Features

- **Session Management**: Create/delete editing sessions
- **Slide Operations**: Add, insert, delete slides
- **Elements**: Textbox, Image, Shape (8 types)
- **Text**: Multi-line, font control, alignment, line/paragraph spacing
- **Shapes**: rectangle, rounded_rectangle, oval, triangle, arrow, star, hexagon
- **Background**: Solid, gradient, image
- **Z-Order**: bring_to_front, send_to_back, bring_forward, send_backward
- **Preview**: JSON mode for layout verification
- **Export**: PPTX format

## Installation

```bash
pip install -e .
```

## Usage

### MCP Configuration

Add to your Claude/Cursor MCP settings:

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

### Available Tools

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

### Example Workflow

```
1. create_session() -> session_id
2. add_slide(session_id, bg_type="solid", color="#FFFFFF")
3. add_textbox(session_id, 0, x=100, y=100, w=800, h=100, text="Hello\nWorld", font_size=36)
4. add_shape(session_id, 0, x=100, y=300, w=200, h=200, shape_type="oval", fill_color="#4A90D9")
5. preview_slides(session_id, format="json")
6. export_pptx(session_id, "output.pptx")
```

### Coordinate System

- Origin: top-left (0, 0)
- X: 0 to 1920 (pixels)
- Y: 0 to 1080 (pixels)
- Based on 1920x1080 (16:9) design resolution

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Version History

- v0.1: Basic session, slide, element CRUD, JSON preview, export
- v0.2: Update/delete elements, z-order, insert/delete slides
