import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

try:
    from src.simulation.simulation_engine import SimulationEngine
    from src.simulation.scenarios import get_scenario
    from src.core.event_orchestrator import EventOrchestrator
    from src.zones.zone_manager import ZoneManager
    from src.zones.zone_state import ZoneStateManager
    from src.zones.border_config import ZONES
    from src.database.database_service import DatabaseService
    from src.dashboard.dashboard_config import DATABASE_PATH
except ImportError:
    from simulation.simulation_engine import SimulationEngine
    from simulation.scenarios import get_scenario
    from core.event_orchestrator import EventOrchestrator
    from zones.zone_manager import ZoneManager
    from zones.zone_state import ZoneStateManager
    from zones.border_config import ZONES
    from database.database_service import DatabaseService
    from dashboard.dashboard_config import DATABASE_PATH


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
    Controls a BorderGuard software simulation from the dashboard.
    """

    def __init__(self, camera_id="SIM-CAM-01"):
        self.camera_id = camera_id
        self.engine = None
        self.orchestrator = None
        self.zone_manager = ZoneManager(ZONES)
        self.zone_states = ZoneStateManager()
        self.running = False
        self.last_update = time.time()
        self.scenario_name = "restricted_crossing"

    def start(self, scenario_name: str = "restricted_crossing"):
        self.scenario_name = scenario_name
        objects = get_scenario(scenario_name)
        self.engine = SimulationEngine(objects=objects, time_scale=1.0)
        self.zone_states = ZoneStateManager()
        db_service = DatabaseService(database_path=DATABASE_PATH)
        self.orchestrator = EventOrchestrator(
            camera_id=self.camera_id,
            db_service=db_service,
            minimum_alert_severity="MEDIUM",
        )
        self.running = True
        self.last_update = time.time()

    def stop(self):
        self.running = False
        if self.orchestrator:
            try:
                self.orchestrator.close()
            except Exception:
                pass
            self.orchestrator = None

    def reset(self, scenario_name: str = "restricted_crossing"):
        self.stop()
        self.start(scenario_name)
        self.running = False

    def update(self, dt: float = 0.1):
        if not self.running or self.engine is None or self.orchestrator is None:
            return []

        self.engine.update(dt)
        active_objects = self.engine.get_objects()

        if not active_objects:
            self.running = False
            return []

        results = []
        for obj in active_objects:
            zone = self.zone_manager.get_zone(obj.center)
            zone_name = zone.name if zone else "NONE"
            self.zone_states.update(obj.track_id, zone_name, self.engine.simulation_time)
            state = self.zone_states.get(obj.track_id)
            if state is None:
                continue

            direction = calculate_direction(obj.vx, obj.vy)
            speed = calculate_speed(obj.vx, obj.vy)
            try:
                dwell_time = self.zone_states.get_dwell_time(obj.track_id, self.engine.simulation_time)
            except Exception:
                dwell_time = 0.0

            setattr(obj, "current_zone", state.current_zone)
            setattr(obj, "previous_zone", state.previous_zone)
            setattr(obj, "direction", direction)
            setattr(obj, "speed", speed)
            setattr(obj, "dwell_time", dwell_time)

            result = self.orchestrator.process(
                track_id=obj.track_id,
                object_type=obj.object_type,
                confidence=obj.confidence,
                previous_zone=state.previous_zone,
                current_zone=state.current_zone,
                direction=direction,
                speed=speed,
                dwell_time=dwell_time,
                timestamp=self.engine.simulation_time,
            )
            if result and result.get("event"):
                results.append(result)

            if obj.x < -50 or obj.x > 1010 or obj.y < -50 or obj.y > 590:
                obj.active = False

        return results

    def get_objects(self):
        if self.engine:
            return self.engine.get_objects()
        return []

    def get_simulation_time(self) -> float:
        if self.engine:
            return self.engine.simulation_time
        return 0.0
