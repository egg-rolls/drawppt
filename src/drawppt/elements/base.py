"""Base element class."""

from dataclasses import dataclass
from abc import ABC, abstractmethod

# Design coordinates to EMU conversion
# 1920px = 18288000 EMU at 96 DPI
EMU_PER_PX = 18288000 / 1920  # = 9525


def px_to_emu(px: int) -> int:
    """Convert pixels to EMU."""
    return int(px * EMU_PER_PX)


@dataclass
class Element(ABC):
    """Base class for all slide elements."""

    element_id: str
    element_type: str  # 'textbox' | 'image' | 'shape'
    x: int
    y: int
    w: int
    h: int
    z_order: int = 0

    @abstractmethod
    def apply_to_slide(self, pptx_slide) -> None:
        """Apply this element to a python-pptx slide."""
        pass

    def to_dict(self) -> dict:
        """Convert element to dictionary for JSON preview."""
        return {
            "element_id": self.element_id,
            "element_type": self.element_type,
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "z_order": self.z_order,
        }
