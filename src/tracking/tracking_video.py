import sys
from pathlib import Path

import cv2
import time

from ultralytics import YOLO

# Ensure src/tracking is in sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from tracker import ObjectTracker
    from track_history import TrackHistory
    from movement import calculate_direction
    from speed import calculate_pixel_speed
except ImportError:
    from src.tracking.tracker import ObjectTracker
    from src.tracking.track_history import TrackHistory
    from src.tracking.movement import calculate_direction
    from src.tracking.speed import calculate_pixel_speed



VIDEO_PATH = "data/simulation/sample.mp4"


def draw_track(
    frame,
    tracked_object,
    trajectory,
    direction,
    speed,
):
    """
    Draw tracking information.
    """

    x1, y1, x2, y2 = tracked_object["bbox"]

    track_id = tracked_object["track_id"]

    class_name = tracked_object["class_name"]

    confidence = tracked_object["confidence"]

    # --------------------------------------------------------
    # Draw bounding box.
    # --------------------------------------------------------

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2,
    )

    # --------------------------------------------------------
    # Draw object label.
    # --------------------------------------------------------

    label_title = f"{class_name.capitalize()} #{track_id}"
    label_conf = f"{confidence * 100:.1f}%"

    cv2.putText(
        frame,
        label_title,
        (x1, max(y1 - 25, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
    )

    cv2.putText(
        frame,
        label_conf,
        (x1, max(y1 - 8, 38)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        2,
    )

    # --------------------------------------------------------
    # Draw trajectory.
    # --------------------------------------------------------

    for index in range(
        1,
        len(trajectory),
    ):

        previous = trajectory[index - 1]

        current = trajectory[index]

        cv2.line(
            frame,
            (
                int(previous[0]),
                int(previous[1]),
            ),
            (
                int(current[0]),
                int(current[1]),
            ),
            (255, 255, 0),
            2,
        )

    # --------------------------------------------------------
    # Draw direction.
    # --------------------------------------------------------

    info = f"Direction: {direction}"

    cv2.putText(
        frame,
        info,
        (x1, y2 + 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
    )

    # --------------------------------------------------------
    # Draw speed.
    # --------------------------------------------------------

    speed_info = f"Speed: {speed:.1f} px/s"

    cv2.putText(
        frame,
        speed_info,
        (x1, y2 + 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
    )


def main():

    print("=" * 60)
    print("       BORDERGUARD AI - OBJECT TRACKING")
    print("=" * 60)

    # --------------------------------------------------------
    # Load YOLO.
    # --------------------------------------------------------

    model = YOLO("yolo11n.pt")

    # --------------------------------------------------------
    # Initialize tracking components.
    # --------------------------------------------------------

    tracker = ObjectTracker()

    history = TrackHistory(max_history=30)

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
        # Run YOLO + ByteTrack.
        # ----------------------------------------------------

        results = model.track(
            source=frame,
            tracker="bytetrack.yaml",
            conf=0.25,
            persist=True,
            verbose=False,
        )

        if not results:
            continue

        result = results[0]

        # ----------------------------------------------------
        # Convert YOLO results into our format.
        # ----------------------------------------------------

        tracked_objects = tracker.update(
            result,
            model.names,
        )

        # ----------------------------------------------------
        # Process each tracked object.
        # ----------------------------------------------------

        for tracked_object in tracked_objects:

            track_id = tracked_object["track_id"]

            center = tracked_object["center"]

            # Update history.
            history.update(
                track_id,
                center,
            )

            trajectory = history.get(track_id)

            # Default values.
            direction = "UNKNOWN"
            speed = 0.0

            # ------------------------------------------------
            # Calculate movement.
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Draw tracking information.
            # ------------------------------------------------

            draw_track(
                frame,
                tracked_object,
                trajectory,
                direction,
                speed,
            )

        # ----------------------------------------------------
        # Display information.
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"Tracked Objects: " f"{len(tracked_objects)}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            "BORDERGUARD AI | TRACKING ACTIVE",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.imshow(
            "BorderGuard AI - Tracking",
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

    print("=" * 60)
    print(f"Frames processed: {frame_count}")
    print("Tracking pipeline completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
