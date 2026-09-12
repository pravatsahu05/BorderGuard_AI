import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

import cv2

try:
    from detection.yolo_detector import YOLODetector
except ImportError:
    from src.detection.yolo_detector import YOLODetector

try:
    from fusion.thermal_simulator import ThermalSimulator
    from fusion.detection_fusion import DetectionFusion
except ImportError:
    from src.fusion.thermal_simulator import ThermalSimulator
    from src.fusion.detection_fusion import DetectionFusion


VIDEO_PATH = "data/simulation/sample.mp4"


def draw_detection(
    frame,
    detection,
):

    x1, y1, x2, y2 = [int(value) for value in detection["box"]]

    class_name = detection["class_name"]

    confidence = detection["confidence"]

    source = detection.get(
        "source",
        "unknown",
    )

    label = f"{class_name} " f"{confidence * 100:.1f}% " f"[{source}]"

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2,
    )

    cv2.putText(
        frame,
        label,
        (x1, max(y1 - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 0),
        2,
    )


def main():

    print("=" * 60)
    print("   BORDERGUARD AI - RGB + THERMAL")
    print("       DECISION-LEVEL FUSION")
    print("=" * 60)

    # ----------------------------------------------------------
    # Initialize modules.
    # ----------------------------------------------------------

    thermal_simulator = ThermalSimulator()

    detector = YOLODetector(
        confidence=0.40,
    )

    fusion_engine = DetectionFusion(
        iou_threshold=0.50,
        confidence_threshold=0.40,
    )

    # ----------------------------------------------------------
    # Open video.
    # ----------------------------------------------------------

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

    frame_count = 0

    # ----------------------------------------------------------
    # Process frames.
    # ----------------------------------------------------------

    while True:

        success, rgb_frame = cap.read()

        if not success:
            break

        frame_count += 1

        # ------------------------------------------------------
        # Generate thermal-like frame.
        # ------------------------------------------------------

        thermal_frame = thermal_simulator.generate(rgb_frame)

        # ------------------------------------------------------
        # RGB detection.
        # ------------------------------------------------------

        rgb_detections = detector.detect(rgb_frame)

        # ------------------------------------------------------
        # Thermal detection.
        # ------------------------------------------------------

        thermal_detections = detector.detect(thermal_frame)

        # ------------------------------------------------------
        # Decision-level fusion.
        # ------------------------------------------------------

        fused_detections = fusion_engine.fuse(
            rgb_detections,
            thermal_detections,
        )

        # ------------------------------------------------------
        # Create display frame.
        # ------------------------------------------------------

        fused_display = rgb_frame.copy()

        for detection in fused_detections:

            draw_detection(
                fused_display,
                detection,
            )

        # ------------------------------------------------------
        # Information panel.
        # ------------------------------------------------------

        cv2.putText(
            fused_display,
            f"RGB: {len(rgb_detections)}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            fused_display,
            f"Thermal: {len(thermal_detections)}",
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            fused_display,
            f"Fused: {len(fused_detections)}",
            (20, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # ------------------------------------------------------
        # Display / Headless handling.
        # ------------------------------------------------------
        if "--headless" in sys.argv or frame_count >= 10:
            if frame_count >= 10:
                break
        else:
            try:
                cv2.imshow(
                    "BorderGuard AI - Detection Fusion",
                    fused_display,
                )

                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break
            except cv2.error:
                break

    cap.release()

    try:
        cv2.destroyAllWindows()
    except cv2.error:
        pass

    print("=" * 60)
    print(f"Frames processed: {frame_count}")
    print("RGB + Thermal detection fusion completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
