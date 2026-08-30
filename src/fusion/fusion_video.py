import cv2

from thermal_simulator import ThermalSimulator
from fusion import FusionEngine


VIDEO_PATH = "data/simulation/sample.mp4"


def add_label(
    frame,
    text,
):
    """
    Add a label to a frame.
    """

    cv2.putText(
        frame,
        text,
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )

    return frame


def main():

    print("=" * 60)
    print("       BORDERGUARD AI - VIDEO FUSION")
    print("=" * 60)

    # --------------------------------------------------------
    # Open video.
    # --------------------------------------------------------

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

    # --------------------------------------------------------
    # Initialize modules.
    # --------------------------------------------------------

    thermal_simulator = ThermalSimulator()

    fusion_engine = FusionEngine(
        rgb_weight=0.60,
        thermal_weight=0.40,
    )

    frame_count = 0

    # --------------------------------------------------------
    # Process video.
    # --------------------------------------------------------

    while True:

        success, rgb_frame = cap.read()

        if not success:
            break

        frame_count += 1

        # ----------------------------------------------------
        # Generate thermal-like frame.
        # ----------------------------------------------------

        thermal_frame = thermal_simulator.generate(rgb_frame)

        # ----------------------------------------------------
        # Fuse RGB + thermal.
        # ----------------------------------------------------

        fused_frame = fusion_engine.fuse(
            rgb_frame,
            thermal_frame,
        )

        # ----------------------------------------------------
        # Add labels.
        # ----------------------------------------------------

        rgb_display = rgb_frame.copy()

        thermal_display = thermal_frame.copy()

        fused_display = fused_frame.copy()

        add_label(
            rgb_display,
            "RGB FEED",
        )

        add_label(
            thermal_display,
            "SIMULATED THERMAL FEED",
        )

        add_label(
            fused_display,
            "FUSED FEED",
        )

        # ----------------------------------------------------
        # Display.
        # ----------------------------------------------------

        cv2.imshow(
            "RGB",
            rgb_display,
        )

        cv2.imshow(
            "Thermal",
            thermal_display,
        )

        cv2.imshow(
            "Fused",
            fused_display,
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
    print("Video fusion completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
