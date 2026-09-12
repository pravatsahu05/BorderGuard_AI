import time
from typing import List, Optional, Any

try:
    from src.simulation.simulation_engine import SimulationEngine
    from src.simulation.scenarios import get_scenario
    from src.core.event_orchestrator import EventOrchestrator
    from src.zones.zone_manager import ZoneManager
    from src.zones.zone_state import ZoneStateManager
    from src.zones.border_config import ZONES
except ImportError:
    from simulation.simulation_engine import SimulationEngine
    from simulation.scenarios import get_scenario
    from core.event_orchestrator import EventOrchestrator
    from zones.zone_manager import ZoneManager
    from zones.zone_state import ZoneStateManager
    from zones.border_config import ZONES


def calculate_direction(vx: float, vy: float) -> str:
    threshold = 3.0
    if vy > threshold:
        return "DOWN"
    if vy < -threshold:
        return "UP"
    if vx > threshold:
        return "RIGHT"
    if vx < -threshold:
        return "LEFT"
    return "STATIONARY"


def calculate_speed(vx: float, vy: float) -> float:
    return (vx**2 + vy**2) ** 0.5


class SimulationController:
    """
    Controls the BorderGuard software simulation
    from the Streamlit dashboard.
    """

    def __init__(
        self,
        camera_id="SIM-CAM-01",
    ):
        self.camera_id = camera_id
        self.engine: Optional[SimulationEngine] = None
        self.orchestrator: Optional[EventOrchestrator] = None
        self.zone_manager: Optional[ZoneManager] = None
        self.zone_states: Optional[ZoneStateManager] = None
        self.running = False
        self.last_update = time.time()

    # ========================================================
    # START
    # ========================================================

    def start(
        self,
        scenario_name,
    ):
        objects = get_scenario(scenario_name)
        self.engine = SimulationEngine(
            objects=objects,
            time_scale=1.0,
        )
        self.zone_manager = ZoneManager(ZONES)
        self.zone_states = ZoneStateManager()
        self.orchestrator = EventOrchestrator(
            camera_id=self.camera_id
        )
        self.running = True
        self.last_update = time.time()

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):
        self.running = False
        if self.orchestrator:
            self.orchestrator.close()
            self.orchestrator = None

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
        scenario_name,
    ):
        self.stop()
        self.start(scenario_name)

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt: Optional[float] = None) -> List[Any]:
        if not self.running:
            return []

        if self.engine is None or self.orchestrator is None:
            return []

        current_time = time.time()
        if dt is not None and dt > 0:
            delta_time = float(dt)
        else:
            delta_time = current_time - self.last_update

        self.last_update = current_time

        self.engine.update(delta_time)
        active_objects = self.engine.get_objects()

        results = []

        for obj in active_objects:
            if not getattr(obj, "active", True):
                continue

            if self.zone_manager and self.zone_states:
                zone = self.zone_manager.get_zone(obj.center)
                zone_name = zone.name if zone is not None else "NONE"
                self.zone_states.update(obj.track_id, zone_name, self.engine.simulation_time)
                state = self.zone_states.get(obj.track_id)

                direction = calculate_direction(obj.vx, obj.vy)
                speed = calculate_speed(obj.vx, obj.vy)
                try:
                    dwell_time = self.zone_states.get_dwell_time(obj.track_id, self.engine.simulation_time)
                except Exception:
                    dwell_time = 0.0

                prev_zone = state.previous_zone if state else "SAFE"
                curr_zone = state.current_zone if state else zone_name
            else:
                prev_zone = getattr(obj, "previous_zone", "SAFE")
                curr_zone = getattr(obj, "current_zone", "SAFE")
                direction = getattr(obj, "direction", "STATIONARY")
                speed = getattr(obj, "speed", 0.0)
                dwell_time = getattr(obj, "dwell_time", 0.0)

            # Assign computed zone and movement dynamics to object
            obj.previous_zone = prev_zone
            obj.current_zone = curr_zone
            obj.direction = direction
            obj.speed = speed
            obj.dwell_time = dwell_time

            result = self.orchestrator.process(
                track_id=obj.track_id,
                object_type=obj.object_type,
                confidence=obj.confidence,
                previous_zone=prev_zone,
                current_zone=curr_zone,
                direction=direction,
                speed=speed,
                dwell_time=dwell_time,
                timestamp=self.engine.simulation_time,
            )

            # Deactivate out-of-bounds simulation targets
            if obj.x < -50 or obj.x > 1010 or obj.y < -50 or obj.y > 590:
                obj.active = False

            if result:
                results.append(result)

        return results

    # ========================================================
    # GET OBJECTS
    # ========================================================

    def get_objects(self) -> List[Any]:
        """
        Return currently active simulation objects.
        """
        if self.engine is None:
            return []
        return self.engine.get_objects()

    # ========================================================
    # GET SIMULATION TIME
    # ========================================================

    def get_simulation_time(self) -> float:
        """
        Return total accumulated simulation time in seconds.
        """
        if self.engine is None:
            return 0.0
        return self.engine.simulation_time