"""
BorderGuard AI
Software Border Simulation Runner

Phase 11

Pipeline:

    Simulated Objects
            ↓
    Simulation Engine
            ↓
       Zone Engine
            ↓
     Zone State Manager
            ↓
     Intrusion Engine
            ↓
        Risk Engine
            ↓
       Alert Engine
            ↓
       SQLite Database

This module provides a completely software-based
demonstration environment for BorderGuard AI.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(BASE_DIR / "src"))
sys.path.append(str(BASE_DIR / "data" / "database"))
sys.path.append(str(BASE_DIR / "data" / "simulation"))
sys.path.append(str(BASE_DIR))

import time

import cv2

try:
    from scenarios import SCENARIOS
    from simulation_engine import SimulationEngine
    from simulation_renderer import SimulationRenderer
except ImportError:
    from data.simulation.scenarios import SCENARIOS
    from data.simulation.simulation_engine import SimulationEngine
    from data.simulation.simulation_renderer import SimulationRenderer

try:
    from zones.border_config import ZONES
    from zones.zone_manager import ZoneManager
    from zones.zone_state import ZoneStateManager
except ImportError:
    from border_config import ZONES
    from zone_manager import ZoneManager
    from zone_state import ZoneStateManager

try:
    from intrusion.intrusion_engine import IntrusionEngine
except ImportError:
    from intrusion_engine import IntrusionEngine

try:
    from risk.risk_engine import RiskEngine
except ImportError:
    from risk_engine import RiskEngine

try:
    from alerts.alert_engine import AlertEngine
except ImportError:
    from alert_engine import AlertEngine

try:
    from database.database_service import DatabaseService
except ImportError:
    try:
        from database_service import DatabaseService
    except ImportError:
        from data.database.database_service import DatabaseService


# ============================================================
# CONFIGURATION
# ============================================================

CAMERA_ID = "SIM-CAM-01"

CAMERA_NAME = "Software Border Simulator"

CAMERA_LOCATION = "Virtual Sector A"

MINIMUM_ALERT_SEVERITY = "MEDIUM"

DEFAULT_SCENARIO = "restricted_crossing"

WINDOW_NAME = "BorderGuard AI - Software Simulation"


# ============================================================
# UTILITY FUNCTIONS
# ============================================================


def calculate_direction(
    vx: float,
    vy: float,
) -> str:
    """
    Determine object movement direction
    from its velocity.

    OpenCV coordinate system:

        +X → right
        -X → left
        +Y → down
        -Y → up
    """

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


def calculate_speed(
    vx: float,
    vy: float,
) -> float:
    """
    Calculate movement speed using
    Euclidean velocity magnitude.
    """

    return (vx**2 + vy**2) ** 0.5


def print_event(
    event,
    risk_result,
    alert,
):
    """
    Print a complete event report
    to the terminal.
    """

    print()
    print("!" * 75)
    print("                 INTRUSION DETECTED")
    print("!" * 75)

    print(f"Event ID     : {event.event_id}")

    print(f"Camera       : {event.camera_id}")

    print(f"Track ID     : {event.track_id}")

    print(f"Object       : {event.object_type}")

    print(f"Confidence   : {event.confidence:.2f}")

    print(f"Transition   : " f"{event.previous_zone}" f" -> " f"{event.current_zone}")

    print(f"Direction    : {event.direction}")

    print(f"Speed        : {event.speed:.2f} px/s")

    print(f"Dwell Time   : {event.dwell_time:.2f} s")

    print(f"Event Type   : {event.event_type}")

    print(f"Severity     : {risk_result.severity}")

    print(f"Risk Score   : {risk_result.score:.2f}")

    if alert:

        print()
        print("                 ALERT GENERATED")

        print(f"Alert ID     : {alert.alert_id}")

        print(f"Alert Level  : {alert.severity}")

        print(f"Message      : {alert.message}")

    print("!" * 75)
    print()


def print_risk_breakdown(
    risk_result,
):
    """
    Display the contribution of every
    risk factor.
    """

    print("Risk Factor Breakdown:")

    print("-" * 55)

    for factor, data in risk_result.breakdown.items():

        print(
            f"{factor:18s}"
            f" raw={data['raw_score']:7.2f}"
            f" weight={data['weight']:.2f}"
            f" contribution="
            f"{data['contribution']:7.2f}"
        )

    print("-" * 55)

    print(f"{'TOTAL':18s}" f" {risk_result.score:7.2f}")


def print_startup_information(
    scenario_name,
):
    """
    Display simulator configuration.
    """

    print()
    print("=" * 75)
    print("             BORDERGUARD AI")
    print("          SOFTWARE BORDER SIMULATION")
    print("=" * 75)

    print(f"Camera ID       : {CAMERA_ID}")

    print(f"Camera Name     : {CAMERA_NAME}")

    print(f"Location        : {CAMERA_LOCATION}")

    print(f"Scenario        : {scenario_name}")

    print(f"Alert Threshold : {MINIMUM_ALERT_SEVERITY}")

    print()
    print("Controls:")

    print("  Q / ESC  -> Exit simulation")

    print()
    print("=" * 75)
    print()


# ============================================================
# MAIN SCENARIO RUNNER
# ============================================================


def run_scenario(
    scenario_name: str,
):
    """
    Run one software border simulation scenario.

    The scenario generates virtual objects.
    Their positions are processed by the same
    downstream security architecture used by
    the real detection pipeline.
    """

    # ========================================================
    # Validate scenario
    # ========================================================

    if scenario_name not in SCENARIOS:

        raise ValueError(
            f"Unknown scenario: "
            f"{scenario_name}\n"
            f"Available scenarios: "
            f"{list(SCENARIOS.keys())}"
        )

    print_startup_information(scenario_name)

    # ========================================================
    # Create simulated objects
    # ========================================================

    objects = SCENARIOS[scenario_name]()

    # ========================================================
    # Create simulation engine
    # ========================================================

    simulation = SimulationEngine(objects)

    # ========================================================
    # Zone manager
    # ========================================================

    zone_manager = ZoneManager(ZONES)

    # ========================================================
    # Zone state manager
    # ========================================================

    zone_states = ZoneStateManager()

    # ========================================================
    # Intrusion engine
    # ========================================================

    intrusion_engine = IntrusionEngine(camera_id=CAMERA_ID)

    # ========================================================
    # Risk engine
    # ========================================================

    risk_engine = RiskEngine()

    # ========================================================
    # Alert engine
    # ========================================================

    alert_engine = AlertEngine(minimum_severity=(MINIMUM_ALERT_SEVERITY))

    # ========================================================
    # Database service
    # ========================================================

    database = DatabaseService()

    # ========================================================
    # Make sure database schema exists
    # ========================================================

    try:
        from database.schema import SCHEMA
    except ImportError:
        from schema import SCHEMA

    connection = database.database.connect()

    connection.executescript(SCHEMA)

    connection.commit()

    # ========================================================
    # Register simulation camera
    # ========================================================

    database.cameras.add_camera(
        camera_id=CAMERA_ID,
        camera_name=CAMERA_NAME,
        location=CAMERA_LOCATION,
        status="ACTIVE",
    )

    database.logger.log(
        level="INFO",
        component="SIMULATION",
        message=(f"Started scenario: " f"{scenario_name}"),
    )

    # ========================================================
    # Renderer
    # ========================================================

    renderer = SimulationRenderer()

    # ========================================================
    # Timing
    # ========================================================

    last_time = time.time()

    # ========================================================
    # Event tracking
    # ========================================================

    processed_event_ids = set()

    # ========================================================
    # Main simulation loop
    # ========================================================

    try:

        while True:

            # ------------------------------------------------
            # Calculate elapsed time
            # ------------------------------------------------

            current_time = time.time()

            delta_time = current_time - last_time

            last_time = current_time

            # Prevent very large time jumps.
            delta_time = min(
                delta_time,
                0.1,
            )

            # ------------------------------------------------
            # Advance simulation
            # ------------------------------------------------

            simulation.update(delta_time)

            # ------------------------------------------------
            # Process active objects
            # ------------------------------------------------

            active_objects = simulation.get_objects()

            for obj in active_objects:

                # ============================================
                # Determine current zone
                # ============================================

                zone = zone_manager.get_zone(obj.center)

                if zone:

                    zone_name = zone.name

                else:

                    zone_name = "NONE"

                # ============================================
                # Update zone state
                # ============================================

                zone_states.update(
                    obj.track_id,
                    zone_name,
                    current_time,
                )

                # ============================================
                # Retrieve current state
                # ============================================

                state = zone_states.get(obj.track_id)

                if state is None:

                    continue

                # ============================================
                # Calculate dwell time
                # ============================================

                dwell_time = zone_states.get_dwell_time(
                    obj.track_id,
                    current_time,
                )

                # ============================================
                # Calculate direction
                # ============================================

                direction = calculate_direction(
                    obj.vx,
                    obj.vy,
                )

                # ============================================
                # Calculate speed
                # ============================================

                speed = calculate_speed(
                    obj.vx,
                    obj.vy,
                )

                # ============================================
                # Intrusion detection
                # ============================================

                event = intrusion_engine.evaluate(
                    track_id=obj.track_id,
                    object_type=(obj.object_type),
                    confidence=(obj.confidence),
                    previous_zone=(state.previous_zone),
                    current_zone=(state.current_zone),
                    direction=direction,
                    speed=speed,
                    dwell_time=dwell_time,
                    timestamp=current_time,
                )

                # ============================================
                # No intrusion
                # ============================================

                if event is None:

                    continue

                # ============================================
                # Avoid duplicate processing
                # ============================================

                if event.event_id in processed_event_ids:

                    continue

                processed_event_ids.add(event.event_id)

                # ============================================
                # Risk evaluation
                # ============================================

                risk_result = risk_engine.evaluate(event)

                # ============================================
                # Alert generation
                # ============================================

                alert = alert_engine.create_alert(
                    event,
                    risk_result,
                )

                # ============================================
                # Persist intrusion event
                # ============================================

                database.events.save_event(event)

                # ============================================
                # Persist risk assessment
                # ============================================

                database.risks.save_risk(
                    event,
                    risk_result,
                )

                # ============================================
                # Persist alert
                # ============================================

                if alert:

                    database.alerts.save_alert(alert)

                # ============================================
                # Log event
                # ============================================

                database.logger.log(
                    level=risk_result.severity,
                    component="INTRUSION",
                    message=(
                        f"Event "
                        f"{event.event_id}: "
                        f"{event.event_type}, "
                        f"risk="
                        f"{risk_result.score:.2f}"
                    ),
                )

                # ============================================
                # Display event
                # ============================================

                print_event(
                    event,
                    risk_result,
                    alert,
                )

                print_risk_breakdown(risk_result)

            # ------------------------------------------------
            # Render frame
            # ------------------------------------------------

            frame = renderer.render(
                active_objects,
                zone_states,
                scenario_name,
            )

            # ------------------------------------------------
            # Display frame
            # ------------------------------------------------

            cv2.imshow(
                WINDOW_NAME,
                frame,
            )

            # ------------------------------------------------
            # Keyboard input
            # ------------------------------------------------

            key = cv2.waitKey(1) & 0xFF

            # Q or ESC
            if key == ord("q") or key == 27:

                print("\nSimulation stopped by user.")

                break

            # ------------------------------------------------
            # Automatically stop when objects
            # leave the simulation environment.
            # ------------------------------------------------

            for obj in active_objects:

                if obj.y > renderer.height + 50:

                    obj.active = False

                if obj.x < -50 or obj.x > renderer.width + 50:

                    obj.active = False

            # ------------------------------------------------
            # Check if simulation completed
            # ------------------------------------------------

            if not simulation.get_objects():

                print("\nSimulation completed.")

                break

    except KeyboardInterrupt:

        print("\nSimulation interrupted.")

    finally:

        # ====================================================
        # Mark camera inactive
        # ====================================================

        try:

            database.cameras.add_camera(
                camera_id=CAMERA_ID,
                camera_name=CAMERA_NAME,
                location=CAMERA_LOCATION,
                status="INACTIVE",
            )

            database.logger.log(
                level="INFO",
                component="SIMULATION",
                message=(f"Stopped scenario: " f"{scenario_name}"),
            )

        except Exception as error:

            print(f"Database shutdown warning: " f"{error}")

        # ====================================================
        # Close OpenCV
        # ====================================================

        cv2.destroyAllWindows()

        # ====================================================
        # Close database
        # ====================================================

        database.close()

        print()
        print("=" * 75)
        print("          SIMULATION SESSION ENDED")
        print("=" * 75)

        print(f"Scenario: {scenario_name}")

        print(f"Events processed: " f"{len(processed_event_ids)}")

        print("Data persisted to:")

        print("data/database/borderguard.db")

        print("=" * 75)
        print()


# ============================================================
# SCENARIO MENU
# ============================================================


def show_scenario_menu():
    """
    Display available scenarios and allow
    the user to choose one.
    """

    print()
    print("=" * 65)
    print("             BORDERGUARD AI")
    print("          SOFTWARE SIMULATION")
    print("=" * 65)

    scenario_names = list(SCENARIOS.keys())

    for index, name in enumerate(
        scenario_names,
        start=1,
    ):

        readable_name = name.replace(
            "_",
            " ",
        ).title()

        print(f"{index}. " f"{readable_name}")

    print()
    print("0. Exit")

    print("=" * 65)

    while True:

        try:

            choice = input("\nSelect scenario: ").strip()

            if choice == "0":

                return None

            index = int(choice)

            if 1 <= index <= len(scenario_names):

                return scenario_names[index - 1]

            print("Invalid selection. " "Please choose a valid number.")

        except ValueError:

            print("Please enter a number.")


# ============================================================
# MAIN
# ============================================================


def main():
    """
    Application entry point.
    """

    # --------------------------------------------------------
    # Display menu
    # --------------------------------------------------------

    scenario_name = show_scenario_menu()

    # --------------------------------------------------------
    # Exit
    # --------------------------------------------------------

    if scenario_name is None:

        print("\nExiting BorderGuard AI.")

        return

    # --------------------------------------------------------
    # Run selected scenario
    # --------------------------------------------------------

    run_scenario(scenario_name)


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
