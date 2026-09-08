"""
Virtual object used by the BorderGuard AI simulator.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class SimulatedObject:
    """
    Represents a virtual tracked object.

    Parameters
    ----------
    track_id:
        Unique tracking ID.

    object_type:
        Type of object, e.g. person or vehicle.

    x, y:
        Current position.

    vx, vy:
        Velocity in pixels per second.
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
    ) -> None:
        """
        Update object position.
        """

        self.x += self.vx * delta_time

        self.y += self.vy * delta_time

    @property
    def center(
        self,
    ) -> Tuple[float, float]:
        """
        Return the object's current center.
        """

        return (
            self.x,
            self.y,
        )

    def set_velocity(
        self,
        vx: float,
        vy: float,
    ) -> None:
        """
        Change the object's velocity.
        """

        self.vx = vx

        self.vy = vy

    def stop(self) -> None:
        """
        Stop the object.
        """

        self.vx = 0.0

        self.vy = 0.0
