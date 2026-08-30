import sys
from pathlib import Path

import cv2

# Ensure src/detection is in sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "detection"))

from thermal_simulator import ThermalSimulator
from fusion import FusionEngine

try:
    from detector import ObjectDetector
except ImportError:
    from src.detection.detector import ObjectDetector



VIDEO_PATH = "data/simulation/sample.mp4"


def draw_detection(
    frame,
    detection,
):

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

    # Draw label.
    label = f"{class_name} " f"{confidence * 100:.1f}%"

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
    print("     BORDERGUARD AI - FUSION + YOLO")
    print("=" * 60)

    # --------------------------------------------------------
    # Initialize components.
    # --------------------------------------------------------

    thermal_simulator = ThermalSimulator()

    fusion_engine = FusionEngine(
        rgb_weight=0.60,
        thermal_weight=0.40,
    )

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

        success, rgb_frame = cap.read()

        if not success:
            break

        frame_count += 1

        # ----------------------------------------------------
        # Generate thermal.
        # ----------------------------------------------------

        thermal_frame = thermal_simulator.generate(rgb_frame)

        # ----------------------------------------------------
        # Fuse.
        # ----------------------------------------------------

        fused_frame = fusion_engine.fuse(
            rgb_frame,
            thermal_frame,
        )

        # ----------------------------------------------------
        # Run YOLO on fused frame.
        # ----------------------------------------------------

        detections = detector.detect(fused_frame)

        # ----------------------------------------------------
        # Draw detections.
        # ----------------------------------------------------

        for detection in detections:

            draw_detection(
                fused_frame,
                detection,
            )

        # ----------------------------------------------------
        # Display detection count.
        # ----------------------------------------------------

        cv2.putText(
            fused_frame,
            f"Objects: {len(detections)}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        # ----------------------------------------------------
        # Display.
        # ----------------------------------------------------

        cv2.imshow(
            "BorderGuard AI - Fused YOLO",
            fused_frame,
        )

        # ----------------------------------------------------
        # Exit.
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    cap.release()

    cv2.destroyAllWindows()

    print("=" * 60)
    print(f"Frames processed: {frame_count}")
    print("Fusion + YOLO completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
