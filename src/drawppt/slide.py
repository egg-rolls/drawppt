"""Slide management."""

from dataclasses import dataclass, field
from typing import List, Optional

from pptx import Presentation
from pptx.util import Emu

from .elements.base import Element


@dataclass
class Background:
    """Slide background configuration."""

    bg_type: str = "none"  # 'none' | 'solid' | 'gradient' | 'image'
    color: Optional[str] = None
    gradient_start: Optional[str] = None
    gradient_end: Optional[str] = None
    gradient_direction: str = "vertical"  # 'horizontal' | 'vertical'
    image_path: Optional[str] = None


@dataclass
class Slide:
    """Represents a single slide."""

    index: int
    background: Background = field(default_factory=Background)
    elements: List[Element] = field(default_factory=list)

    def add_element(self, element: Element) -> None:
        """Add an element to the slide."""
        self.elements.append(element)

    def remove_element(self, element_id: str) -> None:
        """Remove an element by ID."""
        self.elements = [e for e in self.elements if e.element_id != element_id]

    def get_element(self, element_id: str) -> Optional[Element]:
        """Get element by ID."""
        for e in self.elements:
            if e.element_id == element_id:
                return e
        return None

    def apply_to_presentation(self, pres: Presentation) -> None:
        """Apply this slide to a Presentation object."""
        # Use blank layout
        blank_layout = pres.slide_layouts[6]  # Blank layout
        pptx_slide = pres.slides.add_slide(blank_layout)

        # Apply background
        self._apply_background(pptx_slide)

        # Apply elements in z-order
        sorted_elements = sorted(self.elements, key=lambda e: e.z_order)
        for element in sorted_elements:
            element.apply_to_slide(pptx_slide)

    def _apply_background(self, pptx_slide) -> None:
        """Apply background to the slide."""
        if self.background.bg_type == "none":
            return

        background = pptx_slide.background
        fill = background.fill

        if self.background.bg_type == "solid":
            fill.solid()
            fill.fore_color.rgb = _hex_to_rgb(self.background.color)

        elif self.background.bg_type == "gradient":
            fill.gradient()
            fill.gradient_stops[0].color.rgb = _hex_to_rgb(self.background.gradient_start)
            fill.gradient_stops[1].color.rgb = _hex_to_rgb(self.background.gradient_end)

        elif self.background.bg_type == "image":
            # Image background requires adding a full-slide image
            pass


def _hex_to_rgb(hex_color: str):
    """Convert hex color string to RGBColor."""
    from pptx.dml.color import RGBColor

    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return RGBColor(r, g, b)
