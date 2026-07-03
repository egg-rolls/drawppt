"""MCP tool definitions."""

import json
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

from .session import SessionManager
from .slide import Slide, Background
from .elements import Textbox, Image, Shape
from .elements.shape import SHAPE_MAP


def register_tools(server: Server, session_manager: SessionManager):
    """Register all MCP tools."""

    # Define all tools
    TOOLS = [
        Tool(
            name="create_session",
            description="Create a new PPTX editing session",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="delete_session",
            description="Delete a session and its temporary files",
            inputSchema={
                "type": "object",
                "properties": {"session_id": {"type": "string"}},
                "required": ["session_id"],
            },
        ),
        Tool(
            name="add_slide",
            description="Add a new blank slide to the end of the presentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "bg_type": {"type": "string", "enum": ["none", "solid", "gradient", "image"], "default": "none"},
                    "color": {"type": "string", "description": "Background color in hex (e.g. #FFFFFF)"},
                    "gradient_start": {"type": "string"},
                    "gradient_end": {"type": "string"},
                    "gradient_direction": {"type": "string", "enum": ["horizontal", "vertical"], "default": "vertical"},
                    "image_path": {"type": "string"},
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="insert_slide",
            description="Insert a new slide at the specified position",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "slide_index": {"type": "integer"},
                    "bg_type": {"type": "string", "enum": ["none", "solid", "gradient", "image"], "default": "none"},
                    "color": {"type": "string"},
                    "gradient_start": {"type": "string"},
                    "gradient_end": {"type": "string"},
                    "gradient_direction": {"type": "string", "enum": ["horizontal", "vertical"], "default": "vertical"},
                    "image_path": {"type": "string"},
                },
                "required": ["session_id", "slide_index"],
            },
        ),
        Tool(
            name="delete_slide",
            description="Delete a slide at the specified position",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "slide_index": {"type": "integer"},
                },
                "required": ["session_id", "slide_index"],
            },
        ),
        Tool(
            name="add_textbox",
            description="Add a text box to a slide. Supports multi-line text with \\n.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "slide_index": {"type": "integer"},
                    "x": {"type": "integer", "description": "X position in pixels (0-1920)"},
                    "y": {"type": "integer", "description": "Y position in pixels (0-1080)"},
                    "w": {"type": "integer", "description": "Width in pixels"},
                    "h": {"type": "integer", "description": "Height in pixels"},
                    "text": {"type": "string", "description": "Text content (use \\n for new lines)"},
                    "font_size": {"type": "integer", "default": 18},
                    "font_family": {"type": "string", "default": "Microsoft YaHei"},
                    "color": {"type": "string", "default": "#000000", "description": "Text color in hex"},
                    "bold": {"type": "boolean", "default": False},
                    "italic": {"type": "boolean", "default": False},
                    "align": {"type": "string", "enum": ["left", "center", "right"], "default": "left"},
                    "line_spacing": {"type": "number", "default": 1.0},
                    "paragraph_spacing": {"type": "integer", "default": 0},
                },
                "required": ["session_id", "slide_index", "x", "y", "w", "h", "text"],
            },
        ),
        Tool(
            name="add_image",
            description="Add an image to a slide",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "slide_index": {"type": "integer"},
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "w": {"type": "integer"},
                    "h": {"type": "integer"},
                    "image_path": {"type": "string", "description": "Local file path to image"},
                },
                "required": ["session_id", "slide_index", "x", "y", "w", "h", "image_path"],
            },
        ),
        Tool(
            name="add_shape",
            description="Add a shape to a slide",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "slide_index": {"type": "integer"},
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "w": {"type": "integer"},
                    "h": {"type": "integer"},
                    "shape_type": {"type": "string", "enum": list(SHAPE_MAP.keys()), "default": "rectangle"},
                    "fill_color": {"type": "string", "description": "Fill color in hex"},
                    "border_color": {"type": "string", "description": "Border color in hex"},
                    "border_width": {"type": "integer", "default": 0},
                    "border_radius": {"type": "integer", "default": 0},
                },
                "required": ["session_id", "slide_index", "x", "y", "w", "h"],
            },
        ),
        Tool(
            name="update_textbox",
            description="Update a text box's properties",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "element_id": {"type": "string"},
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "w": {"type": "integer"},
                    "h": {"type": "integer"},
                    "text": {"type": "string"},
                    "font_size": {"type": "integer"},
                    "font_family": {"type": "string"},
                    "color": {"type": "string"},
                    "bold": {"type": "boolean"},
                    "italic": {"type": "boolean"},
                    "align": {"type": "string"},
                    "line_spacing": {"type": "number"},
                    "paragraph_spacing": {"type": "integer"},
                },
                "required": ["session_id", "element_id"],
            },
        ),
        Tool(
            name="update_image",
            description="Update an image's properties",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "element_id": {"type": "string"},
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "w": {"type": "integer"},
                    "h": {"type": "integer"},
                    "image_path": {"type": "string"},
                },
                "required": ["session_id", "element_id"],
            },
        ),
        Tool(
            name="update_shape",
            description="Update a shape's properties",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "element_id": {"type": "string"},
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "w": {"type": "integer"},
                    "h": {"type": "integer"},
                    "shape_type": {"type": "string"},
                    "fill_color": {"type": "string"},
                    "border_color": {"type": "string"},
                    "border_width": {"type": "integer"},
                    "border_radius": {"type": "integer"},
                },
                "required": ["session_id", "element_id"],
            },
        ),
        Tool(
            name="delete_element",
            description="Delete an element from a slide",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "element_id": {"type": "string"},
                },
                "required": ["session_id", "element_id"],
            },
        ),
        Tool(
            name="bring_to_front",
            description="Bring an element to the front (top layer)",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "element_id": {"type": "string"},
                },
                "required": ["session_id", "element_id"],
            },
        ),
        Tool(
            name="send_to_back",
            description="Send an element to the back (bottom layer)",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "element_id": {"type": "string"},
                },
                "required": ["session_id", "element_id"],
            },
        ),
        Tool(
            name="bring_forward",
            description="Move an element one layer up",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "element_id": {"type": "string"},
                },
                "required": ["session_id", "element_id"],
            },
        ),
        Tool(
            name="send_backward",
            description="Move an element one layer down",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "element_id": {"type": "string"},
                },
                "required": ["session_id", "element_id"],
            },
        ),
        Tool(
            name="preview_slides",
            description="Preview the current draft presentation as JSON",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "slide_index": {"type": "integer", "description": "Specific slide to preview (optional)"},
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="export_pptx",
            description="Export the presentation to a PPTX file",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "output_path": {"type": "string", "description": "Output filename (relative to working directory)"},
                },
                "required": ["session_id", "output_path"],
            },
        ),
    ]

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return TOOLS

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        result = await _handle_tool(name, arguments, session_manager)
        return [TextContent(type="text", text=result)]


