import math


def calculate_pixel_speed(
    previous: tuple[float, float],
    current: tuple[float, float],
    delta_time: float,
) -> float:
    """
    Calculate approximate image-plane speed.

    Returns:
        Pixels per second.
    """

    if delta_time <= 0:
        return 0.0

    previous_x, previous_y = previous
    current_x, current_y = current

    dx = current_x - previous_x
    dy = current_y - previous_y

    distance = math.sqrt(dx * dx + dy * dy)

    return distance / delta_time
