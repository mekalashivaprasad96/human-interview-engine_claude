"""
Human Communication Module
Generates natural, human-like spoken responses with appropriate personality and seniority.
"""

from .response_generator import ResponseGenerator
from .style_adapter import StyleAdapter
from .persona_renderer import PersonaRenderer

__all__ = [
    "ResponseGenerator",
    "StyleAdapter",
    "PersonaRenderer",
]