import sys
from pathlib import Path
import time

import cv2
from ultralytics import YOLO

# Add src and module directories to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(BASE_DIR / "tracking"))
sys.path.append(str(BASE_DIR))

try:
    from tracker import ObjectTracker
    from track_history import TrackHistory
    from movement import calculate_direction
    from speed import calculate_pixel_speed
    from zone_manager import ZoneManager
    from border_config import ZONES
    from zone_state import ZoneStateManager
except ImportError:
    from src.tracking.tracker import ObjectTracker
    from src.tracking.track_history import TrackHistory
    from src.tracking.movement import calculate_direction
    from src.tracking.speed import calculate_pixel_speed
    from src.zones.zone_manager import ZoneManager
    from src.zones.border_config import ZONES
    from src.zones.zone_state import ZoneStateManager


VIDEO_PATH = "data/simulation/sample.mp4"


def draw_track(
    frame,
    tracked_object,
    zone_name,
    dwell_time,
    direction,
    speed,
):

    x1, y1, x2, y2 = tracked_object["bbox"]

    track_id = tracked_object["track_id"]

    class_name = tracked_object["class_name"]

    confidence = tracked_object["confidence"]

    # --------------------------------------------------------
    # Bounding box
    # --------------------------------------------------------

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2,
    )

    # --------------------------------------------------------
    # Main label
    # --------------------------------------------------------

    label = f"{class_name} " f"#{track_id} " f"{confidence * 100:.1f}%"

    cv2.putText(
        frame,
        label,
        (x1, max(y1 - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
    )

    # --------------------------------------------------------
    # Zone
    # --------------------------------------------------------

    zone_text = f"Zone: {zone_name}"

    cv2.putText(
        frame,
        zone_text,
        (x1, y2 + 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
    )

    # --------------------------------------------------------
    # Direction
    # --------------------------------------------------------

    direction_text = f"Direction: {direction}"

    cv2.putText(
        frame,
        direction_text,
        (x1, y2 + 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
    )

    # --------------------------------------------------------
    # Speed
    # --------------------------------------------------------

    speed_text = f"Speed: {speed:.1f} px/s"

    cv2.putText(
        frame,
        speed_text,
        (x1, y2 + 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
    )

    # --------------------------------------------------------
    # Dwell time
    # --------------------------------------------------------

    dwell_text = f"Dwell: {dwell_time:.1f}s"

    cv2.putText(
        frame,
        dwell_text,
        (x1, y2 + 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
    )


def main():

    print("=" * 60)
    print("    BORDERGUARD AI - TRACKING + ZONE ENGINE")
    print("=" * 60)

    # --------------------------------------------------------
    # Load YOLO.
    # --------------------------------------------------------

    model = YOLO("yolo11n.pt")

    # --------------------------------------------------------
    # Initialize tracker.
    # --------------------------------------------------------

    tracker = ObjectTracker()

    history = TrackHistory(max_history=30)

    # --------------------------------------------------------
    # Initialize zones.
    # --------------------------------------------------------

    zone_manager = ZoneManager(ZONES)

    zone_states = ZoneStateManager()

    # --------------------------------------------------------
    # Open video.
    # --------------------------------------------------------

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():

        raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

    previous_positions = {}
    previous_time = time.time()

    frame_count = 0

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
        # YOLO + ByteTrack.
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
        # Process objects.
        # ----------------------------------------------------

        for tracked_object in tracked_objects:

            track_id = tracked_object["track_id"]

            center = tracked_object["center"]

            # ----------------------------------------------
            # Track history.
            # ----------------------------------------------

            history.update(
                track_id,
                center,
            )

            # ----------------------------------------------
            # Current zone.
            # ----------------------------------------------

            zone = zone_manager.get_zone(center)

            if zone is None:
                zone_name = "NONE"
            else:
                zone_name = zone.name

            # ----------------------------------------------
            # Zone state.
            # ----------------------------------------------

            state = zone_states.update(
                track_id,
                zone_name,
                current_time,
            )

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

                direction = calculate_direction(
                    previous,
                    center,
                )

                speed = calculate_pixel_speed(
                    previous,
                    center,
                    delta_time,
                )

            previous_positions[track_id] = center

            # ----------------------------------------------
            # Draw.
            # ----------------------------------------------

            draw_track(
                frame,
                tracked_object,
                zone_name,
                dwell_time,
                direction,
                speed,
            )

        # ----------------------------------------------------
        # System label.
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "BORDERGUARD AI | ZONE ENGINE ACTIVE",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.imshow(
            "BorderGuard AI - Zone Monitoring",
            frame,
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    cap.release()

    cv2.destroyAllWindows()

    print("=" * 60)
    print(f"Frames processed: {frame_count}")
    print("Zone monitoring completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
