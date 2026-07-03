"""Session management for DrawPPT."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from pptx import Presentation
from pptx.util import Emu

from .slide import Slide


@dataclass
class Session:
    """Represents a PPTX editing session."""

    session_id: str
    width: int = 1920
    height: int = 1080
    slides: List[Slide] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_presentation(self) -> Presentation:
        """Convert session to python-pptx Presentation."""
        pres = Presentation()
        # Set slide dimensions (1920x1080 at 96 DPI)
        pres.slide_width = Emu(18288000)   # 1920 * 914400 / 96
        pres.slide_height = Emu(10287000)  # 1080 * 914400 / 96

        for slide in self.slides:
            slide.apply_to_presentation(pres)

        return pres


class SessionManager:
    """Manages multiple editing sessions."""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create_session(self) -> Session:
        """Create a new session."""
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        session = Session(session_id=session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Session:
        """Get session by ID."""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        return self._sessions[session_id]

    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        del self._sessions[session_id]
