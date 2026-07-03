"""Test v0.2 features: update, delete, z-order, insert/delete slide."""

import asyncio
import json
import sys
sys.path.insert(0, "src")

from drawppt.session import SessionManager
from drawppt.slide import Slide, Background
from drawppt.elements import Textbox, Shape


async def test_v02():
    """Test v0.2 features."""
    manager = SessionManager()
    session = manager.create_session()
    print(f"[OK] Session: {session.session_id}")

    # Create 2 slides
    for i in range(2):
        bg = Background(bg_type="solid", color="#FFFFFF")
        slide = Slide(index=i, background=bg)
        session.slides.append(slide)
    print(f"[OK] Created 2 slides")

    # Add elements to slide 0
    tb1 = Textbox(
        element_id="elem_0000", element_type="textbox",
        x=100, y=100, w=400, h=100, z_order=0,
        text="Text Box 1", font_size=24,
    )
    session.slides[0].add_element(tb1)

    tb2 = Textbox(
        element_id="elem_0001", element_type="textbox",
        x=200, y=200, w=400, h=100, z_order=1,
        text="Text Box 2", font_size=24,
    )
    session.slides[0].add_element(tb2)

    shape1 = Shape(
        element_id="elem_0002", element_type="shape",
        x=150, y=150, w=300, h=200, z_order=2,
        shape_type="rectangle", fill_color="#FF0000",
    )
    session.slides[0].add_element(shape1)
    print(f"[OK] Added 3 elements to slide 0")

    # Test 1: Update textbox
    tb1.text = "Updated Text Box 1"
    tb1.font_size = 36
    tb1.color = "#0000FF"
    print(f"[OK] Updated textbox: text='{tb1.text}', size={tb1.font_size}")

    # Test 2: Update shape
    shape1.fill_color = "#00FF00"
    shape1.shape_type = "rounded_rectangle"
    print(f"[OK] Updated shape: fill={shape1.fill_color}, type={shape1.shape_type}")

    # Test 3: Z-order operations
    print(f"\n--- Z-order test ---")
    print(f"Before: tb1={tb1.z_order}, tb2={tb2.z_order}, shape={shape1.z_order}")

    # Bring tb1 to front
    max_z = max(e.z_order for e in session.slides[0].elements)
    tb1.z_order = max_z + 1
    print(f"After bring_to_front: tb1={tb1.z_order}")

    # Send shape to back
    min_z = min(e.z_order for e in session.slides[0].elements)
    shape1.z_order = min_z - 1
    print(f"After send_to_back: shape={shape1.z_order}")

    # Test 4: Insert slide at index 1
    bg_new = Background(bg_type="gradient", gradient_start="#FF0000", gradient_end="#0000FF")
    new_slide = Slide(index=1, background=bg_new)
    session.slides.insert(1, new_slide)
    for i in range(len(session.slides)):
        session.slides[i].index = i
    print(f"\n[OK] Inserted slide at index 1, total: {len(session.slides)}")

    # Test 5: Delete slide at index 2
    session.slides.pop(2)
    for i in range(len(session.slides)):
        session.slides[i].index = i
    print(f"[OK] Deleted slide at index 2, total: {len(session.slides)}")

    # Preview
    slides_data = []
    for s in session.slides:
        slide_data = {
            "index": s.index,
            "background": {"type": s.background.bg_type, "color": s.background.color},
            "elements": [e.to_dict() for e in sorted(s.elements, key=lambda e: e.z_order)],
        }
        slides_data.append(slide_data)

    print(f"\n[OK] Preview:")
    print(json.dumps({
        "session_id": session.session_id,
        "slide_count": len(session.slides),
        "slides": slides_data,
    }, indent=2, ensure_ascii=False))

    # Export
    output = "test_v02.pptx"
    pres = session.to_presentation()
    pres.save(output)
    print(f"\n[OK] Exported: {output}")

    manager.delete_session(session.session_id)
    print("[DONE] v0.2 tests complete!")


if __name__ == "__main__":
    asyncio.run(test_v02())
