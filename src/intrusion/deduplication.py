import time


class EventDeduplicator:
    """
    Prevents repeated events for the same track
    within a configurable cooldown period.
    """

    def __init__(
        self,
        cooldown_seconds: float = 10.0,
    ):

        self.cooldown_seconds = cooldown_seconds

        self.last_event_time = {}

    def should_create_event(
        self,
        track_id: int,
        current_time: float | None = None,
    ) -> bool:

        if current_time is None:
            current_time = time.time()

        last_time = self.last_event_time.get(track_id)

        # No previous event.
        if last_time is None:

            self.last_event_time[track_id] = current_time

            return True

        elapsed = current_time - last_time

        if elapsed >= self.cooldown_seconds:

            self.last_event_time[track_id] = current_time

            return True

        return False
