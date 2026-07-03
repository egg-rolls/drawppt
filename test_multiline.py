"""Test multiline text and complex layout."""

import asyncio
import json
import sys
sys.path.insert(0, "src")

from drawppt.session import SessionManager
from drawppt.slide import Slide, Background
from drawppt.elements import Textbox, Shape


async def test_multiline():
    """Test multiline text with proper formatting."""
    manager = SessionManager()
    session = manager.create_session()
    print(f"[OK] Session: {session.session_id}")

    # Slide 1 - Title slide
    bg1 = Background(bg_type="gradient", gradient_start="#1a1a2e", gradient_end="#16213e")
    slide1 = Slide(index=0, background=bg1)
    session.slides.append(slide1)

    # Title textbox with multiline
    title = Textbox(
        element_id="elem_0000",
        element_type="textbox",
        x=100, y=200, w=1720, h=200,
        z_order=0,
        text="DrawPPT Demo\nMultiline Title Support",
        font_size=48,
        bold=True,
        color="#FFFFFF",
        align="center",
        line_spacing=1.5,
        paragraph_spacing=20,
    )
    slide1.add_element(title)

    # Subtitle
    subtitle = Textbox(
        element_id="elem_0001",
        element_type="textbox",
        x=100, y=500, w=1720, h=100,
        z_order=1,
        text="Created by AI Agent using DrawPPT MCP",
        font_size=24,
        color="#CCCCCC",
        align="center",
    )
    slide1.add_element(subtitle)

    # Slide 2 - Content slide
    bg2 = Background(bg_type="solid", color="#FFFFFF")
    slide2 = Slide(index=1, background=bg2)
    session.slides.append(slide2)

    # Left column shape
    left_shape = Shape(
        element_id="elem_0002",
        element_type="shape",
        x=50, y=50, w=900, h=980,
        z_order=0,
        shape_type="rounded_rectangle",
        fill_color="#F0F0F0",
        border_color="#CCCCCC",
        border_width=2,
    )
    slide2.add_element(left_shape)

    # Left column text
    left_text = Textbox(
        element_id="elem_0003",
        element_type="textbox",
        x=100, y=100, w=800, h=900,
        z_order=1,
        text="Features:\n\n"
             "- Pixel-precise positioning\n"
             "- Multi-line text support\n"
             "- Shape primitives\n"
             "- Gradient backgrounds\n"
             "- JSON preview mode",
        font_size=20,
        color="#333333",
        line_spacing=1.2,
        paragraph_spacing=10,
    )
    slide2.add_element(left_text)

    # Right column shape
    right_shape = Shape(
        element_id="elem_0004",
        element_type="shape",
        x=970, y=50, w=900, h=980,
        z_order=0,
        shape_type="rectangle",
        fill_color="#4A90D9",
    )
    slide2.add_element(right_shape)

    # Right column text
    right_text = Textbox(
        element_id="elem_0005",
        element_type="textbox",
        x=1020, y=100, w=800, h=900,
        z_order=1,
        text="Use Cases:\n\n"
             "1. Auto-generate presentations\n"
             "2. Image layout composition\n"
             "3. Template filling\n"
             "4. Iterative refinement",
        font_size=20,
        color="#FFFFFF",
        line_spacing=1.2,
        paragraph_spacing=10,
    )
    slide2.add_element(right_text)

    # Preview JSON
    slides_data = []
    for s in session.slides:
        slide_data = {
            "index": s.index,
            "background": {
                "type": s.background.bg_type,
                "color": s.background.color,
                "gradient": {
                    "start": s.background.gradient_start,
                    "end": s.background.gradient_end,
                } if s.background.bg_type == "gradient" else None,
            },
            "elements": [e.to_dict() for e in s.elements],
        }
        slides_data.append(slide_data)

    print(f"\n[OK] Preview:")
    print(json.dumps({
        "session_id": session.session_id,
        "slide_count": len(session.slides),
        "slides": slides_data,
    }, indent=2, ensure_ascii=False))

    # Export
    output = "test_multiline.pptx"
    pres = session.to_presentation()
    pres.save(output)
    print(f"\n[OK] Exported: {output}")

    # Cleanup
    manager.delete_session(session.session_id)
    print("[DONE] Test complete!")


if __name__ == "__main__":
    asyncio.run(test_multiline())
