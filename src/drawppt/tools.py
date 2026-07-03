"""MCP tool definitions."""

import json
from pathlib import Path
from typing import Optional

from mcp.server import Server
from mcp.types import TextContent

from .session import SessionManager
from .slide import Slide, Background
from .elements import Textbox, Image, Shape
from .elements.shape import SHAPE_MAP


def register_tools(server: Server, session_manager: SessionManager):
    """Register all MCP tools."""

    # ==================== Session Tools ====================

    @server.tool()
    async def create_session() -> str:
        """Create a new PPTX editing session."""
        session = session_manager.create_session()
        return json.dumps({
            "session_id": session.session_id,
            "width": session.width,
            "height": session.height,
            "slide_count": 0,
        })

    @server.tool()
    async def delete_session(session_id: str) -> str:
        """Delete a session and its temporary files."""
        session_manager.delete_session(session_id)
        return json.dumps({"success": True})

    # ==================== Slide Tools ====================

    @server.tool()
    async def add_slide(
        session_id: str,
        bg_type: str = "none",
        color: Optional[str] = None,
        gradient_start: Optional[str] = None,
        gradient_end: Optional[str] = None,
        gradient_direction: str = "vertical",
        image_path: Optional[str] = None,
    ) -> str:
        """Add a new blank slide to the end of the presentation."""
        session = session_manager.get_session(session_id)
        background = Background(
            bg_type=bg_type,
            color=color,
            gradient_start=gradient_start,
            gradient_end=gradient_end,
            gradient_direction=gradient_direction,
            image_path=image_path,
        )
        slide = Slide(index=len(session.slides), background=background)
        session.slides.append(slide)
        return json.dumps({
            "slide_index": slide.index,
            "total_slides": len(session.slides),
        })

    @server.tool()
    async def insert_slide(
        session_id: str,
        slide_index: int,
        bg_type: str = "none",
        color: Optional[str] = None,
        gradient_start: Optional[str] = None,
        gradient_end: Optional[str] = None,
        gradient_direction: str = "vertical",
        image_path: Optional[str] = None,
    ) -> str:
        """Insert a new slide at the specified position."""
        session = session_manager.get_session(session_id)

        if slide_index < 0 or slide_index > len(session.slides):
            return json.dumps({"error": f"Slide index {slide_index} out of range"})

        background = Background(
            bg_type=bg_type,
            color=color,
            gradient_start=gradient_start,
            gradient_end=gradient_end,
            gradient_direction=gradient_direction,
            image_path=image_path,
        )
        slide = Slide(index=slide_index, background=background)
        session.slides.insert(slide_index, slide)

        # Update indices for subsequent slides
        for i in range(slide_index + 1, len(session.slides)):
            session.slides[i].index = i

        return json.dumps({
            "slide_index": slide_index,
            "total_slides": len(session.slides),
        })

    @server.tool()
    async def delete_slide(session_id: str, slide_index: int) -> str:
        """Delete a slide at the specified position."""
        session = session_manager.get_session(session_id)

        if slide_index < 0 or slide_index >= len(session.slides):
            return json.dumps({"error": f"Slide index {slide_index} out of range"})

        session.slides.pop(slide_index)

        # Update indices for subsequent slides
        for i in range(slide_index, len(session.slides)):
            session.slides[i].index = i

        return json.dumps({
            "deleted_index": slide_index,
            "total_slides": len(session.slides),
        })

    # ==================== Element Add Tools ====================

    @server.tool()
    async def add_textbox(
        session_id: str,
        slide_index: int,
        x: int,
        y: int,
        w: int,
        h: int,
        text: str,
        font_size: int = 18,
        font_family: str = "微软雅黑",
        color: str = "#000000",
        bold: bool = False,
        italic: bool = False,
        align: str = "left",
        line_spacing: float = 1.0,
        paragraph_spacing: int = 0,
    ) -> str:
        """Add a text box to a slide."""
        session = session_manager.get_session(session_id)

        if slide_index < 0 or slide_index >= len(session.slides):
            return json.dumps({"error": f"Slide index {slide_index} out of range"})

        slide = session.slides[slide_index]
        element_id = f"elem_{len(slide.elements):04d}"

        textbox = Textbox(
            element_id=element_id,
            element_type="textbox",
            x=x, y=y, w=w, h=h,
            z_order=len(slide.elements),
            text=text,
            font_size=font_size,
            font_family=font_family,
            color=color,
            bold=bold,
            italic=italic,
            align=align,
            line_spacing=line_spacing,
            paragraph_spacing=paragraph_spacing,
        )

        slide.add_element(textbox)
        return json.dumps({
            "element_id": element_id,
            "slide_index": slide_index,
            "position": {"x": x, "y": y, "w": w, "h": h},
        })

    @server.tool()
    async def add_image(
        session_id: str,
        slide_index: int,
        x: int,
        y: int,
        w: int,
        h: int,
        image_path: str,
    ) -> str:
        """Add an image to a slide."""
        session = session_manager.get_session(session_id)

        if slide_index < 0 or slide_index >= len(session.slides):
            return json.dumps({"error": f"Slide index {slide_index} out of range"})

        # Validate image path
        if not Path(image_path).exists():
            return json.dumps({"error": f"Image not found: {image_path}"})

        slide = session.slides[slide_index]
        element_id = f"elem_{len(slide.elements):04d}"

        image = Image(
            element_id=element_id,
            element_type="image",
            x=x, y=y, w=w, h=h,
            z_order=len(slide.elements),
            image_path=image_path,
        )

        slide.add_element(image)
        return json.dumps({
            "element_id": element_id,
            "slide_index": slide_index,
            "position": {"x": x, "y": y, "w": w, "h": h},
        })

    @server.tool()
    async def add_shape(
        session_id: str,
        slide_index: int,
        x: int,
        y: int,
        w: int,
        h: int,
        shape_type: str = "rectangle",
        fill_color: Optional[str] = None,
        border_color: Optional[str] = None,
        border_width: int = 0,
        border_radius: int = 0,
    ) -> str:
        """Add a shape to a slide."""
        session = session_manager.get_session(session_id)

        if slide_index < 0 or slide_index >= len(session.slides):
            return json.dumps({"error": f"Slide index {slide_index} out of range"})

        # Validate shape type
        if shape_type not in SHAPE_MAP:
            return json.dumps({"error": f"Invalid shape type: {shape_type}"})

        slide = session.slides[slide_index]
        element_id = f"elem_{len(slide.elements):04d}"

        shape = Shape(
            element_id=element_id,
            element_type="shape",
            x=x, y=y, w=w, h=h,
            z_order=len(slide.elements),
            shape_type=shape_type,
            fill_color=fill_color,
            border_color=border_color,
            border_width=border_width,
            border_radius=border_radius,
        )

        slide.add_element(shape)
        return json.dumps({
            "element_id": element_id,
            "slide_index": slide_index,
            "shape_type": shape_type,
            "position": {"x": x, "y": y, "w": w, "h": h},
        })

    # ==================== Element Update Tools ====================

    @server.tool()
    async def update_textbox(
        session_id: str,
        element_id: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        w: Optional[int] = None,
        h: Optional[int] = None,
        text: Optional[str] = None,
        font_size: Optional[int] = None,
        font_family: Optional[str] = None,
        color: Optional[str] = None,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
        align: Optional[str] = None,
        line_spacing: Optional[float] = None,
        paragraph_spacing: Optional[int] = None,
    ) -> str:
        """Update a text box's properties. Only specified fields will be updated."""
        session = session_manager.get_session(session_id)
        element, slide_index = _find_element(session, element_id)

        if element is None:
            return json.dumps({"error": f"Element {element_id} not found"})

        if not isinstance(element, Textbox):
            return json.dumps({"error": f"Element {element_id} is not a textbox"})

        # Update fields
        if x is not None: element.x = x
        if y is not None: element.y = y
        if w is not None: element.w = w
        if h is not None: element.h = h
        if text is not None: element.text = text
        if font_size is not None: element.font_size = font_size
        if font_family is not None: element.font_family = font_family
        if color is not None: element.color = color
        if bold is not None: element.bold = bold
        if italic is not None: element.italic = italic
        if align is not None: element.align = align
        if line_spacing is not None: element.line_spacing = line_spacing
        if paragraph_spacing is not None: element.paragraph_spacing = paragraph_spacing

        return json.dumps({
            "element_id": element_id,
            "slide_index": slide_index,
            "updated": element.to_dict(),
        })

    @server.tool()
    async def update_image(
        session_id: str,
        element_id: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        w: Optional[int] = None,
        h: Optional[int] = None,
        image_path: Optional[str] = None,
    ) -> str:
        """Update an image's properties. Only specified fields will be updated."""
        session = session_manager.get_session(session_id)
        element, slide_index = _find_element(session, element_id)

        if element is None:
            return json.dumps({"error": f"Element {element_id} not found"})

        if not isinstance(element, Image):
            return json.dumps({"error": f"Element {element_id} is not an image"})

        # Validate image path if provided
        if image_path is not None and not Path(image_path).exists():
            return json.dumps({"error": f"Image not found: {image_path}"})

        # Update fields
        if x is not None: element.x = x
        if y is not None: element.y = y
        if w is not None: element.w = w
        if h is not None: element.h = h
        if image_path is not None: element.image_path = image_path

        return json.dumps({
            "element_id": element_id,
            "slide_index": slide_index,
            "updated": element.to_dict(),
        })

    @server.tool()
    async def update_shape(
        session_id: str,
        element_id: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        w: Optional[int] = None,
        h: Optional[int] = None,
        shape_type: Optional[str] = None,
        fill_color: Optional[str] = None,
        border_color: Optional[str] = None,
        border_width: Optional[int] = None,
        border_radius: Optional[int] = None,
    ) -> str:
        """Update a shape's properties. Only specified fields will be updated."""
        session = session_manager.get_session(session_id)
        element, slide_index = _find_element(session, element_id)

        if element is None:
            return json.dumps({"error": f"Element {element_id} not found"})

        if not isinstance(element, Shape):
            return json.dumps({"error": f"Element {element_id} is not a shape"})

        # Validate shape type if provided
        if shape_type is not None and shape_type not in SHAPE_MAP:
            return json.dumps({"error": f"Invalid shape type: {shape_type}"})

        # Update fields
        if x is not None: element.x = x
        if y is not None: element.y = y
        if w is not None: element.w = w
        if h is not None: element.h = h
        if shape_type is not None: element.shape_type = shape_type
        if fill_color is not None: element.fill_color = fill_color
        if border_color is not None: element.border_color = border_color
        if border_width is not None: element.border_width = border_width
        if border_radius is not None: element.border_radius = border_radius

        return json.dumps({
            "element_id": element_id,
            "slide_index": slide_index,
            "updated": element.to_dict(),
        })

    # ==================== Element Delete Tool ====================

    @server.tool()
    async def delete_element(session_id: str, element_id: str) -> str:
        """Delete an element from a slide."""
        session = session_manager.get_session(session_id)
        element, slide_index = _find_element(session, element_id)

        if element is None:
            return json.dumps({"error": f"Element {element_id} not found"})

        slide = session.slides[slide_index]
        slide.remove_element(element_id)

        return json.dumps({
            "deleted_element_id": element_id,
            "slide_index": slide_index,
        })

    # ==================== Z-Order Tools ====================

    @server.tool()
    async def bring_to_front(session_id: str, element_id: str) -> str:
        """Bring an element to the front (top layer)."""
        session = session_manager.get_session(session_id)
        element, slide_index = _find_element(session, element_id)

        if element is None:
            return json.dumps({"error": f"Element {element_id} not found"})

        slide = session.slides[slide_index]
        max_z = max((e.z_order for e in slide.elements), default=0)
        element.z_order = max_z + 1

        return json.dumps({
            "element_id": element_id,
            "z_order": element.z_order,
        })

    @server.tool()
    async def send_to_back(session_id: str, element_id: str) -> str:
        """Send an element to the back (bottom layer)."""
        session = session_manager.get_session(session_id)
        element, slide_index = _find_element(session, element_id)

        if element is None:
            return json.dumps({"error": f"Element {element_id} not found"})

        slide = session.slides[slide_index]
        min_z = min((e.z_order for e in slide.elements), default=0)
        element.z_order = min_z - 1

        return json.dumps({
            "element_id": element_id,
            "z_order": element.z_order,
        })

    @server.tool()
    async def bring_forward(session_id: str, element_id: str) -> str:
        """Move an element one layer up."""
        session = session_manager.get_session(session_id)
        element, slide_index = _find_element(session, element_id)

        if element is None:
            return json.dumps({"error": f"Element {element_id} not found"})

        slide = session.slides[slide_index]
        sorted_elements = sorted(slide.elements, key=lambda e: e.z_order)

        for i, e in enumerate(sorted_elements):
            if e.element_id == element_id and i < len(sorted_elements) - 1:
                # Swap z_order with next element
                next_elem = sorted_elements[i + 1]
                element.z_order, next_elem.z_order = next_elem.z_order, element.z_order
                break

        return json.dumps({
            "element_id": element_id,
            "z_order": element.z_order,
        })

    @server.tool()
    async def send_backward(session_id: str, element_id: str) -> str:
        """Move an element one layer down."""
        session = session_manager.get_session(session_id)
        element, slide_index = _find_element(session, element_id)

        if element is None:
            return json.dumps({"error": f"Element {element_id} not found"})

        slide = session.slides[slide_index]
        sorted_elements = sorted(slide.elements, key=lambda e: e.z_order)

        for i, e in enumerate(sorted_elements):
            if e.element_id == element_id and i > 0:
                # Swap z_order with previous element
                prev_elem = sorted_elements[i - 1]
                element.z_order, prev_elem.z_order = prev_elem.z_order, element.z_order
                break

        return json.dumps({
            "element_id": element_id,
            "z_order": element.z_order,
        })

    # ==================== Preview & Export Tools ====================

    @server.tool()
    async def preview_slides(
        session_id: str,
        format: str = "json",
        slide_index: Optional[int] = None,
    ) -> str:
        """Preview the current draft presentation. format: 'json'"""
        session = session_manager.get_session(session_id)

        if format == "json":
            slides_data = []
            for slide in session.slides:
                if slide_index is not None and slide.index != slide_index:
                    continue

                slide_data = {
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
                }
                slides_data.append(slide_data)

            return json.dumps({
                "session_id": session_id,
                "slide_count": len(session.slides),
                "slides": slides_data,
            })
        else:
            return json.dumps({"error": "PNG preview not implemented yet"})

    @server.tool()
    async def export_pptx(session_id: str, output_path: str) -> str:
        """Export the presentation to a PPTX file."""
        session = session_manager.get_session(session_id)

        # Convert to presentation
        pres = session.to_presentation()

        # Ensure output path ends with .pptx
        if not output_path.endswith(".pptx"):
            output_path += ".pptx"

        # Save
        pres.save(output_path)

        return json.dumps({
            "file_path": str(Path(output_path).resolve()),
            "slide_count": len(session.slides),
        })


def _find_element(session, element_id: str):
    """Find an element by ID across all slides. Returns (element, slide_index) or (None, -1)."""
    for i, slide in enumerate(session.slides):
        element = slide.get_element(element_id)
        if element is not None:
            return element, i
    return None, -1
