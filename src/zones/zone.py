from dataclasses import dataclass


@dataclass
class Zone:
    """
    Represents a surveillance zone.

    Parameters:
        name:
            Human-readable zone name.

        polygon:
            List of (x, y) points defining the zone.
    """

    name: str
    polygon: list[tuple[int, int]]
