import sys
from pathlib import Path
import time

import cv2

from ultralytics import YOLO

# Add src subdirectories to sys.path so modules can be imported directly
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(BASE_DIR / "tracking"))
sys.path.append(str(BASE_DIR / "zones"))
sys.path.append(str(BASE_DIR))

try:
    from tracker import ObjectTracker
    from zone_manager import ZoneManager
    from border_config import ZONES
    from zone_state import ZoneStateManager
    from intrusion_engine import IntrusionEngine
except ImportError:
    from src.tracking.tracker import ObjectTracker
    from src.zones.zone_manager import ZoneManager
    from src.zones.border_config import ZONES
    from src.zones.zone_state import ZoneStateManager
    from src.intrusion.intrusion_engine import IntrusionEngine



VIDEO_PATH = "data/simulation/sample.mp4"


def main():

    print("=" * 70)
    print("       BORDERGUARD AI - LIVE INTRUSION PIPELINE")
    print("=" * 70)

    # --------------------------------------------------------
    # Load model.
    # --------------------------------------------------------

    model = YOLO("yolo11n.pt")

    # --------------------------------------------------------
    # Initialize components.
    # --------------------------------------------------------

    tracker = ObjectTracker()

    zone_manager = ZoneManager(ZONES)

    zone_states = ZoneStateManager()

    intrusion_engine = IntrusionEngine(camera_id="CAM-01")

    # --------------------------------------------------------
    # Open video.
    # --------------------------------------------------------

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():

        raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

    frame_count = 0

    previous_positions = {}

    previous_time = time.time()

    # --------------------------------------------------------
    # Main loop.
    # --------------------------------------------------------

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame_count += 1

        current_time = time.time()

        delta_time = current_time - previous_time

        previous_time = current_time

        # ----------------------------------------------------
        # Draw zone map.
        # ----------------------------------------------------

        zone_manager.draw_zones(frame)

        # ----------------------------------------------------
        # Run YOLO + ByteTrack.
        # ----------------------------------------------------

        results = model.track(
            source=frame,
            tracker="bytetrack.yaml",
            conf=0.40,
            persist=True,
            verbose=False,
        )

        if not results:
            continue

        result = results[0]

        tracked_objects = tracker.update(
            result,
            model.names,
        )

        # ----------------------------------------------------
        # Process tracked objects.
        # ----------------------------------------------------

        for tracked_object in tracked_objects:

            track_id = tracked_object["track_id"]

            center = tracked_object["center"]

            class_name = tracked_object["class_name"]

            confidence = tracked_object["confidence"]

            # ----------------------------------------------
            # Determine zone.
            # ----------------------------------------------

            zone = zone_manager.get_zone(center)

            if zone is None:
                current_zone = "NONE"
            else:
                current_zone = zone.name

            # ----------------------------------------------
            # Update zone state.
            # ----------------------------------------------

            state = zone_states.update(
                track_id,
                current_zone,
                current_time,
            )

            previous_zone = state.previous_zone

            dwell_time = zone_states.get_dwell_time(
                track_id,
                current_time,
            )

            # ----------------------------------------------
            # Movement.
            # ----------------------------------------------

            direction = "UNKNOWN"
            speed = 0.0

            if track_id in previous_positions:

                previous = previous_positions[track_id]

                dx = center[0] - previous[0]

                dy = center[1] - previous[1]

                if abs(dx) > abs(dy):

                    direction = "RIGHT" if dx > 0 else "LEFT"

                elif abs(dy) > 3:

                    direction = "DOWN" if dy > 0 else "UP"

                else:

                    direction = "STATIONARY"

                if delta_time > 0:

                    distance = (dx**2 + dy**2) ** 0.5

                    speed = distance / delta_time

            previous_positions[track_id] = center

            # ----------------------------------------------
            # Evaluate intrusion.
            # ----------------------------------------------

            event = intrusion_engine.evaluate(
                track_id=track_id,
                object_type=class_name,
                confidence=confidence,
                previous_zone=previous_zone,
                current_zone=current_zone,
                direction=direction,
                speed=speed,
                dwell_time=dwell_time,
                timestamp=current_time,
            )

            # ----------------------------------------------
            # Draw tracked object.
            # ----------------------------------------------

            x1, y1, x2, y2 = tracked_object["bbox"]

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                (f"{class_name} " f"#{track_id}"),
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

            # ----------------------------------------------
            # Display zone.
            # ----------------------------------------------

            cv2.putText(
                frame,
                f"ZONE: {current_zone}",
                (x1, y2 + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
            )

            # ----------------------------------------------
            # Display intrusion.
            # ----------------------------------------------

            if event:

                print("\n" + "!" * 70)

                print("INTRUSION EVENT DETECTED")

                print(f"Event ID     : " f"{event.event_id}")

                print(f"Track ID     : " f"{event.track_id}")

                print(f"Object       : " f"{event.object_type}")

                print(
                    f"Transition   : "
                    f"{event.previous_zone}"
                    f" -> "
                    f"{event.current_zone}"
                )

                print(f"Event Type   : " f"{event.event_type}")

                print(f"Severity     : " f"{event.severity}")

                print("!" * 70)

            # ----------------------------------------------
            # Draw event state on screen.
            # ----------------------------------------------

            if current_zone == "RESTRICTED":

                cv2.putText(
                    frame,
                    "RESTRICTED AREA",
                    (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (255, 255, 255),
                    2,
                )

        # ----------------------------------------------------
        # Global status.
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "BORDERGUARD AI | INTRUSION ENGINE",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.imshow(
            "BorderGuard AI - Intrusion Monitoring",
            frame,
        )

        # ----------------------------------------------------
        # Q to exit.
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    cap.release()

    cv2.destroyAllWindows()

    print("=" * 70)
    print(f"Frames processed: {frame_count}")

    print(f"Events generated: " f"{len(intrusion_engine.events)}")

    print("Intrusion pipeline completed.")

    print("=" * 70)


if __name__ == "__main__":
    main()