async def _handle_tool(name: str, arguments: dict, session_manager: SessionManager) -> str:
    """Handle tool calls."""

    if name == "create_session":
        session = session_manager.create_session()
        return json.dumps({
            "session_id": session.session_id,
            "width": session.width,
            "height": session.height,
            "slide_count": 0,
        })

    elif name == "delete_session":
        session_manager.delete_session(arguments["session_id"])
        return json.dumps({"success": True})

    elif name == "add_slide":
        session = session_manager.get_session(arguments["session_id"])
        background = Background(
            bg_type=arguments.get("bg_type", "none"),
            color=arguments.get("color"),
            gradient_start=arguments.get("gradient_start"),
            gradient_end=arguments.get("gradient_end"),
            gradient_direction=arguments.get("gradient_direction", "vertical"),
            image_path=arguments.get("image_path"),
        )
        slide = Slide(index=len(session.slides), background=background)
        session.slides.append(slide)
        return json.dumps({"slide_index": slide.index, "total_slides": len(session.slides)})

    elif name == "insert_slide":
        session = session_manager.get_session(arguments["session_id"])
        slide_index = arguments["slide_index"]
        if slide_index < 0 or slide_index > len(session.slides):
            return json.dumps({"error": f"Slide index {slide_index} out of range"})
        background = Background(
            bg_type=arguments.get("bg_type", "none"),
            color=arguments.get("color"),
            gradient_start=arguments.get("gradient_start"),
            gradient_end=arguments.get("gradient_end"),
            gradient_direction=arguments.get("gradient_direction", "vertical"),
            image_path=arguments.get("image_path"),
        )
        slide = Slide(index=slide_index, background=background)
        session.slides.insert(slide_index, slide)
        for i in range(slide_index + 1, len(session.slides)):
            session.slides[i].index = i
        return json.dumps({"slide_index": slide_index, "total_slides": len(session.slides)})

    elif name == "delete_slide":
        session = session_manager.get_session(arguments["session_id"])
        slide_index = arguments["slide_index"]
        if slide_index < 0 or slide_index >= len(session.slides):
            return json.dumps({"error": f"Slide index {slide_index} out of range"})
        session.slides.pop(slide_index)
        for i in range(slide_index, len(session.slides)):
            session.slides[i].index = i
        return json.dumps({"deleted_index": slide_index, "total_slides": len(session.slides)})

    elif name == "add_textbox":
        session = session_manager.get_session(arguments["session_id"])
        slide_index = arguments["slide_index"]
        if slide_index < 0 or slide_index >= len(session.slides):
            return json.dumps({"error": f"Slide index {slide_index} out of range"})
        slide = session.slides[slide_index]
        element_id = f"elem_{len(slide.elements):04d}"
        textbox = Textbox(
            element_id=element_id,
            element_type="textbox",
            x=arguments["x"], y=arguments["y"],
            w=arguments["w"], h=arguments["h"],
            z_order=len(slide.elements),
            text=arguments["text"],
            font_size=arguments.get("font_size", 18),
            font_family=arguments.get("font_family", "Microsoft YaHei"),
            color=arguments.get("color", "#000000"),
            bold=arguments.get("bold", False),
            italic=arguments.get("italic", False),
            align=arguments.get("align", "left"),
            line_spacing=arguments.get("line_spacing", 1.0),
            paragraph_spacing=arguments.get("paragraph_spacing", 0),
        )
        slide.add_element(textbox)
        return json.dumps({"element_id": element_id, "slide_index": slide_index, "position": {"x": arguments["x"], "y": arguments["y"], "w": arguments["w"], "h": arguments["h"]}})

    elif name == "add_image":
        session = session_manager.get_session(arguments["session_id"])
        slide_index = arguments["slide_index"]
        if slide_index < 0 or slide_index >= len(session.slides):
            return json.dumps({"error": f"Slide index {slide_index} out of range"})
        image_path = arguments["image_path"]
        if not Path(image_path).exists():
            return json.dumps({"error": f"Image not found: {image_path}"})
        slide = session.slides[slide_index]
        element_id = f"elem_{len(slide.elements):04d}"
        image = Image(
            element_id=element_id,
            element_type="image",
            x=arguments["x"], y=arguments["y"],
            w=arguments["w"], h=arguments["h"],
            z_order=len(slide.elements),
            image_path=image_path,
        )
        slide.add_element(image)
        return json.dumps({"element_id": element_id, "slide_index": slide_index, "position": {"x": arguments["x"], "y": arguments["y"], "w": arguments["w"], "h": arguments["h"]}})

    elif name == "add_shape":
        session = session_manager.get_session(arguments["session_id"])
        slide_index = arguments["slide_index"]
        if slide_index < 0 or slide_index >= len(session.slides):
            return json.dumps({"error": f"Slide index {slide_index} out of range"})
        shape_type = arguments.get("shape_type", "rectangle")
        if shape_type not in SHAPE_MAP:
            return json.dumps({"error": f"Invalid shape type: {shape_type}"})
        slide = session.slides[slide_index]
        element_id = f"elem_{len(slide.elements):04d}"
        shape = Shape(
            element_id=element_id,
            element_type="shape",
            x=arguments["x"], y=arguments["y"],
            w=arguments["w"], h=arguments["h"],
            z_order=len(slide.elements),
            shape_type=shape_type,
            fill_color=arguments.get("fill_color"),
            border_color=arguments.get("border_color"),
            border_width=arguments.get("border_width", 0),
            border_radius=arguments.get("border_radius", 0),
        )
        slide.add_element(shape)
        return json.dumps({"element_id": element_id, "slide_index": slide_index, "shape_type": shape_type, "position": {"x": arguments["x"], "y": arguments["y"], "w": arguments["w"], "h": arguments["h"]}})

    elif name == "update_textbox":
        session = session_manager.get_session(arguments["session_id"])
        element, slide_index = _find_element(session, arguments["element_id"])
        if element is None:
            return json.dumps({"error": f"Element {arguments['element_id']} not found"})
        if not isinstance(element, Textbox):
            return json.dumps({"error": f"Element is not a textbox"})
        for key in ["x", "y", "w", "h", "text", "font_size", "font_family", "color", "bold", "italic", "align", "line_spacing", "paragraph_spacing"]:
            if key in arguments:
                setattr(element, key, arguments[key])
        return json.dumps({"element_id": element.element_id, "slide_index": slide_index, "updated": element.to_dict()})

    elif name == "update_image":
        session = session_manager.get_session(arguments["session_id"])
        element, slide_index = _find_element(session, arguments["element_id"])
        if element is None:
            return json.dumps({"error": f"Element {arguments['element_id']} not found"})
        if not isinstance(element, Image):
            return json.dumps({"error": f"Element is not an image"})
        if "image_path" in arguments and not Path(arguments["image_path"]).exists():
            return json.dumps({"error": f"Image not found: {arguments['image_path']}"})
        for key in ["x", "y", "w", "h", "image_path"]:
            if key in arguments:
                setattr(element, key, arguments[key])
        return json.dumps({"element_id": element.element_id, "slide_index": slide_index, "updated": element.to_dict()})

    elif name == "update_shape":
        session = session_manager.get_session(arguments["session_id"])
        element, slide_index = _find_element(session, arguments["element_id"])
        if element is None:
            return json.dumps({"error": f"Element {arguments['element_id']} not found"})
        if not isinstance(element, Shape):
            return json.dumps({"error": f"Element is not a shape"})
        if "shape_type" in arguments and arguments["shape_type"] not in SHAPE_MAP:
            return json.dumps({"error": f"Invalid shape type: {arguments['shape_type']}"})
        for key in ["x", "y", "w", "h", "shape_type", "fill_color", "border_color", "border_width", "border_radius"]:
            if key in arguments:
                setattr(element, key, arguments[key])
        return json.dumps({"element_id": element.element_id, "slide_index": slide_index, "updated": element.to_dict()})

    elif name == "delete_element":
        session = session_manager.get_session(arguments["session_id"])
        element, slide_index = _find_element(session, arguments["element_id"])
        if element is None:
            return json.dumps({"error": f"Element {arguments['element_id']} not found"})
        session.slides[slide_index].remove_element(arguments["element_id"])
        return json.dumps({"deleted_element_id": arguments["element_id"], "slide_index": slide_index})

    elif name in ["bring_to_front", "send_to_back", "bring_forward", "send_backward"]:
        session = session_manager.get_session(arguments["session_id"])
        element, slide_index = _find_element(session, arguments["element_id"])
        if element is None:
            return json.dumps({"error": f"Element {arguments['element_id']} not found"})
        slide = session.slides[slide_index]
        if name == "bring_to_front":
            max_z = max((e.z_order for e in slide.elements), default=0)
            element.z_order = max_z + 1
        elif name == "send_to_back":
            min_z = min((e.z_order for e in slide.elements), default=0)
            element.z_order = min_z - 1
        elif name == "bring_forward":
            sorted_elems = sorted(slide.elements, key=lambda e: e.z_order)
            for i, e in enumerate(sorted_elems):
                if e.element_id == element.element_id and i < len(sorted_elems) - 1:
                    next_elem = sorted_elems[i + 1]
                    element.z_order, next_elem.z_order = next_elem.z_order, element.z_order
                    break
        elif name == "send_backward":
            sorted_elems = sorted(slide.elements, key=lambda e: e.z_order)
            for i, e in enumerate(sorted_elems):
                if e.element_id == element.element_id and i > 0:
                    prev_elem = sorted_elems[i - 1]
                    element.z_order, prev_elem.z_order = prev_elem.z_order, element.z_order
                    break
        return json.dumps({"element_id": element.element_id, "z_order": element.z_order})

    elif name == "preview_slides":
        session = session_manager.get_session(arguments["session_id"])
        slide_index = arguments.get("slide_index")
        slides_data = []
        for slide in session.slides:
            if slide_index is not None and slide.index != slide_index:
                continue
            slides_data.append({
                "index": slide.index,
                "background": {
                    "type": slide.background.bg_type,
                    "color": slide.background.color,
                    "gradient_start": slide.background.gradient_start,
                    "gradient_end": slide.background.gradient_end,
                    "gradient_direction": slide.background.gradient_direction,
                    "image_path": slide.background.image_path,
                },
                "elements": [e.to_dict() for e in sorted(slide.elements, key=lambda e: e.z_order)],
            })
        return json.dumps({"session_id": arguments["session_id"], "slide_count": len(session.slides), "slides": slides_data})

    elif name == "export_pptx":
        session = session_manager.get_session(arguments["session_id"])
        output_path = arguments["output_path"]
        if not output_path.endswith(".pptx"):
            output_path += ".pptx"
        pres = session.to_presentation()
        pres.save(output_path)
        return json.dumps({"file_path": str(Path(output_path).resolve()), "slide_count": len(session.slides)})

    else:
        return json.dumps({"error": f"Unknown tool: {name}"})


def _find_element(session, element_id: str):
    """Find an element by ID across all slides. Returns (element, slide_index) or (None, -1)."""
    for i, slide in enumerate(session.slides):
        element = slide.get_element(element_id)
        if element is not None:
            return element, i
    return None, -1
