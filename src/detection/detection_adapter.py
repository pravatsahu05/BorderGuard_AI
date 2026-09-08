def adapt_yolo_detections(
    detections,
):

    adapted = []

    for detection in detections:

        adapted.append(
            {
                "object_type": (detection["class_name"]),
                "confidence": (detection["confidence"]),
                "bbox": (detection["box"]),
            }
        )

    return adapted
