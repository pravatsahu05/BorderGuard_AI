from simulated_object import SimulatedObject


VIDEO_WIDTH = 960
VIDEO_HEIGHT = 540


def create_normal_patrol():
    """
    Object moves horizontally inside the safe zone.
    """

    return [
        SimulatedObject(
            track_id=1,
            object_type="person",
            x=150,
            y=100,
            vx=60,
            vy=0,
        )
    ]


def create_border_approach():
    """
    Object moves downward toward the border.
    """

    return [
        SimulatedObject(
            track_id=1,
            object_type="person",
            x=480,
            y=80,
            vx=0,
            vy=60,
        )
    ]


def create_restricted_crossing():
    """
    Object deliberately travels from SAFE
    through WARNING into RESTRICTED.
    """

    return [
        SimulatedObject(
            track_id=1,
            object_type="person",
            x=480,
            y=80,
            vx=0,
            vy=70,
        )
    ]


def create_vehicle_approach():
    """
    Simulated vehicle approaches the border.
    """

    return [
        SimulatedObject(
            track_id=2,
            object_type="vehicle",
            x=200,
            y=100,
            vx=0,
            vy=65,
        )
    ]


def create_multiple_objects():
    """
    Multiple simulated objects with different
    trajectories.
    """

    return [
        SimulatedObject(
            track_id=1,
            object_type="person",
            x=200,
            y=80,
            vx=0,
            vy=65,
        ),
        SimulatedObject(
            track_id=2,
            object_type="person",
            x=600,
            y=100,
            vx=0,
            vy=45,
        ),
        SimulatedObject(
            track_id=3,
            object_type="vehicle",
            x=800,
            y=60,
            vx=0,
            vy=80,
        ),
    ]


SCENARIOS = {
    "normal_patrol": create_normal_patrol,
    "border_approach": create_border_approach,
    "restricted_crossing": create_restricted_crossing,
    "vehicle_approach": create_vehicle_approach,
    "multiple_objects": create_multiple_objects,
}
