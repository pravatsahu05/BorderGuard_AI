"""
BorderGuard AI software simulation runner.

Run from project root:

    python -m src.simulation.run_simulation
"""

import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "src"))
sys.path.append(str(BASE_DIR / "data" / "database"))

import cv2

try:
    from src.core.event_orchestrator import EventOrchestrator
    from src.simulation.scenarios import SCENARIOS
    from src.simulation.simulation_config import SIMULATION_CONFIG, SimulationConfig
    from src.simulation.simulation_engine import SimulationEngine
    from src.simulation.simulation_renderer import SimulationRenderer
    from src.zones.zone_manager import ZoneManager
    from src.zones.zone_state import ZoneStateManager
    from src.zones.border_config import ZONES
except ImportError:
    from core.event_orchestrator import EventOrchestrator
    from simulation.scenarios import SCENARIOS
    from simulation.simulation_config import SIMULATION_CONFIG, SimulationConfig
    from simulation.simulation_engine import SimulationEngine
    from simulation.simulation_renderer import SimulationRenderer
    from zones.zone_manager import ZoneManager
    from zones.zone_state import ZoneStateManager
    from zones.border_config import ZONES

try:
    from database_service import DatabaseService
except ImportError:
    from data.database.database_service import DatabaseService


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


def print_security_event(event, risk_result, alert) -> None:
    print()
    print("=" * 70)
    print("[SECURITY EVENT]")
    print("=" * 70)
    print(f"Event ID    : {event.event_id}")
    print(f"Camera      : {event.camera_id}")
    print(f"Track ID    : {event.track_id}")
    print(f"Object      : {event.object_type}")
    print(f"Transition  : {event.previous_zone} -> {event.current_zone}")
    print(f"Direction   : {event.direction}")
    print(f"Speed       : {event.speed:.2f}")
    print(f"Event Type  : {event.event_type}")

    if risk_result is not None:
        print(f"Risk Score  : {risk_result.score:.2f}")
        print(f"Severity    : {risk_result.severity}")

    if alert is not None:
        print(f"Alert ID    : {alert.alert_id}")
        print(f"Alert       : ACTIVE")
        print(f"Message     : {alert.message}")
    else:
        print("Alert       : NOT GENERATED")
    print("=" * 70)


def run_simulation(config=None):
    """
    Programmatically run simulation with a SimulationConfig object or dict.
    Returns (EventSummary, frame_results).
    """
    if config is None:
        config = SimulationConfig()

    if hasattr(config, "scenario_name"):
        scenario_name = config.scenario_name
        time_scale = config.time_scale
        fps = getattr(config, "fps", 30.0)
        camera_id = getattr(config, "camera_id", "SIM-CAM-01")
        db_path = getattr(config, "db_path", "data/database/borderguard.db")
        reset_db = getattr(config, "reset_db", False)
        min_sev = getattr(config, "minimum_alert_severity", "MEDIUM")
        max_frames = getattr(config, "max_frames", 150)
    else:
        scenario_name = config.get("scenario_name", "restricted_crossing")
        time_scale = config.get("time_scale", 1.0)
        fps = config.get("fps", 30.0)
        camera_id = config.get("camera_id", "SIM-CAM-01")
        db_path = config.get("db_path", "data/database/borderguard.db")
        reset_db = config.get("reset_db", False)
        min_sev = config.get("minimum_alert_severity", "MEDIUM")
        max_frames = config.get("max_frames", 150)

    db_service = None
    if db_path:
        full_db_path = BASE_DIR / db_path if not Path(db_path).is_absolute() else Path(db_path)
        db_service = DatabaseService(str(full_db_path))
        if reset_db:
            db_service.reset_database()

    objects = SCENARIOS[scenario_name]()
    simulation = SimulationEngine(objects=objects, time_scale=time_scale)
    zone_manager = ZoneManager(ZONES)
    zone_states = ZoneStateManager()
    orchestrator = EventOrchestrator(camera_id=camera_id, db_service=db_service, minimum_alert_severity=min_sev)

    dt = 1.0 / fps
    results = []

    for _ in range(max_frames):
        simulation.update(dt)
        active_objects = simulation.get_objects()
        if not active_objects:
            break

        for obj in active_objects:
            zone = zone_manager.get_zone(obj.center)
            zone_name = zone.name if zone else "NONE"
            zone_states.update(obj.track_id, zone_name, simulation.simulation_time)
            state = zone_states.get(obj.track_id)
            if state is None:
                continue

            direction = calculate_direction(obj.vx, obj.vy)
            speed = calculate_speed(obj.vx, obj.vy)
            try:
                dwell_time = zone_states.get_dwell_time(obj.track_id, simulation.simulation_time)
            except Exception:
                dwell_time = 0.0

            res = orchestrator.process(
                track_id=obj.track_id,
                object_type=obj.object_type,
                confidence=obj.confidence,
                previous_zone=state.previous_zone,
                current_zone=state.current_zone,
                direction=direction,
                speed=speed,
                dwell_time=dwell_time,
                timestamp=simulation.simulation_time,
            )

            if res.get("event"):
                results.append((res["event"], res["risk"], res["alert"]))

            if obj.x < -50 or obj.x > 1010 or obj.y < -50 or obj.y > 590:
                obj.active = False

    summary = orchestrator.summary
    if db_service:
        db_service.close()

    return summary, results


