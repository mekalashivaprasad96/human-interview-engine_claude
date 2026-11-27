"""
Follow-up Intelligence Module
Handles follow-up question processing and consistency maintenance.
"""

from .followup_handler import FollowUpHandler
from .consistency_maintainer import ConsistencyMaintainer

__all__ = [
    "FollowUpHandler",
    "ConsistencyMaintainer",
]