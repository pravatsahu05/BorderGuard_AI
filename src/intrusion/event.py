from dataclasses import dataclass
from typing import Optional


@dataclass
class IntrusionEvent:
    """
    Represents a detected intrusion event.
    """

    event_id: str
    timestamp: float

    camera_id: str
    track_id: int

    object_type: str
    confidence: float

    previous_zone: Optional[str]
    current_zone: Optional[str]

    direction: str
    speed: float

    event_type: str

    dwell_time: float

    severity: str = "HIGH"
