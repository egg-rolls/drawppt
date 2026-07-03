"""Shape element."""

from dataclasses import dataclass
from typing import Optional

from pptx.enum.shapes import MSO_SHAPE

from .base import Element, px_to_emu

# Map shape type strings to python-pptx enums
SHAPE_MAP = {
    "rectangle": MSO_SHAPE.RECTANGLE,
    "rounded_rectangle": MSO_SHAPE.ROUNDED_RECTANGLE,
    "oval": MSO_SHAPE.OVAL,
    "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE,
    "arrow_right": MSO_SHAPE.RIGHT_ARROW,
    "arrow_up": MSO_SHAPE.UP_ARROW,
    "star": MSO_SHAPE.STAR_5_POINT,
    "hexagon": MSO_SHAPE.HEXAGON,
}


@dataclass
class Shape(Element):
    """Shape element."""

    shape_type: str = "rectangle"
    fill_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: int = 0
    border_radius: int = 0

    def __post_init__(self):
        self.element_type = "shape"

    def apply_to_slide(self, pptx_slide) -> None:
        """Apply shape to slide."""
        left = px_to_emu(self.x)
        top = px_to_emu(self.y)
        width = px_to_emu(self.w)
        height = px_to_emu(self.h)

        # Get shape type
        if self.shape_type not in SHAPE_MAP:
            raise ValueError(f"Invalid shape type: {self.shape_type}")

        mso_shape = SHAPE_MAP[self.shape_type]
        shape = pptx_slide.shapes.add_shape(mso_shape, left, top, width, height)

        # Fill color
        if self.fill_color:
            shape.fill.solid()
            shape.fill.fore_color.rgb = self._hex_to_rgb(self.fill_color)

        # Border
        if self.border_color:
            shape.line.color.rgb = self._hex_to_rgb(self.border_color)
            shape.line.width = px_to_emu(self.border_width)

    def _hex_to_rgb(self, hex_color: str):
        """Convert hex color to RGBColor."""
        from pptx.dml.color import RGBColor

        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return RGBColor(r, g, b)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "shape_type": self.shape_type,
            "fill_color": self.fill_color,
            "border_color": self.border_color,
            "border_width": self.border_width,
            "border_radius": self.border_radius,
        })
        return base
