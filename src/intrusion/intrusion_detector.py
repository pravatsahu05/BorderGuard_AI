import time
import uuid

from event import IntrusionEvent
from rules import is_restricted_zone_entry


class IntrusionDetector:
    """
    Converts zone transitions into intrusion events.
    """

    def __init__(
        self,
        camera_id: str = "CAM-01",
    ):

        self.camera_id = camera_id

        self.generated_events = []

    def evaluate(
        self,
        track_id: int,
        object_type: str,
        confidence: float,
        previous_zone,
        current_zone,
        direction: str,
        speed: float,
        dwell_time: float,
        timestamp: float | None = None,
    ):
        """
        Evaluate a tracked object against
        configured intrusion rules.

        Returns:
            IntrusionEvent or None.
        """

        if timestamp is None:
            timestamp = time.time()

        # ----------------------------------------------------
        # Apply restricted-zone entry rule.
        # ----------------------------------------------------

        intrusion = is_restricted_zone_entry(
            previous_zone,
            current_zone,
        )

        if not intrusion:
            return None

        # ----------------------------------------------------
        # Generate unique event ID.
        # ----------------------------------------------------

        event_id = f"EVT-" f"{uuid.uuid4().hex[:8].upper()}"

        # ----------------------------------------------------
        # Create event.
        # ----------------------------------------------------

        event = IntrusionEvent(
            event_id=event_id,
            timestamp=timestamp,
            camera_id=self.camera_id,
            track_id=track_id,
            object_type=object_type,
            confidence=confidence,
            previous_zone=previous_zone,
            current_zone=current_zone,
            direction=direction,
            speed=speed,
            event_type="RESTRICTED_ZONE_ENTRY",
            dwell_time=dwell_time,
            severity="HIGH",
        )

        # ----------------------------------------------------
        # Store generated event.
        # ----------------------------------------------------

        self.generated_events.append(event)

        return event
