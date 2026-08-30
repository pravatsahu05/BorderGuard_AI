import sys
from pathlib import Path

import cv2

# Ensure src/detection is in sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from detector import ObjectDetector
except ImportError:
    from src.detection.detector import ObjectDetector


VIDEO_PATH = "data/simulation/sample.mp4"
WINDOW_NAME = "BorderGuard AI - YOLO Detection"


def draw_detection(frame, detection):
    """
    Draw one detection on a frame.
    """

    x1, y1, x2, y2 = detection["bbox"]

    class_name = detection["class_name"]
    confidence = detection["confidence"]

    # Draw bounding box.
    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2,
    )

    # Create label.
    label = f"{class_name} " f"{confidence * 100:.1f}%"

    # Draw label.
    cv2.putText(
        frame,
        label,
        (x1, max(y1 - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
    )


def main():

    print("=" * 60)
    print("        BORDERGUARD AI - YOLO DETECTION")
    print("=" * 60)

    # --------------------------------------------------------
    # Load detector.
    # --------------------------------------------------------

    detector = ObjectDetector(
        model_path="yolo11n.pt",
        confidence_threshold=0.40,
    )

    # --------------------------------------------------------
    # Open video.
    # --------------------------------------------------------

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

    frame_count = 0

    while True:

        # Read frame.
        success, frame = cap.read()

        if not success:
            break

        frame_count += 1

        # ----------------------------------------------------
        # YOLO detection.
        # ----------------------------------------------------

        detections = detector.detect(frame)

        # ----------------------------------------------------
        # Draw every detection.
        # ----------------------------------------------------

        for detection in detections:

            draw_detection(
                frame,
                detection,
            )

        # ----------------------------------------------------
        # Display detection count.
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"Objects: {len(detections)}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # ----------------------------------------------------
        # Display frame.
        # ----------------------------------------------------

        cv2.imshow(
            WINDOW_NAME,
            frame,
        )

        # ----------------------------------------------------
        # Press Q to exit.
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("=" * 60)
    print(f"Frames processed: {frame_count}")
    print("YOLO detection pipeline completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
