"""
Predefined software simulation scenarios.
"""

from typing import Callable, Dict, List

from src.simulation.simulated_object import (
    SimulatedObject,
)


def create_normal_patrol() -> List[SimulatedObject]:
    """
    Object moves horizontally inside the safe zone (Y: 100).
    """
    return [
        SimulatedObject(
            track_id=1,
            object_type="person",
            x=100,
            y=100,
            vx=80,
            vy=0,
        )
    ]


def create_border_approach() -> List[SimulatedObject]:
    """
    Object approaches the warning zone but stays near the perimeter.
    """
    return [
        SimulatedObject(
            track_id=1,
            object_type="person",
            x=480,
            y=80,
            vx=0,
            vy=35,
        )
    ]


def create_restricted_crossing() -> List[SimulatedObject]:
    """
    Single intruder moves straight down: SAFE → WARNING → RESTRICTED.
    """
    return [
        SimulatedObject(
            track_id=101,
            object_type="person",
            x=480,
            y=80,
            vx=0,
            vy=75,
        )
    ]


def create_dwell_violation() -> List[SimulatedObject]:
    """
    Target enters the WARNING zone and loiters in place, triggering a DWELL_TIME violation.
    """
    return [
        SimulatedObject(
            track_id=201,
            object_type="person",
            x=480,
            y=220,  # inside WARNING zone (180..350)
            vx=2.0,  # slow wandering / stationary loitering
            vy=1.0,
        )
    ]


def create_multiple_intruders() -> List[SimulatedObject]:
    """
    Multiple simultaneous targets entering from distinct vectors:
    - Track 301: High-speed person on Left flank
    - Track 302: Medium-speed person in Center
    - Track 303: Fast vehicle on Right flank
    """
    return [
        SimulatedObject(
            track_id=301,
            object_type="person",
            x=200,
            y=60,
            vx=15,
            vy=70,
        ),
        SimulatedObject(
            track_id=302,
            object_type="person",
            x=500,
            y=90,
            vx=-10,
            vy=55,
        ),
        SimulatedObject(
            track_id=303,
            object_type="vehicle",
            x=780,
            y=40,
            vx=-25,
            vy=90,
        ),
    ]


def create_direction_violation() -> List[SimulatedObject]:
    """
    Intruder inside RESTRICTED zone moving horizontally / backwards along border wall.
    """
    return [
        SimulatedObject(
            track_id=401,
            object_type="person",
            x=150,
            y=380,  # inside RESTRICTED zone (350..540)
            vx=90,
            vy=-15,  # illegal lateral/upward movement
        )
    ]


def create_vehicle_approach() -> List[SimulatedObject]:
    """
    Rapid vehicle approach towards the restricted sector.
    """
    return [
        SimulatedObject(
            track_id=501,
            object_type="vehicle",
            x=450,
            y=50,
            vx=10,
            vy=110,
        )
    ]


SCENARIOS: Dict[str, Callable[[], List[SimulatedObject]]] = {
    "normal_patrol": create_normal_patrol,
    "border_approach": create_border_approach,
    "restricted_crossing": create_restricted_crossing,
    "dwell_violation": create_dwell_violation,
    "multiple_intruders": create_multiple_intruders,
    "direction_violation": create_direction_violation,
    "vehicle_approach": create_vehicle_approach,
}


def get_scenario(name: str) -> List[SimulatedObject]:
    """
    Returns list of simulated objects for the given scenario name.
    """
    if name in SCENARIOS:
        return SCENARIOS[name]()
    return create_restricted_crossing()


