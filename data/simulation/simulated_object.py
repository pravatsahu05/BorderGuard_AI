from dataclasses import dataclass


@dataclass
class SimulatedObject:
    """
    Represents an object inside the software border simulator.
    """

    track_id: int

    object_type: str

    x: float

    y: float

    vx: float = 0.0

    vy: float = 0.0

    confidence: float = 0.95

    active: bool = True

    def update(
        self,
        delta_time: float,
    ):
        """
        Update object position according to velocity.
        """

        self.x += self.vx * delta_time

        self.y += self.vy * delta_time

    @property
    def center(self):
        """
        Return the object's center point.
        """

        return (
            self.x,
            self.y,
        )

    def set_velocity(
        self,
        vx: float,
        vy: float,
    ):
        """
        Change the object's velocity.
        """

        self.vx = vx
        self.vy = vy

    def stop(self):
        """
        Stop the object.
        """

        self.vx = 0.0
        self.vy = 0.0
