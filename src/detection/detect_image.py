import cv2

from detector import ObjectDetector


IMAGE_PATH = "data/simulation/image..jpg"


def main():

    detector = ObjectDetector(
        model_path="yolo11n.pt",
        confidence_threshold=0.40,
    )

    image = cv2.imread(IMAGE_PATH)

    if image is None:
        raise RuntimeError(f"Could not read image: {IMAGE_PATH}")

    detections = detector.detect(image)

    print("=" * 60)
    print("YOLO IMAGE DETECTION RESULTS")
    print("=" * 60)

    print(f"Objects detected: {len(detections)}")

    for index, detection in enumerate(
        detections,
        start=1,
    ):

        print(
            f"{index}. "
            f"{detection['class_name']} | "
            f"confidence="
            f"{detection['confidence']:.3f} | "
            f"bbox="
            f"{detection['bbox']}"
        )

    print("=" * 60)

    # Draw detections.
    for detection in detections:

        x1, y1, x2, y2 = detection["bbox"]

        label = f"{detection['class_name']} " f"{detection['confidence'] * 100:.1f}%"

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2,
        )

        cv2.putText(
            image,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

    cv2.imshow(
        "BorderGuard AI - Image Detection",
        image,
    )

    print("Press any key to close.")

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
