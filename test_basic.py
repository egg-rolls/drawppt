"""Basic test script for DrawPPT."""

import asyncio
import json
import sys
sys.path.insert(0, "src")

from drawppt.session import SessionManager
from drawppt.slide import Slide, Background
from drawppt.elements import Textbox, Image, Shape


async def test_basic_flow():
    """Test basic create -> add elements -> export flow."""
    manager = SessionManager()

    # 1. Create session
    session = manager.create_session()
    print(f"[OK] Created session: {session.session_id}")

    # 2. Add slide
    background = Background(bg_type="solid", color="#FFFFFF")
    slide = Slide(index=0, background=background)
    session.slides.append(slide)
    print(f"[OK] Added slide 0")

    # 3. Add textbox
    textbox = Textbox(
        element_id="elem_0000",
        element_type="textbox",
        x=100, y=100, w=800, h=100,
        z_order=0,
        text="Hello DrawPPT!",
        font_size=36,
        bold=True,
        color="#333333",
    )
    slide.add_element(textbox)
    print(f"[OK] Added textbox: {textbox.text}")

    # 4. Add shape
    shape = Shape(
        element_id="elem_0001",
        element_type="shape",
        x=100, y=300, w=400, h=300,
        z_order=1,
        shape_type="rectangle",
        fill_color="#4A90D9",
    )
    slide.add_element(shape)
    print(f"[OK] Added shape: {shape.shape_type}")

    # 5. Preview (JSON)
    slides_data = []
    for s in session.slides:
        slide_data = {
            "index": s.index,
            "background": {"type": s.background.bg_type, "color": s.background.color},
            "elements": [e.to_dict() for e in s.elements],
        }
        slides_data.append(slide_data)

    preview = {
        "session_id": session.session_id,
        "slide_count": len(session.slides),
        "slides": slides_data,
    }
    print(f"[OK] Preview JSON:")
    print(json.dumps(preview, indent=2, ensure_ascii=False))

    # 6. Export PPTX
    output_path = "test_output.pptx"
    pres = session.to_presentation()
    pres.save(output_path)
    print(f"[OK] Exported to: {output_path}")

    # Cleanup
    manager.delete_session(session.session_id)
    print(f"[OK] Session deleted")

    print("\n[DONE] All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_basic_flow())
