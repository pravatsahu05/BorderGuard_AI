import cv2


def draw_detections(
    frame,
    detections,
):

    output = frame.copy()

    for detection in detections:

        x1, y1, x2, y2 = map(
            int,
            detection["box"],
        )

        class_name = detection["class_name"]

        confidence = detection["confidence"]

        label = f"{class_name} " f"{confidence:.2f}"

        cv2.rectangle(
            output,
            (x1, y1),
            (x2, y2),
            (255, 255, 255),
            2,
        )

        cv2.putText(
            output,
            label,
            (x1, max(20, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

    return output