def run_scenario(scenario_name: str) -> None:
    print()
    print("=" * 70)
    print("       BORDERGUARD AI - SOFTWARE SIMULATION")
    print("=" * 70)
    print(f"Scenario: {scenario_name}")
    print("=" * 70)

    if scenario_name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}")

    config = SIMULATION_CONFIG
    camera_id = config["camera_id"]
    width = config["width"]
    height = config["height"]
    time_scale = config["time_scale"]
    minimum_alert_severity = config["minimum_alert_severity"]

    objects = SCENARIOS[scenario_name]()
    simulation = SimulationEngine(objects=objects, time_scale=time_scale)
    zone_manager = ZoneManager(ZONES)
    zone_states = ZoneStateManager()
    orchestrator = EventOrchestrator(camera_id=camera_id, minimum_alert_severity=minimum_alert_severity)
    renderer = SimulationRenderer(width=width, height=height)

    last_time = time.time()
    try:
        while True:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            delta_time = min(delta_time, 0.1)

            simulation.update(delta_time)
            active_objects = simulation.get_objects()

            for obj in active_objects:
                zone = zone_manager.get_zone(obj.center)
                zone_name = zone.name if zone is not None else "NONE"

                zone_states.update(obj.track_id, zone_name, current_time)
                state = zone_states.get(obj.track_id)
                if state is None:
                    continue

                direction = calculate_direction(obj.vx, obj.vy)
                speed = calculate_speed(obj.vx, obj.vy)
                try:
                    dwell_time = zone_states.get_dwell_time(obj.track_id, current_time)
                except Exception:
                    dwell_time = 0.0

                result = orchestrator.process(
                    track_id=obj.track_id,
                    object_type=obj.object_type,
                    confidence=obj.confidence,
                    previous_zone=state.previous_zone,
                    current_zone=state.current_zone,
                    direction=direction,
                    speed=speed,
                    dwell_time=dwell_time,
                    timestamp=current_time,
                )

                event = result["event"]
                risk_result = result["risk"]
                alert = result["alert"]

                if event is not None:
                    print_security_event(event, risk_result, alert)

                if obj.x < -50 or obj.x > width + 50 or obj.y < -50 or obj.y > height + 50:
                    obj.active = False

            frame = renderer.render(
                objects=simulation.get_objects(),
                zone_states=zone_states,
                scenario_name=scenario_name,
            )

            cv2.imshow("BorderGuard AI - Software Simulation", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                print("\nSimulation stopped by user.")
                break

            if not simulation.get_objects():
                print("\nSimulation completed.")
                break
    finally:
        cv2.destroyAllWindows()
        orchestrator.close()


def main() -> None:
    print()
    print("=" * 70)
    print("       BORDERGUARD AI SIMULATION")
    print("=" * 70)
    print()
    print("Available scenarios:")
    scenario_names = list(SCENARIOS.keys())

    for index, name in enumerate(scenario_names, start=1):
        readable_name = name.replace("_", " ").title()
        print(f"{index}. {readable_name}")

    print()
    print("0. Exit\n")
    choice = input("Select scenario (Enter = default): ").strip()

    if choice == "":
        scenario_name = SIMULATION_CONFIG["default_scenario"]
    elif choice == "0":
        print("Exiting simulation.")
        return
    else:
        try:
            index = int(choice)
            if index < 1 or index > len(scenario_names):
                raise ValueError
            scenario_name = scenario_names[index - 1]
        except ValueError:
            print("Invalid selection.")
            return

    run_scenario(scenario_name)


if __name__ == "__main__":
    main()
