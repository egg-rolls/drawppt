"""Image element."""

from dataclasses import dataclass
from pathlib import Path

from .base import Element, px_to_emu


@dataclass
class Image(Element):
    """Image element."""

    image_path: str = ""

    def __post_init__(self):
        self.element_type = "image"

    def apply_to_slide(self, pptx_slide) -> None:
        """Apply image to slide."""
        left = px_to_emu(self.x)
        top = px_to_emu(self.y)
        width = px_to_emu(self.w)
        height = px_to_emu(self.h)

        # Validate image path
        if not Path(self.image_path).exists():
            raise FileNotFoundError(f"Image not found: {self.image_path}")

        pptx_slide.shapes.add_picture(
            self.image_path, left, top, width, height
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "image_path": self.image_path,
        })
        return base
