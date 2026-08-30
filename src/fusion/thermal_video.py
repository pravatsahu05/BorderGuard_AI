import cv2

from thermal_simulator import ThermalSimulator


VIDEO_PATH = "data/simulation/sample.mp4"


def main():

    print("=" * 60)
    print("      BORDERGUARD AI - THERMAL VIDEO SIMULATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Open RGB video.
    # --------------------------------------------------------

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

    # --------------------------------------------------------
    # Create thermal simulator.
    # --------------------------------------------------------

    simulator = ThermalSimulator(
        blur_size=5,
        contrast=1.5,
    )

    frame_count = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame_count += 1

        # ----------------------------------------------------
        # Generate thermal-like frame.
        # ----------------------------------------------------

        thermal_frame = simulator.generate(frame)

        # ----------------------------------------------------
        # Add labels.
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "SIMULATED RGB FEED",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            thermal_frame,
            "SIMULATED THERMAL FEED",
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
            "RGB Feed",
            frame,
        )

        cv2.imshow(
            "Thermal Feed",
            thermal_frame,
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
    print("Thermal video simulation completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
