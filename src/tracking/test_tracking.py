from ultralytics import YOLO


VIDEO_PATH = "data/simulation/sample.mp4"


def main():

    print("=" * 60)
    print("       BORDERGUARD AI - TRACKING TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Load YOLO model.
    # --------------------------------------------------------

    model = YOLO("yolo11n.pt")

    print("YOLO model loaded.")

    # --------------------------------------------------------
    # Run tracking.
    # --------------------------------------------------------

    results = model.track(
        source=VIDEO_PATH,
        tracker="bytetrack.yaml",
        conf=0.40,
        persist=True,
        show=True,
    )

    print("=" * 60)
    print("Tracking completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
