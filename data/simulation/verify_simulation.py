import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(BASE_DIR / "src"))
sys.path.append(str(BASE_DIR / "data" / "database"))
sys.path.append(str(BASE_DIR / "data" / "simulation"))
sys.path.append(str(BASE_DIR))

from simulated_object import SimulatedObject
from scenarios import SCENARIOS
from simulation_engine import SimulationEngine
from simulation_renderer import SimulationRenderer
from zones.zone_manager import ZoneManager
from zones.zone_state import ZoneStateManager
from zones.border_config import ZONES
from intrusion.intrusion_engine import IntrusionEngine
from risk.risk_engine import RiskEngine
from alerts.alert_engine import AlertEngine
try:
    from database_service import DatabaseService
except ImportError:
    from data.database.database_service import DatabaseService

try:
    from schema import SCHEMA
except ImportError:
    from data.database.schema import SCHEMA



def run_checks():
    results = {}

    # 1. Directory & __init__.py
    sim_dir = BASE_DIR / "data" / "simulation"
    results["simulation_dir_exists"] = sim_dir.exists() and sim_dir.is_dir()
    results["init_py_exists"] = (sim_dir / "__init__.py").exists()

    # 2. SimulatedObject & movement
    obj = SimulatedObject(track_id=99, object_type="person", x=100, y=100, vx=10, vy=20)
    obj.update(1.0)
    results["simulated_object_movement"] = (obj.x == 110 and obj.y == 120 and obj.center == (110, 120))

    # 3. Scenarios
    expected_scenarios = {"normal_patrol", "border_approach", "restricted_crossing", "vehicle_approach", "multiple_objects"}
    results["scenarios_created"] = expected_scenarios.issubset(set(SCENARIOS.keys()))

    # 4. SimulationEngine
    scen_objs = SCENARIOS["restricted_crossing"]()
    engine = SimulationEngine(scen_objs)
    engine.update(0.1)
    results["simulation_engine_working"] = len(engine.get_objects()) > 0

    # 5. SimulationRenderer
    renderer = SimulationRenderer()
    zone_states = ZoneStateManager()
    frame = renderer.render(engine.get_objects(), zone_states, "restricted_crossing")
    results["simulation_renderer_working"] = frame is not None and frame.shape == (540, 960, 3)

    # 6. Zones evaluation
    zm = ZoneManager(ZONES)
    safe_zone = zm.get_zone((500, 100))
    warn_zone = zm.get_zone((500, 250))
    rest_zone = zm.get_zone((500, 400))
    results["safe_zone_works"] = (safe_zone is not None and safe_zone.name == "SAFE")
    results["warning_zone_works"] = (warn_zone is not None and warn_zone.name == "WARNING")
    results["restricted_zone_works"] = (rest_zone is not None and rest_zone.name == "RESTRICTED")

    # 7. Pipeline: Restricted crossing, risk, alert, SQLite saving
    db_path = BASE_DIR / "data" / "database" / "test_verify.db"
    if db_path.exists():
        db_path.unlink()

    db_service = DatabaseService(str(db_path))
    db_service.database.connect().executescript(SCHEMA)
    db_service.cameras.add_camera("TEST-CAM", "Test Camera")


    intrusion_engine = IntrusionEngine(camera_id="TEST-CAM")
    risk_engine = RiskEngine()
    alert_engine = AlertEngine(minimum_severity="MEDIUM")

    # Simulate transition from WARNING to RESTRICTED
    event = intrusion_engine.evaluate(
        track_id=1,
        object_type="person",
        confidence=0.95,
        previous_zone="WARNING",
        current_zone="RESTRICTED",
        direction="DOWN",
        speed=70.0,
        dwell_time=2.0,
    )
    results["restricted_crossing_event"] = (event is not None and event.event_type == "RESTRICTED_ZONE_ENTRY")

    if event:
        risk_res = risk_engine.evaluate(event)
        results["risk_score_generated"] = (risk_res.score > 0 and risk_res.severity in ("MEDIUM", "HIGH", "CRITICAL"))

        alert = alert_engine.create_alert(event, risk_res)
        results["alert_generated"] = (alert is not None and alert.severity == risk_res.severity)

        db_service.events.save_event(event)
        db_service.risks.save_risk(event, risk_res)
        if alert:
            db_service.alerts.save_alert(alert)

        saved = db_service.events.get_event(event.event_id)
        results["event_saved_sqlite"] = (saved is not None and saved["event_id"] == event.event_id)

    db_service.close()
    if db_path.exists():
        db_path.unlink()

    # 8. Vehicle approach scenario
    veh_objs = SCENARIOS["vehicle_approach"]()
    results["vehicle_scenario_works"] = (len(veh_objs) > 0 and veh_objs[0].object_type == "vehicle")

    # 9. Multiple objects scenario
    multi_objs = SCENARIOS["multiple_objects"]()
    results["multiple_objects_works"] = (len(multi_objs) >= 3)

    return results


if __name__ == "__main__":
    res = run_checks()
    print("=" * 60)
    print("BORDERGUARD AI - SIMULATION VERIFICATION")
    print("=" * 60)
    all_passed = True
    for key, val in res.items():
        status = "PASSED" if val else "FAILED"
        if not val:
            all_passed = False
        print(f"{key:32s} : {status}")
    print("=" * 60)
    print("OVERALL RESULT:", "ALL PASSED" if all_passed else "SOME FAILED")
    sys.exit(0 if all_passed else 1)

