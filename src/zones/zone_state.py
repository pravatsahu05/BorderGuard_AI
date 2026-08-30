from dataclasses import dataclass
from typing import Optional


@dataclass
class ZoneState:
    """
    Stores the current and previous zone
    of a tracked object.
    """

    current_zone: Optional[str] = None

    previous_zone: Optional[str] = None

    entered_at: Optional[float] = None


class ZoneStateManager:
    """
    Maintains zone state for every tracked object.
    """

    def __init__(self):

        self.states: dict[int, ZoneState] = {}

    def update(
        self,
        track_id: int,
        zone_name: Optional[str],
        timestamp: float,
    ) -> ZoneState:
        """
        Update the zone state for a tracked object.
        """

        if track_id not in self.states:

            self.states[track_id] = ZoneState()

        state = self.states[track_id]

        # ----------------------------------------------------
        # Detect zone transition.
        # ----------------------------------------------------

        if zone_name != state.current_zone:

            state.previous_zone = state.current_zone

            state.current_zone = zone_name

            state.entered_at = timestamp

        return state

    def get(
        self,
        track_id: int,
    ) -> Optional[ZoneState]:

        return self.states.get(track_id)

    def get_dwell_time(
        self,
        track_id: int,
        current_timestamp: float,
    ) -> float:

        state = self.states.get(track_id)

        if state is None:
            return 0.0

        if state.entered_at is None:
            return 0.0

        return max(
            0.0,
            current_timestamp - state.entered_at,
        )
