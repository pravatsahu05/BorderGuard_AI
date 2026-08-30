import math


def calculate_direction(
    previous_pos: tuple,
    current_pos: tuple,
    threshold: float = 2.0,
) -> str:
    """
    Calculate direction of movement between two consecutive positions.

    Parameters:
        previous_pos: (x, y) tuple of previous position
        current_pos: (x, y) tuple of current position
        threshold: minimum displacement distance to register movement

    Returns:
        Direction string (e.g., "DOWN", "DOWN-RIGHT", "UP", "STATIONARY").
    """

    dx = current_pos[0] - previous_pos[0]
    dy = current_pos[1] - previous_pos[1]

    distance = math.hypot(dx, dy)

    if distance < threshold:
        return "STATIONARY"

    # Angle in degrees (-180 to 180)
    # Note: image y-axis increases downwards
    angle = math.degrees(math.atan2(dy, dx))

    if -22.5 <= angle < 22.5:
        return "RIGHT"
    elif 22.5 <= angle < 67.5:
        return "DOWN-RIGHT"
    elif 67.5 <= angle < 112.5:
        return "DOWN"
    elif 112.5 <= angle < 157.5:
        return "DOWN-LEFT"
    elif angle >= 157.5 or angle < -157.5:
        return "LEFT"
    elif -157.5 <= angle < -112.5:
        return "UP-LEFT"
    elif -112.5 <= angle < -67.5:
        return "UP"
    elif -67.5 <= angle < -22.5:
        return "UP-RIGHT"

    return "STATIONARY"
