from collections import defaultdict, deque


class TrackHistory:
    """
    Stores recent center positions for tracked objects.
    """

    def __init__(
        self,
        max_history: int = 30,
    ):

        self.max_history = max_history

        self.history = defaultdict(lambda: deque(maxlen=self.max_history))

    def update(
        self,
        track_id: int,
        center: tuple[float, float],
    ):
        """
        Add a new position for a tracked object.
        """

        self.history[track_id].append(center)

    def get(
        self,
        track_id: int,
    ):
        """
        Return the stored trajectory.
        """

        return list(self.history.get(track_id, []))

    def clear(
        self,
        track_id: int,
    ):
        """
        Remove history for a track.
        """

        self.history.pop(
            track_id,
            None,
        )
