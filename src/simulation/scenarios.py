"""
Predefined software simulation scenarios.
"""

from typing import Callable, Dict, List

from src.simulation.simulated_object import (
    SimulatedObject,
)


def create_normal_patrol() -> List[SimulatedObject]:
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


def create_border_approach() -> List[SimulatedObject]:
    """
    Object approaches the warning zone but does not
    intentionally cross into the restricted zone.
    """

    return [
        SimulatedObject(
            track_id=1,
            object_type="person",
            x=480,
            y=80,
            vx=0,
            vy=40,
        )
    ]


def create_restricted_crossing() -> List[SimulatedObject]:
    """
    Person moves downward through SAFE → WARNING
    → RESTRICTED.
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


def create_vehicle_approach() -> List[SimulatedObject]:
    """
    Simulated vehicle approaches the border.
    """

    return [
        SimulatedObject(
            track_id=2,
            object_type="vehicle",
            x=200,
            y=80,
            vx=0,
            vy=65,
        )
    ]


def create_multiple_objects() -> List[SimulatedObject]:
    """
    Multiple simulated objects moving independently.
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


SCENARIOS: Dict[str, Callable[[], List[SimulatedObject]]] = {
    "normal_patrol": create_normal_patrol,
    "border_approach": create_border_approach,
    "restricted_crossing": create_restricted_crossing,
    "vehicle_approach": create_vehicle_approach,
    "multiple_objects": create_multiple_objects,
}


def get_scenario(name: str) -> List[SimulatedObject]:
    """
    Returns list of simulated objects for the given scenario name.
    """
    if name in SCENARIOS:
        return SCENARIOS[name]()
    return create_restricted_crossing()

