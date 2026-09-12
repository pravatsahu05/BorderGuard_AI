"""
Simulation module for BorderGuard AI.
"""
from src.simulation.simulation_config import SimulationConfig, SIMULATION_CONFIG
from src.simulation.simulated_object import SimulatedObject
from src.simulation.scenarios import SCENARIOS
from src.simulation.simulation_engine import SimulationEngine

try:
    from src.simulation.simulation_renderer import SimulationRenderer
    from src.simulation.run_simulation import run_simulation
except ImportError:
    SimulationRenderer = None
    run_simulation = None

__all__ = [
    "SimulationConfig",
    "SIMULATION_CONFIG",
    "SimulatedObject",
    "SCENARIOS",
    "SimulationEngine",
    "SimulationRenderer",
    "run_simulation",
]

