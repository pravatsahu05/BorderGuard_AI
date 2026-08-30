class ObjectTracker:
    """
    Extracts and formats object tracking information from YOLO results.
    """

    def __init__(self):
        pass

    def update(self, result, names):
        """
        Process tracking results from YOLO.

        Parameters:
            result: YOLO Result object from model.track() or model.predict()
            names: Dict or list of class names

        Returns:
            List of tracked object dictionaries.
        """

        tracked_objects = []

        if result.boxes is None or len(result.boxes) == 0:
            return tracked_objects

        for index, box in enumerate(result.boxes):

            # Use ByteTrack ID if available, otherwise assign fallback ID based on index
            if box.id is not None:
                track_id = int(box.id[0])
            else:
                track_id = index + 1

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            confidence = float(box.conf[0])

            class_id = int(box.cls[0])

            class_name = names[class_id]

            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0

            tracked_object = {
                "track_id": track_id,
                "class_id": class_id,
                "class_name": class_name,
                "confidence": confidence,
                "bbox": (x1, y1, x2, y2),
                "center": (center_x, center_y),
            }

            tracked_objects.append(tracked_object)

        return tracked_objects
